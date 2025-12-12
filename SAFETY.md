# Safety Policy Overview

This system applies input and output guardrails to reduce unsafe behavior.

## Categories (blocked/sanitized)
- **Self-harm**: language encouraging self-harm or suicide.
- **Violence/terror/illegal**: violent, weapons, terroristic or illegal guidance.
- **PII**: social security numbers, credit cards, passwords, phone numbers.
- **Prompt injection** (input guard only): attempts to override system behavior.
- **Misinformation/off-topic**: flagged but generally not blocked unless combined with other risks.

## Behaviors
- **Inputs**: If unsafe, the request is refused with a safety message.
- **Outputs**: Unsafe content is sanitized or refused per `config.yaml` (`on_violation`).
- **Logging**: Safety events are recorded in `logs/safety_events.log` with type, preview, and violations.

## Configuration
- Set in `config.yaml` under `safety`. Default framework is `builtin`; NeMo rails can be configured but is currently disabled due to parsing issues.
- Block-on categories: `self_harm`, `violence`, `pii`, `illegal_content`.
- Response strategy: `refuse` with a configurable message (default: “I cannot process this request due to safety policies.”).

## Known limits
- Keyword-based heuristics may over/under-block nuanced content.
- If an API/tool fails, the system returns an error message and logs the event; users should retry or check logs.
