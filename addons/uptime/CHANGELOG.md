# Changelog

## 2.15.0

Ready for 1000+ monitors. Measured on de2 (148 monitors) the bot used 1.5 % of one core, and a local benchmark put the bot's own work at about 0.15 ms of CPU per check (plus 1-3 ms for a TLS handshake), so CPU is not what limits it; the changes below address what does.

### Changed
- **Hung targets no longer block the queue**: a `HEAD` request that times out (or cannot connect: refused, DNS, certificate) is no longer repeated as `GET`, which held a check slot for a second full timeout. Up to 200 checks run at once instead of 50 (`CHECK_CONCURRENCY`; HTTP connection pool 250, since aiohttp counts the wait for a pooled connection against the timeout), and `docker-compose.yml` raises the open-file limit from 1024 to 8192. 300 targets that accept connections but never answer: 131 s before, 21 s now - before, they delayed every other check past its one-minute interval.
- **Batched peer cross-checks**: failing monitors found within 5 seconds are sent to each peer in one `[UPTIME_PEER_CHECK_BATCH_REQ]` message (up to 100 targets, identical targets once), answered with one `[UPTIME_PEER_CHECK_BATCH_RESP]`; the peer runs them 20 at a time. Before, each failing target sent a message to every peer and got one back - 600 mails per peer a minute for 300 failing targets, far over the relays' 60 messages a minute. Bots announce support with `caps: ["batch_check"]` in telemetry and check messages; until a peer has announced it, it gets the old one-target requests, so mixed versions keep working. Answers are only accepted from the chat the batch went to; URLs are taken from the request, the peer's answer only fills positions; refused targets keep their position as "Target refused".
- **Telemetry with changes first**: with more than 200 targets per peer, each message starts with the targets whose status changed since the last one and fills the rest by rotation over the whole list, so a status change reaches peers within 2 minutes even with 1000+ monitors (before: up to 10 minutes). 200 per message stays, as receivers take no more.
- **Quiet logs**: `Check result` lines are INFO only for DOWN results and status changes, routine UP results and `Triggering N target checks` are DEBUG, and a summary is logged once a minute: `Checks in the last 60s: 148 (146 up, 2 down, 0 skipped), avg latency 87 ms, slowest … ; running now: 3`. At 1000 monitors the per-check lines alone filled Docker's 30 MB log rotation in 2-3 hours.
- **One DB transaction per check**: the status of every monitor of a target and the local peer measurement are written together (`database.record_check_results`) instead of in 2+ transactions. Results are still written right away: deferring them would let the scheduler re-read an old `last_checked` and run the same check twice.

## 2.14.0

### Added
- **IPv6 targets**: `/ping` and `/add` accept IPv6 addresses - `2a00::1` or `[2a00::1]` (ICMP ping), `[2a00::1]:443` (TCP; with a port the address goes in brackets, as in URLs, because `2a00::1:22` is itself a valid address). Addresses are stored normalized (compressed, lowercase). Private, link-local and loopback IPv6 addresses stay blocked.
- **`/ping -4` / `/ping -6`**: check a name only over IPv4 / IPv6, like `ping -4/-6`. The flag is sent to the other regions too (older peers ignore it and check either family); a name without an address of that family gets "has no IPv6 address". The `/add` hint is left out, since monitors have no family setting; `/add -6` explains to add the address itself.

### Fixed
- **IPv6 address read as host:port**: `/ping 2a00:da00:f443:e900::1` was parsed as a TCP check of `2a00:da00:f443:e900:` on port 1 and failed with "Name or service not known".
- **No IPv6 on a node is not an outage**: before connecting, the bot asks the kernel for a route to each IPv6 address (a UDP `connect()`, which sends nothing). Unroutable IPv6 addresses are dropped, so a host with A and AAAA records is checked over IPv4 instead of failing with `[Errno 101] Connect call failed ('2a00:…', 22)`. An IPv6-only target on such a node is skipped - no retries, no peer cross-check, no alert, status unchanged - and `/ping` shows ⚪ "Not checked" with the verdict of the other regions. Peers answer such requests with status `skip` (shown as ⚪). `/add` of an IPv6 target warns when this node has no IPv6.
- **TCP error of the preferred address**: when every address of a host fails, the error of the first one (IPv4 first) is reported instead of the last one.
- **Peer measurements of IPv6 targets**: check responses were classified as TCP whenever the target contained ":", so IPv6 ping targets were dropped as unsafe; the type now comes from the same parser as `/add`.

## 2.13.0

### Changed
- **Peers Identified by Key Fingerprint, Not Address**: Since Delta Chat 2.61 a bot can have several relays and sends from whichever one is reachable. Peers were stored and matched by email address, so as soon as a peer switched relays (e.g. `ruptimebo@chat.gluek.info` → `ruptimebot@chatmail.uk`) its telemetry, cross-check requests and answers were dropped as coming from an "untrusted sender", although they arrived end-to-end encrypted, from the same key, in the same 1:1 chat. Each peer now stores its OpenPGP fingerprint:
  - taken from the invite when adding a peer with `/addpeer <link>`, from an encrypted `HELLO` when a bot pairs with an `/invitepeer` token, or from the first encrypted message for existing peers;
  - incoming peer messages are matched by fingerprint first; the stored address and 1:1 chat follow the peer, and probe targets it mirrored to this node move with it;
  - once a key is bound, a message from the peer's address signed by another key (or unencrypted) is rejected, which is stricter than the address check before.
- **Cross-Check Answers Matched by Chat**: Answers are expected from the 1:1 chats the request was sent to instead of from the addresses, so a peer answering via another relay is still counted.
- **`/peers` Shows Keys, `/rmpeer` Accepts Them**: `/peers` shows the first 16 hex digits of each peer's key (or "not bound yet"). `/rmpeer` accepts the current address, the full fingerprint or a unique prefix of at least 8 hex digits.
- **Re-adding a Known Bot**: `/addpeer <link>` for a bot whose key is already a peer updates that peer instead of creating a second entry.

### Upgrade Notes
- No action needed. Existing peers are bound to their key on their first encrypted message: in their 1:1 chat (also when they already send from a new address) or from their stored address. Peers that switched relays before this release recover on the next telemetry round (every 2 minutes).
- All nodes should run 2.13.0: an older node still drops this node's messages once this node sends from another relay.

## 2.12.1

### Added
- **MIT License**: the project is now licensed under MIT (`LICENSE`).

### Fixed
- **Crash Risk in DNS Pinning**: 2.12.0 created and closed a new aiodns/pycares resolver for every lookup. Queries cancelled by a timeout were torn down mid-flight, and pycares destroys channels in a background thread that can crash the interpreter at shutdown (the test run on `main` ended with SIGBUS, exit code 135, after the PR run had passed). Lookups now share one long-lived resolver per event loop, which is how aiodns is meant to be used.
- **Tests Made Hermetic**: Some peer and redirect tests performed real DNS queries, which only happened in CI (where the network is reachable). All tests now stub DNS, and CI runs with `-X faulthandler` so a native crash prints a traceback.

## 2.12.0

### Security
- **No More Automatic Peering**: Any Delta Chat user could send a `[UPTIME_PEER_HELLO]` message to the bot, be added as a peer automatically and from then on receive every monitor of every chat every 2 minutes. An unknown bot is now only accepted as a peer if it presents a single-use token from `/invitepeer` (valid 24h); the admin is notified when that happens. `HELLO_ACK` is only accepted from bots the admin added. Without a token, both admins have to run `/addpeer` for each other.
- **Peer Messages Only From Peers**: `CHECK_REQ`, `CHECK_RESP` and `METRICS` were processed from any sender, so anyone could make the bot probe arbitrary hosts, plant up to 200 probe targets per message and inject fake per-node results into public status pages. They are now accepted only from configured peers, in a 1:1 chat and end-to-end encrypted (padlock). The sender is taken from the Delta Chat contact only; `sender_email` and `node_name` in the payload are no longer trusted.
- **Cross-Check Responses Bound to Requests**: A response is only accepted for a pending `req_id`, from a peer the request was sent to, once per peer. Request IDs are now 96-bit.
- **Controlled Disclosure (`/peershare admin|all|none`)**: Telemetry and cross-check requests now include only monitors from chats the administrator is a member of (`admin`, default). `all` restores the previous behaviour, `none` shares no local monitors. Monitor names are no longer sent. `/ping` from non-admin users reaches peers only with `all`.
- **No Relaying of Mirrored Targets**: Targets one peer asked this node to probe are reported back only to that peer instead of being forwarded to every other peer (and from there further across the mesh). Each peer can make this node probe at most 200 targets; `/rmpeer` removes the targets mirrored from that peer.
- **SSRF via Redirects**: HTTP checks and `/ping` title fetches followed redirects without re-validating them, so a public URL could redirect the probe to `127.0.0.1` or cloud metadata addresses. Redirects are now followed manually (at most 10) and every hop is checked by the SSRF filter.

- **DNS Rebinding Protection**: Targets were validated with one DNS lookup and then connected to after a second, independent lookup, so a hostname could answer with a public address during validation and with `127.0.0.1` or a cloud metadata address at connect time. All probe connections (HTTP checks, redirects, TCP, ping, SSL expiry, `/ping` title fetch) now go through one resolver that checks every address and pins the validated answer for the record's TTL (clamped to 30–300 s, 60 s when the TTL is unknown). After expiry the new answer is validated again. HTTP checks use a custom aiohttp resolver; TCP, ping and SSL checks connect to the validated IP; the title fetch connects to the pinned IP with the original hostname for SNI and no longer uses environment proxies. DNS is now resolved asynchronously (aiodns, falling back to the system resolver for `/etc/hosts`) instead of blocking the event loop on every check.

### Fixed
- **TCP Targets With IPv6 Literals**: `[::1]:22` style targets were not recognised as IP literals by the SSRF filter.
- **SecureJoin Peers With Unknown Address**: A peer stored under the `peer_<chat>@securejoin` placeholder never matched incoming messages. The placeholder is now replaced with the real address on the first message in that chat.

### Upgrade Notes
- Existing peers keep working. Pairing with a new bot requires the `/addpeer ... token=...` command printed by `/invitepeer` (or `/addpeer` on both sides).
- Unencrypted peer telemetry is dropped. Bots exchange keys during the HELLO handshake, so this only affects peers on classic email providers without Autocrypt.
- If you relied on peers seeing monitors of all chats, run `/peershare all`.

## 2.11.1

- **User-Agent No Longer Contains "Bot"**: HTTP checks now send `Delta Chat Uptime Monitor/<version> (+https://git.gluek.info/gluek/deltachat_uptime)` instead of `DeltaChat-Uptime-Bot/...`. Hiddify Manager (and other services that block crawlers) answered `400 Bad Request` to any User-Agent containing "bot", so working subscription links showed as down while they opened fine in a browser.

## 2.11.0

- **`/transports` Shows the Relay Actually Used for Sending**: Since core 2.61 the core sends through the relay that last worked and switches only when it cannot connect, so the main address (`configured_addr`) says nothing about where mail goes out. `/transports` now lists relays in the order the core tries them, with the current sending relay first, shows the core's send queue (waiting messages and retries) and outgoing status, and per relay the incoming status, when the last message arrived, mailbox storage usage (⚠️ from 80%) and when it was added. The sending order and queue are read from the core's account database (read-only); the report is built by the shared `transports_view.py`.
- **Removed Misleading Per-Relay Sent/Received Counters**: They credited every message to `configured_addr` (or, in some places, the wrong address), so the numbers and "last sent" dates were wrong once the core sent through another relay. Counting them also cost extra RPC calls per message. The `transport_stats` table is left in place but no longer updated.

## 2.10.0

### Removed
- **Bot-Side Relay Failover**: Removed the `MSG_FAILED` failover handler and the resilient-send `send_msg` patch. Both switched `configured_addr` and called `resend_messages`, but since Delta Chat core 2.61 the SMTP relay is no longer chosen by `configured_addr`: the core tries the newest relay first and falls back to the next one if a relay is unreachable. The old logic could no longer switch relays and only caused delayed duplicate resends.

### Changed
- **`/setprimary` and `/resilient` Deprecated**: Both commands are disabled and only reply with an explanation of how the core picks relays now. They are removed from `/help` and the README.
- **`/transports` Sending Order**: Relays are listed newest first, in the order the core tries them for sending, instead of marking `configured_addr` as "Used for sending".
- **Core Requirement**: `requirements.txt` now requires `deltachat-rpc-server>=2.62.0`.

## 2.9.7

### Fixed
- **`update.sh` Deployed the Wrong Branch**: Branch detection took the first remote branch in alphabetical order, so a leftover PR branch such as `origin/claude/...` sorted before `origin/master` and was deployed instead (and new `master` commits were reported as "Already up to date"). It now follows the checked-out branch, falling back to `main`/`master`.

## 2.9.6

### Changed
- **Private `/help` in Groups**: A plain `/help` sent in a group chat is now answered in a private 1:1 chat with the sender instead of the group, so several bots don't flood it with help texts (the reply ends with a note on how to show it in the group). Addressed `/help@uptime` is still answered in the group. Previously a plain `/help` was answered in the group, or silently ignored when other bots were present.

## 2.9.5

### Fixed
- **False SSRF block for hosts with Yggdrasil IPv6 records**: Domains publishing an AAAA record in the Yggdrasil mesh range (`200::/7`, e.g. `cm1.wwire.su`) were rejected with "Target blocked: internal or private network address", because Python's `ipaddress` flags that range as reserved. Yggdrasil addresses are now treated as routable, while other reserved ranges stay blocked. IP checks are consolidated in a new `_is_blocked_ip()` helper.

## 2.9.4

### Security
- **SSRF & DNS Rebinding Hardening**: Added DNS resolution check in `is_safe_target_url()` ensuring domains resolving to loopback, private, link-local, cloud metadata, or reserved ranges are rejected. Blocked `.local`, `.internal`, `.lan`, `.localdomain` suffixes. Added SSRF validation to `/add`, `fetch_html_title`, and `run_single_check`.
- **Request Body Limits & Rate Limiting**: Added `client_max_size=256KB` on web server and sliding-window rate limiting on public web endpoints with HTTP 429 `Retry-After: 60`.
- **Dependency Pinning**: Pinned dependencies to secure ranges in `requirements.txt`.

## 2.9.3

### Added
- **Auto-Memorization of GET Method on HTTP 405 (Method Not Allowed)**:
  - When a target server responds with `405 Method Not Allowed` to a lightweight `HEAD` probe (common on GoToSocial, Mastodon, and specialized web frameworks that disallow HEAD on root or API endpoints), the bot now automatically remembers `GET` as the preferred method for that monitor and URL.
  - Persisted to database via new `http_method` column in `resources` and `probe_targets` tables, and synchronized with active in-memory scheduler caches.
  - Subsequent minute checks bypass the `HEAD` attempt and directly issue `GET` requests, eliminating redundant `405` error log entries on target servers and halving network overhead for those endpoints.

## 2.9.2

### Fixed
- **Persistent SQLite Writer Connection & Elimination of Continuous Disk Writes**:
  - Resolved root cause of continuous disk I/O (~500 kB/s on Linux ext4 / `jbd2` journal): SQLite in WAL mode defaults to connection-scoped `synchronous = FULL`, causing `fdatasync()` on every single commit. When combined with ephemeral per-operation database connections, every monitor check caused repeated WAL header synchronizations and ext4 journal commits.
  - Implemented a dedicated persistent writer connection (`_writer_conn`) and `_writer_transaction()` context manager under `_write_lock`, eliminating per-check connection open/close churn and reusing the connection across all database writes.
  - Enforced `PRAGMA synchronous = NORMAL;` across all reader and writer connections. In WAL mode, `NORMAL` guarantees full ACID durability and WAL crash-safety while eliminating `fdatasync()` during transaction commits, reducing fsync operations by >98% (from 400+ calls per 100 commits to 0 during commits).
  - Added `close_db()` lifecycle helper for clean connection teardown and test isolation.

## 2.9.1

### Fixed
- **Container Environment Compatibility (`socket.getprotobyname("icmp")` / `OSError: protocol not found`)**:
  - Added a defensive IANA protocol number fallback (`IPPROTO_ICMP = 1`, `IPPROTO_ICMPV6 = 58`) for `socket.getprotobyname` during `aioping` initialization, preventing startup crashes in minimal container base images lacking `/etc/protocols` (such as Debian minimal without `netbase` or minimal Alpine in Home Assistant Add-ons).
  - Widened `import aioping` and `import aiodns` exception handling to catch all `Exception`/`OSError` types, guaranteeing safe fallback to `/bin/ping` subprocesses if socket initialization fails for any reason.
  - Added `netbase` to `Dockerfile` dependencies to supply `/etc/protocols` out-of-the-box.

## 2.9.0

### Added
- **Native Async ICMP Ping (`aioping`)**:
  - Integrated `aioping` for native in-process ICMP echo requests, avoiding OS subprocess spawning overhead on ping monitors.
  - Implemented graceful fallback: automatically falls back to system `/bin/ping` subprocess if `aioping` is unavailable or if raw socket permissions (`CAP_NET_RAW`) are restricted.
- **Asynchronous DNS Resolver & 5-Minute DNS TTL Caching (`aiodns`)**:
  - Added `aiodns` integration with `aiohttp.AsyncResolver`, eliminating blocking system `getaddrinfo` calls from thread pools during routine HTTP/HTTPS checks.
  - Configured 5-minute DNS caching (`ttl_dns_cache=300, use_dns_cache=True`) across the shared monitoring session.
- **Deterministic Time Slot Staggering**:
  - Implemented uniform deterministic phase staggering (`(r_id * 11) % interval`) to evenly distribute monitor checks across 5-second execution windows, eliminating thundering-herd CPU/network spikes on bot startup and synchronized intervals without expensive hashing.
- **Concurrent Lock-Free SQLite WAL Reads (`_write_lock`)**:
  - Separated SQLite synchronization into a dedicated `_write_lock` for database mutations (`INSERT`, `UPDATE`, `DELETE`, batch updates, and pruning).
  - Unlocked all read-only queries (`SELECT`) with `_connect()` and `PRAGMA busy_timeout = 5000`, enabling parallel non-blocking reads across web status dashboards, commands (`/status`, `/list`), and background workers.
  - Maintained `_lock = _write_lock` alias for full backwards compatibility.

### Changed
- **Two-Tier HTTP Monitoring Strategy (`HEAD` -> `GET`)**:
  - For standard HTTP/HTTPS monitors without keyword assertions, the bot now issues a lightweight `HEAD` request first (transferring 0 body bytes and 0 CPU decode overhead).
  - Automatically falls back to `GET` reading at most 16 KB (`16384` bytes) if the server returns non-2xx/3xx (e.g. `405 Method Not Allowed`) or on connection errors.
  - When custom keyword assertions are configured, direct `GET` is used with body reading capped at 128 KB (`131072` bytes, reduced from 256 KB).
  - `fetch_html_title` buffer reduced from 64 KB to 16 KB (`16384` bytes).

## 2.8.0

### Added
- **Performance Indexes for SQLite**:
  - Added indexes on `downtime_events` (`went_up_at`, `(resource_id, went_down_at, went_up_at)`), `incidents` (`(dc_chat_id, status)`, `resolved_at`), `resources` (`(dc_chat_id, status)`, `url`, `status`), `peers` (`last_seen`), and `peer_measurements` (`last_checked`) to eliminate full table scans during checks, audits, and cleanup.
- **Dedicated Thread Pools for DB vs RPC**:
  - Introduced separate `db_executor` (for fast non-blocking SQLite operations) and `rpc_executor` (for Delta Chat JSON-RPC and SMTP network operations) via `run_db` and `run_rpc`, preventing slow email delivery from exhausting worker threads.
- **In-Memory Uptime TTL Cache & Batch Calculation**:
  - Implemented `_uptime_cache` with a 60-second TTL and `get_resources_uptime_30d` for single-query batch calculation across all monitors in a chat, eliminating N+1 query patterns on web status dashboards, `/list`, and `/status`.
  - Added cache invalidation on status transitions, resource deletions, and maintenance cleanup.
- **Batch Check Status Updates**:
  - Implemented `batch_update_resource_status` to commit grouped check results in a single transaction under the database lock.
- **Non-Blocking Check Concurrency Semaphore**:
  - Refactored `check_group_task` with `check_network_probe` to hold the concurrency semaphore only during physical network probes. Retry backoff sleeps (30s) and remote peer cross-checks now run without holding semaphore slots, preventing failing endpoints from starving healthy monitors.
- **Incident Sync Lock Pruning**:
  - Added `prune_incident_sync_locks` to automatically evict idle, unlocked chat incident synchronization locks, preventing unbounded in-memory dictionary growth over long operational periods.
- **Standardized Admin Authentication**:
  - Added standardized `get_admin_email`, `set_admin_email`, `get_admin_fingerprint`, `set_admin_fingerprint`, and `is_authorized_sender` in `database.py`.
- **New Unit Test Suite**:
  - Added `tests/test_database.py` covering schema indexes, batch uptime calculation, caching, status updates, and admin handling, bringing test coverage to 88 automated tests.

## 2.7.7

### Security
- **Credential Protection in `/addtransport`:**
  - Restricted `/addtransport` exclusively to private 1:1 chats with the bot, protecting passwords and chatmail tokens from accidental exposure in group chats.
- **Sanitized Command Error Messages:**
  - Sanitized exception disclosures across administrative commands (`/rmaccount`, `/addtransport`, `/rmtransport`, `/setprimary`, `/resilient`, `/invite`, `/addpeer`) to prevent internal system or credential leakages in chat replies.
- **Resilient Sending Concurrency Protection:**
  - Synchronized initial message queueing inside `resilient_lock` to eliminate data races with background transport failover workers.

### Performance & Optimization
- **Single Atomic Write for Status & Latency:**
  - Merged routine check latency and status updates into a single atomic SQLite transaction, cutting database disk write operations in half.
- **Shared HTTP Connection Pooling:**
  - Transitioned routine monitoring HTTP checks to a persistent shared `aiohttp.ClientSession` with connection pooling, DNS caching, and TCP keep-alive, significantly reducing socket and SSL handshake CPU overhead.
- **Buffered Transport Stats:**
  - Introduced in-memory buffering for transport send/receive statistics with periodic flushing (and automatic flush-on-read), eliminating per-message synchronous disk writes.
- **Scheduler Cache Optimization:**
  - Preserved resource schedule cache across active checks instead of invalidating it every 5-second tick, drastically reducing full-table database scans.
- **Automated Database Maintenance:**
  - Added scheduled pruning (`database.cleanup_old_records`) of resolved downtime events, closed incidents older than 90 days, and stale peer measurements older than 7 days.
- **Rate Limiting on Diagnostic Checks:**
  - Added a 15-second per-chat anti-spam cooldown on `/ping`, `/check`, and `/test` commands with administrator bypass to prevent resource exhaustion.

## 2.7.6

### Fixed
- **Home Assistant Display Name & Status Text Configuration:**
  - Added direct fallback reading of `/data/options.json` in `on_init` for `display_name` and `status_text`, ensuring custom display names configured in Home Assistant Add-on settings are always applied even if environment variables are not exported.

## 2.7.3
### Added
- **ASCII QR Code in Startup Logs:**
  - Render ASCII QR code directly into stdout on bot startup for easy terminal and container log onboarding.
  - Added line-buffering and explicit flushing for container environments (Docker, Home Assistant Add-on).

### Fixed
- **Relative Web Asset URLs for Ingress:**
  - Changed absolute `/icon.png` and `/favicon.ico` paths to relative (`icon.png`, `favicon.ico`) in both dashboard and index HTML templates so logos and favicons load correctly under Home Assistant Ingress reverse proxy paths.
- Set default `chatmail_qr` server (`dcaccount:https://chat.gluek.info/new`) for zero-configuration startup.

## 2.7.2
- Initial Home Assistant Add-on release.
- Home Assistant Ingress web dashboard integration on port 8081.
- Automatic account provisioning and ASCII QR code invite logging.
- Parallel multi-region cross-checks in `/ping`.
