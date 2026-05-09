# CCB CLI + iMessage Unified Room Proposal

## Document Role

This document is the high-level architecture proposal for the CCB CLI + iMessage unified room design.

For implementation tracking, use:

- `docs/proposals/ccb-cli-imessage-room-todo.md` — original task breakdown and backlog
- `docs/proposals/milestone-1-to-10-status.md` — current implementation status snapshot
- `docs/proposals/ccb-runtime-test-plan.md` — focused test strategy for the new runtime design

---

## Current Status

The proposal has moved beyond design-only status. The repository now includes implemented foundations for:

- shared RoomEvent model
- shared command parser
- RoomEvent JSONL store
- CLI room helpers and command routing
- iMessage outbound sender
- iMessage inbound watcher
- Room-to-iMessage delivery policy
- dispatch bridge
- reply correlation
- subprocess executor
- stream executor
- runtime supervisor skeleton
- focused `my_test` runtime validation layer

Remaining major work is runtime composition:

```text
bootstrap wiring
real DispatchWorker
real DeliveryWorker
real WatchWorker
persistent daemon lifecycle
```

---

## Vision

Create a unified collaboration room between:

- Human owner
- Codex
- Claude
- Gemini

CLI and iMessage become synchronized transports over the same CCB event bus.

---

## 4-Person Team Model

```text
You      = human owner / decision maker
Codex    = implementation agent
Claude   = architect / reviewer
Gemini   = researcher / verifier
```

---

## Core Architecture

```text
CLI
 ├── terminal
 └── iMessage
        ↓
Unified CCB Room Event Bus
        ↓
Codex
Claude
Gemini
```

All transports share the same room timeline.

---

## Unified Event Flow

### CLI Flow

```text
CLI input
  ↓
RoomEvent
  ↓
Dispatcher
  ↓
Agent reply
  ↓
CLI + optional iMessage output
```

### iMessage Flow

```text
iMessage input
  ↓
RoomEvent
  ↓
Dispatcher
  ↓
Agent reply
  ↓
iMessage + optional CLI output
```

---

## Command Grammar

Supported on both CLI and iMessage:

```text
@codex <task>
@claude <task>
@gemini <task>
@all <message>
@status
```

Implemented aliases:

```text
@code     → codex
@review   → claude
@research → gemini
```

Future grammar candidates:

```text
@stop <target>
default agent fallback
config-driven aliases
```

---

## Shared Room Event Schema

```json
{
  "event_id": "evt_123",
  "room_id": "default",
  "source": "cli|imessage",
  "sender": "you",
  "target": "codex",
  "type": "user_message",
  "body": "fix failing test",
  "correlation_id": "job_123"
}
```

---

## Transport Synchronization

### CLI

- High-frequency workspace
- Full developer control
- Multi-pane runtime

### iMessage

- Mobile control layer
- Async follow-up
- Notification surface

Users can switch between desktop and mobile without losing context.

---

## Security Model

Inbound iMessage safety rules:

- sender allowlist required
- prefix required
- no arbitrary shell execution
- audit logging
- rate limiting
- risky actions require confirmation

---

## Implementation Phases

### Phase 1

Shared RoomEvent model.

### Phase 2

CLI room timeline.

### Phase 3

iMessage outbound notifications.

### Phase 4

iMessage inbound command watcher.

### Phase 5

Cross-transport synchronization.

### Phase 6

Runtime supervisor and always-on orchestration.

---

## Expected Outcome

CCB evolves into:

```text
Human-in-the-loop
multi-agent collaboration runtime
```

with synchronized:

- CLI
- iPhone
- Codex
- Claude
- Gemini
