# Architecture & Deployment Reference Guide

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Requests                          │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Kubernetes Cluster                          │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         LoadBalancer Service (Port 80)               │   │
│  │  Routes traffic to deployment pods                   │   │
│  └────────┬─────────────────────────────────────────────┘   │
│           │                                                   │
│  ┌────────▼──────────────────────────────────────────────┐   │
│  │       Deployment (card-signal-board-api)              │   │
│  │  Rolling Updates | 3 Replicas | Zero-downtime        │   │
│  └────────┬──────────────────────────────────────────────┘   │
│           │                                                   │
│  ┌────────┴──────────────┬─────────────────┬──────────────┐  │
│  │                       │                 │              │  │
│  ▼                       ▼                 ▼              ▼  │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│ │   Pod #1     │  │   Pod #2     │  │   Pod #3     │        │
│ │              │  │              │  │              │        │
│ │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │        │
│ │ │ FastAPI  │ │  │ │ FastAPI  │ │  │ │ FastAPI  │ │        │
│ │ │ Uvicorn  │ │  │ │ Uvicorn  │ │  │ │ Uvicorn  │ │        │
│ │ │:8000     │ │  │ │:8000     │ │  │ │:8000     │ │        │
│ │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │        │
│ │              │  │              │  │              │        │
│ │ Health: ✓    │  │ Health: ✓    │  │ Health: ✓    │        │
│ │ CPU: 100m    │  │ CPU: 100m    │  │ CPU: 100m    │        │
│ │ RAM: 64Mi    │  │ RAM: 64Mi    │  │ RAM: 64Mi    │        │
│ └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ HorizontalPodAutoscaler (2-10 replicas)              │   │
│  │ Scales based on: CPU 70% | Memory 80%                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ConfigMap (card-signal-board-config)                 │   │
│  │ • LOG_LEVEL=INFO                                      │   │
│  │ • PYTHONUNBUFFERED=1                                  │   │
│  │ • ENVIRONMENT=production                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## CI/CD Pipeline Flow

```
┌──────────────────────────────────────────────────────────────┐
│              GitHub Push / Pull Request                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │                               │
         ▼                               ▼
    ┌─────────┐                   ┌──────────┐
    │ Push to │                   │Pull Req? │
    │ main    │                   │ Feedback │
    └────┬────┘                   └──────────┘
         │
    ┌────▼────────────────────────────────────────────┐
    │            PARALLEL JOBS                        │
    ├────────────────────────────────────────────────┤
    │                                                 │
    │ ┌──────────────────────────────────────────┐   │
    │ │ Test Job (pytest)                        │   │
    │ │ ✓ Run unit tests                         │   │
    │ │ ✓ Generate coverage report               │   │
    │ │ ✓ Upload to codecov                      │   │
    │ └──────────────────────────────────────────┘   │
    │                                                 │
    │ ┌──────────────────────────────────────────┐   │
    │ │ SAST Job (Bandit)                        │   │
    │ │ ✓ Static security analysis                │   │
    │ │ ✓ Detect vulnerabilities                 │   │
    │ │ ✓ Generate report                        │   │
    │ └──────────────────────────────────────────┘   │
    │                                                 │
    │ ┌──────────────────────────────────────────┐   │
    │ │ Lint Job (Black + flake8)                │   │
    │ │ ✓ Code formatting check                  │   │
    │ │ ✓ Style compliance                       │   │
    │ │ ✓ Code quality rules                     │   │
    │ └──────────────────────────────────────────┘   │
    │                                                 │
    │ ┌──────────────────────────────────────────┐   │
    │ │ Build Job (Docker buildx)                │   │
    │ │ ✓ Multi-platform build                   │   │
    │ │ ✓ Layer caching optimization             │   │
    │ │ ✓ Image tagging                          │   │
    │ └──────────────────────────────────────────┘   │
    │                                                 │
    │ ┌──────────────────────────────────────────┐   │
    │ │ Security Job (Trivy)                     │   │
    │ │ ✓ Vulnerability scan                     │   │
    │ │ ✓ SARIF report upload                    │   │
    │ └──────────────────────────────────────────┘   │
    │                                                 │
    └────┬────────────────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────────────┐
    │        Report Job (Status Summary)             │
    ├────────────────────────────────────────────────┤
    │ Test Status: ✓/✗                               │
    │ SAST Status: ✓/✗                               │
    │ Lint Status: ✓/✗                               │
    │ Build Status: ✓/✗/Skipped                      │
    │ Security Status: ✓/✗                           │
    │                                                 │
    │ Success: Merge to main & push Docker image    │
    │ Failure: Block merge, require fixes            │
    └────────────────────────────────────────────────┘
```

## Docker Multi-Stage Build

```
┌─────────────────────────────────────────────────────────┐
│                   Dockerfile                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  BUILDER STAGE                                 │    │
│  │                                                 │    │
│  │ FROM python:3.10-slim as builder               │    │
│  │ • Installs pip packages                        │    │
│  │ • Compiles dependencies                        │    │
│  │ • Creates /root/.local with site-packages      │    │
│  │ • Size: ~500MB (includes build tools)          │    │
│  └────────────────────────────────────────────────┘    │
│           │                                             │
│           │ COPY only /root/.local                      │
│           │                                             │
│  ┌────────▼────────────────────────────────────────┐   │
│  │  RUNTIME STAGE                                  │   │
│  │                                                 │    │
│  │ FROM python:3.10-slim                          │    │
│  │ • Minimal base image                           │    │
│  │ • Copy precompiled dependencies                │    │
│  │ • Copy application code                        │    │
│  │ • Set non-root user (uvicorn:1000)             │    │
│  │ • Expose port 8000                             │    │
│  │ • Health check /health endpoint                │    │
│  │ • Size: ~200MB (only runtime)                  │    │
│  │                                                 │    │
│  │ Final Image: card-signal-board:latest          │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘

Benefits:
✓ Smaller final image (60% reduction)
✓ Faster builds (cached layers)
✓ Better security (no build tools in runtime)
✓ Faster startup time
```

## Application Request Flow

```
┌────────────────────────────────────────────────────────┐
│                HTTP Request                            │
│         POST /cards (Create Card)                      │
└────────────┬─────────────────────────────────────────┘
             │
    ┌────────▼────────────┐
    │ Uvicorn ASGI Server │
    │ (Port 8000)         │
    └────────┬────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ Request Logging Middleware                 │
    │ • Generate unique 8-char request ID        │
    │ • Record request timestamp                 │
    │ • Log method, path, query params           │
    └────────┬────────────────────────────────────┘
             │
    ┌────────▼────────────────────────────────────┐
    │ FastAPI Route Handler                      │
    │ @app.post("/cards")                        │
    │                                             │
    │ • Validate request with Pydantic          │
    │ • Check email format                       │
    │ • Validate required fields                 │
    └────────┬────────────────────────────────────┘
             │
         ┌───┴───────────────────────┐
         │ Validation Result         │
         ├───────────┬───────────────┤
         │           │               │
    ┌────▼──┐   ┌───▼──┐     ┌──────▼──┐
    │ Valid │   │Error │     │Success? │
    └────┬──┘   └──┬───┘     └────┬────┘
         │         │              │
         │    ┌────▼─────┐        │
         │    │ Return   │        │
         │    │ 422 Error│        │
         │    └──────────┘        │
         │                        │
    ┌────▼─────────────────────────────────┐
    │ Generate Token (UUID)                │
    │ Create Card Record                   │
    │ Store in In-Memory Dictionary        │
    │ Set TTL: 7 days from creation        │
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │ Update Metrics                        │
    │ • Increment REQUEST_COUNT             │
    │ • Record response time to RESPONSE_TIME│
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │ Structured Logging                    │
    │ Log: {                                │
    │   "request_id": "abc12345",            │
    │   "timestamp": "2026-01-14T...",       │
    │   "method": "POST",                    │
    │   "path": "/cards",                    │
    │   "status": 201,                       │
    │   "response_time_ms": 45               │
    │ }                                      │
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │ HTTP Response (201 Created)            │
    │ {                                      │
    │   "id": "card-uuid",                   │
    │   "email": "user@example.com",         │
    │   "content": "Test card",              │
    │   "token": "token-uuid",               │
    │   "created_at": "2026-01-14T...",      │
    │   "expires_at": "2026-01-21T..."       │
    │ }                                      │
    └────────────────────────────────────────┘
```

## Kubernetes Deployment Lifecycle

```
┌─────────────────────────────────────────────────────┐
│  kubectl apply -f k8s/deployment.yaml               │
└────────────────┬────────────────────────────────────┘
                 │
    ┌────────────▼──────────────┐
    │ Deployment Created         │
    │ (3 replicas desired)       │
    └────────────┬───────────────┘
                 │
    ┌────────────▼─────────────────────────┐
    │ ReplicaSet Created                   │
    │ (Manages pod replicas)                │
    └────────────┬────────────────────────┘
                 │
    ┌────────────▼─────────────────────────────────────┐
    │ 3 Pods Scheduled (Pending)                       │
    │                                                   │
    │ ┌──────────┬──────────┬──────────┐              │
    │ │ Pod 1    │ Pod 2    │ Pod 3    │              │
    │ │ Pending  │ Pending  │ Pending  │              │
    │ └──────────┴──────────┴──────────┘              │
    └────────────┬─────────────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────┐
    │ Container Image Pulled & Started               │
    │ • Initialize container                        │
    │ • Mount volumes                                │
    │ • Set environment variables                    │
    │ • Execute entrypoint                           │
    └────────────┬─────────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────┐
    │ Initial Delay: 10 seconds                      │
    │ (Wait for app startup)                        │
    └────────────┬─────────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────┐
    │ Liveness Probe (Every 10s)                     │
    │ HTTP GET /health                               │
    │ Status: 200 OK ✓                               │
    │ (Pod is alive, restart if fails)              │
    └────────────┬─────────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────┐
    │ Readiness Probe (Every 5s)                     │
    │ HTTP GET /health                               │
    │ Status: 200 OK ✓                               │
    │ (Pod ready to receive traffic)                │
    └────────────┬─────────────────────────────────┘
                 │
    ┌────────────▼──────────────────────────────────┐
    │ ┌──────────┬──────────┬──────────┐            │
    │ │ Pod 1    │ Pod 2    │ Pod 3    │            │
    │ │ Running  │ Running  │ Running  │            │
    │ │ Ready ✓  │ Ready ✓  │ Ready ✓  │            │
    │ └──────────┴──────────┴──────────┘            │
    │                                                │
    │ Service Load Balancing ✓                       │
    └────────────────────────────────────────────────┘
```

## Helm Chart Deployment

```
┌───────────────────────────────────────────────────────┐
│  helm install csb ./helm/card-signal-board            │
│  -f values-prod.yaml                                  │
│  -n production                                        │
└────────────┬──────────────────────────────────────────┘
             │
    ┌────────▼──────────────────────┐
    │ Helm Template Rendering        │
    │                                │
    │ • Load Chart.yaml              │
    │ • Load values.yaml             │
    │ • Load values-prod.yaml        │
    │ • Merge configurations         │
    └────────┬──────────────────────┘
             │
    ┌────────▼─────────────────────────────────────┐
    │ Template Processing (_helpers.tpl)            │
    │                                               │
    │ • Generate labels (app, version, instance)   │
    │ • Create resource names                      │
    │ • Apply Helm functions (toYaml, include)     │
    └────────┬─────────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────────┐
    │ Kubernetes Manifests Generated                │
    │                                               │
    │ ✓ namespace.yaml                              │
    │ ✓ serviceaccount.yaml                         │
    │ ✓ configmap.yaml (from env vars)             │
    │ ✓ deployment.yaml (5 replicas, prod values)  │
    │ ✓ service.yaml (LoadBalancer)                │
    │ ✓ hpa.yaml (5-20 replicas)                   │
    └────────┬──────────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────────┐
    │ Apply to Kubernetes Cluster                   │
    │                                               │
    │ kubectl apply -f <generated-manifests>       │
    └────────┬──────────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────────┐
    │ Deployment Complete                           │
    │                                               │
    │ Release Name: csb                             │
    │ Namespace: production                         │
    │ Replicas: 5 (starting)                        │
    │ Status: Deployed ✓                            │
    │                                               │
    │ Commands:                                     │
    │ helm status csb -n production                 │
    │ helm upgrade csb ... (modify values)          │
    │ helm rollback csb 1 (revert)                  │
    └────────────────────────────────────────────────┘
```

## Observability Stack

```
┌──────────────────────────────────────────────────────┐
│              Application Pod                         │
│                                                      │
│ ┌────────────────────────────────────────────────┐  │
│ │          FastAPI Application                   │  │
│ │  (Card Signal Board API)                       │  │
│ └────┬──────────────────┬───────────────┬────────┘  │
│      │                  │               │            │
│      │ Metrics          │ Logs          │ Health     │
│      │ Prometheus       │ Structured    │ Endpoint   │
│      │ Format          │ JSON/Text     │ /health    │
│      │                  │               │            │
└──────┼──────────────────┼───────────────┼────────────┘
       │                  │               │
       │                  │               │
   ┌───▼──────┐   ┌──────▼──────┐  ┌────▼─────┐
   │Prometheus│   │  Log Sink   │  │Readiness │
   │/metrics  │   │  (stdout)   │  │Probe     │
   │          │   │             │  │          │
   │ Scrapes  │   │ Stored in:  │  │Checked:  │
   │ every:   │   │ - Log files │  │- K8s     │
   │ 30s      │   │ - Logstash  │  │- Cloud   │
   │          │   │ - CloudWatch│  │monitoring│
   └───┬──────┘   └─────────────┘  └──────────┘
       │
   ┌───▼──────────────────────────────────┐
   │ Grafana Dashboards                   │
   │ (Visualize metrics in real-time)     │
   │                                      │
   │ • Request Rate                       │
   │ • Response Time (latency)            │
   │ • Error Rate (5xx/4xx)               │
   │ • Pod CPU/Memory Usage               │
   │ • Request by Endpoint                │
   └──────────────────────────────────────┘
```

This reference guide complements the LaTeX report with ASCII diagrams showing data flows and architecture.
