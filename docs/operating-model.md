# Operating Model

## Core loop

```
RHYTHM
  ↓
WITNESS
  ↓
CONDITION
  ├─ Good  → return to rhythm
  ├─ Watch → carry forward into future witnesses
  └─ Act   → route
               ↓
              WORK
               ↓
            RESOLUTION
               ↓
             RHYTHM
```

## Rhythm

A rhythm describes a responsibility that deserves continued attention. It is not necessarily a recurring task.

Examples:
- Daily water-system witness
- Daily sewer-system witness
- Main Street trash condition
- Park grounds during growing season
- Equipment inspection by operating interval
- Snow/ice response when conditions warrant

Rhythms may be calendar-, seasonal-, interval-, event-, or condition-driven.

## Witness

A witness is a dated observation of a place, system, or asset in the context of a rhythm or incoming condition.

The ordinary field vocabulary is deliberately small:

- **Good** — no intervention indicated.
- **Watch** — changed or noteworthy; retain attention.
- **Act** — intervention is indicated.

## Condition

A condition may persist across multiple witnesses. It can accumulate history before, during, and after intervention.

A condition may originate from:
- Rhythm observation
- Employee observation
- Citizen report
- Alarm or system signal
- Office request
- Planned maintenance

## Route

Routing determines where attention belongs without necessarily creating a formal work order.

Possible routing states can include:
- Now
- Today
- Upcoming
- Watch
- Office
- Project

Rules should infer the route when confidence is high and ask the worker only when judgment is actually required.

## Work

Work is intervention prompted by a condition or by planned activity. A work session inherits its context from the condition so the worker does not re-enter location, asset, service area, or reason for work.

During work, the field interface should primarily expose:
- elapsed work
- add material
- add significant equipment
- voice
- photo
- finish

## Resolution

Finishing work is not merely closing a record. Ask what condition remains:

- Good
- Watch
- Still needs work

The resulting condition determines whether the matter resolves or returns to the routing/rhythm loop.

## Routine action, work order, project

Administrative structure should scale with the underlying work:

```
Condition → Routed Action → Work Order → Project
```

Most routine Public Works activity should never require a formal work order.

## Field-interface test

The first prototype should be understandable as if it were physical controls on a plywood panel:

```
GOOD     WATCH     ACT

START     ADD      DONE

SAY      SHOW
```

If an interaction cannot be made simple at this level, first ask whether the backend can absorb the complexity before adding another field control.
