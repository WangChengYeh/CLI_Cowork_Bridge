# CCB Room + iMessage Runtime Status

Status snapshot for milestones 1 through 10.

Related proposal:

- `docs/proposals/ccb-cli-imessage-room.md`
- `docs/proposals/ccb-cli-imessage-room-todo.md`

---

# Current System State

The repository now contains a functional architectural foundation for:

```text
CLI ↔ RoomEvent Bus ↔ iMessage
```

with synchronized multi-agent coordination between:

```text
You
Codex
Claude
Gemini
```

The system currently supports:

- shared room event model
- shared parser grammar
- room event persistence
- CLI transport helpers
- dispatcher preparation layer
- iMessage outbound delivery
- iMessage inbound watcher
- reply correlation
- transport synchronization foundation

---

# Milestone Completion Status

## Milestone 1 — Shared Room Event Model

Status: completed.

Implemented:

```text
lib/room/models.py
lib/room/parser.py
```

Features:

- RoomEvent dataclass
- RoomEventType enum
- RoomSource enum
- validation
- serialization/deserialization
- shared parser
- aliases
- @all
- @status

---

## Milestone 2 — Room Event Store

Status: completed.

Implemented:

```text
lib/room/store.py
```

Features:

- JSONL persistence
- append
- list
- load by id
- cursor tracking
- tailing
- audit logging
- transport bindings

Runtime layout:

```text
.ccb/room/
  events.jsonl
  audit.jsonl
  cursors/
  transport-bindings.json
```

---

## Milestone 3 — Shared Command Parser

Status: completed.

Supported commands:

```text
@codex
@claude
@gemini
@all
@status
```

Shared between:

- CLI
- iMessage

---

## Milestone 4 — CLI Transport Integration

Status: partially completed.

Implemented:

```text
lib/cli/room.py
```

Features:

- send_room_message()
- list_room_events()
- render_room_events()

Pending:

- real CLI entrypoint wiring
- ccb room subcommands
- live tail mode

---

## Milestone 5 — Dispatcher Bridge

Status: foundation completed.

Implemented:

```text
lib/room/dispatcher.py
```

Features:

- RoomDispatchRequest
- TASK_SUBMITTED lifecycle events
- ask argv normalization
- broadcast detection
- correlation preparation

Pending:

- real ccb ask runtime execution
- live agent streaming

---

## Milestone 6 — iMessage Outbound MVP

Status: completed.

Implemented:

```text
lib/imessage/applescript.py
lib/imessage/sender.py
lib/imessage/doctor.py
```

Features:

- AppleScript generation
- osascript execution
- dry-run support
- message chunking
- doctor checks

---

## Milestone 7 — Room-to-iMessage Delivery Policy

Status: completed.

Implemented:

```text
lib/room/imessage_delivery.py
```

Features:

- delivery policy
- notify filtering
- dedupe
- transport delivery events
- iMessage formatting

---

## Milestone 8 — iMessage Inbound Watcher

Status: completed.

Implemented:

```text
lib/imessage/watcher.py
```

Features:

- chat.db read-only polling
- allowlist
- prefix filtering
- dry-run mode
- cursor tracking
- audit logging
- RoomEvent conversion

---

## Milestone 9 — iMessage Dispatch Bridge

Status: completed.

Implemented:

```text
lib/room/imessage_dispatch.py
```

Features:

- iMessage event dispatch
- TASK_SUBMITTED correlation
- RoomDispatcher integration

---

## Milestone 10 — Reply Correlation

Status: completed.

Implemented:

```text
lib/room/imessage_correlation.py
```

Features:

- reply correlation binding
- recipient restoration
- chat/thread restoration
- reply transport metadata

---

# Remaining Major Work

The architecture layer is now mostly complete.

The remaining work is primarily:

```text
real runtime integration
```

---

# Remaining Critical Integration Tasks

## 1. Real ccb ask runtime integration

Currently:

```text
RoomDispatcher
  ↓
ask argv preparation
```

Needed:

```text
RoomDispatcher
  ↓
actual ccb ask runtime execution
```

The room layer must invoke the real execution path for:

- Codex
- Claude
- Gemini

---

## 2. Agent reply streaming

Currently:

```text
reply events are synthetic helpers
```

Needed:

```text
real streaming replies
```

The runtime should convert live provider output into:

- AGENT_MESSAGE
- TASK_COMPLETED
- TASK_FAILED
- APPROVAL_NEEDED

---

## 3. Real CLI integration

Currently:

```text
CLI helper module only
```

Needed:

```bash
ccb room send
ccb room tail
ccb room status
ccb imessage watch
```

wired into the real CLI entrypoint.

---

## 4. Background watch mode

Currently:

```text
manual polling only
```

Needed:

```text
persistent watch/daemon mode
```

Potential future:

```text
ccbd room supervisor
```

---

## 5. Multi-agent orchestration

Currently:

```text
single-event dispatch preparation
```

Needed:

```text
parallel @all fanout
agent-to-agent coordination
shared summaries
approval workflows
```

---

# Current Architectural Result

The repository now contains the foundation for:

```text
human-in-the-loop
multi-agent collaboration runtime
```

with synchronized transports:

```text
CLI
↕
RoomEvent Bus
↕
iMessage
```

and participants:

```text
You
Codex
Claude
Gemini
```

The remaining work is primarily runtime execution integration rather than foundational architecture.
