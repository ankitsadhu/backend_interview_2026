# Kubernetes Interview Questions

## Fundamentals

### Q1: What is Kubernetes and why is it used?
**Answer:** Kubernetes is an open-source container orchestration platform that automates deployment, scaling, and management of containerized applications. It's used for:
- Automated rollouts and rollbacks
- Self-healing (restarts failed containers)
- Horizontal scaling
- Service discovery and load balancing
- Storage orchestration
- Secret and configuration management

### Q2: Explain Kubernetes architecture
**Answer:** Kubernetes has two main components:

**Control Plane:**
- API Server: Front-end for Kubernetes, exposes REST API
- etcd: Key-value store for cluster data
- Scheduler: Assigns pods to nodes
- Controller Manager: Runs controller processes
- Cloud Controller Manager: Interacts with cloud providers

**Worker Nodes:**
- Kubelet: Agent ensuring containers are running
- Kube-proxy: Network proxy maintaining network rules
- Container Runtime: Runs containers (containerd, CRI-O)

### Q3: What is a Pod?
**Answer:** A Pod is the smallest deployable unit in Kubernetes. It represents a single instance of a running process and can contain one or more containers that share:
- Network namespace (same IP address)
- Storage volumes
- Lifecycle

Pods are ephemeral and should be managed by controllers (Deployments, StatefulSets).

### Q4: What's the difference between a Pod and a Container?
**Answer:**
- **Container:** Single running instance of an image
- **Pod:** Wrapper around one or more containers that share resources
- Containers in a pod share network and can share volumes
- Pods are the unit of deployment in Kubernetes

### Q5: What are Namespaces?
**Answer:** Namespaces provide virtual clusters within a physical cluster, used for:
- Resource isolation between teams/projects
- Resource quota enforcement
- Access control via RBAC
- Logical separation of environments

Default namespaces: `default`, `kube-system`, `kube-public`, `kube-node-lease`

## Workloads

### Q6: Explain different types of workload controllers
**Answer:**

**Deployment:** Stateless applications, supports rolling updates
```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
```

**StatefulSet:** Stateful applications requiring stable identities
- Stable network identifiers (pod-0, pod-1)
- Persistent storage per pod
- Ordered deployment and scaling

**DaemonSet:** Runs one pod per node (logging, monitoring agents)

**Job:** One-time tasks that run to completion

**CronJob:** Scheduled jobs (backups, reports)

### Q7: What's the difference between Deployment and StatefulSet?
**Answer:**

**Deployment:**
- For stateless applications
- Pods are interchangeable
- Random pod names
- No guaranteed ordering
- Shared storage (if any)

**StatefulSet:**
- For stateful applications
- Pods have unique identities
- Predictable names (app-0, app-1)
- Ordered deployment/scaling
- Dedicated persistent storage per pod

### Q8: How does a ReplicaSet work?
**Answer:** ReplicaSet ensures a specified number of pod replicas are running at any time:
- Monitors pod count via label selectors
- Creates pods if count is below desired
- Deletes pods if count is above desired
- Usually managed by Deployments (don't create directly)

## Services and Networking

### Q9: What is a Service and why is it needed?
**Answer:** A Service provides stable networking for Pods:
- Pods have dynamic IPs that change on restart
- Service provides stable virtual IP (ClusterIP)
- Load balances traffic across pods
- Enables service discovery via DNS

### Q10: Explain different Service types
**Answer:**

**ClusterIP (default):** Internal cluster access only
```yaml
type: ClusterIP
```

**NodePort:** Exposes on each node's IP at static port (30000-32767)
```yaml
type: NodePort
nodePort: 30080
```

**LoadBalancer:** Cloud provider's load balancer
```yaml
type: LoadBalancer
```

**ExternalName:** Maps to external DNS name
```yaml
type: ExternalName
externalName: database.example.com
```

### Q11: What is Ingress?
**Answer:** Ingress manages external HTTP/HTTPS access to services:
- Single entry point for multiple services
- Host-based and path-based routing
- TLS termination
- Requires Ingress Controller (NGINX, Traefik)

```yaml
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /api
        backend:
          service:
            name: api-service
```

### Q12: How does service discovery work in Kubernetes?
**Answer:** Two methods:

**DNS (preferred):**
```bash
# Format: <service>.<namespace>.svc.cluster.local
curl backend-service.production.svc.cluster.local
```

**Environment Variables:**
```bash
BACKEND_SERVICE_HOST=10.0.0.1
BACKEND_SERVICE_PORT=80
```

### Q13: What are Network Policies?
**Answer:** Network Policies control traffic flow between pods:
- Namespace-scoped
- Define ingress/egress rules
- Use label selectors
- Require CNI plugin support (Calico, Cilium)

```yaml
spec:
  podSelector:
    matchLabels:
      app: backend
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
```

## Configuration and Storage

### Q14: What's the difference between ConfigMap and Secret?
**Answer:**

**ConfigMap:**
- Non-sensitive configuration data
- Stored as plain text
- Visible in kubectl describe

**Secret:**
- Sensitive data (passwords, tokens)
- Base64 encoded (not encrypted by default)
- Not shown in kubectl describe
- Can be encrypted at rest in etcd

### Q15: How do you use ConfigMaps and Secrets in Pods?
**Answer:** Three ways:

**Environment variables:**
```yaml
env:
- name: DB_HOST
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: database_url
```

**Volume mount:**
```yaml
volumes:
- name: config
  configMap:
    name: app-config
volumeMounts:
- name: config
  mountPath: /etc/config
```

**Command arguments:**
```yaml
command: ["$(DB_HOST)"]
```

### Q16: Explain Persistent Volumes (PV) and Persistent Volume Claims (PVC)
**Answer:**

**PV:** Cluster-level storage resource
- Provisioned by admin or dynamically
- Has capacity, access modes, reclaim policy
- Independent lifecycle from pods

**PVC:** Request for storage by user
- Specifies size and access mode
- Binds to suitable PV
- Used by pods

```yaml
# PVC
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### Q17: What are Storage Classes?
**Answer:** StorageClass defines storage types with different properties:
- Enables dynamic provisioning
- Specifies provisioner (AWS EBS, Azure Disk)
- Defines parameters (type, IOPS)
- Sets reclaim policy

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
```

## Security

### Q18: What is RBAC?
**Answer:** Role-Based Access Control defines who can do what:

**Role:** Namespace-scoped permissions
**ClusterRole:** Cluster-wide permissions
**RoleBinding:** Grants Role to subjects
**ClusterRoleBinding:** Grants ClusterRole to subjects

```yaml
# Role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]

# RoleBinding
subjects:
- kind: ServiceAccount
  name: my-sa
roleRef:
  kind: Role
  name: pod-reader
```

### Q19: What are Service Accounts?
**Answer:** Service Accounts provide identity for pods:
- Automatically created for each namespace
- Pods use SA to authenticate to API server
- Token mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token`
- Used with RBAC for authorization

```yaml
spec:
  serviceAccountName: my-service-account
```

### Q20: Explain Security Contexts
**Answer:** Security Contexts define privilege and access control:

**Pod level:**
```yaml
securityContext:
  runAsUser: 1000
  runAsGroup: 3000
  fsGroup: 2000
```

**Container level:**
```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

### Q21: What are Pod Security Standards?
**Answer:** Three levels of security policies:

**Privileged:** Unrestricted (default)
**Baseline:** Minimally restrictive
**Restricted:** Heavily restricted (best practice)

Applied via namespace labels:
```yaml
metadata:
  labels:
    pod-security.kubernetes.io/enforce: restricted
```

## Observability

### Q22: What are the three types of health probes?
**Answer:**

**Liveness Probe:** Is container running? Restart if fails
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
```

**Readiness Probe:** Is container ready for traffic? Remove from service if fails
```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
```

**Startup Probe:** Has container started? Disables other probes until succeeds
```yaml
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  failureThreshold: 30
```

### Q23: How do you debug a failing pod?
**Answer:**

```bash
# Check pod status
kubectl get pods
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# Execute commands
kubectl exec -it <pod-name> -- /bin/bash

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Debug with ephemeral container
kubectl debug <pod-name> -it --image=busybox
```

### Q24: How do you monitor Kubernetes clusters?
**Answer:**

**Metrics:**
- Metrics Server (basic resource metrics)
- Prometheus (comprehensive metrics)
- Grafana (visualization)

**Logging:**
- kubectl logs (basic)
- EFK Stack (Elasticsearch, Fluentd, Kibana)
- Loki + Grafana

**Tracing:**
- Jaeger
- OpenTelemetry

## Scaling and Updates

### Q25: Explain Horizontal Pod Autoscaler (HPA)
**Answer:** HPA automatically scales pods based on metrics:

```yaml
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

Requires Metrics Server. Can scale on:
- CPU/memory utilization
- Custom metrics (requests per second)
- External metrics

### Q26: What is a Pod Disruption Budget?
**Answer:** PDB ensures minimum availability during voluntary disruptions:

```yaml
spec:
  minAvailable: 2  # Or maxUnavailable: 1
  selector:
    matchLabels:
      app: web
```

Protects against:
- Node drains
- Cluster upgrades
- Voluntary evictions

Doesn't protect against:
- Node failures
- Pod crashes

### Q27: Explain different deployment strategies
**Answer:**

**Rolling Update:** Gradual replacement (default)
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 1
```

**Recreate:** Kill all, then create new
```yaml
strategy:
  type: Recreate
```

**Blue-Green:** Two identical environments, switch traffic

**Canary:** Gradual rollout to subset of users

### Q28: How do you rollback a deployment?
**Answer:**

```bash
# View rollout history
kubectl rollout history deployment/myapp

# Rollback to previous version
kubectl rollout undo deployment/myapp

# Rollback to specific revision
kubectl rollout undo deployment/myapp --to-revision=2

# Check rollout status
kubectl rollout status deployment/myapp
```

## Advanced Topics

### Q29: What is a StatefulSet and when would you use it?
**Answer:** StatefulSet manages stateful applications requiring:
- Stable, unique network identifiers
- Stable, persistent storage
- Ordered deployment and scaling
- Ordered rolling updates

**Use cases:**
- Databases (MySQL, PostgreSQL, MongoDB)
- Distributed systems (Kafka, Zookeeper, Cassandra)
- Applications requiring stable hostnames

### Q30: Explain Init Containers
**Answer:** Init Containers run before app containers:
- Run to completion sequentially
- Must succeed before app containers start
- Share volumes with app containers

**Use cases:**
- Wait for dependencies
- Setup tasks (database migrations)
- Clone git repositories
- Generate configuration

```yaml
initContainers:
- name: init-db
  image: busybox
  command: ['sh', '-c', 'until nslookup db; do sleep 2; done']
```

### Q31: What are Taints and Tolerations?
**Answer:**

**Taints:** Applied to nodes to repel pods
```bash
kubectl taint nodes node1 key=value:NoSchedule
```

**Tolerations:** Applied to pods to tolerate taints
```yaml
tolerations:
- key: "key"
  operator: "Equal"
  value: "value"
  effect: "NoSchedule"
```

**Effects:**
- `NoSchedule`: Don't schedule new pods
- `PreferNoSchedule`: Try not to schedule
- `NoExecute`: Evict existing pods

### Q32: What is Node Affinity?
**Answer:** Node Affinity attracts pods to nodes:

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: disktype
          operator: In
          values:
          - ssd
```

**Types:**
- `requiredDuringScheduling`: Hard requirement
- `preferredDuringScheduling`: Soft preference
- `IgnoredDuringExecution`: Don't evict if node changes

### Q33: What is Pod Affinity and Anti-Affinity?
**Answer:**

**Pod Affinity:** Schedule pods together
```yaml
podAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
  - labelSelector:
      matchLabels:
        app: cache
    topologyKey: kubernetes.io/hostname
```

**Pod Anti-Affinity:** Spread pods apart
```yaml
podAntiAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
  - labelSelector:
      matchLabels:
        app: web
    topologyKey: kubernetes.io/hostname
```

### Q34: What is a DaemonSet?
**Answer:** DaemonSet ensures all (or some) nodes run a copy of a pod:
- Automatically adds pods to new nodes
- Removes pods when nodes are removed
- Useful for node-level services

**Use cases:**
- Log collection (Fluentd)
- Monitoring agents (Prometheus Node Exporter)
- Storage daemons (Ceph, Gluster)
- Network plugins

### Q35: Explain Jobs and CronJobs
**Answer:**

**Job:** Runs pods to completion
```yaml
spec:
  completions: 5      # Run 5 times
  parallelism: 2      # 2 at a time
  backoffLimit: 4     # Retry 4 times
```

**CronJob:** Scheduled jobs
```yaml
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-tool
```

## Scenario-Based Questions

### Q36: How would you troubleshoot a pod stuck in Pending state?
**Answer:**

```bash
# Check pod details
kubectl describe pod <pod-name>

# Common causes:
# 1. Insufficient resources
kubectl top nodes
kubectl describe nodes

# 2. PVC not bound
kubectl get pvc

# 3. Node selector/affinity not matching
kubectl get nodes --show-labels

# 4. Taints preventing scheduling
kubectl describe nodes | grep Taints

# 5. Image pull issues
kubectl describe pod <pod-name> | grep -A 5 Events
```

### Q37: How would you handle a pod in CrashLoopBackOff?
**Answer:**

```bash
# View logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous

# Check events
kubectl describe pod <pod-name>

# Common causes:
# 1. Application error - check logs
# 2. Missing dependencies - check init containers
# 3. Liveness probe failing - adjust probe settings
# 4. Resource limits too low - increase limits
# 5. Configuration issues - check ConfigMaps/Secrets

# Debug interactively
kubectl debug <pod-name> -it --image=busybox --copy-to=debug-pod
```

### Q38: How would you implement zero-downtime deployments?
**Answer:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # Zero downtime
  
  template:
    spec:
      containers:
      - name: app
        image: myapp:2.0
        
        # Readiness probe
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        
        # Graceful shutdown
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]

---
# Pod Disruption Budget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: myapp
```

### Q39: How would you secure a Kubernetes cluster?
**Answer:**

1. **Enable RBAC** with least privilege
2. **Use Pod Security Standards** (restricted profile)
3. **Network Policies** for network segmentation
4. **Encrypt secrets** at rest in etcd
5. **Run containers as non-root**
6. **Use read-only root filesystem**
7. **Drop all capabilities**
8. **Scan images** for vulnerabilities
9. **Enable audit logging**
10. **Use private registries** with authentication
11. **Regular updates** of Kubernetes and dependencies
12. **Implement admission controllers**

### Q40: How would you optimize costs in Kubernetes?
**Answer:**

1. **Right-size resources** using VPA
2. **Use HPA** to scale down during low traffic
3. **Enable Cluster Autoscaler** to remove unused nodes
4. **Use spot/preemptible instances** for non-critical workloads
5. **Set resource quotas** per namespace
6. **Clean up unused resources** (PVCs, LoadBalancers)
7. **Use reserved instances** for predictable workloads
8. **Optimize storage** (delete old snapshots, use appropriate storage classes)
9. **Monitor and alert** on resource waste
10. **Use namespace quotas** to prevent overuse

## Key Takeaways

- Understand core concepts: Pods, Services, Deployments
- Know different workload controllers and when to use them
- Master RBAC and security best practices
- Understand networking (Services, Ingress, Network Policies)
- Know how to debug and troubleshoot common issues
- Understand scaling strategies (HPA, VPA, Cluster Autoscaler)
- Be familiar with production best practices
- Practice hands-on with real clusters
