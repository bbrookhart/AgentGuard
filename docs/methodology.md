# AgentGuard Threat Modeling Methodology

## Overview

AgentGuard adapts the principles of established threat modeling frameworks
(STRIDE, PASTA, LINDDUN) for the unique characteristics of agentic AI systems.
This document explains the methodology and the reasoning behind design decisions.

## Why Standard Frameworks Fall Short

### STRIDE Limitations for Agents

STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation)
works by analyzing data flows between system components. For traditional software,
data flows are explicit and bounded. For agentic AI:

- **Goals change at runtime** based on context — there is no fixed data flow diagram
- **Prompt injection** has no STRIDE equivalent — it is not spoofing, tampering, or
  elevation in the classical sense, though it may involve all three
- **Emergent tool chains** create attack paths that don't exist in any static diagram
- **Multi-turn context** means a threat may only materialize after several interactions

### The Agentic Threat Surface

An agentic AI system has five primary attack surfaces that traditional frameworks
do not model:

1. **The Instruction Boundary** — The divide between trusted system instructions
   and untrusted user/external input. Unique to LLM systems.

2. **The Tool Execution Layer** — Each tool is a code execution interface. An agent
   with 5 tools has 5 potential execution contexts, each with their own attack surface.

3. **The Memory System** — Persistent memory creates a new attack vector: an attacker
   who can influence memory can plant instructions that persist across sessions.

4. **The Context Window** — Everything in the context window influences the model's
   behavior. External content retrieved into the context becomes part of the
   reasoning substrate.

5. **The Agent-to-Agent Channel** — In multi-agent systems, agents communicate
   with each other. A compromised orchestrator can corrupt all subordinate agents.

## The AgentGuard Scoring Model

### Why Not Just Use CVSS?

CVSS (Common Vulnerability Scoring System) is the industry standard for scoring
software vulnerabilities. It uses Base, Temporal, and Environmental metrics to
produce a 0–10 score.

AgentGuard extends CVSS with three agentic-specific dimensions:

| CVSS Dimension | AgentGuard Equivalent | Agentic Extension |
|---|---|---|
| Attack Vector | Exploitability | + Untrusted input surface size |
| Impact | Impact | + Data sensitivity modifier |
| Scope | Blast Radius | Explicit tool chain propagation |
| — | Autonomy Factor | NEW: How much does autonomy amplify? |
| — | Reversibility | NEW: Can agentic actions be undone? |
| Temporal | Detection Difficulty | Adapted for AI observability challenges |

### Autonomy Factor — The Key Agentic Dimension

The most important innovation in AgentGuard's scoring model is the **Autonomy Factor**.

In a supervised system (autonomy level 1), a human approves every significant action.
Even if an agent is successfully injected with malicious instructions, a human will
catch the issue before execution. The threat's effective risk is dramatically reduced.

In a fully autonomous system (autonomy level 5), there is no human checkpoint.
A successful prompt injection can execute a full kill chain — from initial compromise
to data exfiltration — without any human ever seeing it. The same underlying
vulnerability is orders of magnitude more dangerous.

The Autonomy Factor (1.0 to 3.0) captures this reality quantitatively.

## Threat Applicability

Not every threat in the taxonomy applies to every agent. AgentGuard checks
applicability before scoring:

- **Tool-dependent threats** are only scored if the relevant tool is present
- **Memory threats** are only scored if the agent has a non-null memory configuration
- **Multi-agent threats** are only scored for multi-agent architectures

This prevents false positives and keeps reports focused on actionable findings.

## Report Interpretation

### Reading Risk Scores

A risk score represents the combination of how likely a threat is to be exploited
AND how bad it would be if it were. A Critical 9.5 means both conditions are true:
the attack is easy to execute and the consequences are severe.

A High 7.0 might mean the attack is moderately difficult (but plausible) with
severe consequences, OR easy to execute with moderate consequences. The scoring
breakdown in the full report shows which dimensions are driving the score.

### Prioritization Guidance

In practice, you should prioritize remediation in this order:

1. **Critical + Easy to fix first** — Maximum risk reduction per hour of effort
2. **Critical + Hard to fix** — Requires architectural changes; start planning now
3. **High with write permissions** — Agents with write access amplify high findings
4. **Medium in high-autonomy agents** — Autonomy amplifies everything

## Limitations

AgentGuard is a static analysis tool. It models threats based on the architecture
definition you provide. It cannot:

- Detect runtime prompt injection in actual conversations
- Test whether your guardrails actually work
- Account for emergent behaviors not derivable from architecture alone
- Replace penetration testing or red teaming

Use AgentGuard for architecture review and security planning. Complement it with
dynamic testing using PromptShield or similar red team tooling.
