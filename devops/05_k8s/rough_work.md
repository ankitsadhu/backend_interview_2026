was created by google, open source container orchestration tool.

K8s -> Container + Orchestration (Difficult setup, has alot of features)
Docker Swarm -> by docker (Easy setup & started, lacks advance features)
MESOS -> Apache (Difficult setup, has alot of features)


Containers are isolated envs, have their own `process`, `networks`, `mounts` & shares same underline OS kernel.

Docker utilises LXC containers. Setuping these LXC containers are hard, docker provider high level controlling

OS 
- kernel
- software

Unlike hypervisors, docker is not meant to virtualise & run different os & kernels on same hardware.

What is Hypervisior in a VM?


Images
Containers



## Container Orechestration:

Scale up / Scale down Nodes - load increase / decrease

## Architecture
1. Node (Worker Machine) ealier known as minion: a machine physical or virtual on which k8s is installed. Here containers will be launched by K8s
2. Cluster: is a set of nodes grouped together, if any goes down, other will take care.
3. Master (Node configured as master): It watches over the other nodes


## K8s Components
1. API Server: Acts as frontend for k8s, users, management devices, commmand line interfaces, all talk to api server.
2. etcd Service: Distributed Reliable KV store used by K8s to store all data used to manage the cluster. Responsible for implementing locks within the cluster, so that there is no conflict between the master.
3. kubelet Service: is the agent that runs on each node in the cluster. The agent is responsible for making sure that the containers are running on the node as expected. 
4. Container Runtime
5. Controller: brain behind orchestration, if anything goes down, spins new container 

6. Scheduler: Distributing work/container across nodes


## Master vs Worker Nodes
- Master: has the Kube API Server
- Worker: Kubelet Agent
- etcd saves the {master: {worker1, worker2}, master2}

## kubectl
`kubectl run hello-minikube`
`kubectl cluster-info`
`kubectl get nodes`

## PODS
Prerequists: app is build as a docker img & uploaded to docker hub, so k8s can pull it down

K8s doesnot deploy containers directly on the worker nodes. The containers are encapsulated into a K8s object known as `Pods` (single instance of an application / smallest obj that can be created in K8s).

A Node can have multiple pods, if too many users increases, current nodes doesnot have enough capacity, add another node to cluster.

Though a single pod can have multiple containers, but we dont do that, unless helper container (processor), both can talk to each other using localhost, & same storage space - sidecar (Rare usecase)

```bash
docker version
docker run python-app
docker run helper-app -link app1
```


- `kubectl run nginx --image=nginx ` -> creates a pod -> deployes an img of the nginx docker img from docker hub (public or private)

- `kubectl get pods` - status of all pods

- `kubectl describe pod nginx`






## YAML Files (Config files)

```yaml
Fruit: Apple # must have space between : , diff key & value
Vegetables: Carrot
Laptops:    
-   Macbook # - represent an element of array
-   Dell XPS
-   Lenovo Legion
Banana:     # Dict are ordered collection, arrays are not 
    Calories: 105 
    Fat: 0.4 g
    Carbs: 27 g
Employee: # dict of dict { name: Ankit , location: {lat, long}}
    name: Ankit
    location:
        lat: 107
        long: 108
```



## k8s on Cloud
Self hosted - AWS using kops or KubeOne, on VM
Hosted (Managed) - K8s as a Service, e.g 
                    Google Container Enginee (GKE)
                    Azure K8s Service (AKS)
                    Amazon Elastic Kubernetes Service (EKS)

Create K8s cluster -> Node Size, Node Count -> Create Storage 
