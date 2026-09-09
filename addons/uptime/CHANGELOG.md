# Changelog

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
