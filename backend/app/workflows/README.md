# backend/app/workflows/

LangGraph orchestration: the shared review state, deterministic intake and file classification, conditional routing to agent nodes, and the risk synthesis step.

Routing must be **deterministic first**. For example, a changed dependency manifest triggers the Dependency agent, without asking an LLM to decide.

**Primary owners:** Sarthak + Alex

> **TODO (Sprint 1, Sarthak + Alex: "Implement Initial LangGraph Agent Orchestration"):** shared state, classification, conditional routing, mock Dependency/CI/CD/Release nodes, synthesis and tests. Coordinate agent node interfaces with Rohit + Ronn (`app/agents/`).
