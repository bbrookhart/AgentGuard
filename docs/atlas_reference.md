# MITRE ATLAS Integration Guide

How AgentGuard maps its 47-threat taxonomy to MITRE ATLAS — and how
to use those mappings in your security program.

---

## What Is MITRE ATLAS?

MITRE ATLAS (Adversarial Threat Landscape for Artificial-Intelligence
Systems) is the authoritative knowledge base for adversarial attacks
against AI/ML systems. Think of it as MITRE ATT&CK, rebuilt from the
ground up for machine learning.

Where ATT&CK catalogs tactics and techniques against traditional IT
infrastructure, ATLAS catalogs how adversaries attack the AI/ML
components specifically — the models, training pipelines, inference
systems, and now agentic architectures.

**Key difference from ATT&CK:**
ATT&CK assumes deterministic systems. ATLAS accounts for probabilistic,
learned behavior — systems where the "vulnerability" is not a code bug
but a property of how the model generalizes from training data.

Reference: https://atlas.mitre.org/

---

## ATLAS Structure

```
Tactics  →  Techniques  →  Sub-Techniques
  │              │                │
  │         "What" the       Specific variant
  │         adversary        of the technique
  │         does
  │
"Why" / phase
of the attack
```

### ATLAS Tactics (the 9 relevant to agentic systems)

| Tactic ID | Name | Relevance to Agents |
|-----------|------|-------------------|
| AML.TA000 | ML Attack Staging | Crafting prompts, adversarial inputs |
| AML.TA002 | ML Supply Chain Compromise | Model tampering, plugin poisoning |
| AML.TA0003 | Persistence | Backdoors, memory poisoning |
| AML.TA0005 | Defense Evasion | Jailbreaks, guardrail bypass |
| AML.TA0007 | Execution | Tool misuse, agent action execution |
| AML.TA0009 | Impact | Excessive agency, irreversible actions |
| AML.TA006 | Exfiltration | PII leakage, system prompt extraction |
| AML.TA004 | Collection | Data aggregation via agent tools |
| AML.TA008 | Resource Development | Attacker infrastructure for injections |

---

## AgentGuard → ATLAS Technique Mapping

### AML.T0051 — Prompt Injection

The foundational agentic attack technique. An adversary crafts malicious
inputs to alter the model's behavior — overriding instructions, bypassing
guardrails, causing unauthorized actions.

**AgentGuard threats mapped here:**

| Threat ID | Name | Notes |
|-----------|------|-------|
| PI-001 | Direct System Prompt Override | Classic T0051 — user input overrides system |
| PI-003 | Multi-Turn Context Manipulation | Injection spread across conversation turns |
| PI-006 | Persona Injection | Role-based guardrail bypass variant |
| PI-007 | Jailbreak via Encoding | Obfuscation to evade content filters |
| PI-008 | Multi-Agent Prompt Propagation | T0051 in an inter-agent context |
| PE-002 | Role Confusion via Prompt Engineering | Privilege escalation via identity claim |
| PE-004 | Permission Boundary Violation via Context | Auth bypass via conversation assertion |
| MAC-001 | Orchestrator Trust Collapse | T0051 with pipeline-wide blast radius |
| MAC-002 | Agent Impersonation | T0051 variant — attacker poses as trusted agent |

**Why this matters for agents:**
Standard prompt injection assumes the attack arrives through the user
turn. In agentic systems, the injection surface extends to every piece
of external content the agent reads: web pages, documents, emails,
API responses, tool outputs. The attack surface scales with the agent's
tools.

---

### AML.T0051.001 — Indirect Prompt Injection

The sub-technique that defines modern agentic attacks. Adversarial
instructions embedded in external content retrieved during normal operation.

**AgentGuard threats mapped here:**

| Threat ID | Name | Notes |
|-----------|------|-------|
| PI-002 | Indirect Injection via Retrieved Content | Canonical T0051.001 — web/doc injection |
| PI-004 | RAG Knowledge Base Poisoning | T0051.001 at ingestion time vs. retrieval |

**Why this is scored more severely than T0051:**
Direct prompt injection requires the attacker to have user-level access
to the agent. Indirect injection requires only that the agent retrieve
content from a source the attacker can write to — a web page, a document
in a shared folder, an email. The attacker does not need to interact with
the agent at all.

---

### AML.T0048 — Excessive Agency Exploitation

Exploiting an agent's tool permissions or autonomous capabilities to
perform actions beyond intended scope.

**AgentGuard threats mapped here:**

| Threat ID | Name | Notes |
|-----------|------|-------|
| TM-001 | Unauthorized Tool Invocation | Direct T0048 — tool called outside authorization |
| TM-002 | SSRF via HTTP Client Tool | T0048 exploiting network-reaching tool |
| TM-003 | Excessive Permissions / Blast Radius | T0048 from over-provisioned tool set |
| TM-005 | Rate Limit Bypass via Agent Loop | Autonomous loop exhausts rate controls |
| TM-006 | Unauthorized Data Store Write | Write tool invoked outside authorization |
| PE-001 | Tool Chain Privilege Escalation | T0048 through chained authorized calls |
| PE-003 | Indirect Escalation via Orchestration | T0048 proxied through trust hierarchy |
| PE-005 | Scope Creep via Autonomous Goal Pursuit | T0048 from misaligned goal specification |
| MAC-005 | Shared State Race Condition | T0048 exploiting concurrent tool access |

**The tool chain insight:**
T0048 is the technique that most distinguishes agentic risk from
traditional application risk. A traditional app has a defined API —
a limited set of actions it can take. An agent with 10 tools has
10! possible action sequences. The authorization challenge isn't
"can this tool be called?" but "can this tool be called in this
sequence following this data retrieval?"

---

### AML.T0020 — Poison Training Data

Introducing malicious data into the AI system's knowledge base or
training pipeline.

**AgentGuard threats mapped here:**

| Threat ID | Name | Notes |
|-----------|------|-------|
| PI-004 | RAG Knowledge Base Poisoning | T0020 at RAG ingestion time |
| MA-001 | Session Memory Poisoning | T0020 limited to session scope |
| MA-002 | Persistent Vector Store Poisoning | T0020 with cross-session persistence |
| MA-003 | Cross-User Memory Contamination | T0020 with cross-user blast radius |
| MA-005 | Long-Term Behavioral Drift | T0020 via incremental injection |
| MAC-003 | Cascading Context Poisoning | T0020 propagating through agent pipeline |
| SC-003 | Malicious RAG Data Source | T0020 via compromised upstream data source |

**Agentic extension of T0020:**
In traditional ML, T0020 requires access to the training pipeline —
a high-bar attack requiring significant technical access. In RAG-augmented
agents, the "training data" is the knowledge base, and insertion may
require only document upload privileges or the ability to create a
web page the agent will retrieve.

---

### AML.T0056 — LLM Prompt/Output Extraction

Crafting prompts to extract the AI system's internal configuration,
system prompt, or sensitive operational details.

**AgentGuard threats mapped here:**

| Threat ID | Name | Notes |
|-----------|------|-------|
| PI-005 | System Prompt Extraction | Canonical T0056 |
| TM-007 | Cross-Tool Data Leakage | T0056 via tool chain data flow |
| MA-006 | Memory Exfiltration via Side Channel | T0056 targeting memory contents |
| DE-001 | PII Exfiltration via Tool Chain | T0056 at scale via tool execution |
| DE-002 | System Prompt Extraction | Same as PI-005, different domain framing |
| DE-003 | Conversation History Exfiltration | T0056 against cross-session history |
| DE-004 | Covert Channel via Encoded Output | T0056 via steganographic encoding |
| DE-005 | Training Data Reconstruction | T0056 targeting memorized training data |
| MAC-006 | Sub-Agent Capability Probing | T0056 to enumerate pipeline architecture |

---

### AML.T0043 — Craft Adversarial Data

Creating inputs specifically designed to cause the AI model to produce
incorrect or unexpected outputs.

**AgentGuard threats mapped here:**

| Threat ID | Name | Notes |
|-----------|------|-------|
| MA-004 | Embedding Space Adversarial Attack | T0043 in vector space |
| GM-001 | Specification Gaming | T0043 via objective exploitation |
| GM-002 | Reward Hacking via Proxy Metric | T0043 via metric manipulation |
| MAC-004 | Feedback Loop Amplification | T0043 amplified through refinement loops |
| DE-006 | Side-Channel Timing Attack | T0043 via observable timing patterns |

---

### AML.T0015 — Evade ML Model

Crafting inputs to evade the AI system's safety and content filtering
mechanisms.

**AgentGuard threats mapped here:**

| Threat ID | Name | Notes |
|-----------|------|-------|
| PI-006 | Persona Injection | Role-based guardrail bypass |
| PI-007 | Jailbreak via Encoding / Obfuscation | Encoding to evade content filters |
| GM-003 | Goal Drift via Multi-Turn Manipulation | Gradual evasion via context shift |
| GM-004 | Distributional Shift Exploitation | Out-of-distribution input evasion |

---

### AML.T0010 — ML Supply Chain Compromise

Compromising a component of the AI/ML supply chain to introduce
malicious behavior into downstream systems.

**AgentGuard threats mapped here:**

| Threat ID | Name | Notes |
|-----------|------|-------|
| SC-001 | Poisoned Plugin or Tool Dependency | T0010 via package registry |
| SC-004 | Infrastructure API Interception | T0010 via network interception |
| MAC-007 | Byzantine Agent via Model Substitution | T0010 targeting sub-agent integrity |

---

### AML.T0018 — Backdoor ML Model

Inserting a hidden backdoor into a model during training or fine-tuning
that activates on specific trigger inputs.

**AgentGuard threats mapped here:**

| Threat ID | Name | Notes |
|-----------|------|-------|
| SC-002 | Compromised Model Weights | Canonical T0018 |

---

### AML.T0054 — LLM Plugin Compromise

Compromising or creating a malicious plugin/tool for an LLM-based system.

**AgentGuard threats mapped here:**

| Threat ID | Name | Notes |
|-----------|------|-------|
| TM-004 | Tool Output Injection | T0054 — malicious tool response |

---

## Using ATLAS Mappings in Your Security Program

### Threat Intelligence Integration

ATLAS technique IDs in AgentGuard reports can be used to:

1. **Cross-reference ATLAS case studies** — ATLAS publishes real-world
   incident cases organized by technique. When AgentGuard flags
   AML.T0051.001, look up the ATLAS case studies for that technique
   to see how it has been exploited in production systems.
   https://atlas.mitre.org/studies/

2. **Map to ATT&CK for Enterprise** — ATLAS provides explicit mappings
   between ATLAS techniques and ATT&CK for Enterprise techniques where
   overlap exists. If your SOC operates on ATT&CK, use these mappings
   to integrate AI-specific findings into existing detection workflows.

3. **Feed into threat intel platforms** — ATLAS technique IDs are stable
   identifiers that can be imported into MITRE Navigator, threat intel
   platforms (MISP, OpenCTI), and SIEM correlation rules.

### Generating ATLAS Navigator Layers

AgentGuard's JSON report output can be transformed into a MITRE ATLAS
Navigator layer to visualize your agent's threat coverage:

```python
import json

# Load AgentGuard JSON report
with open("report.json") as f:
    report = json.load(f)

# Extract ATLAS technique IDs from findings
techniques = []
for finding in report["findings"]:
    if atlas_id := finding.get("atlas_technique"):
        level = finding["risk_level"]
        color = {
            "critical": "#dc2626",
            "high":     "#ea580c",
            "medium":   "#ca8a04",
            "low":      "#16a34a",
        }.get(level, "#94a3b8")
        techniques.append({
            "techniqueID": atlas_id,
            "color": color,
            "comment": f"{finding['name']} — Score: {finding['final_score']}/10",
            "enabled": True,
        })

# Build Navigator layer
layer = {
    "name": f"AgentGuard: {report['meta']['agent_name']}",
    "version": "4.4",
    "domain": "ATLAS",
    "techniques": techniques,
}

with open("navigator_layer.json", "w") as f:
    json.dump(layer, f, indent=2)
```

Upload the resulting JSON to https://mitre-atlas.github.io/atlas-navigator/

### Mapping to Security Controls

Use ATLAS technique IDs to look up ATLAS mitigations — structured
countermeasures published alongside the technique catalog:

```
AML.T0051 → AML.M0015 (Adversarial Input Detection)
AML.T0051 → AML.M0016 (Limit Model Artifact Release)
AML.T0020 → AML.M0007 (Sanitize Training Data)
AML.T0048 → AML.M0047 (AI-Specific Access Controls)
```

ATLAS mitigations provide vendor-neutral control specifications that
can be used to write security requirements for your AI development teams.

---

## Staying Current with ATLAS

ATLAS is actively maintained and updated as new attack research emerges.

- **Subscribe to ATLAS updates:** https://atlas.mitre.org/updates/
- **Contribute case studies:** If your organization discovers a novel
  attack against an AI system, ATLAS accepts community contributions
  of anonymized case studies.
- **ATLAS versioning:** AgentGuard's `atlas_mappings.yaml` documents
  the ATLAS version it was built against. When ATLAS releases new
  techniques, update `atlas_mappings.yaml` and re-run your analyses.

AgentGuard's taxonomy will be updated with each major ATLAS release.
Watch the AgentGuard releases page for updates.
