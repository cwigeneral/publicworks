# Public Works

A small-town public works operations platform built around stewardship rather than paperwork.

## Design premise

**Primitive interface. Sophisticated backend.**

The person in the field should communicate with the system in the smallest meaningful way possible. The system should derive, relate, route, remember, and report everything it reasonably can without asking the worker to become a clerk.

The core operating loop is:

```
Rhythm → Witness → Condition → Route → Work → Resolution → Rhythm
```

The first prototype is intentionally narrow: establish a rhythm, witness a place or asset, record **Good / Watch / Act**, and allow conditions requiring attention to route themselves into the work view.

See `docs/principles.md`, `docs/operating-model.md`, and `docs/data-model.md`.
