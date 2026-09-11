# Changelog

## 2.19.0

- **Telegram Rich Post & Album WebXDC Packaging**:
  - Full support for converting Telegram long-form rich posts (posts with tables, spoilers, blockquotes, inline formatting, and multi-image photo albums) into standalone offline WebXDC applications (`.xdc`).
  - WebXDC container includes complete responsive reader interface with Telegram Instant View styling, dark/light theme support (`prefers-color-scheme`), clickable spoiler reveal, horizontally scrollable table wrapper, image lightbox viewer, and an attribution footer (`Post bridged at ... by Delta Chat Telegram Bridge` linking to `https://git.gluek.info/gluek/deltachat_telegram_bridge`).
  - Bundles high-resolution images locally into `images/` directory inside `.xdc` ZIP archive with PIL optimization (capped at 1600px, JPEG 85%).
  - Automatically generates tailored square 128x128 icon from channel author avatar or custom vector Telegram icon fallback.
- **Media Group (Album) Deduplication**:
  - Implemented `_is_media_group_processed` tracking `media_group_id` (Bot API) and `grouped_id` (Userbot) to prevent spamming duplicate events when Telegram delivers multi-photo albums as individual message updates.
- **Configurable Relay Modes (`/richmode`)**:
  - Added `/richmode [webxdc|split|both|off]` command for administrators to configure relay strategy:
    - `webxdc` (default): Package rich posts and multi-photo albums into interactive WebXDC app.
    - `split`: Send first photo with text, then send remaining photos sequentially as captioned follow-up messages (`[2/N]`, `[3/N]`).
    - `both`: Send interactive WebXDC package AND send individual follow-up images.
    - `off`: Legacy behavior with fallback text notifications.
  - Added persistent DB storage via `get_rich_mode()` and `set_rich_mode()` in `database.py`.
- **Public Embed Rich Post Parser (`_extract_public_tg_post_rich`)**:
  - Extracts author name, avatar, text HTML, formatted markdown, all image URLs, view count, published date, and detects rich post characteristics (tables, albums, long-form content).
- **Unit Testing**:
  - Added `tests/test_rich_posts.py` with comprehensive unit tests covering rich mode database config, media group deduplication, HTML cleaning, teaser generation, public post extraction, WebXDC archive packaging, and `/richmode` command authorization.

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
