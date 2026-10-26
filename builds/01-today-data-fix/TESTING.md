# Validation

| Check | Result |
| --- | --- |
| Full Vitest suite | 155 files passed; 1,997 tests passed |
| Focused sync / metric-merge / SQLite transaction / render-safety checks | 4 files passed; 29 tests passed |
| TypeScript (`tsc --noEmit`) | Passed |
| ESLint | 0 errors; 8 existing upstream warnings in i18n/config.ts and queries/log.ts |
| Android Metro/Hermes export | Passed; 14 MB Hermes bundle generated |
| Native release APK build and signature | In progress; results recorded after completion |

Raw local command logs are in `logs/` and are excluded from Git. The full suite ran outside the Windows sandbox
because the sandbox's temporary worker-cache files were inaccessible. A platform-specific upstream fixture failure
was corrected by normalizing the render-safety tool's diagnostic paths; application rendering was unaffected.

Regression coverage includes partial daily metrics, import-read failure rollback, database commit failure,
change-token ordering, retaining scores until replacement, revoked permissions, actual zero corrections,
and the existing source-deletion and midnight-crossing cases.

## Phone review

No physical phone/watch test has been performed in this environment. This release is a phone-test candidate.

1. Install Pulse Monarch on the paired Android phone, allow Health Connect reads and history, then let the first
   import finish. Record which today's metrics are actually available from Samsung Health.
2. Refresh several times. Previously imported metrics should stay visible when the latest read lacks those fields.
3. Background and reopen the app, and check today's values again after a further Samsung Health sync.
4. Revoke one Health Connect read permission after a successful sync. Existing data should remain; diagnostics
   may report a changed-permissions error when a destructive replacement would otherwise be needed.
5. Restore the permission and refresh. New measurements should arrive, and corrections should replace old values.
6. Check an earlier date and refresh across midnight in the phone's configured time zone.

Report the app version, local time, which card disappeared, and the existing sync diagnostics if the symptom recurs.
The next feature build starts after this candidate has been reviewed on the phone.
