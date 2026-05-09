# CCB CLI + iMessage Unified Room TODO

## Document Role

This document is the original implementation breakdown and backlog tracker for the CCB Room + iMessage runtime design.

This file is intentionally preserved as a milestone-oriented checklist.

For current implementation status, use:

- `docs/proposals/milestone-1-to-10-status.md`
- `docs/proposals/ccb-runtime-test-plan.md`

---

## Current Status Notice

The repository has progressed significantly beyond the original proposal phase.

Major implemented foundations now include:

- RoomEvent model
- RoomEvent JSONL store
- shared parser
- CLI room integration
- dispatcher bridge
- subprocess executor
- stream executor
- iMessage outbound sender
- iMessage inbound watcher
- reply correlation
- runtime supervisor skeleton
- daemon CLI skeleton
- focused `my_test` runtime validation layer

Many checklist items below represent:

```text
original design intent
future expansion work
runtime composition tasks
hardening work
```

rather than missing greenfield implementation.

---

## Milestone 0: Project Preparation

### Repository setup

- [ ] Confirm the current CCB fork builds locally.
- [ ] Confirm test command and minimum supported Python version.
- [ ] Create a feature branch, for example `custom/room-imessage-sync`.
- [ ] Identify existing CLI entrypoints.
- [ ] Identify existing ask / mailbox / dispatcher APIs.
- [ ] Identify existing provider reply event paths for Codex, Claude, and Gemini.

### Design boundaries

- [ ] Confirm CLI and iMessage are transports, not separate conversation systems.
- [ ] Define the room event bus as the single source of truth.
- [ ] Keep iMessage disabled by default.
- [ ] Keep iMessage inbound limited to safe ask-style messages.
- [ ] Avoid arbitrary shell execution from iMessage.

---

## Milestone 1: Shared Room Event Model

### Add room module

Create:

```text
lib/room/
  __init__.py
  models.py
  parser.py
  store.py
  dispatcher.py
  config.py
```

### RoomEvent model

- [ ] Add `RoomEvent` dataclass.
- [ ] Add `RoomEventType` enum.
- [ ] Add `RoomSource` enum or string validation for `cli`, `imessage`, `system`, `agent`.
- [ ] Add required fields:
  - [ ] `event_id`
  - [ ] `room_id`
  - [ ] `created_at`
  - [ ] `source`
  - [ ] `sender`
  - [ ] `target`
  - [ ] `type`
  - [ ] `body`
- [ ] Add optional fields:
  - [ ] `correlation_id`
  - [ ] `parent_event_id`
  - [ ] `job_id`
  - [ ] `agent_name`
  - [ ] `transport`
  - [ ] `metadata`
- [ ] Add `to_record()` serialization.
- [ ] Add `from_record()` deserialization.
- [ ] Add schema validation errors.

### Suggested event types

- [ ] `user_message`
- [ ] `agent_message`
- [ ] `system_message`
- [ ] `task_submitted`
- [ ] `task_started`
- [ ] `task_completed`
- [ ] `task_failed`
- [ ] `approval_needed`
- [ ] `status_snapshot`
- [ ] `transport_delivery`
- [ ] `transport_error`

### Transport metadata shape

- [ ] Define CLI metadata:

```json
{
  "name": "cli",
  "session_id": null,
  "pane_id": null
}
```

- [ ] Define iMessage metadata:

```json
{
  "name": "imessage",
  "chat_id": "...",
  "message_id": "...",
  "sender_handle": "+886..."
}
```

---

## Milestone 3: Shared Command Parser

### Supported grammar

Implemented grammar:

```text
@codex <task>
@claude <task>
@gemini <task>
@all <message>
@status
```

Implemented aliases:

```text
@code
@review
@research
```

Future grammar candidates:

```text
@stop <target>
default agent fallback
config-driven aliases
```
