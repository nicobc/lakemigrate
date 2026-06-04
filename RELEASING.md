# Releasing

Releases are triggered by pushing a SemVer tag (`vMAJOR.MINOR.PATCH`). The tag is the release decision — always manual. A release typically includes multiple PRs.

Commit convention follows `.claude/board/rules.md`.

## PR scope

One ticket = one PR. Include more only when tickets are directly dependent (e.g. a chore that unblocks the feat in the same PR). Keep PRs lean — a focused PR is easier to review and revert.

Keep the PR description current: update the summary when new commits change the scope, and tick test plan items as CI validates them.

Omit the test plan section when there is nothing to test — changes confined to `.claude/` files, `.md` files, or other non-executable assets do not require one.

## Local setup

After cloning:
```bash
uv sync
uv run pre-commit install
```

## Branching

Work on short-lived feature branches cut directly from `main`. Branch name mirrors the commit type and scope: `type/scope` (e.g. `feat/core`, `ci/publish`, `fix/checksum`). Delete the branch after the PR merges.

## Release planning

Releases are planned in `.claude/board/` — `index.yaml` for the overview, individual epic files for ticket detail. Each release bundles one or more complete epics. Never ship a partial epic.

A release requires a SemVer tag if the epic contains any `feat` or `fix` tickets. Pure `ci`/`chore`/`docs` epics do not.

## Process

Before writing any status value to a board file, confirm the ticket's current status and that the intended transition is the immediate next step. The only valid moves are READY → IN PROGRESS (work starts), IN PROGRESS → DONE (CI passes). Any other jump is wrong.

1. Mark the ticket IN PROGRESS. Cut a branch from main:
   ```bash
   git fetch origin
   git switch -c type/scope origin/main
   ```
2. Commit following conventional commits.
3. `git push origin type/scope`
4. Create the PR:
   `/opt/homebrew/bin/gh pr create --base main --head type/scope --repo nicobc/lakemigrate`
5. `sleep 5` then watch all PR checks: `/opt/homebrew/bin/gh pr checks <n> --repo nicobc/lakemigrate --watch`
   - CI is the authoritative source of truth — local tests passing is not sufficient.
   - CI failure → fix and return to step 2. Never merge a failing PR.
6. CI passes. Commit the DONE board update with `Closes EPIC-XX/TN` footer before merging. Push it, then re-watch checks before attempting merge:
   `sleep 5 && /opt/homebrew/bin/gh pr checks <n> --repo nicobc/lakemigrate --watch`
7. Get explicit approval before merging. PR title must follow conventional commits — it becomes the squash commit message on main.
   `/opt/homebrew/bin/gh pr merge <n> --squash --delete-branch --repo nicobc/lakemigrate`
8. Clean up local branch:
   ```bash
   git switch main
   git pull origin main
   git branch -D type/scope
   ```
   `-D` required — squash merges leave the local branch unrecognised as merged by git.
9. _(Only if the release contains any `feat` or `fix` tickets)_ Create and push a SemVer tag from main:
   ```bash
   git fetch origin main
   git tag vMAJOR.MINOR.PATCH origin/main
   git push origin vMAJOR.MINOR.PATCH
   ```
   Increment patch for bug fixes, minor for new features, major for breaking changes.

## GHA workflow testing

When iterating on a GHA workflow: commit and push the change, dispatch with `gh workflow run <file> --ref <branch> --repo nicobc/lakemigrate`, then immediately watch with `gh run watch <run-id> --repo nicobc/lakemigrate`. On failure, fetch logs with `gh run view <run-id> --log-failed --repo nicobc/lakemigrate`, diagnose, fix, and repeat — without waiting for the user to paste output. `gh` is at `/opt/homebrew/bin/gh`.
