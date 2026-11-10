# Sentinel Open Source Project Plan

## Table of Contents

- [Project Description](#-project-description)
  - [Objectives](#objectives)
  - [Stakeholders](#stakeholders)
- [Scope](#scope)
  - [Minimum Viable Product](#minimum-viable-product)
  - [Initial Supported Ecosystems](#initial-supported-ecosystems)
  - [Stretch Goals](#stretch-goals)
- [System Workflow](#system-workflow)
- [Implementation Plan](#-implementation-plan)
  - [Project Timeline](#project-timeline)
- [Technical Architecture](#technical-architecture)
  - [Main Services](#main-services)
- [Agent Design](#agent-design)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [MCP Tool Design](#mcp-tool-design)
- [API Design](#api-design)
- [Testing and Evaluation](#testing-and-evaluation)
- [CI/CD and Hosting](#cicd-and-hosting)
- [Team Management](#-team-management)
  - [Team Members](#team-members)
  - [Roles and Responsibilities](#roles-and-responsibilities)
  - [Communication](#communication)
- [Definition of Done](#definition-of-done)
- [Sprint Planning](#-sprint-planning)
  - [Working Model](#working-model)
  - [Sprint 1 — November 9–22, 2026](#sprint-1--november-922-2026)
  - [Sprint 1 Deliverables by Workstream](#sprint-1-deliverables-by-workstream)
  - [Sprint 1 Definition of Success](#sprint-1-definition-of-success)
  - [Sprint Planning Template](#sprint-planning-template)
  - [Definition of Done for Issues](#definition-of-done-for-issues)

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

Sentinel will follow six two-week sprints beginning November 9, 2026, with an optional holiday buffer. Dates and deliverables are planning targets and may be adjusted based on team capacity, exams, integration progress, and technical discoveries.

| Period | Dates | Primary focus | Target outcome |
|---|---|---|---|
| Sprint 1 | Nov 9–22, 2026 | Foundation and shared contracts | Sample PR flows through FastAPI, mock LangGraph agents, and structured findings |
| Sprint 2 | Nov 23–Dec 6, 2026 | Real dependency and CI/CD checks; GitHub intake | First deterministic security findings with evidence on real or representative PR inputs |
| Sprint 3 | Dec 7–20, 2026 | End-to-end MVP integration | Working PR-to-report flow, with core checks and reproducible tests |
| Holiday buffer | Dec 21, 2026–Jan 3, 2027 | Optional async fixes, documentation and rest | No mandatory sprint commitments |
| Sprint 4 | Jan 4–17, 2027 | Human review, dashboard and release risk | Reviewable findings, reviewer decisions, initial release checks |
| Sprint 5 | Jan 18–31, 2027 | Security hardening and evaluation | Prompt-injection safeguards, tracing, improved precision and reliability |
| Sprint 6 | Feb 1–14, 2027 | Beta, deployment and demo | Deployed beta candidate, documentation, evaluation summary and demonstration |

### Sprint 1: Foundations and Vertical Slice (November 9–22)

- Establish shared PR context, agent input/output, and security finding schemas by November 11.
- Build deterministic file classification and a LangGraph workflow with placeholder Dependency, CI/CD, and Release nodes.
- Set up FastAPI endpoints and a read-only MCP repository tool prototype.
- Prototype source-aware repository ingestion and keyword retrieval.
- Configure Docker, GitHub Actions CI, and contributor documentation.
- Design a findings interface and create labelled evaluation fixtures.
- Integrate a sample PR → FastAPI → LangGraph → mock agents → synthesis → structured findings demo by November 22.

**Out of scope for Sprint 1:** production-grade LLM analysis, full vulnerability intelligence, live GitHub publication, production deployment, and a fully integrated frontend. Mock data is acceptable for the first vertical slice.

### Sprint 2: Security Checks and GitHub Intake (November 23–December 6)

- Receive and validate GitHub webhook events; retrieve PR metadata and diffs with least-privilege access.
- Implement initial deterministic dependency and GitHub Actions checks using Sprint 1 rules and fixtures.
- Expand MCP tools for changed files, workflow inspection and dependency metadata.
- Add npm/Node.js parsing first, with Python support as capacity allows.
- Attach source paths, line references, tool evidence and uncertainty to findings.
- Extend integration tests to exercise realistic PR changes.

### Sprint 3: End-to-End MVP (December 7–20)

- Connect GitHub intake, file classification, real security checks, repository context and risk synthesis.
- Normalize findings, deduplicate repeated results, and distinguish verified facts from inferred risks.
- Produce an evidence-backed review report from a representative pull request.
- Add failure handling, timeouts and basic workflow tracing.
- Test safe and unsafe PR examples; document known limitations.
- Keep commitments flexible during December exams.

### Holiday Buffer (December 21–January 3)

- No mandatory work or meetings.
- Optional documentation, bug fixes, review of open PRs and preparation for January.

### Sprint 4: Human Review and Release Analysis (January 4–17)

- Implement dashboard views for findings, evidence, severity and uncertainty.
- Add human review actions: confirm, dismiss, request changes or escalate.
- Persist review decisions where needed.
- Add initial build/release configuration checks.
- Prototype publishing approved findings to GitHub, with appropriate permissions and safeguards.

### Sprint 5: Hardening and Evaluation (January 18–31)

- Treat repository content, diffs and tool responses as untrusted inputs.
- Add prompt-injection and unsafe tool-use tests; keep MCP tools read-only by default.
- Expand labelled PR fixtures and evaluate precision, recall and false positives.
- Improve observability, tool-call tracing, error handling and review latency.
- Refine evidence quality and reduce unsupported security claims.

### Sprint 6: Beta and Demonstration (February 1–14)

- Prepare a reproducible cloud deployment, with secure secrets management.
- Run end-to-end regression tests and a small beta evaluation.
- Polish the dashboard, API documentation and contributor onboarding.
- Publish deployment and architecture instructions, known limitations and a demo walkthrough.
- Present the beta and prioritize follow-on work based on feedback.

### Post-Beta Backlog

Additional ecosystems, richer package provenance and maintainer analysis, sandboxed behavior analysis, repository security memory, infrastructure-as-code checks, advanced release artifact analysis, GitHub Marketplace distribution and broader public release work are future options, not commitments for the six-sprint beta timeline.

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
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── CODEOWNERS
│   └── PULL_REQUEST_TEMPLATE.md
│
├── README.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── PROJECT.md
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

Sentinel is led by Lukhsaan Elankumaran with twelve contributors organized into six initial pairs. Assignments are proposed starting points and can change based on contributor preferences and sprint planning.

| Primary workstream | Initial pair | Sprint 1 focus |
|---|---|---|
| Agent Architecture | Sarthak Kulashari and Alex Melnbardis | LangGraph state, routing and mock agents |
| Security Agents | Rohit Suryadevara and Ronn Philip | Dependency and CI/CD detection rules |
| Backend and MCP | Megh Joshi and Behzad Janjua | FastAPI, Pydantic contracts and read-only MCP tool |
| Repository Context | Yug Vashisth and Toheeb Eji | Repository ingestion and retrieval |
| Cloud and DevOps | Neel Oza and Parmeet Abbat | Local Docker, GitHub Actions and setup docs |
| Product and Evaluation | Saqib Khan and Nana Appiagyei Poku | Findings UI and labelled test fixtures |

**Cross-team coordination:** Megh and Sarthak coordinate shared schemas; Neel and Parmeet coordinate contribution guidelines; Sarthak and Behzad coordinate the Sprint 1 integration demo. These are additional responsibilities, not separate full-time teams.

Contributors may collaborate beyond their primary issue, while allowing the assigned owners to lead implementation and receive meaningful credit. Across future sprints, members should have opportunities to explore other areas while developing ownership of a specific Sentinel subsystem.

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

### Meeting and Update Cadence

- **Weekly team meeting:** Sundays, 3:30–4:00 PM Eastern Time, subject to team confirmation.
- **Sprint length:** Two weeks, Monday through the second Sunday.
- **Midweek asynchronous update:** Thursday in Discord, noting completed work, next steps and blockers.
- **Mid-sprint check-in:** Sunday meeting after the first week.
- **Sprint review and planning:** Sunday meeting at the end of the second week; demonstrate working artifacts and select the next sprint's issues.
- **Code and task tracking:** GitHub Issues, pull requests and GitHub Projects; Discord is for coordination and unblock requests.

For Sprint 1, the key checkpoints are November 11 (shared contracts), November 12 (first async update), November 13 (contribution workflow), November 15 (mid-sprint review), November 19 (integration checkpoint), and November 22 (demo and retrospective).

### Collaboration Expectations

- Each issue has clear owners and an expected deliverable; cross-team help is welcome.
- Open draft PRs early when possible, rather than integrating everything on the last day.
- Raise blockers in Discord promptly and link related GitHub issues or PRs.
- Every contributor is accountable for code they submit, including AI-assisted work. AI tools are encouraged as accelerators, but contributors should understand, test and be able to explain their changes.
- Security-related code and findings must be validated; do not treat generated outputs as verified evidence.
- Optional in-person work sessions and technical workshops can be organized when useful and feasible.

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

### Working Model

- **Standard sprint:** Two weeks.
- **Board columns:** Backlog, Ready, In Progress, In Review, Done.
- **Issue ownership:** Usually two contributors per implementation issue, with a clear lead for cross-team coordination issues.
- **Priority:** P0 for critical dependencies and integration; P1 for important supporting work.
- **Review:** At least one other contributor reviews implementation PRs before merge.
- **Sprint review:** Demo completed functionality, note unfinished work and blockers, and revise the next sprint's scope.

### Sprint 1 — November 9–22, 2026

**Sprint goal:** Demonstrate a sample pull request passing through a FastAPI review endpoint, deterministic LangGraph routing, mock security agents and risk synthesis, returning a validated structured finding. Supporting teams will deliver repository retrieval, CI, UI design and evaluation fixtures.

| Issue title | Suggested owners | Priority | Target |
|---|---|---|---|
| Implement Initial LangGraph Agent Orchestration | Neel + Alex | P0 | Nov 22 |
| Research and Define Initial Dependency and CI/CD Security Checks | Jin + Behzad | P0 | Nov 22 |
| Set Up FastAPI Backend and Initial MCP Tool Integration | Toheeb + Parmeet | P0 | Nov 22 |
| Prototype Repository Context Ingestion and Retrieval | Yug + Nana | P1 | Nov 22 |
| Configure Local Development Environment, Docker, and GitHub Actions CI | Saqib + Megh | P0 | Nov 22 |
| Design Security Findings Dashboard and Initial Evaluation Framework | Sarthak + Rohit | P1 | Nov 22 |
| Finalize Shared API Schemas and Agent Communication Contracts | Ronn + Neel | P0 | Nov 11 |
| Establish GitHub Contribution Guidelines and Pull Request Templates | Lukhsaan | P1 | Nov 13 |
| Integrate Sprint 1 Components into an End-to-End Sentinel Demo | Parmeet | P0 | Nov 22 |

These assignments are initial recommendations; GitHub issue assignees are the source of truth after contributors confirm ownership.

### Sprint 1 Deliverables by Workstream

**Agent Architecture:** Shared LangGraph state, deterministic classification, conditional routing, mock Dependency/CI/CD/Release nodes, synthesis and tests.

**Security Agents:** At least three dependency and three CI/CD checks documented with detection criteria, evidence, safe/unsafe fixtures and false-positive limitations.

**Backend and MCP:** Running FastAPI application, health and mock review endpoints, validated Pydantic models, one read-only repository/diff MCP tool and tests.

**Repository Context:** Sample repository ingestion, keyword retrieval, file-path references and a reproducible demonstration.

**Cloud and DevOps:** Docker-based local setup, automated GitHub Actions lint/test, contributor instructions and a Cloud Run deployment proposal.

**Product and Evaluation:** Findings dashboard wireframe, evidence/uncertainty and human-review design, at least six labelled PR fixtures and a basic evaluation harness.

**Coordination:** Shared schemas by November 11, contribution process by November 13, and end-to-end integration demo by November 22.

### Sprint 1 Definition of Success

A reproducible local demo follows this path:


a sample PR → FastAPI → LangGraph Intake → appropriate mock agents → Risk Synthesis → structured findings.

The demonstration must include a sample request/response, passing integration test and instructions for running it. Production deployment, live GitHub publishing, complete RAG and fully implemented AI agents are not required in Sprint 1.

### Sprint Planning Template

For each future sprint, record:

- **Dates and sprint goal**
- **Issues, priorities and assignees**
- **Dependencies and early checkpoints**
- **Expected demo or measurable deliverable**
- **Risks and capacity constraints**
- **Retrospective:** what shipped, what slipped, blockers and what to improve

### Definition of Done for Issues

An issue is complete when its acceptance criteria are met, relevant tests and documentation are included, the work is demonstrated where appropriate, and the corresponding PR has passed review. Research and design issues may be completed with reviewed documentation, fixtures or wireframes rather than production code.
