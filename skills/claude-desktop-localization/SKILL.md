---
name: claude-desktop-localization
description: Use when localizing a Claude Desktop macOS bundle, adding or updating zh-Hans resources, repairing a modified ASAR, or diagnosing launch failures after modification such as invalid signatures, failed ElectronAsarIntegrity checks, unexpected exits, or missing Claude Safe Storage access.
---

# Claude Desktop Localization

Only modify a Claude Desktop bundle when the user explicitly asks. Treat it as an unofficial, version-sensitive patch of a signed proprietary application. Keep an untouched official app and work on a `ditto` copy until the staged bundle passes integrity, signature, and startup checks.

## Core Invariant

Complete every content change before the final signing pass:

```text
translation resources
→ repack ASAR
→ update ASAR header hashes
→ update embedded integrity-dictionary digest, when present
→ sign nested code from inside out
→ sign the outer app last
→ verify and launch
```

Editing an ASAR, `Info.plist`, Electron Framework, or helper after signing invalidates the signature again. `xattr -dr com.apple.quarantine` is not a signature or integrity repair.

## Workflow

1. **Detect the existing state before any edit.** Run [detect_localization.py](scripts/detect_localization.py). Treat this as a mandatory read-only gate. It checks `i18n/zh-Hans.json`, `i18n/dynamic/zh-Hans.json`, translation coverage, native `zh_CN` resources, ASAR integrity, and the code signature.
2. **Choose the source deliberately.** Proceed from a pristine official copy only when the state is `not-localized`. For `localized-valid`, stop and ask whether the user wants to reuse, update coverage, or repair the existing version. For `localized-invalid` or `localization-incomplete`, preserve it for diagnosis and obtain a trusted same-version official copy; do not treat it as a clean base.
3. **Stage a copy.** Record the Claude version. Copy with `/usr/bin/ditto`; never experiment in `/Applications/Claude.app`. Preserve an untouched official source for rollback.
4. **Map the resources.** Inspect `Contents/Resources/ion-dist.asar` for UI translations and language registration, `zh_CN.lproj` for native macOS strings, and `Contents/Info.plist` for `ElectronAsarIntegrity`. Do not assume filenames stay identical across releases.
5. **Apply translations.** Unpack only the target ASAR, add a distinct locale such as `zh-Hans`, register its display name, preserve English fallback, then repack. Translate native strings separately. Report measured key coverage rather than describing partial translation as complete.
6. **Repair all integrity layers.** Run [claude_integrity.py](scripts/claude_integrity.py) in check mode first. If it reports stale hashes, inspect the staged app and then use explicit write mode. The script also verifies per-file ASAR integrity and updates the embedded Electron Framework dictionary digest when that mechanism is active.
7. **Resign on the staged copy.** Run [resign_claude_app.py](scripts/resign_claude_app.py). It signs nested Mach-O files, frameworks, helper bundles, and the outer app from inside out while preserving required runtime entitlements and removing restricted identities that ad-hoc signing cannot claim.
8. **Verify three separate layers.** Require a clean integrity check, a successful strict `codesign --verify --deep --strict`, and a real launch with `--enable-logging=stderr` that does not contain `:FATAL:`. Do not infer startup success from signature validation alone.
9. **Install only with approval.** Quit the running app, keep a rollback copy, install the verified stage, then repeat signature and launch verification at the final path. Ask the user to select the language and restart the app.

Read [macos-integrity-and-signing.md](references/macos-integrity-and-signing.md) before changing hashes, patching Electron Framework, or claiming the result is safely signed.

## Commands

Run detection against the installed app before staging. Replace `$STAGE` with the copied `Claude.app` for the write path; both modification scripts default to check-only and reject `--write` under `/Applications`.

```bash
python3 scripts/detect_localization.py "/Applications/Claude.app"
python3 scripts/claude_integrity.py "$STAGE"
python3 scripts/claude_integrity.py "$STAGE" --write
python3 scripts/resign_claude_app.py "$STAGE" --write
codesign --verify --deep --strict --all-architectures --verbose=2 "$STAGE"
"$STAGE/Contents/MacOS/Claude" --enable-logging=stderr
```

## Stop Conditions

- Stop before creating or replacing localization files when `detect_localization.py` returns `localized-valid`; ask whether to reuse or update the existing resources.
- Stop if the chosen Claude version has a different integrity mechanism, the sentinel format differs, per-file ASAR integrity is missing, or a script reports ambiguous matches.
- Stop if a modified app requires an official Anthropic team identity for the feature being used. Ad-hoc signing cannot restore that identity.
- Do not claim automatic updates, Touch ID passkeys, keychain access, enterprise sign-in, or notarization will continue to work after local signing.
- Do not replace the installed app or delete backups without the user's explicit approval.

## Expected Consequences

- The first access to `Claude Safe Storage` may request the macOS login password because the code identity changed.
- Touch ID/passkey access may fail because the official `keychain-access-groups` entitlement cannot be reproduced by an ad-hoc signature.
- System privacy permissions may need to be granted again.
- An automatic update replaces the localized resources, signed framework, and signatures; rerun the complete workflow after every version change.

## Common Mistakes

| Mistake | Consequence |
|---|---|
| Starting a new translation pass without checking the installed app | Existing translations may be overwritten, duplicated, or mistaken for an official baseline |
| Updating only `ElectronAsarIntegrity` | Electron Framework may still embed the old dictionary digest and terminate at startup |
| Hashing the whole ASAR file | The expected value is the SHA-256 of the ASAR header payload, not the complete archive |
| Editing `Info.plist` after signing | macOS rejects the app even when resources are valid |
| Signing only the outer `.app` | Electron Framework and helper signatures remain inconsistent |
| Using `codesign --deep` as the signing strategy | It hides ordering problems instead of correctly signing nested code |
| Removing quarantine and retrying | It cannot repair invalid signatures or integrity metadata |
| Reusing a modified bundle across Claude updates | Versions, framework digests, helpers, and translation keys may differ |
