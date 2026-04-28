# Configuration and Secrets

## ConfigMaps

Store non-confidential configuration data as key-value pairs.

### Creating ConfigMaps

#### From Literal Values
```bash
kubectl create configmap app-config \
  --from-literal=database_url=postgres://localhost:5432/mydb \
  --from-literal=log_level=info
```

#### From File
```bash
# config.properties
database_url=postgres://localhost:5432/mydb
log_level=info

kubectl create configmap app-config --from-file=config.properties
```

#### From Directory
```bash
kubectl create configmap app-config --from-file=config-dir/
```

#### From YAML
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgres://localhost:5432/mydb"
  log_level: "info"
  config.json: |
    {
      "feature_flags": {
        "new_ui": true,
        "beta_features": false
      }
    }
```

### Using ConfigMaps

#### As Environment Variables

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    env:
    # Single value
    - name: DATABASE_URL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database_url
    
    # All keys as env vars
    envFrom:
    - configMapRef:
        name: app-config
```

#### As Volume Mount

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

#### Specific Keys as Files

```yaml
volumes:
- name: config-volume
  configMap:
    name: app-config
    items:
    - key: config.json
      path: app-config.json
```

### ConfigMap Operations

```bash
# List ConfigMaps
kubectl get configmaps

# Describe ConfigMap
kubectl describe configmap app-config

# View ConfigMap data
kubectl get configmap app-config -o yaml

# Edit ConfigMap
kubectl edit configmap app-config

# Delete ConfigMap
kubectl delete configmap app-config
```

## Secrets

Store sensitive information like passwords, tokens, keys.

### Secret Types

- `Opaque` - Arbitrary user-defined data (default)
- `kubernetes.io/service-account-token` - Service account token
- `kubernetes.io/dockercfg` - Docker config
- `kubernetes.io/dockerconfigjson` - Docker config JSON
- `kubernetes.io/basic-auth` - Basic authentication
- `kubernetes.io/ssh-auth` - SSH authentication
- `kubernetes.io/tls` - TLS certificate

### Creating Secrets

#### From Literal Values
```bash
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=secretpass123
```

#### From Files
```bash
kubectl create secret generic ssh-key \
  --from-file=ssh-privatekey=~/.ssh/id_rsa \
  --from-file=ssh-publickey=~/.ssh/id_rsa.pub
```

#### From YAML (Base64 Encoded)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:
  username: YWRtaW4=        # base64 encoded 'admin'
  password: c2VjcmV0cGFzczEyMw==  # base64 encoded 'secretpass123'
```

```bash
# Encode values
echo -n 'admin' | base64
echo -n 'secretpass123' | base64

# Decode values
echo 'YWRtaW4=' | base64 --decode
```

#### Using stringData (Plain Text)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:
  username: admin
  password: secretpass123
```

### TLS Secret

```bash
kubectl create secret tls tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tls-secret
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-cert>
  tls.key: <base64-encoded-key>
```

### Docker Registry Secret

```bash
kubectl create secret docker-registry regcred \
  --docker-server=https://index.docker.io/v1/ \
  --docker-username=myuser \
  --docker-password=mypassword \
  --docker-email=myemail@example.com
```

### Using Secrets

#### As Environment Variables

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    env:
    # Single value
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: username
    
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: password
    
    # All keys as env vars
    envFrom:
    - secretRef:
        name: db-secret
```

#### As Volume Mount

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets
      readOnly: true
  
  volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
```

#### For Image Pull

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: private-app
spec:
  containers:
  - name: app
    image: private-registry.com/myapp:1.0
  
  imagePullSecrets:
  - name: regcred
```

### Secret Operations

```bash
# List secrets
kubectl get secrets

# Describe secret (doesn't show values)
kubectl describe secret db-secret

# View secret data (base64 encoded)
kubectl get secret db-secret -o yaml

# Decode secret value
kubectl get secret db-secret -o jsonpath='{.data.password}' | base64 --decode

# Edit secret
kubectl edit secret db-secret

# Delete secret
kubectl delete secret db-secret
```

## Environment Variables

### Direct Values

```yaml
env:
- name: APP_ENV
  value: "production"
- name: PORT
  value: "8080"
```

### From ConfigMap

```yaml
env:
- name: DATABASE_URL
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: database_url
```

### From Secret

```yaml
env:
- name: API_KEY
  valueFrom:
    secretKeyRef:
      name: api-secret
      key: api_key
```

### From Field

```yaml
env:
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name

- name: POD_NAMESPACE
  valueFrom:
    fieldRef:
      fieldPath: metadata.namespace

- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP

- name: NODE_NAME
  valueFrom:
    fieldRef:
      fieldPath: spec.nodeName
```

### From Resource

```yaml
env:
- name: CPU_REQUEST
  valueFrom:
    resourceFieldRef:
      containerName: app
      resource: requests.cpu

- name: MEMORY_LIMIT
  valueFrom:
    resourceFieldRef:
      containerName: app
      resource: limits.memory
```

## Immutable ConfigMaps and Secrets

Prevent accidental updates and improve performance.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: immutable-config
data:
  key: value
immutable: true
```

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: immutable-secret
data:
  password: c2VjcmV0
immutable: true
```

## Projected Volumes

Combine multiple volume sources into a single directory.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: projected-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    volumeMounts:
    - name: all-in-one
      mountPath: /projected-volume
  
  volumes:
  - name: all-in-one
    projected:
      sources:
      - secret:
          name: db-secret
      - configMap:
          name: app-config
      - downwardAPI:
          items:
          - path: "labels"
            fieldRef:
              fieldPath: metadata.labels
```

## Downward API

Expose Pod and Container fields to running containers.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: downward-api-pod
  labels:
    app: myapp
    tier: frontend
spec:
  containers:
  - name: app
    image: myapp:1.0
    env:
    - name: POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: metadata.namespace
    
    volumeMounts:
    - name: podinfo
      mountPath: /etc/podinfo
  
  volumes:
  - name: podinfo
    downwardAPI:
      items:
      - path: "labels"
        fieldRef:
          fieldPath: metadata.labels
      - path: "annotations"
        fieldRef:
          fieldPath: metadata.annotations
```

## External Secrets Management

### External Secrets Operator

Integrates with external secret management systems.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      version: "v2"
      auth:
        tokenSecretRef:
          name: vault-token
          key: token

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  
  target:
    name: db-secret
    creationPolicy: Owner
  
  data:
  - secretKey: username
    remoteRef:
      key: database/config
      property: username
  
  - secretKey: password
    remoteRef:
      key: database/config
      property: password
```

### Sealed Secrets

Encrypt secrets for safe storage in Git.

```bash
# Install kubeseal
brew install kubeseal

# Create sealed secret
kubectl create secret generic mysecret \
  --from-literal=password=mypassword \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

# Apply sealed secret
kubectl apply -f sealed-secret.yaml
```

## Best Practices

1. **Use Secrets for sensitive data**, ConfigMaps for non-sensitive
2. **Never commit secrets to Git** (use Sealed Secrets or External Secrets)
3. **Use RBAC** to restrict secret access
4. **Enable encryption at rest** for etcd
5. **Use immutable ConfigMaps/Secrets** when possible
6. **Mount secrets as volumes** instead of env vars (more secure)
7. **Rotate secrets regularly**
8. **Use specific keys** instead of mounting entire ConfigMap/Secret
9. **Validate configuration** before deployment
10. **Use external secret management** for production (Vault, AWS Secrets Manager)

## Practice Exercises

### Exercise 1: ConfigMap

```bash
# Create ConfigMap
kubectl create configmap app-config \
  --from-literal=env=production \
  --from-literal=debug=false

# Create pod using ConfigMap
kubectl run test-pod --image=busybox --restart=Never \
  --env="APP_ENV=$(kubectl get configmap app-config -o jsonpath='{.data.env}')" \
  -- sleep 3600

# Verify
kubectl exec test-pod -- env | grep APP_ENV
```

### Exercise 2: Secret

```bash
# Create secret
kubectl create secret generic db-creds \
  --from-literal=username=admin \
  --from-literal=password=secret123

# View secret (encoded)
kubectl get secret db-creds -o yaml

# Decode secret
kubectl get secret db-creds -o jsonpath='{.data.password}' | base64 --decode
```

### Exercise 3: Volume Mount

```yaml
# config-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: config-pod
spec:
  containers:
  - name: app
    image: busybox
    command: ['sh', '-c', 'cat /config/app.conf && sleep 3600']
    volumeMounts:
    - name: config
      mountPath: /config
  volumes:
  - name: config
    configMap:
      name: app-config
```

## Key Takeaways

- ConfigMaps for non-sensitive configuration
- Secrets for sensitive data (base64 encoded, not encrypted)
- Multiple ways to consume: env vars, volumes, projected volumes
- Use external secret management for production
- Immutable ConfigMaps/Secrets improve security and performance
- Mount secrets as volumes for better security
- Never commit secrets to version control
