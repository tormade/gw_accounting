## Parent

Parent: #1

## What to build

Keep direct invoice creation available after an order, but make it secondary to `Lieferschein erstellen` and require explicit confirmation that quantities and Pfand-Rückgabe are final. A direct invoice must skip `Rücklauf offen`.

## Acceptance criteria

- [ ] `Rechnung direkt erstellen` is visible after saving an order, but visually secondary to `Lieferschein erstellen`.
- [ ] Clicking direct invoice creation asks for confirmation that quantities and Pfand-Rückgabe are final.
- [ ] Cancelling the confirmation does not create an invoice.
- [ ] Confirming creates the invoice through existing document generation.
- [ ] Direct invoice creation does not add the order to open returns.
- [ ] Tests cover confirm and cancel paths.

## Blocked by

- #5
