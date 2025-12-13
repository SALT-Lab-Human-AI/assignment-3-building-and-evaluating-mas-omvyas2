#!/usr/bin/env bash
set -euo pipefail

# One-shot script to run a single query through the orchestrator and export artifacts.
# Loads API keys from .env if present.

if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

python - <<'PY'
import json, yaml
from pathlib import Path
from src.autogen_orchestrator import AutoGenOrchestrator

query = "Compare retrieval-augmented generation approaches for large language models"
config = yaml.safe_load(open("config.yaml"))
orch = AutoGenOrchestrator(config)
result = orch.process_query(query)

Path("outputs").mkdir(exist_ok=True)
with open("outputs/sample_session.json", "w") as f:
    json.dump(result, f, indent=2)

response = result.get("response", "")
citations = result.get("citations", []) or []
md_path = Path("outputs/sample_final.md")
md_path.write_text(
    "# " + query + "\n\n"
    + response + "\n\n"
    + "## Sources\n"
    + "\n".join(f"{i+1}. {c}" for i, c in enumerate(citations))
)
print("Wrote artifacts to outputs/sample_session.json and outputs/sample_final.md")
PY
