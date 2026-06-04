Read the board, release process, and recent git history, then output a session briefing.

1. Read `.claude/board/rules.md`
2. Read `RELEASING.md`
3. Read `.claude/board/index.yaml`
4. Read epic files for all IN PROGRESS and READY epics
5. Run `git log --oneline -10`
6. Run `git status --short`
7. Run `git log origin/main..HEAD --oneline`

Output:
**Compliance** — State explicitly that board rules and release process have been read and will be followed for this session without exception.
**Active** — IN PROGRESS epics and next actionable feat ticket
**Up next** — READY feat tickets across epics, in file order
**Needs grooming** — IDEATION epics blocking progress
**Next release** — first entry in the ready list (or ideation if ready is empty): epic id, title, and whether it needs a SemVer tag (true if epic has any feat/fix tickets)
**Recent commits** — last 5, one line each
**Working tree** — git status output; omit section if clean
**Branch diff** — commits ahead of origin/main, one line each; omit section if none

Tight. No flourish.
