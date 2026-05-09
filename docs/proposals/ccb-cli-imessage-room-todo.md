# CCB CLI + iMessage Unified Room TODO

This document breaks the proposal into concrete implementation tasks.

Related proposal:

- `docs/proposals/ccb-cli-imessage-room.md`

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

## Milestone 2: Room Event Store

### File layout

Create runtime storage under project `.ccb`:

```text
.ccb/room/
  events.jsonl
  cursors/
    cli.json
    imessage.json
  transport-bindings.json
  audit.jsonl
```

### Store implementation

- [ ] Add append-only JSONL writer.
- [ ] Add atomic append / lock protection.
- [ ] Add event id generation.
- [ ] Add timestamp generation in UTC.
- [ ] Add event loading by id.
- [ ] Add event tailing by cursor.
- [ ] Add event listing with limit.
- [ ] Add cursor read/write helpers.
- [ ] Add transport binding read/write helpers.
- [ ] Add audit log writer.

### Reliability

- [ ] Handle corrupted JSONL lines gracefully.
- [ ] Never crash the whole daemon on one malformed event.
- [ ] Add compaction plan placeholder, but do not implement in MVP.
- [ ] Add log rotation TODO for future.

---

## Milestone 3: Shared Command Parser

### Supported grammar

Parse the same syntax for CLI and iMessage:

```text
@codex <task>
@claude <task>
@gemini <task>
@all <message>
@status
@stop <target>
```

### Parser tasks

- [ ] Add `parse_room_command(text, participants, prefix='@')`.
- [ ] Normalize whitespace.
- [ ] Reject empty messages.
- [ ] Resolve target aliases.
- [ ] Support default agent fallback.
- [ ] Support `@all` broadcast event.
- [ ] Support `@status` status request event.
- [ ] Support rejected parse result with reason.
- [ ] Reuse the parser from both CLI and iMessage.

### Alias design

- [ ] Support aliases such as:
  - [ ] `@code` → `codex`
  - [ ] `@review` → `claude`
  - [ ] `@research` → `gemini`
- [ ] Add config-driven aliases later.

---

## Milestone 4: CLI Transport Integration

### CLI commands

Add commands:

```bash
ccb room send "@codex fix failing tests"
ccb room tail
ccb room status
ccb room events --limit 20
```

### CLI tasks

- [ ] Add CLI parser entrypoint for `room` subcommands.
- [ ] Add `room send` to normalize input into `RoomEvent`.
- [ ] Add `room tail` to follow `events.jsonl`.
- [ ] Add `room status` to summarize recent room state.
- [ ] Add `room events` to list recent events.
- [ ] Add terminal rendering for user, agent, system, and error events.
- [ ] Ensure existing `ccb ask` behavior does not break.
- [ ] Optionally mirror `ccb ask` into room events.

### CLI output policy

- [ ] CLI should show all local events by default.
- [ ] CLI should distinguish source:
  - [ ] CLI-originated user message
  - [ ] iMessage-originated user message
  - [ ] agent reply
  - [ ] system notice

---

## Milestone 5: Connect Room Events to Ask / Dispatcher

### Dispatch design

When a `user_message` targets an agent:

```text
RoomEvent(user_message)
  ↓
submit to existing ask / dispatcher path
  ↓
create task_submitted event
  ↓
agent reply
  ↓
create agent_message / task_completed event
```

### Tasks

- [ ] Find current `ccb ask` implementation.
- [ ] Extract reusable submit function if needed.
- [ ] Add `RoomDispatcher` that accepts a RoomEvent.
- [ ] Submit targeted events to the right agent.
- [ ] Submit `@all` to multiple agents or broadcast path.
- [ ] Create `task_submitted` event with job id.
- [ ] Correlate agent reply with original event.
- [ ] Create `agent_message` event from reply.
- [ ] Create `task_failed` event on failure.
- [ ] Preserve existing mailbox / reply behavior.

---

## Milestone 6: iMessage Outbound MVP

### Add iMessage module

Create:

```text
lib/imessage/
  __init__.py
  applescript.py
  sender.py
  doctor.py
  config.py
```

### Sender tasks

- [ ] Implement `send_imessage(to, message)`.
- [ ] Use `osascript` and Messages.app.
- [ ] Escape AppleScript strings safely.
- [ ] Support phone number handles.
- [ ] Support email handles.
- [ ] Return structured success / failure.
- [ ] Add chunking for long messages.
- [ ] Add dry-run mode.

### CLI commands

```bash
ccb imessage send --to "+886912345678" --message "hello"
ccb imessage doctor
```

### Doctor checks

- [ ] macOS platform check.
- [ ] `osascript` availability.
- [ ] Messages.app availability.
- [ ] Full Disk Access note for future inbound.
- [ ] Config enabled/disabled status.
- [ ] Sender allowlist presence.

---

## Milestone 7: Room-to-iMessage Delivery Policy

### Delivery policy config

```toml
[room.transports.imessage]
enabled = true
prefix = "@"
allow_senders = ["+886912345678"]
notify_on = ["agent_message", "task_failed", "approval_needed"]
mirror_cli_inputs = false
```

### Tasks

- [ ] Add transport policy model.
- [ ] Add `should_deliver_to_imessage(event, policy)`.
- [ ] Send agent replies to configured recipient.
- [ ] Send failure events to configured recipient.
- [ ] Send approval-needed events to configured recipient.
- [ ] Avoid echoing every CLI input unless explicitly configured.
- [ ] Add delivery record event.
- [ ] Add delivery error event.
- [ ] Add idempotency guard so the same event is not sent twice.

---

## Milestone 8: iMessage Inbound Watcher

### macOS Messages source

Read from:

```text
~/Library/Messages/chat.db
```

### Watcher tasks

- [ ] Implement read-only SQLite access.
- [ ] Query recent incoming messages.
- [ ] Extract message id / rowid.
- [ ] Extract sender handle.
- [ ] Extract text body.
- [ ] Extract chat/thread id if available.
- [ ] Poll at configurable interval.
- [ ] Deduplicate processed message ids.
- [ ] Store cursor in `.ccb/room/cursors/imessage.json`.
- [ ] Ignore outgoing messages.
- [ ] Ignore empty messages.
- [ ] Ignore non-allowlisted senders.
- [ ] Ignore messages without prefix.
- [ ] Audit rejected messages without storing sensitive body by default.

### CLI command

```bash
ccb imessage watch
ccb imessage watch --dry-run
ccb imessage watch --once
```

### Dry run behavior

- [ ] Read and parse messages.
- [ ] Print accepted/rejected reason.
- [ ] Do not dispatch to agents.
- [ ] Do not send replies.

---

## Milestone 9: iMessage Inbound to RoomEvent

### Conversion tasks

- [ ] Convert accepted iMessage messages to `RoomEvent`.
- [ ] Set `source = imessage`.
- [ ] Set `sender = you` after allowlist match.
- [ ] Set `transport.name = imessage`.
- [ ] Preserve iMessage message id.
- [ ] Preserve chat/thread id.
- [ ] Dispatch through the same room dispatcher as CLI.
- [ ] Record parse errors as audit events.

### Example

Input:

```text
@codex fix build error
```

RoomEvent:

```json
{
  "source": "imessage",
  "sender": "you",
  "target": "codex",
  "type": "user_message",
  "body": "fix build error"
}
```

---

## Milestone 10: Reply Correlation Back to iMessage

### Correlation tasks

- [ ] Store original iMessage chat/thread id.
- [ ] Store original iMessage message id.
- [ ] Store CCB job id / correlation id.
- [ ] When agent reply arrives, find original transport binding.
- [ ] Reply to same iMessage sender/thread.
- [ ] Add fallback to configured owner recipient.
- [ ] Avoid duplicate replies.
- [ ] Split long replies into multiple iMessages.

### Binding file

```text
.ccb/room/transport-bindings.json
```

Suggested record:

```json
{
  "correlation_id": "job_123",
  "source_event_id": "evt_123",
  "transport": "imessage",
  "chat_id": "chat123",
  "message_id": "456",
  "recipient": "+886912345678"
}
```

---

## Milestone 11: Configuration

### Project config fields

Add:

```toml
[room]
enabled = true
default_agent = "claude"
participants = ["you", "codex", "claude", "gemini"]

[room.transports.cli]
enabled = true
show_all_events = true

[room.transports.imessage]
enabled = false
prefix = "@"
allow_senders = []
notify_on = ["agent_message", "task_failed", "approval_needed"]
mirror_cli_inputs = false
poll_interval_seconds = 5

[agents.codex]
role = "implementer"

[agents.claude]
role = "architect_reviewer"

[agents.gemini]
role = "researcher_reviewer"
```

### Config tasks

- [ ] Add room config dataclasses.
- [ ] Add default config values.
- [ ] Validate participants exist.
- [ ] Validate default agent exists.
- [ ] Validate iMessage allowlist when inbound is enabled.
- [ ] Validate poll interval.
- [ ] Validate notify event names.
- [ ] Keep feature disabled by default.

---

## Milestone 12: Safety and Permissions

### iMessage safety

- [ ] Require explicit enable flag.
- [ ] Require allowlist for inbound.
- [ ] Require command prefix.
- [ ] Reject unknown agents.
- [ ] Reject empty body.
- [ ] Set max message length.
- [ ] Set max dispatches per minute.
- [ ] Do not support raw shell mode.
- [ ] Add confirmation flow for risky actions later.

### Audit log

- [ ] Log accepted command metadata.
- [ ] Log rejected command reason.
- [ ] Avoid storing full rejected body by default.
- [ ] Redact phone/email if configured.
- [ ] Include source transport and timestamp.

---

## Milestone 13: Tests

### Unit tests

- [ ] RoomEvent serialization/deserialization.
- [ ] Room parser target routing.
- [ ] Room parser aliases.
- [ ] Room parser rejection cases.
- [ ] Room store append/read/cursor.
- [ ] Transport policy selection.
- [ ] iMessage AppleScript escaping.
- [ ] iMessage watcher dedupe.
- [ ] iMessage allowlist filtering.

### Integration tests

- [ ] CLI room send writes event.
- [ ] CLI room tail reads event.
- [ ] Room event dispatch calls ask path.
- [ ] Agent reply creates agent_message event.
- [ ] iMessage dry-run parses messages without dispatch.
- [ ] Delivery policy avoids duplicate sends.

### Platform tests

- [ ] macOS-specific tests skipped on non-macOS.
- [ ] Non-macOS `imessage doctor` reports unsupported platform cleanly.
- [ ] Missing `osascript` reports clear error.
- [ ] Missing Messages database reports clear error.

---

## Milestone 14: Documentation

### User docs

- [ ] Add overview of CCB room model.
- [ ] Add CLI examples.
- [ ] Add iMessage setup steps.
- [ ] Add macOS Full Disk Access note.
- [ ] Add safety warning.
- [ ] Add config examples.
- [ ] Add troubleshooting section.

### Developer docs

- [ ] Document RoomEvent schema.
- [ ] Document transport adapter contract.
- [ ] Document room store layout.
- [ ] Document dispatcher integration.
- [ ] Document test strategy.

---

## Milestone 15: MVP Cut Line

The MVP should include:

- [ ] RoomEvent model.
- [ ] RoomEvent JSONL store.
- [ ] Shared parser for `@codex`, `@claude`, `@gemini`, `@all`, `@status`.
- [ ] `ccb room send`.
- [ ] `ccb room tail`.
- [ ] `ccb imessage send`.
- [ ] `ccb imessage doctor`.
- [ ] iMessage outbound delivery for important room events.

The MVP should not include yet:

- [ ] Always-on background iMessage daemon.
- [ ] Arbitrary shell commands from iMessage.
- [ ] Complex group chat behavior.
- [ ] Full reply threading guarantees.
- [ ] Cross-device conflict resolution.

---

## Agent Work Assignment

### Codex

- [ ] Implement RoomEvent model and store.
- [ ] Implement CLI commands.
- [ ] Implement iMessage sender module.
- [ ] Add tests.

### Claude

- [ ] Review architecture.
- [ ] Refine event schema.
- [ ] Review safety model.
- [ ] Review config design.

### Gemini

- [ ] Verify macOS Messages.app integration constraints.
- [ ] Research chat.db schema compatibility risks.
- [ ] Review AppleScript sending behavior.
- [ ] Provide second opinion on security risks.

### Human owner

- [ ] Confirm config syntax.
- [ ] Confirm iMessage sender allowlist.
- [ ] Approve MVP scope.
- [ ] Test on local macOS machine.

---

## Open Questions

- [ ] Should CLI-originated tasks always notify iMessage, or only completion/failure?
- [ ] Should iMessage inbound support group chats or direct messages only in MVP?
- [ ] Should `@all` dispatch in parallel or sequentially?
- [ ] Should iMessage replies be summarized by default to avoid long message spam?
- [ ] Should room events become the long-term source of memory for agent coordination?
- [ ] Should this be integrated into `ccbd` supervision or remain a foreground `watch` command first?

---

## Recommended First PR

First PR scope:

- [ ] Add `docs/proposals/ccb-cli-imessage-room.md`.
- [ ] Add this TODO document.
- [ ] Add `lib/room/models.py` skeleton.
- [ ] Add `lib/room/parser.py` skeleton.
- [ ] Add tests for parser only.

This keeps the first PR small and gives the team a stable foundation before integrating transports.
