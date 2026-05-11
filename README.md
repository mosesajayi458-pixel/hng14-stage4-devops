# SwiftDeploy

SwiftDeploy is a production-ready CLI deployment orchestration tool that provisions, validates, deploys, and manages containerized application stacks using a single declarative configuration file: `manifest.yaml`.

The platform is designed around modern DevOps principles including:

* Declarative infrastructure
* Progressive delivery
* Policy-as-Code governance
* Automated validation
* Observability and auditing
* Secure container deployment

SwiftDeploy automates the generation of infrastructure configuration, deployment execution, health validation, canary promotion workflows, Open Policy Agent (OPA) policy enforcement, metrics collection, audit reporting, and environment teardown.

---

# Features

* Single Source of Truth via `manifest.yaml`
* Automated generation of:

  * `nginx.conf`
  * `docker-compose.yml`
* Pre-deployment validation pipeline
* Docker-based deployment orchestration
* Health-aware rollout process
* Canary and stable deployment promotion
* Chaos testing support
* Prometheus-compatible metrics endpoint
* Open Policy Agent (OPA) governance enforcement
* Audit logging and deployment reporting
* Secure container hardening configuration
* Idempotent deployment operations

---

# Requirement Coverage

| Requirement                       | Implementation                  |
| --------------------------------- | ------------------------------- |
| Declarative configuration         | `manifest.yaml`                 |
| Configuration templating          | Jinja2 templates                |
| CLI orchestration tool            | `swiftdeploy`                   |
| Validation engine                 | `swiftdeploy validate`          |
| Deployment orchestration          | `swiftdeploy deploy`            |
| Canary / stable promotion         | `swiftdeploy promote`           |
| Infrastructure teardown           | `swiftdeploy teardown`          |
| Health checks                     | `/healthz`                      |
| Chaos testing                     | `/chaos`                        |
| Metrics collection                | `/metrics`                      |
| Policy-as-Code                    | OPA + Rego                      |
| Infrastructure policy checks      | `infra.rego`                    |
| Canary rollout policy checks      | `canary.rego`                   |
| Audit reporting                   | `swiftdeploy audit`             |
| Deployment governance enforcement | OPA policy decisions            |
| Container security hardening      | `cap_drop`, `no-new-privileges` |

---

# Architecture Overview

SwiftDeploy follows a declarative deployment workflow:

1. `manifest.yaml` acts as the single source of truth.
2. Jinja2 templates generate infrastructure configuration files.
3. Validation checks ensure deployment readiness.
4. OPA policies evaluate infrastructure and rollout conditions.
5. Docker Compose provisions the stack.
6. Health checks validate service readiness.
7. Metrics and audit logs provide observability and traceability.

---

# Project Structure

```bash
.
├── app/
│   ├── main.py
│   └── requirements.txt
├── templates/
│   ├── nginx.conf.j2
│   └── docker-compose.yml.j2
├── policies/
│   ├── infra.rego
│   ├── canary.rego
│   └── data.json
├── manifest.yaml
├── swiftdeploy
├── Dockerfile
├── audit_report.md
├── history.jsonl
└── README.md
```

---

# Prerequisites

The following dependencies are required:

* Linux / Ubuntu / WSL
* Python 3
* Docker
* Docker Compose
* curl

---

# Installation

Install required system packages:

```bash
sudo apt update

sudo apt install -y \
  docker.io \
  docker-compose \
  python3 \
  python3-pip \
  curl
```

Install Python dependencies:

```bash
pip3 install pyyaml jinja2 requests
```

---

# Build the Application Image

Before using SwiftDeploy, build the application container image:

```bash
docker build -t swift-deploy-1-node:latest .
```

---

# Manifest Configuration

All deployment behavior is controlled from `manifest.yaml`.

Example configuration:

```yaml
logging:
  volume: swiftdeploy-logs

network:
  driver_type: bridge
  name: swiftdeploy-net

nginx:
  image: nginx:latest
  port: 8080
  proxy_timeout: 5

services:
  image: swift-deploy-1-node:latest
  mode: stable
  port: 3000
  restart_policy: always
  version: 1.0.0

opa:
  image: openpolicyagent/opa:latest

policy:
  min_disk_free_gb: 10
  max_cpu_load: 2.0
  max_error_rate: 0.01
  max_p99_latency_ms: 500
```

The manifest serves as the single source of truth for:

* Infrastructure configuration
* Network configuration
* Service runtime settings
* Policy thresholds
* Deployment behavior

---

# CLI Setup

Make the CLI executable:

```bash
chmod +x swiftdeploy
```

---

# CLI Commands

## Initialize Configuration

Generate deployment configuration files:

```bash
./swiftdeploy init
```

Generated files:

* `nginx.conf`
* `docker-compose.yml`

---

## Validate Deployment

Run pre-deployment validation checks:

```bash
./swiftdeploy validate
```

Validation includes:

* YAML syntax validation
* Required manifest field checks
* Docker image verification
* Port availability checks
* Nginx syntax validation
* Policy data generation

---

## Deploy Application Stack

Deploy the application environment:

```bash
./swiftdeploy deploy
```

Deployment workflow:

1. Generate infrastructure configuration
2. Run validation checks
3. Start Docker services
4. Wait for health readiness
5. Verify successful deployment

Test deployment:

```bash
curl http://127.0.0.1:8080/
curl http://127.0.0.1:8080/healthz
```

---

## Promote Deployment Mode

Switch between stable and canary deployment modes:

### Promote Canary

```bash
./swiftdeploy promote canary
```

### Promote Stable

```bash
./swiftdeploy promote stable
```

Verify deployment mode:

```bash
curl -i http://127.0.0.1:8080/
```

Expected response header:

```text
X-Mode: canary
```

---

## Chaos Testing

Chaos testing is restricted to canary mode deployments.

### Simulate Slow Responses

```bash
curl -X POST http://127.0.0.1:8080/chaos \
  -H "Content-Type: application/json" \
  -d '{"mode":"slow","duration":5}'
```

### Inject Error Responses

```bash
curl -X POST http://127.0.0.1:8080/chaos \
  -H "Content-Type: application/json" \
  -d '{"mode":"error","rate":0.5}'
```

### Recover Service State

```bash
curl -X POST http://127.0.0.1:8080/chaos \
  -H "Content-Type: application/json" \
  -d '{"mode":"recover"}'
```

---

## Teardown Environment

Stop deployed services:

```bash
./swiftdeploy teardown
```

Remove generated files and resources:

```bash
./swiftdeploy teardown --clean
```

---

# Policy-as-Code Governance

SwiftDeploy integrates Open Policy Agent (OPA) to enforce deployment governance before rollout execution.

OPA evaluates:

* Infrastructure health conditions
* Canary rollout metrics
* Resource compliance thresholds

Deployment proceeds only when all policy checks pass.

OPA service:

* Container: `swiftdeploy-opa`
* Endpoint: `127.0.0.1:8181`

---

# Policy Files

Policies are located in:

```bash
policies/
├── infra.rego
├── canary.rego
└── data.json
```

## Infrastructure Policy

`infra.rego` validates:

* Minimum free disk space
* Maximum CPU load

## Canary Policy

`canary.rego` validates:

* Error rate thresholds
* P99 latency thresholds

---

# Dynamic Policy Thresholds

Policy thresholds are automatically generated from `manifest.yaml`.

Generated `data.json` example:

```json
{
  "limits": {
    "min_disk_free_gb": 10,
    "max_cpu_load": 2.0,
    "max_error_rate": 0.01,
    "max_p99_latency_ms": 500
  }
}
```

This ensures deployment policy configuration remains centralized and version-controlled.

---

# Deployment Governance Enforcement

Before deployment execution, SwiftDeploy queries OPA policies.

## Successful Policy Evaluation

```text
OPA Policy Check: PASSED
Deployment Approved
```

## Blocked Deployment Example

```text
Deployment blocked by OPA Infra Policy

Violations:
- Disk free 5.86GB is below minimum 10.00GB
```

Deployments are prevented when policy conditions fail.

---

# Observability

SwiftDeploy exposes runtime metrics and deployment audit reporting for operational visibility.

---

# Metrics Endpoint

Prometheus-compatible metrics are available at:

```bash
curl http://127.0.0.1:8080/metrics
```

Metrics include:

* Request counters
* Request latency histograms
* Uptime metrics
* Deployment mode state
* Chaos testing state

Example metric:

```text
# HELP chaos_active Chaos state (0=none, 1=slow, 2=error)
chaos_active 0.0
```

---

# Audit Logging

SwiftDeploy records deployment activity and operational metrics over time.

Generated files:

* `history.jsonl`
* `audit_report.md`

Generate an audit report:

```bash
./swiftdeploy audit
```

Example output:

```text
Audit report generated: audit_report.md
```

The report includes:

* Deployment timeline
* Deployment mode history
* Request throughput
* P99 latency metrics
* Error rate metrics
* Infrastructure policy decisions
* Canary policy decisions

---

# Security Hardening

SwiftDeploy applies secure container runtime configurations including:

* Dropped Linux capabilities (`cap_drop: ALL`)
* `no-new-privileges` enforcement
* Localhost-only OPA binding
* Public exposure limited to Nginx
* Internal-only API service exposure

---

# Testing Coverage

The following deployment scenarios were validated:

* Successful validation workflow
* Healthy deployment execution
* Canary promotion workflow
* Chaos testing execution
* Metrics endpoint verification
* OPA policy approval
* OPA deployment rejection
* Audit report generation
* Multi-container orchestration verification

---

# API Endpoints

| Endpoint   | Description                          |
| ---------- | ------------------------------------ |
| `/`        | Root API endpoint                    |
| `/healthz` | Health check endpoint                |
| `/metrics` | Prometheus metrics                   |
| `/chaos`   | Chaos testing endpoint (canary only) |

---

# Design Decisions

SwiftDeploy was designed to reflect real-world DevOps delivery practices:

* Declarative configuration ensures consistency and reproducibility
* Template generation reduces configuration drift
* Validation shifts failure detection earlier in the pipeline
* Canary deployments support progressive delivery strategies
* Chaos testing validates resilience assumptions
* OPA enforces deployment governance automatically
* Audit reporting improves traceability and accountability
* Metrics integration enables operational observability

---

# Author

**Damilola Olowookere**
HNG DevOps Internship — Stage 4A & Stage 4B
Blog post: https://medium.com/@mosesajayi458/building-swiftdeploy-a-cli-deployment-tool-with-canary-releases-chaos-engineering-99b407796a1a?postPublishedType=repub
---

# Conclusion

SwiftDeploy demonstrates a complete deployment orchestration workflow with:

* Infrastructure automation
* Progressive delivery
* Policy enforcement
* Observability
* Security hardening
* Operational auditing

The project satisfies all HNG Stage 4A and Stage 4B requirements while following production-grade DevOps engineering practices.
