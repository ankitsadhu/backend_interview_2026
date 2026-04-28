# Advanced MANG Networking Scenarios

This file is for the questions that separate memorized networking knowledge from production-grade reasoning.

Use this structure in interviews:

```text
packet path -> layer involved -> failure modes -> evidence/commands -> fix -> prevention
```

## 1. Full Packet Path: Browser to Backend API

Scenario:

```text
User opens https://api.company.com/orders/123
```

Packet path:

```text
Browser
  |
  | DNS lookup for api.company.com
  v
Recursive DNS resolver
  |
  v
Azure Front Door edge
  |
  | TLS termination, WAF, routing
  v
Regional Application Gateway
  |
  | optional TLS re-encryption
  v
AKS ingress / App Service / VM backend
  |
  v
Service code
  |
  v
Private Endpoint to database/cache/storage
```

What can fail at each step:

| Step | Possible Failure |
|------|------------------|
| DNS | stale record, wrong CNAME, private DNS conflict |
| TCP | firewall, NSG, route table, backend port closed |
| TLS | expired cert, SNI mismatch, missing intermediate cert |
| Front Door | WAF block, unhealthy origin, wrong route |
| App Gateway | bad backend pool, probe failure, TLS mismatch |
| AKS/App | pod not ready, ingress rule wrong, service selector wrong |
| DB/cache | Private DNS, NSG, firewall, connection pool exhaustion |

Strong interview answer:

```text
I would not start by restarting services. I would split the path into DNS, TCP, TLS, proxy routing, backend health, and dependency health, then use logs and probes at each boundary.
```

## 2. TCP Internals That Matter in Production

### TIME_WAIT

After a TCP connection closes, one side may stay in `TIME_WAIT` to handle delayed packets safely.

Why it matters:

- many short-lived connections create many `TIME_WAIT` sockets
- can contribute to ephemeral port pressure
- usually fixed with connection reuse, not random OS tuning first

Command:

```bash
ss -tan state time-wait | wc -l
```

### Keepalive

TCP keepalive detects dead idle connections.

Application-level keepalive or health pings may also exist.

Interview nuance:

```text
TCP keepalive and HTTP keep-alive are different. TCP keepalive checks idle connection liveness. HTTP keep-alive means reuse the same TCP connection for multiple HTTP requests.
```

### Retransmission

TCP retransmits lost packets.

Symptoms:

- increased latency
- reduced throughput
- request timeouts

Possible causes:

- packet loss
- overloaded network device
- bad route
- MTU issues
- congested link

Useful signals:

```bash
netstat -s | grep -i retrans
ss -ti
```

## 3. Ephemeral Port and SNAT Exhaustion

When a client opens outbound TCP connections, it uses ephemeral source ports.

Example:

```text
10.0.1.5:51001 -> 52.10.10.8:443
10.0.1.5:51002 -> 52.10.10.8:443
```

SNAT exhaustion happens when many private clients share limited outbound translated ports.

Symptoms:

- intermittent outbound failures
- connection timeouts
- failures increase under load
- CPU may look normal
- retries make it worse

Common causes:

- no connection pooling
- too many short-lived outbound connections
- high fan-out to same destination
- NAT Gateway or load balancer outbound SNAT limits
- retry storm after downstream slowness

Azure fixes:

- use Azure NAT Gateway for more scalable outbound SNAT
- reuse connections
- increase backend public IPs where appropriate
- reduce aggressive retries
- use private endpoints for Azure PaaS dependencies
- monitor SNAT connection count and failed connections

Interview answer:

```text
If failures are intermittent and outbound-only under load, I would consider SNAT exhaustion early, especially in Azure App Service, AKS, or VMs behind a shared outbound path.
```

## 4. DNS Edge Cases

### Split-Horizon DNS

The same hostname resolves differently depending on where the query comes from.

Example:

```text
Inside VNet:  db.company.com -> 10.10.2.4
Internet:     db.company.com -> no record or public IP
```

Useful for private services, but confusing during debugging.

### Negative Caching

If DNS returns NXDOMAIN, resolvers may cache that negative answer.

Problem:

```text
You create the correct record, but some clients still think it does not exist.
```

### CNAME Chains

Long CNAME chains increase lookup complexity and can break if one link is wrong.

Example:

```text
api.company.com -> app.azurefd.net -> regional-app.contoso.com
```

### Private Endpoint DNS Trap

For Azure Private Endpoint, the public hostname often must resolve to a private IP from inside the VNet.

Example:

```text
mystorage.blob.core.windows.net -> mystorage.privatelink.blob.core.windows.net -> 10.10.5.4
```

If DNS resolves to the public IP, traffic may fail due to storage firewall rules.

## 5. TLS, SNI, and mTLS

### SNI

Server Name Indication lets a client tell the server which hostname it wants during TLS handshake.

Why it matters:

- multiple HTTPS sites can share one IP
- load balancers choose certificates using hostname
- missing SNI can return the wrong certificate

Debug:

```bash
openssl s_client -connect api.company.com:443 -servername api.company.com
```

### Certificate Chain

Clients need a chain from server certificate to trusted root CA.

Common failures:

- expired leaf certificate
- missing intermediate certificate
- wrong hostname
- private CA not trusted

### mTLS

Mutual TLS means both client and server present certificates.

Use cases:

- service-to-service authentication
- partner APIs
- zero-trust internal networks

Pitfalls:

- client cert rotation
- CA trust distribution
- proxy termination hiding client identity
- hard-to-debug handshake failures

## 6. MTU and Fragmentation

MTU is the maximum packet size on a link.

If packets are too large:

- they may be fragmented
- they may be dropped if fragmentation is blocked
- TLS or VPN traffic may hang mysteriously

Classic symptom:

```text
Small requests work. Large requests hang or time out.
```

Why VPN/overlay networks matter:

- encapsulation adds headers
- effective MTU becomes smaller
- Kubernetes overlay networks can expose this

Debug idea:

```bash
ping -D -s 1472 example.com
```

Exact flags vary by OS.

## 7. Kubernetes Networking Deep Dive

Core objects:

- Pod IP
- Service ClusterIP
- NodePort
- LoadBalancer Service
- Ingress
- NetworkPolicy
- CNI plugin

Traffic path example:

```text
Client
  |
  v
Azure Load Balancer / Application Gateway
  |
  v
Ingress controller pod
  |
  v
Kubernetes Service
  |
  v
Pod IP
```

Common failure modes:

- service selector does not match pods
- pod is running but not ready
- ingress host/path mismatch
- TLS secret wrong
- NetworkPolicy blocks traffic
- cloud health probe path blocked
- CNI IP exhaustion
- CoreDNS failure

Commands:

```bash
kubectl get svc,ingress,endpoints
kubectl describe ingress <name>
kubectl get endpoints <service-name>
kubectl logs -n ingress-nginx deploy/ingress-nginx-controller
kubectl exec -it <pod> -- nslookup kubernetes.default
kubectl exec -it <pod> -- curl -v http://service.namespace.svc.cluster.local
```

MANG-style nuance:

```text
Kubernetes Service discovery may work while external ingress fails, because they are different paths with different DNS, load balancer, TLS, and routing behavior.
```

## 8. Azure Hub-Spoke and Forced Tunneling

Hub-spoke design:

```text
Spoke VNets -> Hub VNet -> Azure Firewall -> internet/on-prem
```

The hub hosts shared network services:

- Azure Firewall
- VPN Gateway
- ExpressRoute Gateway
- Private DNS Resolver
- Bastion
- monitoring/logging

Forced tunneling:

```text
0.0.0.0/0 route from spoke subnet -> Azure Firewall or NVA
```

Benefits:

- centralized inspection
- consistent egress control
- audit logs

Failure modes:

- asymmetric routing
- missing return route
- firewall denies required Azure service
- DNS points to private IP but route sends traffic wrong way
- UDR overrides default platform route unexpectedly

Interview answer:

```text
In Azure, I would inspect effective routes on the NIC because user-defined routes, peering, VPN, ExpressRoute, and service endpoints can change the actual path.
```

## 9. ExpressRoute vs VPN

### VPN Gateway

- encrypted tunnel over public internet
- faster to set up
- lower cost
- more variable latency

### ExpressRoute

- private dedicated connectivity through provider
- more predictable latency and bandwidth
- higher cost and setup complexity
- does not encrypt by default at the same level as VPN

Use ExpressRoute for:

- regulated enterprise connectivity
- large data transfer
- predictable hybrid network performance

Use VPN for:

- smaller workloads
- backup connectivity
- faster setup
- cost-sensitive environments

## 10. Designing a Secure Internal API on Azure

Goal:

```text
Expose internal API to employees and internal services only.
```

Design:

```text
Employee device
  |
  v
VPN / ZTNA / ExpressRoute
  |
  v
Private DNS
  |
  v
Internal Application Gateway
  |
  v
Private AKS/App Service
  |
  v
Private Endpoint to database
```

Controls:

- no public backend IP
- private DNS zone
- NSG least privilege
- Azure Firewall for egress
- WAF if HTTP exposure exists
- Entra ID authentication
- mTLS for service-to-service where needed
- logging at gateway, firewall, app, and identity layers

Tradeoff:

```text
Private networking reduces exposure but increases DNS, routing, and operational complexity.
```

## 11. Designing Global Low-Latency API

Goal:

```text
Serve users across regions with low latency and high availability.
```

Design:

```text
Users
  |
  v
Azure Front Door + WAF
  |
  +-- Region A App Gateway -> AKS/App Service -> regional data store
  +-- Region B App Gateway -> AKS/App Service -> regional data store
```

Key decisions:

- active-active or active-passive
- data replication strategy
- regional failover
- cache strategy
- DNS/edge routing
- sticky sessions avoided where possible
- global rate limiting
- observability per region

Cross question:

```text
If region A fails, does data also fail over safely?
```

A senior answer discusses both network failover and data consistency.

## 12. Debugging Playbooks

### Service Unreachable

```text
DNS -> route -> firewall/NSG -> port listener -> load balancer health -> app logs
```

### Slow Service

```text
DNS time -> connect time -> TLS time -> gateway time -> app time -> dependency time
```

### Intermittent Failure

```text
load balancer backend distribution
deployment changes
connection pool
NAT/SNAT
DNS cache split
zone/regional issue
retry storm
```

### Works by IP, Fails by Name

```text
DNS record
private DNS zone link
search suffix
split-horizon DNS
TLS hostname mismatch
proxy route based on Host header
```

### Works Internally, Fails Externally

```text
public DNS
edge/WAF
public load balancer
TLS cert
ingress route
health probe
NSG/firewall
```

## Final MANG Checklist

Before saying a networking design is production-ready, cover:

- CIDR plan and non-overlap
- ingress path
- egress path
- DNS design
- TLS/certificate lifecycle
- private access to data stores
- load balancer health checks
- timeout and retry policy
- observability and runbooks
- failure domains: zone, region, dependency, network edge
- security controls: WAF, firewall, NSG, identity, audit logs

