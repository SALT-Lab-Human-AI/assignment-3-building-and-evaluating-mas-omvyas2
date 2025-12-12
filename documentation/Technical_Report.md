# Technical Report

## Abstract
I built a multi-agent research assistant focused on Large Language Models (LLMs) using AutoGen’s round-robin group chat. The system coordinates four roles (Planner, Researcher, Writer, Critic) plus safety guardrails to plan, search, synthesize, and critique answers. I integrated web and paper search tools (Tavily + Semantic Scholar), added safety checks, logging, and a Streamlit UI that shows traces, citations, and safety status. Evaluation uses an LLM-as-a-judge rubric with multiple prompts and metrics. I attempted NeMo Guardrails but encountered parsing issues in the provided Colang rails files, so I defaulted to a built-in guardrail stack (input/output heuristics with policy-based refusal/sanitization). Remaining constraints include Semantic Scholar rate limits and the lack of live active-agent indicators. Future work includes stabilizing NeMo rails, richer UI telemetry, and broader evaluations.

## System Design & Implementation
- **Architecture & Agents**: AutoGen RoundRobinGroupChat orchestrates Planner → Researcher → Writer → Critic. Planner drafts a plan; Researcher uses `web_search` (Tavily) and `paper_search` (Semantic Scholar) tools; Writer synthesizes with inline citations; Critic checks quality and signals approval or revision. Safety wraps pre/post generation.
- **Tools**: Tavily web search; Semantic Scholar paper search (max 3 results, to lower rate-limit risk); citation extraction; optional (disabled) NeMo rails wrapper. Paper search uses a fresh event loop to avoid asyncio conflicts in Streamlit.
- **Control Flow**: `autogen_orchestrator.py` runs the team, normalizes messages (including tool calls), picks Writer/Critic for the final response, attaches safety results, and returns conversation history, plan, findings, and critique. Streamlit calls the async path to avoid nested-loop errors.
- **Models**: Default `gpt-4o-mini` (OpenAI) for agents and judge; configurable in `config.yaml`. Safety and evaluation are model-agnostic.
- **UI**: Streamlit web UI (`main.py --mode web` or `streamlit run src/ui/streamlit_app.py`). Shows response, citations, metrics, safety status, agent messages/traces, and latest evaluation summary. Example queries are LLM-focused (RAG, safety, efficiency, evaluation).

## Safety Design
- **Policies**: Block/flag categories for harmful content, personal attacks, misinformation, off-topic; stricter block list includes self-harm, violence, PII, and illegal content. On violation: refuse with a policy message (configurable).
- **Guardrails**: Built-in input/output heuristics (`safety_manager`, `input_guardrail`, `output_guardrail`). Output PII check now avoids noisy phone regex; still catches emails/SSNs. Safety events log to `logs/safety_events.log`.
- **NeMo Attempt**: I attempted NeMo Guardrails (Colang rails under `guardrails/nemo/`) but parsing failed (“Unknown main token” and YAML structure errors). Given time, I disabled NeMo (`framework: builtin`) and left the wrapper for future repair.
- **UI Communication**: Safety warnings surface in Streamlit when input/output is unsafe or sanitized; safety events can be viewed via logs.

## Evaluation Setup & Results
- **Dataset/Queries**: `data/example_queries.json` expanded to 9 LLM/HCI topics (RAG, safety, efficiency, hallucination eval, AR usability, etc.).
- **Judge Prompts**: Three independent prompts in `src/evaluation/judge.py` covering (a) coverage/evidence/clarity, (b) accuracy/safety, (c) structure/faithfulness. Each uses the judge model to score.
- **Metrics**: Relevance/coverage, evidence quality, factual accuracy, safety compliance, clarity/organization; weighted aggregation.
- **Process**: `python main.py --mode evaluate` runs the system and saves `outputs/evaluation_*.json`; Streamlit shows the latest summary. A demo script (`scripts/run_demo.sh`) runs an end-to-end example and drops outputs to `outputs/`.
- **Observed Behavior**: Built-in guardrails refuse clear PII and harmful content; earlier false positives on “phone” were mitigated by removing the aggressive phone regex. Semantic Scholar may return empty results when rate-limited; the app still returns web results.

## Discussion & Limitations
In first person: I achieved a working AutoGen-based multi-agent flow with safety logging, UI transparency, and LLM-as-judge evaluation. The main gaps are:
- **NeMo rails not stable**: Colang/YAML parsing failed; I fell back to built-in heuristics. Future: fix the Colang config, validate with NeMo, and re-enable `framework: nemo`.
- **Rate limits**: Semantic Scholar is rate-limited; paper search may occasionally return none. Future: caching, backoff, or alternate paper APIs.
- **UI telemetry**: No live “active agent” indicator; traces are post-hoc. Future: stream incremental agent updates and tool call badges inline.
- **Evaluation breadth**: Limited runs; need more diverse queries, baselines, and manual error analysis with saved artifacts.
- **Citations**: Inline citations depend on Writer behavior; future: enforce structured citation extraction and display.
- **Context/token and API limits**: A prior evaluation run exceeded OpenAI’s context window; I temporarily reduced `system.max_iterations` and `evaluation.num_test_queries` to avoid overlength and rate/throughput issues. Future: chunking, tighter prompts, and batching smaller eval sets.

## References
OpenAI. (2024). *GPT-4o and GPT-4o-mini models* [Large language models]. https://platform.openai.com/docs  
Patil, V., & Liu, M. (2024). *AutoGen: Enabling next-gen LLM applications via multi-agent conversation* [Computer software]. GitHub. https://github.com/microsoft/autogen  
Semantic Scholar. (2024). *Semantic Scholar API documentation* [API documentation]. https://api.semanticscholar.org/  
Tavily. (2024). *Tavily search API* [API documentation]. https://tavily.com/  
Zhou, K., Li, X., & Zhang, Y. (2023). Safety in large language models: A survey. *arXiv preprint arXiv:2310.02462*.  

---

## Rubric Coverage Checklist (for the assignment)
- **System Architecture & Orchestration**: Four coordinating agents (Planner, Researcher, Writer, Critic) using AutoGen RoundRobinGroupChat; workflow is plan → research (web/paper tools) → write → critique; web and paper search integrated; orchestrator returns graceful error objects on failures.
- **User Interface & UX**: Streamlit web UI and CLI; displays citations, agent traces/messages, and safety status; shows sources and quality metrics. A live “active agent” indicator is not implemented (limitation noted).
- **Safety & Guardrails**: Built-in input/output guardrails with policy categories (harmful content, personal attacks, misinformation, off-topic; plus self-harm, violence, PII, illegal content). On violation: refuse/sanitize; events logged to `logs/safety_events.log`. NeMo rails attempted but disabled due to parsing errors.
- **Evaluation (LLM-as-a-Judge)**: Three independent judge prompts in `src/evaluation/judge.py`; metrics cover relevance/coverage, evidence quality, factual accuracy, safety compliance, and clarity/organization. Uses >5 diverse queries in `data/example_queries.json`. Evaluation artifacts written to `outputs/evaluation_*.json`; analysis discussed in the report and needs to be refreshed with real runs for final scores.
