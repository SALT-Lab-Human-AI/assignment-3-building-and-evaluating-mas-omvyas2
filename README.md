# Multi-Agent Research Assistant (LLM-focused)

Streamlined, safety-aware multi-agent research assistant built with AutoGen. Four agents (Planner, Researcher, Writer, Critic) plus guardrails plan, search (web + papers), synthesize, and critique answers on Large Language Models (LLMs). A Streamlit UI exposes traces, citations, safety status, and evaluation summaries; CLI and evaluation modes are included.

![Demo Screenshot (replace with your capture)](documentation/demo_screenshot.png)

> Tip: capture your own screenshot/video after running the web app and place it at `documentation/demo_screenshot.png` (or link a video).
> Report: See `documentation/Technical_Report.md` (add a PDF or link here if required).

## Quickstart
Requirements: Python 3.10+, `pip install -r requirements.txt`. Set env vars: `OPENAI_API_KEY`, `TAVILY_API_KEY`. (Semantic Scholar paper search is keyless but rate-limited.)

### One-command demo
```bash
bash scripts/run_demo.sh
```
Runs an end-to-end example (orchestrator + evaluation) and writes artifacts to `outputs/`.

### Manual runs
- **Web UI**: `python main.py --mode web` (or `streamlit run src/ui/streamlit_app.py`)
- **CLI**: `python main.py --mode cli`
- **Evaluation (LLM-as-judge)**: `python main.py --mode evaluate`

## What to expect
- Agents coordinate via AutoGen RoundRobinGroupChat: Planner -> Researcher (web_search, paper_search) -> Writer -> Critic -> Safety.
- UI shows response, citations, safety status, quality metrics, agent messages/traces, and latest evaluation summary.
- Safety refuses/sanitizes unsafe content; events log to `logs/safety_events.log`.

## Tested queries (LLM-focused)
- Recent safety benchmarks and mitigations for large language models
- Compare retrieval-augmented generation approaches for LLMs
- Efficiency techniques for serving 70B+ LLMs on GPUs
- Evaluation methods for hallucination and factuality in LLMs

## Sample artifacts (in repo)
- `outputs/sample_session.json` (Planner/Researcher/Writer/Critic trace and final response)
- `outputs/sample_final.md` (final answer with inline citations + sources list)
- `outputs/sample_judge_output.json` (example judge scores/output)

Regenerate fresh artifacts with your keys: run the web/CLI/evaluate modes or `bash scripts/run_one_query.sh` and overwrite these files with real outputs.

## UI transparency
- Agent messages & traces are viewable in expanders.
- Tool calls are tagged (e.g., `[ToolCall] web_search ...`, `[ToolCall] paper_search ...`).
- Citations under “📚 Citations”; safety warnings appear when content is refused/sanitized.

## Safety
- Built-in guardrails for input/output (harmful content, personal attacks, misinformation, off-topic; plus self-harm, violence, PII, illegal content).
- NeMo Guardrails was attempted but disabled due to Colang parsing errors; fallback is the built-in guardrail stack. Configure in `config.yaml` under `safety.framework`.
- Logs: `logs/safety_events.log`.

## Evaluation (LLM-as-judge)
- Three judge prompts (`coverage_evidence_clarity`, `accuracy_safety`, `structure_faithfulness`) in `src/evaluation/judge.py`.
- Metrics: relevance/coverage, evidence quality, factual accuracy, safety compliance, clarity/organization (weights in `config.yaml`).
- Data: `data/example_queries.json` (trimmed to 3 queries for context safety).
- Outputs: `outputs/evaluation_*.json`; latest summary shown in the web UI.

## Reproducing the write-up results
1) Set env vars: `export OPENAI_API_KEY=...`, `export TAVILY_API_KEY=...` (or create `.env`).
2) Install deps: `pip install -r requirements.txt`.
3) Run one end-to-end query and export artifacts: `bash scripts/run_one_query.sh` (writes `outputs/sample_session.json` and `outputs/sample_final.md`).
4) Run evaluation (3 queries to avoid context bloat): `python main.py --mode evaluate`; then `latest=$(ls outputs/evaluation_*.json | sort | tail -1); cp "$latest" outputs/sample_judge_output.json`.
5) Web UI for screenshots: `python main.py --mode web`; submit a query, open Agent Messages/Traces and Citations, capture screenshot to `documentation/demo_screenshot.png`.
6) (Optional) Convert final Markdown to HTML:
   ```bash
   pip install markdown
   python - <<'PY'
   from pathlib import Path
   import markdown
   html = markdown.markdown(Path('outputs/sample_final.md').read_text())
   Path('outputs/sample_final.html').write_text(html)
   PY
   ```
7) Safety check: issue an unsafe query in the web UI (e.g., obvious PII) and confirm a warning/refusal plus an entry in `logs/safety_events.log`.

## Folder structure (key parts)
```
├── src/
│   ├── agents/               # Planner/Researcher/Writer/Critic + tool wiring
│   ├── guardrails/           # Safety manager + input/output guardrails (+ nemo wrapper)
│   ├── tools/                # web_search, paper_search
│   ├── evaluation/           # judge + evaluator
│   ├── ui/                   # streamlit_app.py, cli.py
│   └── autogen_orchestrator.py
├── data/example_queries.json # small eval set (3 queries)
├── outputs/                  # sample_session.json, sample_final.md/html, sample_judge_output.json
├── scripts/                  # run_demo.sh, run_one_query.sh
├── documentation/            # Technical_Report.md, demo_screenshot placeholder
├── config.yaml               # config (models, tools, safety, eval)
└── logs/                     # runtime and safety logs
```

## Known limitations / future work
- Semantic Scholar rate limits can yield empty paper results; web search still runs. Add caching/backoff or alternate paper APIs if needed.
- No live “active agent” indicator (traces are post-hoc). Could add streaming agent badges.
- NeMo rails parsing fails; fix Colang/YAML and re-enable `framework: nemo` when stable.
