# board rules

## terminology
ticket: generic term for any item in an epic
story: alias for a `feat`-type ticket; "As a X, I want Y" format applies to stories only; other types have no prescribed format

## ticket numbering
Tickets are numbered per-epic or per-file: T1, T2, …
Numbers must read sequentially (T1, T2, T3 …) top-to-bottom with no gaps. The file is the source of truth for execution order.

## ticket type
All tickets have a `type` field. Valid values mirror the conventional commits specification:
`feat`, `fix`, `docs`, `style`, `refactor`, `test`, `perf`, `ci`, `chore`, `build`, `revert`

## epic scope
All epics have a `scope` field: short human-readable name used in commit messages (e.g. `migrator`, `cli`).

## ticket statuses
Valid values: IDEATION, READY, IN PROGRESS, DONE, DISCARDED.

Lifecycle: READY → IN PROGRESS → DONE.

DISCARDED tickets stay in their file. Do not delete or renumber.

## epic status
- READY: all tickets READY, none started
- IN PROGRESS: any ticket is IN PROGRESS, or DONE, but not all tickets are DONE or DISCARDED
- DONE: all tickets DONE or DISCARDED; final and cannot be reopened

New work discovered after an epic is DONE goes into the current epic — do not reopen.

When updating a ticket status, check whether the change requires updating the parent epic status (e.g. last ticket going DONE closes the epic; first ticket going IN PROGRESS opens the epic). Update index.yaml accordingly in the same commit.

## commit convention
Code commits: `type(scope): description [EPIC-XX/TN]` — ticket ID in the title makes git log self-contextualizing without scanning epic files. `type` and `scope` are taken directly from the ticket; epic tickets inherit scope from the parent epic.

Board-only commits (status updates, grooming, meta-work): `chore(board): description`. No ticket ID required. `board` is a reserved scope — nothing else uses it.

Agent-facing commits (anything under `.claude/` except board YAML files, plus `CLAUDE.md`): `chore(agent): description`. No ticket ID required. `agent` is a reserved scope — nothing else uses it. Board YAML status updates and grooming remain `chore(board):`.

Board status updates can be standalone commits within the branch. The commit that transitions a ticket to DONE carries a `Closes EPIC-XX/TN` footer for traceability. Place it after `Co-Authored-By` if present.

## release order
The `ready` and `ideation` lists in `index.yaml` are maintained in planned release order — top entry ships next. Reordering these lists requires explicit owner approval.

A release requires a SemVer tag if the epic contains any `feat` or `fix` tickets. Pure `ci`/`chore`/`docs` epics do not.

## grooming convention
Grooming commits include the epic file and any corresponding index.yaml changes.

## epic filenames
Epic yaml files use lowercase: `epic-07.yaml` not `EPIC-07.yaml`. The `id:` field inside the file stays uppercase (`id: EPIC-07`).

## yaml integrity
Edit field values only. Never add or remove keys from epic or ticket entries.
Intentional schema changes (e.g. adding a new field to all epics) are exceptions and require an explicit decision.
