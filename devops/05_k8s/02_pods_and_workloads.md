# Pods and Workloads

## Pods

### What is a Pod?
- Smallest deployable unit in Kubernetes
- Can contain one or more containers
- Shares network namespace (same IP, port space)
- Shares storage volumes
- Ephemeral by nature

### Single Container Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
```

### Multi-Container Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: multi-container-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
    volumeMounts:
    - name: shared-data
      mountPath: /usr/share/nginx/html
  
  - name: sidecar
    image: busybox
    command: ['sh', '-c', 'while true; do echo "$(date)" > /data/index.html; sleep 10; done']
    volumeMounts:
    - name: shared-data
      mountPath: /data
  
  volumes:
  - name: shared-data
    emptyDir: {}
```

### Pod Lifecycle

**Phases:**
- `Pending` - Accepted but not yet running
- `Running` - At least one container is running
- `Succeeded` - All containers terminated successfully
- `Failed` - All containers terminated, at least one failed
- `Unknown` - State cannot be determined

**Container States:**
- `Waiting` - Not yet running
- `Running` - Executing without issues
- `Terminated` - Finished execution

### Init Containers

Run before app containers, used for setup tasks.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: init-demo
spec:
  initContainers:
  - name: init-service
    image: busybox
    command: ['sh', '-c', 'until nslookup myservice; do echo waiting; sleep 2; done']
  
  containers:
  - name: main-app
    image: nginx:1.21
```

### Liveness and Readiness Probes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: probe-demo
spec:
  containers:
  - name: app
    image: myapp:1.0
    
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 3
      periodSeconds: 3
    
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
    
    startupProbe:
      httpGet:
        path: /startup
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
```

**Probe Types:**
- `httpGet` - HTTP GET request
- `tcpSocket` - TCP connection
- `exec` - Execute command in container

## ReplicaSet

Maintains a stable set of replica Pods running at any given time.

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-replicaset
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

**Note**: Rarely used directly. Use Deployments instead.

## Deployments

Provides declarative updates for Pods and ReplicaSets.

### Basic Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

### Deployment Strategies

#### 1. Rolling Update (Default)

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max pods above desired count
      maxUnavailable: 1  # Max pods unavailable during update
```

#### 2. Recreate

```yaml
spec:
  strategy:
    type: Recreate  # Kill all pods, then create new ones
```

### Deployment Operations

```bash
# Create deployment
kubectl create deployment nginx --image=nginx:1.21 --replicas=3

# Update image
kubectl set image deployment/nginx nginx=nginx:1.22

# Rollout status
kubectl rollout status deployment/nginx

# Rollout history
kubectl rollout history deployment/nginx

# Rollback to previous version
kubectl rollout undo deployment/nginx

# Rollback to specific revision
kubectl rollout undo deployment/nginx --to-revision=2

# Pause rollout
kubectl rollout pause deployment/nginx

# Resume rollout
kubectl rollout resume deployment/nginx

# Scale deployment
kubectl scale deployment/nginx --replicas=5

# Autoscale
kubectl autoscale deployment/nginx --min=2 --max=10 --cpu-percent=80
```

### Blue-Green Deployment Pattern

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
# Service (switch by changing selector)
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
    version: blue  # Change to 'green' to switch
  ports:
  - port: 80
```

## StatefulSets

For stateful applications requiring stable network identities and persistent storage.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: "password"
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

### StatefulSet Features
- Stable, unique network identifiers (pod-0, pod-1, pod-2)
- Stable, persistent storage
- Ordered, graceful deployment and scaling
- Ordered, automated rolling updates

```bash
# Scale StatefulSet
kubectl scale statefulset mysql --replicas=5

# Delete StatefulSet (keep PVCs)
kubectl delete statefulset mysql --cascade=orphan
```

## DaemonSets

Ensures all (or some) nodes run a copy of a Pod.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  labels:
    app: fluentd
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluentd:v1.14
        resources:
          limits:
            memory: 200Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
      
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
```

### Use Cases
- Log collection (Fluentd, Logstash)
- Monitoring agents (Prometheus Node Exporter)
- Storage daemons (Ceph, Gluster)
- Network plugins (Calico, Flannel)

### Node Selection

```yaml
spec:
  template:
    spec:
      nodeSelector:
        disktype: ssd
      
      # Or use affinity
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: kubernetes.io/os
                operator: In
                values:
                - linux
```

## Jobs

Creates one or more Pods and ensures a specified number complete successfully.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: pi-calculation
spec:
  completions: 5      # Run 5 times
  parallelism: 2      # Run 2 at a time
  backoffLimit: 4     # Retry 4 times on failure
  
  template:
    spec:
      containers:
      - name: pi
        image: perl:5.34
        command: ["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"]
      restartPolicy: Never
```

```bash
# Create job
kubectl create job hello --image=busybox -- echo "Hello World"

# View jobs
kubectl get jobs

# View job logs
kubectl logs job/pi-calculation

# Delete job
kubectl delete job pi-calculation
```

## CronJobs

Creates Jobs on a repeating schedule.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job
spec:
  schedule: "0 2 * * *"  # Every day at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: backup-tool:1.0
            command: ["/bin/sh", "-c", "backup.sh"]
          restartPolicy: OnFailure
  
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  concurrencyPolicy: Forbid  # Forbid, Allow, or Replace
```

### Cron Schedule Format
```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
# │ │ │ │ │
# * * * * *
```

Examples:
- `*/5 * * * *` - Every 5 minutes
- `0 */2 * * *` - Every 2 hours
- `0 0 * * 0` - Every Sunday at midnight

## Best Practices

1. **Always use Deployments** instead of bare Pods or ReplicaSets
2. **Set resource requests and limits** for all containers
3. **Use health probes** (liveness, readiness, startup)
4. **Use labels** for organization and selection
5. **Avoid latest tag** - use specific versions
6. **Use init containers** for setup tasks
7. **Set appropriate restart policies**
8. **Use StatefulSets** for stateful apps requiring stable identities
9. **Use DaemonSets** for node-level services
10. **Clean up completed Jobs** to avoid clutter

## Practice Exercises

### Exercise 1: Create and Scale Deployment
```bash
kubectl create deployment nginx --image=nginx:1.21 --replicas=3
kubectl get deployments
kubectl scale deployment nginx --replicas=5
kubectl get pods
```

### Exercise 2: Rolling Update
```bash
kubectl set image deployment/nginx nginx=nginx:1.22
kubectl rollout status deployment/nginx
kubectl rollout history deployment/nginx
kubectl rollout undo deployment/nginx
```

### Exercise 3: Create a Job
```bash
kubectl create job test --image=busybox -- echo "Hello K8s"
kubectl get jobs
kubectl logs job/test
kubectl delete job test
```

## Key Takeaways

- Pods are ephemeral; use controllers for reliability
- Deployments are the standard for stateless apps
- StatefulSets for stateful apps with stable identities
- DaemonSets for node-level services
- Jobs for one-time tasks, CronJobs for scheduled tasks
- Always use health probes and resource limits
