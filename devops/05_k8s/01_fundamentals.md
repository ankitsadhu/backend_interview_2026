# Kubernetes Fundamentals

## What is Kubernetes?

Kubernetes (K8s) is an open-source container orchestration platform that automates deployment, scaling, and management of containerized applications.

### Key Benefits
- **Automated rollouts and rollbacks**
- **Self-healing** - restarts failed containers
- **Horizontal scaling** - scale applications up/down
- **Service discovery and load balancing**
- **Storage orchestration**
- **Secret and configuration management**

## Architecture

### Control Plane Components

#### 1. API Server (kube-apiserver)
- Front-end for the Kubernetes control plane
- Exposes the Kubernetes API
- Validates and processes REST requests
- Updates etcd with cluster state

```bash
# Check API server status
kubectl cluster-info
```

#### 2. etcd
- Consistent and highly-available key-value store
- Stores all cluster data
- Source of truth for cluster state

#### 3. Scheduler (kube-scheduler)
- Watches for newly created Pods with no assigned node
- Selects a node for them to run on
- Considers resource requirements, constraints, affinity/anti-affinity

#### 4. Controller Manager (kube-controller-manager)
- Runs controller processes
- **Node Controller** - monitors node health
- **Replication Controller** - maintains correct number of pods
- **Endpoints Controller** - populates Endpoints object
- **Service Account Controller** - creates default ServiceAccounts

#### 5. Cloud Controller Manager
- Embeds cloud-specific control logic
- Links cluster to cloud provider's API
- Manages cloud resources (load balancers, volumes)

### Node Components

#### 1. Kubelet
- Agent that runs on each node
- Ensures containers are running in Pods
- Takes PodSpecs and ensures described containers are running and healthy

#### 2. Kube-proxy
- Network proxy on each node
- Maintains network rules
- Enables communication to Pods from inside/outside cluster

#### 3. Container Runtime
- Software responsible for running containers
- Examples: containerd, CRI-O, Docker Engine

## Core Concepts

### 1. Cluster
A set of nodes that run containerized applications managed by Kubernetes.

```bash
# View cluster info
kubectl cluster-info

# View nodes
kubectl get nodes
```

### 2. Node
A worker machine (VM or physical) that runs containerized applications.

```bash
# Get node details
kubectl describe node <node-name>

# Label a node
kubectl label nodes <node-name> disktype=ssd
```

### 3. Namespace
Virtual clusters backed by the same physical cluster. Used to divide cluster resources.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: development
```

```bash
# List namespaces
kubectl get namespaces

# Create namespace
kubectl create namespace dev

# Set default namespace
kubectl config set-context --current --namespace=dev
```

### 4. Pod
Smallest deployable unit in Kubernetes. Contains one or more containers.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
```

```bash
# Create pod
kubectl apply -f pod.yaml

# Get pods
kubectl get pods

# Describe pod
kubectl describe pod nginx-pod

# Delete pod
kubectl delete pod nginx-pod
```

### 5. Labels and Selectors

Labels are key-value pairs attached to objects. Selectors identify a set of objects.

```yaml
metadata:
  labels:
    app: nginx
    environment: production
    tier: frontend
```

```bash
# Get pods with label
kubectl get pods -l app=nginx

# Get pods with multiple labels
kubectl get pods -l 'environment=production,tier=frontend'

# Add label to existing pod
kubectl label pod nginx-pod version=v1
```

### 6. Annotations
Non-identifying metadata attached to objects.

```yaml
metadata:
  annotations:
    description: "Production nginx server"
    contact: "ops@example.com"
```

## kubectl Basics

### Configuration

```bash
# View config
kubectl config view

# Get current context
kubectl config current-context

# Switch context
kubectl config use-context <context-name>

# Set namespace
kubectl config set-context --current --namespace=<namespace>
```

### Common Commands

```bash
# Get resources
kubectl get <resource>
kubectl get pods
kubectl get services
kubectl get deployments

# Describe resource
kubectl describe <resource> <name>

# Create resource
kubectl create -f <file.yaml>
kubectl apply -f <file.yaml>

# Delete resource
kubectl delete <resource> <name>
kubectl delete -f <file.yaml>

# Edit resource
kubectl edit <resource> <name>

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/bash

# View logs
kubectl logs <pod-name>
kubectl logs -f <pod-name>  # Follow logs

# Port forwarding
kubectl port-forward <pod-name> 8080:80
```

### Resource Shortcuts

```bash
po  - pods
svc - services
deploy - deployments
rs - replicasets
ns - namespaces
cm - configmaps
pv - persistentvolumes
pvc - persistentvolumeclaims
```

## Declarative vs Imperative

### Imperative (Commands)
```bash
kubectl create deployment nginx --image=nginx
kubectl expose deployment nginx --port=80
kubectl scale deployment nginx --replicas=3
```

### Declarative (YAML files)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
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
```

```bash
kubectl apply -f deployment.yaml
```

**Best Practice**: Use declarative approach for production (GitOps).

## Resource Management

### Resource Requests and Limits

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"
```

- **Requests**: Guaranteed resources
- **Limits**: Maximum resources allowed

### Quality of Service (QoS) Classes

1. **Guaranteed**: requests = limits for all containers
2. **Burstable**: requests < limits
3. **BestEffort**: no requests or limits set

## YAML Basics

### Structure
```yaml
apiVersion: v1  # API version
kind: Pod       # Resource type
metadata:       # Metadata about the resource
  name: my-pod
  labels:
    app: myapp
spec:          # Specification of the resource
  containers:
  - name: nginx
    image: nginx:1.21
```

### Common Fields
- `apiVersion`: API group and version
- `kind`: Type of resource
- `metadata`: Name, labels, annotations
- `spec`: Desired state of the resource

## Practice Exercises

### Exercise 1: Create a Simple Pod
```bash
# Create a pod running nginx
kubectl run nginx --image=nginx

# Verify it's running
kubectl get pods

# Get detailed info
kubectl describe pod nginx

# Delete the pod
kubectl delete pod nginx
```

### Exercise 2: Use Namespaces
```bash
# Create namespace
kubectl create namespace test

# Create pod in namespace
kubectl run nginx --image=nginx -n test

# List pods in namespace
kubectl get pods -n test

# Delete namespace (deletes all resources in it)
kubectl delete namespace test
```

### Exercise 3: Work with Labels
```bash
# Create pod with labels
kubectl run nginx --image=nginx --labels="app=web,env=prod"

# Query by label
kubectl get pods -l app=web

# Add label to existing pod
kubectl label pod nginx tier=frontend

# Remove label
kubectl label pod nginx tier-
```

## Key Takeaways

1. Kubernetes orchestrates containerized applications across a cluster
2. Control plane manages the cluster, nodes run the workloads
3. Pods are the smallest deployable units
4. Use namespaces to organize resources
5. Labels and selectors enable flexible resource grouping
6. kubectl is the primary CLI tool for interacting with clusters
7. Declarative configuration (YAML) is preferred for production

## Next Steps

- Learn about [Pods and Workloads](02_pods_and_workloads.md)
- Understand [Services and Networking](03_services_and_networking.md)
- Practice with a local cluster (Minikube or Kind)
