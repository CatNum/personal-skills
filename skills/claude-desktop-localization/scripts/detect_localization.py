#!/usr/bin/env python3
"""Detect existing Claude Desktop zh-Hans localization without modifying it."""

from __future__ import annotations

import argparse
import json
import plistlib
import subprocess
import sys
from pathlib import Path
from typing import Any

import claude_integrity as integrity


class DetectionError(RuntimeError):
    """Raised when localization state cannot be inspected safely."""


def asar_node(header: dict[str, Any], relative_path: str) -> dict[str, Any] | None:
    node: dict[str, Any] = header
    for component in relative_path.split("/"):
        files = node.get("files")
        if not isinstance(files, dict):
            return None
        child = files.get(component)
        if not isinstance(child, dict):
            return None
        node = child
    return node


def read_node_data(
    archive: Path, data_offset: int, node: dict[str, Any]
) -> bytes:
    size = node.get("size")
    offset = node.get("offset")
    if not isinstance(size, int) or not isinstance(offset, str):
        raise DetectionError(f"Invalid ASAR node in {archive}")
    with archive.open("rb") as stream:
        stream.seek(data_offset + int(offset))
        data = stream.read(size)
    if len(data) != size:
        raise DetectionError(f"Truncated ASAR entry in {archive}")
    return data


def json_key_count(data: bytes) -> int | None:
    try:
        value = json.loads(data)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return len(value) if isinstance(value, dict) else None


def locale_report(archive: Path) -> dict[str, Any]:
    _, data_offset, header = integrity.read_asar(archive)
    main_zh = asar_node(header, "i18n/zh-Hans.json")
    dynamic_zh = asar_node(header, "i18n/dynamic/zh-Hans.json")
    main_en = asar_node(header, "i18n/en-US.json")
    dynamic_en = asar_node(header, "i18n/dynamic/en-US.json")
    if not main_zh and not dynamic_zh:
        return {}

    report: dict[str, Any] = {
        "archive": str(archive),
        "main_present": main_zh is not None,
        "dynamic_present": dynamic_zh is not None,
    }
    if main_zh:
        zh_data = read_node_data(archive, data_offset, main_zh)
        report["main_keys"] = json_key_count(zh_data)
        if main_en:
            en_data = read_node_data(archive, data_offset, main_en)
            try:
                en_keys = set(json.loads(en_data))
                zh_keys = set(json.loads(zh_data))
            except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
                pass
            else:
                report["main_coverage"] = (
                    len(en_keys & zh_keys) / len(en_keys) if en_keys else 0.0
                )
    if dynamic_zh:
        zh_data = read_node_data(archive, data_offset, dynamic_zh)
        report["dynamic_keys"] = json_key_count(zh_data)
        if dynamic_en:
            en_data = read_node_data(archive, data_offset, dynamic_en)
            try:
                en_keys = set(json.loads(en_data))
                zh_keys = set(json.loads(zh_data))
            except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
                pass
            else:
                report["dynamic_coverage"] = (
                    len(en_keys & zh_keys) / len(en_keys) if en_keys else 0.0
                )
    return report


def integrity_report(app: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    try:
        _, info = integrity.load_bundle(app)
        mapping = info["ElectronAsarIntegrity"]
        actual = integrity.current_headers(app, mapping)
        for relative_path, payload in mapping.items():
            if actual[relative_path] != payload.get("hash"):
                failures.append(f"{relative_path}: header hash mismatch")
            archive = app / "Contents" / relative_path
            _, data_offset, header = integrity.read_asar(archive)
            failures.extend(
                f"{relative_path}: {failure}"
                for failure in integrity.verify_asar_files(
                    archive, data_offset, header
                )
            )
        framework = integrity.framework_binary(app)
        expected = integrity.dictionary_digest(mapping)
        active = [
            slot
            for slot in integrity.find_digest_slots(framework)
            if slot[1] != 0
        ]
        for _, _, version, digest in active:
            if version != integrity.DICTIONARY_VERSION:
                failures.append(f"unknown integrity slot version: {version}")
            elif digest != expected:
                failures.append("embedded integrity dictionary mismatch")
    except (integrity.IntegrityError, OSError, plistlib.InvalidFileException) as exc:
        failures.append(str(exc))
    return not failures, failures


def run(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(args, capture_output=True)


def signature_report(app: Path) -> dict[str, Any]:
    verify = run(
        "/usr/bin/codesign",
        "--verify",
        "--deep",
        "--strict",
        "--all-architectures",
        "--verbose=2",
        str(app),
    )
    details = run(
        "/usr/bin/codesign",
        "-d",
        "--verbose=4",
        str(app),
    )
    detail_text = (details.stdout + details.stderr).decode(errors="replace")
    authorities = [
        line.split("=", 1)[1]
        for line in detail_text.splitlines()
        if line.startswith("Authority=")
    ]
    ad_hoc = "Signature=adhoc" in detail_text
    if ad_hoc:
        kind = "ad-hoc"
    elif authorities:
        kind = "certificate"
    else:
        kind = "unknown"
    team = None
    for line in detail_text.splitlines():
        if line.startswith("TeamIdentifier="):
            team = line.split("=", 1)[1]
            break
    return {
        "valid": verify.returncode == 0,
        "kind": kind,
        "authorities": authorities,
        "team_identifier": team,
        "error": (
            ""
            if verify.returncode == 0
            else (verify.stderr or verify.stdout).decode(errors="replace")
        ),
    }


def inspect(app: Path) -> dict[str, Any]:
    plist_path = app / "Contents/Info.plist"
    with plist_path.open("rb") as stream:
        info = plistlib.load(stream)

    locales: list[dict[str, Any]] = []
    resources = app / "Contents/Resources"
    for archive in sorted(resources.glob("*.asar")):
        report = locale_report(archive)
        if report:
            locales.append(report)

    native = app / "Contents/Resources/zh_CN.lproj/Localizable.strings"
    integrity_ok, integrity_failures = integrity_report(app)
    signature = signature_report(app)
    main_reports = [item for item in locales if item.get("main_present")]
    dynamic_reports = [
        item for item in locales if item.get("dynamic_present")
    ]
    main_keys = max(
        (item.get("main_keys") or 0 for item in main_reports),
        default=0,
    )
    dynamic_keys = max(
        (item.get("dynamic_keys") or 0 for item in dynamic_reports),
        default=0,
    )

    if not locales:
        state = "not-localized"
    elif not main_reports or not dynamic_reports or main_keys <= 0:
        state = "localization-incomplete"
    elif not integrity_ok or not signature["valid"]:
        state = "localized-invalid"
    else:
        state = "localized-valid"

    return {
        "app": str(app),
        "version": info.get("CFBundleShortVersionString"),
        "state": state,
        "locales": locales,
        "native_zh_cn_present": native.is_file(),
        "integrity_valid": integrity_ok,
        "integrity_failures": integrity_failures,
        "signature": signature,
    }


def print_report(report: dict[str, Any]) -> None:
    print(f"APP {report['app']}")
    print(f"VERSION {report['version'] or 'unknown'}")
    print(f"STATE {report['state']}")
    print(f"INTEGRITY {'VALID' if report['integrity_valid'] else 'INVALID'}")
    for failure in report["integrity_failures"][:20]:
        print(f"  {failure}")
    signature = report["signature"]
    print(
        f"SIGNATURE {'VALID' if signature['valid'] else 'INVALID'} "
        f"KIND {signature['kind']}"
    )
    for item in report["locales"]:
        print(f"LOCALE {item['archive']}")
        print(
            f"  MAIN present={item['main_present']} "
            f"keys={item.get('main_keys', 0)} "
            f"coverage={item.get('main_coverage', 0):.2%}"
        )
        print(
            f"  DYNAMIC present={item['dynamic_present']} "
            f"keys={item.get('dynamic_keys', 0)} "
            f"coverage={item.get('dynamic_coverage', 0):.2%}"
        )
    print(f"NATIVE_ZH_CN {report['native_zh_cn_present']}")

    recommendations = {
        "not-localized": "Proceed from a pristine official copy.",
        "localization-incomplete": (
            "Do not reuse as a clean baseline; confirm the intended resources "
            "or restart from the official app."
        ),
        "localized-invalid": (
            "Preserve for diagnosis, then repair on a staged copy; do not "
            "reapply translations blindly."
        ),
        "localized-valid": (
            "Stop before a new localization pass. Ask whether to reuse, update, "
            "or repair the existing localization."
        ),
    }
    print(f"RECOMMENDATION {recommendations[report['state']]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect Claude Desktop zh-Hans resources before localization."
    )
    parser.add_argument("app", type=Path, help="Claude.app path")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = args.app.expanduser().resolve()
    try:
        report = inspect(app)
    except (OSError, ValueError, KeyError, DetectionError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)
    return {
        "localized-valid": 0,
        "not-localized": 1,
        "localization-incomplete": 3,
        "localized-invalid": 3,
    }[report["state"]]


if __name__ == "__main__":
    raise SystemExit(main())
