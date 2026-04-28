# Kubernetes Security

## Security Layers

1. **Authentication** - Who are you?
2. **Authorization** - What can you do?
3. **Admission Control** - Policy enforcement
4. **Network Policies** - Network segmentation
5. **Security Contexts** - Container security
6. **Secrets Management** - Sensitive data

## Authentication

### User Types

1. **Normal Users** - External (not managed by K8s)
2. **Service Accounts** - For Pods/applications

### Authentication Methods

- Client certificates
- Bearer tokens
- Authentication proxy
- HTTP basic auth (deprecated)
- OpenID Connect (OIDC)

### Service Accounts

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: default
```

```bash
# Create service account
kubectl create serviceaccount my-sa

# List service accounts
kubectl get serviceaccounts

# Describe service account
kubectl describe sa my-sa
```

### Using Service Account in Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  serviceAccountName: my-service-account
  containers:
  - name: app
    image: myapp:1.0
```

### Service Account Token

```bash
# Get token (K8s 1.24+)
kubectl create token my-sa

# Get token from secret (older versions)
kubectl get secret <sa-token-secret> -o jsonpath='{.data.token}' | base64 --decode
```

## Authorization (RBAC)

Role-Based Access Control defines who can do what.

### Roles and ClusterRoles

**Role** - Namespace-scoped permissions

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

**ClusterRole** - Cluster-wide permissions

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
```

### Common Verbs

- `get` - Read single resource
- `list` - List resources
- `watch` - Watch for changes
- `create` - Create resources
- `update` - Update resources
- `patch` - Patch resources
- `delete` - Delete resources
- `deletecollection` - Delete multiple resources

### RoleBindings and ClusterRoleBindings

**RoleBinding** - Grants Role permissions in namespace

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

**ClusterRoleBinding** - Grants ClusterRole permissions cluster-wide

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-secrets-global
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: default
roleRef:
  kind: ClusterRole
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

### RBAC Examples

#### Read-Only Access to Pods

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

#### Full Access to Deployments

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployment-manager
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["*"]
```

#### Namespace Admin

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: admin-binding
  namespace: development
subjects:
- kind: User
  name: admin-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: admin  # Built-in ClusterRole
  apiGroup: rbac.authorization.k8s.io
```

### Built-in ClusterRoles

- `cluster-admin` - Full cluster access
- `admin` - Full namespace access
- `edit` - Read/write namespace access
- `view` - Read-only namespace access

### RBAC Commands

```bash
# Check if user can perform action
kubectl auth can-i create deployments
kubectl auth can-i delete pods --as=jane
kubectl auth can-i get secrets --namespace=prod

# List roles
kubectl get roles
kubectl get clusterroles

# Describe role
kubectl describe role pod-reader

# Create role
kubectl create role pod-reader --verb=get,list --resource=pods

# Create rolebinding
kubectl create rolebinding read-pods --role=pod-reader --serviceaccount=default:my-sa
```

## Security Contexts

Define privilege and access control settings for Pods/Containers.

### Pod Security Context

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
    fsGroupChangePolicy: "OnRootMismatch"
    seccompProfile:
      type: RuntimeDefault
  
  containers:
  - name: app
    image: busybox
    command: ["sh", "-c", "sleep 3600"]
```

### Container Security Context

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo-2
spec:
  containers:
  - name: app
    image: busybox
    command: ["sh", "-c", "sleep 3600"]
    securityContext:
      runAsUser: 2000
      runAsNonRoot: true
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
        add:
        - NET_BIND_SERVICE
```

### Security Context Fields

- `runAsUser` - User ID to run container
- `runAsGroup` - Group ID to run container
- `runAsNonRoot` - Require non-root user
- `readOnlyRootFilesystem` - Make root filesystem read-only
- `allowPrivilegeEscalation` - Allow privilege escalation
- `privileged` - Run as privileged container
- `capabilities` - Add/drop Linux capabilities
- `seLinuxOptions` - SELinux options
- `seccompProfile` - Seccomp profile

### Capabilities

```yaml
securityContext:
  capabilities:
    drop:
    - ALL  # Drop all capabilities
    add:
    - NET_BIND_SERVICE  # Allow binding to ports < 1024
    - CHOWN  # Allow changing file ownership
```

Common capabilities:
- `NET_BIND_SERVICE` - Bind to ports < 1024
- `SYS_TIME` - Set system time
- `CHOWN` - Change file ownership
- `DAC_OVERRIDE` - Bypass file permissions
- `KILL` - Send signals to processes

## Pod Security Standards

Replaced PodSecurityPolicy (deprecated in 1.21, removed in 1.25).

### Security Levels

1. **Privileged** - Unrestricted (default)
2. **Baseline** - Minimally restrictive
3. **Restricted** - Heavily restricted (best practice)

### Pod Security Admission

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Modes

- `enforce` - Reject non-compliant pods
- `audit` - Log violations
- `warn` - Show warnings to user

### Restricted Profile Requirements

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: restricted-pod
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile:
      type: RuntimeDefault
  
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false
      runAsNonRoot: true
      capabilities:
        drop:
        - ALL
```

## Network Policies

Control traffic between Pods (covered in detail in Networking chapter).

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

## Secrets Management

### Encryption at Rest

Enable encryption for secrets in etcd.

```yaml
# encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64-encoded-32-byte-key>
  - identity: {}
```

### External Secrets

Use external secret management systems:
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager

```yaml
# Using External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: vault-secret
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: my-secret
  data:
  - secretKey: password
    remoteRef:
      key: secret/data/myapp
      property: password
```

## Image Security

### Private Registry

```bash
kubectl create secret docker-registry regcred \
  --docker-server=<registry> \
  --docker-username=<username> \
  --docker-password=<password>
```

```yaml
spec:
  imagePullSecrets:
  - name: regcred
  containers:
  - name: app
    image: private-registry.com/myapp:1.0
```

### Image Pull Policy

```yaml
containers:
- name: app
  image: myapp:1.0
  imagePullPolicy: Always  # Always, IfNotPresent, Never
```

### Image Scanning

Use tools to scan images for vulnerabilities:
- Trivy
- Clair
- Anchore
- Snyk

## Admission Controllers

Intercept requests to API server before persistence.

### Common Admission Controllers

- `NamespaceLifecycle` - Prevents deletion of system namespaces
- `LimitRanger` - Enforces resource limits
- `ServiceAccount` - Automates service account creation
- `ResourceQuota` - Enforces resource quotas
- `PodSecurityPolicy` - Enforces pod security (deprecated)
- `PodSecurity` - Enforces Pod Security Standards

### Validating Admission Webhooks

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingWebhookConfiguration
metadata:
  name: pod-policy
webhooks:
- name: validate.example.com
  clientConfig:
    service:
      name: validation-service
      namespace: default
      path: /validate
    caBundle: <base64-ca-cert>
  rules:
  - operations: ["CREATE", "UPDATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
```

### Mutating Admission Webhooks

Modify objects before admission.

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingWebhookConfiguration
metadata:
  name: pod-mutator
webhooks:
- name: mutate.example.com
  clientConfig:
    service:
      name: mutation-service
      namespace: default
      path: /mutate
    caBundle: <base64-ca-cert>
  rules:
  - operations: ["CREATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
```

## Resource Quotas

Limit resource consumption per namespace.

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: development
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "10"
    services: "5"
    persistentvolumeclaims: "5"
```

## Limit Ranges

Set default resource limits for containers.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: limit-range
  namespace: development
spec:
  limits:
  - max:
      cpu: "2"
      memory: 2Gi
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

## Audit Logging

Track API server requests.

```yaml
# audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
- level: RequestResponse
  resources:
  - group: ""
    resources: ["pods"]
```

## Best Practices

1. **Enable RBAC** and follow principle of least privilege
2. **Use Service Accounts** for applications
3. **Run containers as non-root** user
4. **Use read-only root filesystem** when possible
5. **Drop all capabilities** and add only required ones
6. **Enable Pod Security Standards** (restricted profile)
7. **Implement Network Policies** for network segmentation
8. **Encrypt secrets at rest** in etcd
9. **Use external secret management** for production
10. **Scan images** for vulnerabilities
11. **Enable audit logging**
12. **Set resource quotas and limits**
13. **Use private registries** with authentication
14. **Regularly update** Kubernetes and dependencies
15. **Implement admission controllers** for policy enforcement

## Security Checklist

- [ ] RBAC enabled and configured
- [ ] Service accounts with minimal permissions
- [ ] Pod Security Standards enforced
- [ ] Network Policies implemented
- [ ] Secrets encrypted at rest
- [ ] Resource quotas and limits set
- [ ] Audit logging enabled
- [ ] Images scanned for vulnerabilities
- [ ] Containers run as non-root
- [ ] Read-only root filesystem where possible
- [ ] Capabilities dropped
- [ ] Private registry with authentication
- [ ] TLS for all external communication
- [ ] Regular security updates

## Practice Exercises

### Exercise 1: Create Service Account with RBAC

```bash
# Create service account
kubectl create serviceaccount app-sa

# Create role
kubectl create role pod-reader --verb=get,list --resource=pods

# Create rolebinding
kubectl create rolebinding app-sa-binding --role=pod-reader --serviceaccount=default:app-sa

# Test
kubectl auth can-i list pods --as=system:serviceaccount:default:app-sa
```

### Exercise 2: Secure Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  serviceAccountName: app-sa
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  
  containers:
  - name: app
    image: nginx:1.21
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    volumeMounts:
    - name: cache
      mountPath: /var/cache/nginx
    - name: run
      mountPath: /var/run
  
  volumes:
  - name: cache
    emptyDir: {}
  - name: run
    emptyDir: {}
```

## Key Takeaways

- Security is multi-layered: authentication, authorization, admission, runtime
- RBAC provides fine-grained access control
- Security contexts enforce container security policies
- Pod Security Standards replace PodSecurityPolicy
- Always run containers as non-root with minimal capabilities
- Use external secret management for production
- Implement Network Policies for network segmentation
- Regular security audits and updates are essential
