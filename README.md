# 🛡️ Sentinel
Welcome to **Sentinel**, an open-source, agentic security review platform for pull requests, dependencies, CI/CD workflows, and release pipelines. 🚀

## 🔍 About
Modern software security risks do not only come from bugs in application code. They can also come from compromised dependencies, unsafe workflow permissions, exposed secrets, misconfigured build tools, and release artifacts that reveal sensitive information.

Recent incidents involving the Axios package ecosystem and the accidental exposure of Claude Code source files showed how serious security issues can originate from dependency updates, packaging decisions, and release processes.

Sentinel aims to address this gap by acting as an **AI-powered security investigation system** for pull requests.

Rather than relying on one general-purpose code reviewer, Sentinel will use specialized agents to inspect different areas of a software change, gather evidence through tools, retrieve repository-specific context, and produce a transparent security report.

**Our ultimate goal is to create and publish an open-source platform that helps maintainers answer one important question before merging a pull request: is this change safe to merge and safe to release?**

## ⚙️ How Sentinel Works
When a pull request is opened, Sentinel will:

1. Inspect which files and systems were changed.
2. Route the review to specialized security agents.
3. Use MCP tools to retrieve repository and package information.
4. Ground findings using repository-specific documentation and policies.
5. Combine findings into a structured security report.
6. Show the evidence and reasoning behind each finding.
7. Allow a maintainer to approve, edit, dismiss, or escalate findings before they are posted.

## 🤖 Specialized Agents
Sentinel may include agents such as:

- **Intake Agent**
Classifies the pull request and determines which security reviews are required.
- **Dependency Agent**
Reviews package manifests and lockfiles for suspicious updates, install scripts, unusual versions, and supply-chain risks.
- **CI/CD Agent**
Reviews GitHub Actions and deployment workflows for unsafe permissions, insecure triggers, unpinned actions, and secret exposure.
- **Release Agent**
Reviews build and packaging configuration for exposed source maps, unsafe artifacts, and release mistakes.
- **Repository Context Agent**
Retrieves repository policies, architecture documentation, previous findings, and accepted exceptions.
- **Risk Synthesis Agent**
Combines the findings into a final report with severity, confidence, evidence, and recommended next steps.

## 🧰 Technologies We Will Explore
Sentinel will give contributors hands-on experience with modern AI and software architecture, including:

- Model Context Protocol servers and tools
- Tool-calling AI agents
- Retrieval-Augmented Generation
- Hybrid semantic and keyword retrieval
- Stateful agent workflows
- LangGraph and LangChain
- Multi-agent coordination and handoffs
- Human-in-the-loop approval systems
- Tracing and observability
- GitHub Apps and webhooks
- Cloud-native application deployment
- Google Cloud Run
- PostgreSQL and vector search
- Docker and CI/CD pipelines

## 📚 What We Will Learn

- How AI agents interact with external tools and data
- How to design and build a custom MCP server
- How to connect agents to existing MCP integrations
- How to build a repository-grounded RAG pipeline
- How to create stateful and reliable agent workflows
- How to parse dependency files across software ecosystems
- How modern software supply-chain attacks occur
- How to review CI/CD and release workflows for security risks
- How to evaluate AI-generated security findings
- How to build transparent systems with evidence and human approval
- How to collaborate through GitHub issues, pull requests, testing, and code reviews
- How to deploy and monitor an agentic system in the cloud

## 👐 Who Should Join
Sentinel is designed for students interested in any of the following areas:

- Artificial intelligence and machine learning
- Cybersecurity
- Backend development
- Frontend development
- Cloud computing
- DevOps
- Open-source software
- Developer tooling
Prior experience with every technology is not required. Contributors will work in focused areas based on their interests and experience.

A basic understanding of programming, Git, and software development is recommended. More advanced topics such as MCP, RAG, agent orchestration, cloud deployment, and software supply-chain security will be introduced throughout the project.

Bring your curiosity, willingness to learn, and interest in building secure and transparent AI systems.