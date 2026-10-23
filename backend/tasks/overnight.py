"""Overnight automation tasks - the 'set it and forget it' lazy chores.

Each task is idempotent and safe to run on a schedule (cron / Temporal / GitHub
Actions). They run while you sleep so you don't have to.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List

from agents.sloth_agent import ChatMessage, sloth_agent


DEFAULT_MESSAGES = [
    ChatMessage(sender="Alice", text="Hey, are we still on for dinner Thursday?", timestamp="22:15"),
    ChatMessage(sender="Group", text="Meeting moved to 10am tomorrow. Don't be late.", timestamp="23:02"),
    ChatMessage(sender="Bob", text="Can you send me the Q3 report?", timestamp="23:45"),
    ChatMessage(sender="Alice", text="Never mind the report, I found it.", timestamp="00:10"),
]


def run_nightly(directory: str = ".", csv_path: str | None = None, target_column: str | None = None) -> dict:
    """One nightly run: summarize inbox, tidy directory, predict from CSV."""
    run_id = f"nightly-{datetime.utcnow().strftime('%Y%m%d')}"
    run = sloth_agent.overnight_run(
        run_id=run_id,
        messages=DEFAULT_MESSAGES,
        directory=directory,
        csv_path=csv_path,
        target_column=target_column,
    )
    return {
        "run_id": run.id,
        "status": run.status,
        "summary": run.summary,
        "tidy_actions_count": len(run.tidy_actions),
        "tidy_actions": run.tidy_actions[:5],
        "predictions": run.predictions,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
    }


if __name__ == "__main__":  # pragma: no cover - manual CLI run
    result = run_nightly(directory=str(Path.home() / "Downloads"))
    print(json.dumps(result, indent=2))
