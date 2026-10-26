# Build 01 — today's data fix

Version: **0.4.2**, Android version code **40201**. Phone app: **Pulse Monarch**.
Package: `in.portlabs.pulse.monarch`. Architecture: `arm64-v8a`.

This candidate contains the refresh/data-retention fix and this fork's release configuration. Workout additions,
GPS recording and native Samsung sensor collection are planned for later builds.

- [Changes](CHANGELOG.md)
- [Validation and phone checklist](TESTING.md)
- [Release notes](RELEASE-NOTES.md)
- `pulse-mobile-0.4.2-arm64.apk` — local APK, also attached to the GitHub Release after publication
- `SHA256SUMS.txt` — checksum generated from the built APK

Install the APK on the **Android phone paired with the watch**. This is not a Wear OS APK.
It installs alongside the original Pulse app because the original publisher's signing key is unavailable.
Android keeps each app's database separate. Grant this fork its own Health Connect read permissions; it will
import the Samsung Health records that have been shared into Health Connect.
Updating subsequent Monarch builds retains this fork's data; do not uninstall between updates.

From the repository root, with dependencies installed and `JAVA_HOME` / `ANDROID_HOME` set:

```powershell
.\scripts\build-apk.ps1
```

The script runs checks, creates or reuses the private release signing key, regenerates Android through Expo,
verifies the official Gradle download, builds the release APK and copies it into this folder.
On Windows it compiles a public-source copy under the user's temporary directory with pnpm's flat dependency
layout, avoiding the native compiler's long/spaced-path failure. The private signing key stays in this workspace.
