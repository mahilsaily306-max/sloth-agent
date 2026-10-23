"""Gemma open-weight model wrapper.

Sloth Agent runs on open-source AI at its core. Gemma (Google's open-weight
model) is the default local LLM. It can run:

1. Via Ollama (recommended): `ollama run gemma3:1b` then point OLLAMA_BASE_URL.
2. Via Hugging Face transformers + torch (heavier, GPU optional).
3. Stub mode: no ML deps installed -> returns deterministic canned responses
   so the whole project still runs and demonstrates the agent design.

Open innovation angle: the model lives on YOUR machine. No API key, no
internet required after download, your chats never leave your laptop.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class GemmaResponse:
    text: str
    model: str
    local: bool
    tokens: Optional[int] = None
    cost_usd: float = 0.0  # open-weight = $0 to run locally


class GemmaModel:
    def __init__(self, model_name: str = "gemma3:1b"):
        self.model_name = model_name
        self.backend = self._pick_backend()

    def _pick_backend(self) -> str:
        # Prefer Ollama (lightweight local runtime), then transformers, then stub.
        if os.environ.get("USE_OLLAMA", "1") == "1" and self._ollama_available():
            return "ollama"
        if self._transformers_available():
            return "transformers"
        return "stub"

    def _ollama_available(self) -> bool:
        try:  # pragma: no cover - depends on ollama CLI being installed
            import urllib.request

            base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
            req = urllib.request.Request(f"{base}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _transformers_available(self) -> bool:
        try:
            import transformers  # noqa: F401
            import torch  # noqa: F401
            return True
        except Exception:
            return False

    def generate(self, prompt: str, system: Optional[str] = None) -> GemmaResponse:
        if self.backend == "ollama":
            return self._generate_ollama(prompt, system)
        if self.backend == "transformers":
            return self._generate_transformers(prompt, system)
        return self._generate_stub(prompt, system)

    def _generate_ollama(self, prompt: str, system: Optional[str]) -> GemmaResponse:
        import urllib.request

        base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system or "You are Sloth Agent, a helpful open-source AI assistant.",
            "stream": False,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{base}/api/generate", data=data, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return GemmaResponse(
            text=result.get("response", ""),
            model=self.model_name,
            local=True,
            tokens=result.get("eval_count"),
            cost_usd=0.0,
        )

    def _generate_transformers(self, prompt: str, system: Optional[str]) -> GemmaResponse:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        model_id = os.environ.get("GEMMA_MODEL_ID", "google/gemma-2-2b-it")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id)
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer([text], return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=256, do_sample=True, temperature=0.7)
        decoded = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=True)
        return GemmaResponse(
            text=decoded,
            model=model_id,
            local=True,
            cost_usd=0.0,
        )

    def _generate_stub(self, prompt: str, system: Optional[str]) -> GemmaResponse:
        """Deterministic fallback so the agent works with zero ML dependencies."""
        lower = prompt.lower()
        if "summary" in lower or "summarize" in lower:
            text = (
                "Morning summary: 3 new items need your attention. "
                "Nothing urgent - you can keep lazing a while longer."
            )
        elif "tidy" in lower or "organize" in lower:
            text = "I've sorted your downloads folder and archived old files. Desktop is clean."
        elif "predict" in lower or "forecast" in lower:
            text = "Based on your data, the trend is slightly upward. No action needed."
        else:
            text = (
                "Sloth Agent is on the case. I'll handle it while you rest. "
                "Running locally on Gemma - your data never leaves this machine."
            )
        return GemmaResponse(
            text=text,
            model=self.model_name + " (stub)",
            local=True,
            cost_usd=0.0,
        )


# Singleton instance
gemma = GemmaModel()


def chat(prompt: str, system: Optional[str] = None) -> GemmaResponse:
    return gemma.generate(prompt, system)
