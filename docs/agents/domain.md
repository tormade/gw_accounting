# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- `CONTEXT.md` at the repo root when it exists.
- `docs/adr/` for architectural decisions that touch the area being changed.
- `AGENTS.md` for always-current local development rules, architecture invariants, data rules, onboarding principles, and milestone process.

If `CONTEXT.md` or `docs/adr/` do not exist yet, proceed silently. Do not block work on their absence. Domain-modeling or architecture skills may create them later when useful.

## File structure

This is a single-context repo:

```text
/
├── AGENTS.md
├── CONTEXT.md
├── docs/adr/
└── src/
```

There is no monorepo context map. If a `CONTEXT-MAP.md` is introduced later, this file should be updated.

## Use the glossary's vocabulary

When output names a domain concept, prefer terms already used in `AGENTS.md`, `CONTEXT.md`, and the codebase. Important current terms include:

- Kunde
- Bestellung
- Lieferschein
- Rechnung
- Beleg
- Pfand-Rueckgabe
- Kundensortiment
- Pruefliste
- Stammdaten

If a needed concept is missing from the glossary, note it for domain modeling instead of inventing competing terms.

## Flag ADR conflicts

If a proposal or implementation contradicts an existing ADR, surface it explicitly rather than silently overriding it.
