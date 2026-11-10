# backend/app/workflows/

LangGraph orchestration: the shared review state, deterministic intake and file classification, conditional routing to agent nodes, and the risk synthesis step.

Routing must be **deterministic first**. For example, a changed dependency manifest triggers the Dependency agent, without asking an LLM to decide.

**Primary owners:** Neel + Alex (#1)

> **TODO (Sprint 1, Neel + Alex, #1: "Implement Initial LangGraph Agent Orchestration"):** shared state, classification, conditional routing, mock Dependency/CI/CD/Release nodes, synthesis and tests. Coordinate state and finding contracts with Ronn + Neel (#7) and check definitions with Jin + Behzad (#2).
