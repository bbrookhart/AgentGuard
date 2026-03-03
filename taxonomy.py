"""
Threat Taxonomy Loader
Loads and serves threat definitions from YAML model files
"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ThreatDefinition:
    """A single threat in the AgentGuard taxonomy."""
    id: str
    name: str
    domain: str
    description: str
    attack_scenario: str
    base_exploitability: float
    base_impact: float
    base_reversibility: float
    base_detection_difficulty: float
    atlas_technique: Optional[str] = None
    atlas_tactic: Optional[str] = None
    rmf_functions: list[str] = field(default_factory=list)
    requires_tools: list[str] = field(default_factory=list)
    requires_memory: bool = False
    requires_multi_agent: bool = False
    base_severity: str = "medium"
    recommendation: str = ""
    references: list[str] = field(default_factory=list)
    _atlas_enrichment: dict = field(default_factory=dict)


class ThreatTaxonomy:
    """
    Loads all threat definitions from the models/threats/ directory.
    Acts as the single source of truth for threat data.
    """

    MODELS_DIR = Path(__file__).parent.parent / "models" / "threats"

    def __init__(self, threats: list[ThreatDefinition]):
        self._threats = threats
        self._index = {t.id: t for t in threats}

    @classmethod
    def load(cls) -> "ThreatTaxonomy":
        """Load all threat YAML files from the models directory."""
        threats = []

        if not cls.MODELS_DIR.exists():
            # Return empty taxonomy if models dir not yet created
            return cls(threats)

        for yaml_file in sorted(cls.MODELS_DIR.glob("*.yaml")):
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            domain_name = data.get("domain", yaml_file.stem)
            for entry in data.get("threats", []):
                threat = ThreatDefinition(
                    id=entry["id"],
                    name=entry["name"],
                    domain=domain_name,
                    description=entry.get("description", ""),
                    attack_scenario=entry.get("attack_scenario", ""),
                    base_exploitability=float(entry.get("base_exploitability", 0.5)),
                    base_impact=float(entry.get("base_impact", 0.5)),
                    base_reversibility=float(entry.get("base_reversibility", 1.0)),
                    base_detection_difficulty=float(
                        entry.get("base_detection_difficulty", 1.0)
                    ),
                    atlas_technique=entry.get("atlas_technique"),
                    atlas_tactic=entry.get("atlas_tactic"),
                    rmf_functions=entry.get("rmf_functions", []),
                    requires_tools=entry.get("requires_tools", []),
                    requires_memory=entry.get("requires_memory", False),
                    requires_multi_agent=entry.get("requires_multi_agent", False),
                    base_severity=entry.get("base_severity", "medium"),
                    recommendation=entry.get("recommendation", ""),
                    references=entry.get("references", []),
                )
                threats.append(threat)

        return cls(threats)

    def get_all_threats(self) -> list[ThreatDefinition]:
        return list(self._threats)

    def get_by_id(self, threat_id: str) -> Optional[ThreatDefinition]:
        return self._index.get(threat_id)

    def get_threats(
        self,
        domain: Optional[str] = None,
        severity: Optional[str] = None
    ) -> list[ThreatDefinition]:
        results = self._threats
        if domain:
            results = [t for t in results if domain.lower() in t.domain.lower()]
        if severity:
            results = [t for t in results if t.base_severity == severity.lower()]
        return results
