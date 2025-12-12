"""
Optional NeMo Guardrails wrapper.

This wrapper is designed to plug into SafetyManager when `framework: nemo` is set
in the safety config. If the `nemoguardrails` package or rails config is not
available, the wrapper will disable itself and the caller should fall back to
the built-in heuristic guardrails.
"""

from typing import Dict, Any, List, Optional
import logging
from pathlib import Path


class NemoGuardrailsWrapper:
    """
    Lightweight adapter around NeMo Guardrails.
    """

    def __init__(self, config: Dict[str, Any]):
        self.logger = logging.getLogger("safety.nemo")
        self.enabled = False
        self.rails = None

        # Config path where NeMo rails live (config.yml or directory)
        rails_path = config.get("nemo_config_path", "guardrails/nemo")
        self.rails_path = Path(rails_path)

        # Try to load NeMo Guardrails if installed
        try:
            from nemoguardrails import RailsConfig, LLMRails  # type: ignore

            if self.rails_path.exists():
                try:
                    # If path is a file, use it directly; if directory, let RailsConfig find config.yml
                    load_path = str(self.rails_path)
                    rails_config = RailsConfig.from_path(load_path)
                    self.rails = LLMRails(rails_config)
                    # Ensure required methods exist
                    if not hasattr(self.rails, "filter_prompt_async") or not hasattr(self.rails, "filter_response_async"):
                        self.logger.warning("NeMo Guardrails loaded but missing filter_* APIs; disabling.")
                        self.enabled = False
                    else:
                        self.enabled = True
                        self.logger.info(f"NeMo Guardrails enabled using config at {load_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to load NeMo rails config at {self.rails_path}: {e}")
                    self.enabled = False
            else:
                self.logger.warning(f"NeMo rails path not found: {self.rails_path}")
        except Exception as e:
            self.logger.warning(f"NeMo Guardrails not available, falling back to builtin: {e}")
            self.enabled = False

    async def check_input(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Run NeMo guardrails on input text. Returns None if disabled.
        """
        if not self.enabled or not self.rails:
            return None
        try:
            # NeMo Guardrails can classify inputs via the moderation pipeline
            result = await self.rails.filter_prompt_async(text)
            # Result is a dict with 'blocked' and 'violations'
            return {
                "safe": not result.get("blocked", False),
                "violations": result.get("violations", []),
                "sanitized_input": result.get("prompt", text),
            }
        except Exception as e:
            self.logger.error(f"NeMo input guardrails error: {e}")
            return None

    async def check_output(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Run NeMo guardrails on output text. Returns None if disabled.
        """
        if not self.enabled or not self.rails:
            return None
        try:
            result = await self.rails.filter_response_async(text)
            return {
                "safe": not result.get("blocked", False),
                "violations": result.get("violations", []),
                "sanitized_output": result.get("response", text),
            }
        except Exception as e:
            self.logger.error(f"NeMo output guardrails error: {e}")
            return None
