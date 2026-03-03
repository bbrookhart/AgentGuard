# Contributing to AgentGuard

AgentGuard is an open-source project. Contributions are welcome and
actively encouraged — particularly from security practitioners,
AI/ML engineers, and GRC professionals who work with agentic systems.

---

## What We Need Most

In rough priority order:

1. **New threat entries** — AI agent threats not yet in the taxonomy
2. **Real-world scenario validation** — have you seen a threat in
   production? Help us make the attack scenario more accurate.
3. **Bug reports** — scoring errors, parser failures, report issues
4. **ATLAS mapping corrections** — ATLAS is updated regularly; mappings
   go stale
5. **New example agent architectures** — real architectures (anonymized)
   are more valuable than synthetic ones
6. **Integration guides** — how to run AgentGuard in your specific
   CI/CD or deployment environment

---

## Development Setup

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/agentguard.git
cd agentguard

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate          # Windows

# 3. Install in development mode with all extras
pip install -e ".[dev]" --break-system-packages

# 4. Verify everything works
pytest tests/ -v

# 5. Run the CLI against a sample agent
agentguard analyze examples/research_agent.yaml
```

**Required Python:** 3.10+

**Core dependencies:**
- `click` — CLI framework
- `pyyaml` — YAML parsing
- `jinja2` — report templating
- `rich` — terminal output formatting

**Dev dependencies (installed with `[dev]` extra):**
- `pytest`, `pytest-cov` — test runner
- `ruff` — linting and formatting
- `mypy` — type checking

---

## Project Structure

```
agentguard/
├── agentguard/         ← Core Python package — start here for logic changes
│   ├── analyzer.py     ← Main orchestration: coordinates all modules
│   ├── parser.py       ← YAML ingestion and AgentModel construction
│   ├── scorer.py       ← 7-dimension risk scoring engine
│   ├── mapper.py       ← MITRE ATLAS enrichment
│   ├── reporter.py     ← HTML/MD/JSON/PDF report generation
│   ├── taxonomy.py     ← Threat YAML loader and ThreatDefinition builder
│   └── cli.py          ← Click CLI entry point
│
├── models/
│   ├── threats/        ← One YAML per threat domain — add new threats here
│   ├── atlas_mappings.yaml   ← ATLAS technique reference data
│   └── rmf_mappings.yaml     ← NIST AI RMF function mappings
│
├── templates/          ← Jinja2 report templates — modify for report changes
├── examples/           ← Sample agent YAMLs — add new examples here
├── tests/              ← Pytest test suite
└── docs/               ← Documentation source
```

---

## Adding a New Threat

The most common contribution. All threat definitions live in
`models/threats/` as YAML files organized by domain.

### Step 1 — Find the right domain file

| Domain | File |
|--------|------|
| Prompt Injection | `models/threats/prompt_injection.yaml` |
| Tool Misuse | `models/threats/tool_misuse.yaml` |
| Memory Attacks | `models/threats/memory_poisoning.yaml` |
| Privilege Escalation | `models/threats/privilege_escalation.yaml` |
| Goal Misgeneralization | `models/threats/goal_misgeneralization.yaml` |
| Data Exfiltration | `models/threats/data_exfiltration.yaml` |
| Multi-Agent Collapse | `models/threats/multi_agent_collapse.yaml` |
| Supply Chain | `models/threats/supply_chain.yaml` |

If your threat doesn't fit any existing domain, open an issue to
discuss adding a new domain before writing the YAML.

### Step 2 — Use the threat template

```yaml
- id: "XX-NNN"                    # Domain prefix + sequential number
  name: "Threat Name"             # Short, specific, searchable
  base_severity: "high"           # critical | high | medium | low
  base_exploitability: 0.70       # 0.0–1.0 (see scoring_guide.md)
  base_impact: 0.80               # 0.0–1.0
  base_reversibility: 1.3         # 1.0–1.5
  base_detection_difficulty: 1.4  # 1.0–1.6 (informational, not in score)
  atlas_technique: "AML.T0051"    # Primary ATLAS technique ID
  atlas_tactic: "AML.TA000"       # Corresponding tactic ID
  rmf_functions:                  # NIST AI RMF functions this maps to
    - "MAP"
    - "MEASURE"
  # Optional applicability flags — omit if threat applies universally
  requires_memory: true
  requires_multi_agent: true
  requires_pii_input: true
  description: >
    Clear, factual description of the threat. What is the mechanism?
    Why does it exist in agentic systems specifically? 2–4 sentences.
  attack_scenario: >
    A concrete, specific scenario showing how the threat is exploited
    against a real agent type. Include specific tool names, data types,
    and action sequences. This is the most important field — make it
    real enough that a security engineer immediately recognizes it.
  recommendation: >
    One to three specific, actionable countermeasures. Favor technical
    controls over policy. Be specific — not "implement access controls"
    but "restrict CRM read tool output from being passed to email_sender."
  references:
    - "https://atlas.mitre.org/techniques/AML.T0051"
    - "https://example.com/relevant-research-paper"
```

### Step 3 — Calibrate the scores

Before submitting, verify your base scores are calibrated against
existing threats in the same domain. Compare:

- Is this threat more or less exploitable than existing threats at
  similar severity? The scores should reflect that relative ordering.
- Is the attack scenario realistic or theoretical? Theoretical threats
  get lower exploitability scores.
- Does the `base_severity` match the CVSS-equivalent severity you
  would assign this finding if discovered in a penetration test?

### Step 4 — Test it

```bash
# Run the full test suite — all existing tests must pass
pytest tests/ -v

# Verify your new threat loads correctly
python -c "
from agentguard.taxonomy import ThreatTaxonomy
t = ThreatTaxonomy()
print(f'Loaded {len(t.all_threats())} threats')
for threat in t.all_threats():
    if threat.id == 'XX-NNN':  # your new threat ID
        print(f'Found: {threat.name}')
        break
"

# Run a full analysis to see your threat scored
agentguard analyze examples/research_agent.yaml --format md
```

### Step 5 — Open a pull request

Include in your PR description:
- Why this threat belongs in the taxonomy
- One or more real-world references (CVEs, research papers, published
  incident reports, or ATLAS case studies) if available
- How you calibrated the base scores
- Whether you've observed this threat in a production system
  (anonymized details are fine and very helpful)

---

## Modifying the Scoring Engine

The scoring model is in `agentguard/scorer.py`. Changes here affect
every threat score for every user.

**Before changing the scoring model:**

1. Open an issue first. Scoring changes should be discussed before
   implementation because they affect reproducibility — a team tracking
   their agent's score over time will see unexpected changes if the
   model shifts under them.

2. Any change to the formula must be accompanied by:
   - Updated `docs/scoring_guide.md` explaining the change
   - A worked example showing before/after scores for the same agent
   - Updated tests in `tests/test_scorer.py`

3. Score-affecting changes require a minor version bump per semver.

---

## Modifying Report Templates

Templates are in `templates/` as Jinja2 files.

- `report.html.j2` — Full HTML report
- `report.md.j2` — Markdown report
- `executive_summary.j2` — HTML executive summary (board/management)

When modifying templates:
- Test against all four example agent YAMLs
- Verify the template renders correctly when there are zero findings
- Verify it renders correctly when all severity levels are present
- Do not add fields to the template that don't exist on `ThreatReport`
  or `AgentModel` — this silently produces empty output in Jinja2

---

## Code Standards

```bash
# Lint and format (ruff handles both)
ruff check agentguard/ tests/
ruff format agentguard/ tests/

# Type checking
mypy agentguard/

# Tests with coverage
pytest tests/ -v --cov=agentguard --cov-report=term-missing
```

**Style notes:**
- Type hints on all public functions and methods
- Docstrings on all public classes and methods
- No line over 100 characters
- No bare `except:` — always catch specific exception types
- All new code must have tests — aim for 80%+ coverage on new modules

---

## Reporting Security Vulnerabilities

If you find a security vulnerability in AgentGuard itself
(not in agent architectures it analyzes), please do **not** open a
public GitHub issue.

Email: security@[yourdomain].com

Include:
- Description of the vulnerability
- Steps to reproduce
- Impact assessment
- Any suggested remediation

We will acknowledge within 48 hours and aim to patch within 14 days.

---

## Code of Conduct

AgentGuard follows the [Contributor Covenant](https://www.contributor-covenant.org/)
Code of Conduct. Be direct, be specific, be respectful.

Contributions that add threats to normalize harmful AI use, circumvent
safety controls without legitimate research purpose, or that are
designed to help attackers rather than defenders will be declined.

---

## Recognition

Contributors who add new threats to the taxonomy are credited in:
- The release notes for the version their contribution ships in
- The threat entry itself (optional — we can attribute to your GitHub
  handle, your organization, or leave anonymous per your preference)
- The `CONTRIBUTORS.md` file in the root of the repository

---

## Questions

Open a GitHub Discussion for questions about contributing, architecture
decisions, or threat modeling methodology. Issues are for bugs and
concrete feature requests. Discussions are for everything else.
