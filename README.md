# AgentGuard

**Runtime Authority Enforcement for Agentic AI Systems**

> *"Agentic AI will not become safe through monitoring. It becomes safe when unauthorized action cannot execute."*

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-0a0a0a?style=for-the-badge&logo=python&logoColor=00f5ff)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-0a0a0a?style=for-the-badge&logo=fastapi&logoColor=00f5ff)
![OPA](https://img.shields.io/badge/Open_Policy_Agent-0.58+-0a0a0a?style=for-the-badge&logoColor=00f5ff)
![License](https://img.shields.io/badge/License-MIT-0a0a0a?style=for-the-badge&logoColor=00f5ff)

**A project by [AetherHorizon](https://github.com/AetherHorizon)**

</div>

---

## The Problem

Modern AI agents are wired to tools, memory stores, databases, APIs, and real-world infrastructure. When something goes wrong — and research shows it frequently does — the failure is almost never a language quality problem. It is an **authority boundary violation**.

An agent was allowed to:
- Execute a task outside its authorized scope *(Unauthorized Compliance)*
- Accumulate permissions beyond original intent *(Privilege Drift)*
- Use a legitimate tool for an unauthorized purpose *(Tool Misuse)*
- Report success without completing the task *(False Completion)*
- Pass malicious instructions to downstream agents *(Cross-Agent Propagation)*
- Cause irreversible damage to systems *(System-Level Damage)*

These failures are not solved by better prompts, more careful red-teaming, or improved monitoring dashboards. They happen because agents are **architecturally permitted to act without real-time authority enforcement**. Monitoring observes chaos after it happens. AgentGuard makes unauthorized action structurally impossible before it happens.

---

## What AgentGuard Does

AgentGuard is a **runtime middleware layer** that intercepts every tool call an AI agent attempts to execute and enforces a three-part authority check before allowing execution:

```
Agent → [Tool Call Attempt] → AgentGuard → [Authority Check] → Execute or Block
                                                ↓
                                    1. Authority:   Who authorized this?
                                    2. Scope:       Is this within task bounds?
                                    3. Admissibility: Is this valid right now?
```

Every check resolves against a **declarative policy** written in Rego (Open Policy Agent). If all three checks pass, execution proceeds. If any check fails, execution is **structurally blocked** and a rejection record is written to the immutable audit log with full causal context.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AGENT RUNTIME                        │
│  ┌──────────────┐    ┌─────────────────────────────────┐   │
│  │  LLM Agent   │───▶│      AgentGuard Middleware       │   │
│  │ (LangChain / │    │                                 │   │
│  │  AutoGen /   │    │  ┌───────────┐ ┌─────────────┐  │   │
│  │  Custom)     │    │  │  Policy   │ │  Authority  │  │   │
│  └──────────────┘    │  │  Engine   │ │   Resolver  │  │   │
│                      │  │  (OPA)    │ │             │  │   │
│                      │  └─────┬─────┘ └──────┬──────┘  │   │
│                      │        │              │          │   │
│                      │  ┌─────▼──────────────▼──────┐  │   │
│                      │  │    Enforcement Decision    │  │   │
│                      │  │    ALLOW │ BLOCK │ PAUSE   │  │   │
│                      │  └─────────────────┬──────────┘  │   │
│                      └────────────────────│─────────────┘   │
│                                           │                 │
│  ┌───────────────────────────────────────▼──────────────┐  │
│  │              Immutable Audit Log (Hash-Chained)       │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                                       │
    ┌────▼────┐                           ┌──────▼──────┐
    │  Tool   │                           │  Dashboard  │
    │  Suite  │                           │  (FastAPI + │
    │         │                           │   HTML/JS)  │
    └─────────┘                           └─────────────┘
```

### Core Components

| Component | Location | Responsibility |
|-----------|----------|----------------|
| `PolicyEngine` | `src/core/policy_engine.py` | Loads and evaluates Rego policies via OPA |
| `AuthorityResolver` | `src/core/authority_resolver.py` | Validates principal → action authorization chains |
| `EnforcementLayer` | `src/core/enforcement.py` | Orchestrates checks and renders ALLOW/BLOCK/PAUSE decisions |
| `AuditLogger` | `src/audit/audit_logger.py` | Append-only, hash-chained audit trail |
| `ToolRegistry` | `src/tools/tool_registry.py` | Registers tools with their scope definitions |
| `AgentGuardAPI` | `src/api/routes.py` | FastAPI REST interface for external integrations |
| `Dashboard` | `src/dashboard/` | Real-time enforcement monitoring UI |

---

## Security Model

### Execution-Bound Governance

AgentGuard implements what researchers call **execution-bound governance**: every action requires three resolved conditions at the moment of execution. This is distinct from policy-at-configuration-time approaches, where policies are set up once and then assumed to hold.

```
At execution time, for every tool call:
  authority_resolved    AND
  scope_valid           AND
  contextually_admissible
    → ALLOW

Otherwise:
    → BLOCK (structurally, before execution)
```

### Authority Chains

AgentGuard models authority as a directed chain from a **root principal** (human operator) through delegation layers to the executing agent. Each delegation step must be cryptographically verifiable. An agent cannot claim authority that was not explicitly granted in a traceable chain.

```
Human Operator
    └── grants → Orchestrator Agent (scope: customer-support)
                    └── grants → Sub-Agent A (scope: read-tickets)
                    └── grants → Sub-Agent B (scope: send-replies)
                                    └── BLOCKED: Sub-Agent B cannot delete tickets
                                                 (never in its authority chain)
```

### Policy-as-Code

All enforcement rules are written in **Rego**, the policy language of Open Policy Agent. This means:
- Policies are version-controlled alongside code
- Policy changes are auditable through git history
- Policies can be tested with `opa test` before deployment
- Policies are human-readable and reviewable by security teams

---

## Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# Open Policy Agent
curl -L -o opa https://openpolicyagent.org/downloads/latest/opa_linux_amd64
chmod +x opa && sudo mv opa /usr/local/bin/opa

# Verify
opa version
```

### Installation

```bash
git clone https://github.com/AetherHorizon/agentguard.git
cd agentguard

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Run the Demo

```bash
# Start AgentGuard with demo configuration
python -m src.main --config config/demo_policy.yaml

# In a separate terminal, run the attack simulation
python scripts/demo_attack_simulation.py

# Open the dashboard
open http://localhost:8000/dashboard
```

### Run the Test Suite

```bash
pytest tests/ -v --tb=short

# Run the adversarial red-team tests specifically
pytest tests/test_adversarial.py -v
```

---

## Usage

### Protecting a LangChain Agent

```python
from agentguard import AgentGuard, PolicyConfig, Principal

# Define the policy
config = PolicyConfig.from_file("config/customer_support_policy.yaml")

# Define the principal (who is authorizing this agent session)
principal = Principal(
    id="operator-001",
    role="customer_support_supervisor",
    session_token="<signed-jwt>"
)

# Wrap your agent's tool suite
guard = AgentGuard(config=config, principal=principal)

# Register only the tools this agent is authorized to use
guard.register_tool("read_ticket",    scope="tickets:read")
guard.register_tool("send_reply",     scope="tickets:write")
guard.register_tool("escalate_ticket", scope="tickets:escalate")
# NOTE: delete_ticket is NOT registered — not in this agent's scope

# Execute with enforcement
result = guard.execute("read_ticket", ticket_id="TKT-12345")
# → ALLOWED: within scope, authority resolved, admissible

result = guard.execute("delete_user_account", user_id="USR-99")
# → BLOCKED: tool not in registry, scope violation logged to audit trail
```

### Defining a Policy

```yaml
# config/customer_support_policy.yaml
policy:
  name: customer-support-agent-v1
  version: "1.0.0"
  
  principals:
    - id: operator-001
      role: customer_support_supervisor
      max_delegation_depth: 2

  agents:
    - id: support-agent
      authorized_by: operator-001
      scope:
        - tickets:read
        - tickets:write
        - tickets:escalate
      forbidden:
        - user_accounts:*
        - billing:*
        - admin:*
      
  constraints:
    require_human_confirmation:
      - action: tickets:bulk_close
        threshold: "> 10 tickets"
      - action: tickets:escalate
        when: "severity == 'critical'"
    
    rate_limits:
      - scope: tickets:write
        max_per_minute: 30
    
    irreversible_actions:
      - tickets:delete
      - user_accounts:delete
    # Irreversible actions require explicit human confirmation
    # and a 60-second cooling-off period
```

---

## Attack Simulation Results

The `scripts/demo_attack_simulation.py` runs 12 adversarial scenarios against a configured AgentGuard instance. Below are results from the reference configuration:

| Attack Scenario | Without AgentGuard | With AgentGuard |
|----------------|-------------------|-----------------|
| Prompt injection via email content | ✅ Executed | 🛡️ Blocked at input sanitization |
| Privilege escalation via task chaining | ✅ Executed | 🛡️ Blocked — authority chain invalid |
| Tool misuse (search tool → data exfil) | ✅ Executed | 🛡️ Blocked — scope violation |
| Cross-agent trust exploitation | ✅ Propagated | 🛡️ Blocked — zero-trust inter-agent auth |
| False completion state injection | ✅ Accepted | 🛡️ Blocked — completion verification |
| Bulk irreversible action (mass delete) | ✅ Executed | 🛡️ Paused — human confirmation required |
| Rate limit bypass via task fragmentation | ✅ Executed | 🛡️ Blocked — aggregate rate enforcement |
| Scope creep through delegation | ✅ Executed | 🛡️ Blocked — delegation depth exceeded |
| TOCTOU permission race condition | ✅ Exploited | 🛡️ Blocked — atomic check-execute |
| Session token replay | ✅ Accepted | 🛡️ Blocked — token binding enforced |
| Memory poisoning via context injection | ✅ Accepted | 🛡️ Blocked — context integrity check |
| Cascading failure via false audit entry | ✅ Accepted | 🛡️ Blocked — hash chain broken, flagged |

**Block rate: 12/12 (100%) on reference attack suite**

---

## Threat Model

AgentGuard is designed to operate in environments where:
- The LLM itself may produce adversarial outputs (either through misalignment or prompt injection)
- External data sources are considered untrusted
- Agent-to-agent communication is not inherently trusted
- Operators may be subject to social engineering or coercion
- Adversaries have knowledge of the agent's tool suite

**AgentGuard does NOT protect against:**
- A compromised root principal who intentionally grants malicious authority
- Physical compromise of the host system
- Vulnerabilities in OPA itself
- Side-channel attacks on cryptographic operations

---

## Project Structure

```
agentguard/
├── src/
│   ├── main.py                      # Application entry point
│   ├── core/
│   │   ├── enforcement.py           # Central enforcement orchestrator
│   │   ├── policy_engine.py         # OPA policy evaluation
│   │   ├── authority_resolver.py    # Principal → action authority chains
│   │   └── models.py                # Core data models (Pydantic)
│   ├── audit/
│   │   └── audit_logger.py          # Hash-chained, append-only audit log
│   ├── tools/
│   │   └── tool_registry.py         # Tool registration and scope management
│   ├── api/
│   │   ├── routes.py                # FastAPI REST endpoints
│   │   └── middleware.py            # Request authentication middleware
│   └── dashboard/
│       ├── static/                  # Dashboard frontend assets
│       └── templates/               # Jinja2 HTML templates
├── policies/
│   ├── base_policy.rego             # Base Rego policy (OPA)
│   └── constraints.rego             # Constraint rules
├── config/
│   ├── demo_policy.yaml             # Demo configuration
│   └── production_template.yaml    # Production config template
├── tests/
│   ├── test_enforcement.py          # Core enforcement unit tests
│   ├── test_authority.py            # Authority chain tests
│   ├── test_audit.py                # Audit log integrity tests
│   └── test_adversarial.py         # Red-team adversarial scenarios
├── scripts/
│   └── demo_attack_simulation.py   # Interactive attack demo
├── docs/
│   ├── threat_model.md              # Full threat model documentation
│   ├── policy_language.md          # Policy authoring guide
│   └── architecture.md             # Deep-dive architecture docs
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Relation to Broader Agentic Security Research

AgentGuard implements concepts from several active research areas:

- **Capability-based security** — Authority is tied to unforgeable capability tokens, not ambient permissions
- **Zero-trust architecture** — No agent trusts another by default; every interaction requires verification
- **Byzantine fault tolerance** — The system is designed to function correctly even when individual agents are compromised
- **Policy-as-code** — All security rules are declarative, version-controlled, and auditable

This project is part of the **AetherHorizon** portfolio exploring the frontier of AI system security. Related projects:
- [PromptShield](https://github.com/AetherHorizon/promptshield) — Prompt injection detection and neutralization
- [AgentAudit](https://github.com/AetherHorizon/agentaudit) — Cryptographic integrity verification for agent audit trails
- [CrossAgentTrust](https://github.com/AetherHorizon/crossagenttrust) — Zero-trust inter-agent communication framework

---

## Contributing

AgentGuard is an open research project. Contributions, adversarial test cases, and policy examples are welcome. Please read `CONTRIBUTING.md` before submitting pull requests.

For security disclosures, use the GitHub Security Advisory feature. Do not open public issues for vulnerabilities.

---

## License

MIT License — see `LICENSE` for details.

---

<div align="center">

**AetherHorizon** · Securing the frontier of agentic AI

*Built for engineers who understand that safety is an architecture problem, not a prompt problem.*

</div>
