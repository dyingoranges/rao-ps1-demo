"""Main API/worker pipeline in a fresh interpreter, with durable diagnostics."""
import argparse
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=30)
    parser.add_argument("--scenarios", nargs="+", choices=["A", "B", "C"], default=list("ABC"))
    parser.add_argument("--demo-dates", action="store_true")
    args = parser.parse_args()
    if args.seconds <= 0:
        parser.error("seconds must be positive")
    if args.demo_dates and args.instance.resolve() != (ROOT / "data/calendar-demo").resolve():
        parser.error("Synthetic date mapping is allowed only for data/calendar-demo.")
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    os.environ["RAO_DATABASE_URL"] = "sqlite:///" + str(out / "schedule.db")
    os.environ["RAO_START_INPROCESS_WORKER"] = "false"
    os.environ["RAO_QUEUE_BACKEND"] = "memory"
    from app.main import create_app
    from app.modules.instance import load_instance
    from app.workers.rail_solver_worker import process_next_job
    from fastapi.testclient import TestClient
    from httpx import HTTPError
    from icalendar import Calendar

    instance = load_instance(args.instance)
    print(f"Validated input: {len(instance.activities)} activities; "
          f"{len(instance.contracts)} contracts", flush=True)
    summary = {"instance": str(args.instance), "demo_dates": args.demo_dates, "jobs": []}

    def save(name, value):
        (out / name).write_text(json.dumps(value, indent=2), encoding="utf-8")

    def require(response):
        response.raise_for_status()
        return response

    with TestClient(create_app()) as client:
        run = require(client.post("/api/v1/runs", files=[
            ("files", (p.name, p.read_bytes(), "text/csv"))
            for p in sorted(args.instance.glob("*.csv"))
        ])).json()
        summary["run_id"] = run["id"]
        save("SUMMARY.json", summary)
        for scenario in dict.fromkeys(args.scenarios):
            row = {"scenario": scenario, "ready": False}
            try:
                job = require(client.post(f'/api/v1/runs/{run["id"]}/jobs', json={
                    "scenario": scenario, "time_limit_seconds": args.seconds,
                })).json()
                row["job_id"] = job["id"]
                print(f"{scenario}: preparing model; {args.seconds}s search budget…", flush=True)
                process_next_job(timeout=0)
                base = f'/api/v1/runs/{run["id"]}/jobs/{job["id"]}'
                state = require(client.get(base)).json()
                save(f"JOB_{scenario}.json", state)
                row["state"] = state["state"]
                row["solver_status"] = (state.get("result") or {}).get("status")
                if state["state"] != "COMPLETED":
                    row["error"] = state.get("error") or "No validated solution; see JOB JSON."
                    continue
                save(f"REPORT_{scenario}.json", require(client.get(base + "/report")).json())
                save(f"WITNESS_{scenario}.json", require(client.get(base + "/schedule")).json())
                calendar = require(client.get(base + "/calendar")).json()
                if args.demo_dates:
                    start = date.fromisoformat(calendar["horizon_start"])
                    bindings = {}
                    for event in calendar["events"]:
                        if not 1 <= event["physical_night"] <= 7:
                            raise ValueError("More than seven physical slots need explicit date planning.")
                        key = f'{event["week"]}:{event["physical_night"]}'
                        bindings[key] = str(start + timedelta(
                            weeks=event["week"] - 1, days=event["physical_night"] - 1))
                    calendar = require(client.post(base + "/calendar/publish", json={
                        "date_bindings": bindings,
                    })).json()
                    raw = require(client.get(base + "/calendar/ics")).content
                    parsed = Calendar.from_ical(raw).walk("VEVENT")
                    expected = {f'{calendar["schedule_version"]}.{e["possession_id"]}@rao'
                                for e in calendar["events"]}
                    if len(parsed) != len(expected) or {str(e["UID"]) for e in parsed} != expected:
                        raise ValueError("ICS does not match the possession snapshot.")
                    (out / f"SCENARIO_{scenario}.ics").write_bytes(raw)
                save(f"CALENDAR_{scenario}.json", calendar)
                (out / f"SCENARIO_{scenario}.zip").write_bytes(
                    require(client.get(base + "/export")).content)
                row.update(ready=True, possessions=len(calendar["events"]),
                           authority=calendar["validator_authority"], scores=calendar["scores"])
            except (HTTPError, ValueError, RuntimeError) as exc:
                row["error"] = str(exc)
            finally:
                summary["jobs"].append(row)
                save("SUMMARY.json", summary)
                print(json.dumps(row), flush=True)
    return 0 if all(row["ready"] for row in summary["jobs"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
