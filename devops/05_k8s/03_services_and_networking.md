# Services and Networking

## Services

Services provide stable networking for Pods. Pods are ephemeral, but Services provide a consistent way to access them.

### Why Services?
- Pods have dynamic IPs that change on restart
- Services provide stable virtual IP (ClusterIP)
- Load balancing across multiple Pods
- Service discovery via DNS

### Service Types

#### 1. ClusterIP (Default)
Exposes service on cluster-internal IP. Only reachable within cluster.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80        # Service port
    targetPort: 8080  # Container port
```

```bash
# Create service
kubectl expose deployment backend --port=80 --target-port=8080

# Access from within cluster
curl backend-service.default.svc.cluster.local
```

#### 2. NodePort
Exposes service on each Node's IP at a static port (30000-32767).

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
    nodePort: 30080  # Optional, auto-assigned if not specified
```

```bash
# Access from outside cluster
curl <node-ip>:30080
```

#### 3. LoadBalancer
Exposes service externally using cloud provider's load balancer.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

```bash
# Get external IP
kubectl get service web-service
# Access via external IP
curl <external-ip>
```

#### 4. ExternalName
Maps service to external DNS name.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-db
spec:
  type: ExternalName
  externalName: database.example.com
```

### Service with Multiple Ports

```yaml
apiVersion: v1
kind: Service
metadata:
  name: multi-port-service
spec:
  selector:
    app: myapp
  ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 8080
  - name: https
    protocol: TCP
    port: 443
    targetPort: 8443
```

### Headless Service
For direct Pod-to-Pod communication without load balancing.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: headless-service
spec:
  clusterIP: None  # Makes it headless
  selector:
    app: myapp
  ports:
  - port: 80
```

Returns individual Pod IPs instead of service IP.

## Service Discovery

### DNS
Kubernetes automatically creates DNS records for services.

```bash
# Format: <service-name>.<namespace>.svc.cluster.local

# Same namespace
curl backend-service

# Different namespace
curl backend-service.production.svc.cluster.local

# Full FQDN
curl backend-service.production.svc.cluster.local.
```

### Environment Variables
Kubernetes injects service info as environment variables.

```bash
BACKEND_SERVICE_HOST=10.0.0.1
BACKEND_SERVICE_PORT=80
```

## Endpoints

Services route traffic to Endpoints (Pod IPs).

```bash
# View endpoints
kubectl get endpoints backend-service

# Describe endpoints
kubectl describe endpoints backend-service
```

```yaml
# Manual endpoint (for external service)
apiVersion: v1
kind: Service
metadata:
  name: external-service
spec:
  ports:
  - port: 80

---
apiVersion: v1
kind: Endpoints
metadata:
  name: external-service
subsets:
- addresses:
  - ip: 192.168.1.100
  ports:
  - port: 80
```

## Ingress

Manages external access to services, typically HTTP/HTTPS.

### Ingress Controller
Required to fulfill Ingress resources. Popular options:
- NGINX Ingress Controller
- Traefik
- HAProxy
- AWS ALB Ingress Controller

### Basic Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: simple-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

### Multiple Hosts

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-host-ingress
spec:
  rules:
  - host: app1.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app1-service
            port:
              number: 80
  
  - host: app2.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app2-service
            port:
              number: 80
```

### Path-Based Routing

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-based-ingress
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
      
      - path: /web
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

### TLS/HTTPS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: tls-secret
  
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
```

```bash
# Create TLS secret
kubectl create secret tls tls-secret \
  --cert=path/to/cert.crt \
  --key=path/to/cert.key
```

### Ingress Annotations

```yaml
metadata:
  annotations:
    # NGINX specific
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    
    # Cert-manager for automatic TLS
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

## Network Policies

Control traffic flow between Pods.

### Default Deny All Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
```

### Allow Specific Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend
spec:
  podSelector:
    matchLabels:
      app: backend
  
  policyTypes:
  - Ingress
  
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

### Allow from Namespace

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-namespace
spec:
  podSelector:
    matchLabels:
      app: api
  
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          environment: production
```

### Egress Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-egress
spec:
  podSelector:
    matchLabels:
      app: myapp
  
  policyTypes:
  - Egress
  
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

### Combined Ingress and Egress

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: full-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  
  policyTypes:
  - Ingress
  - Egress
  
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
  
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
```

## DNS

### CoreDNS
Default DNS server in Kubernetes.

```bash
# View CoreDNS config
kubectl get configmap coredns -n kube-system -o yaml

# CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

### DNS Resolution

```yaml
# Pod DNS config
spec:
  dnsPolicy: ClusterFirst  # Default
  dnsConfig:
    nameservers:
    - 8.8.8.8
    searches:
    - my.dns.search.suffix
    options:
    - name: ndots
      value: "2"
```

**DNS Policies:**
- `ClusterFirst` - Use cluster DNS (default)
- `Default` - Use node's DNS
- `None` - Use dnsConfig only
- `ClusterFirstWithHostNet` - For pods using hostNetwork

## Service Mesh (Brief Overview)

Service meshes provide advanced networking features:
- **Istio** - Full-featured service mesh
- **Linkerd** - Lightweight service mesh
- **Consul** - Service mesh and service discovery

Features:
- Traffic management
- Security (mTLS)
- Observability
- Circuit breaking
- Retries and timeouts

## Practice Exercises

### Exercise 1: Create Service

```bash
# Create deployment
kubectl create deployment nginx --image=nginx --replicas=3

# Expose as ClusterIP
kubectl expose deployment nginx --port=80

# Test from within cluster
kubectl run test --image=busybox -it --rm -- wget -O- nginx
```

### Exercise 2: NodePort Service

```bash
# Create NodePort service
kubectl expose deployment nginx --type=NodePort --port=80

# Get NodePort
kubectl get svc nginx

# Access from outside (if using Minikube)
minikube service nginx
```

### Exercise 3: Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-ingress
spec:
  rules:
  - host: test.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
```

```bash
kubectl apply -f ingress.yaml

# Add to /etc/hosts
echo "$(minikube ip) test.local" | sudo tee -a /etc/hosts

# Test
curl test.local
```

## Best Practices

1. **Use ClusterIP** for internal services
2. **Use Ingress** instead of multiple LoadBalancers
3. **Implement Network Policies** for security
4. **Use meaningful service names** for DNS discovery
5. **Set resource limits** on Ingress controllers
6. **Use TLS** for external services
7. **Monitor service endpoints** for health
8. **Use headless services** for StatefulSets
9. **Implement proper DNS policies**
10. **Use service mesh** for complex microservices

## Key Takeaways

- Services provide stable networking for dynamic Pods
- ClusterIP for internal, LoadBalancer for external access
- Ingress manages HTTP/HTTPS routing efficiently
- Network Policies control Pod-to-Pod communication
- DNS enables service discovery within cluster
- Use appropriate service type for your use case
