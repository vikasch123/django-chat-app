# TASK.md — Cloud Deployment Roadmap for `django-chat-app`

## Mission

Treat this repository as a Django application that needs to be made deployable and operable in a local AWS-compatible environment first, then in a real cloud environment later.

The application owner is primarily interested in:

- deploying the application to cloud-like infrastructure;
- establishing reliable CI/CD;
- deploying and managing workloads with Kubernetes and Argo CD;
- adding monitoring, dashboards, logging, and alerting;
- proceeding in small, reviewable phases rather than trying to redesign the application all at once.

Do **not** begin by refactoring the application into a new architecture. First understand the existing application, document assumptions, make the smallest changes required for a repeatable containerized deployment, and keep infrastructure changes separate from application changes wherever practical.

## Repository and application context

Repository: `vikasch123/django-chat-app`

The repository description is `For CICD pipeline` and it currently contains a Django project under `fundoo/`. The root also contains a Jenkins pipeline and Python dependency file.

The application appears to be a Django chat application with:

- Django 4.2;
- Django REST Framework and `django-rest-auth`;
- Django Channels for asynchronous/WebSocket chat behavior;
- Redis as the Channels layer;
- MySQL as the production database backend;
- SQLite in-memory database selection when tests are run;
- `gunicorn` and `daphne` dependencies for HTTP and ASGI serving;
- authentication, signup, activation, password reset, and chat routes;
- static assets and Django templates;
- an existing Jenkins pipeline that performs checkout, SonarQube scanning, dependency installation, tests on the `test` branch, and a placeholder production deployment stage.

The current code should be treated as an existing application that we are learning and operationalizing, not as a clean-slate sample project.

## Current directory structure

The important structure currently known is:

```text
.
├── .gitignore
├── Jenkinsfile
├── README.md
├── requirements.txt
└── fundoo/
    ├── .gitignore
    ├── README.md
    ├── manage.py
    ├── start.sh
    ├── jwt,json
    ├── fundoo/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   ├── routing.py
    │   └── models.py
    ├── chat/
    │   ├── admin.py
    │   ├── apps.py
    │   ├── consumers.py
    │   ├── models.py
    │   ├── routing.py
    │   ├── tests.py
    │   ├── urls.py
    │   ├── views.py
    │   ├── migrations/
    │   └── templates/
    ├── fundooapp/
    │   ├── admin.py
    │   ├── apps.py
    │   ├── forms.py
    │   ├── models.py
    │   ├── tokens.py
    │   ├── tests.py
    │   ├── views.py
    │   ├── migrations/
    │   ├── static/
    │   └── templates/
    └── static/
```

The exact contents of nested template, static, migration, and application files must be verified from the repository before implementation. Do not invent endpoints or infrastructure dependencies that are not supported by the code.

## How the application is written

### Django project package: `fundoo/fundoo/`

This package contains project-level Django configuration:

- `settings.py` configures installed apps, middleware, templates, database settings, static files, email, authentication backends, Redis Channels, WSGI, and ASGI behavior.
- `urls.py` defines the main HTTP URL table. It exposes the admin site, home/signup/sign-in flows, account activation, chat URLs, and Django authentication/password-reset URLs.
- `wsgi.py` exposes the WSGI application for traditional synchronous HTTP serving.
- `routing.py` composes the ASGI/Channels routing used for WebSockets.
- `models.py` appears to be a project-level placeholder and must be checked before assuming it is used.

### Django application: `fundoo/fundooapp/`

This is the account and general application area. It contains forms, models, token helpers, views, templates, static assets, migrations, tests, and admin/app configuration.

Expected responsibilities include user-facing pages, registration/authentication flows, account activation, token handling, and related persistence. The implementation must be inspected before deciding which routes are public, which require authentication, and which health checks can be safely added.

### Django application: `fundoo/chat/`

This is the chat area. It contains HTTP URLs/views plus Channels consumers and routing for real-time communication. It also has models, migrations, templates, and tests.

Because the project uses `channels` and `channels-redis`, deployment must account for both:

1. normal HTTP traffic; and
2. WebSocket/ASGI traffic.

Do not deploy only a WSGI process if the chat functionality requires WebSockets. Determine whether the production command should use Daphne, an ASGI-capable Gunicorn worker, or a split HTTP/WebSocket process based on the existing routing and application behavior.

### Configuration and runtime dependencies

The current settings contain values that are unsafe for production, including a hard-coded Django secret key, `DEBUG = True`, wildcard `ALLOWED_HOSTS`, hard-coded email configuration, and a Redis host of `127.0.0.1`. These are deployment blockers and must be addressed in a focused configuration-hardening step before production-like deployment.

The database settings already read several values from environment variables (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`). Redis, Django secret key, debug mode, allowed hosts, email settings, and other environment-dependent settings should be converted to an explicit, documented configuration contract rather than embedded in manifests or source code.

Never commit real passwords, SMTP credentials, API tokens, private keys, or kubeconfig files.

## Operating assumptions

- The first infrastructure target is a local AWS-compatible environment using **Floci**, not a real AWS account.
- Floci exposes AWS-compatible APIs through the standard local endpoint, normally `http://localhost:4566`, and uses test credentials for local development.
- Terraform must be written so the provider endpoint and credentials are configurable. Do not hard-code real AWS endpoints or credentials.
- Floci documentation indicates that the local emulator supports AWS-compatible services and an EKS workflow that creates a real k3s node behind the EKS-compatible API. Validate exactly which Terraform resources and operations are supported before relying on them.
- Terraform state, Kubernetes manifests, and monitoring configuration should be kept separate from this application repository unless a later decision explicitly chooses a monorepo.
- The application image must be reproducible and should run without requiring a developer workstation layout.
- Any design that works only against Floci but cannot later be adapted to AWS should be clearly labelled as local-only.

## Delivery strategy

Work in phases. Each phase must:

1. start with repository and runtime discovery;
2. document assumptions and unsupported operations;
3. make the smallest useful change;
4. include validation commands and tests;
5. leave a usable checkpoint before continuing.

Do not combine all phases into one large unreviewable change.

# Phase 0 — Discovery and application readiness

Before creating infrastructure repositories, produce a short implementation note covering:

- the actual HTTP and WebSocket entrypoints;
- the application start commands that work from a clean checkout;
- required environment variables;
- required services: database, Redis, SMTP, object storage, or anything else discovered;
- database migration and static-file collection commands;
- current test commands and their current pass/fail state;
- whether the existing `Jenkinsfile` paths work from the repository root;
- whether `start.sh` is usable and what it launches;
- whether the large `jwt,json` file is required at runtime or should be excluded/reviewed;
- a minimal health/readiness check that does not expose secrets.

Only after this discovery should the agent add a Dockerfile, container entrypoint, health endpoint, or configuration changes. If a production fix is necessary, keep it separate from infrastructure repository creation.

# Phase 1 — Separate Terraform infrastructure repository

Create a separate repository dedicated to Terraform/IaC. The repository name should be proposed before creation, for example `django-chat-app-infra` or another name approved by the owner.

The Terraform repository should eventually cover:

- IAM roles and policies needed by the local compatibility environment;
- VPC/networking abstractions if supported and useful in Floci;
- EKS-compatible cluster resources;
- EC2 resources where the local simulator supports the required operations;
- supporting resources such as security groups, subnets, load-balancer prerequisites, databases, Redis, or registries only after verifying Floci support;
- separate environment inputs for local/Floci and future real AWS usage;
- remote or local state strategy appropriate for the current environment.

### Floci-specific requirements

Use the Floci Terraform guidance and quickstart as the starting point:

- Terraform AWS provider endpoints must point to Floci for every service actually used.
- Use local credentials such as `test` only through variables or a local environment configuration.
- Use a local endpoint such as `http://localhost:4566` for development, not an AWS regional endpoint.
- Keep provider settings configurable so a future AWS profile/account can be used without rewriting resources.
- Confirm whether the chosen Floci version supports each Terraform resource before adding it.
- Do not claim that a resource is implemented merely because the AWS API exists; run Terraform validation/plan/apply against Floci.
- Prefer the documented Floci EKS workflow and verify how kubeconfig is obtained and how `kubectl` reaches the cluster.
- If EC2, EKS, IAM, networking, or load balancing is only partially emulated, document the limitation and provide a supported local substitute rather than silently pretending parity.

The first Phase 1 deliverable is a minimal, tested Terraform layout and provider configuration that can initialize against Floci without real AWS credentials. It should not attempt to create every possible service immediately.

Suggested layout:

```text
terraform-infra/
├── README.md
├── versions.tf
├── providers.tf
├── variables.tf
├── outputs.tf
├── main.tf
├── modules/
│   ├── iam/
│   ├── eks/
│   └── ec2/
└── environments/
    └── floci/
        ├── backend.tf
        ├── terraform.tfvars.example
        └── main.tf
```

# Phase 2 — Separate Kubernetes manifests/deployment repository

Create a separate repository for application deployment and Kubernetes platform configuration. The repository name should be proposed before creation, for example `django-chat-app-manifests`.

This repository should contain the deployment model for the application, including:

- Deployment or StatefulSet only where justified;
- Service;
- Ingress or Gateway configuration compatible with the selected local ingress controller;
- ConfigMap and Secret references, with no plaintext production secrets;
- database and Redis connection configuration;
- migration and static-file handling;
- liveness, readiness, and startup probes;
- resource requests and limits;
- PodDisruptionBudget and security context where appropriate;
- namespace/environment overlays;
- ServiceMonitor and/or PodMonitor for Prometheus scraping;
- optional NetworkPolicy after validating cluster networking support;
- Helm chart and/or Kustomize overlays, avoiding unnecessary duplication.

Use Helm for reusable packaging and Kustomize overlays for environment-specific customization only if that split remains understandable. Establish a clear source of truth and document whether Argo CD renders Helm, Kustomize, or both.

The manifests must support both HTTP and WebSocket traffic. Verify ingress timeout and upgrade settings for WebSockets. Do not assume a cloud load balancer exists in the local cluster.

The first Phase 2 deliverable is a deployment that can be installed into the Floci-provided Kubernetes environment and verified with `kubectl`, including application logs, probes, service routing, and a smoke test.

# Phase 3 — Argo CD continuous delivery

Set up Argo CD against the Kubernetes cluster and configure GitOps deployment from the manifest repository.

Expected outcomes:

- Argo CD is installed using a pinned, documented version or chart;
- the application is represented by an `Application` or `ApplicationSet` resource;
- sync policy, pruning, self-healing, and sync waves are consciously chosen and documented;
- image updates are promoted through Git changes rather than mutable tags alone;
- namespaces and repository credentials are handled securely;
- deployment status and rollback procedures are documented;
- local Floci/Kubernetes limitations are clearly separated from future production AWS behavior.

Do not place secrets directly in Git. Use a local development secret mechanism initially and define the migration path to a real secret manager or sealed/external secrets later.

# Phase 4 — Monitoring, dashboards, logging, and alerting

Monitoring may use a separate repository, for example `django-chat-app-observability`, if that keeps ownership and release cadence clear.

Start with the minimum useful platform:

- Prometheus;
- Grafana;
- Alertmanager;
- kube-state-metrics and node/container metrics where supported;
- ServiceMonitor/PodMonitor for the application;
- dashboards for availability, latency, request rate, errors, pod restarts, CPU/memory, database/Redis health, and WebSocket-related symptoms;
- alerts for application unavailability, failed readiness, crash loops, high error rate, high latency, resource exhaustion, and absent metrics;
- log collection only after the basic metrics path is healthy.

Determine whether the Django application exposes Prometheus metrics. If it does not, add metrics in a small, isolated application change or begin with black-box and Kubernetes metrics. Do not claim application-level latency or request metrics if only container metrics are available.

Alert destinations must be configurable and must not contain credentials in Git. Include a test procedure for firing and acknowledging a non-production alert.

## CI/CD direction

The existing Jenkinsfile is a starting point, not the final design. It currently has a placeholder production deployment stage and uses a hard-coded SonarQube URL. The agent must evaluate whether to:

- retain Jenkins and make it build/test/scan/publish an image while Argo CD handles deployment; or
- migrate build automation to GitHub Actions; or
- support both temporarily.

Do not create two competing deployment mechanisms. The desired separation is:

```text
Application repository
  -> test, lint, security scan, build image, push immutable image tag

Manifest repository
  -> update image reference, review change, Argo CD syncs to Kubernetes

Terraform repository
  -> provision or emulate infrastructure

Observability repository
  -> install/configure Prometheus, Grafana, Alertmanager, dashboards, alerts
```

The CI pipeline should eventually include dependency installation, tests, Django checks, migration validation, image build, image vulnerability scanning, and image publication to a registry supported by the selected environment. For Floci, verify whether its ECR-compatible service or a local OCI registry is the better target.

## Security and production-readiness blockers to track

Track these as explicit tasks rather than hiding them in a deployment PR:

- remove the hard-coded Django `SECRET_KEY` from source;
- set `DEBUG` from environment/configuration and default it safely;
- replace wildcard `ALLOWED_HOSTS` with configured hosts;
- move SMTP username/password and email settings to secrets;
- configure Redis through environment variables/service discovery instead of `127.0.0.1`;
- confirm database credentials and TLS requirements;
- audit the committed `jwt,json` artifact for secrets and necessity;
- remove public infrastructure IPs and tokens from CI configuration;
- pin container base images and infrastructure chart/provider versions;
- define non-root container execution where compatible;
- add image and dependency scanning;
- document backup, restore, migration, and rollback procedures.

## Definition of done for the overall roadmap

The work is complete only when:

- the application can be built from a clean checkout;
- automated tests and Django checks run in CI;
- an immutable container image can be produced;
- Terraform infrastructure can be validated and exercised against Floci without a real AWS account;
- Kubernetes manifests install successfully into the target local cluster;
- HTTP and WebSocket behavior are both tested;
- Argo CD can synchronize the application from Git;
- Prometheus scrapes the application/platform metrics;
- Grafana has useful dashboards;
- Alertmanager can deliver a tested alert;
- secrets are not committed;
- limitations between Floci and real AWS are documented;
- every phase has a README with prerequisites, commands, expected output, and cleanup steps.

## Working rules for the agent

- Explain what you found before changing unfamiliar application code.
- Ask for confirmation only when a decision cannot be resolved from the repository or this task; otherwise choose a reversible default and document it.
- Prefer small pull requests with one phase or one coherent concern per PR.
- Keep application, Terraform, Kubernetes/GitOps, and observability concerns separated.
- Never use real AWS credentials for Floci testing.
- Never delete existing application behavior without a migration or rollback plan.
- Validate all commands from the repository paths that actually exist.
- At the end of each phase, report: what changed, what was tested, what remains unknown, and the next proposed phase.

## Initial next step

Start with Phase 0 discovery. Produce a concise application and runtime assessment, identify the minimum container/runtime changes, and propose names and boundaries for the Terraform, manifest, and observability repositories before creating them.
