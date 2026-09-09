# Changelog

## 1.6.56

### Security
- **Private Chat Enforcement**:
  - Restrict `/addtransport` to 1:1 private chats with the bot to prevent leaking mail passwords and chatmail tokens in group chats.
  - Restrict `/initadmin` to 1:1 private chats to prevent ownership claims in group chats.
- **Error Sanitization**:
  - Mask raw exception messages in user replies for `/transports`, `/addtransport`, `/setprimary`, `/resilient`, and `/rmtransport` to prevent leaking internal error details or paths.

### Fixed
- **Resilient Mode & Message Failover Concurrency**:
  - Wrap initial message dispatch and `configured_addr` lookup under `resilient_lock` to avoid transport misconfiguration during concurrent background resends.
  - Wrap sequential resending in `try...finally` to guarantee restoration of the primary transport address upon errors.
  - Fix message failover restoration running inside `with resilient_lock:`.
  - Protect `_message_failover_attempts` with `_message_failover_lock` and enforce FIFO bounding.

### Performance & Database
- **SQLite WAL & Busy Timeout**:
  - Enabled SQLite WAL mode (`PRAGMA journal_mode = WAL`), `synchronous = NORMAL`, `cache_size = -4000`, and `busy_timeout = 5000` for high concurrency without database lock contention.
  - Added indexes on `url_map(created_at)` and `info_cache(created_at)`.
- **Buffered Transport Statistics**:
  - Implemented thread-safe in-memory buffer `_transport_stats_buffer` with 30-second periodic flush, eliminating synchronous SQLite writes on every message.
- **True FIFO Bounded Message Deduplication & Rate Limiting**:
  - Refactored `_processed_msg_ids` to `collections.OrderedDict` (capped at 1000) for deterministic O(1) FIFO eviction.
  - Added thread-safe `_user_rate_limits_lock` with automated pruning of stale rate limit entries.
- **Automated Record Retention Cleanup**:
  - Added `cleanup_old_records(retention_days=30)` in `database.py` integrated into `_cache_cleaner_loop`.

### Tests
- Added `tests/test_database.py` and `tests/test_transport_commands.py` adhering to `AGENTS.md`.

## 1.6.55

### Added
- **Configurable Display Name & Status Text**:
  - `on_init` now checks `DISPLAY_NAME` and `STATUS_TEXT` environment variables with `/data/options.json` fallback instead of overwriting display name with static strings.

## 1.6.54
- Initial Home Assistant Add-on release.
- Audio and music downloads, track slicing, chunked delivery, and Navidrome integration.
- Automatic direct download for Instagram Reels.
