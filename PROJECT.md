# Sentinel Open Source Project Plan

## Table of Contents

- [Project Description](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#-project-description)
- [Objectives](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#objectives)
- [Stakeholders](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#stakeholders)
- [Scope](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#scope)
- [System Workflow](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#system-workflow)
- [Implementation Plan](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#-implementation-plan)
- [Project Timeline](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#project-timeline)
- [Technical Architecture](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#technical-architecture)
- [Agent Design](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#agent-design)
- [Tech Stack](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#tech-stack)
- [Project Structure](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#project-structure)
- [MCP Tool Design](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#mcp-tool-design)
- [API Design](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#api-design)
- [Testing and Evaluation](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#testing-and-evaluation)
- [CI/CD and Hosting](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#cicd-and-hosting)
- [Team Management](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#-team-management)
- [Roles and Responsibilities](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#roles-and-responsibilities)
- [Communication](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#communication)
- [Definition of Done](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#definition-of-done)
- [Sprint Planning](https://chatgpt.com/g/g-p-68d86d526e508191ad3ddd09399a432e/c/69d34de7-3ac8-8328-bd08-4c7cb3d93926#-sprint-planning)

---

## 💡 Project Description
Sentinel is an open-source, agentic security review platform designed to help developers identify risky changes before pull requests are merged or released.

Most code review tools focus primarily on application logic and code quality. However, modern software incidents increasingly originate from areas such as dependencies, lockfiles, CI/CD workflows, build configuration, packaging, and release artifacts.

Sentinel will treat security review as a structured investigation rather than a single AI response. Specialized agents will inspect different parts of a pull request, use MCP-connected tools to gather evidence, retrieve repository-specific context, and produce a transparent security report.

The system will include human approval before findings are posted back to a pull request.

### Objectives

1. Build an open-source security review platform for pull requests.
2. Detect dependency, supply-chain, CI/CD, packaging, and release risks.
3. Develop a custom MCP server for repository and security tools.
4. Integrate selected existing MCP servers where useful.
5. Build a custom repository-grounded RAG pipeline.
6. Create stateful multi-agent workflows using LangGraph.
7. Provide evidence, traces, and confidence for each generated finding.
8. Include human approval before actions are taken.
9. Deploy the platform using cloud-native services.
10. Give contributors experience with modern AI systems, cybersecurity, open-source collaboration, and cloud infrastructure.

### Stakeholders

- Open-source maintainers
- Software development teams
- Security-conscious developers
- Student contributors
- DevOps and platform engineers
- Repository owners
- GDG McMaster members

---

## Scope

### Minimum Viable Product
The MVP will support:

- GitHub pull request ingestion
- Detection of changed dependency and workflow files
- A custom Sentinel MCP server
- Dependency, CI/CD, and Repository Context agents
- Repository-grounded retrieval
- LangGraph-based workflow orchestration
- Structured security reports
- Human approval before posting findings
- Basic tracing and observability
- Cloud deployment

### Initial Supported Ecosystems
The first version should support a limited number of package ecosystems:

- npm and Node.js
- Python requirements or `pyproject.toml`
- One additional ecosystem depending on team experience
Possible third ecosystems include:

- Maven or Gradle
- Cargo
- Go modules

### Stretch Goals

- Release artifact analysis
- Source map exposure detection
- Secret scanning
- Package ownership and maintainer-change analysis
- Vulnerability database integrations
- Software Bill of Materials generation
- Support for more package ecosystems
- Historical incident memory
- False-positive learning
- Configurable repository security policies
- Public deployment templates
- GitHub Marketplace integration

---

## System Workflow
A typical Sentinel workflow will follow these steps:

```
Pull Request Opened
        |
        v
GitHub Webhook
        |
        v
Intake and File Classification
        |
        +------------------+
        |                  |
        v                  v
Dependency Review     CI/CD Review
        |                  |
        +--------+---------+
                 |
                 v
      Repository Context Retrieval
                 |
                 v
         Risk Synthesis Agent
                 |
                 v
       Human Review and Approval
                 |
                 v
       GitHub Comment or Report
```
The system will use deterministic rules before involving an LLM.

For example:

- If a dependency manifest changes, run the Dependency Agent.
- If a workflow file changes, run the CI/CD Agent.
- If build or packaging files change, run the Release Agent.
- If a file type is unsupported, notify the user and recommend manual review.
This prevents the model from guessing when security analysis is required.

---

## 🧭 Implementation Plan

## Project Timeline
The project will be divided into six major milestones.

### Milestone 1: Foundations and Onboarding
**Target:** September to early October

- Introduce contributors to Git, GitHub, pull requests, and open-source workflows.
- Finalize project architecture and supported ecosystems.
- Set up frontend, backend, MCP server, and infrastructure repositories.
- Configure GitHub Projects and contribution guidelines.
- Build a basic GitHub webhook receiver.
- Create initial UI wireframes.
- Define shared data models and tool schemas.

### Milestone 2: Deterministic Pull Request Analysis
**Target:** October

- Retrieve pull request metadata and file diffs.
- Classify changed files.
- Detect package manifests, lockfiles, workflow files, and release files.
- Implement npm dependency parsing.
- Normalize dependency changes into a shared schema.
- Add support for a second package ecosystem.
- Store review sessions in PostgreSQL.

### Milestone 3: Custom MCP Server
**Target:** November

- Build the Sentinel MCP server.
- Expose structured repository and security tools.
- Deploy the MCP server using Streamable HTTP.
- Add authentication and authorization.
- Connect the workflow backend to the MCP server.
- Integrate one existing MCP server where useful.
Initial tools may include:

- `get_pull_request_diff`
- `get_changed_files`
- `get_dependency_changes`
- `get_workflow_changes`
- `get_repository_security_policy`
- `get_previous_findings`
- `lookup_package_metadata`
- `lookup_vulnerability_data`

### Milestone 4: MVP Agent Workflow
**Target:** January to February

- Implement the Intake Agent.
- Implement the Dependency Agent.
- Implement the CI/CD Agent.
- Implement the Repository Context Agent.
- Implement the Risk Synthesis Agent.
- Build the LangGraph state machine.
- Add retries, checkpoints, and error handling.
- Produce a structured security report.

### Milestone 5: RAG, Transparency, and Human Approval
**Target:** February to March

- Build the repository indexing pipeline.
- Add hybrid semantic and keyword retrieval.
- Index security policies, architecture docs, and prior findings.
- Show evidence for each finding.
- Build the human approval dashboard.
- Allow findings to be approved, edited, dismissed, or escalated.
- Add workflow and tool-call traces.

### Milestone 6: Evaluation, Deployment, and Final Release
**Target:** March to April

- Create vulnerable pull request test cases.
- Measure false-positive and false-negative rates.
- Improve agent routing and prompts.
- Harden cloud deployment.
- Improve documentation and onboarding.
- Prepare the final demo.
- Publish the project as an open-source release.

---

## Technical Architecture
Sentinel will use a modular, cloud-native architecture.

```
GitHub
  |
  v
Webhook and Orchestration API
  |
  v
LangGraph Workflow
  |
  +----------------------+
  |                      |
  v                      v
Sentinel MCP Server   Existing MCP Servers
  |                      |
  +----------+-----------+
             |
             v
Repository and Security Tools
             |
             v
PostgreSQL, Vector Index, and Object Storage
             |
             v
Review Dashboard
```

### Main Services

#### Frontend
The frontend will provide:

- Pull request review summaries
- Finding severity and confidence
- Retrieved evidence
- Agent and tool-call traces
- Approval and dismissal controls
- Historical review results

#### Backend
The backend will manage:

- GitHub webhook events
- Authentication
- LangGraph workflow execution
- Database operations
- Review state
- Human approval actions
- GitHub report publishing

#### Sentinel MCP Server
The custom MCP server will expose structured tools for:

- Repository inspection
- Pull request analysis
- Dependency parsing
- Workflow inspection
- Security-policy retrieval
- Package metadata lookup
- Vulnerability lookup
- Historical finding retrieval

#### Retrieval Layer
The custom RAG system will index:

- `SECURITY.md`
- `CONTRIBUTING.md`
- Architecture documentation
- Release documentation
- Repository policies
- Previous findings
- Reviewer decisions
- Historical incidents
Retrieval should combine:

- Vector similarity
- Keyword or BM25 search
- Metadata filters
- File-path filters
- Recency filters
- Risk-category filters

#### Persistence Layer
PostgreSQL will store:

- Repository information
- Review sessions
- Findings
- Approval decisions
- Workflow state
- Agent traces
- Repository memory
- Reviewer feedback
Vector search may use PostgreSQL with `pgvector` or another open-source vector store.

---

## Agent Design

### Intake Agent
Responsibilities:

- Read normalized pull request metadata.
- Classify the type of change.
- Route the workflow to relevant agents.
- Avoid launching unnecessary reviews.

### Dependency Agent
Responsibilities:

- Inspect dependency and lockfile changes.
- Query package registry metadata.
- Look for install scripts.
- Look for unusual version changes.
- Retrieve known vulnerability data.
- Identify suspicious supply-chain indicators.

### CI/CD Agent
Responsibilities:

- Review workflow permissions.
- Identify unpinned third-party actions.
- Detect unsafe triggers.
- Identify remote script execution.
- Check for possible secret exposure.
- Compare workflow changes against repository policy.

### Release Agent
Responsibilities:

- Inspect build configuration.
- Review packaging settings.
- Detect exposed source maps.
- Review artifact-upload settings.
- Check release pipeline permissions.
The Release Agent may begin as a stretch goal.

### Repository Context Agent
Responsibilities:

- Query the custom RAG system.
- Retrieve relevant security policies.
- Retrieve historical findings.
- Retrieve approved exceptions.
- Ground findings in repository-specific evidence.

### Risk Synthesis Agent
Responsibilities:

- Combine findings from all agents.
- Remove duplicates.
- Assign severity and confidence.
- Explain supporting evidence.
- Recommend whether changes should be requested.
- Produce a structured final report.

---

## Tech Stack

### Frontend
Possible options:

- Next.js
- React
- TypeScript
- Tailwind CSS
- ShadCN UI

### Backend
Possible options:

- Python
- FastAPI
- Pydantic
- SQLAlchemy

### Agent and AI Layer

- LangGraph
- LangChain where useful
- Model Context Protocol SDK
- Open-weight or hosted LLM APIs
- Structured output schemas

### Retrieval
Possible options:

- PostgreSQL with `pgvector`
- Qdrant
- Chroma
- OpenSearch

### Database

- PostgreSQL
- Redis for caching or temporary workflow state if needed

### Cloud and Infrastructure

- Google Cloud Run
- Google Cloud SQL
- Google Cloud Storage
- Google Artifact Registry
- Google Secret Manager
- Google Cloud Logging
- Docker
- Terraform as a stretch goal

### Development and Collaboration

- GitHub
- GitHub Projects
- GitHub Actions
- Discord
- Google Meet

---

## Project Structure

```
sentinel/
├── frontend/
│   ├── src/
│   ├── components/
│   ├── app/
│   └── tests/
│
├── backend/
│   ├── api/
│   ├── github/
│   ├── workflows/
│   ├── agents/
│   ├── retrieval/
│   ├── memory/
│   ├── models/
│   └── tests/
│
├── mcp-server/
│   ├── tools/
│   ├── resources/
│   ├── adapters/
│   ├── security/
│   └── tests/
│
├── dependency-scanners/
│   ├── npm/
│   ├── python/
│   └── shared/
│
├── infrastructure/
│   ├── docker/
│   ├── cloud-run/
│   ├── github-actions/
│   └── terraform/
│
├── evaluation/
│   ├── vulnerable-prs/
│   ├── expected-findings/
│   └── metrics/
│
├── docs/
│   ├── architecture/
│   ├── onboarding/
│   ├── mcp/
│   └── security/
│
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
└── PROJECT_PLAN.md
```

---

## MCP Tool Design
The MCP server should return structured facts rather than asking the model to infer raw data.

### Example Tool: Dependency Changes

```
get_dependency_changes(repository, pull_request)
```
Responsibilities:

1. Detect changed dependency files.
2. Identify the package ecosystem.
3. Compare old and new versions.
4. Parse the correct manifest or lockfile.
5. Return normalized package changes.
Example response:

```
{
  "ecosystem": "npm",
  "added": [
    {
      "name": "example-package",
      "version": "1.0.0"
    }
  ],
  "updated": [
    {
      "name": "axios",
      "old_version": "1.6.0",
      "new_version": "1.7.0"
    }
  ],
  "removed": []
}
```

### Example Tool: Package Risk Lookup

```
lookup_package_risk(ecosystem, package_name, version)
```
Possible outputs:

- Known vulnerabilities
- Package age
- Publication date
- Maintainer information
- Install scripts
- Download statistics
- Registry metadata
- Dependency-tree information
- Risk indicators

### Adapter Pattern
Each package ecosystem should implement a shared interface:

```
DependencyScanner
├── NpmScanner
├── PythonScanner
├── MavenScanner
├── CargoScanner
└── GoScanner
```
Unsupported ecosystems should be reported clearly rather than analyzed through model guesswork.

---

## API Design

### Example Endpoints

```
POST /api/github/webhook
GET  /api/reviews/{review_id}
GET  /api/reviews/{review_id}/findings
GET  /api/reviews/{review_id}/trace
POST /api/findings/{finding_id}/approve
POST /api/findings/{finding_id}/dismiss
POST /api/findings/{finding_id}/escalate
POST /api/reviews/{review_id}/publish
```

### Documentation

- OpenAPI
- Swagger UI
- Postman collection where useful

---

## Testing and Evaluation
Sentinel requires both standard software testing and security-review evaluation.

### Unit Testing

- Dependency parsers
- MCP tools
- API handlers
- File classifiers
- Data normalization
- Retrieval filters
- Agent output schemas
Possible frameworks:

- Pytest
- Vitest
- Jest
- Playwright

### Integration Testing

- GitHub webhook to workflow execution
- Backend to MCP server communication
- MCP server to external APIs
- Agent workflow to database
- Approval flow to GitHub report publishing

### Evaluation Dataset
The team will create seeded pull requests containing known issues such as:

- New dependency with an install script
- Suspicious package name
- Vulnerable package version
- Unpinned GitHub Action
- Excessive workflow permissions
- Remote script execution
- Public source map configuration
- Exposed secret
- Valid change that should not be flagged

### Evaluation Metrics

- Precision
- Recall
- False-positive rate
- False-negative rate
- Finding severity accuracy
- Evidence relevance
- Tool-call success rate
- Review latency
- Human approval rate

---

## CI/CD and Hosting

### CI/CD
GitHub Actions will be used for:

- Linting
- Formatting
- Unit tests
- Integration tests
- Docker image builds
- Security checks
- Deployment to staging
- Deployment to production

### Hosting

- **Frontend:** Vercel or Google Cloud Run
- **Backend:** Google Cloud Run
- **MCP Server:** Google Cloud Run using Streamable HTTP
- **Database:** Google Cloud SQL for PostgreSQL
- **Vector Search:** `pgvector` or hosted open-source vector database
- **Artifacts:** Google Cloud Storage
- **Container Images:** Google Artifact Registry
- **Secrets:** Google Secret Manager
- **Monitoring:** Google Cloud Logging and custom workflow traces

---

## 📋 Team Management

## Team Members
The project is intended for approximately 10 contributors.

- **Project Lead / Scrum Master / Product Owner:** Lukhsaan Elankumaran
- **Frontend Developers:** 2
- **Backend Developers:** 2
- **MCP and Integration Developers:** 2
- **Agent Workflow Developers:** 2
- **Retrieval and Evaluation Developers:** 1
- **Cloud and DevOps Developer:** 1
Roles may overlap depending on contributor interests and experience.

---

## Roles and Responsibilities

### Project Lead

- Maintain the project vision.
- Define and prioritize the backlog.
- Break milestones into achievable issues.
- Assign and review tickets.
- Facilitate sprint planning and retrospectives.
- Support blocked contributors.
- Review pull requests.
- Coordinate demos and documentation.
- Ensure contributors have meaningful ownership.

### Frontend Developers

- Build the review dashboard.
- Display findings and evidence.
- Build trace visualizations.
- Implement approval and dismissal flows.
- Write frontend tests.
- Maintain accessible and responsive UI.

### Backend Developers

- Build FastAPI endpoints.
- Handle GitHub webhook events.
- Manage authentication and persistence.
- Integrate workflow state with the database.
- Publish approved reports to GitHub.
- Write backend tests.

### MCP and Integration Developers

- Build the custom Sentinel MCP server.
- Define tool schemas.
- Build dependency adapters.
- Connect registry and vulnerability sources.
- Integrate selected existing MCP servers.
- Implement authentication and testing.

### Agent Workflow Developers

- Build LangGraph workflows.
- Develop agent routing and handoffs.
- Define structured agent outputs.
- Add retries and checkpoints.
- Improve prompts and tool-use logic.
- Build tracing and observability.

### Retrieval and Evaluation Developers

- Build repository indexing.
- Implement hybrid retrieval.
- Design metadata filters.
- Create evaluation datasets.
- Measure precision and recall.
- Track false positives and false negatives.

### Cloud and DevOps Developer

- Containerize services.
- Configure Cloud Run deployments.
- Build GitHub Actions pipelines.
- Manage secrets and service identities.
- Configure logs and monitoring.
- Maintain staging and production environments.

---

## Communication

- **Primary communication:** Discord
- **Code collaboration:** GitHub
- **Project tracking:** GitHub Projects
- **Meetings:** Google Meet and in-person sessions

### Suggested Schedule

- Weekly sprint review
- Biweekly sprint retrospective
- Biweekly in-person work session
- Monthly project demo
- Additional technical workshops during onboarding

### In-Person Sessions
In-person work sessions will be used to:

- Help contributors work through blockers.
- Pair newer and more experienced developers.
- Review architecture decisions.
- Test integrations.
- Demo completed work.
- Build stronger team collaboration.

---

## Definition of Done
A pull request is considered complete when:

- The assigned issue requirements are satisfied.
- The code follows project formatting and linting standards.
- Relevant unit or integration tests are included.
- Existing tests pass.
- Documentation is updated.
- Structured logs or error handling are included where needed.
- No secrets or credentials are committed.
- The pull request has a clear description.
- The pull request has been reviewed by at least one other contributor.
- The Project Lead or assigned reviewer approves the change.
- The branch has no unresolved merge conflicts.

---

## 👟 Sprint Planning

### Sprint Length

- Standard sprint length: two weeks
- Weekly check-ins may be used within each sprint

## High-Level Sprint Goals

### Sprint 1: Onboarding and Architecture

- Introduce Git and GitHub workflow.
- Finalize architecture.
- Create repository structure.
- Configure GitHub Projects.
- Create starter issues.
- Set up local development.

### Sprint 2: GitHub Integration

- Receive pull request webhooks.
- Fetch pull request metadata.
- Retrieve changed files.
- Store review sessions.

### Sprint 3: File Classification

- Detect dependency files.
- Detect workflow files.
- Detect release configuration.
- Add routing rules.
- Create normalized change schemas.

### Sprint 4: Dependency Parsing

- Build npm parser.
- Compare manifest and lockfile changes.
- Add Python parser.
- Write parser tests.

### Sprint 5: MCP Server Foundations

- Set up MCP server.
- Create repository tools.
- Create dependency tools.
- Add structured schemas.
- Deploy a development instance.

### Sprint 6: Package Risk Lookups

- Query registry metadata.
- Query vulnerability sources.
- Detect install scripts.
- Normalize risk signals.
- Add caching and error handling.

### Sprint 7: Agent Workflow Foundations

- Build Intake Agent.
- Build Dependency Agent.
- Define LangGraph state.
- Add agent traces.
- Add basic report generation.

### Sprint 8: CI/CD Review

- Build CI/CD Agent.
- Detect broad permissions.
- Detect unpinned actions.
- Detect unsafe commands.
- Add workflow policy retrieval.

### Sprint 9: Repository RAG

- Index repository policies.
- Build hybrid retrieval.
- Add metadata filters.
- Build Repository Context Agent.
- Display retrieved evidence.

### Sprint 10: Risk Synthesis

- Build Risk Synthesis Agent.
- Combine duplicate findings.
- Assign severity and confidence.
- Generate recommended actions.

### Sprint 11: Human Approval UI

- Display findings.
- Show evidence.
- Add approve, dismiss, edit, and escalate actions.
- Persist reviewer decisions.

### Sprint 12: GitHub Reporting

- Publish approved findings.
- Add pull request summaries.
- Handle retries and permissions.
- Test the full workflow.

### Sprint 13: Evaluation

- Create vulnerable test PRs.
- Measure precision and recall.
- Track false positives.
- Improve routing and prompts.

### Sprint 14: Deployment and Final Release

- Harden Cloud Run services.
- Finalize CI/CD.
- Improve documentation.
- Prepare final presentation.
- Publish the open-source release.

---

## Sprint Planning Template

### Sprint Duration

- **Sprint Length:** Two weeks
- **Start Date:** TBD
- **End Date:** TBD

### Sprint Goals

1. Goal 1
2. Goal 2
3. Goal 3

### User Stories
IDUser StoryPriorityStory PointsAssigneeUS01As a maintainer, I want Sentinel to detect changed dependency files so that dependency reviews are triggered reliably.High5TBDUS02As an agent, I want normalized package metadata so that I do not need to interpret raw lockfiles.High5TBDUS03As a maintainer, I want to see supporting evidence for a finding so that I can decide whether to approve it.High3TBDUS04As a contributor, I want clear local setup instructions so that I can begin development quickly.Medium2TBD
### Sprint Review Questions

- What was completed?
- What remains unfinished?
- What technical blockers were discovered?
- What should be changed in the next sprint?
- Are contributors receiving enough support and ownership?