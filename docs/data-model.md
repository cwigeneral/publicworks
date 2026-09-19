# Initial Data Model

This model is intentionally conceptual. It establishes the operational grammar before implementation details.

## Core entities

### Person
A worker or other actor who witnesses, performs, reports, or reviews activity.

### Stewardship Domain
A broad responsibility such as Water, Sewer, Streets, Parks, Facilities, or Public Realm.

### Place
A location under stewardship, such as Jackson's Garden, Main Street, a pump station, or Town Hall.

### Asset
A specific maintainable object such as a hydrant, pump, valve, sign, vehicle, or mower. An asset may belong to a place and stewardship domain.

### Rhythm
Defines what deserves continued attention and the circumstances under which it should be witnessed.

### Witness
A timestamped observation made in a known context.

### Condition
A persistent operational fact or concern. Conditions may span multiple witnesses and multiple work sessions.

Suggested initial state vocabulary:
- good
- watch
- act
- resolved

### Route
Represents where an active condition belongs operationally.

Candidate routing states:
- now
- today
- upcoming
- watch
- office
- project

### Work Session
A bounded period of intervention associated with a condition or planned work.

### Resource Use
Resources associated with work:
- labor
- materials
- equipment

### Resolution
The condition left behind after intervention: good, watch, or still requiring action.

## Relationship sketch

```
Stewardship Domain
      │
      ├── Place ── Asset
      │
    Rhythm
      │
    Witness
      │
   Condition
      │
     Route
      │
 Work Session
      │
 ┌────┼────────┐
Labor Material Equipment
      │
  Resolution
      │
    Rhythm
```

## Prototype scope

Milestone 0 should implement only enough structure to prove:

1. A user can see today's rhythms.
2. A user can enter a rhythm/place context.
3. A user can record Good, Watch, or Act.
4. Watch and Act create or update a condition.
5. Active conditions appear automatically in a routed-condition view.
6. The interaction is mobile-first and requires minimal input.

Voice, images, AI interpretation, accounting, payroll, inventory, equipment costing, GIS, and external integrations are deliberately deferred until this loop is proven.
