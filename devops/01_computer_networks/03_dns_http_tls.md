# DNS, HTTP, and TLS

## What Happens When You Open a URL?

For `https://api.example.com/users/1`:

```text
1. Browser resolves api.example.com using DNS.
2. Browser opens TCP connection to the resolved IP on port 443.
3. Browser performs TLS handshake.
4. Browser sends HTTP request.
5. Server returns HTTP response.
```

Debug in that order.

## DNS

DNS maps names to records.

Common record types:

| Record | Purpose |
|--------|---------|
| A | hostname to IPv4 |
| AAAA | hostname to IPv6 |
| CNAME | alias to another hostname |
| MX | mail server |
| TXT | verification, SPF, DKIM |
| NS | authoritative nameserver |

## DNS Resolution Flow

```text
client cache
  |
  v
recursive resolver
  |
  v
root nameserver
  |
  v
TLD nameserver
  |
  v
authoritative nameserver
```

Caching happens at many layers.

## TTL

TTL controls how long DNS answers can be cached.

Low TTL:

- faster failover
- more DNS query load

High TTL:

- better caching
- slower changes

Interview trap:

```text
Changing DNS does not mean every client switches immediately.
```

## HTTP Basics

HTTP is request-response.

Request:

```text
GET /users/1 HTTP/1.1
Host: api.example.com
Authorization: Bearer ...
```

Response:

```text
HTTP/1.1 200 OK
Content-Type: application/json

{"id": 1}
```

## Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 301/302 | Redirect |
| 400 | Bad request |
| 401 | Unauthenticated |
| 403 | Unauthorized |
| 404 | Not found |
| 409 | Conflict |
| 429 | Rate limited |
| 500 | Server error |
| 502 | Bad gateway |
| 503 | Service unavailable |
| 504 | Gateway timeout |

## HTTP/1.1 vs HTTP/2 vs HTTP/3

### HTTP/1.1

- text-based
- persistent connections
- limited multiplexing

### HTTP/2

- binary framing
- multiplexing over one TCP connection
- header compression

Problem:

- TCP head-of-line blocking can still affect streams

### HTTP/3

- runs over QUIC
- uses UDP
- faster connection setup
- avoids TCP-level head-of-line blocking

## TLS

TLS provides:

- encryption
- server authentication
- integrity

TLS handshake roughly:

```text
client hello
server hello + certificate
key exchange
encrypted application data
```

## Certificates

A certificate proves a public key belongs to a domain.

A client validates:

- hostname matches certificate
- certificate is not expired
- certificate chains to a trusted CA
- certificate is not revoked, where applicable

## TLS Failure Examples

- expired certificate
- wrong hostname
- missing intermediate certificate
- unsupported TLS version
- private CA not trusted by client
- proxy terminating TLS incorrectly

## Curl Debug Examples

```bash
# See DNS, connection, TLS, and HTTP timing
curl -v https://api.example.com/health

# Show detailed timing
curl -w "\nDNS:%{time_namelookup} Connect:%{time_connect} TLS:%{time_appconnect} TTFB:%{time_starttransfer} Total:%{time_total}\n" \
  -o /dev/null -s https://api.example.com/health

# Resolve hostname to a specific IP for testing
curl --resolve api.example.com:443:10.0.1.10 https://api.example.com/health
```

## Cross Questions

### Why can DNS resolve but curl still fail?

DNS only gives an IP. TCP, TLS, HTTP routing, or backend health may still fail.

### What is the difference between 502 and 504?

502 usually means a proxy or gateway received an invalid response from upstream. 504 means the gateway timed out waiting for upstream.

### Why might TLS fail only in production?

Production may use different hostname, certificate chain, proxy, private CA, TLS policy, or SNI routing.

### Why is HTTP/2 useful for APIs?

It multiplexes multiple streams over one connection and reduces connection overhead, which can improve efficiency for many concurrent requests.

