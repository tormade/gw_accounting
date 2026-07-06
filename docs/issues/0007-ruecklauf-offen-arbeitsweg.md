## Parent

Parent: #1

## What to build

Represent the delivery-note return workflow in `Arbeiten`. After a delivery note is created, the order should appear as `Rücklauf offen`. Opening a return should show a focused return workplace with a simple quantities list, Pfand-Rückgabe, and `Rechnung erstellen`.

## Acceptance criteria

- [ ] Creating a delivery note makes the order visible as an open return.
- [ ] Open returns show customer, delivery note number/date, and status in everyday language.
- [ ] Selecting an open return opens a focused return workplace.
- [ ] The return workplace shows a simple editable quantities list.
- [ ] Pfand-Rückgabe can be added in the return workplace.
- [ ] `Rechnung erstellen` creates the invoice and removes the item from open returns.
- [ ] Creating the invoice from return automatically treats quantities as final.
- [ ] Tests cover delivery note -> open return -> invoice.

## Blocked by

- #5
