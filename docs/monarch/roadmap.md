# Monarch roadmap and upstream PR audit

Reviewed 27 October 2026 (Asia/Kolkata). Target device: Galaxy Watch 8.
Release one feature at a time, retaining Pulse's UI components, typography, navigation, honest missing-data states,
local storage and existing scoring behavior unless the feature explicitly calls for a scoring change.

## Delivery order

| Order | Feature | Acceptance criteria |
| --- | --- | --- |
| 01 | Today's data/stats disappearance | Repeat refreshes and failed imports retain the last valid data; signed APK and phone review |
| 02 | Activity logging in Pulse | Add an activity with time, sport and optional measured distance/calories; durable through sync; no duplicate credit when the watch's copy arrives |
| 03 | Advanced strength tracking | Exercise guidance/demonstrations; sets, reps, load, warmups, optional RPE; routines; draft recovery; rest timer; previous performance, PRs and muscle workload |
| 04 | Runs and GPS | Route display, distance/pace/elevation graphs where supported; permissions, pause/resume, missing GPS states and battery-aware recording |
| 05 | Direct watch connection | Wear OS companion, paired-app transport, offline persistence/acknowledgments, permissions and freshness indicators; live HR into the existing pipeline |
| 06 | Measured IBI / HRV | Samsung IBI quality/status handling; artifact-aware RMSSD; preserve measurement protocol/source; validate on real Watch 8 before use in recovery |
| 07 | Skin temperature | Direct Samsung tracker, quality/freshness, nightly aggregation only within recorded sleep, distinguish skin from core temperature |
| 08 | ECG waveform | Foreground on-demand measurement, electrode contact/sequence validation, waveform/history/export; no invented clinical diagnosis |
| 09 | Body composition | Samsung BIA, required user profile and measurement flow; retain measured fat/muscle/water and label arithmetic derived quantities |
| 10 | Blood pressure records | Import/log measured BP and show history; direct cuffless BP measurement needs a separately supported, validated route |

Hevy-like tracking does not require copying Hevy's proprietary content. A pinned public-domain alternative with 876
exercise descriptions, muscle groups and demonstration image references was verified during research:
[Free Exercise DB](https://github.com/yuhonas/free-exercise-db), commit `f00c92c7dcf1216a928a52c3706c7ce8e2f71ed5`,
Unlicense. It is not bundled into build 01. Review strength-training volume and estimated-1RM formulas separately;
muscle set counts are a workload summary, not a measurement of muscle recovery or growth.

## Pull request candidates

The list below comes from upstream PR descriptions, code excerpts, metadata and relevant maintainer comments.
The search returned 9 mobile PRs and 38 web PRs; dependency-only changes are omitted from this feature shortlist.
Proposed claims are not treated as validation. This is a candidate audit, not a full merge review. Open PRs are not
in our baseline and must be reviewed/ported against the current code before use.

| PR | Verified state at review | Useful addition | Recommendation |
| --- | --- | --- | --- |
| [Pulse Mobile #22](https://github.com/adityaongit/pulse-mobile/pull/22) | Merged; head equals our base commit | Workout deduplication, selected-day Coach context, negative-temperature chart fixes | Already present; retain its tests instead of importing it again |
| [Pulse Mobile #11](https://github.com/adityaongit/pulse-mobile/pull/11) | Open | BP record storage, Health Connect import, metadata and validation | Strong starting point for the measured-BP stage. Its old source-policy/import-version code needs porting; it cannot simply be cherry-picked |
| [Pulse Mobile #12](https://github.com/adityaongit/pulse-mobile/pull/12) | Open, depends on #11 | BP card, dual-value history chart and detail queries | Review after BP ingestion. Classification labels and educational copy need current primary-source checks before shipping |
| [Pulse Mobile #21](https://github.com/adityaongit/pulse-mobile/pull/21) | Open | Protocol eligibility for using BP in Pulse Age | Separate optional scoring change; validate coefficients/protocol and retain old nine-factor behavior for unavailable BP |
| [Pulse Mobile #23](https://github.com/adityaongit/pulse-mobile/pull/23) | Open, built on #11/#12/#21 | Relative vascular load and cuff-calibrated estimated overnight corridor | Research candidate only. This estimates a model output; it does not measure Samsung watch BP. Do not merge into the first BP-record build |
| [Pulse Mobile #10](https://github.com/adityaongit/pulse-mobile/pull/10) | Open | Avoid penalties for unlogged strength and incomplete wear days | Review missing-data handling alongside workout logging. The changed aging/VO2 coefficients are a separate scientific validation task |
| [Pulse web #57](https://github.com/adityaongit/pulse/pull/57) | Description reviewed | Count duplicate exercise records once | Useful reference for local-log/watch-record reconciliation; mobile already has a deduplicator, so compare behavior and adapt tests |
| [Pulse web #49](https://github.com/adityaongit/pulse/pull/49) | Description reviewed | 12/24-hour clock selection | Mobile already has display preferences; check parity before calling this a new feature |
| [Pulse web #52](https://github.com/adityaongit/pulse/pull/52) and [#55](https://github.com/adityaongit/pulse/pull/55) | Descriptions reviewed | MCP access for an external AI agent | Later, optional architecture decision: these use a server/auth flow and are not a direct fit for the phone-local app |

BP candidate heads recorded for reproducibility: #11 `89e6c0af7071a3955cd838b5a8ba343d8dfd18d4`,
#12 `784dff73fad4039a9a05e38c81d8ac1339112c1a`, #21 `f7a71e759391622812d6d027855050e6d0ce70cc`,
#23 `8a22b78832bd2fab2249ee41c879fa67fe4e24e5`, #10 `d2086d12e96e9472f1ee817e731674eda59f003d`.

The maintainer's [#10 review note](https://github.com/adityaongit/pulse-mobile/pull/10#issuecomment-6382830067)
confirms it targets an older Pulse Age implementation and needs rebasing onto the new engine. The
[#11 review note](https://github.com/adityaongit/pulse-mobile/pull/11#issuecomment-6382830184) confirms outdated
source-policy code, versions and localization requirements. On [#23](https://github.com/adityaongit/pulse-mobile/pull/23#issuecomment-6410047173)
the maintainer plans to review and resolve conflicts; that is not a completed review or merge.

## Direct Samsung access findings

- [Samsung Health Sensor SDK](https://developer.samsung.com/health/sensor/guide/data-specifications.html) runs on the
  watch. Documented trackers include measured HR/IBI, raw PPG, ECG, skin temperature and BIA; supported trackers
  must be checked at runtime. Watch 8 also supports additional EDA/MF-BIA capabilities on compatible software.
- [Samsung app verification](https://developer.samsung.com/health/sensor/guide/app-verification.html) requires a
  registered package/signing identity for distribution. A phone-only SDK integration cannot collect watch sensors.
- [Wear OS Health Services](https://developer.android.com/health-and-fitness/health-services) supports direct watch
  exercise/live activity data. It complements Health Connect history rather than retrieving all Samsung algorithms.
- [Samsung Health Data SDK data types](https://developer.samsung.com/health/data/guide/features/data-types.html)
  offer a separate phone-side route for stored BP/body composition and richer sleep-associated data. Its access
  requirements differ from the Sensor SDK; confirm the fields and permissions individually.
- Samsung does not list a public blood-pressure sensor tracker or a direct respiratory-rate tracker in the Sensor
  SDK specifications reviewed. Raw sensor access alone does not reproduce Samsung's BP, respiratory, sleep,
  Energy Score, apnea, antioxidant or AGEs algorithms. Each needs a supported record source or validated method.
- [GeminiMan Wellness Companion's public repository](https://github.com/ITDev93/GeminiMan-Wellness-Companion)
  contains a roadmap and video/version metadata, not reusable application source code. Its existence is not evidence
  that the ECG/BP implementation is available to copy.
- [REA](https://github.com/yuenanmu/REA) can assist static/runtime investigation when a specific APK and tools are
  available. No APK was supplied or reverse-engineered for build 01. It cannot grant Samsung sensor access or
  establish that a proprietary algorithm is scientifically valid.

## Measurement and calculation gaps to investigate before Samsung stages

Health Connect may have delayed/absent Samsung HRV, skin temperature, respiratory rate and some device-specific
records. That affects Pulse's recovery, vitals baselines/outlier flags, stress/energy estimates, and any downstream
readiness/age feature relying on those inputs. The exact gap must be checked against the owner's permission and
source diagnostics; no missing value should become zero, a normal-range value or an invented measurement.

Direct collection adds timestamps, signal quality, measured beat intervals, workout control and raw waveforms. It
also adds battery, foreground/background permission, offline sync, deduplication and measurement-protocol work.
Retain Samsung's recorded sleep stages through supported history sources until a separate sleep model is validated.
