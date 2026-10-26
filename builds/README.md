# Monarch builds

Repository: [rohannijhawan02/Monarch-Samsung-connected](https://github.com/rohannijhawan02/Monarch-Samsung-connected).
Base: complete Pulse Mobile source, commit `6fe93bf6d15fe021e6674abe59f7696ed5231d8f` (919 files verified before changes).

| Build | Scope | Folder | Status |
| --- | --- | --- | --- |
| 01 / 0.4.2 | Today's data and stats disappearing during refresh | [01-today-data-fix](01-today-data-fix/README.md) | Building phone-test candidate |
| 02 | Add and retain activities in the app | Planned | After build 01 phone review |
| 03 | Advanced strength tracking with sets, reps, routines, rest timer, muscle workload and progression | Planned | Separate feature build |
| 04 | Run route and GPS graphs | Planned | Separate feature build |
| 05+ | Direct Galaxy Watch 8 connection and individual sensor features | Planned | See roadmap |

Each delivered build folder contains its change notes, test notes, APK checksum and a GitHub Release link.
The APK is kept in this folder locally and uploaded as a Release asset; binaries are not committed into Git.
Later APKs use the same private signing key and package name so they can update this fork while keeping its data.
The signing key is stored locally in `.release-signing/`; that entire folder is excluded from Git.

Upstream Pulse is licensed under PolyForm Noncommercial 1.0.0. Its license and copyright notices are retained.
