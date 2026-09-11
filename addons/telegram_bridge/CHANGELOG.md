# Changelog

## 2.20.0

- **Telegram Video Post & Album WebXDC Packaging**:
  - Full support for embedding MP4 videos into standalone offline WebXDC applications (`.xdc`).
  - Added responsive HTML5 `<video controls playsinline preload="metadata">` player with dark/light mode support, play/pause controls, and duration badges.
  - Implemented smart size limits & budgeting:
    - **Per-video cap**: Videos up to **20 MB** individually are downloaded and embedded directly into the WebXDC app.
    - **Total budget**: Direct embedding of videos up to a cumulative package budget of **50 MB**.
    - **Fast packaging**: Stored MP4 files uncompressed (`ZIP_STORED`) to prevent redundant CPU-heavy re-compression and ensure instant `.xdc` creation.
  - **Smart Overflow Cards**: Videos exceeding 20 MB individually, exceeding the 50 MB cumulative budget, or flagged as "Media is too big" by Telegram web embeds are rendered as elegant preview cards with duration badges, optimized WebP posters (`images/vid_poster_{idx}.webp`), and a prominent «Смотреть все видео в Telegram ↗» button pointing to the original Telegram post.
  - **Public Embed Video Extraction**: Extracted video streams (`.mp4`), thumbnail posters, durations, and status directly from Telegram public embed cards (`tgme_widget_message_video_player`).
  - **Poster De-duplication**: Filtered out video poster images from the photo gallery (`image_urls`) to eliminate duplicate image previews.
  - **Streaming Guard (`_download_video_with_limit`)**: Added HTTP `HEAD` early-rejection check and chunk-counting streaming downloader to prevent downloading oversize media beyond allowable byte budgets.
  - **Unit Tests**: Added comprehensive test coverage for video extraction, budgeting limits, overflow fallback, and streaming download guards.

## 2.19.3

- **Local Channel Avatar Integration for WebXDC**:
  - Prioritized existing local channel avatars from Delta Chat core (`profile_image`) when packaging WebXDC apps.
  - Automatically crops and resizes the channel's avatar to a 128x128 square PNG (`icon.png`, ~5–8 KB) matching the channel's authentic avatar in the chat list.
  - Eliminates external network requests and CDN blocking (e.g. 403 Forbidden) for avatar retrieval, ensuring the WebXDC card always renders the channel's official logo.
  - Fixed `tempfile.mkdtemp` typo in Userbot rich mode fallback.

## 2.19.2

- **Native 1280px Resolution Alignment**:
  - Aligned WebXDC maximum image bounding dimension to `1280px` to match Telegram's standard native photo delivery size (`y` size box 1280x1280).
  - Bypasses unnecessary image downsampling/interpolation overhead for native Telegram photos, reducing CPU usage during packaging while preserving crisp 1:1 original clarity.
  - Still automatically caps oversize images (e.g., 2560px `w` size) down to 1280px.

## 2.19.1

- **WebP Image Compression for WebXDC**:
  - Switched bundled WebXDC post images from JPEG to WebP (`format="WEBP"`, `quality=80`, `method=3`).
  - Optimized maximum image bounding box dimension from 1600px to 1200px (retina-sharp on mobile/desktop readers while reducing file size by ~60% compared to uncompressed JPEGs and cutting encoding time in half).
  - Significantly reduced `.xdc` package sizes, saving server bandwidth and speeding up downloads on mobile networks.

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
