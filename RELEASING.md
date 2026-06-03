# Releasing

Production deploys are triggered by pushing a CalVer tag. The tag is the deploy decision — always manual. A release typically includes multiple PRs.

Commit convention follows `.claude/board/rules.md`.

## PR scope

One ticket = one PR. Include more only when tickets are directly dependent (e.g. a chore that unblocks the feat in the same PR). Keep PRs lean — a focused PR is easier to review and revert.

Keep the PR description current: update the summary when new commits change the scope, and tick test plan items as CI validates them.

Omit the test plan section when there is nothing to test — changes confined to `.claude/` files, `.md` files, or other non-executable assets do not require one.

## Local setup

After cloning, activate the pre-commit hook:
```bash
git config core.hooksPath .githooks
```

## Branching

Work on short-lived feature branches cut directly from `main`. Branch name mirrors the commit type and scope: `type/scope` (e.g. `feat/cost-tracker`, `ci/deployment`, `fix/kanban`). Delete the branch after the PR merges.

Each branch gets its own Cloudflare Pages preview deployment.

## Release planning

Releases are planned in `.claude/board/roadmap.yaml`. Each release bundles one or more complete epics and any relevant maintenance tickets. Never ship a partial epic.

A release requires a CalVer tag if the epic contains any `feat` or `fix` tickets. Pure `ci`/`chore`/`docs` epics do not.

## Process

Before writing any status value to a board file, confirm the ticket's current status and that the intended transition is the immediate next step. The only valid moves are READY → IN PROGRESS (work starts), IN PROGRESS → TESTING (PR created), TESTING → DONE (CI passes). Any other jump is wrong.

1. Mark the ticket IN PROGRESS. Cut a branch from main:
   ```bash
   git fetch origin
   git switch -c type/scope origin/main
   ```
2. Commit following conventional commits.
3. `git push origin type/scope`
4. Create the PR:
   `/opt/homebrew/bin/gh pr create --base main --head type/scope --repo nicobc/patos`
   - If the PR has a test plan (manual verification needed): commit the TESTING board update now, before watching CI.
   - If the PR has no test plan: skip the TESTING commit — go straight to step 6 after CI passes.
5. `sleep 5` then watch all PR checks: `/opt/homebrew/bin/gh pr checks <n> --repo nicobc/patos --watch`
   - CI is the authoritative source of truth — local tests passing is not sufficient.
   - CI failure → fix and return to step 2. Never merge a failing PR.
6. CI passes. Commit the DONE board update with `Closes EPIC-XXX/TN` footer before merging. Push it, then re-watch checks before attempting merge:
   `sleep 5 && /opt/homebrew/bin/gh pr checks <n> --repo nicobc/patos --watch`
7. Get explicit approval before merging. PR title must follow conventional commits — it becomes the squash commit message on main.
   `/opt/homebrew/bin/gh pr merge <n> --squash --delete-branch --repo nicobc/patos`
8. Clean up local branch:
   ```bash
   git switch main
   git pull origin main
   git branch -D type/scope
   ```
   `-D` required — squash merges leave the local branch unrecognised as merged by git.
9. _(Only if `deploy: true` for this release in `.claude/board/roadmap.yaml`)_ Create and push a CalVer tag from main:
   ```bash
   git fetch origin main
   git tag vYYYY.MM.N origin/main
   git push origin vYYYY.MM.N
   ```
   Increment the patch number within the month (e.g. `v2026.05.2` follows `v2026.05.1`).
   Watch deploy: `/opt/homebrew/bin/gh run watch <run-id> --repo nicobc/patos`. Report success or failure.

## GHA workflow testing

When iterating on a GHA workflow: commit and push the change, dispatch with `gh workflow run <file> --ref <branch> --repo nicobc/patos`, then immediately watch with `gh run watch <run-id> --repo nicobc/patos`. On failure, fetch logs with `gh run view <run-id> --log-failed --repo nicobc/patos`, diagnose, fix, and repeat — without waiting for the user to paste output. `gh` is at `/opt/homebrew/bin/gh`.
