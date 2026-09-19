# Start here — reviewed PS1-core Colab package

1. Extract the delivery ZIP and locate `RAO_Reviewed_Colab.ipynb`.
2. In Google Colab, choose File → Upload notebook, and upload that file.
3. Use a fresh CPU runtime and choose Runtime → Run all.
4. The notebook already embeds the reviewed Python project and CSV inputs. Do not
   upload one of the older project ZIPs. No ZIP selection is required.
5. The first run uses a three-activity synthetic PC+C+C demonstration. It generates
   one physical possession per scenario, validates it and exports demo-date ICS.
6. For the full 54-activity input, change DATASET to `public-instance`, then rerun
   the dataset, solve, display and download cells. This uses physical slot views;
   real dates are not inferred. Increase the search budget if needed, without any
   guarantee of an optimal result or a solution within that budget.
7. For your own data, set UPLOAD_CUSTOM_CSVS=True and select the eight CSV files.
8. Download results from the last cell. Diagnostics are retained even if some
   scenarios fail; only accepted jobs produce calendars and submission exports.

The full React website is included in `frontend`; the notebook displays its own
inline possession view using the same backend response. See CALENDAR_DEMO.md for
running the website. Colab is not used to host a separate web server.

## Why the old import failed

`app` is the source package in `backend/app`. Installing with pip in a subprocess
does not reliably update an already-running notebook kernel's editable-package
import hooks. The old notebook did not insert the backend path into the kernel.
The new notebook explicitly adds the resolved backend directory to sys.path,
invalidates import caches, and checks app.__file__. Its worker also runs in a
fresh interpreter with an explicit source path.

If a different `app` was already imported, restart the runtime and Run all. Do not
install a similarly named package from PyPI; that would not be this project's code.

The old runner also used `python -m app.modules.solver`. That entrypoint exists in
the older full-project package but not in the uploaded PS1-core branch. The new
runner uses `scripts/colab_run.py` and the actual Main API/worker/persistence pipeline.

## Files for your team

- RAO_Reviewed_Colab.ipynb: self-contained notebook.
- PRESENTATION_SCRIPT.md: approximately five-minute talk, demo cues and judge Q&A.
- REVIEW_NOTES.md: findings, test evidence and limits.
- scripts/colab_run.py: real solve/witness/validator/calendar/export runner.
- backend and frontend: reviewed source, including the possession calendar.

The earlier activity calendar based on Friday/Saturday/Sunday display assumptions
is superseded by this physical-witness view. Do not merge the four old packages
into one backend folder.
