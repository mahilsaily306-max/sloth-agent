"""Sentry agent tracing configuration.

Sentry captures agent setup, latency, tokens, cost, and errors so you can show
your agent's work in the write-up (Sentry Agent Tracing prize category).

Initialize once at app startup:
    from backend.sentry_config import init_sentry
    init_sentry()
"""

from __future__ import annotations

import os

import sentry_sdk


def init_sentry(environment: str = "development") -> None:
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn:
        # No DSN = tracing disabled but app still runs. Add SENTRY_DSN to enable.
        return

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        release=os.environ.get("SENTRY_RELEASE", "sloth-agent@local"),
        # Tag everything as an agent run so traces are easy to filter.
        _experiments={"record_sql_parameters": True},
    )

    # Global tags useful for debugging agent runs.
    sentry_sdk.set_tag("component", "sloth-agent")
    sentry_sdk.set_tag("ai_runtime", "open-source/local")


def capture_agent_event(event: str, details: dict) -> None:
    """Manually record an agent milestone (summary done, tidy done, predict done)."""
    import sentry_sdk

    with sentry_sdk.start_transaction(op="agent.task", name=event) as txn:
        for k, v in details.items():
            txn.set_tag(k, str(v))
