# Changelog

## 1.8.6

### Fixed
- **`update.sh` Deployed the Wrong Branch**: Branch detection took the first remote branch in alphabetical order, so a leftover PR branch such as `origin/claude/...` sorted before `origin/master` and was deployed instead (and new `master` commits were reported as "Already up to date"). It now follows the checked-out branch, falling back to `main`/`master`.

## 1.8.4

### Security
- **Web Endpoint Rate Limiting**: Added sliding-window per-IP rate limiting to root homepage (`GET /`) and username card view (`GET /{username}/card`) with HTTP 429 `Retry-After: 60` response headers.
- **Dependency Pinning**: Pinned dependencies to secure ranges in `requirements.txt`.

## 1.8.3

### Security & Hardening
- **Private Chat Enforcement**: Enforced `_is_private_chat` on sensitive commands `/initadmin` and `/addtransport`, preventing credentials or admin claiming from leaking inside group chats.
- **Error Sanitization**: Sanitized user-facing error messages in transport administration commands (`/addtransport`, `/rmtransport`, `/setprimary`, `/transports`, `/resilient`), logging detailed diagnostics to server logs while replying with safe generic notices.
- **Resilient Sending Mode**: Added `_setup_resilient_mode(bot)` and `resilient_lock = threading.Lock()` with automatic failover transport resending and temporary primary address fallback restoration under `try...finally`.
- **Automatic Message Failover**: Added `on_msg_failed` handler with exponential backoff resend across configured mail relays.

### Performance & Concurrency
- **SQLite WAL & Concurrency**: Enabled WAL journal mode (`PRAGMA journal_mode = WAL`), `synchronous = NORMAL`, and `busy_timeout = 5000` via `get_connection()`.
- **Resource Cleanup**: Ensured all database connections strictly adhere to `try...finally: conn.close()`, resolving database connection leaks.
- **Buffered Transport Statistics**: Implemented in-memory write buffer (`_transport_stats_buffer` with `_transport_stats_lock`) and periodic background flushing (`flush_transport_stats`), slashing disk I/O under high traffic.
- **Automated Retention Worker**: Added background daemon worker in `on_start` running periodic stats flushing and expired pending claim cleanups (`cleanup_old_records`).
- **Comprehensive Test Suite**: Added `tests/test_database.py` and `tests/test_transport_commands.py` with 100% pass rate.

---

## 1.8.2

### Added
- **Options.json Fallback for Display Name & Status Text**:
  - `configure_bot_profile` now checks `/data/options.json` fallback when `DISPLAY_NAME` or `STATUS_TEXT` are not set in environment variables.

---

## 1.8.1
- Initial Home Assistant Add-on release.
- Registers custom usernames and short invite redirect links (`deltachat.id`).
- Web interface with Home Assistant Ingress integration on port 8084.
