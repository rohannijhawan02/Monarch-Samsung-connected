# Changes

Two data-loss paths were reproduced in automated tests:

1. A partial refresh generated a daily metrics row with steps/calories but null vitals. Replacing the stored row
   discarded previously imported HRV, resting heart rate, breathing rate and temperature.
2. A re-import cleared imported rows before all per-day sensor reads had completed. A later read failure could
   leave the app with missing raw data and scores even though an earlier sync had succeeded.

The fix:

- Commit Health Connect imports in one SQLite transaction, through the Store contract. A failed import rolls back.
- Keep each previously known daily metric when a normal refresh supplies no replacement for that field.
  Actual corrections, including a numeric zero, still replace the previous value.
- Advance Health Connect change tokens and the importer version only after the database commits.
- Preserve stored scores during re-imports until the pipeline has replacement scores, and mark the affected days
  dirty so the pipeline recalculates them.
- Defer destructive replacement if a previously granted record permission was revoked or a read skipped malformed
  records. The last committed data remains visible while the sync error is available in existing diagnostics.
- Preserve the existing handling of genuine Health Connect deletions; it remains covered by regression tests.

Importer version is 9. Scoring formulas and the screens are unchanged.
The static render-safety tool also normalizes diagnostic paths so its existing checks work on Windows.
The fork has its own package, release signing key and update feed. This prevents its installer and future updates
from colliding with the original publisher's app/signature.

These findings explain reproducible loss paths in the code. Confirmation that they cover the exact intermittent
symptom on the owner's phone requires the phone checklist in TESTING.md.
