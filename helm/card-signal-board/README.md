# Helm Chart for Card Signal Board

A Helm chart for deploying the Card Signal Board API to Kubernetes with production-ready configurations, auto-scaling, and observability.

## Quick Start

### Prerequisites
- Kubernetes 1.20+
- Helm 3.0+
- Docker image available (local or registry)

### Install Chart

```bash
# Using default values
helm install card-signal-board ./helm/card-signal-board -n card-signal-board --create-namespace

# Using custom values
helm install card-signal-board ./helm/card-signal-board \
  -f values-prod.yaml \
  -n card-signal-board

# Dry-run (preview generated manifests)
helm install card-signal-board ./helm/card-signal-board --dry-run --debug
```

### Verify Installation

```bash
# Check deployment
helm list -n card-signal-board
helm status card-signal-board -n card-signal-board

# Check pods
kubectl get pods -n card-signal-board
kubectl logs -f -n card-signal-board -l app.kubernetes.io/name=card-signal-board
```

### Access Application

```bash
# Get service endpoint
kubectl get svc -n card-signal-board

# Port forward (if using ClusterIP)
kubectl port-forward svc/card-signal-board 8000:80 -n card-signal-board

# Test API
curl http://localhost:8000/health
curl http://localhost:8000/cards
```

## Customization

### Override Values

Create a custom `values.yaml`:

```yaml
# values-prod.yaml
replicaCount: 5

image:
  repository: myregistry.azurecr.io/card-signal-board
  tag: v1.0.0

service:
  type: LoadBalancer
  port: 80

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20

resources:
  limits:
    cpu: 1000m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 128Mi
```

Install with custom values:

```bash
helm install card-signal-board ./helm/card-signal-board -f values-prod.yaml -n production --create-namespace
```

### Common Customizations

**Change service type to ClusterIP (internal):**
```bash
helm install card-signal-board ./helm/card-signal-board \
  --set service.type=ClusterIP \
  -n card-signal-board
```

**Enable Ingress:**
```bash
helm install card-signal-board ./helm/card-signal-board \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=api.example.com \
  -n card-signal-board
```

**Disable auto-scaling and set replicas:**
```bash
helm install card-signal-board ./helm/card-signal-board \
  --set autoscaling.enabled=false \
  --set replicaCount=5 \
  -n card-signal-board
```

**Update container image for new deployment:**
```bash
helm upgrade card-signal-board ./helm/card-signal-board \
  --set image.tag=v1.0.0 \
  -n card-signal-board
```

## Helm Commands Reference

### Install
```bash
helm install <RELEASE_NAME> <CHART_PATH> [OPTIONS]
```

### Upgrade
```bash
helm upgrade <RELEASE_NAME> <CHART_PATH> -f values.yaml
```

### Uninstall
```bash
helm uninstall <RELEASE_NAME> -n <NAMESPACE>
```

### Dry-run
```bash
helm install <RELEASE_NAME> <CHART_PATH> --dry-run --debug
```

### Template validation
```bash
helm template <RELEASE_NAME> <CHART_PATH> -f values.yaml
```

### Get release info
```bash
helm get all <RELEASE_NAME> -n <NAMESPACE>
helm get values <RELEASE_NAME> -n <NAMESPACE>
```

## Chart Structure

```
helm/card-signal-board/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default values
├── templates/
│   ├── _helpers.tpl        # Template helpers
│   ├── namespace.yaml       # Namespace resource
│   ├── serviceaccount.yaml  # ServiceAccount
│   ├── configmap.yaml       # ConfigMap
│   ├── deployment.yaml      # Deployment
│   ├── service.yaml         # Service
│   └── hpa.yaml            # HorizontalPodAutoscaler
└── README.md               # This file
```

## Configuration Values

| Key | Default | Description |
|-----|---------|-------------|
| `replicaCount` | `3` | Number of pod replicas |
| `image.repository` | `card-signal-board` | Docker image name |
| `image.tag` | `latest` | Docker image tag |
| `image.pullPolicy` | `IfNotPresent` | Image pull policy |
| `service.type` | `LoadBalancer` | Kubernetes service type |
| `service.port` | `80` | Service port |
| `autoscaling.enabled` | `true` | Enable HPA |
| `autoscaling.minReplicas` | `2` | Minimum replicas |
| `autoscaling.maxReplicas` | `10` | Maximum replicas |
| `resources.requests.cpu` | `100m` | CPU request |
| `resources.requests.memory` | `64Mi` | Memory request |
| `resources.limits.cpu` | `500m` | CPU limit |
| `resources.limits.memory` | `256Mi` | Memory limit |

## Deployment Examples

### Development (Single Replica)
```bash
helm install card-signal-board ./helm/card-signal-board \
  --set replicaCount=1 \
  --set autoscaling.enabled=false \
  --set service.type=ClusterIP \
  -n development
```

### Staging (3 Replicas, Auto-scale 2-10)
```bash
helm install card-signal-board ./helm/card-signal-board \
  --set replicaCount=3 \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10 \
  -n staging
```

### Production (5 Replicas, Auto-scale 5-20, High Resources)
```bash
helm install card-signal-board ./helm/card-signal-board \
  --set replicaCount=5 \
  --set autoscaling.minReplicas=5 \
  --set autoscaling.maxReplicas=20 \
  --set resources.requests.cpu=250m \
  --set resources.requests.memory=256Mi \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=512Mi \
  -n production
```

## Troubleshooting

### Check template syntax
```bash
helm lint ./helm/card-signal-board
helm template card-signal-board ./helm/card-signal-board
```

### Debug values
```bash
helm get values card-signal-board -n card-signal-board
```

### View generated manifests
```bash
helm get manifest card-signal-board -n card-signal-board
```

### Check deployment status
```bash
kubectl describe deployment card-signal-board-card-signal-board -n card-signal-board
kubectl logs -f -n card-signal-board -l app.kubernetes.io/name=card-signal-board
```

## Cleanup

```bash
helm uninstall card-signal-board -n card-signal-board
kubectl delete namespace card-signal-board
```
