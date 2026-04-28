# Computer Networks Interview Questions

## Beginner

### 1. What happens when you type a URL in the browser?

The browser resolves the domain with DNS, opens a TCP connection to the server, performs a TLS handshake for HTTPS, sends an HTTP request, receives the response, and renders it.

### 2. What is the difference between IP address and port?

IP identifies the host or network interface. Port identifies the process or service on that host.

### 3. What is DNS?

DNS maps human-readable names like `api.example.com` to IP addresses and other records.

### 4. What is the difference between public and private IP?

Public IPs are routable on the internet. Private IPs are used inside private networks and are not directly internet-routable.

### 5. What is NAT?

NAT rewrites source or destination addresses/ports, commonly allowing private machines to access the internet through shared public IPs.

## Intermediate

### 6. Explain TCP three-way handshake.

TCP connection setup uses SYN, SYN-ACK, and ACK. It establishes that both sides can send and receive before application data flows.

### 7. TCP vs UDP?

TCP is connection-oriented and provides reliable ordered delivery. UDP is connectionless and does not guarantee delivery or ordering.

### 8. Why is connection pooling important?

It avoids repeated TCP and TLS handshakes, reduces latency, and prevents excessive connection churn.

### 9. What is CIDR?

CIDR expresses an IP range using a prefix length, such as `10.0.1.0/24`.

### 10. What is the difference between L4 and L7 load balancers?

L4 load balancers route based on IP, port, and protocol. L7 load balancers understand application protocols like HTTP and can route by host, path, headers, or cookies.

### 11. What is TLS?

TLS provides encryption, integrity, and server authentication for network communication.

### 12. What is a reverse proxy?

A reverse proxy receives client requests and forwards them to backend services, often handling TLS, routing, retries, timeouts, and observability.

## Advanced

### 13. Why can DNS changes take time to propagate?

DNS answers are cached by clients, recursive resolvers, and intermediate systems according to TTL values. Some clients may cache longer than expected.

### 14. Why can ping fail but HTTPS work?

Ping uses ICMP, which may be blocked. HTTPS uses TCP port 443, which may still be allowed.

### 15. Why might an API return 502?

A gateway or proxy could not get a valid response from upstream. Causes include upstream crash, wrong port, TLS mismatch, bad response, or proxy routing error.

### 16. Why might an API return 504?

The gateway timed out waiting for upstream. Causes include slow app, blocked dependency, connection pool exhaustion, or timeout mismatch.

### 17. What is head-of-line blocking?

It happens when one delayed packet or stream blocks progress of later data. TCP can suffer from this because it guarantees ordered delivery.

### 18. What is SNAT port exhaustion?

It occurs when too many outbound connections share limited source NAT ports, causing new connections to fail or hang.

### 19. How would you debug high API latency?

Break latency into DNS lookup, TCP connect, TLS handshake, gateway time, upstream app time, database/downstream time, and response transfer time.

### 20. How would you design secure network access to a database?

Place the database in a private subnet or private endpoint, deny public access, allow only app subnet traffic, use TLS, enforce identity/auth, and log access.

## Azure Cross Questions

### 21. What is a VNet?

A VNet is an isolated private network in Azure where resources can communicate using private IP addresses.

### 22. NSG vs Azure Firewall?

NSG provides subnet/NIC-level allow/deny rules. Azure Firewall is a centralized managed firewall with richer logging, filtering, threat intelligence, and routing control.

### 23. Private Endpoint vs Service Endpoint?

Private Endpoint exposes an Azure PaaS service as a private IP in your VNet. Service Endpoint keeps the public endpoint but restricts access to selected VNets.

### 24. Application Gateway vs Azure Front Door?

Application Gateway is regional L7 load balancing and WAF. Front Door is global edge L7 routing, acceleration, CDN-like behavior, and WAF.

### 25. Traffic Manager vs Front Door?

Traffic Manager is DNS-based routing and does not proxy traffic. Front Door proxies HTTP/S traffic at the edge.

### 26. Why can Azure Private Endpoint fail even though the endpoint exists?

The private DNS zone may not be linked, the hostname may resolve to public IP, the endpoint may not be approved, NSG/routes may block traffic, or the service firewall may deny access.

### 27. How do you troubleshoot Azure VM connectivity?

Check DNS, effective NSG rules, effective routes, VM firewall, service listener, load balancer health probe, NAT path, and Network Watcher connectivity tests.

## Scenario Questions

### 28. Users report intermittent timeouts. What do you check?

Check load balancer health, app latency, dependency latency, connection pool usage, retry storms, NAT/SNAT exhaustion, DNS changes, deployment events, and regional metrics.

### 29. A service works locally but not from AKS. What could be wrong?

Different DNS, network policy, NSG, route table, private endpoint DNS, service account identity, egress firewall, or proxy configuration.

### 30. Your backend can connect to Redis sometimes but gets random resets. Why?

Possible idle timeout, Redis max clients, connection pool churn, NAT timeout, pod restarts, load balancer reset, or network policy changes.

### 31. You need to expose an internal API only to company network users. Design it.

Use private networking, VPN or ExpressRoute, internal load balancer or private Application Gateway, private DNS, identity-aware authentication, NSG/firewall least privilege, and logging.

### 32. You need global low-latency access to a web app on Azure. What do you use?

Use Azure Front Door for global edge routing/WAF, regional backends behind Application Gateway or App Service/AKS, health probes, TLS, and autoscaling.

## MANG Follow-Up Chains

### 33. Walk me through the packet path for `https://api.company.com/orders`.

Start with DNS resolution, then TCP connection, TLS handshake, HTTP request to edge/load balancer, WAF or routing decision, backend selection, service processing, dependency calls, and response back through the same or proxied path.

Good follow-up detail:

```text
At each boundary I would identify what terminates the connection: browser to edge, edge to regional gateway, gateway to service, service to database/cache.
```

### 34. Follow-up: where can latency be introduced in that path?

DNS lookup, TCP connect, TLS handshake, WAF inspection, load balancer queueing, backend processing, database/cache calls, retries, response transfer, and client-side rendering.

### 35. Follow-up: how would you prove whether latency is network or app?

Use timing breakdowns from `curl`, gateway/load balancer logs, distributed tracing, backend request duration, dependency metrics, and packet/connect metrics. If connect/TLS time is low but upstream app time is high, it is likely application or dependency latency.

### 36. Why can an application have high latency even when bandwidth is high?

Latency and bandwidth are different. A high-bandwidth link can still have high round-trip time, packet loss, congestion, slow TLS handshakes, or backend queueing.

### 37. Explain ephemeral port exhaustion.

Clients use ephemeral source ports for outbound connections. If too many short-lived outbound connections are created, the client or NAT device can run out of available translated ports, causing intermittent connection failures.

### 38. Follow-up: how do you fix ephemeral port or SNAT exhaustion?

Reuse connections, tune connection pools, reduce aggressive retries, add NAT Gateway or more outbound IP capacity, use private endpoints for Azure services, and monitor outbound connection metrics.

### 39. What is the difference between HTTP keep-alive and TCP keepalive?

HTTP keep-alive reuses a TCP connection for multiple HTTP requests. TCP keepalive sends low-level probes to detect whether an idle connection is still alive.

### 40. Why does `TIME_WAIT` exist?

It lets TCP handle delayed packets from a recently closed connection and prevents old packets from being mistaken for a new connection using the same tuple.

### 41. What is SNI?

SNI lets a TLS client tell the server which hostname it is connecting to during the TLS handshake. This allows multiple certificates and HTTPS sites to share an IP.

### 42. Follow-up: why can TLS fail through a load balancer?

The load balancer may present the wrong certificate, miss an intermediate certificate, require unsupported TLS versions, route by SNI incorrectly, fail backend TLS validation, or terminate/re-encrypt TLS incorrectly.

### 43. What is mTLS and when would you use it?

mTLS means both client and server present certificates. Use it for service-to-service authentication, partner APIs, and zero-trust internal networks.

### 44. What is split-horizon DNS?

Split-horizon DNS returns different answers depending on where the query originates, such as private IPs inside a VNet and public records outside.

### 45. Why can a service work by IP but fail by hostname?

DNS may resolve incorrectly, private DNS may not be linked, TLS hostname validation may fail, or an HTTP proxy/load balancer may route based on the `Host` header.

### 46. What is MTU and how can it break applications?

MTU is maximum packet size on a link. If packets exceed the effective MTU and fragmentation fails, small requests may work while larger requests hang or time out.

### 47. In Kubernetes, why can a Service have no endpoints?

The Service selector may not match pod labels, pods may not be ready, or pods may be in another namespace.

### 48. Kubernetes Service vs Ingress?

Service exposes a stable virtual IP inside the cluster or via cloud load balancer. Ingress provides HTTP routing by host/path through an ingress controller.

### 49. Kubernetes NetworkPolicy vs Azure NSG?

NetworkPolicy controls pod-level traffic inside Kubernetes if supported by the CNI. NSG controls subnet/NIC-level traffic in Azure.

### 50. Azure UDR vs NSG?

UDR controls where traffic goes. NSG controls whether traffic is allowed. A route may send traffic to the right place, but an NSG can still block it.

### 51. What is forced tunneling in Azure?

Forced tunneling sends default outbound traffic, often `0.0.0.0/0`, through a firewall, NVA, VPN, or ExpressRoute path for centralized inspection.

### 52. Why can forced tunneling break Azure workloads?

It can route traffic asymmetrically, block required Azure service endpoints, break DNS assumptions, or send private endpoint traffic through an unintended firewall path.

### 53. ExpressRoute vs VPN?

VPN is encrypted connectivity over the public internet and is easier/cheaper to set up. ExpressRoute provides private dedicated connectivity with more predictable performance but higher cost and complexity.

### 54. How would you design private access to Azure Storage?

Use Private Endpoint, disable or restrict public network access, configure the correct Private DNS zone, link it to the VNet, allow only required identities, and validate from a workload using DNS and TCP checks.

### 55. What would you check if Azure Private Endpoint DNS resolves to a public IP?

Check private DNS zone existence, VNet link, A record, conditional forwarding, custom DNS resolver, and whether the client is querying the expected DNS server.

### 56. How would you debug an AKS app reachable internally but not externally?

Check ingress, service endpoints, pod readiness, ingress controller logs, cloud load balancer health probes, public/private DNS, TLS secret, NSG rules, and Application Gateway/Front Door backend health if used.

### 57. How do retries make networking incidents worse?

Retries can amplify load, exhaust connection pools, consume SNAT ports, increase queueing, and turn a small downstream slowdown into a system-wide outage.

### 58. What is a good timeout strategy?

Set explicit connect/read/request timeouts, keep client timeout larger than gateway timeout, keep gateway timeout larger than app/downstream timeout, and retry only idempotent operations with backoff and jitter.

### 59. How would you explain 99th percentile latency in networking terms?

Tail latency often comes from rare slow paths: packet loss, retransmissions, connection setup, DNS cache misses, cold TLS handshakes, overloaded backend instances, or slow dependencies.

### 60. How do you make a network design observable?

Collect DNS timing, connect time, TLS time, gateway latency, upstream latency, status codes, resets, timeouts, retransmissions, load balancer health, firewall denies, WAF blocks, and trace IDs across services.

## Rapid Fire

### Does HTTPS always mean the backend is secure?

No. HTTPS protects transport. You still need auth, authorization, input validation, secrets management, and secure backend configuration.

### Is a load balancer enough for high availability?

No. You need healthy independent backends, multi-zone or multi-region design, health checks, autoscaling, and failover.

### Can two VNets with overlapping CIDR be peered?

No, overlapping address spaces cause routing ambiguity and peering is not allowed in normal Azure VNet peering.

### Why use private DNS?

To resolve internal or private endpoint hostnames to private IPs from inside selected networks.

### What is the most common networking interview mistake?

Jumping to conclusions instead of debugging layer by layer.

### What is the strongest networking interview habit?

Name the exact layer and boundary you are debugging before proposing a fix.

## Final Interview Tip

For MANG-level answers, use this pattern:

```text
First principles -> exact network layer -> likely failure modes -> commands/metrics -> production-safe fix
```
