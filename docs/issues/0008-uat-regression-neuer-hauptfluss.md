## Parent

Parent: #1

## What to build

Run and document UAT and regression for the new main workflow. The UAT must cover both the standard delivery-note return path and the direct invoice path.

## Acceptance criteria

- [ ] UAT covers customer search -> order intake -> delivery note -> open return -> invoice.
- [ ] UAT covers direct invoice creation with final-quantities confirmation.
- [ ] UAT checks generated Excel and PDF files still exist in the customer folder.
- [ ] UAT checks known articles with empty/zero quantities remain visible on documents.
- [ ] UAT checks Pfand-Rückgabe is handled separately and correctly.
- [ ] The full automated test suite passes.
- [ ] `compileall src tests` succeeds.
- [ ] Findings and remaining risks are documented.

## Blocked by

- #2
- #3
- #4
- #5
- #6
- #7
