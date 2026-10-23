# Sloth Agent

Open-source AI that works while you laze. Built for the **Hacktoberfest Open-Source AI Challenge: Week 3 — Slow and Steady**.

> Theme: build something that does the work so you don't have to. Sloth Agent reads your overnight inbox/group chats, tidies your files, and forecasts from your CSVs — all while you sleep. Runs on open-weight models (Gemma) and open-source tooling, entirely local by default.

## What it does

| Lazy chore | How Sloth Agent handles it |
|---|---|
| Overnight inbox / group chats | Two-line morning summary highlighting only what needs action |
| Messy downloads / desktop folder | Sorts, renames, archives files by type (images, docs, spreadsheets, archives, installers) |
| Running the numbers on a CSV | Forecasts or classifies using TabPFN (Prior Labs' tabular foundation model) |
| Chatting with an assistant | Gemma, Google's open-weight model, running locally |
| Full nightly suite | One `overnight` call: summarize + tidy + predict |

## Why open innovation matters

- **Runs on a laptop with no internet.** Gemma + TabPFN run locally after download; no API keys, no servers, no per-call cost.
- **Your data stays on your machine.** Messages, files, and CSVs never leave your laptop — unlike closed SaaS agents that upload everything.
- **Set up once, never pay again.** Open-weight models cost $0 to run locally. No subscriptions, no rate limits.
- **Swap models freely.** The agent is model-agnostic: swap Gemma for Mistral, Llama, or another open weight; swap TabPFN for a sklearn fallback.

## Quick start

```bash
# 1. Clone
git clone https://github.com/mahilsaily306-max/sloth-agent.git
cd sloth-agent

# 2. Backend (Python 3.12+)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 3. Open http://localhost:8000 and click "Run Overnight Suite"
# 4. Or smoke-test:
python tests/smoke_test.py
```

With Docker (includes Temporal server):

```bash
docker compose up
```

## Prize integrations (all 20 categories)

Featured ($200 each):

- **Gemma** — core local open-weight LLM (`backend/models/gemma.py`)
- **TabPFN** — tabular forecast/classify from CSV (`backend/models/tabpfn.py`)
- **Render** — `render.yaml` deploys the frontend to Render
- **DigitalOcean** — deploy config in `docs/deploy.md`
- **Tinker** — fine-tune Gemma for overnight summarization (`docs/tinker.md`)
- **Arduino** — UNO Q physical agent sketch (`docs/arduino.md`; needs hardware)

Partner ($100 each):

- **Mastra** — agent orchestration over open models (`integrations/integrations.ts`)
- **Sentry** — agent tracing: latency, tokens, cost, errors (`backend/sentry_config.py`)
- **Temporal** — durable overnight workflows with retries/resume (`backend/temporal/workflows.py`)
- **MongoDB Atlas** — vector-search memory layer (`integrations/integrations.ts`)
- **SerpApi** — live web search grounding (`integrations/integrations.ts`)
- **Browserbase** — real browser for the agent (`integrations/integrations.ts`)
- **ElevenLabs** — voice narration for the agent (`integrations/integrations.ts`)
- **Auth0** — user sign-in to the agent (`integrations/integrations.ts`)
- **Backboard** — R-CLI terminal agent + model comparison (`integrations/integrations.ts`)
- **Entire** — share agent sessions via DevRelay (`docs/entire.md`)
- **GitHub Copilot** — CI/CD via GitHub Actions (`.github/workflows/ci.yml`)
- **.tech Domains** — claim free .tech domain at hacktoberfest.com/my/promos
- **Tiger Data** — pgvector embeddings + hybrid search (`docs/tiger.md`)
- **Ultramarine** — Paper Instruments model for analysis (`docs/ultramarine.md`)

## Project structure

```
backend/          FastAPI + Gemma + TabPFN + Sentry + Temporal
frontend/         Single-file HTML/JS dashboard
integrations/     TypeScript SDK wrappers for all partner services
.github/workflows/ GitHub Actions CI (Copilot-reviewed PRs)
render.yaml       Render hosting config
docker-compose.yml Local run incl. Temporal
sample.csv        Demo dataset for TabPFN predictions
DEV_SUBMISSION.md Ready-to-publish dev.to submission write-up
```

## License

MIT. Open source, open weights, open innovation.
