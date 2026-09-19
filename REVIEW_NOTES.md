# Review findings and verification

## Scope

Compared all four uploaded artifacts. The uploaded PS1-core archive matches the
base source of the possession-calendar package in the Python/TypeScript modules
apart from the expected calendar integration changes. The older full-project ZIP
and old Colab notebook belong to an earlier implementation and should not be mixed
into the current backend. This delivery combines PS1-core and its calendar extension
with a new notebook runner; it does not change the solver's scheduling algorithm.

## Issues found and corrected

1. **Notebook import path.** The old pip subprocess runs with cwd=backend, but the
   live notebook kernel's source path is never updated. Editable installation may
   register import hooks only for future interpreters. Explicitly insert the resolved
   backend directory into the kernel sys.path and verify app.__file__. No PyPI package
   named app is needed. A stale, already-imported app from another project requires
   restarting the notebook runtime.
2. **Wrong solver entrypoint for PS1-core.** The old notebook calls
   `python -m app.modules.solver`; this branch does not have solver/__main__.py.
   The new runner invokes the actual Main API/worker/persistence pipeline and stores
   both diagnostics and the physical witness.
3. **Old calendar semantics.** The old notebook used activity rows and a Friday/
   Saturday/Sunday mapping from local access_night. That is not the operational
   calendar requested for PS1-core. The replacement renders physical possessions
   from the assured calendar endpoint. Only the labelled synthetic demo uses an
   explicit demo mapping from physical slot to date. Public/custom inputs stay
   undated until dates are confirmed in the full web app.
4. **CSV export could trust a stale green flag.** get_export previously checked
   only stored ready_for_submission. It now reuses the same current persisted-row
   assurance gate as the calendar. Two regressions verify that an old green report
   cannot export a failed job or a schedule whose physical witness was removed.
5. **Failure visibility and result isolation.** The new runner saves JOB and REPORT
   diagnostics for failed scenarios, never reads old output folders, and checks
   run/job identity before rendering. The notebook clears old calendar state before
   every solve and kills its worker subprocess if a bounded overall wait expires.
6. **Initial calendar selection.** The notebook explicitly selects its first week;
   merely populating an initially empty widget's options can leave its value None.

## Verification performed

- Full reviewed backend suite: 227 tests passed before adding the two export tests.
- Expanded calendar/export regression suite: 17 tests passed, including those two
  additional tests (229 distinct backend tests covered across the runs).
- Frontend: 10 tests passed and TypeScript/Vite production build succeeded.
- New notebook: executed source restoration, exact import-origin check, pip install,
  OR-Tools import, input parsing, real A/B/C worker solves and possession-view logic
  in a fresh Python 3.12 interpreter. Google-specific upload/download dialogs were
  not exercised in an authenticated Colab session.
- Synthetic co-share dataset: 3 activities/3 contracts, A/B/C OPTIMAL, one PC+C+C
  event in each calendar. ICS parsed independently and event UIDs matched snapshots.
- Full public dataset: 54 activities/14 contracts, 30 seconds search per scenario.
  A: FEASIBLE, 187 possessions, score 449.4, 6 late contracts, 336 total overrun days.
  B: FEASIBLE, 216 possessions, score 473, zero late contracts, 54 excess access units
  and 19 ECLO accesses in the validator report.
  C: TIMED_OUT / UNKNOWN, no calendar or submission export produced.
  Scores differ in formula between scenarios and are not directly ranked.

Run evidence is included under reviewed-run-evidence. Timing and heuristic search
results can vary with environment. A timeout does not prove infeasibility.

## Limits that remain

This is evidence for the tested implementation, not a proof of correctness on all
possible data. The official organiser validator was not supplied; authority stays
fallback. The branch's documented interpretation/calibration limits remain.
Physical slot labels do not specify dates, operating times or timezone. ICS is
date-only, and live external-calendar integration is not implemented. External
calendar-account import and browser visual inspection remain manual checks.
The notebook is an inline view of the backend, not the full React website.
The inherited development authentication is not production access control.

See START_COLAB.md for setup and PRESENTATION_SCRIPT.md for the talk and Q&A.
