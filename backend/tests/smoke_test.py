"""Smoke tests for the Sloth Agent backend.

Verifies the agent runs end-to-end with zero ML dependencies (stub Gemma +
sklearn TabPFN fallback). Run with:  python backend/tests/smoke_test.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from agents.sloth_agent import ChatMessage, sloth_agent  # noqa: E402
from models.gemma import chat  # noqa: E402
from tasks.overnight import run_nightly  # noqa: E402


def test_chat_returns_local_reply():
    r = chat("smoke test")
    assert isinstance(r.text, str) and len(r.text) > 0
    assert r.local is True
    assert r.cost_usd == 0.0
    print("chat OK:", r.text[:60])


def test_overnight_run_completes():
    res = run_nightly(directory=".")
    assert res["status"] == "done"
    assert res["summary"] is not None
    assert isinstance(res["tidy_actions"], list)
    print("overnight OK:", res["status"], "|", res["summary"][:50])


def test_summarize_and_tidy_directly():
    msgs = [ChatMessage(sender="A", text="hi", timestamp="00:00")]
    s = sloth_agent.summarize_messages(msgs, "test")
    assert s.summary
    t = sloth_agent.tidy_files(".", dry_run=True)
    assert t.before_count >= 0
    print("summarize+tidy OK")


if __name__ == "__main__":
    test_chat_returns_local_reply()
    test_overnight_run_completes()
    test_summarize_and_tidy_directly()
    print("ALL SMOKE TESTS PASSED")
