# Networking Fundamentals

## What Is a Network?

A network lets machines exchange data.

At the most practical level:

```text
process -> socket -> OS network stack -> network interface -> routers -> remote host
```

An application does not usually send "a request" directly. It writes bytes to a socket. The operating system breaks those bytes into packets and sends them across the network.

## Packet Mental Model

A packet has:

- source address
- destination address
- protocol metadata
- payload

Example:

```text
From: 10.0.1.4:53218
To:   10.0.2.9:443
Protocol: TCP
Payload: encrypted HTTPS bytes
```

## OSI Model vs TCP/IP Model

The OSI model is useful for interviews, but real systems often use the TCP/IP model.

| OSI Layer | Example | Interview Use |
|----------|---------|---------------|
| 7 Application | HTTP, DNS, SMTP | API behavior, status codes |
| 6 Presentation | TLS, encoding | encryption, certificates |
| 5 Session | connection/session state | less directly used |
| 4 Transport | TCP, UDP | ports, reliability, retries |
| 3 Network | IP, ICMP | routing, subnets |
| 2 Data Link | Ethernet, Wi-Fi | MAC, ARP, VLAN |
| 1 Physical | cables, radio | physical connectivity |

Practical debugging shortcut:

```text
DNS -> IP reachability -> port reachability -> TLS -> HTTP -> application
```

## IP Address

An IP address identifies a network interface.

Examples:

- IPv4: `10.0.1.5`
- IPv6: `2001:db8::1`

Private IPv4 ranges:

- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

These are not routed publicly on the internet.

## Ports

A port identifies a process or service on a host.

Common ports:

| Port | Protocol |
|------|----------|
| 22 | SSH |
| 53 | DNS |
| 80 | HTTP |
| 443 | HTTPS |
| 5432 | PostgreSQL |
| 6379 | Redis |

Strong interview sentence:

```text
IP gets traffic to a host; port gets traffic to the right process on that host.
```

## Client Port vs Server Port

When a browser calls `https://example.com`, the server usually listens on port `443`.

The client uses an ephemeral source port:

```text
client 192.168.1.10:53124 -> server 93.184.216.34:443
```

The connection is identified by a 5-tuple:

```text
source IP, source port, destination IP, destination port, protocol
```

## Latency, Bandwidth, Throughput

### Latency

Time for data to travel and be processed.

Measured in milliseconds.

### Bandwidth

Maximum capacity of the network path.

Measured in Mbps or Gbps.

### Throughput

Actual data transferred per second.

Interview trap:

```text
High bandwidth does not guarantee low latency.
```

## NAT

Network Address Translation rewrites IP addresses or ports.

Common use:

```text
private VM 10.0.1.4 -> NAT gateway -> public internet
```

Why NAT exists:

- private networks need internet access
- IPv4 addresses are limited
- many internal machines can share fewer public IPs

NAT can cause issues:

- port exhaustion
- confusing logs
- blocked inbound access
- idle connection timeouts

## Firewall and Security Groups

Firewalls decide whether traffic is allowed.

Rules usually consider:

- source IP
- destination IP
- source port
- destination port
- protocol
- direction

Azure example:

```text
NSG allows inbound TCP 443 from Internet to frontend subnet.
NSG denies inbound TCP 5432 from Internet to database subnet.
```

## Basic Commands

```bash
# Check DNS resolution
nslookup example.com
dig example.com

# Check reachability
ping 8.8.8.8

# Show route path
traceroute example.com

# Check port connectivity
nc -vz example.com 443

# Show local listening ports
lsof -iTCP -sTCP:LISTEN -n -P
```

## Cross Questions

### If ping fails, is the service down?

Not necessarily. ICMP may be blocked while TCP 443 still works.

### If a port is open, does the app work?

No. The network path may be open, but TLS, HTTP routing, authentication, or application health may still fail.

### Why can an app work from one VM but fail from another?

Different subnet, NSG, route table, DNS config, NAT path, identity, or firewall rule.

