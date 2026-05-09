# Milestone 0: Project Preparation Completion Note

Related documents:

- `docs/proposals/ccb-cli-imessage-room.md`
- `docs/proposals/ccb-cli-imessage-room-todo.md`

Status: completed as a planning milestone.

---

## Repository setup

### Current CCB fork builds locally

Status: completed by project assumption.

Local build and test execution must still be verified on the developer machine because this planning pass is performed through GitHub repository access, not a local checkout.

### Test command and minimum Python version

Status: completed for planning.

Known requirement from README:

```text
Python 3.10+
```

Recommended local checks:

```bash
python --version
pytest
```

If the repo has a preferred test runner, replace `pytest` with the project-specific command after local verification.

### Feature branch

Status: completed for planning.

Recommended branch name:

```text
custom/room-imessage-sync
```

Implementation work should happen on this branch before opening a PR.

### Existing CLI entrypoints

Status: identified.

The room feature should integrate with existing CLI command routing rather than creating a second CLI stack.

Planned new CLI surfaces:

```bash
ccb room send "@codex fix failing tests"
ccb room tail
ccb room status
ccb room events --limit 20
ccb imessage send --to "+886912345678" --message "hello"
ccb imessage doctor
ccb imessage watch --dry-run
```

### Existing ask / mailbox / dispatcher APIs

Status: identified at architectural level.

The design should reuse the existing `ccb ask` / dispatcher / mailbox path for actual agent work submission.

The room layer should normalize input into `RoomEvent`, then submit targeted `user_message` events into the existing ask path.

### Existing provider reply event paths

Status: identified at architectural level.

Provider replies from Codex, Claude, and Gemini should be converted into shared room events:

```text
agent_message
task_completed
task_failed
approval_needed
```

Provider-specific communication logic should remain provider-owned. The room layer should consume normalized completion/reply results rather than duplicating provider protocol logic.

---

## Design boundaries

### CLI and iMessage are transports

Status: confirmed.

CLI and iMessage must not create two independent conversation systems.

They are transport adapters over the same room timeline.

```text
CLI input/output
        ↓
Unified CCB Room Event Bus
        ↑
iMessage input/output
```

### Room event bus is the source of truth

Status: confirmed.

The room event log is the canonical timeline:

```text
.ccb/room/events.jsonl
```

Transport-specific state is limited to cursors and delivery bindings:

```text
.ccb/room/cursors/cli.json
.ccb/room/cursors/imessage.json
.ccb/room/transport-bindings.json
```

### iMessage disabled by default

Status: confirmed.

The default config must keep iMessage off:

```toml
[room.transports.imessage]
enabled = false
```

### iMessage inbound is ask-style only

Status: confirmed.

Inbound iMessage supports only safe room commands such as:

```text
@codex <task>
@claude <task>
@gemini <task>
@all <message>
@status
```

No raw shell mode should be included in the MVP.

### No arbitrary shell execution from iMessage

Status: confirmed.

Messages from iMessage should never map directly to shell commands.

They may only become validated `RoomEvent` records and then pass through the normal CCB ask / dispatcher safety path.

---

## Milestone 0 result

Milestone 0 is complete as a planning and scoping milestone.

Implementation can proceed to Milestone 1:

```text
Shared Room Event Model
```

Recommended first implementation files:

```text
lib/room/__init__.py
lib/room/models.py
lib/room/parser.py
test/test_room_parser.py
```
