# macOS Integrity and Signing

This reference records the Claude Desktop 4.4212.0 behavior verified during localization. Fields and mechanisms are version-sensitive; re-inspect every new release before applying them.

## Bundle Map

| Path or field | Meaning | Relevance |
|---|---|---|
| `Contents/Resources/ion-dist.asar` | Packed frontend/localization resources | Primary UI translation surface in the verified version |
| `Contents/Resources/app.asar` | Packed Electron application code | Checked by the same integrity dictionary |
| `Contents/Info.plist` | Bundle metadata | Contains `ElectronAsarIntegrity` |
| `ElectronAsarIntegrity` | ASAR validation map | Maps each relative ASAR path to its `algorithm` and header `hash` |
| `algorithm` | Digest algorithm name | Verified as `SHA256` |
| `hash` | Expected ASAR header digest | Not the SHA-256 of the entire `.asar` file |
| `Contents/Resources/zh_CN.lproj` | macOS native localization directory | Localizes Electron-generated system dialogs |
| `Contents/Frameworks/Electron Framework.framework` | Electron runtime | May embed a digest of the complete integrity map |
| `Contents/Frameworks/Claude Helper*.app` | Electron helper processes | Must be signed after the framework and before the outer app |
| `Contents/Helpers/Claude iOS Sim.app` | Nested helper app | Keep its original signature unless modified, but account for it during verification |

## Three Integrity Layers

### 1. Per-file integrity inside each ASAR

An ASAR starts with a length-prefixed JSON header. File entries may contain:

- `offset`: position of the file data relative to the end of the ASAR header.
- `size`: file length in bytes.
- `integrity.algorithm`: `SHA256`.
- `integrity.hash`: SHA-256 of the complete file.
- `integrity.blockSize`: chunk size used for additional verification.
- `integrity.blocks`: SHA-256 for each data chunk.

When Electron has validated the enclosing ASAR header, it can require this per-file integrity data. A repack that drops or invalidates those fields can still reach a runtime fatal error.

## Preflight Localization Detection

Before copying or editing the app, inspect its existing state without writing:

```bash
python3 scripts/detect_localization.py "/Applications/Claude.app"
```

The verified localization resources are:

- `i18n/zh-Hans.json`: main translation catalog.
- `i18n/dynamic/zh-Hans.json`: dynamic translation catalog.
- `zh_CN.lproj/Localizable.strings`: native macOS strings.

The detector compares the Zh-Hans key sets with `en-US.json` and
`i18n/dynamic/en-US.json`. A high key-coverage value is a localization
completeness measure, not proof that every sentence is translated naturally.

The possible states are:

| State | Meaning | Required action |
|---|---|---|
| `not-localized` | No Zh-Hans ASAR catalog was found | A new pass may start from a pristine official copy |
| `localization-incomplete` | Only one catalog is present or the main catalog is empty | Do not reuse; restore a trusted source or complete the resources deliberately |
| `localized-invalid` | Zh-Hans resources exist, but integrity or signature validation fails | Preserve for diagnosis and repair a staged copy |
| `localized-valid` | Zh-Hans resources, integrity, and signatures are valid | Stop before a new pass; ask whether to reuse, update, or repair |

`localized-valid` can mean either a working custom localization or an official
future build that already ships Zh-Hans. The report includes the signature kind
(`ad-hoc` or `certificate`) and should be used with the Claude version to decide
whether third-party localization is present.

### 2. ASAR header hash in `Info.plist`

`ElectronAsarIntegrity[relativePath].hash` validates the JSON header payload. Repacking changes offsets, file sizes, integrity fields, or ordering, so the header hash must be recalculated after every repack.

Do not hash the complete `.asar` file. Read the header length-prefixed by the ASAR container and hash only the JSON header payload expected by Electron.

### 3. Integrity-dictionary digest in Electron Framework

The verified Electron 44.9.3 framework stores an additional digest slot in its binary. The active slot is marked as used, has version `1`, and contains a 32-byte digest. The digest is calculated over the complete `ElectronAsarIntegrity` map in sorted relative-path order:

```text
for each sorted relative path:
    SHA256.update(relative path)
    SHA256.update(algorithm)
    SHA256.update(hash)
```

This is an internal Electron mechanism, not an application configuration field. Updating `Info.plist` without this digest leaves a valid-looking plist with an invalid dictionary anchor. The observed fatal error was:

```text
Failed to get integrity for validatable asar archive: Resources/app.asar
```

The local helper script locates the known sentinel and only patches slots already marked as active with version `1`. If the sentinel, count, marker, or version changes, stop and investigate the new Electron version rather than guessing an offset.

## Signing Rules

1. Finish all file edits before signing.
2. Sign the modified Electron Framework first.
3. Sign nested Mach-O files, frameworks, and helper applications from deepest to shallowest.
4. Sign the outer `Claude.app` last.
5. Use `codesign --verify --deep --strict` only for verification, not as a substitute for correct signing order.

Ad-hoc signing uses:

```text
--force --sign - --options runtime
```

The identity `-` means an ad-hoc local signature. It provides a structurally valid local signature but does not impersonate Anthropic or restore the official Team ID.

## Entitlements

Preserve runtime entitlements that the application needs, including permissions such as:

- `com.apple.security.cs.allow-jit`: allows the hardened runtime to use JIT.
- `com.apple.security.device.audio-input`: allows microphone access.
- `com.apple.security.device.camera`: allows camera access.
- `com.apple.security.automation.apple-events`: allows Apple Events automation.

Remove entitlements that the local signature cannot legitimately claim:

- `com.apple.application-identifier`: official application signing identity.
- `com.apple.developer.team-identifier`: Anthropic team identity.
- `keychain-access-groups`: official keychain sharing groups.

Add this to the modified outer app and helpers when they must load locally signed Electron code:

```text
com.apple.security.cs.disable-library-validation = true
```

`disable-library-validation` weakens one hardened-runtime check so that code signed with the local ad-hoc identity can load the locally signed framework. It does not restore Apple notarization or vendor trust.

## Verification

Use all three checks:

```bash
python3 scripts/claude_integrity.py "/path/to/staged/Claude.app"
python3 scripts/resign_claude_app.py "/path/to/staged/Claude.app"
codesign --verify --deep --strict --all-architectures --verbose=2 "/path/to/staged/Claude.app"
```

Then launch the staged executable with terminal logging:

```bash
"/path/to/staged/Claude.app/Contents/MacOS/Claude" --enable-logging=stderr
```

Keep it running long enough to load the renderer. A successful signature check with an immediate `SIGTRAP`, a `:FATAL:` ASAR message, or a missing helper is still a failed verification.

`spctl --assess --type execute` can fail for an ad-hoc signed local copy. Treat that as an unresolved distribution-trust result; do not disable system security checks to force it to pass.

## Keychain After Resigning

`Claude Safe Storage` holds the encryption key used for local secure storage. macOS associates Keychain access with code identity. A locally signed app may therefore prompt for the macOS login Keychain password. This is not a request for the Claude account password.

Allowing access may preserve existing local encrypted data. Denying it may force a fresh login or make old local secure-storage data unreadable. Never ask the user to type the macOS password into the Claude UI.

## Update Policy

An official auto-update can replace the whole bundle, including ASAR files, framework bytes, signatures, and native localization. Reapply the workflow to the new version; never assume offsets, sentinels, helpers, or translation keys are unchanged.
