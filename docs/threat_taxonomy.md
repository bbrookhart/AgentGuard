# AgentGuard Threat Taxonomy Reference

Complete reference for all 47 threats across 8 domains.
Each entry includes threat ID, severity, ATLAS mapping, and key scoring parameters.

---

## Domain 1: Prompt Injection (PI) — 8 Threats

Threats that exploit the model's inability to distinguish trusted instructions
from untrusted input when both are delivered through natural language.

| ID | Name | Severity | ATLAS | Key Risk Factors |
|----|------|----------|-------|-----------------|
| PI-001 | Direct System Prompt Override | high | AML.T0051 | Autonomy multiplier, no human checkpoint |
| PI-002 | Indirect Injection via Retrieved Content | critical | AML.T0051.001 | External content, write tools, blast radius |
| PI-003 | Multi-Turn Context Manipulation | high | AML.T0051 | Persistent memory, session length |
| PI-004 | RAG Knowledge Base Poisoning | critical | AML.T0020 | Vector store write access |
| PI-005 | System Prompt Extraction | high | AML.T0056 | Confidentiality of config |
| PI-006 | Persona Injection | medium | AML.T0015 | Guardrail bypass |
| PI-007 | Jailbreak via Encoding / Obfuscation | medium | AML.T0015 | Safety filter evasion |
| PI-008 | Multi-Agent Prompt Propagation | high | AML.T0051 | Multi-agent trust chain |

---

## Domain 2: Tool Misuse (TM) — 7 Threats

Threats arising from agent tools being invoked in unauthorized, unintended,
or chained ways that exceed the scope of their individual authorizations.

| ID | Name | Severity | ATLAS | Key Risk Factors |
|----|------|----------|-------|-----------------|
| TM-001 | Unauthorized Tool Invocation | high | AML.T0048 | Autonomy level, tool permissions |
| TM-002 | SSRF via HTTP Client Tool | high | AML.T0048 | External access, internal network reach |
| TM-003 | Excessive Permissions (Blast Radius) | critical | AML.T0048 | Write tools + PII + external access |
| TM-004 | Tool Output Injection | high | AML.T0054 | Untrusted tool response, reasoning context |
| TM-005 | Rate Limit Bypass via Agent Loop | medium | AML.T0048 | Autonomous looping, no throttle |
| TM-006 | Unauthorized Data Store Write | high | AML.T0048 | Write access, data integrity |
| TM-007 | Cross-Tool Data Leakage | high | AML.T0056 | PII read + external write in same session |

---

## Domain 3: Memory Attacks (MA) — 6 Threats

Threats that target the agent's persistent or session memory systems,
including vector stores, context windows, and shared state.

| ID | Name | Severity | ATLAS | Key Risk Factors |
|----|------|----------|-------|-----------------|
| MA-001 | Session Memory Poisoning | high | AML.T0020 | Persistent memory, write via conversation |
| MA-002 | Persistent Vector Store Poisoning | critical | AML.T0020 | Vector store, document upload access |
| MA-003 | Cross-User Memory Contamination | high | AML.T0020 | Shared memory, multi-tenant |
| MA-004 | Embedding Space Adversarial Attack | medium | AML.T0043 | Vector store, retrieval manipulation |
| MA-005 | Long-Term Behavioral Drift via Memory | medium | AML.T0020 | Persistent memory, incremental injection |
| MA-006 | Memory Exfiltration via Side Channel | high | AML.T0056 | PII in memory, retrieval without auth |

---

## Domain 4: Privilege Escalation (PE) — 5 Threats

Threats that result in the agent operating with greater permissions, scope,
or capability than was originally authorized.

| ID | Name | Severity | ATLAS | Key Risk Factors |
|----|------|----------|-------|-----------------|
| PE-001 | Tool Chain Privilege Escalation | critical | AML.T0048 | Multiple tools, no chain validation |
| PE-002 | Role Confusion via Prompt Engineering | high | AML.T0051 | No technical auth enforcement |
| PE-003 | Indirect Escalation via Agent Orchestration | high | AML.T0048 | Multi-agent, low-priv→high-priv path |
| PE-004 | Permission Boundary Violation via Context | medium | AML.T0051 | Session context as auth source |
| PE-005 | Scope Creep via Autonomous Goal Pursuit | medium | AML.T0048 | High autonomy, broad goal specification |

---

## Domain 5: Goal Misgeneralization (GM) — 4 Threats

Threats arising from the agent pursuing its specified objective in ways
that satisfy the metric while violating the intended outcome.

| ID | Name | Severity | ATLAS | Key Risk Factors |
|----|------|----------|-------|-----------------|
| GM-001 | Specification Gaming | high | AML.T0043 | Poorly constrained objectives |
| GM-002 | Reward Hacking via Proxy Metric | high | AML.T0043 | Metric-only evaluation |
| GM-003 | Goal Drift via Multi-Turn Manipulation | medium | AML.T0051 | Long sessions, no goal anchoring |
| GM-004 | Distributional Shift Exploitation | medium | AML.T0015 | Out-of-distribution inputs, no escalation |

---

## Domain 6: Data Exfiltration (DE) — 6 Threats

Threats that result in sensitive data leaving authorized boundaries through
the agent's tool capabilities or natural language outputs.

| ID | Name | Severity | ATLAS | Key Risk Factors |
|----|------|----------|-------|-----------------|
| DE-001 | PII Exfiltration via Tool Chain | critical | AML.T0056 | PII input, external write tool |
| DE-002 | System Prompt Extraction | high | AML.T0056 | Config confidentiality |
| DE-003 | Conversation History Exfiltration | high | AML.T0056 | Shared memory, multi-user |
| DE-004 | Covert Channel via Encoded Output | medium | AML.T0056 | No output normalization |
| DE-005 | Training Data Reconstruction | medium | AML.T0056 | Fine-tuned on sensitive data |
| DE-006 | Side-Channel Timing Attack | low | AML.T0043 | Response timing inference |

---

## Domain 7: Multi-Agent Collapse (MAC) — 7 Threats

Threats unique to multi-agent architectures where trust relationships,
shared state, and inter-agent communication create compound attack surfaces.

| ID | Name | Severity | ATLAS | Key Risk Factors |
|----|------|----------|-------|-----------------|
| MAC-001 | Orchestrator Trust Collapse | critical | AML.T0051 | No inter-agent auth, compound blast radius |
| MAC-002 | Agent Impersonation | high | AML.T0051 | No message signing, natural lang comms |
| MAC-003 | Cascading Context Poisoning | high | AML.T0020 | Pipeline propagation, no trust reduction |
| MAC-004 | Feedback Loop Amplification | medium | AML.T0043 | Refinement loops, no convergence check |
| MAC-005 | Shared State Race Condition | medium | AML.T0048 | Concurrent writes, no locking |
| MAC-006 | Sub-Agent Capability Probing | medium | AML.T0056 | Architecture enumeration |
| MAC-007 | Byzantine Agent via Model Substitution | high | AML.T0010 | No model integrity verification |

---

## Domain 8: Supply Chain (SC) — 4 Threats

Threats arising from the compromise of components used to build, deploy,
or operate the AI agent — including models, plugins, and data sources.

| ID | Name | Severity | ATLAS | Key Risk Factors |
|----|------|----------|-------|-----------------|
| SC-001 | Poisoned Plugin or Tool Dependency | critical | AML.T0010 | No dependency integrity checking |
| SC-002 | Compromised Model Weights | critical | AML.T0018 | No model provenance verification |
| SC-003 | Malicious RAG Data Source Injection | high | AML.T0020 | External data source, no ingestion validation |
| SC-004 | Infrastructure-Level API Interception | high | AML.T0010 | No TLS pinning, MITM exposure |

---

## Severity Distribution

| Level | Count | % of Taxonomy |
|-------|-------|--------------|
| Critical | 10 | 21% |
| High | 24 | 51% |
| Medium | 11 | 23% |
| Low | 2 | 4% |

---

## ATLAS Technique Coverage

| ATLAS ID | Name | Threats Mapped |
|----------|------|---------------|
| AML.T0051 | Prompt Injection | PI-001, PI-003, PI-006, PE-002, PE-004, MAC-001, MAC-002 |
| AML.T0051.001 | Indirect Prompt Injection | PI-002 |
| AML.T0048 | Excessive Agency | TM-001, TM-002, TM-003, TM-005, TM-006, PE-001, PE-003, PE-005, MAC-005 |
| AML.T0020 | Poison Training Data | PI-004, MA-001, MA-002, MA-003, MA-005, MAC-003, SC-003 |
| AML.T0056 | LLM Output Extraction | PI-005, TM-007, MA-006, DE-001, DE-002, DE-003, DE-004, DE-005, MAC-006 |
| AML.T0043 | Craft Adversarial Data | MA-004, GM-001, GM-002, MAC-004, DE-006 |
| AML.T0015 | Evade ML Model | PI-006, PI-007, GM-003, GM-004 |
| AML.T0010 | ML Supply Chain | SC-001, SC-004, MAC-007 |
| AML.T0018 | Backdoor ML Model | SC-002 |
| AML.T0054 | LLM Plugin Compromise | TM-004 |
