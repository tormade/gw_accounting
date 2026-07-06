## Parent

Parent: #1

## What to build

Reduce the visible main navigation to `Arbeiten`, `Rechnungen`, and `Verwaltung`. The old top-level areas `Heute`, `Kunden`, `Bestellungen`, and `Belege` must no longer appear as equal main navigation items. Existing functionality should be preserved by placing the daily work path under `Arbeiten`, the invoice/payment path under `Rechnungen`, and admin tools under `Verwaltung`.

## Acceptance criteria

- [ ] The main navigation shows exactly `Arbeiten`, `Rechnungen`, and `Verwaltung`.
- [ ] `Bestellungen` and `Belege` no longer appear as top-level navigation entries.
- [ ] `Rechnungen` opens the existing invoice/open-items workplace.
- [ ] `Verwaltung` exposes admin tools for customers, products, import, checklist items, and document archive.
- [ ] Existing invoice/payment and admin functions remain reachable.
- [ ] UI tests cover the new visible navigation and the absence of old top-level entries.

## Blocked by

None - can start immediately.
