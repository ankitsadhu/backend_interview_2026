# Observability in Kubernetes

## The Three Pillars

1. **Logging** - What happened?
2. **Metrics** - How much/many?
3. **Tracing** - Where did it go?

## Logging

### Container Logs

```bash
# View logs
kubectl logs <pod-name>

# Follow logs
kubectl logs -f <pod-name>

# Previous container logs
kubectl logs <pod-name> --previous

# Multi-container pod
kubectl logs <pod-name> -c <container-name>

# Last N lines
kubectl logs <pod-name> --tail=100

# Since timestamp
kubectl logs <pod-name> --since=1h
kubectl logs <pod-name> --since-time=2024-01-01T00:00:00Z

# All pods with label
kubectl logs -l app=nginx

# Timestamps
kubectl logs <pod-name> --timestamps
```

### Logging Architecture

#### Node-Level Logging

Logs written to stdout/stderr are captured by container runtime.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: counter
spec:
  containers:
  - name: count
    image: busybox
    command: ['sh', '-c', 'i=0; while true; do echo "$i: $(date)"; i=$((i+1)); sleep 1; done']
```

#### Sidecar Pattern

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: counter-sidecar
spec:
  containers:
  # Application container
  - name: app
    image: busybox
    command: ['sh', '-c', 'while true; do echo "$(date) INFO app log" >> /var/log/app.log; sleep 1; done']
    volumeMounts:
    - name: logs
      mountPath: /var/log
  
  # Logging sidecar
  - name: log-shipper
    image: busybox
    command: ['sh', '-c', 'tail -f /var/log/app.log']
    volumeMounts:
    - name: logs
      mountPath: /var/log
  
  volumes:
  - name: logs
    emptyDir: {}
```

### Centralized Logging

#### EFK Stack (Elasticsearch, Fluentd, Kibana)

```yaml
# Fluentd DaemonSet
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      serviceAccountName: fluentd
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch.logging.svc.cluster.local"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

#### Loki Stack (Grafana Loki)

Lightweight alternative to EFK.

```yaml
# Promtail DaemonSet
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: promtail
spec:
  selector:
    matchLabels:
      app: promtail
  template:
    metadata:
      labels:
        app: promtail
    spec:
      containers:
      - name: promtail
        image: grafana/promtail:latest
        args:
        - -config.file=/etc/promtail/promtail.yaml
        volumeMounts:
        - name: config
          mountPath: /etc/promtail
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      
      volumes:
      - name: config
        configMap:
          name: promtail-config
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

### Structured Logging

```python
# Python example
import json
import logging

logger = logging.getLogger(__name__)

# Structured log
log_data = {
    "timestamp": "2024-01-01T12:00:00Z",
    "level": "INFO",
    "message": "User logged in",
    "user_id": "12345",
    "ip": "192.168.1.1"
}
print(json.dumps(log_data))
```

## Metrics

### Metrics Server

Collects resource metrics from Kubelets.

```bash
# Install Metrics Server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View node metrics
kubectl top nodes

# View pod metrics
kubectl top pods

# View pod metrics in namespace
kubectl top pods -n kube-system

# Sort by CPU
kubectl top pods --sort-by=cpu

# Sort by memory
kubectl top pods --sort-by=memory
```

### Prometheus

Industry-standard monitoring solution.

#### Prometheus Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: storage
          mountPath: /prometheus
      
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: storage
        emptyDir: {}
```

#### Prometheus Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    
    scrape_configs:
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
      
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

#### ServiceMonitor (Prometheus Operator)

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: app-monitor
spec:
  selector:
    matchLabels:
      app: myapp
  endpoints:
  - port: metrics
    interval: 30s
```

### Application Metrics

#### Exposing Metrics

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-metrics
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
spec:
  containers:
  - name: app
    image: myapp:1.0
    ports:
    - name: metrics
      containerPort: 8080
```

#### Custom Metrics

```python
# Python example with prometheus_client
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Counter
requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
requests_total.labels(method='GET', endpoint='/api/users').inc()

# Histogram
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
with request_duration.time():
    # Process request
    pass

# Gauge
active_users = Gauge('active_users', 'Number of active users')
active_users.set(42)

# Start metrics server
start_http_server(8080)
```

### Grafana

Visualization and dashboards.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grafana-secret
              key: admin-password
        volumeMounts:
        - name: storage
          mountPath: /var/lib/grafana
      
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: grafana-pvc
```

## Health Checks

### Liveness Probe

Determines if container is running. Restarts if fails.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: liveness-demo
spec:
  containers:
  - name: app
    image: myapp:1.0
    
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
        httpHeaders:
        - name: Custom-Header
          value: Awesome
      initialDelaySeconds: 3
      periodSeconds: 3
      timeoutSeconds: 1
      successThreshold: 1
      failureThreshold: 3
```

### Readiness Probe

Determines if container is ready to serve traffic.

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 1
  successThreshold: 1
  failureThreshold: 3
```

### Startup Probe

For slow-starting containers. Disables liveness/readiness until succeeds.

```yaml
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  initialDelaySeconds: 0
  periodSeconds: 10
  timeoutSeconds: 1
  successThreshold: 1
  failureThreshold: 30  # 30 * 10 = 300s max startup time
```

### Probe Types

#### HTTP GET

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
    scheme: HTTP
```

#### TCP Socket

```yaml
livenessProbe:
  tcpSocket:
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 20
```

#### Exec Command

```yaml
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
  initialDelaySeconds: 5
  periodSeconds: 5
```

#### gRPC

```yaml
livenessProbe:
  grpc:
    port: 9090
  initialDelaySeconds: 5
```

### Health Check Best Practices

```yaml
# Good health check endpoint
apiVersion: v1
kind: Pod
metadata:
  name: best-practice-health
spec:
  containers:
  - name: app
    image: myapp:1.0
    
    # Startup probe for slow initialization
    startupProbe:
      httpGet:
        path: /startup
        port: 8080
      failureThreshold: 30
      periodSeconds: 10
    
    # Liveness probe - simple check
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 10
      timeoutSeconds: 1
      failureThreshold: 3
    
    # Readiness probe - thorough check
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 5
      timeoutSeconds: 1
      failureThreshold: 3
```

## Distributed Tracing

### Jaeger

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jaeger
  template:
    metadata:
      labels:
        app: jaeger
    spec:
      containers:
      - name: jaeger
        image: jaegertracing/all-in-one:latest
        ports:
        - containerPort: 16686  # UI
        - containerPort: 14268  # Collector
        - containerPort: 6831   # Agent
          protocol: UDP
        env:
        - name: COLLECTOR_ZIPKIN_HTTP_PORT
          value: "9411"
```

### OpenTelemetry

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: otel-collector-config
data:
  config.yaml: |
    receivers:
      otlp:
        protocols:
          grpc:
          http:
    
    processors:
      batch:
    
    exporters:
      jaeger:
        endpoint: jaeger:14250
        tls:
          insecure: true
      
      prometheus:
        endpoint: "0.0.0.0:8889"
    
    service:
      pipelines:
        traces:
          receivers: [otlp]
          processors: [batch]
          exporters: [jaeger]
        
        metrics:
          receivers: [otlp]
          processors: [batch]
          exporters: [prometheus]
```

## Events

```bash
# View events
kubectl get events

# Watch events
kubectl get events --watch

# Events for specific resource
kubectl describe pod <pod-name>

# Events in namespace
kubectl get events -n kube-system

# Sort by timestamp
kubectl get events --sort-by='.lastTimestamp'

# Filter by type
kubectl get events --field-selector type=Warning
```

## Debugging

### Pod Debugging

```bash
# Describe pod
kubectl describe pod <pod-name>

# Get pod YAML
kubectl get pod <pod-name> -o yaml

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/bash

# Copy files
kubectl cp <pod-name>:/path/to/file ./local-file
kubectl cp ./local-file <pod-name>:/path/to/file

# Port forward
kubectl port-forward <pod-name> 8080:80

# Debug with ephemeral container (1.23+)
kubectl debug <pod-name> -it --image=busybox --target=<container-name>
```

### Node Debugging

```bash
# Describe node
kubectl describe node <node-name>

# Cordon node (mark unschedulable)
kubectl cordon <node-name>

# Drain node (evict pods)
kubectl drain <node-name> --ignore-daemonsets

# Uncordon node
kubectl uncordon <node-name>

# SSH to node (if accessible)
kubectl debug node/<node-name> -it --image=ubuntu
```

### Network Debugging

```bash
# Run debug pod
kubectl run debug --image=nicolaka/netshoot -it --rm -- /bin/bash

# Inside debug pod
nslookup kubernetes.default
curl http://service-name
ping pod-ip
traceroute service-name
```

## Monitoring Best Practices

1. **Use structured logging** with consistent format
2. **Implement all three probe types** appropriately
3. **Set up centralized logging** (EFK or Loki)
4. **Deploy Prometheus** for metrics collection
5. **Create Grafana dashboards** for visualization
6. **Monitor resource usage** (CPU, memory, disk, network)
7. **Set up alerts** for critical conditions
8. **Use distributed tracing** for microservices
9. **Monitor application-specific metrics**
10. **Regularly review logs and metrics**

## Key Metrics to Monitor

### Cluster Level
- Node CPU/memory usage
- Pod count and status
- API server latency
- etcd performance
- Network throughput

### Application Level
- Request rate
- Error rate
- Response time (latency)
- Saturation (resource usage)

### The Four Golden Signals
1. **Latency** - Time to serve requests
2. **Traffic** - Demand on system
3. **Errors** - Rate of failed requests
4. **Saturation** - Resource utilization

## Practice Exercises

### Exercise 1: View Logs

```bash
# Create pod
kubectl run nginx --image=nginx

# View logs
kubectl logs nginx

# Follow logs
kubectl logs -f nginx
```

### Exercise 2: Metrics

```bash
# Install metrics server
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View metrics
kubectl top nodes
kubectl top pods
```

### Exercise 3: Health Checks

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: health-check-demo
spec:
  containers:
  - name: nginx
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 3
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
```

## Key Takeaways

- Observability requires logging, metrics, and tracing
- Use kubectl logs for basic log viewing
- Implement centralized logging for production
- Metrics Server provides basic resource metrics
- Prometheus is the standard for metrics collection
- Grafana provides powerful visualization
- Health probes are essential for reliability
- Use startup, liveness, and readiness probes appropriately
- Monitor the Four Golden Signals
- Set up alerts for critical conditions
