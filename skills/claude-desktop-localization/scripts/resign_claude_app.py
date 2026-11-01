#!/usr/bin/env python3
"""Locally re-sign a staged Claude Desktop macOS application."""

from __future__ import annotations

import argparse
import plistlib
import subprocess
import sys
from pathlib import Path


REMOVE_ENTITLEMENTS = {
    "com.apple.application-identifier",
    "com.apple.developer.team-identifier",
    "keychain-access-groups",
}


class SigningError(RuntimeError):
    """Raised when the bundle cannot be re-signed safely."""


def require_staged_target(app: Path) -> None:
    protected_roots = (Path("/Applications"), Path("/System/Applications"))
    if any(app == root or app.is_relative_to(root) for root in protected_roots):
        raise SigningError(
            "Refusing to re-sign an installed application in place; "
            "sign the staged copy before installation"
        )


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(args, capture_output=True)
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout).decode(errors="replace")
        raise SigningError(f"{' '.join(args)} failed:\n{detail}")
    return result


def verify(app: Path) -> None:
    result = run(
        "/usr/bin/codesign",
        "--verify",
        "--deep",
        "--strict",
        "--verbose=2",
        str(app),
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).decode(errors="replace")
        raise SigningError(f"Signature verification failed:\n{detail}")
    print((result.stderr or result.stdout).decode(errors="replace").strip())
    print("SIGNATURE_VALID")


def read_entitlements(target: Path) -> dict[str, object]:
    result = run(
        "/usr/bin/codesign",
        "-d",
        "--entitlements",
        ":-",
        str(target),
        check=False,
    )
    raw = result.stdout or result.stderr
    if result.returncode != 0 or not raw.strip():
        return {}
    xml_start = raw.find(b"<?xml")
    if xml_start < 0:
        return {}
    return plistlib.loads(raw[xml_start:])


def local_entitlements(target: Path) -> dict[str, object]:
    entitlements = read_entitlements(target)
    for key in REMOVE_ENTITLEMENTS:
        entitlements.pop(key, None)
    entitlements["com.apple.security.cs.disable-library-validation"] = True
    return entitlements


def nested_bundles(app: Path, suffix: str) -> list[Path]:
    roots = [
        app / "Contents/Frameworks",
        app / "Contents/Helpers",
    ]
    targets: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        targets.update(
            path
            for path in root.glob(f"**/*{suffix}")
            if path.is_dir() and not path.is_symlink()
        )
    return sorted(targets, key=lambda path: (-len(path.parts), str(path)))


def mach_o_files(app: Path) -> list[Path]:
    roots = [
        app / "Contents/Frameworks",
        app / "Contents/Helpers",
    ]
    files: set[Path] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.glob("**/*"):
            if (
                not path.is_file()
                or path.is_symlink()
                or "_CodeSignature" in path.parts
            ):
                continue
            result = run("/usr/bin/file", "-b", str(path), check=False)
            if b"Mach-O" in result.stdout:
                files.add(path)
    return sorted(files, key=lambda path: (-len(path.parts), str(path)))


def write_entitlements(path: Path, payload: dict[str, object]) -> None:
    with path.open("wb") as stream:
        plistlib.dump(payload, stream, sort_keys=False)


def resign(app: Path) -> None:
    frameworks = nested_bundles(app, ".framework")
    helpers = nested_bundles(app, ".app")
    executables = mach_o_files(app)
    if not frameworks:
        raise SigningError("No nested frameworks found")
    print(f"NESTED_FRAMEWORKS {len(frameworks)}")
    print(f"NESTED_APPS {len(helpers)}")
    print(f"NESTED_MACH_O_FILES {len(executables)}")

    entitlement_dir = app.parent / f".{app.name}.resign-entitlements"
    entitlement_dir.mkdir(exist_ok=False)
    index = 0

    def sign(target: Path, *, bundle: bool) -> None:
        nonlocal index
        entitlement_path = entitlement_dir / f"{index:03d}.plist"
        write_entitlements(entitlement_path, local_entitlements(target))
        arguments = [
            "/usr/bin/codesign",
            "--force",
            "--sign",
            "-",
            "--options",
            "runtime",
            "--entitlements",
            str(entitlement_path),
            str(target),
        ]
        run(*arguments)
        print(f"SIGNED {'BUNDLE' if bundle else 'MACH_O'} {target}")
        index += 1

    try:
        for target in executables:
            sign(target, bundle=False)
        for target in frameworks:
            sign(target, bundle=True)
        for target in helpers:
            sign(target, bundle=True)
        sign(app, bundle=True)
    finally:
        for path in entitlement_dir.iterdir():
            path.unlink()
        entitlement_dir.rmdir()

    verify(app)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check or locally re-sign a staged Claude Desktop app."
    )
    parser.add_argument("app", type=Path, help="Staged Claude.app path")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Apply local signatures; without this flag only verify",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = args.app.expanduser().resolve()
    try:
        if args.write:
            require_staged_target(app)
            resign(app)
        else:
            verify(app)
    except (SigningError, OSError, plistlib.InvalidFileException) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
