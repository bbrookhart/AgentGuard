"""
Main Orchestration Engine
Coordinates parsing → scoring → mapping → reporting
"""

from agentguard.parser import AgentModel
from agentguard.scorer import RiskScorer, ScoredThreat
from agentguard.taxonomy import ThreatTaxonomy
from agentguard.mapper import AtlasMapper
from agentguard.reporter import ThreatReport


class AgentAnalyzer:
    """
    Primary interface for running a full threat analysis.

    Usage:
        analyzer = AgentAnalyzer.from_yaml("my_agent.yaml")
        report = analyzer.run()
        report.export("report.html", format="html")
    """

    def __init__(self, agent: AgentModel):
        self.agent = agent
        self.taxonomy = ThreatTaxonomy.load()
        self.scorer = RiskScorer(agent)
        self.mapper = AtlasMapper()

    @classmethod
    def from_yaml(cls, filepath: str) -> "AgentAnalyzer":
        from agentguard.parser import AgentArchitectureParser
        parser = AgentArchitectureParser(filepath)
        agent = parser.parse()
        return cls(agent)

    def run(self, verbose: bool = False) -> ThreatReport:
        """
        Execute the full analysis pipeline:
          1. Load all threat definitions
          2. Score each threat against the agent
          3. Enrich with MITRE ATLAS mappings
          4. Build and return the report
        """
        threats = self.taxonomy.get_all_threats()

        scored_threats = self.scorer.score_all(threats)

        # Enrich with ATLAS data
        for st in scored_threats:
            atlas_data = self.mapper.get_atlas_data(st.threat.atlas_technique)
            st.threat._atlas_enrichment = atlas_data

        report = ThreatReport(
            agent=self.agent,
            scored_threats=scored_threats,
        )

        return report
