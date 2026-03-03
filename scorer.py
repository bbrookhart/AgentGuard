"""
Risk Scoring Engine
Implements the 7-dimension agentic risk scoring model.

Score = (Exploitability × Impact × Autonomy × BlastRadius × Reversibility × Detection)
        ─────────────────────────────────────────────────────────────────────────────────
                                    MitigationFactor
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScoredThreat:
    """Result of scoring a single threat against an agent."""
    threat: object                   # ThreatDefinition (avoid circular import)
    exploitability: float = 0.0
    impact: float = 0.0
    autonomy_factor: float = 1.0
    blast_radius: float = 1.0
    reversibility: float = 1.0
    detection_difficulty: float = 1.0
    mitigation_factor: float = 1.0
    final_score: float = 0.0
    risk_level: str = "low"
    applicable: bool = True
    applicability_notes: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.threat.id,
            "name": self.threat.name,
            "domain": self.threat.domain,
            "atlas_technique": self.threat.atlas_technique,
            "risk_level": self.risk_level,
            "final_score": round(self.final_score, 2),
            "dimensions": {
                "exploitability": self.exploitability,
                "impact": self.impact,
                "autonomy_factor": self.autonomy_factor,
                "blast_radius": self.blast_radius,
                "reversibility": self.reversibility,
                "detection_difficulty": self.detection_difficulty,
                "mitigation_factor": self.mitigation_factor,
            },
            "recommendation": self.threat.recommendation,
            "applicable": self.applicable,
        }


class RiskScorer:
    """
    Scores threats against a specific agent architecture.

    The scoring model adapts each threat's base score using agent-specific
    context: autonomy level, tools present, memory type, human-in-loop,
    and data classification.
    """

    RISK_THRESHOLDS = {
        "critical": 8.5,
        "high": 6.5,
        "medium": 4.0,
        "low": 0.0,
    }

    def __init__(self, agent):
        """
        Args:
            agent: AgentModel — the parsed agent architecture
        """
        self.agent = agent

    def score_threat(self, threat) -> ScoredThreat:
        """Score a single ThreatDefinition against the loaded agent."""

        # Check applicability first
        applicable, notes = self._check_applicability(threat)

        if not applicable:
            return ScoredThreat(
                threat=threat,
                applicable=False,
                applicability_notes=notes,
                final_score=0.0,
                risk_level="low"
            )

        # Calculate each dimension
        exploitability = self._score_exploitability(threat)
        impact = self._score_impact(threat)
        autonomy_factor = self._score_autonomy_factor(threat)
        blast_radius = self._score_blast_radius(threat)
        reversibility = self._score_reversibility(threat)
        detection = self._score_detection_difficulty(threat)
        mitigations = self._score_mitigations(threat)

        # Compute raw score (normalize to 0–10)
        raw = (
            exploitability *
            impact *
            autonomy_factor *
            blast_radius *
            reversibility *
            detection
        ) / mitigations

        # Normalize: maximum possible raw value before normalization
        max_raw = 1.0 * 1.0 * 3.0 * 2.0 * 1.5 * 1.5 / 0.5
        final_score = min((raw / max_raw) * 10.0, 10.0)

        return ScoredThreat(
            threat=threat,
            exploitability=round(exploitability, 3),
            impact=round(impact, 3),
            autonomy_factor=round(autonomy_factor, 3),
            blast_radius=round(blast_radius, 3),
            reversibility=round(reversibility, 3),
            detection_difficulty=round(detection, 3),
            mitigation_factor=round(mitigations, 3),
            final_score=round(final_score, 2),
            risk_level=self._get_risk_level(final_score),
            applicable=True,
            applicability_notes=notes,
        )

    def score_all(self, threats: list) -> list[ScoredThreat]:
        """Score all threats and return sorted list (highest risk first)."""
        results = [self.score_threat(t) for t in threats]
        return sorted(results, key=lambda x: x.final_score, reverse=True)

    # ── Private scoring methods ──────────────────────────────────────────

    def _check_applicability(self, threat) -> tuple[bool, str]:
        """
        Determine if this threat is applicable to this specific agent.
        Returns (is_applicable, notes_string).
        """
        required_tools = getattr(threat, "requires_tools", [])
        agent_tool_names = {t.name for t in self.agent.tools}

        for req_tool in required_tools:
            if req_tool not in agent_tool_names:
                return False, f"Requires tool '{req_tool}' which is not present"

        requires_memory = getattr(threat, "requires_memory", False)
        if requires_memory and self.agent.memory.type == "none":
            return False, "Requires memory, but agent has no memory configured"

        requires_multi_agent = getattr(threat, "requires_multi_agent", False)
        if requires_multi_agent:
            return False, "Multi-agent threats require a multi-agent architecture"

        return True, ""

    def _score_exploitability(self, threat) -> float:
        """Base exploitability modified by attack surface."""
        base = threat.base_exploitability
        # Untrusted inputs increase exploitability
        untrusted_count = sum(
            1 for tb in self.agent.trust_boundaries
            if "untrusted" in tb.lower()
        )
        modifier = min(0.1 * untrusted_count, 0.3)
        return min(base + modifier, 1.0)

    def _score_impact(self, threat) -> float:
        """Base impact modified by data sensitivity."""
        base = threat.base_impact
        data_multipliers = {
            "PHI": 0.15, "PII": 0.10,
            "confidential": 0.05, "internal": 0.0, "public": -0.1
        }
        modifier = data_multipliers.get(self.agent.data_classification.input, 0.0)
        return min(max(base + modifier, 0.0), 1.0)

    def _score_autonomy_factor(self, threat) -> float:
        """
        Autonomy level (1–5) maps to factor (1.0–3.0).
        Higher autonomy means threats can propagate further without interruption.
        """
        autonomy_map = {1: 1.0, 2: 1.3, 3: 1.7, 4: 2.2, 5: 3.0}
        base_factor = autonomy_map.get(self.agent.autonomy_level, 1.7)

        # Human-in-loop reduces autonomy factor
        if self.agent.human_in_loop.enabled:
            triggers = len(self.agent.human_in_loop.triggers)
            reduction = min(0.2 * triggers, 0.6)
            base_factor = max(base_factor - reduction, 1.0)

        return base_factor

    def _score_blast_radius(self, threat) -> float:
        """How many systems/users can be affected."""
        base = 1.0
        # More tools = larger blast radius
        tool_count = len(self.agent.tools)
        if tool_count >= 5:
            base += 0.5
        elif tool_count >= 3:
            base += 0.3
        elif tool_count >= 1:
            base += 0.1

        # Write permissions expand blast radius
        write_tools = sum(
            1 for tool in self.agent.tools
            if any("write" in p or "send" in p or "delete" in p
                   for p in tool.permissions)
        )
        base += min(0.1 * write_tools, 0.5)

        return min(base, 2.0)

    def _score_reversibility(self, threat) -> float:
        """How hard is it to undo the damage? Higher = worse."""
        base = threat.base_reversibility
        # Persistent memory makes some attacks harder to reverse
        if self.agent.memory.persistence and "memory" in threat.domain.lower():
            base = min(base + 0.2, 1.5)
        return base

    def _score_detection_difficulty(self, threat) -> float:
        """How hard is it to detect? Higher = worse."""
        return threat.base_detection_difficulty

    def _score_mitigations(self, threat) -> float:
        """
        Returns a divisor representing mitigations present.
        Higher value = more mitigations = lower final score.
        Range: 0.5 (no mitigations) to 1.0 (strong mitigations).
        """
        # This can be extended to check for explicit mitigations
        # in the agent definition. Default: no mitigations assumed.
        return 0.5

    def _get_risk_level(self, score: float) -> str:
        if score >= 8.5:
            return "critical"
        elif score >= 6.5:
            return "high"
        elif score >= 4.0:
            return "medium"
        return "low"
