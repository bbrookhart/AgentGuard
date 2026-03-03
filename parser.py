"""
Agent Architecture Parser
Ingests YAML/JSON agent definitions and returns a structured AgentModel
"""

import yaml
import json
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional


# ─────────────────────────────────────────
# Pydantic data models
# ─────────────────────────────────────────

class ModelConfig(BaseModel):
    provider: str = "openai"
    name: str = "gpt-4o"
    temperature: float = 0.7


class MemoryConfig(BaseModel):
    type: str = "none"            # none | buffer | vector_store | external_db
    provider: Optional[str] = None
    persistence: bool = False
    user_isolation: bool = True


class ToolDefinition(BaseModel):
    name: str
    description: str = ""
    permissions: list[str] = Field(default_factory=list)
    user_controlled: bool = False


class HumanInLoopConfig(BaseModel):
    enabled: bool = False
    triggers: list[str] = Field(default_factory=list)


class DataClassification(BaseModel):
    input: str = "internal"       # public | internal | confidential | PII | PHI
    output: str = "internal"
    training_data_used: bool = False


class AgentModel(BaseModel):
    """
    Full structured representation of an agent's architecture.
    This is the primary data object passed through the AgentGuard pipeline.
    """
    name: str
    version: str = "1.0.0"
    description: str = ""
    autonomy_level: int = Field(default=3, ge=1, le=5)
    model: ModelConfig = Field(default_factory=ModelConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    tools: list[ToolDefinition] = Field(default_factory=list)
    trust_boundaries: list[str] = Field(default_factory=list)
    human_in_loop: HumanInLoopConfig = Field(default_factory=HumanInLoopConfig)
    data_classification: DataClassification = Field(default_factory=DataClassification)


# ─────────────────────────────────────────
# Parser class
# ─────────────────────────────────────────

class AgentArchitectureParser:
    """
    Parses a YAML or JSON agent architecture file into an AgentModel.

    Usage:
        parser = AgentArchitectureParser("my_agent.yaml")
        agent = parser.parse()
    """

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"Agent file not found: {filepath}")

    def parse(self) -> AgentModel:
        raw = self._load_raw()
        agent_data = raw.get("agent", raw)   # Support both top-level and wrapped
        return AgentModel(**agent_data)

    def _load_raw(self) -> dict:
        suffix = self.filepath.suffix.lower()
        with open(self.filepath, "r", encoding="utf-8") as f:
            if suffix in (".yaml", ".yml"):
                return yaml.safe_load(f)
            elif suffix == ".json":
                return json.load(f)
            else:
                # Try YAML as default
                return yaml.safe_load(f)
