Build 01 fixes two reproducible causes of today's data/stats disappearing during a Health Connect refresh:
partial daily rows overwriting known vitals, and failed re-imports leaving cleared data behind.

Imports now commit atomically, change tokens advance after commit, and previous scores stay until rescoring.
The app keeps Pulse's existing screens and scoring formulas. See `builds/01-today-data-fix/` for the full notes.

Install `pulse-mobile-0.4.2-arm64.apk` on your paired Android phone. It is named **Pulse Monarch** and installs
alongside upstream Pulse. It has its own Health Connect permissions/database. This is a signed release build
for phone testing; it has not been tested on the owner's physical phone or Galaxy Watch 8 yet.

Workout logging, advanced strength tracking, GPS graphs and direct Samsung sensor collection are separate later builds.
