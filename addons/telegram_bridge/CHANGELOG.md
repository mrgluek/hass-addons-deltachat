# Changelog

## 2.18.7

- **Security & Authorization Hardening**:
  - Implemented missing `/initadmin` command handler to claim bot ownership securely in private 1:1 chat with email and cryptographic fingerprint binding.
  - Enforced private 1:1 chat requirement on `/addtransport` to prevent credential exposure in shared groups.
  - Sanitized user-facing error messages across all mail relay and admin commands (`/transports`, `/addtransport`, `/rmtransport`, `/setprimary`, `/resilient`), logging full exception traces while returning clean status messages to users.
  - Deduplicated redundant `/rmtransport` command registration in `bot.py`.
- **Database Concurrency & Performance**:
  - Added `_connect()` helper enforcing SQLite WAL PRAGMAs (`journal_mode = WAL`, `synchronous = NORMAL`, `busy_timeout = 5000`) and 5.0s connection timeouts.
  - Wrapped all database operations in strict `try...finally: conn.close()` blocks, eliminating unclosed connection leaks and ResourceWarnings.
  - Implemented thread-safe in-memory buffering for transport message statistics (`_transport_stats_buffer`) with automatic 30s batch flushing to minimize database disk writes.
  - Added background cleanup & flush worker (`_bg_cleanup_worker`) in `on_start` to periodically flush stats and prune old message mappings via `cleanup_old_records`.
- **Testing & Verification**:
  - Added comprehensive unit tests in `tests/test_database.py` and `tests/test_transport_commands.py` covering admin binding, sender authorization, stats buffering, resilient mode toggling, and command error sanitization.

## 2.18.6

- **Configurable Display Name & Status Text**:
  - `on_init` now checks `DISPLAY_NAME` and `STATUS_TEXT` environment variables with `/data/options.json` fallback instead of overwriting display name and status text with static strings.

## 2.18.5

- **Fixed Telethon Infinite Reconnection Loop on NoneType Connection**:
  - Monkey-patched `MTProtoSender._reconnect` (`_safe_telethon_reconnect`) to immediately abort reconnection attempts when `_connection` is `None` (sender was already disconnected or abandoned), preventing infinite loop crashes (`AttributeError: 'NoneType' object has no attribute 'connect'`).
  - Changed `connection_retries` from `None` (unbounded infinite attempts) to `5` in `TelegramClient`, allowing dead senders to terminate cleanly so the userbot watchdog can re-initialize a fresh session.
  - Added `telethon.network.mtprotosender` to `PollingErrorFilter`.
## 2.18.4
- Initial Home Assistant Add-on release.
- Bidirectional Telegram <-> Delta Chat bridge with media and edit sync.
- Interactive Home Assistant configuration tab for bot tokens and mail credentials.
