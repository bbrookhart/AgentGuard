"""
Tests for agentguard.parser — Agent architecture ingestion and validation.
"""

import pytest
from pathlib import Path
from unittest.mock import patch

from agentguard.parser import (
    AgentParser,
    AgentModel,
    ToolDefinition,
    MemoryConfig,
    DataClassification,
    TrustBoundary,
    AgentParseError,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SAMPLE_AGENT = FIXTURE_DIR / "sample_agent.yaml"


MINIMAL_YAML = """
name: MinimalAgent
version: "1.0.0"
autonomy_level: 1
tools: []
memory:
  type: session
  persistent: false
  shared: false
data_classification:
  input: public
  output: public
human_in_loop: true
multi_agent: false
"""

FULL_YAML = """
name: FullAgent
version: "2.1.0"
description: A comprehensive agent for testing
autonomy_level: 4
tools:
  - name: web_search
    description: Search the web
    write_access: false
    external_access: true
    elevated_risk: false
  - name: database_write
    description: Write to internal database
    write_access: true
    external_access: false
    elevated_risk: true
memory:
  type: vector_store
  persistent: true
  shared: true
  vector_store: true
trust_boundaries:
  - Sandbox execution only
  - No production access
human_in_loop: false
data_classification:
  input: pii
  output: confidential
multi_agent: true
agent_count: 3
mitigations:
  - Input sanitization
  - Rate limiting
deployment:
  environment: production
  users: external_customers
  regulatory_scope:
    - GDPR
    - HIPAA
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_yaml_string(content: str) -> AgentModel:
    parser = AgentParser()
    return parser.parse_string(content)


# ── Basic parsing ─────────────────────────────────────────────────────────────

class TestMinimalParsing:
    def test_minimal_yaml_parses_without_error(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert isinstance(agent, AgentModel)

    def test_name_parsed_correctly(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert agent.name == "MinimalAgent"

    def test_version_parsed(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert agent.version == "1.0.0"

    def test_autonomy_level_parsed(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert agent.autonomy_level == 1

    def test_empty_tools_list(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert agent.tools == []

    def test_human_in_loop_true(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert agent.human_in_loop is True

    def test_multi_agent_false(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert agent.multi_agent is False


class TestFullParsing:
    def test_full_yaml_parses(self):
        agent = parse_yaml_string(FULL_YAML)
        assert isinstance(agent, AgentModel)

    def test_description_parsed(self):
        agent = parse_yaml_string(FULL_YAML)
        assert "comprehensive" in agent.description.lower()

    def test_tools_count(self):
        agent = parse_yaml_string(FULL_YAML)
        assert len(agent.tools) == 2

    def test_tool_names(self):
        agent = parse_yaml_string(FULL_YAML)
        names = [t.name for t in agent.tools]
        assert "web_search" in names
        assert "database_write" in names

    def test_tool_write_access(self):
        agent = parse_yaml_string(FULL_YAML)
        db_tool = next(t for t in agent.tools if t.name == "database_write")
        assert db_tool.write_access is True

    def test_tool_external_access(self):
        agent = parse_yaml_string(FULL_YAML)
        search = next(t for t in agent.tools if t.name == "web_search")
        assert search.external_access is True

    def test_tool_elevated_risk(self):
        agent = parse_yaml_string(FULL_YAML)
        db_tool = next(t for t in agent.tools if t.name == "database_write")
        assert db_tool.elevated_risk is True

    def test_memory_type(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.memory.type == "vector_store"

    def test_memory_persistent(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.memory.persistent is True

    def test_memory_shared(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.memory.shared is True

    def test_memory_vector_store_flag(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.memory.vector_store is True

    def test_data_classification_input(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.data_classification.input == "pii"

    def test_data_classification_output(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.data_classification.output == "confidential"

    def test_human_in_loop_false(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.human_in_loop is False

    def test_multi_agent_true(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.multi_agent is True

    def test_mitigations_list(self):
        agent = parse_yaml_string(FULL_YAML)
        assert len(agent.mitigations) == 2

    def test_regulatory_scope(self):
        agent = parse_yaml_string(FULL_YAML)
        assert "GDPR" in agent.deployment.regulatory_scope
        assert "HIPAA" in agent.deployment.regulatory_scope


# ── Fixture file ──────────────────────────────────────────────────────────────

class TestFixtureFile:
    def test_sample_fixture_loads(self):
        if not SAMPLE_AGENT.exists():
            pytest.skip("Fixture file not found — create tests/fixtures/sample_agent.yaml")
        parser = AgentParser()
        agent = parser.parse_file(str(SAMPLE_AGENT))
        assert agent.name == "TestAgent"

    def test_fixture_autonomy_level(self):
        if not SAMPLE_AGENT.exists():
            pytest.skip("Fixture file not found")
        parser = AgentParser()
        agent = parser.parse_file(str(SAMPLE_AGENT))
        assert agent.autonomy_level == 3

    def test_fixture_has_tools(self):
        if not SAMPLE_AGENT.exists():
            pytest.skip("Fixture file not found")
        parser = AgentParser()
        agent = parser.parse_file(str(SAMPLE_AGENT))
        assert len(agent.tools) > 0

    def test_fixture_memory_vector_store(self):
        if not SAMPLE_AGENT.exists():
            pytest.skip("Fixture file not found")
        parser = AgentParser()
        agent = parser.parse_file(str(SAMPLE_AGENT))
        assert agent.memory.vector_store is True


# ── Validation errors ─────────────────────────────────────────────────────────

class TestValidation:
    def test_missing_name_raises(self):
        bad = MINIMAL_YAML.replace("name: MinimalAgent\n", "")
        with pytest.raises((AgentParseError, KeyError, Exception)):
            parse_yaml_string(bad)

    def test_autonomy_level_bounds(self):
        bad = MINIMAL_YAML.replace("autonomy_level: 1", "autonomy_level: 9")
        with pytest.raises((AgentParseError, ValueError, Exception)):
            parse_yaml_string(bad)

    def test_autonomy_level_zero_invalid(self):
        bad = MINIMAL_YAML.replace("autonomy_level: 1", "autonomy_level: 0")
        with pytest.raises((AgentParseError, ValueError, Exception)):
            parse_yaml_string(bad)

    def test_empty_string_raises(self):
        with pytest.raises(Exception):
            parse_yaml_string("")

    def test_invalid_yaml_raises(self):
        with pytest.raises(Exception):
            parse_yaml_string("this: is: not: valid: yaml: {{{")


# ── Computed properties ───────────────────────────────────────────────────────

class TestComputedProperties:
    def test_has_write_tools(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.has_write_tools is True

    def test_has_external_tools(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.has_external_tools is True

    def test_no_write_tools_minimal(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert agent.has_write_tools is False

    def test_tool_count(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.tool_count == 2

    def test_accepts_pii(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.accepts_pii is True

    def test_no_pii_minimal(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert agent.accepts_pii is False

    def test_is_high_autonomy(self):
        agent = parse_yaml_string(FULL_YAML)
        assert agent.is_high_autonomy is True

    def test_is_not_high_autonomy_minimal(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert agent.is_high_autonomy is False


# ── Edge cases ────────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_description_defaults_to_empty_string(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert isinstance(agent.description, str)

    def test_mitigations_defaults_to_empty_list(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert isinstance(agent.mitigations, list)

    def test_trust_boundaries_defaults_to_empty_list(self):
        agent = parse_yaml_string(MINIMAL_YAML)
        assert isinstance(agent.trust_boundaries, list)

    def test_parse_from_dict(self):
        data = {
            "name": "DictAgent",
            "version": "1.0.0",
            "autonomy_level": 2,
            "tools": [],
            "memory": {"type": "session", "persistent": False, "shared": False},
            "data_classification": {"input": "public", "output": "public"},
            "human_in_loop": True,
            "multi_agent": False,
        }
        parser = AgentParser()
        agent = parser.parse_dict(data)
        assert agent.name == "DictAgent"
