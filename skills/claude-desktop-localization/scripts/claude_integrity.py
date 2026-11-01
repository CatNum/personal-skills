#!/usr/bin/env python3
"""Inspect or repair Claude Desktop ASAR integrity metadata on a staged app."""

from __future__ import annotations

import argparse
import hashlib
import json
import mmap
import os
import plistlib
import struct
import sys
from pathlib import Path
from typing import Any


DIGEST_SENTINEL = b"AGbevlPCksUGKNL8TSn7wGmJEuJsXb2A"
DICTIONARY_VERSION = 1


class IntegrityError(RuntimeError):
    """Raised when the bundle does not match a safely patchable layout."""


def require_staged_target(app: Path) -> None:
    protected_roots = (Path("/Applications"), Path("/System/Applications"))
    if any(app == root or app.is_relative_to(root) for root in protected_roots):
        raise IntegrityError(
            "Refusing to write integrity metadata to an installed application; "
            "stage a copy elsewhere and verify the final path separately"
        )


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def read_asar(path: Path) -> tuple[bytes, int, dict[str, Any]]:
    """Return the JSON header bytes, data offset, and parsed header."""
    with path.open("rb") as stream:
        prefix = stream.read(16)
        if len(prefix) != 16:
            raise IntegrityError(f"ASAR prefix is too short: {path}")
        header_block_size = struct.unpack_from("<I", prefix, 4)[0]
        header_json_size = struct.unpack_from("<I", prefix, 12)[0]
        header_bytes = stream.read(header_json_size)
        if len(header_bytes) != header_json_size:
            raise IntegrityError(f"ASAR header is truncated: {path}")
        data_offset = 8 + header_block_size
        file_size = path.stat().st_size
        if data_offset > file_size:
            raise IntegrityError(f"ASAR data offset exceeds file size: {path}")
    try:
        header = json.loads(header_bytes)
    except json.JSONDecodeError as exc:
        raise IntegrityError(f"ASAR header is not valid JSON: {path}: {exc}") from exc
    if not isinstance(header, dict) or not isinstance(header.get("files"), dict):
        raise IntegrityError(f"ASAR header lacks a files map: {path}")
    return header_bytes, data_offset, header


def dictionary_digest(integrity: dict[str, Any]) -> bytes:
    digest = hashlib.sha256()
    for relative_path in sorted(integrity):
        payload = integrity[relative_path]
        for value in (
            relative_path,
            payload["algorithm"],
            payload["hash"],
        ):
            digest.update(value.encode("utf-8"))
    return digest.digest()


def iter_file_nodes(nodes: dict[str, Any], prefix: str = ""):
    for name, node in nodes.items():
        relative_path = f"{prefix}{name}"
        if not isinstance(node, dict):
            raise IntegrityError(f"Invalid ASAR node: {relative_path}")
        if isinstance(node.get("files"), dict):
            yield from iter_file_nodes(node["files"], f"{relative_path}/")
            continue
        if "link" in node or node.get("unpacked") is True:
            continue
        yield relative_path, node


def verify_asar_files(
    path: Path, data_offset: int, header: dict[str, Any]
) -> list[str]:
    failures: list[str] = []
    with path.open("rb") as stream:
        for relative_path, node in iter_file_nodes(header["files"]):
            size = node.get("size")
            relative_offset = node.get("offset")
            integrity = node.get("integrity")
            if not isinstance(size, int) or not isinstance(relative_offset, str):
                failures.append(f"{relative_path}: invalid size or offset")
                continue
            if not isinstance(integrity, dict):
                failures.append(f"{relative_path}: missing integrity")
                continue
            if integrity.get("algorithm") != "SHA256":
                failures.append(f"{relative_path}: unsupported algorithm")
                continue
            try:
                offset = int(relative_offset)
            except ValueError:
                failures.append(f"{relative_path}: invalid offset")
                continue
            stream.seek(data_offset + offset)
            data = stream.read(size)
            if len(data) != size:
                failures.append(f"{relative_path}: truncated data")
                continue
            actual = hashlib.sha256(data).hexdigest()
            if actual != integrity.get("hash"):
                failures.append(f"{relative_path}: file hash mismatch")
                continue
            block_size = integrity.get("blockSize")
            blocks = integrity.get("blocks")
            if not isinstance(block_size, int) or block_size <= 0:
                failures.append(f"{relative_path}: invalid block size")
                continue
            if not isinstance(blocks, list):
                failures.append(f"{relative_path}: missing block hashes")
                continue
            expected_blocks = [
                hashlib.sha256(data[index:index + block_size]).hexdigest()
                for index in range(0, len(data), block_size)
            ]
            if not data:
                expected_blocks = [hashlib.sha256(b"").hexdigest()]
            if expected_blocks != blocks:
                failures.append(f"{relative_path}: block hash mismatch")
    return failures


def framework_binary(app: Path) -> Path:
    candidates_by_target: dict[Path, Path] = {}
    for path in (
        app / "Contents/Frameworks/Electron Framework.framework/Versions"
    ).glob("*/Electron Framework"):
        if path.is_file() and not path.is_symlink():
            target = path.resolve()
            existing = candidates_by_target.get(target)
            if (
                existing is None
                or (
                    existing.parent.name == "Current"
                    and path.parent.name != "Current"
                )
            ):
                candidates_by_target[target] = path
    candidates = sorted(candidates_by_target.values())
    if len(candidates) != 1:
        raise IntegrityError(
            "Expected exactly one Electron Framework executable; "
            f"found {len(candidates)}"
        )
    return candidates[0]


def find_digest_slots(path: Path) -> list[tuple[int, int, int, bytes]]:
    """Return offset, used, version, digest for every known sentinel slot."""
    slots: list[tuple[int, int, int, bytes]] = []
    with path.open("rb") as stream:
        with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as data:
            position = 0
            while True:
                position = data.find(DIGEST_SENTINEL, position)
                if position < 0:
                    break
                metadata = position + len(DIGEST_SENTINEL)
                if metadata + 34 > len(data):
                    raise IntegrityError("Integrity slot metadata is truncated")
                used = data[metadata]
                version = data[metadata + 1]
                digest = bytes(data[metadata + 2:metadata + 34])
                slots.append((position, used, version, digest))
                position = metadata + 34
    return slots


def update_dictionary_slots(path: Path, expected: bytes) -> int:
    patched = 0
    with path.open("r+b") as stream:
        with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_WRITE) as data:
            position = 0
            while True:
                position = data.find(DIGEST_SENTINEL, position)
                if position < 0:
                    break
                metadata = position + len(DIGEST_SENTINEL)
                if metadata + 34 > len(data):
                    raise IntegrityError("Integrity slot metadata is truncated")
                used, version = data[metadata], data[metadata + 1]
                if used == 0:
                    position = metadata + 34
                    continue
                if version != DICTIONARY_VERSION:
                    raise IntegrityError(
                        f"Unknown active integrity slot version {version}; stop"
                    )
                data[metadata + 2:metadata + 34] = expected
                patched += 1
                position = metadata + 34
            data.flush()
    return patched


def load_bundle(app: Path) -> tuple[Path, dict[str, Any]]:
    plist_path = app / "Contents/Info.plist"
    if not plist_path.is_file():
        raise IntegrityError(f"Info.plist not found under app bundle: {app}")
    with plist_path.open("rb") as stream:
        info = plistlib.load(stream)
    integrity = info.get("ElectronAsarIntegrity")
    if not isinstance(integrity, dict) or not integrity:
        raise IntegrityError("Info.plist has no ElectronAsarIntegrity map")
    return plist_path, info


def current_headers(app: Path, integrity: dict[str, Any]) -> dict[str, str]:
    contents = app / "Contents"
    hashes: dict[str, str] = {}
    for relative_path, payload in integrity.items():
        archive = contents / relative_path
        if not is_within(archive, contents):
            raise IntegrityError(f"ASAR path escapes app bundle: {relative_path}")
        if not archive.is_file():
            raise IntegrityError(f"ASAR is missing: {archive}")
        if payload.get("algorithm") != "SHA256":
            raise IntegrityError(
                f"Unsupported integrity algorithm for {relative_path}: "
                f"{payload.get('algorithm')!r}"
            )
        header_bytes, _, _ = read_asar(archive)
        hashes[relative_path] = hashlib.sha256(header_bytes).hexdigest()
    return hashes


def write_plist(path: Path, info: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    mode = path.stat().st_mode
    with temporary.open("wb") as stream:
        plistlib.dump(info, stream, sort_keys=False)
    os.chmod(temporary, mode)
    os.replace(temporary, path)


def check_app(app: Path, deep: bool) -> bool:
    plist_path, info = load_bundle(app)
    integrity = info["ElectronAsarIntegrity"]
    actual_hashes = current_headers(app, integrity)
    ok = True

    print(f"APP {app}")
    print(f"VERSION {info.get('CFBundleShortVersionString', 'unknown')}")
    print(f"PLIST {plist_path}")
    for relative_path, payload in integrity.items():
        expected_hash = payload.get("hash")
        actual_hash = actual_hashes[relative_path]
        matches = actual_hash == expected_hash
        ok &= matches
        print(
            f"ASAR {relative_path} "
            f"{'MATCH' if matches else 'MISMATCH'} {actual_hash}"
        )

        if deep:
            archive = app / "Contents" / relative_path
            _, data_offset, header = read_asar(archive)
            failures = verify_asar_files(archive, data_offset, header)
            print(
                f"FILES {relative_path} "
                f"{'MATCH' if not failures else f'{len(failures)} FAILURES'}"
            )
            for failure in failures[:20]:
                print(f"  {failure}")
            if len(failures) > 20:
                print(f"  ... {len(failures) - 20} more")
            ok &= not failures

    expected_dictionary = dictionary_digest(integrity)
    framework = framework_binary(app)
    slots = find_digest_slots(framework)
    active_slots = [slot for slot in slots if slot[1] != 0]
    print(f"DICTIONARY {expected_dictionary.hex()}")
    print(f"FRAMEWORK {framework}")
    print(f"DIGEST_SLOTS {len(slots)} ACTIVE {len(active_slots)}")
    if not slots:
        print("DIGEST_SLOTS NONE: the embedded dictionary check is not present")
    for position, used, version, digest in active_slots:
        matches = version == DICTIONARY_VERSION and digest == expected_dictionary
        ok &= matches
        print(
            f"SLOT offset={position} used={used} version={version} "
            f"{'MATCH' if matches else 'MISMATCH'} {digest.hex()}"
        )
    return bool(ok)


def write_app(app: Path, deep: bool) -> bool:
    plist_path, info = load_bundle(app)
    integrity = info["ElectronAsarIntegrity"]
    actual_hashes = current_headers(app, integrity)
    for relative_path, actual_hash in actual_hashes.items():
        integrity[relative_path]["hash"] = actual_hash

    if deep:
        for relative_path in integrity:
            archive = app / "Contents" / relative_path
            _, data_offset, header = read_asar(archive)
            failures = verify_asar_files(archive, data_offset, header)
            if failures:
                raise IntegrityError(
                    f"{relative_path} has {len(failures)} per-file integrity "
                    "failures; repack it with matching integrity data first"
                )

    expected_dictionary = dictionary_digest(integrity)
    framework = framework_binary(app)
    slots_before = find_digest_slots(framework)
    active_before = [slot for slot in slots_before if slot[1] != 0]
    unknown = [slot for slot in active_before if slot[2] != DICTIONARY_VERSION]
    if unknown:
        raise IntegrityError(
            "Active integrity slots use an unknown version; stop before writing"
        )

    write_plist(plist_path, info)
    patched = update_dictionary_slots(framework, expected_dictionary)
    print(f"WROTE {plist_path}")
    print(f"PATCHED_ACTIVE_DIGEST_SLOTS {patched}")
    if active_before and patched == 0:
        raise IntegrityError("Active slots were found but no slot was patched")
    if not slots_before:
        print(
            "WARNING: no embedded digest sentinel was found; verify this "
            "Electron version instead of assuming the plist update is enough"
        )
    return check_app(app, deep=deep)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect or repair Claude Desktop ASAR integrity metadata."
    )
    parser.add_argument("app", type=Path, help="Staged Claude.app path")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Update Info.plist header hashes and embedded dictionary digest",
    )
    parser.add_argument(
        "--skip-files",
        action="store_true",
        help="Skip per-file ASAR hash and block verification",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = args.app.expanduser().resolve()
    try:
        if args.write:
            require_staged_target(app)
        passed = (
            write_app(app, deep=not args.skip_files)
            if args.write
            else check_app(app, deep=not args.skip_files)
        )
    except (IntegrityError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
