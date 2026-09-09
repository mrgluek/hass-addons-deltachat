# Changelog

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
