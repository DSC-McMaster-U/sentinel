# infrastructure/

Deployment and environment configuration.

| Path | What goes here |
| --- | --- |
| `docker/` | Dockerfiles and Docker Compose for local development |
| `cloud-run/` | Google Cloud Run service configuration and the deployment proposal |
| `terraform/` | Infrastructure as code (stretch goal) |

**Primary owners:** Neel + Parmeet

> **TODO (Sprint 1, Neel + Parmeet: "Configure Local Development Environment, Docker, and GitHub Actions CI"):** Docker-based local setup and a Cloud Run deployment proposal. Nothing is deployed in Sprint 1.

Never commit credentials, service account keys or Terraform state. `.gitignore` already covers the common cases.
