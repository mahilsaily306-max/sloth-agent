---
title: Sloth Agent — the open-source AI agent that works while you laze
published: true
tags: devchallenge, hf26challenge, ai, open-source, automation, hacktoberfest
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge: Week 3 — Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19).*

## What I Built

**Sloth Agent** — an open-source AI automation agent that does your overnight chores so you can keep lazing. It reads your inbox/group chats and hands you a two-line morning summary, sorts and archives your messy files, and forecasts or classifies from your CSVs using TabPFN. All of it runs on open-weight models (Gemma) on your own machine — no API keys, no subscriptions, no internet required after download.

Repo: `mahilsaily306-max/sloth-agent`

## Demo

Deployed frontend: *(link goes here — render / digitalocean / .tech domain)*

Demo video: *(link goes here)*

Core flows, one click each:
- **Overnight Summary** → two-line summary of last night's messages
- **Tidy Files** → sort/rename/archive by type (dry-run safe by default)
- **Predict (TabPFN)** → forecast/classify from a CSV
- **Chat (Gemma)** → local open-weight model conversation
- **Full Overnight Run** → summarize + tidy + predict in a single call

## Code

<repo>mahilsaily306-max/sloth-agent</repo>

Key files:
- `backend/models/gemma.py` — Gemma open-weight model (Ollama / transformers / stub)
- `backend/models/tabpfn.py` — TabPFN tabular foundation model (sklearn fallback)
- `backend/agents/sloth_agent.py` — the agent: summarize, tidy, predict, overnight
- `backend/temporal/workflows.py` — durable Temporal workflow (retries, resume)
- `backend/sentry_config.py` — Sentry agent tracing (latency, tokens, cost)
- `integrations/integrations.ts` — SDK wrappers for all 20 partner categories
- `.github/workflows/ci.yml` — GitHub Actions CI (Copilot-reviewed)
- `render.yaml` — Render hosting config
- `backend/tests/smoke_test.py` — zero-dependency smoke tests (passing)

## How I Built It

Open-source AI at every layer:

- **Runtime:** Gemma (open-weight) via Ollama or Hugging Face transformers; falls back to a deterministic stub so the project runs with zero ML installs.
- **Tabular prediction:** TabPFN-3.5 (Prior Labs) for CSV forecasting; sklearn fallback if TabPFN isn't installed.
- **Orchestration:** Mastra-style agent pattern over open models with tools and memory.
- **Durability:** Temporal workflow wraps the overnight run so it survives failures and resumes where it left off.
- **Tracing:** Sentry captures agent setup, latency, tokens, cost, and errors.
- **Frontend:** Single-file HTML/JS dashboard calling the FastAPI backend.
- **CI:** GitHub Actions lint + smoke tests on every PR.

## Why Open Innovation Matters

Running open-weight models locally means:

1. **No internet needed.** Gemma + TabPFN run on a laptop offline after download. A closed API agent would stop working without connectivity.
2. **Data stays on your machine.** Your messages, files, and CSVs are never uploaded to a server you don't control.
3. **Set up once, never pay again.** Open-weight models cost $0 to run locally — no per-token charges, no subscriptions.
4. **Swap models freely.** Swap Gemma for Mistral, Llama, or any open weight; swap TabPFN for another tabular model. Closed APIs lock you into one vendor.

The open-based approach worked better here because this is a personal automation agent — privacy, offline use, and zero recurring cost matter more than a hosted SaaS.

## My Agent Session

Saved with [DevRelay](https://devrelay.com) and embedded below (Entire prize category: share the agent sessions behind your project).

*(agent_session embed link goes here)*

## The Lazy Payoff

Before Sloth Agent, you'd wake up, scroll through last night's group chat, dig through a messy downloads folder, and manually open spreadsheets to forecast — maybe 15–20 minutes of drudgery.

After: one `overnight` call runs while you sleep. Morning summary in two lines, files already sorted, CSV prediction ready. The agent does the work so you don't have to — and it runs for $0 on your own hardware.

## Prize Categories

Entering every applicable partner category:

**Featured ($200 each):** Gemma, TabPFN, Render, DigitalOcean, Tinker, Arduino

**Partner ($100 each):** Mastra, Sentry, Temporal, MongoDB Atlas, SerpApi, Browserbase, ElevenLabs, Auth0, Backboard, Entire, GitHub Copilot, .tech Domains, Tiger Data, Ultramarine

Each integration is coded in `integrations/integrations.ts` or configured (render.yaml, ci.yml) and documented in `docs/`.
