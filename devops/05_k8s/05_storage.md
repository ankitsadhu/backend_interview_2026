# Storage in Kubernetes

## Volume Types

### emptyDir
Temporary storage that exists as long as Pod exists.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: emptydir-pod
spec:
  containers:
  - name: writer
    image: busybox
    command: ['sh', '-c', 'echo "Hello" > /data/hello.txt && sleep 3600']
    volumeMounts:
    - name: shared-data
      mountPath: /data
  
  - name: reader
    image: busybox
    command: ['sh', '-c', 'cat /data/hello.txt && sleep 3600']
    volumeMounts:
    - name: shared-data
      mountPath: /data
  
  volumes:
  - name: shared-data
    emptyDir: {}
```

**Use Cases:**
- Scratch space
- Cache
- Sharing data between containers in same Pod

### hostPath
Mounts file or directory from host node's filesystem.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hostpath-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: host-volume
      mountPath: /usr/share/nginx/html
  
  volumes:
  - name: host-volume
    hostPath:
      path: /data/web
      type: DirectoryOrCreate
```

**Types:**
- `DirectoryOrCreate` - Create if doesn't exist
- `Directory` - Must exist
- `FileOrCreate` - Create file if doesn't exist
- `File` - Must exist
- `Socket`, `CharDevice`, `BlockDevice`

**Warning**: Security risk, avoid in production.

### configMap and secret
Already covered in Configuration chapter.

### downwardAPI
Expose Pod metadata to containers.

```yaml
volumes:
- name: podinfo
  downwardAPI:
    items:
    - path: "labels"
      fieldRef:
        fieldPath: metadata.labels
```

## Persistent Volumes (PV)

Cluster-level storage resource provisioned by admin.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-example
spec:
  capacity:
    storage: 10Gi
  
  accessModes:
  - ReadWriteOnce
  
  persistentVolumeReclaimPolicy: Retain
  
  storageClassName: standard
  
  hostPath:
    path: /mnt/data
```

### Access Modes

- `ReadWriteOnce (RWO)` - Single node read-write
- `ReadOnlyMany (ROX)` - Multiple nodes read-only
- `ReadWriteMany (RWX)` - Multiple nodes read-write
- `ReadWriteOncePod (RWOP)` - Single pod read-write (1.22+)

### Reclaim Policies

- `Retain` - Manual reclamation (data preserved)
- `Delete` - Delete volume when PVC is deleted
- `Recycle` - Basic scrub (deprecated)

### Volume Modes

- `Filesystem` - Mounted as directory (default)
- `Block` - Raw block device

### PV Lifecycle

1. **Provisioning** - Static or Dynamic
2. **Binding** - PVC binds to PV
3. **Using** - Pod uses PVC
4. **Reclaiming** - PVC deleted, PV reclaimed

### PV Status

- `Available` - Free, not bound
- `Bound` - Bound to PVC
- `Released` - PVC deleted, not yet reclaimed
- `Failed` - Automatic reclamation failed

## Persistent Volume Claims (PVC)

Request for storage by user.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-example
spec:
  accessModes:
  - ReadWriteOnce
  
  resources:
    requests:
      storage: 5Gi
  
  storageClassName: standard
```

### Using PVC in Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pvc-pod
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - name: storage
      mountPath: /usr/share/nginx/html
  
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: pvc-example
```

### PVC Operations

```bash
# Create PVC
kubectl apply -f pvc.yaml

# List PVCs
kubectl get pvc

# Describe PVC
kubectl describe pvc pvc-example

# Delete PVC
kubectl delete pvc pvc-example
```

## Storage Classes

Defines classes of storage with different properties.

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iopsPerGB: "10"
  fsType: ext4
reclaimPolicy: Delete
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

### Common Provisioners

- `kubernetes.io/aws-ebs` - AWS EBS
- `kubernetes.io/azure-disk` - Azure Disk
- `kubernetes.io/gce-pd` - GCE Persistent Disk
- `kubernetes.io/cinder` - OpenStack Cinder
- `kubernetes.io/vsphere-volume` - vSphere
- `kubernetes.io/no-provisioner` - Local volumes

### Volume Binding Modes

- `Immediate` - Bind immediately when PVC created
- `WaitForFirstConsumer` - Bind when Pod using PVC is created

### Dynamic Provisioning

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: dynamic-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: fast-ssd  # References StorageClass
  resources:
    requests:
      storage: 10Gi
```

PV is automatically created based on StorageClass.

### Default Storage Class

```bash
# Set default StorageClass
kubectl patch storageclass standard \
  -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# View default
kubectl get storageclass
```

## StatefulSet with Storage

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
          value: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 10Gi
```

Each Pod gets its own PVC: `data-mysql-0`, `data-mysql-1`, `data-mysql-2`

## Volume Snapshots

Create snapshots of persistent volumes.

### VolumeSnapshotClass

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapclass
driver: ebs.csi.aws.com
deletionPolicy: Delete
```

### VolumeSnapshot

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: pvc-snapshot
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: pvc-example
```

### Restore from Snapshot

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: restored-pvc
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 10Gi
  dataSource:
    name: pvc-snapshot
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
```

## Volume Expansion

Expand PVC size (if StorageClass allows).

```yaml
# Original PVC
spec:
  resources:
    requests:
      storage: 10Gi

# Edit to expand
spec:
  resources:
    requests:
      storage: 20Gi
```

```bash
# Edit PVC
kubectl edit pvc pvc-example

# Or patch
kubectl patch pvc pvc-example -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'
```

**Note**: Requires `allowVolumeExpansion: true` in StorageClass.

## CSI (Container Storage Interface)

Standard for exposing storage systems to containers.

### CSI Driver

```yaml
apiVersion: storage.k8s.io/v1
kind: CSIDriver
metadata:
  name: ebs.csi.aws.com
spec:
  attachRequired: true
  podInfoOnMount: false
  volumeLifecycleModes:
  - Persistent
```

### Popular CSI Drivers

- AWS EBS CSI Driver
- Azure Disk CSI Driver
- GCE PD CSI Driver
- Ceph CSI
- NFS CSI
- Longhorn

## Local Persistent Volumes

For high-performance local storage.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  local:
    path: /mnt/disks/ssd1
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - node-1
```

**Use Cases:**
- Databases requiring high IOPS
- Distributed storage systems (Cassandra, MongoDB)

## NFS Volumes

Network File System for shared storage.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteMany
  nfs:
    server: nfs-server.example.com
    path: /exported/path
```

## Projected Volumes

Combine multiple volume sources.

```yaml
volumes:
- name: all-in-one
  projected:
    sources:
    - secret:
        name: mysecret
        items:
        - key: username
          path: my-group/my-username
    - configMap:
        name: myconfigmap
        items:
        - key: config
          path: my-group/my-config
    - downwardAPI:
        items:
        - path: "labels"
          fieldRef:
            fieldPath: metadata.labels
```

## Best Practices

1. **Use StorageClasses** for dynamic provisioning
2. **Set appropriate access modes** based on requirements
3. **Use StatefulSets** for stateful applications
4. **Enable volume expansion** in StorageClass
5. **Implement backup strategy** (snapshots, external backups)
6. **Monitor storage usage** and set alerts
7. **Use appropriate reclaim policy** (Retain for production)
8. **Consider performance requirements** when choosing storage
9. **Use ReadWriteMany** only when necessary (expensive)
10. **Test disaster recovery** procedures regularly

## Storage Patterns

### Database Pattern
```yaml
# StatefulSet with persistent storage
# Each pod gets own PVC
# Use fast SSD storage class
# Enable snapshots for backups
```

### Shared Files Pattern
```yaml
# Use ReadWriteMany access mode
# NFS or cloud file storage
# Multiple pods can access
```

### Cache Pattern
```yaml
# Use emptyDir for temporary cache
# Or local SSD for performance
# Data loss acceptable on pod restart
```

## Practice Exercises

### Exercise 1: Create PV and PVC

```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: task-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
  - ReadWriteOnce
  hostPath:
    path: /mnt/data

---
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: task-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```bash
kubectl apply -f pv.yaml
kubectl apply -f pvc.yaml
kubectl get pv,pvc
```

### Exercise 2: Use PVC in Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pvc-pod
spec:
  containers:
  - name: nginx
    image: nginx
    volumeMounts:
    - name: storage
      mountPath: /usr/share/nginx/html
  volumes:
  - name: storage
    persistentVolumeClaim:
      claimName: task-pvc
```

### Exercise 3: Dynamic Provisioning

```bash
# Create StorageClass (if not exists)
kubectl get storageclass

# Create PVC with storageClassName
# PV automatically created
```

## Key Takeaways

- Volumes provide storage to Pods
- PVs are cluster resources, PVCs are requests for storage
- StorageClasses enable dynamic provisioning
- Use appropriate access modes and reclaim policies
- StatefulSets with volumeClaimTemplates for stateful apps
- CSI drivers provide standardized storage interface
- Consider performance, durability, and cost when choosing storage
