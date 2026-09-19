# RAO — presentation script (approximately 5 minutes)

Replace speaker names with your teammates. Bracketed text is a demo cue, not spoken text.
Use the small synthetic co-sharing dataset for the live demonstration; say that it is
synthetic. Use the full public dataset for discussing scale and trade-offs.

## Opening — 30 seconds

“Our project is Railway Access Optimisation, or RAO. It helps plan when different
contractors can access railway locations for maintenance and construction.

The challenge is that many activities need the same limited access opportunities.
They also have safety restrictions, deadlines and dependencies. Allocating each
activity separately can create conflicts elsewhere in the network.

Our system takes the project and railway data, searches for a schedule, checks its
physical feasibility, and presents the accepted result as an operational calendar.”

## DEV1: understand and validate the input — 45 seconds

[Show the input summary: eight CSV files, activity count, contract count.]

“The first stage takes eight CSV files describing the lines, stations, sectors,
location supply, safety-buffer rules, planning horizon, contracts and activities.

DEV1 turns these files into a consistent internal representation. We check file
structure, identifiers, references and activity dependencies before scheduling.
We then expand each activity’s route and determine the safety areas it affects.
For example, an activity may need a buffer, an opposite-bound restriction or an
interchange restriction.

This stage matters because even a powerful optimiser cannot produce a trustworthy
answer if its inputs or network interpretation are wrong.”

## DEV2: compare scheduling policies — 60 seconds

[Show scenario selection.]

“We use Google OR-Tools CP-SAT to represent scheduling decisions and constraints.
The model assigns activities to weeks and physical access slots while respecting
the rules encoded in our implementation.

We support three scenarios. Scenario A keeps access supply strict and can accept
completion delays. Scenario B keeps planned completion dates strict and can use
additional supply and extended access, with penalties. Scenario C balances delay,
limited supply flexibility and ECLO restrictions.

These are different policies with different objectives. A lower numeric score in
one scenario is not automatically better than a score in another scenario.

We also set a search time budget. A feasible solution is not necessarily optimal.
If the search returns unknown or times out without a solution, we show that status
instead of pretending that a valid schedule has been found.”

## DEV3: establish assurance — 60 seconds

[Show the job status, validator report and physical witness.]

“A solver result is only the beginning. We persist a physical witness that records
which physical night each access uses. This is separate from access_night, which
is the contract-local accounting index in the submission format.

The physical checker rechecks simultaneous access, possession mixes, safety
closures, capacity and workfront limits. The validator also checks the complete
workload and the submission rules.

Only a completed schedule with complete workload, a passing physical witness and
zero hard validator violations can pass our calendar and CSV export gates.

In this demonstration, the report is produced by our bundled fallback validator.
We label it honestly: it is not the organisers’ official validator. Our automated
tests provide evidence for the implemented rules, not a guarantee about unseen
datasets or unresolved interpretations in the problem statement.”

## DEV4: operational calendar — 60 seconds

[Open Calendar. Click the PC + C + C possession.]

“The calendar is a view of the validated schedule, not another scheduling engine.
One event represents one physical possession. Here, one PC activity and two C
activities share a physical possession, so we display one event with three member
activities rather than three separate bookings.

The event includes the physical slot, occupied locations, contracts, sharing group,
ECLO status and the evidence recorded by the backend. Evidence explains the
recorded scheduling reasons; it is not an AI-generated justification.

In the full web application, the DTL and CCL names are optional display aliases.
The solver still uses its original identifiers, and unknown identifiers remain
visible without inventing a mapping.

The calendar also checks job identity. Switching to another job cannot leave an
old successful schedule displayed as if it belonged to a failed or unfinished job.”

## Publication and export — 40 seconds

[Show publication status and a downloaded ICS file.]

“The witness contains physical slot numbers, but not operating timestamps. We
therefore require explicit dates before publication. For this synthetic demo,
we have explicitly chosen demonstration dates; they are not real railway bookings.

Each publication has a schedule version. A newer publication supersedes the
previous version for that scenario. ICS exports use stable identifiers, with one
calendar event for each validated possession. These are date-only events because
the input does not supply operating hours.

The files are designed for import into Outlook, Google Calendar or Apple Calendar.
This is file export, not live account synchronisation. External calendar changes
must never silently overwrite the validated schedule.”

## Closing — 20 seconds

“Our contribution is the complete chain from structured input to scheduling,
physical evidence, validation and an understandable operational view. We make
trade-offs and failure states visible rather than hiding them behind a calendar.

Our next steps are to calibrate against the official validator, improve search
performance, and support replanning through new validated schedule versions.”

## Questions the judges may ask

**Does it always find the best schedule?**
“No. CP-SAT is time-bounded. We distinguish feasible results from proven optimal
results, and unknown from infeasible. The small demo completed optimally; that
does not establish optimality for the full public instance.”

**Why is the calendar not automatically Monday/Tuesday/etc.?**
“The persisted witness uses physical slot labels. Those labels are not actual
dates. Automatically treating local access_night 1 as Monday would add a scheduling
assumption that the source data has not authorised.”

**How did the full public run perform?**
“In the reviewed 30-second-per-scenario run, A and B produced accepted schedules;
C timed out with unknown status. We retained its diagnostics and did not publish
a calendar for it. Runtime and solution quality can vary.”

**Did you test Google/Outlook import?**
“We checked ICS syntax with an independent parser and verified exact event counts
and UIDs against the possession snapshot. Actual import into an external account
remains a manual acceptance step.”

**Can a user drag an event to another date?**
“Not as a direct schedule change. That should become a change request followed by
a new solve, physical witness, validation and schedule version.”

**What would you say specifically for DEV1?**
“My responsibility is making the input trustworthy and usable: parsing the eight
CSV files, checking their structure and references, validating the network and
dependencies, and preparing route and safety information for the scheduling model.”
