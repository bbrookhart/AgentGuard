# AgentGuard-A-Runtime-Authority-Enforcement-Layer
A middleware layer that sits between an LLM agent and its tool suite. Every tool call passes through AgentGuard, which checks it against a policy definition (YAML or JSON-based), verifies the authority chain, and either approves or blocks with a detailed rejection reason. 
