# IP, Subnetting, Routing, and Load Balancing

## CIDR

CIDR notation defines a network range.

Example:

```text
10.0.1.0/24
```

`/24` means the first 24 bits are the network part. The remaining 8 bits are host addresses.

Approximate usable sizes:

| CIDR | Addresses |
|------|-----------|
| /16 | 65,536 |
| /20 | 4,096 |
| /24 | 256 |
| /25 | 128 |
| /26 | 64 |
| /27 | 32 |

Cloud providers reserve some addresses in each subnet, so usable IP count is lower.

## Subnetting Mental Model

A VNet or network is a big block.

Subnets are smaller blocks:

```text
10.0.0.0/16
  |
  +-- 10.0.1.0/24 frontend
  +-- 10.0.2.0/24 backend
  +-- 10.0.3.0/24 database
```

Why subnet:

- security boundaries
- routing control
- blast-radius reduction
- load balancer and gateway placement
- IP planning

## Routing

A route tells traffic where to go.

Route table idea:

| Destination | Next Hop |
|-------------|----------|
| 10.0.0.0/16 | local VNet |
| 0.0.0.0/0 | internet/NAT/firewall |
| 10.2.0.0/16 | peering/VPN |

Most specific route wins.

Example:

```text
10.0.2.5 matches 10.0.0.0/16 and 10.0.2.0/24.
The /24 route wins.
```

## Gateway

A gateway connects networks.

Examples:

- internet gateway
- NAT gateway
- VPN gateway
- ExpressRoute gateway
- application gateway

Do not use the word "gateway" loosely in interviews. Clarify whether it is network routing, NAT, VPN, or application-layer proxying.

## ARP

ARP maps IP addresses to MAC addresses inside a local network.

You rarely debug ARP directly in managed cloud platforms, but it explains why L2 and L3 are different.

## L4 vs L7 Load Balancing

### L4 Load Balancer

Works with TCP/UDP.

Decisions based on:

- IP
- port
- protocol

Use cases:

- database proxying
- TCP services
- simple regional traffic distribution

### L7 Load Balancer

Works with application protocols like HTTP.

Decisions based on:

- hostname
- path
- headers
- cookies
- HTTP method

Use cases:

- API routing
- TLS termination
- WAF
- path-based routing

## Reverse Proxy

A reverse proxy receives requests on behalf of backend services.

Examples:

- NGINX
- Envoy
- HAProxy
- Azure Application Gateway
- Azure Front Door

It may handle:

- TLS termination
- routing
- retries
- timeouts
- compression
- auth integration
- observability

## Health Checks

Load balancers need health checks to decide whether a backend should receive traffic.

Bad health check:

```text
GET /
```

Better:

```text
GET /health/ready
```

Readiness should check whether the app can actually serve traffic, but should avoid expensive downstream dependency calls on every probe.

## Sticky Sessions

Sticky sessions route a client to the same backend repeatedly.

Useful when:

- legacy app stores session in memory
- WebSocket sessions need stability

Tradeoffs:

- uneven load
- harder scaling
- failure impact

Better design:

```text
stateless service + shared session store/cache
```

## Practical Example: API Behind Load Balancer

```text
Client
  |
  v
DNS: api.example.com
  |
  v
L7 load balancer
  |
  +-- /users  -> user-service
  +-- /orders -> order-service
  +-- /admin  -> admin-service
```

## Cross Questions

### Can two subnets have overlapping CIDR ranges?

Not inside the same VNet/network. Peered networks should also avoid overlap because routing becomes ambiguous.

### Why might a backend be healthy but users still get 502?

The health endpoint may be too shallow, the proxy may have timeout/TLS/header issues, or only some routes are broken.

### Why use L7 instead of L4?

Use L7 when you need HTTP-aware routing, TLS termination, WAF, redirects, header-based rules, or path-based routing.

### Why use L4 instead of L7?

Use L4 for non-HTTP protocols, lower overhead, pass-through TLS, or simple TCP/UDP load balancing.

