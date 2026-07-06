## Parent

Parent: #1

## What to build

Make order intake usable inline inside the focused customer workplace in `Arbeiten`. The user should not need to switch to a separate top-level `Bestellungen` area. Reuse existing order-entry logic where possible, but present it as part of the customer workflow.

## Acceptance criteria

- [ ] `Neue Bestellung aufnehmen` opens order intake inside `Arbeiten`.
- [ ] The order intake shows the selected customer context.
- [ ] Recommended/previously ordered articles can be used in the order.
- [ ] Known articles with quantity `0` or empty quantity can remain visible for documents.
- [ ] Pfand-Rückgabe can be entered separately from article deposit.
- [ ] Saving the order keeps the user in `Arbeiten`.
- [ ] After saving, `Lieferschein erstellen` is the clear primary action.
- [ ] Tests cover inline order intake from customer context.

## Blocked by

- #4
