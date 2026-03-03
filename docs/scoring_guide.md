# AgentGuard Scoring Guide

How AgentGuard calculates threat risk scores — and why each dimension exists.

---

## The Formula

```
Final Score = (Exploitability × Impact × Autonomy_Factor
               × Blast_Radius × Reversibility)
              / Mitigations_Present

Normalized to 0.0–10.0
```

This is not CVSS. It was designed from scratch for agentic AI systems.
Here is why each dimension is here and what drives each value.

---

## Dimension 1: Exploitability (0.0–1.0)

*How easily can an attacker trigger this threat against this specific agent?*

CVSS conflates exploitability with prerequisites. AgentGuard separates
them because an agent's configuration — its tools, its inputs, its
external access — dramatically changes how exploitable each threat is.

| Value Range | Meaning |
|-------------|---------|
| 0.1–0.3 | Requires specialized access or significant attacker capability |
| 0.4–0.6 | Exploitable by a moderately skilled attacker with normal access |
| 0.7–0.9 | Trivially exploitable — any user, normal interaction |

**What raises exploitability for a given agent:**
- Agent accepts untrusted external content (web, emails, documents)
- Agent has no input validation or sanitization
- Attack vector is in the agent's normal operational path
- Agent has been deployed without adversarial testing

**Example:** PI-002 (Indirect Prompt Injection via web search) has base
exploitability 0.80 because an agent that searches the web as part of
normal operation is naturally exposed to attacker-controlled content.
No special access required.

---

## Dimension 2: Impact (0.0–1.0)

*If this threat is exploited, how severe is the worst credible outcome?*

Impact is assessed against the agent's specific configuration —
the data it handles, the tools it has, and what the downstream
consequences of exploitation would be.

| Value Range | Meaning |
|-------------|---------|
| 0.1–0.3 | Information disclosure, minor behavioral change, easily corrected |
| 0.4–0.6 | Significant data exposure or material operational disruption |
| 0.7–0.9 | PII exfiltration, unauthorized write operations, regulatory impact |
| 0.9–1.0 | Catastrophic data breach, financial fraud, compliance violation |

**What raises impact for a given agent:**
- Agent handles PII or confidential data
- Agent has write access to persistent systems
- Agent can initiate external communications (email, API calls)
- Agent's actions are difficult to reverse
- Regulatory scope (GDPR, HIPAA, SOX) applies

---

## Dimension 3: Autonomy Factor (1.0–3.0)

*The most important innovation in AgentGuard's scoring model.*

The same vulnerability is not equally dangerous at all autonomy levels.
An agent that requires human approval before every action is fundamentally
different from one that autonomously executes 50-step plans.

This multiplier exists because standard frameworks have no concept of
autonomous action — they were designed for systems where a human is
in the execution loop.

| Autonomy Level | Multiplier | Description |
|---------------|------------|-------------|
| 1 | 1.0× | Every action requires explicit human approval |
| 2 | 1.3× | Batch approval — human reviews before execution |
| 3 | 1.7× | Human-in-loop at key checkpoints only |
| 4 | 2.2× | Mostly autonomous, human can interrupt |
| 5 | 3.0× | Fully autonomous — human only reviews outcomes |

**Why the multiplier grows non-linearly:**
The relationship between autonomy and risk is not linear because autonomous
agents can chain actions. At autonomy level 5, a single injected instruction
can trigger a 50-step plan before any human observes the behavior. The
window for harm is orders of magnitude larger than at autonomy level 1.

**Example:** PI-002 scored against a customer service agent at autonomy
level 3 (no human checkpoint between web search and CRM write):
Autonomy Factor = 1.7. The same threat against a human-in-loop agent
that requires approval before each tool call: 1.0. Same vulnerability,
meaningfully different risk.

---

## Dimension 4: Blast Radius (1.0–2.0)

*How many systems, users, or data records can be affected if this threat fires?*

CVSS scope has a binary "changed/unchanged" flag. For agents, blast radius
is a continuous function of how many tools the agent has, how much data
it can access, and how many downstream systems it touches.

| Value | Meaning |
|-------|---------|
| 1.0 | Isolated impact — affects current session only |
| 1.2 | Affects one external system (one DB, one API) |
| 1.4 | Affects multiple systems or data stores |
| 1.6 | Affects all users of the agent or multiple backend systems |
| 1.8 | Cross-organization impact or pipeline-wide compromise |
| 2.0 | Systemic — affects all downstream users, multiple systems at scale |

**What drives blast radius:**
- Number of tools: more tools = larger potential blast radius
- Write tool presence: read-only tools limit blast radius
- External communication tools: email/webhook = unlimited external reach
- Multi-agent deployment: pipeline blast radius multiplies
- Shared memory: poisoning affects all users, not just the attacker

---

## Dimension 5: Reversibility (1.0–1.5)

*Can the effects of exploitation be fully undone?*

This dimension exists because agentic systems can take irreversible
actions at machine speed. A human clicking "delete" is one action.
An agent executing a cleanup routine can delete 10,000 records before
a human notices.

| Value | Meaning |
|-------|---------|
| 1.0 | Fully reversible — undo or rollback is complete and fast |
| 1.2 | Partially reversible — recovery requires effort or time |
| 1.3 | Difficult to reverse — some permanent effects likely |
| 1.5 | Irreversible — data loss, external communications, regulatory events |

**Irreversibility drivers:**
- External email sent: cannot be unsent
- Production database modified: rollback may be incomplete
- External API called: side effects in third-party systems
- PII exfiltrated: cannot be "unexfiltrated"
- Regulatory notification triggered: breach disclosed, cannot be undone

---

## Dimension 6: Mitigations Present (1.0–2.0)

*The denominator — how much does the agent's current defense posture reduce the risk?*

A higher mitigations score reduces the final risk score. This is the
dimension you control by implementing defenses.

| Value | Meaning |
|-------|---------|
| 1.0 | No applicable mitigations present |
| 1.2 | Partial mitigations — one relevant control in place |
| 1.5 | Meaningful mitigations — multiple relevant controls |
| 2.0 | Strong mitigations — comprehensive controls aligned to this threat |

**Mitigation credit is granted for:**
- Input sanitization / validation layer
- Output filtering
- Tool permission restrictions (allowlist)
- Rate limiting on sensitive operations
- Human-in-loop checkpoints for high-impact actions
- Memory isolation (per-user namespacing)
- Dependency integrity verification
- Behavioral monitoring / anomaly detection

**Important:** Mitigations claimed in the agent definition are taken at
face value by AgentGuard. Verification that controls are actually
implemented is a separate process — security testing and code review.
AgentGuard models what you say is in place, not what is verified.

---

## Risk Level Thresholds

After normalization to 0.0–10.0:

| Score Range | Risk Level | Default Action |
|-------------|------------|---------------|
| 8.5–10.0 | 🔴 Critical | Block deployment — remediate before release |
| 6.5–8.4 | 🟠 High | Remediate in current sprint — do not defer |
| 4.0–6.4 | 🟡 Medium | Plan remediation — next cycle with monitoring |
| 0.0–3.9 | 🟢 Low | Accept with documentation — add to monitoring |

---

## A Worked Example

**Agent:** Customer service agent, autonomy level 3, no human checkpoint,
tools: [web_search, crm_lookup (read PII), crm_update (write), email_sender]

**Threat:** PI-002 — Indirect Prompt Injection via Retrieved Content

```
Exploitability:      0.80  (agent routinely retrieves untrusted web content)
Impact:              0.90  (PII in scope + write tools + external email)
Autonomy Factor:     1.70  (autonomy level 3, no human checkpoint)
Blast Radius:        1.60  (4 tools including 2 with write/external access)
Reversibility:       1.30  (CRM writes partially reversible; email irreversible)
Mitigations:         1.20  (partial — email domain allowlist in place)

Raw Score:
  0.80 × 0.90 × 1.70 × 1.60 × 1.30 / 1.20
= 0.72 × 1.70 × 1.60 × 1.30 / 1.20
= 1.224 × 1.60 × 1.30 / 1.20
= 1.9584 × 1.30 / 1.20
= 2.5459 / 1.20
= 2.12

Normalized (÷ max theoretical × 10):
  Final Score: 9.2 / 10  →  CRITICAL
```

**If you add a human checkpoint before email_sender fires:**
Autonomy Factor drops from 1.70 to 1.30 (checkpoint at key action).
Final score drops to approximately **7.1 / 10 → HIGH**.
The control is measurable, the reduction is concrete.

---

## Applicability Logic

Not every threat applies to every agent. AgentGuard checks each threat's
`requires_*` conditions against the agent's configuration before scoring:

| Condition | Checked Against |
|-----------|----------------|
| `requires_memory` | `agent.memory.vector_store or agent.memory.persistent` |
| `requires_multi_agent` | `agent.multi_agent == true` |
| `requires_pii_input` | `agent.data_classification.input in [pii, sensitive, phi]` |
| `requires_external_tools` | Any tool with `external_access: true` |
| `requires_write_tools` | Any tool with `write_access: true` |

Threats that fail applicability checks are scored 0 and marked
`applicable: false` in the report. This prevents false positives
that would inflate risk scores for agents that simply don't have
the configuration the threat requires.

---

## CI/CD Integration

Use the `--fail-on` flag to enforce quality gates:

```bash
# Block deployment on any critical finding
agentguard analyze my_agent.yaml --fail-on critical

# Block on critical or high
agentguard analyze my_agent.yaml --fail-on critical,high

# Exit code 0 = passed, 1 = threshold breached
```

This is designed to slot directly into your CI/CD pipeline's
deployment gate checks.
