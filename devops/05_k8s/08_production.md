# Production Best Practices

## High Availability

### Control Plane HA

- **Multiple API servers** behind load balancer
- **etcd cluster** with odd number of nodes (3, 5, 7)
- **Multiple controller managers** (leader election)
- **Multiple schedulers** (leader election)

```yaml
# etcd cluster example
apiVersion: v1
kind: Pod
metadata:
  name: etcd-1
spec:
  containers:
  - name: etcd
    image: k8s.gcr.io/etcd:3.5.0
    command:
    - etcd
    - --name=etcd-1
    - --initial-advertise-peer-urls=http://etcd-1:2380
    - --listen-peer-urls=http://0.0.0.0:2380
    - --listen-client-urls=http://0.0.0.0:2379
    - --advertise-client-urls=http://etcd-1:2379
    - --initial-cluster=etcd-1=http://etcd-1:2380,etcd-2=http://etcd-2:2380,etcd-3=http://etcd-3:2380
    - --initial-cluster-state=new
```

### Worker Node HA

- **Multiple worker nodes** across availability zones
- **Node auto-scaling** based on load
- **Pod anti-affinity** to spread across nodes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - web
            topologyKey: kubernetes.io/hostname
      
      containers:
      - name: web
        image: myapp:1.0
```

## Scaling

### Horizontal Pod Autoscaler (HPA)

Automatically scales pods based on metrics.

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  
  minReplicas: 2
  maxReplicas: 10
  
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 15
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

```bash
# Create HPA
kubectl autoscale deployment web-app --cpu-percent=70 --min=2 --max=10

# View HPA
kubectl get hpa

# Describe HPA
kubectl describe hpa web-hpa
```

### Custom Metrics HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: custom-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  
  minReplicas: 2
  maxReplicas: 10
  
  metrics:
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
```

### Vertical Pod Autoscaler (VPA)

Automatically adjusts CPU and memory requests/limits.

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  
  updatePolicy:
    updateMode: "Auto"  # Auto, Recreate, Initial, Off
  
  resourcePolicy:
    containerPolicies:
    - containerName: web
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2
        memory: 2Gi
```

### Cluster Autoscaler

Automatically adjusts cluster size.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      serviceAccountName: cluster-autoscaler
      containers:
      - name: cluster-autoscaler
        image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.24.0
        command:
        - ./cluster-autoscaler
        - --cloud-provider=aws
        - --namespace=kube-system
        - --nodes=2:10:worker-nodes
        - --scale-down-enabled=true
        - --scale-down-delay-after-add=10m
        - --scale-down-unneeded-time=10m
```

## Resource Management

### Resource Requests and Limits

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: resource-demo
spec:
  containers:
  - name: app
    image: myapp:1.0
    resources:
      requests:
        memory: "256Mi"
        cpu: "500m"
      limits:
        memory: "512Mi"
        cpu: "1000m"
```

### LimitRange

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: limit-range
  namespace: production
spec:
  limits:
  - max:
      cpu: "4"
      memory: 4Gi
    min:
      cpu: "100m"
      memory: 128Mi
    default:
      cpu: "500m"
      memory: 512Mi
    defaultRequest:
      cpu: "250m"
      memory: 256Mi
    type: Container
```

### ResourceQuota

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: production
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    pods: "100"
    services: "50"
    persistentvolumeclaims: "50"
```

## Pod Disruption Budgets

Ensure minimum availability during voluntary disruptions.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
spec:
  minAvailable: 2  # Or use maxUnavailable: 1
  selector:
    matchLabels:
      app: web
```

```yaml
# Percentage-based
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: web-pdb
spec:
  maxUnavailable: 25%
  selector:
    matchLabels:
      app: web
```

## Deployment Strategies

### Rolling Update

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rolling-update
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 2        # Max pods above desired
      maxUnavailable: 1  # Max pods unavailable
  
  template:
    spec:
      containers:
      - name: app
        image: myapp:2.0
```

### Blue-Green Deployment

```yaml
# Blue deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: blue
  template:
    metadata:
      labels:
        app: myapp
        version: blue
    spec:
      containers:
      - name: app
        image: myapp:1.0

---
# Green deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      version: green
  template:
    metadata:
      labels:
        app: myapp
        version: green
    spec:
      containers:
      - name: app
        image: myapp:2.0

---
# Service (switch selector to change version)
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
    version: blue  # Change to 'green' to switch
  ports:
  - port: 80
```

### Canary Deployment

```yaml
# Stable deployment (90%)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
      track: stable
  template:
    metadata:
      labels:
        app: myapp
        track: stable
    spec:
      containers:
      - name: app
        image: myapp:1.0

---
# Canary deployment (10%)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      track: canary
  template:
    metadata:
      labels:
        app: myapp
        track: canary
    spec:
      containers:
      - name: app
        image: myapp:2.0

---
# Service (routes to both)
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp  # Matches both stable and canary
  ports:
  - port: 80
```

## GitOps

### ArgoCD

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  
  source:
    repoURL: https://github.com/myorg/myapp
    targetRevision: HEAD
    path: k8s
  
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

### Flux

```yaml
apiVersion: source.toolkit.fluxcd.io/v1beta2
kind: GitRepository
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 1m
  url: https://github.com/myorg/myapp
  ref:
    branch: main

---
apiVersion: kustomize.toolkit.fluxcd.io/v1beta2
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: myapp
  path: ./k8s
  prune: true
  targetNamespace: production
```

## Backup and Disaster Recovery

### Velero

```bash
# Install Velero
velero install \
  --provider aws \
  --bucket my-backup-bucket \
  --secret-file ./credentials-velero

# Backup namespace
velero backup create my-backup --include-namespaces production

# Backup with label selector
velero backup create app-backup --selector app=myapp

# Schedule backups
velero schedule create daily-backup --schedule="0 2 * * *"

# Restore
velero restore create --from-backup my-backup

# List backups
velero backup get
```

### etcd Backup

```bash
# Backup etcd
ETCDCTL_API=3 etcdctl snapshot save snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify backup
ETCDCTL_API=3 etcdctl snapshot status snapshot.db

# Restore etcd
ETCDCTL_API=3 etcdctl snapshot restore snapshot.db \
  --data-dir=/var/lib/etcd-restore
```

## Multi-Tenancy

### Namespace Isolation

```yaml
# Namespace with quotas and limits
apiVersion: v1
kind: Namespace
metadata:
  name: tenant-a
  labels:
    tenant: a

---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-a-quota
  namespace: tenant-a
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    pods: "20"

---
apiVersion: v1
kind: LimitRange
metadata:
  name: tenant-a-limits
  namespace: tenant-a
spec:
  limits:
  - max:
      cpu: "2"
      memory: 2Gi
    min:
      cpu: "100m"
      memory: 128Mi
    type: Container

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-from-other-namespaces
  namespace: tenant-a
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}
```

## Production Checklist

### Cluster Setup
- [ ] Multi-master setup for HA
- [ ] etcd cluster with backups
- [ ] Multiple worker nodes across AZs
- [ ] Cluster autoscaler configured
- [ ] Network plugin installed (Calico, Cilium)
- [ ] Storage classes configured
- [ ] Ingress controller deployed

### Security
- [ ] RBAC enabled and configured
- [ ] Pod Security Standards enforced
- [ ] Network Policies implemented
- [ ] Secrets encrypted at rest
- [ ] Image scanning enabled
- [ ] Audit logging enabled
- [ ] Regular security updates

### Observability
- [ ] Metrics Server deployed
- [ ] Prometheus and Grafana setup
- [ ] Centralized logging (EFK/Loki)
- [ ] Distributed tracing (Jaeger)
- [ ] Alerts configured
- [ ] Dashboards created

### Reliability
- [ ] Resource requests/limits set
- [ ] Health probes configured
- [ ] Pod Disruption Budgets defined
- [ ] HPA configured
- [ ] Multiple replicas for critical apps
- [ ] Anti-affinity rules set

### Operations
- [ ] GitOps workflow (ArgoCD/Flux)
- [ ] CI/CD pipelines
- [ ] Backup strategy (Velero)
- [ ] Disaster recovery plan
- [ ] Runbooks documented
- [ ] On-call rotation

## Best Practices

### Configuration
1. **Use namespaces** for logical separation
2. **Set resource requests and limits** for all containers
3. **Use ConfigMaps and Secrets** for configuration
4. **Version control** all manifests
5. **Use labels** consistently

### Deployment
1. **Use Deployments** instead of bare Pods
2. **Implement health probes** (startup, liveness, readiness)
3. **Set Pod Disruption Budgets**
4. **Use rolling updates** with appropriate maxSurge/maxUnavailable
5. **Test in staging** before production

### Security
1. **Run as non-root** user
2. **Use read-only root filesystem**
3. **Drop all capabilities** and add only required
4. **Implement Network Policies**
5. **Scan images** for vulnerabilities
6. **Rotate secrets** regularly

### Scaling
1. **Configure HPA** for variable load
2. **Use VPA** for right-sizing
3. **Enable cluster autoscaler**
4. **Monitor resource usage**
5. **Set appropriate replica counts**

### Monitoring
1. **Collect metrics** (Prometheus)
2. **Centralize logs** (EFK/Loki)
3. **Set up alerts** for critical conditions
4. **Create dashboards** (Grafana)
5. **Implement distributed tracing**

### Backup
1. **Backup etcd** regularly
2. **Use Velero** for cluster backups
3. **Test restore procedures**
4. **Store backups** off-cluster
5. **Document recovery process**

## Performance Optimization

### Node Optimization
- Use appropriate instance types
- Enable node auto-scaling
- Use local SSD for high I/O workloads
- Configure kernel parameters

### Pod Optimization
- Set appropriate resource requests/limits
- Use init containers for setup
- Implement caching strategies
- Optimize container images

### Network Optimization
- Use service mesh for advanced routing
- Implement connection pooling
- Use CDN for static content
- Enable HTTP/2 and gRPC

### Storage Optimization
- Use appropriate storage classes
- Enable volume expansion
- Implement caching layers
- Use local volumes for performance

## Cost Optimization

1. **Right-size resources** using VPA
2. **Use spot/preemptible instances** for non-critical workloads
3. **Implement cluster autoscaler** to scale down
4. **Use namespace quotas** to prevent overuse
5. **Monitor and optimize** storage usage
6. **Use reserved instances** for predictable workloads
7. **Clean up unused resources** regularly

## Key Takeaways

- High availability requires redundancy at all levels
- Implement autoscaling (HPA, VPA, Cluster Autoscaler)
- Use Pod Disruption Budgets for reliability
- GitOps provides declarative, version-controlled deployments
- Regular backups and tested disaster recovery are essential
- Security, observability, and resource management are critical
- Follow production checklist before going live
- Continuous monitoring and optimization are necessary
