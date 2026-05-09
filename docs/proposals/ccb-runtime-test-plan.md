# CCB Runtime Test Plan Proposal

This document defines the test plan for the newly added CCB Room + iMessage + Runtime Supervisor design.

Scope is intentionally limited to the new design work. This plan does not require rewriting or reorganizing legacy tests.

---

# Document Role

This document is both:

- the focused test strategy for the new runtime architecture
- the current coverage tracker for tests under `my_test/`

Related documents:

- `docs/proposals/ccb-cli-imessage-room.md` — architecture vision
- `docs/proposals/ccb-cli-imessage-room-todo.md` — original backlog
- `docs/proposals/milestone-1-to-10-status.md` — implementation status snapshot

---

# Current Implementation Snapshot

The focused runtime test layer has started under:

```text
my_test/
  helpers/
  unit/
  runtime/
  integration/
```

Implemented helper files:

```text
my_test/helpers/fake_process.py
```

Implemented unit tests:

```text
my_test/unit/test_room_models.py
my_test/unit/test_room_parser.py
my_test/unit/test_room_store.py
my_test/unit/test_room_dispatcher.py
my_test/unit/test_room_executor.py
my_test/unit/test_room_stream_executor.py
my_test/unit/test_room_imessage_delivery.py
my_test/unit/test_imessage_sender.py
my_test/unit/test_imessage_doctor.py
my_test/unit/test_imessage_watcher.py
my_test/unit/test_imessage_correlation.py
my_test/unit/test_imessage_dispatch.py
my_test/unit/test_room_cli.py
my_test/unit/test_imessage_cli.py
my_test/unit/test_daemon_cli.py
```

Implemented runtime tests:

```text
my_test/runtime/test_runtime_event_loop.py
my_test/runtime/test_runtime_worker_registry.py
my_test/runtime/test_runtime_supervisor.py
```

Implemented integration tests:

```text
my_test/integration/test_stream_delivery_flow.py
my_test/integration/test_imessage_dispatch_flow.py
```

Known remaining focused tests:

```text
my_test/integration/test_runtime_polling_flow.py
```

Future tests after bootstrap workers exist:

```text
my_test/runtime/test_dispatch_worker.py
my_test/runtime/test_delivery_worker.py
my_test/runtime/test_watch_worker.py
my_test/e2e/test_full_runtime_loop.py
```

Recent API alignment fixes:

- `run_imessage_doctor()` now supports dependency injection for platform / osascript / chat.db checks.
- sender tests now use `split_imessage_chunks()` and import AppleScript escaping from `imessage.applescript`.

---

# Goals

Provide high confidence for the new event-driven runtime architecture:

```text
CLI / iMessage
      ↓
RoomEvent Bus
      ↓
Runtime Supervisor
      ↓
Dispatcher / Stream Executor
      ↓
Delivery Policy
      ↓
iMessage
```

The tests should protect:

- event ordering
- cursor progression
- dispatch request generation
- streaming output conversion
- delivery deduplication
- correlation binding
- supervisor event loop behavior
- daemon CLI behavior
- failure handling

---

# Non-Goals

This plan does not cover:

- legacy tmux behavior
- provider-specific CLI internals
- real AppleScript execution
- real Messages chat.db access in CI
- real Codex / Claude / Gemini network execution
- large end-to-end macOS-only system tests

All external systems should be mocked or faked.

---

# Proposed Test Directory

New tests should live under:

```text
my_test/
```

Recommended layout:

```text
my_test/
  unit/
  runtime/
  integration/
  helpers/
```

Rationale:

- keep new runtime validation separate from legacy tests
- avoid large test-file migration risk
- make it clear these tests target the new design
- allow future marker-based execution

---

# Pytest Configuration

Recommended future `pytest.ini`:

```ini
[pytest]
testpaths =
    my_test

python_files = test_*.py

markers =
    unit: isolated unit tests
    runtime: runtime orchestration tests
    integration: cross-module runtime tests
    e2e: end-to-end tests that may require platform-specific setup
```

Coverage can be added after the new tests are stable.

---

# Shared Test Helpers

Create:

```text
my_test/helpers/
```

Implemented helpers:

```text
fake_process.py
```

Suggested future helpers:

```text
fake_delivery.py
fake_imessage.py
fake_runtime.py
```

## FakeProcess / FakePopen

Used by:

- RoomAskStreamExecutor
- RoomAskExecutor

Responsibilities:

- simulate stdout lines
- simulate return code
- record argv/cwd/stdout/stderr parameters

## FakeDelivery

Used by:

- delivery worker tests
- stream-to-delivery integration tests

Responsibilities:

- collect delivered events
- optionally raise delivery errors
- expose call count

## FakeIMessageSender

Used by:

- RoomIMessageDelivery tests
- iMessage sender policy tests

Responsibilities:

- collect recipient/message/dry_run calls
- avoid real osascript execution

---

# Coverage Map

## Implemented Coverage

Current `my_test` coverage protects:

- RoomEvent serialization and validation
- shared command grammar
- event store persistence
- cursor progression
- dispatcher lifecycle
- subprocess executor lifecycle
- stream executor lifecycle
- delivery deduplication
- transport binding persistence
- iMessage inbound filtering
- iMessage reply correlation
- iMessage dispatch bridge
- CLI room commands
- iMessage CLI commands
- daemon CLI skeleton
- runtime event loop polling
- worker registry fanout
- runtime supervisor dispatch
- stream-to-delivery integration
- iMessage-to-dispatch integration

## Known Coverage Gaps

Still needed:

- runtime polling flow integration test
- malformed JSONL audit behavior
- invalid cursor name rejection
- real delivery policy skipped cases for missing recipients
- CLI parser error behavior tests
- pytest.ini / marker setup
- bootstrap worker tests after workers exist

---

# Unit Test Plan

## RoomEvent Model

Target file:

```text
my_test/unit/test_room_models.py
```

Status: partially implemented.

Cases:

1. `RoomEvent.to_record()` preserves all required fields.
2. `RoomEvent.from_record()` restores enums and metadata.
3. empty `room_id` raises validation error.
4. empty `sender` raises validation error.
5. empty `target` raises validation error.
6. empty `body` raises validation error.
7. generated event IDs use expected `evt_` prefix.
8. timestamps are generated when not provided.

---

## Room Parser

Target file:

```text
my_test/unit/test_room_parser.py
```

Status: implemented for current grammar.

Cases:

1. `@codex fix tests` parses as target `codex`.
2. `@claude review diff` parses as target `claude`.
3. `@gemini research api` parses as target `gemini`.
4. `@all sync status` parses as broadcast.
5. `@status` parses as status command.
6. aliases work:
   - `@code` → `codex`
   - `@review` → `claude`
   - `@research` → `gemini`
7. unknown participant raises `RoomCommandError`.
8. missing body raises for normal targets.
9. missing body raises for `@all`.
10. empty input raises.
11. input without prefix raises.

---

## Room Store

Target file:

```text
my_test/unit/test_room_store.py
```

Status: partially implemented.

Cases:

1. store creates runtime layout.
2. append then list returns the event.
3. load by event ID returns correct event.
4. list limit returns the latest N events.
5. cursor read defaults to 0.
6. cursor write/read round-trips.
7. invalid cursor name is rejected.
8. `tail_from_cursor()` returns expected events and next offset.
9. audit log accepts records.
10. transport bindings read/write round-trips.
11. malformed JSONL line is skipped and audited.

---

## Room Dispatcher

Target file:

```text
my_test/unit/test_room_dispatcher.py
```

Status: implemented for core lifecycle.

Cases:

1. USER_MESSAGE to `codex` builds dispatch request.
2. request converts to `['ask', target, body]`.
3. broadcast request cannot convert to single ask argv.
4. status/system target is rejected.
5. non-USER_MESSAGE is rejected.
6. `dispatch_prepare_only()` appends TASK_SUBMITTED.
7. TASK_SUBMITTED parent_event_id points to source event.
8. correlation_id is set to source event or job id.

---

## Room Executor

Target file:

```text
my_test/unit/test_room_executor.py
```

Status: implemented for subprocess success/failure lifecycle.

Cases:

1. successful subprocess returns TASK_COMPLETED.
2. failed subprocess returns TASK_FAILED.
3. stdout is used as event body when available.
4. stderr is used as event body when stdout is empty.
5. argv contains ccb path and ask arguments.
6. subprocess cwd equals project root.
7. metadata stores returncode/stdout/stderr/argv.
8. broadcast requests are rejected by request conversion.

---

## Room Stream Executor

Target file:

```text
my_test/unit/test_room_stream_executor.py
```

Status: implemented for line streaming, terminal events, and callback emission.

Cases:

1. each stdout line produces one AGENT_MESSAGE.
2. blank stdout lines are ignored.
3. successful process produces TASK_COMPLETED.
4. failed process produces TASK_FAILED.
5. output events preserve ordering.
6. `on_event` callback fires for every AGENT_MESSAGE.
7. `on_event` callback fires for terminal event.
8. terminal event metadata stores returncode and output_count.
9. broadcast requests are rejected.
10. process cwd equals project root.

---

## iMessage AppleScript / Sender

Target file:

```text
my_test/unit/test_imessage_sender.py
```

Status: partially implemented for escaping and chunking.

Cases:

1. AppleScript string escaping handles quotes.
2. AppleScript string escaping handles backslashes.
3. generated script includes recipient and message.
4. message chunking splits long messages.
5. empty recipient raises.
6. empty message raises.
7. non-macOS sender raises.
8. dry-run returns successful result without osascript.
9. osascript failure raises `IMessageSendError`.

---

## iMessage Doctor

Target file:

```text
my_test/unit/test_imessage_doctor.py
```

Status: implemented.

Cases:

1. non-Darwin platform reports unsupported.
2. missing osascript reports unavailable.
3. missing chat.db adds note.
4. result `ok` requires platform and osascript.
5. Full Disk Access note is always present.

---

## iMessage Watcher

Target file:

```text
my_test/unit/test_imessage_watcher.py
```

Status: implemented for evaluation path; poll cursor test still pending.

Cases:

1. valid allowlisted command becomes RoomEvent.
2. outgoing message is rejected.
3. empty message is rejected.
4. non-allowlisted sender is rejected.
5. missing prefix is rejected.
6. invalid command is rejected.
7. dry-run does not append event.
8. accepted event includes iMessage transport metadata.
9. status command maps to status/system event.
10. rejected messages are audited.
11. poll_once advances iMessage cursor.

Use fake SQLite or monkeypatched `read_inbound_messages()`.

---

## Room iMessage Delivery

Target file:

```text
my_test/unit/test_room_imessage_delivery.py
```

Status: implemented for delivery, binding, dedupe, and multiple recipients.

Cases:

1. disabled policy skips delivery.
2. missing recipients skips delivery.
3. AGENT_MESSAGE is delivered by default.
4. TASK_FAILED is delivered by default.
5. APPROVAL_NEEDED is delivered by default.
6. USER_MESSAGE is skipped unless `mirror_cli_inputs` is enabled.
7. delivery formats message correctly.
8. delivery writes transport binding.
9. duplicate delivery is skipped.
10. TRANSPORT_DELIVERY event is appended after successful send.
11. delivery passes dry_run to sender.
12. multiple recipients all receive the message.

---

## iMessage Correlation

Target file:

```text
my_test/unit/test_imessage_correlation.py
```

Status: implemented.

Cases:

1. iMessage source event creates binding.
2. CLI source event returns no binding.
3. missing sender_handle returns no binding.
4. binding persists in transport-bindings.json.
5. binding can be loaded by correlation_id.
6. invalid transport binding raises error.
7. binding preserves chat_id/message_id/recipient.

---

## iMessage Dispatch Bridge

Target file:

```text
my_test/unit/test_imessage_dispatch.py
```

Status: implemented.

Cases:

1. dispatch_event creates TASK_SUBMITTED.
2. dispatch_event creates correlation binding for iMessage events.
3. CLI-origin events dispatch without iMessage binding.
4. create_agent_reply restores recipient from binding.
5. create_agent_reply restores chat_id/message_id.
6. create_agent_reply records `has_correlation_binding` metadata.
7. missing binding still creates reply event safely.

---

## CLI Room Runner

Target file:

```text
my_test/unit/test_room_cli.py
```

Status: implemented for happy paths.

Cases:

1. `room send` appends event and prints event ID.
2. `room events` renders stored events.
3. `room status` renders stored events.
4. invalid command exits with parser error.
5. invalid room command propagates parse error.

---

## CLI iMessage Runner

Target file:

```text
my_test/unit/test_imessage_cli.py
```

Status: partially implemented.

Cases:

1. `imessage send --dry-run` calls sender.
2. `imessage doctor` prints platform fields.
3. `imessage watch --dry-run` calls watcher poll_once.
4. invalid command exits with parser error.
5. missing required args exits with parser error.

---

## CLI Daemon Runner

Target file:

```text
my_test/unit/test_daemon_cli.py
```

Status: implemented for skeleton behavior.

Cases:

1. `daemon status` prints worker_count.
2. `daemon poll-once` prints processed_events and next_offset.
3. `daemon start` currently reports running.
4. `daemon stop` currently reports stopped.
5. future blocking start should be tested with injected supervisor to avoid infinite loop.

---

# Runtime Test Plan

## Runtime Event Loop

Target file:

```text
my_test/runtime/test_runtime_event_loop.py
```

Status: implemented for polling, cursor, and ordering.

Cases:

1. poll_once consumes new events.
2. poll_once updates cursor.
3. second poll does not re-consume old events.
4. empty poll returns zero processed events.
5. on_event callback receives events in order.
6. USER_MESSAGE writes runtime audit record.
7. limit parameter restricts number of processed events.

---

## Runtime Worker Registry

Target file:

```text
my_test/runtime/test_runtime_worker_registry.py
```

Status: implemented.

Cases:

1. register worker by name.
2. dispatch calls enabled worker.
3. disabled worker is skipped.
4. multiple workers receive same event.
5. later worker with same name replaces previous worker.

---

## Runtime Supervisor

Target file:

```text
my_test/runtime/test_runtime_supervisor.py
```

Status: implemented.

Cases:

1. supervisor initializes with shared store.
2. register_worker adds worker to registry.
3. poll_once dispatches events to registered workers.
4. status returns worker count.
5. status returns cursor name.

---

# Integration Test Plan

## Stream to Delivery Flow

Target file:

```text
my_test/integration/test_stream_delivery_flow.py
```

Status: implemented with fake delivery callback.

Scenario:

```text
RoomDispatchRequest
  ↓
RoomAskStreamExecutor
  ↓
AGENT_MESSAGE events
  ↓
on_event callback
  ↓
RoomIMessageDelivery / fake delivery
```

Cases:

1. streamed AGENT_MESSAGE is delivered to fake iMessage sender.
2. terminal TASK_COMPLETED is delivered when policy includes it.
3. delivery binding prevents duplicate stream event delivery.
4. failed stream produces TASK_FAILED and delivers failure notice.

---

## iMessage to Dispatch Flow

Target file:

```text
my_test/integration/test_imessage_dispatch_flow.py
```

Status: implemented.

Scenario:

```text
iMessage inbound message
  ↓
IMessageWatcher.evaluate_message()
  ↓
RoomEvent
  ↓
IMessageDispatchBridge
  ↓
TASK_SUBMITTED
  ↓
correlation binding
```

Cases:

1. valid inbound `@codex` creates RoomEvent.
2. dispatch bridge creates TASK_SUBMITTED.
3. correlation binding preserves iMessage recipient.
4. agent reply restores iMessage transport metadata.

---

## Runtime Polling Flow

Target file:

```text
my_test/integration/test_runtime_polling_flow.py
```

Status: pending.

Scenario:

```text
RoomEventStore append USER_MESSAGE
  ↓
RuntimeSupervisor.poll_once()
  ↓
registered fake worker
```

Cases:

1. supervisor sees newly appended event.
2. fake worker receives event once.
3. cursor prevents duplicate worker calls.
4. multiple events are processed in append order.

---

# Future E2E Test Plan

E2E tests should not be required for the first test pass.

Future target:

```text
my_test/e2e/test_full_runtime_loop.py
```

Scenario:

```text
fake iMessage inbound
  ↓
watcher
  ↓
RoomEvent
  ↓
dispatch
  ↓
fake provider stream
  ↓
delivery
  ↓
fake iMessage outbound
```

This should be added after bootstrap workers exist.

---

# Suggested Implementation Order

## Pass 1 — Fast Unit Coverage

Status: mostly implemented.

Create:

```text
my_test/unit/test_room_parser.py
my_test/unit/test_room_store.py
my_test/unit/test_room_dispatcher.py
my_test/unit/test_room_stream_executor.py
my_test/unit/test_room_imessage_delivery.py
my_test/unit/test_imessage_watcher.py
my_test/unit/test_imessage_correlation.py
```

Reason:

- protects core event model
- protects parser behavior
- protects stream lifecycle
- protects delivery dedupe
- protects inbound safety checks

---

## Pass 2 — Runtime Coverage

Status: implemented.

Create:

```text
my_test/runtime/test_runtime_event_loop.py
my_test/runtime/test_runtime_worker_registry.py
my_test/runtime/test_runtime_supervisor.py
```

Reason:

- validates supervisor cursor progression
- validates worker callback behavior
- prevents duplicate consumption regressions

---

## Pass 3 — Integration Coverage

Status: partially implemented.

Create:

```text
my_test/integration/test_stream_delivery_flow.py
my_test/integration/test_imessage_dispatch_flow.py
my_test/integration/test_runtime_polling_flow.py
```

Reason:

- validates cross-module behavior
- catches wiring errors
- protects runtime architecture assumptions

---

# Stability Risks Covered

This test plan specifically addresses the highest-risk failure modes:

## Duplicate Processing

Covered by:

- RoomStore cursor tests
- RuntimeEventLoop cursor tests
- RuntimeSupervisor polling tests
- iMessage delivery binding tests

## Duplicate iMessage Delivery

Covered by:

- RoomIMessageDelivery dedupe tests
- stream delivery integration tests

## Lost Agent Output

Covered by:

- RoomAskStreamExecutor line streaming tests
- callback emission tests
- stream-to-delivery integration tests

## Bad Inbound Commands

Covered by:

- parser tests
- iMessage watcher rejection tests
- audit log tests

## Broken Reply Routing

Covered by:

- iMessage correlation tests
- iMessage dispatch bridge tests
- create_agent_reply tests

## Runtime Reprocessing After Restart

Covered by:

- cursor persistence tests
- runtime polling tests

---

# Acceptance Criteria

The new design should be considered stable when:

1. all `my_test/unit` tests pass.
2. all `my_test/runtime` tests pass.
3. integration tests prove stream-to-delivery and iMessage-to-dispatch flows.
4. no tests require real osascript.
5. no tests require real chat.db.
6. no tests invoke real Codex / Claude / Gemini providers.
7. cursor tests prove events are not reprocessed.
8. delivery tests prove iMessage messages are not duplicated.

---

# Future CI Command

Recommended future commands:

```bash
pytest my_test/unit
pytest my_test/runtime
pytest my_test/integration
```

Optional marker-based form:

```bash
pytest -m unit
pytest -m runtime
pytest -m integration
```

---

# Summary

This plan creates a focused stability layer for the newly added design:

```text
RoomEvent Bus
Dispatcher
Streaming Executor
iMessage Transport
Delivery Policy
Runtime Supervisor
```

It intentionally avoids broad legacy test restructuring and focuses only on protecting the new runtime architecture.
