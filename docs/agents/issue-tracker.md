# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues in `tormade/gw_accounting`. Use the `gh` CLI for issue operations when GitHub access is available.

## Conventions

- Create an issue: `gh issue create --title "..." --body "..."`
- Read an issue: `gh issue view <number> --comments`
- List issues: `gh issue list --state open --json number,title,body,labels,comments`
- Comment on an issue: `gh issue comment <number> --body "..."`
- Apply or remove labels: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- Close an issue: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` does this automatically inside the clone.

## Pull requests as a triage surface

PRs as a request surface: no.

Do not pull external PRs into the same queue as feature requests or support issues. Treat PRs as code-review or integration work unless Thomas explicitly asks otherwise.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The map is a single issue with child issues as tickets.

- Map: a single issue labelled `wayfinder:map`, holding Notes / Decisions-so-far / Fog body.
- Child ticket: an issue linked to the map as a GitHub sub-issue when available. If sub-issues are unavailable, add `Part of #<map>` at the top of the child body.
- Blocking: prefer GitHub native issue dependencies when available. If unavailable, use a `Blocked by: #<n>` line at the top of the child body.
- Frontier query: list the map's open children, skip assigned or blocked issues, and pick the first unblocked ticket.
- Claim: `gh issue edit <n> --add-assignee @me`.
- Resolve: comment with the result, close the child issue, and update the map with the decision/context pointer.
