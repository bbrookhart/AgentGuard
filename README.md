# 🛡️ AgentGuard
### Agentic AI Threat Modeling Framework

<p align="center">
  <img src="https://img.shields.io/badge/version-0.1.0-blue.svg" />
  <img src="https://img.shields.io/badge/python-3.10%2B-brightgreen.svg" />
  <img src="https://img.shields.io/badge/license-MIT-lightgrey.svg" />
  <img src="https://img.shields.io/badge/MITRE%20ATLAS-mapped-red.svg" />
  <img src="https://img.shields.io/badge/NIST%20AI%20RMF-aligned-orange.svg" />
  <img src="https://img.shields.io/badge/status-active-success.svg" />
</p>

<p align="center">
  <strong>The first open-source threat modeling framework purpose-built for agentic AI systems.</strong><br/>
  Model threats, score risk, and generate audit-ready reports for LLM agents,
  multi-agent pipelines, and autonomous AI workflows.
</p>

---

## 📌 Why AgentGuard Exists

Traditional threat modeling frameworks — STRIDE, PASTA, DREAD — were designed for
deterministic software systems. They assume predictable inputs, well-defined state,
and human-controlled execution flows.

**Agentic AI systems break every one of those assumptions.**

An agent equipped with tools (web search, code execution, file access, API calls)
operating inside an autonomous loop introduces a fundamentally new attack surface:

| Traditional System | Agentic AI System |
|--------------------|-------------------|
| Executes defined instructions | Interprets natural language goals |
| Bounded state transitions | Emergent multi-step reasoning |
| Human approves actions | Self-directed tool invocation |
| Single trust boundary | Dynamic, nested trust chains |
| Predictable outputs | Stochastic, context-dependent outputs |

No existing framework adequately addresses **prompt injection chains**,
**tool privilege escalation**, **memory poisoning**, or **multi-agent trust collapse**.
AgentGuard was built to fill this gap.

---

## 🎯 Who This Is For

- **AI Security Engineers** building or auditing agentic systems
- **GRC Professionals** responsible for AI risk programs
- **Red Teams** scoping engagements against LLM-powered products
- **AI/ML Engineers** who want to ship agents with a security mindset
- **Compliance Teams** mapping agent risks to NIST AI RMF, EU AI Act, or ISO 42001

---

## ✨ Features

- 🗂️ **Agentic Threat Taxonomy** — 47 categorized threats across 8 attack domains,
  mapped to MITRE ATLAS
- 🏗️ **Architecture Ingestion** — Define your agent in YAML/JSON; AgentGuard parses
  tools, memory, permissions, and trust boundaries
- 📊 **AI-Adapted Risk Scoring** — CVSS-inspired scoring extended with agentic
  dimensions: autonomy level, blast radius, reversibility
- 🗺️ **MITRE ATLAS Mapping** — Every threat linked to relevant ATLAS tactics and
  techniques
- 📋 **Report Generation** — Export audit-ready reports as HTML, PDF, or Markdown
- 🔌 **Framework Alignment** — Outputs tagged to NIST AI RMF functions
  (GOVERN, MAP, MEASURE, MANAGE)
- 🖥️ **CLI + Python API** — Use interactively or integrate into CI/CD pipelines

---

## 🚀 Quick Start

### Prerequisites

```
Python 3.10+
pip
```

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/agentguard.git
cd agentguard

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install AgentGuard in development mode
pip install -e .
```

### Run Your First Threat Model

```bash
# Analyze an example agent architecture
agentguard analyze --input examples/research_agent.yaml --output report.html

# View all threats in the taxonomy
agentguard list-threats

# Score a specific threat against your architecture
agentguard score --threat PI-002 --agent examples/research_agent.yaml

# Generate a blank agent template to fill in
agentguard init --name "My Agent" --output my_agent.yaml
```

---

## 📁 Project Structure

```
agentguard/
│
├── README.md                        # You are here
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package configuration
├── .gitignore
│
├── agentguard/                      # Core package
│   ├── __init__.py
│   ├── cli.py                       # CLI entry point (Click)
│   ├── analyzer.py                  # Main orchestration engine
│   ├── scorer.py                    # Risk scoring logic
│   ├── mapper.py                    # MITRE ATLAS mapping engine
│   ├── reporter.py                  # Report generation
│   ├── parser.py                    # Agent architecture parser
│   └── taxonomy.py                  # Threat taxonomy loader
│
├── models/                          # Threat taxonomy definitions
│   ├── threats/
│   │   ├── prompt_injection.yaml    # 8 prompt injection threats
│   │   ├── tool_misuse.yaml         # 7 tool misuse threats
│   │   ├── memory_poisoning.yaml    # 6 memory attack threats
│   │   ├── privilege_escalation.yaml
│   │   ├── goal_misgeneralization.yaml
│   │   ├── data_exfiltration.yaml
│   │   ├── multi_agent_collapse.yaml
│   │   └── supply_chain.yaml
│   ├── atlas_mappings.yaml          # MITRE ATLAS technique references
│   └── rmf_mappings.yaml            # NIST AI RMF function mappings
│
├── templates/                       # Report output templates
│   ├── report.html.j2               # Jinja2 HTML report template
│   ├── report.md.j2                 # Markdown report template
│   └── executive_summary.j2        # Executive summary template
│
├── examples/                        # Sample agent architectures
│   ├── research_agent.yaml
│   ├── coding_agent.yaml
│   ├── customer_service_agent.yaml
│   └── multi_agent_pipeline.yaml
│
├── tests/                           # Test suite
│   ├── test_parser.py
│   ├── test_scorer.py
│   ├── test_mapper.py
│   └── fixtures/
│
├── .github/
│   └── workflows/
│       └── agentguard-ci.yml        # CI/CD pipeline
│
└── docs/                            # Extended documentation
    ├── methodology.md               # Threat modeling methodology
    ├── threat_taxonomy.md           # Full taxonomy reference
    ├── scoring_guide.md             # How risk scores are calculated
    ├── atlas_reference.md           # MITRE ATLAS integration guide
    └── contributing.md              # Contribution guidelines
```

---

## 🏗️ Defining Your Agent Architecture

AgentGuard ingests your agent's architecture as a YAML file.
Here's the complete schema with annotations:

```yaml
# my_agent.yaml

agent:
  name: "Customer Support Agent"
  version: "1.2.0"
  description: "Handles tier-1 customer inquiries and CRM updates"
  autonomy_level: 3          # 1 (fully supervised) → 5 (fully autonomous)

  model:
    provider: "openai"
    name: "gpt-4o"
    temperature: 0.2

  memory:
    type: "vector_store"       # none | buffer | vector_store | external_db
    provider: "pinecone"
    persistence: true          # Does memory survive session end?
    user_isolation: true       # Is each user's memory isolated from others?

  tools:
    - name: "web_search"
      description: "Searches the internet"
      permissions: ["read_web"]
      user_controlled: false

    - name: "crm_update"
      description: "Updates customer records in Salesforce"
      permissions: ["read_crm", "write_crm"]
      user_controlled: false

    - name: "email_sender"
      description: "Sends emails on behalf of support team"
      permissions: ["send_email"]
      user_controlled: false

  trust_boundaries:
    - "User input (untrusted)"
    - "Internal CRM API (trusted)"
    - "External web content (untrusted)"

  human_in_loop:
    enabled: false
    triggers: []

  data_classification:
    input: "PII"               # public | internal | confidential | PII | PHI
    output: "internal"
    training_data_used: false
```

---

## 📊 Risk Scoring Methodology

AgentGuard scores each applicable threat using a **7-dimension model**
adapted specifically for agentic AI systems:

```
Risk Score =
  (Exploitability × Impact × Autonomy_Factor × Blast_Radius × Reversibility × Detection_Difficulty)
  ─────────────────────────────────────────────────────────────────────────────────────────────────
                                      Mitigations_Present

  Normalized to 0.0 – 10.0
```

### Scoring Dimensions

| Dimension | What It Measures | Scale |
|-----------|-----------------|-------|
| **Exploitability** | How easily can an attacker trigger this threat? | 0.0 – 1.0 |
| **Impact** | What is the potential damage if exploited? | 0.0 – 1.0 |
| **Autonomy Factor** | Does agent autonomy amplify propagation? | 1.0 – 3.0 |
| **Blast Radius** | How many systems or users can be affected? | 1.0 – 2.0 |
| **Reversibility** | Can the damage be undone after the fact? | 1.0 – 1.5 |
| **Detection Difficulty** | How hard is the threat to observe in production? | 1.0 – 1.5 |
| **Mitigations Present** | Controls already in place (acts as divisor) | 0.5 – 1.0 |

### Risk Levels

| Score | Level | Recommended Action |
|-------|-------|--------------------|
| 8.5 – 10.0 | 🔴 **Critical** | Block deployment or remediate immediately |
| 6.5 – 8.4 | 🟠 **High** | Address within current sprint |
| 4.0 – 6.4 | 🟡 **Medium** | Schedule for next planning cycle |
| 0.0 – 3.9 | 🟢 **Low** | Document, monitor, accept risk |

### The Autonomy Factor — The Key Innovation

The most important dimension unique to AgentGuard is the **Autonomy Factor**.

In a supervised system (level 1), a human approves every significant action.
Even a successful prompt injection is likely caught before damage occurs.

In a fully autonomous system (level 5), there is no human checkpoint.
A successful injection can execute a complete kill chain — initial access,
lateral movement, data exfiltration — without any human ever observing it.

The same underlying vulnerability can be 3x more dangerous in an autonomous agent
than in a supervised one. Autonomy Factor captures this numerically.

---

## 🗺️ MITRE ATLAS Mapping

Every threat in AgentGuard's taxonomy is mapped to relevant
[MITRE ATLAS](https://atlas.mitre.org/) tactics and techniques.

```
Threat: Indirect Prompt Injection via Retrieved Documents (PI-002)
  │
  ├── ATLAS Tactic:      ML Attack Staging (AML.TA000)
  ├── ATLAS Technique:   Prompt Injection (AML.T0051)
  │   └── Sub-technique: Indirect Prompt Injection (AML.T0051.001)
  │
  └── ATLAS Tactic:      Impact (AML.TA0009)
      └── ATLAS Technique: Evade ML Model (AML.T0015)
```

---

## 📋 Sample Report Output

```
╔══════════════════════════════════════════════════════════════════╗
║             AGENTGUARD THREAT MODEL REPORT                       ║
║             Customer Support Agent v1.2.0                        ║
║             Generated: 2025-01-15  |  AgentGuard v0.1.0          ║
╚══════════════════════════════════════════════════════════════════╝

EXECUTIVE SUMMARY
─────────────────
Agent Analyzed:    Customer Support Agent
Autonomy Level:    3 / 5 (Conditional Automation)
Threats Evaluated: 47
Applicable:        31
──────────────────────
  Critical:  2     🔴
  High:      7     🟠
  Medium:   11     🟡
  Low:      11     🟢

Overall Risk Score: 7.4 / 10.0  →  HIGH
Recommended Action: Do not deploy without addressing Critical findings.

────────────────────────────────────────────────────────────────────
TOP CRITICAL FINDINGS
────────────────────────────────────────────────────────────────────

[1]  CRITICAL  9.2  ──  Indirect Prompt Injection via Web Search
     ─────────────────────────────────────────────────────────────
     Domain:       Prompt Injection
     ATLAS:        AML.T0051.001
     Tools at risk: web_search → crm_update → email_sender

     Attack chain:
       Adversarial content embedded in a public web page is retrieved
       by the agent's web_search tool. The injected instructions direct
       the agent to update CRM records or send emails to attacker-
       controlled addresses. The user never sees this occur.

     Scoring breakdown:
       Exploitability:       0.80  (untrusted web content in context)
       Impact:               0.90  (PII + write access to CRM)
       Autonomy Factor:      1.70  (level 3, no human checkpoint)
       Blast Radius:         1.60  (5 tools, 2 with write permissions)
       Reversibility:        1.20  (CRM writes not auto-reverted)
       Detection Difficulty: 1.40  (hard to distinguish from normal use)
       Mitigation Factor:    0.50  (no mitigations configured)
       ──────────────────────────────────────────────────────────
       Final Score:          9.2 / 10.0   🔴 CRITICAL

     Recommendation:
       Implement an output sanitization layer between web_search results
       and the agent's reasoning context. Treat retrieved web content as
       untrusted data, not instructions. Apply a secondary classifier to
       flag potential injection payloads before context insertion.

[2]  CRITICAL  8.8  ──  Privilege Escalation via Tool Chaining
     ─────────────────────────────────────────────────────────────
     Domain:       Privilege Escalation
     ATLAS:        AML.T0048
     Tools at risk: crm_lookup → web_search → email_sender

     Attack chain:
       Each tool invocation is individually authorized. However, the
       chain crm_lookup (retrieve PII) → email_sender (transmit PII)
       achieves an effect that would be denied if requested directly.
       The agent acts as an unwitting exfiltration vector.

     Recommendation:
       Implement intent-aware tool chain validation. Before executing
       a multi-tool sequence, validate that the combined effect is
       consistent with the authorized intent of the session.
```

---

## 🧩 Threat Taxonomy Overview

| Domain | Threats | Key Attack Examples |
|--------|---------|---------------------|
| 🎯 **Prompt Injection** | 8 | Direct, Indirect, Multi-turn, RAG poisoning |
| 🔧 **Tool Misuse** | 7 | Unauthorized invocation, SSRF, excess permissions |
| 🧠 **Memory Attacks** | 6 | Session poisoning, cross-user contamination, embedding attacks |
| 🔑 **Privilege Escalation** | 5 | Tool chaining, permission boundary violations, role confusion |
| 🎭 **Goal Misgeneralization** | 4 | Specification gaming, reward hacking, distributional shift |
| 📤 **Data Exfiltration** | 6 | PII leakage, model inversion, training data extraction |
| 🕸️ **Multi-Agent** | 7 | Trust collapse, orchestrator compromise, agent impersonation |
| 📦 **Supply Chain** | 4 | Poisoned plugins, malicious tool providers, model tampering |

Full taxonomy reference: [`docs/threat_taxonomy.md`](docs/threat_taxonomy.md)

---

## 🖥️ CLI Reference

```bash
# Analyze an agent architecture file → generate threat model report
agentguard analyze --input <file> --output <report> --format [html|md|pdf]

# List all threats in the taxonomy
agentguard list-threats [--domain <domain>] [--severity <level>]

# Score a single threat against a specific agent
agentguard score --threat <threat-id> --agent <file>

# Compare two agent versions (e.g. before and after security changes)
agentguard diff --baseline <file> --current <file>

# Generate a blank agent architecture template
agentguard init --name "My Agent" --output my_agent.yaml

# Validate a YAML file against the AgentGuard schema
agentguard validate --input <file>
```

---

## 🔌 Python API

```python
from agentguard import AgentAnalyzer

# Load and analyze an agent
analyzer = AgentAnalyzer.from_yaml("my_agent.yaml")
report = analyzer.run()

# Access structured results
for threat in report.critical_threats:
    print(f"{threat.threat.id}: {threat.threat.name} — {threat.final_score}/10")

# Export in any format
report.export("report.html", format="html")
report.export("report.md",   format="md")
report.export("report.pdf",  format="pdf")

# CI/CD integration — raises SystemExit(1) if critical threats found
if report.has_critical_threats():
    raise SystemExit(1)
```

---

## 🧪 CI/CD Security Gate

Embed AgentGuard directly into your deployment pipeline to prevent
insecure agent architectures from reaching production:

```yaml
# .github/workflows/agentguard.yml
name: AI Security Gate

on: [push, pull_request]

jobs:
  threat-model:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install AgentGuard
        run: pip install agentguard

      - name: Run Threat Model
        run: |
          agentguard analyze \
            --input agent_architecture.yaml \
            --output security-report.html \
            --fail-on critical,high

      - name: Upload Report as Artifact
        uses: actions/upload-artifact@v4
        with:
          name: agentguard-threat-report
          path: security-report.html
```

---

## 🗺️ Regulatory Alignment

| Requirement | Source Framework | AgentGuard Coverage |
|-------------|-----------------|---------------------|
| Risk identification for AI systems | NIST AI RMF — MAP 1.1 | ✅ Full threat enumeration |
| Documentation of AI risks | NIST AI RMF — MEASURE 2.5 | ✅ Audit-ready report export |
| Security requirements for high-risk AI | EU AI Act — Article 9 | ✅ Risk scoring + control recs |
| Adversarial robustness testing | ISO 42001 — Clause 8.4 | ✅ ATLAS-mapped threat library |
| AI risk identification and assessment | NIST CSF 2.0 — ID.RA | ✅ Risk register output |
| AI incident readiness | NIST AI RMF — MANAGE 4.1 | ✅ Threat prioritization output |

---

## 🤝 Contributing

The agentic AI threat landscape evolves fast. Contributions are actively needed.

**High-priority contribution areas:**

- New threat definitions — follow the YAML format in `models/threats/`
- MITRE ATLAS mapping updates as new techniques are catalogued
- Framework alignment additions: DORA, FedRAMP AI, HIPAA AI
- Real-world agent architecture examples from production deployments
- Translations of methodology docs

See [`docs/contributing.md`](docs/contributing.md) for full guidelines.

---

## 📚 References & Further Reading

- [MITRE ATLAS](https://atlas.mitre.org/) — Adversarial Threat Landscape for AI Systems
- [NIST AI RMF 1.0](https://airc.nist.gov/RMF) — NIST AI Risk Management Framework
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — LLM Application Security Risks
- [EU AI Act](https://artificialintelligenceact.eu/) — Full text and annexes
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html) — AI Management Systems
- [CISA AI Security Guidance](https://www.cisa.gov/ai)
- [Anthropic Responsible Scaling Policy](https://www.anthropic.com/index/anthropics-responsible-scaling-policy)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
Free to use, modify, and distribute. Attribution appreciated.

---

## 👤 Author

Built by **[Your Name]** as part of an open AI GRC knowledge initiative.

| Platform | Link |
|----------|------|
| 🐦 Twitter/X | @Aether_Horizon |
| 💼 LinkedIn | linkedin.com/brian-brookhart |
| 📺 YouTube | @Aether-Horizon |


---

<p align="center">
  <sub>
    If AgentGuard helped you ship safer AI, please ⭐ the repo.<br/>
    It helps other security engineers find it.
  </sub>
</p>
