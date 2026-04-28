# Computer Networks Study Guide

> Beginner-to-advanced networking path for backend, DevOps, cloud, and MANG-level interviews.

Networking interviews test whether you can reason from first principles when a real production system is slow, unreachable, insecure, or failing under load.

## Structure

| # | File | Topics | Level |
|---|------|--------|-------|
| 01 | [Fundamentals](./01_fundamentals.md) | OSI/TCP-IP models, packets, ports, latency, bandwidth, NAT, firewalls | Beginner |
| 02 | [TCP, UDP, and Sockets](./02_tcp_udp_and_sockets.md) | TCP handshake, reliability, congestion, UDP, sockets, connection pooling | Beginner-Intermediate |
| 03 | [DNS, HTTP, and TLS](./03_dns_http_tls.md) | DNS resolution, HTTP/1.1, HTTP/2, HTTP/3, TLS handshake, certificates | Intermediate |
| 04 | [IP, Subnetting, Routing, and Load Balancing](./04_ip_subnetting_routing_load_balancing.md) | CIDR, routing tables, gateways, L4/L7 load balancing, reverse proxies | Intermediate-Advanced |
| 05 | [Azure Networking Examples](./05_azure_networking_examples.md) | VNet, subnets, NSG, Application Gateway, Front Door, Private Endpoint, AKS networking | Intermediate-Advanced |
| 06 | [Troubleshooting and Practical Use Cases](./06_troubleshooting_and_practical_use_cases.md) | Debug flow, commands, common outages, latency, packet loss, DNS, TLS, Azure cases | Advanced |
| 07 | [Interview Questions](./07_interview_questions.md) | Cross questions, scenario questions, rapid-fire answers, system design prompts | All Levels |
| 08 | [Advanced MANG Scenarios](./08_advanced_mang_scenarios.md) | packet path, SNAT, DNS edge cases, TLS/SNI/mTLS, MTU, AKS, hub-spoke, ExpressRoute | Advanced |

## Study Path

1. Learn the TCP/IP model and what happens when a client calls a service.
2. Understand IP addresses, ports, DNS, TCP, TLS, and HTTP deeply.
3. Practice subnetting and routing until CIDR feels natural.
4. Learn load balancing at L4 and L7.
5. Map those basics to Azure: VNet, subnets, NSG, App Gateway, Front Door, Private Link.
6. Study advanced packet-path, Azure, and Kubernetes scenarios.
7. Finish with troubleshooting scenarios and cross questions.

## Core Mental Model

```text
User
  |
  v
DNS lookup
  |
  v
TCP/TLS connection
  |
  v
HTTP request
  |
  v
Load balancer / proxy
  |
  v
Service
  |
  v
Database / cache / downstream service
```

In interviews, always separate:

- name resolution
- reachability
- connection establishment
- encryption
- application protocol
- backend health
- observability

## Why This Matters for MANG Interviews

Many candidates memorize OSI layers.

Stronger candidates can explain:

- why DNS works locally but fails in Kubernetes or Azure
- why TCP latency affects API tail latency
- why a service is reachable by IP but not by hostname
- why TLS can fail even when the port is open
- why L4 and L7 load balancers behave differently
- how NSG, route tables, NAT, and private endpoints interact
- how to debug production connectivity without guessing
- how SNAT exhaustion, SNI, MTU, split DNS, and Kubernetes networking cause real outages
