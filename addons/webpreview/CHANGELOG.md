# Changelog

## 2.10.0

### Security
- **SSRF Hardening & DNS Rebinding Protection**:
  - Enhanced `_is_internal_or_invalid_url` to resolve candidate hostnames via `socket.getaddrinfo` (with IDNA punycode handling for international and Cyrillic domains) and reject destinations that resolve to private, loopback, link-local, reserved, multicast, or unspecified (`0.0.0.0`, `::`) IP addresses.
  - Added `SafeRedirectHandler` to intercept HTTP redirects across `urllib.request` calls, ensuring that redirects to private/internal networks are rejected with HTTP 403.
- **Private Chat Enforcement for Sensitive Commands**:
  - Enforced `_is_private_chat` check on `/addtransport` to prevent administrator credentials and email passwords from being leaked into group chats.
  - Enforced `_is_private_chat` check on `/initadmin` to prevent bot ownership claim races in group chats.
- **Error Message Sanitization**:
  - Sanitized error output in `/addtransport`, `/setprimary`, `/resilient`, `/rmtransport`, `/invidious_list`, `/ai`, and file downloading to avoid leaking internal exception details, credentials, or file paths into chats while preserving full error traces in the logger.

### Fixed
- **Resilient Transport Concurrency Race**:
  - Synchronized `original_send_msg` and `configured_addr` configuration with `resilient_lock`, preventing race conditions when concurrent messages are queued while background failover workers temporarily switch mail transports.
  - Wrapped secondary transport iteration in `bg_resend_worker` with a `try ... finally` block to guarantee the primary transport is always restored.
- **Bounded Message Deduplication & Rate Limiting**:
  - Replaced unordered set slicing in `_is_duplicate_msg` with `collections.OrderedDict` FIFO eviction capped at 1000 messages, eliminating arbitrary eviction of recent messages.
  - Added thread-safe locking and periodic cleanup to `_user_rate_limits` to prevent unbounded memory growth.

### Performance & Database
- **SQLite Concurrency & WAL PRAGMAs**:
  - Standardized all database connections using a helper with `PRAGMA journal_mode=WAL;`, `PRAGMA synchronous=NORMAL;`, `PRAGMA busy_timeout=5000;`, and `PRAGMA cache_size=-4000;`.
  - Added performance indexes on `preview_stats`, `api_log`, `url_cache`, `og_cache`, `tldr_cache`, and `url_hashes`.
- **Buffered Transport Statistics**:
  - Implemented in-memory buffering (`_transport_stats_buffer`) for transport sent and received counters with batch flushing to disk every 30 seconds, eliminating synchronous disk writes on every message.
- **Automated Record Retention Pruning**:
  - Added `cleanup_old_records(retention_days=30)` to prune stale preview stats and API logs during hourly cache cleanup cycles.

### Tests
- Added `tests/test_database.py` adhering to `AGENTS.md` testing conventions (config, admin fingerprinting, buffered transport stats, and 30-day retention).
- Added `tests/test_transport_commands.py` testing transport commands, private chat verification, `/resilient` toggle, and error sanitization.
- Expanded `tests/test_url_validation.py` with DNS resolution, rebinding, and `SafeRedirectHandler` tests.

## 2.9.9

### Fixed
- **Filter Non-Fetchable Image URLs (`blob:`, `data:`, localhost, private IPs):**
  - Added `_is_valid_image_url` helper to validate candidate preview images before making network requests.
  - Skips non-fetchable URL schemes (`blob:`, `data:`, `javascript:`, `file:`, `about:`) and internal/private network targets (`localhost`, `127.0.0.1`, private IP ranges, `.local`, `.lan`) without triggering 3 failed download attempts or warning logs.
  - Enhanced `_parse_jina_response` and HTML meta tag parsing to skip invalid or browser-local `blob:` images and discover the first valid HTTP/HTTPS image URL in webpage content.
  - Enhanced `_inline_soup_images` to decompose `blob:` and `javascript:` images instead of attempting network fetches.

## 2.9.8

### Added
- **Configurable Display Name & Status Text**:
  - `on_init` now checks `DISPLAY_NAME` and `STATUS_TEXT` environment variables with `/data/options.json` fallback instead of overwriting display name with static strings.

## 2.9.7
- **Prebuilt Monolith Binary in Docker:**
  - Replaced multi-stage Rust compilation (`cargo install monolith`) with direct download of the official prebuilt `monolith` binary (v2.10.1) for x86_64 and aarch64.
  - Drastically speeds up Docker image builds from several minutes down to seconds and avoids heavy Rust toolchain dependencies.
- Set default `chatmail_qr` server (`dcaccount:https://chat.gluek.info/new`) for zero-configuration startup.

## 2.9.6
- Initial Home Assistant Add-on release.
- Saves web pages as offline HTML (`monolith`), reader mode views, and WebXDC apps.
- Clean Instagram preview formatting and Gemini AI `/tldr` summaries.
