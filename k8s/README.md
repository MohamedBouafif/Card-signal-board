# Kubernetes Deployment Guide

## Overview
This directory contains Kubernetes manifests for deploying the Card Signal Board API to a Kubernetes cluster.

## Files

### namespace.yaml
Creates an isolated namespace `card-signal-board` for all resources.

### deployment.yaml
Deploys the Card Signal Board API with:
- 3 replicas for high availability
- Rolling update strategy
- Health checks (liveness & readiness)
- Resource requests and limits
- Security context (non-root user, read-only filesystem)
- Prometheus metrics scraping annotations
- Graceful shutdown (30s termination period)

### service.yaml
Exposes the API with:
- LoadBalancer type (change to ClusterIP for internal access)
- Port 80 routing to container port 8000
- Service discovery via DNS

### configmap.yaml
Provides environment configuration:
- Log level
- Python unbuffered output
- Environment designation

### hpa.yaml
Horizontal Pod Autoscaler for automatic scaling:
- Scales 2-10 replicas based on CPU (70%) and memory (80%) utilization
- Conservative scale-down (5min stability window)
- Aggressive scale-up (1min stability window)

## Deployment Instructions

### Prerequisites
- Kubernetes cluster (1.20+)
- kubectl configured
- Docker image built and available (or update image in deployment.yaml)

### Deploy to Minikube (Local Development)

```bash
# Build image locally
docker build -t card-signal-board:latest .

# Load image into minikube
minikube image load card-signal-board:latest

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy all resources
kubectl apply -f k8s/

# Verify deployment
kubectl get deployments -n card-signal-board
kubectl get pods -n card-signal-board
kubectl get svc -n card-signal-board

# Get service IP (for minikube, use this instead of EXTERNAL-IP)
minikube service card-signal-board-api -n card-signal-board
```

### Deploy to Cloud (AWS/Azure/GCP)

```bash
# Push image to registry
docker tag card-signal-board:latest your-registry.azurecr.io/card-signal-board:latest
docker push your-registry.azurecr.io/card-signal-board:latest

# Update image in deployment.yaml
sed -i 's|card-signal-board:latest|your-registry.azurecr.io/card-signal-board:latest|' k8s/deployment.yaml

# Apply manifests
kubectl apply -f k8s/

# Check EXTERNAL-IP
kubectl get svc -n card-signal-board
```

## Verification

### Check Pod Status
```bash
kubectl get pods -n card-signal-board -w
kubectl logs -f -n card-signal-board -l app=card-signal-board
```

### Test API
```bash
# Get service IP/endpoint
kubectl get svc -n card-signal-board

# Create card
curl -X POST http://<SERVICE_IP>/cards \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "content": "Test card"}'

# List cards
curl http://<SERVICE_IP>/cards

# Check metrics
curl http://<SERVICE_IP>/metrics

# Check health
curl http://<SERVICE_IP>/health
```

### Monitor with Prometheus
The deployment includes Prometheus annotations. Scrape metrics from `/metrics` endpoint:

```bash
kubectl port-forward svc/card-signal-board-api 8000:80 -n card-signal-board
curl http://localhost:8000/metrics
```

## Cleanup

```bash
# Delete all resources in namespace
kubectl delete namespace card-signal-board

# Or delete individual resources
kubectl delete -f k8s/
```

## Architecture Notes

- **High Availability**: 3 replicas with rolling updates
- **Auto-scaling**: HPA adjusts replicas 2-10 based on metrics
- **Security**: Non-root user, read-only filesystem, dropped capabilities
- **Observability**: Prometheus metrics, structured logging, health checks
- **Resource Efficiency**: CPU 100m/500m, Memory 64Mi/256Mi per pod

## Customization

### Change Replica Count
Edit `deployment.yaml`:
```yaml
spec:
  replicas: 5  # Change from 3
```

### Change Service Type
For internal access, edit `service.yaml`:
```yaml
spec:
  type: ClusterIP  # Instead of LoadBalancer
```

### Update Container Image
```bash
kubectl set image deployment/card-signal-board-api \
  api=your-registry.azurecr.io/card-signal-board:v1.0.0 \
  -n card-signal-board
```

### Scale Manually
```bash
kubectl scale deployment card-signal-board-api --replicas=5 -n card-signal-board
```
