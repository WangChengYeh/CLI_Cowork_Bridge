# CCB Room + iMessage Runtime Status

Status snapshot for milestones 1 through 10 plus runtime integration progress.

Related proposal:

- `docs/proposals/ccb-cli-imessage-room.md`
- `docs/proposals/ccb-cli-imessage-room-todo.md`

---

# Current System State

The repository now contains a functional runtime foundation for:

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
- dispatcher preparation layer
- subprocess runtime execution
- streaming agent output
- iMessage outbound delivery
- iMessage inbound watcher
- reply correlation
- runtime supervisor skeleton
- daemon CLI skeleton
- transport synchronization foundation

---

# Architectural Evolution

The project has evolved through four major phases.

## Phase 1 — CLI Bridge

Original system:

```text
Human
  ↓
ccb ask
  ↓
Provider CLI
```

This phase focused primarily on:

- Codex integration
- Claude integration
- Gemini integration
- tmux coordination

---

## Phase 2 — Shared RoomEvent Bus

The repository evolved into:

```text
CLI ↔ RoomEvent Bus
```

with:

- shared events
- shared parsing
- event persistence
- correlation metadata

---

## Phase 3 — Multi-Transport Runtime

The system now supports:

```text
CLI ↔ RoomEvent Bus ↔ iMessage
```

including:

- outbound iMessage delivery
- inbound iMessage parsing
- transport synchronization
- correlation bindings
- delivery policies

---

## Phase 4 — Always-On Runtime Foundation

The repository now contains:

```text
RuntimeSupervisor
RuntimeEventLoop
RuntimeWorkerRegistry
RoomAskStreamExecutor
```

This is the beginning of:

```text
persistent multi-agent orchestration
```

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

Status: completed.

Implemented:

```text
lib/cli/room.py
lib/cli/room_cli.py
```

Features:

- send_room_message()
- list_room_events()
- render_room_events()
- standalone room CLI
- room command routing from ccb

Supported commands:

```bash
ccb room send
ccb room events
ccb room status
```

---

## Milestone 5 — Dispatcher Bridge

Status: completed.

Implemented:

```text
lib/room/dispatcher.py
lib/room/executor.py
lib/room/stream_executor.py
```

Features:

- RoomDispatchRequest
- TASK_SUBMITTED lifecycle events
- ask argv normalization
- subprocess runtime execution
- stdout streaming
- AGENT_MESSAGE streaming
- TASK_COMPLETED/TASK_FAILED generation
- callback-based event emission

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
- live stream callback compatibility

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

# Runtime Supervisor Progress

## Runtime Event Loop

Implemented:

```text
lib/runtime/event_loop.py
```

Features:

- cursor-driven polling
- continuous runtime loop
- event callbacks
- audit integration

---

## Runtime Worker Registry

Implemented:

```text
lib/runtime/worker.py
```

Features:

- worker registration
- event dispatching
- enable/disable controls

---

## Runtime Supervisor

Implemented:

```text
lib/runtime/supervisor.py
```

Features:

- shared orchestration layer
- event loop integration
- worker registry integration
- supervisor status reporting

---

## Daemon CLI

Implemented:

```text
lib/cli/daemon_cli.py
```

Supported commands:

```bash
ccb daemon start
ccb daemon stop
ccb daemon status
ccb daemon poll-once
```

Current status:

```text
skeleton implementation
```

The daemon currently supports:

- supervisor creation
- polling execution
- runtime status reporting

Persistent background orchestration is not yet complete.

---

# Current Runtime Topology

The repository now contains the architectural foundation for:

```text
iPhone
   ↓
IMessageWatcher
   ↓
RoomEvent Bus
   ↓
RuntimeSupervisor
   ↓
Dispatch Layer
   ↓
Codex / Claude / Gemini
   ↓
Streaming Executor
   ↓
Delivery Layer
   ↓
iPhone
```

---

# Remaining Critical Work

The repository is now in:

```text
runtime integration phase
```

rather than:

```text
architecture design phase
```

The remaining work is primarily runtime composition.

---

# Remaining Integration Tasks

## 1. Runtime bootstrap wiring

Needed:

```text
lib/runtime/bootstrap.py
```

Responsibilities:

- instantiate supervisor
- instantiate shared store
- instantiate shared delivery policy
- register runtime workers
- wire callbacks
- inject dependencies

---

## 2. Real DispatchWorker

Needed:

```text
lib/runtime/workers/dispatch_worker.py
```

Responsibilities:

```text
USER_MESSAGE
  ↓
RoomDispatcher
  ↓
RoomAskStreamExecutor
```

---

## 3. Real DeliveryWorker

Needed:

```text
lib/runtime/workers/delivery_worker.py
```

Responsibilities:

```text
AGENT_MESSAGE
TASK_COMPLETED
TASK_FAILED
  ↓
RoomIMessageDelivery
```

---

## 4. Real WatchWorker

Needed:

```text
lib/runtime/workers/imessage_watch_worker.py
```

Responsibilities:

```text
chat.db polling
  ↓
RoomEvent append
```

---

## 5. Persistent daemon lifecycle

Currently:

```text
daemon CLI skeleton only
```

Needed:

```text
blocking forever loop
background execution
PID management
restart recovery
heartbeat
```

---

## 6. Parallel orchestration

Future work:

```text
@all fanout
parallel execution
approval workflows
agent-to-agent coordination
shared summaries
```

---

# Current Architectural Result

The repository now contains the foundation for:

```text
persistent human-in-the-loop
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

The repository has evolved beyond:

```text
CLI bridge
```

and is now transitioning into:

```text
always-on multi-agent operating runtime
```
