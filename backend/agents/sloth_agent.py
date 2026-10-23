"""Sloth Agent - the open-source AI agent that works while you laze.

Theme: "Slow and Steady" (Hacktoberfest Week 3). Build something that does the
work so you don't have to. Runs on open-weight models (Gemma) and open-source
agent tooling, entirely local by default.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from models.gemma import chat as gemma_chat
from models.tabpfn import tabpfn


@dataclass
class ChatMessage:
    sender: str
    text: str
    timestamp: str


@dataclass
class SummaryResult:
    summary: str
    source: str
    generated_at: str
    model: str


@dataclass
class TidyResult:
    actions: List[str]
    before_count: int
    after_count: int


@dataclass
class OvernightRun:
    id: str
    started_at: str
    finished_at: Optional[str]
    summary: Optional[str]
    tidy_actions: List[str]
    predictions: List[dict]
    status: str  # "running" | "done" | "error"


class SlothAgent:
    """Core agent. One method per 'lazy' chore."""

    def __init__(self):
        self.runs: dict[str, OvernightRun] = {}

    def summarize_messages(self, messages: List[ChatMessage], source: str = "inbox") -> SummaryResult:
        """Read overnight group chats / inbox and hand you a two-line summary."""
        transcript = "\n".join(
            f"{m.sender} ({m.timestamp}): {m.text}" for m in messages
        )
        prompt = (
            "You are Sloth Agent. Summarize the following overnight messages "
            "into exactly two short lines. Highlight only what actually needs "
            "action. Ignore chatter.\n\nMESSAGES:\n" + transcript
        )
        response = gemma_chat(
            prompt,
            system="You are a concise overnight summarizer. Output exactly two lines, plain text.",
        )
        return SummaryResult(
            summary=response.text.strip(),
            source=source,
            generated_at=datetime.utcnow().isoformat() + "Z",
            model=response.model,
        )

    def tidy_files(self, directory: str, dry_run: bool = True) -> TidyResult:
        """Sort, rename, and archive clutter so you never face a messy folder."""
        import os
        from pathlib import Path

        target = Path(directory)
        if not target.exists():
            return TidyResult(actions=[f"Directory {directory} not found"], before_count=0, after_count=0)

        files = [p for p in target.iterdir() if p.is_file()]
        before = len(files)
        actions: List[str] = []

        # Extension -> folder map
        buckets = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
            "documents": [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf"],
            "spreadsheets": [".csv", ".xls", ".xlsx", ".ods"],
            "archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
            "installers": [".exe", ".msi", ".dmg", ".pkg"],
        }

        for f in files:
            ext = f.suffix.lower()
            folder = "misc"
            for name, exts in buckets.items():
                if ext in exts:
                    folder = name
                    break
            dest_dir = target / folder
            if not dry_run:
                dest_dir.mkdir(exist_ok=True)
                f.rename(dest_dir / f.name)
            actions.append(f"{'[dry-run] ' if dry_run else ''}{f.name} -> {folder}/")

        after = len([p for p in target.iterdir() if p.is_file()]) if not dry_run else before
        return TidyResult(actions=actions, before_count=before, after_count=after)

    def predict_csv(self, csv_path: str, target_column: str) -> dict:
        """Forecast/classify from a CSV so you don't have to run the numbers."""
        result = tabpfn.predict_from_csv(csv_path, target_column)
        return {
            "target_column": result.target_column,
            "prediction": result.prediction,
            "confidence": result.confidence,
            "model": result.model,
            "local": result.local,
            "cost_usd": result.cost_usd,
        }

    def overnight_run(self, run_id: str, messages: List[ChatMessage], directory: str,
                      csv_path: Optional[str] = None, target_column: Optional[str] = None) -> OvernightRun:
        """Run the full lazy suite: summarize, tidy, predict. One call, done while you sleep."""
        run = OvernightRun(
            id=run_id,
            started_at=datetime.utcnow().isoformat() + "Z",
            finished_at=None,
            summary=None,
            tidy_actions=[],
            predictions=[],
            status="running",
        )
        self.runs[run_id] = run

        try:
            # 1. Summarize overnight messages
            summary = self.summarize_messages(messages, source="overnight-inbox")
            run.summary = summary.summary

            # 2. Tidy files (dry-run by default - safe)
            tidy = self.tidy_files(directory, dry_run=True)
            run.tidy_actions = tidy.actions

            # 3. Predict from CSV if provided
            if csv_path and target_column:
                run.predictions.append(self.predict_csv(csv_path, target_column))

            run.status = "done"
        except Exception as exc:  # pragma: no cover - defensive
            run.status = "error"
            run.summary = f"Error: {exc}"

        run.finished_at = datetime.utcnow().isoformat() + "Z"
        self.runs[run_id] = run
        return run

    def get_run(self, run_id: str) -> Optional[OvernightRun]:
        return self.runs.get(run_id)


# Singleton agent instance
sloth_agent = SlothAgent()
