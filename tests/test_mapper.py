"""
Tests for agentguard.mapper — MITRE ATLAS technique enrichment.
"""

import pytest
from agentguard.mapper import AtlasMapper, AtlasEnrichment


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def mapper():
    return AtlasMapper()


# ── Initialization ────────────────────────────────────────────────────────────

class TestInitialization:
    def test_mapper_instantiates(self, mapper):
        assert mapper is not None

    def test_mapper_has_techniques(self, mapper):
        techniques = mapper.get_all_techniques()
        assert len(techniques) > 0

    def test_mapper_has_core_technique(self, mapper):
        """AML.T0051 (Prompt Injection) must always be present."""
        result = mapper.get_atlas_data("AML.T0051")
        assert result is not None

    def test_all_techniques_are_enrichment_objects(self, mapper):
        for t in mapper.get_all_techniques():
            assert isinstance(t, AtlasEnrichment)


# ── Core technique lookups ────────────────────────────────────────────────────

class TestCoreTechniques:
    EXPECTED_TECHNIQUES = [
        "AML.T0051",       # Prompt Injection
        "AML.T0051.001",   # Indirect Prompt Injection
        "AML.T0048",       # Excessive Agency
        "AML.T0020",       # Poison Training Data
        "AML.T0056",       # LLM Prompt/Output Extraction
        "AML.T0043",       # Craft Adversarial Data
        "AML.T0015",       # Evade ML Model
        "AML.T0010",       # ML Supply Chain Compromise
        "AML.T0018",       # Backdoor ML Model
        "AML.T0054",       # LLM Plugin Compromise
    ]

    @pytest.mark.parametrize("technique_id", EXPECTED_TECHNIQUES)
    def test_technique_present(self, mapper, technique_id):
        result = mapper.get_atlas_data(technique_id)
        assert result is not None, f"Technique {technique_id} not found in mapper"

    @pytest.mark.parametrize("technique_id", EXPECTED_TECHNIQUES)
    def test_technique_has_name(self, mapper, technique_id):
        result = mapper.get_atlas_data(technique_id)
        assert result.technique_name and len(result.technique_name) > 0

    @pytest.mark.parametrize("technique_id", EXPECTED_TECHNIQUES)
    def test_technique_has_tactic(self, mapper, technique_id):
        result = mapper.get_atlas_data(technique_id)
        assert result.tactic and len(result.tactic) > 0

    @pytest.mark.parametrize("technique_id", EXPECTED_TECHNIQUES)
    def test_technique_has_url(self, mapper, technique_id):
        result = mapper.get_atlas_data(technique_id)
        assert result.url.startswith("https://atlas.mitre.org/")

    @pytest.mark.parametrize("technique_id", EXPECTED_TECHNIQUES)
    def test_technique_has_description(self, mapper, technique_id):
        result = mapper.get_atlas_data(technique_id)
        assert result.description and len(result.description) > 20

    @pytest.mark.parametrize("technique_id", EXPECTED_TECHNIQUES)
    def test_technique_has_mitigation_guidance(self, mapper, technique_id):
        result = mapper.get_atlas_data(technique_id)
        assert result.mitigation_guidance and len(result.mitigation_guidance) > 10


# ── Specific technique data integrity ─────────────────────────────────────────

class TestTechniqueDataIntegrity:
    def test_prompt_injection_technique_name(self, mapper):
        t = mapper.get_atlas_data("AML.T0051")
        assert "Prompt Injection" in t.technique_name

    def test_prompt_injection_tactic_id(self, mapper):
        t = mapper.get_atlas_data("AML.T0051")
        assert t.tactic_id == "AML.TA000"

    def test_indirect_injection_is_sub_of_t0051(self, mapper):
        t = mapper.get_atlas_data("AML.T0051.001")
        assert "Indirect" in t.technique_name

    def test_supply_chain_technique(self, mapper):
        t = mapper.get_atlas_data("AML.T0010")
        assert "Supply Chain" in t.technique_name

    def test_id_matches_key(self, mapper):
        """technique_id field must match the key used to retrieve it."""
        t = mapper.get_atlas_data("AML.T0048")
        assert t.technique_id == "AML.T0048"

    def test_related_techniques_is_list(self, mapper):
        t = mapper.get_atlas_data("AML.T0051")
        assert isinstance(t.related_techniques, list)


# ── None / unknown lookups ────────────────────────────────────────────────────

class TestMissingLookups:
    def test_none_input_returns_none(self, mapper):
        result = mapper.get_atlas_data(None)
        assert result is None

    def test_empty_string_returns_none(self, mapper):
        result = mapper.get_atlas_data("")
        assert result is None

    def test_unknown_id_returns_none(self, mapper):
        result = mapper.get_atlas_data("AML.T9999")
        assert result is None

    def test_wrong_format_returns_none(self, mapper):
        result = mapper.get_atlas_data("T1059")  # MITRE ATT&CK format, not ATLAS
        assert result is None


# ── Tactic filtering ──────────────────────────────────────────────────────────

class TestTacticFiltering:
    def test_get_by_tactic_returns_list(self, mapper):
        results = mapper.get_techniques_by_tactic("AML.TA000")
        assert isinstance(results, list)

    def test_get_by_tactic_returns_matching_techniques(self, mapper):
        results = mapper.get_techniques_by_tactic("AML.TA000")
        for t in results:
            assert t.tactic_id == "AML.TA000"

    def test_get_by_unknown_tactic_returns_empty(self, mapper):
        results = mapper.get_techniques_by_tactic("AML.TA9999")
        assert results == []

    def test_exfiltration_tactic_has_techniques(self, mapper):
        results = mapper.get_techniques_by_tactic("AML.TA006")
        assert len(results) > 0


# ── to_dict serialization ─────────────────────────────────────────────────────

class TestSerialization:
    def test_to_dict_returns_dict(self, mapper):
        t = mapper.get_atlas_data("AML.T0051")
        d = t.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_has_required_keys(self, mapper):
        t = mapper.get_atlas_data("AML.T0051")
        d = t.to_dict()
        required_keys = {
            "technique_id", "technique_name", "tactic",
            "tactic_id", "description", "url",
            "mitigation_guidance", "related_techniques",
        }
        assert required_keys.issubset(d.keys())

    def test_to_dict_technique_id_correct(self, mapper):
        t = mapper.get_atlas_data("AML.T0056")
        d = t.to_dict()
        assert d["technique_id"] == "AML.T0056"
