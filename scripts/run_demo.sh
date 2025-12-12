#!/usr/bin/env bash
set -e

# Simple end-to-end demo runner
# Usage: ./scripts/run_demo.sh
# Requires: OPENAI_API_KEY (and optional SEMANTIC_SCHOLAR_API_KEY)

echo "Running one-shot demo query and evaluation..."

QUERY="Summarize recent evaluation methods for large language models, including safety and bias metrics."

# Run a single orchestrator call and save session
python - <<'PY'
import json, yaml, os, time
from src.autogen_orchestrator import AutoGenOrchestrator

query = os.getenv("DEMO_QUERY") or "Summarize recent evaluation methods for large language models, including safety and bias metrics."
with open("config.yaml") as f:
    config = yaml.safe_load(f)
orch = AutoGenOrchestrator(config)
result = orch.process_query(query)

ts = time.strftime("%Y%m%d_%H%M%S")
session_path = f"outputs/demo_session_{ts}.json"
answer_path = f"outputs/demo_answer_{ts}.md"

with open(session_path, "w") as f:
    json.dump(result, f, indent=2)

with open(answer_path, "w") as f:
    f.write("# Demo Answer\n\n")
    f.write(result.get("response", ""))
    f.write("\n\n## Sources\n")
    for i, c in enumerate(result.get("metadata", {}).get("citations", []), 1):
        f.write(f"{i}. {c}\n")

print("Saved session to", session_path)
print("Saved answer to", answer_path)
PY

# Run evaluation across the dataset
python main.py --mode evaluate

echo "Demo complete. Check outputs/ for artifacts."
