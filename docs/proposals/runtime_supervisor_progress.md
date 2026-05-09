# Runtime Supervisor Progress

## Overview

The runtime has evolved from a foreground-only orchestration loop into a self-healing, observable orchestration supervisor.

Current runtime capabilities now include:

- Background daemon lifecycle management
- Detached subprocess orchestration
- Runtime heartbeat persistence
- Runtime health scoring
- Restart remediation flows
- Watchdog supervision loops
- Restart backoff enforcement
- Crash-loop suppression
- Worker-level health persistence
- Worker execution isolation
- Worker quarantine and cooldown recovery
- Runtime metrics aggregation
- CLI JSON metrics export
- Embedded HTTP metrics serving
- Managed metrics runtime lifecycle
- Unified lifecycle state semantics
- Lifecycle-aware daemon status and watchdog output
- Top-level `ccb daemon` routing
- Injectable daemon CLI dependencies for deterministic tests

---

# Current Runtime Architecture

## Daemon Lifecycle

Implemented components:

- `launch_background_daemon()`
- `stop_background_daemon()`
- `restart_background_daemon_if_needed()`
- `run_watchdog_tick()`
- `run_watchdog_loop()`
- `collect_runtime_metrics()`
- `RuntimeMetricsHttpServer`
- `start_metrics_runtime()`
- `RuntimeLifecycleStateMachine`
- `map_runtime_health_to_lifecycle_state()`

Current CLI surface:

```bash
ccb daemon start
ccb daemon start --foreground
ccb daemon stop
ccb daemon restart
ccb daemon status
ccb daemon metrics
ccb daemon watchdog
ccb daemon watchdog --loop
```

---

# Runtime Health Layer

## Runtime Health States

Supported runtime health states:

- healthy
- stale
- stopped
- unknown

Health scoring evaluates:

- PID ownership
- Heartbeat freshness
- Runtime stale detection
- Runtime stop state

Current telemetry:

```text
health_status=
health_score=
health_reason=
lifecycle_state=
```

---

# Unified Lifecycle Semantics

The runtime now has a lifecycle state model for normalized orchestration semantics.

Lifecycle states:

```text
stopped
starting
running
degraded
recovering
stopping
failed
```

The current lifecycle mapping normalizes:

```text
daemon runtime state
+
runtime health
↓
lifecycle_state
```

Current consumers:

- `ccb daemon status`
- `ccb daemon watchdog`
- `ccb daemon watchdog --loop`
- `ccb daemon metrics`
- `/metrics` HTTP telemetry

---

# Watchdog Supervision

## Continuous Watchdog

The watchdog runtime now supports:

- Continuous supervision loops
- Health-aware remediation
- Automatic restart attempts
- Restart accounting
- Restart suppression
- Runtime state propagation in watchdog tick results
- Lifecycle-normalized watchdog telemetry

Current watchdog loop telemetry:

```text
watchdog_iterations=
watchdog_restarts=
health_status=
lifecycle_state=
```

---

# Restart Backoff System

## Restart Budgeting

Implemented:

- Restart counters
- Restart suppression policies
- Time-window restart decay
- Automatic restart budget reset

Current policy model:

```python
RestartBackoffPolicy(
    max_restarts=3,
    window_seconds=300,
)
```

This prevents infinite restart loops while still allowing recovery after cooldown windows.

---

# Worker Isolation Layer

## Worker Health Persistence

Implemented:

- Per-worker health tracking
- Worker success counters
- Worker failure counters
- Worker error persistence
- Failure isolation

Persisted metadata:

```text
success_count
failure_count
last_success_at
last_failure_at
last_error
```

Persistence location:

```text
.ccb/worker-health.json
```

---

# Worker Quarantine Layer

Implemented:

- Worker quarantine policy
- Failure-threshold quarantine
- Quarantine persistence
- Cooldown-based recovery
- Quarantined worker bypass during dispatch

Persistence location:

```text
.ccb/worker-quarantine.json
```

Current behavior:

```text
worker repeated failure
↓
record failure state
↓
quarantine worker
↓
skip worker during dispatch
↓
auto-recover after cooldown
```

---

# Observability Layer

Implemented:

- Runtime metrics snapshot aggregation
- CLI metrics JSON export
- Embedded HTTP `/metrics` endpoint
- Managed metrics runtime thread lifecycle
- Lifecycle state included in metrics

Current metrics fields:

```text
runtime_state
runtime_health
runtime_health_score
lifecycle_state
restart_count
worker_count
quarantined_workers
healthy_workers
failed_workers
```

---

# Current Test Coverage

## Runtime Tests

Current runtime coverage includes:

- Background daemon launch
- Detached subprocess semantics
- Runtime stop signaling
- Restart recovery
- Health scoring
- Watchdog remediation
- Watchdog loop execution
- Watchdog runtime state propagation
- Restart backoff enforcement
- Restart decay windows
- Worker health persistence
- Worker execution isolation
- Worker quarantine
- Quarantine cooldown recovery
- Runtime metrics aggregation
- Metrics HTTP serving
- Managed metrics runtime lifecycle
- Lifecycle state transitions
- Lifecycle health mapping
- Lifecycle metrics export
- Top-level `ccb daemon` routing
- Daemon CLI dependency injection

Current runtime tests:

```text
my_test/runtime/test_background.py
my_test/runtime/test_health.py
my_test/runtime/test_watchdog.py
my_test/runtime/test_backoff.py
my_test/runtime/test_worker_health.py
my_test/runtime/test_worker_registry.py
my_test/runtime/test_worker_quarantine.py
my_test/runtime/test_metrics.py
my_test/runtime/test_metrics_server.py
my_test/runtime/test_metrics_runtime.py
my_test/runtime/test_state_machine.py
my_test/unit/test_daemon_cli.py
my_test/unit/test_ccb_daemon_routing.py
```

---

# Unfinished Tasks

## P0 Stabilization

These tasks should be completed before adding distributed orchestration features.

### 1. Run and stabilize tests locally/CI

The repository now has many new runtime tests, but test execution has not been confirmed in this maintenance thread.

Actions:

- Run the full runtime and daemon CLI test subset.
- Fix constructor mismatches in worker tests if `RoomEvent` usage is stale.
- Verify no CLI unit test starts a real subprocess.
- Verify watchdog tests do not depend on real OS PID state.
- Confirm `ccb daemon status`, `metrics`, and `watchdog` commands work through the top-level shim.

### 2. Fix real daemon foreground semantics

Current known issue:

```text
ccb daemon start --foreground
```

uses a bounded foreground iteration default for testability.

Risk:

```text
background daemon launch may exit after one runtime loop
```

Actions:

- Split production foreground mode from test bounded mode.
- Add an explicit `--iterations` or `--once` flag for test-only bounded runs.
- Ensure background daemon launch starts a persistent foreground process.

### 3. Complete dependency injection cleanup

`run_daemon_cli()` supports injected daemon/watchdog functions, but more runtime side effects may still be hardwired.

Actions:

- Add injection for `run_runtime_forever()` where foreground tests need isolation.
- Add injection for signal handler installation.
- Keep production defaults unchanged.

### 4. Stabilize PID-dependent tests

Some daemon/background/watchdog tests may depend on fake PIDs that are evaluated through real OS PID checks.

Actions:

- Prefer dependency-injected PID checks.
- Avoid fake PID assumptions that vary by host.
- Ensure stale/running test cases are deterministic.

---

## P1 Runtime Architecture Consolidation

### 5. Full state-machine ownership

The state machine currently normalizes health/state into lifecycle semantics, but it does not yet own all runtime transitions.

Actions:

- Route daemon start/stop/restart lifecycle transitions through `RuntimeLifecycleStateMachine`.
- Route watchdog remediation decisions through lifecycle events.
- Persist lifecycle state if needed.
- Define transition audit records.

### 6. Supervisor lifecycle object

Runtime lifecycle responsibilities are still split across:

```text
background.py
daemon_cli.py
daemon_runner.py
watchdog.py
metrics_runtime.py
state_machine.py
```

Actions:

- Introduce a supervisor lifecycle coordinator.
- Centralize start, stop, restart, watchdog, metrics boot, and shutdown semantics.
- Reduce direct cross-calls between CLI and low-level runtime modules.

### 7. Metrics daemon integration

The metrics runtime can start independently, but it is not yet automatically owned by daemon startup.

Actions:

- Add daemon option to boot metrics runtime.
- Add shared shutdown coordination.
- Add configurable metrics host/port.
- Add tests for daemon-owned metrics lifecycle.

### 8. Runtime config model

Runtime options are currently scattered across constants and defaults.

Actions:

- Add `RuntimeConfig` dataclass.
- Include watchdog interval, heartbeat timeout, restart policy, metrics host/port, worker quarantine policy, and daemon iteration mode.
- Load config from defaults first; later allow `.ccb/runtime-config.json`.

---

## P2 Platform Expansion

These should wait until P0/P1 are stable.

- Persistent analytics storage
- Prometheus-compatible metrics output
- Remote orchestration control API
- Multi-project runtime federation
- Distributed orchestration coordination
- Runtime dashboard

---

# Runtime Maturity

The runtime has evolved through the following stages:

```text
foreground orchestration
→ detached runtime
→ recoverable runtime
→ self-healing runtime
→ continuous supervision runtime
→ bounded resilience supervisor
→ worker-isolated orchestration runtime
→ observable orchestration runtime
→ lifecycle-normalized orchestration runtime
→ regression-protected orchestration platform
```

Current architecture direction:

```text
production orchestration supervisor
```
