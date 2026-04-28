# Troubleshooting and Practical Use Cases

## Production Debugging Flow

Use layers. Do not guess.

```text
1. Is the hostname resolving?
2. Is the IP reachable?
3. Is the port reachable?
4. Does TLS succeed?
5. Does HTTP routing succeed?
6. Is the backend healthy?
7. Are dependencies healthy?
8. What changed recently?
```

## Useful Commands

```bash
# DNS
dig api.example.com
nslookup api.example.com

# Connectivity
ping 10.0.1.4
nc -vz api.example.com 443

# Route path
traceroute api.example.com

# HTTP and TLS
curl -v https://api.example.com/health
openssl s_client -connect api.example.com:443 -servername api.example.com

# Local ports
lsof -iTCP -sTCP:LISTEN -n -P

# Linux network view
ip addr
ip route
ss -tunap
```

## Use Case 1: API Is Down for Some Users

Symptoms:

- users in one region report failure
- internal health checks are green

Possible causes:

- DNS geo-routing issue
- CDN/edge outage
- regional backend failure
- WAF rule false positive
- ISP route issue

Debug:

- compare DNS answers from different regions
- check load balancer backend health
- inspect edge/WAF logs
- use synthetic probes from multiple locations

Azure angle:

```text
Check Azure Front Door origin health, WAF logs, route configuration, and backend regional availability.
```

## Use Case 2: Service Can Reach Database by IP but Not Hostname

Likely DNS issue.

Check:

- private DNS zone linked to VNet
- record exists
- resolver configuration
- search suffixes
- split-horizon DNS behavior

Azure angle:

```text
For Private Endpoint, verify the privatelink DNS zone is linked to the VNet and has the correct A record.
```

## Use Case 3: 504 Gateway Timeout

A gateway timed out waiting for upstream.

Possible causes:

- app is slow
- dependency is slow
- wrong timeout settings
- connection pool exhaustion
- backend not accepting connections
- load balancer points to wrong port

Debug:

- check gateway logs
- check upstream latency
- compare app logs with request ID
- test backend directly
- review timeout hierarchy

Timeout hierarchy should usually be:

```text
client timeout > gateway timeout > app timeout > downstream timeout
```

## Use Case 4: Random Connection Resets

Possible causes:

- idle timeout on load balancer/NAT/proxy
- server restarts
- pod/VM termination without draining
- TLS termination issue
- too-small connection pool

Fixes:

- tune keepalive
- graceful shutdown
- connection draining
- retry idempotent requests
- align idle timeouts

## Use Case 5: Slow API After Moving to HTTPS

Possible causes:

- new TLS handshake for every request
- no connection reuse
- expensive certificate chain validation
- proxy misconfiguration
- HTTP/2 disabled

Fix:

- enable keep-alive
- use connection pooling
- enable HTTP/2 where useful
- terminate TLS at a suitable proxy

## Use Case 6: Azure Private Service Cannot Be Reached

Scenario:

```text
VM in VNet cannot reach Azure Storage through Private Endpoint.
```

Check:

- private endpoint is approved
- private DNS zone is linked
- hostname resolves to private IP
- NSG allows traffic
- route table does not force traffic incorrectly
- storage firewall allows private endpoint

Command shape:

```bash
nslookup mystorage.blob.core.windows.net
nc -vz mystorage.blob.core.windows.net 443
curl -v https://mystorage.blob.core.windows.net
```

## Use Case 7: Kubernetes Service Works Internally but Not Externally

Check:

- service type
- ingress resource
- ingress controller logs
- load balancer IP
- DNS record
- TLS secret
- network policy
- cloud load balancer health probe

Azure angle:

```text
For AKS, inspect the Azure Load Balancer or Application Gateway backend health and ensure NSG rules allow the probe path.
```

## Observability Signals

Track:

- DNS lookup time
- TCP connect time
- TLS handshake time
- time to first byte
- total request time
- 4xx/5xx rate
- reset count
- timeout count
- retransmissions
- load balancer health
- WAF blocks

## Practical Checklist Before Production

- CIDR plan avoids overlap
- all subnets sized for growth
- ingress and egress paths are documented
- NSG/firewall rules are least privilege
- private endpoints have DNS configured
- load balancer health checks are meaningful
- timeouts and retries are aligned
- TLS certificates are monitored for expiry
- dashboards separate DNS/connect/TLS/app latency
- runbook includes exact commands

