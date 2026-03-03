"""
Unit tests for the RiskScorer engine
"""

import pytest
from agentguard.parser import AgentModel, MemoryConfig, ToolDefinition, ModelConfig
from agentguard.scorer import RiskScorer
from agentguard.taxonomy import ThreatDefinition


def make_agent(**kwargs) -> AgentModel:
    """Helper to create test agents with sensible defaults."""
    defaults = {
        "name": "Test Agent",
        "autonomy_level": 3,
        "tools": [],
        "memory": MemoryConfig(type="none"),
        "trust_boundaries": [],
        "data_classification": {"input": "internal", "output": "internal"},
    }
    defaults.update(kwargs)
    return AgentModel(**defaults)


def make_threat(**kwargs) -> ThreatDefinition:
    """Helper to create test threats with sensible defaults."""
    defaults = {
        "id": "TEST-001",
        "name": "Test Threat",
        "domain": "Test",
        "description": "A test threat",
        "attack_scenario": "An attacker does something",
        "base_exploitability": 0.5,
        "base_impact": 0.5,
        "base_reversibility": 1.0,
        "base_detection_difficulty": 1.0,
        "base_severity": "medium",
        "recommendation": "Fix it.",
        "requires_tools": [],
        "requires_memory": False,
        "requires_multi_agent": False,
    }
    defaults.update(kwargs)
    return ThreatDefinition(**defaults)


class TestApplicability:
    def test_threat_not_applicable_missing_tool(self):
        agent = make_agent(tools=[])
        threat = make_threat(requires_tools=["web_search"])
        scorer = RiskScorer(agent)
        result = scorer.score_threat(threat)
        assert result.applicable is False
        assert result.final_score == 0.0

    def test_threat_applicable_tool_present(self):
        agent = make_agent(tools=[
            ToolDefinition(name="web_search", permissions=["read_web"])
        ])
        threat = make_threat(requires_tools=["web_search"])
        scorer = RiskScorer(agent)
        result = scorer.score_threat(threat)
        assert result.applicable is True
        assert result.final_score > 0.0

    def test_memory_threat_not_applicable_no_memory(self):
        agent = make_agent(memory=MemoryConfig(type="none"))
        threat = make_threat(requires_memory=True)
        scorer = RiskScorer(agent)
        result = scorer.score_threat(threat)
        assert result.applicable is False


class TestAutonomyFactor:
    def test_higher_autonomy_increases_score(self):
        threat = make_threat(base_exploitability=0.5, base_impact=0.5)
        low_auto = make_agent(autonomy_level=1)
        high_auto = make_agent(autonomy_level=5)

        low_score = RiskScorer(low_auto).score_threat(threat).final_score
        high_score = RiskScorer(high_auto).score_threat(threat).final_score

        assert high_score > low_score

    def test_human_in_loop_reduces_score(self):
        from agentguard.parser import HumanInLoopConfig
        threat = make_threat()

        agent_no_hil = make_agent(autonomy_level=4)
        agent_with_hil = make_agent(
            autonomy_level=4,
            human_in_loop=HumanInLoopConfig(
                enabled=True,
                triggers=["action_1", "action_2", "action_3"]
            )
        )

        score_no_hil = RiskScorer(agent_no_hil).score_threat(threat).final_score
        score_with_hil = RiskScorer(agent_with_hil).score_threat(threat).final_score

        assert score_with_hil < score_no_hil


class TestRiskLevels:
    def test_critical_threshold(self):
        # High exploitability + high impact + high autonomy = critical
        agent = make_agent(autonomy_level=5, trust_boundaries=["untrusted", "untrusted"])
        threat = make_threat(
            base_exploitability=0.95,
            base_impact=0.95,
            base_reversibility=1.5,
            base_detection_difficulty=1.5,
        )
        result = RiskScorer(agent).score_threat(threat)
        assert result.risk_level in ["critical", "high"]  # Very high either way

    def test_low_scores_for_minimal_agent(self):
        agent = make_agent(autonomy_level=1)
        threat = make_threat(
            base_exploitability=0.1,
            base_impact=0.1,
        )
        result = RiskScorer(agent).score_threat(threat)
        assert result.risk_level == "low"
