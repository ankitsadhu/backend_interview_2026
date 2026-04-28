# TCP, UDP, and Sockets

## Transport Layer

The transport layer moves data between processes.

The two most common protocols are:

- TCP
- UDP

## TCP

TCP provides reliable, ordered byte streams.

It handles:

- connection establishment
- retransmission
- ordering
- flow control
- congestion control

Use cases:

- HTTP/1.1
- HTTP/2
- PostgreSQL
- Redis
- SSH

## TCP Three-Way Handshake

```text
Client -> Server: SYN
Server -> Client: SYN-ACK
Client -> Server: ACK
```

After this, both sides can send data.

If the handshake fails:

- server may not be listening
- firewall may block traffic
- route may be wrong
- backlog may be full
- load balancer health may be wrong

## TCP Connection Close

TCP uses FIN/ACK to close gracefully.

You may also see RST when a connection is reset abruptly.

Common reasons for reset:

- server process crashed
- proxy closed connection
- firewall reset idle connection
- application rejected the connection

## Reliability Is Not Free

TCP reliability has cost:

- retransmission delay
- head-of-line blocking
- connection state on both sides
- congestion-window warmup

This is why connection reuse matters.

## Connection Pooling

Opening a new TCP/TLS connection for every request is expensive.

Connection pools reuse existing connections.

Example:

```python
import requests

session = requests.Session()

for user_id in range(10):
    response = session.get(f"https://api.example.com/users/{user_id}")
    print(response.status_code)
```

The session can reuse TCP connections instead of creating a fresh one for each request.

## UDP

UDP sends datagrams without connection setup.

It does not guarantee:

- delivery
- ordering
- duplicate protection

Use cases:

- DNS
- video/audio streaming
- gaming
- QUIC/HTTP/3
- telemetry

UDP is useful when low latency matters more than built-in reliability, or when the application protocol implements reliability itself.

## TCP vs UDP

| Feature | TCP | UDP |
|--------|-----|-----|
| Connection | Yes | No |
| Reliability | Built in | Application-defined |
| Ordering | Built in | No |
| Overhead | Higher | Lower |
| Common Use | APIs, databases | DNS, streaming, QUIC |

## Socket Mental Model

A socket is an endpoint for network communication.

Server:

```python
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 8080))
server.listen()

conn, addr = server.accept()
data = conn.recv(1024)
conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
conn.close()
```

Client:

```python
import socket

client = socket.create_connection(("example.com", 80), timeout=3)
client.sendall(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
print(client.recv(1024))
client.close()
```

## Timeouts

Always configure timeouts.

Bad pattern:

```python
requests.get("https://api.example.com/data")
```

Better:

```python
requests.get("https://api.example.com/data", timeout=(2, 5))
```

The tuple means:

- connect timeout
- read timeout

## Cross Questions

### Why can too many outbound calls fail even when CPU is low?

Possible causes include connection pool exhaustion, ephemeral port exhaustion, NAT port exhaustion, DNS latency, or downstream throttling.

### Why does connection reuse improve performance?

It avoids repeated TCP handshakes, TLS handshakes, and congestion-window warmup.

### Why is UDP used for DNS?

DNS queries are usually small and benefit from low overhead. DNS can use TCP for large responses, zone transfers, or fallback.

### Is TCP enough for exactly-once delivery?

No. TCP reliably delivers bytes on a connection, but application-level retries, crashes, and duplicate requests still require idempotency.

