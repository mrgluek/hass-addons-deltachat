# Changelog

## 2.24.3

- **Fix: NameError Crashing Rich Article Extraction**:
  - `_process_page_blocks()`'s `PageBlockVideo` handling referenced `TG_WEBXDC_VIDEO_MAX_BYTES`, a constant that was never defined (a leftover from the v2.24.0 inline article rendering rewrite), causing every rich post containing an inline video block to fail extraction with `NameError`.
  - Defined `TG_WEBXDC_VIDEO_MAX_BYTES = 20 * 1024 * 1024` (20 MB), matching the existing `MAX_SINGLE_VIDEO_BYTES` cap used in `_package_tg_post_webxdc`.

## 2.24.2

- **Direct Post Link Progress Feedback**:
  - Added `_react()` helper and wired it into `_async_handle_direct_tg_post()`: reacts with ⏳ on the triggering DC message as soon as a direct Telegram post link is detected, ☑️ once the post is delivered (cache hit, WebXDC, photo, or text), and ❌ if extraction fails or errors out — matching the feedback pattern already used by `deltachat_yt` and `deltachat_webpreview`.

## 2.24.1

- **Fix: Micro-sized Images in Rich Article WebXDC Posts**:
  - `RichMessage.photos` from Telegram sometimes only carries a low-res `PhotoStrippedSize` preview stub for photos that belong to an album, resulting in near-invisible thumbnails in the WebXDC gallery/lightbox.
  - Added `_resolve_full_res_photos_for_group()`: for posts with a `grouped_id`, looks up sibling messages in the same media group and swaps in their full-resolution attached photo (matched by Telegram's global `photo.id`) before `_process_page_blocks()` downloads images for `PageBlockPhoto`/`PageBlockCollage`.
  - Falls back silently to prior behavior when there's no `grouped_id` or no matching sibling is found.

## 2.24.0

- **Inline Article Rendering for Rich Telegram Posts**:
  - Completely redesigned WebXDC article layout: inline images are now embedded directly inside the post body as `<figure>` elements with optional captions, matching the original Telegram article reading experience.
  - Added `_process_page_blocks()` — a new recursive async function that fully handles all Telegram MTProto `PageBlock` types: `PageBlockParagraph`, `PageBlockPhoto`, `PageBlockCollage`, `PageBlockSlideshow`, `PageBlockVideo`, `PageBlockDetails`, `PageBlockBlockquote`, `PageBlockList`/`PageBlockOrderedList`, `PageBlockCover`, `PageBlockFooter`, `PageBlockEmbedPost`, and `PageBlockPreformatted` (code blocks).
  - `PageBlockDetails` (expandable/collapsible) sections are now rendered fully expanded inline — no folding inside WebXDC.
  - Full `GetRichMessageRequest` fetch for partitioned (`part=True`) rich messages, ensuring complete content is always retrieved rather than truncated previews.
- **Unified Gallery Lightbox**:
  - Replaced single-image lightbox with a full multi-image gallery lightbox supporting previous/next navigation, thumbnail strip, caption display, image counter, keyboard arrow keys, and touch-swipe gestures.
  - All images in a post (both top gallery and inline article images) are collected into a single shared `galleryImages[]` array, so clicking any image opens the unified lightbox and allows paging through all post images.
- **Bot Avatar Fallback**:
  - `_get_channel_avatar_path()` now correctly fetches the channel's own avatar from Telegram (not the requesting user's avatar), preventing copyright / avatar leakage issues.
  - Added `_get_bot_self_avatar_path()`: uses the bot's own Delta Chat selfavatar as fallback icon when no channel avatar is available.
  - Added `_generate_fallback_bridge_icon()`: generates a neutral SVG speech-bubble icon (bridge logo, no Telegram trademarks) as last-resort fallback.
- **Paragraph & Formatting Fixes**:
  - Added `_format_paragraph_html()`: properly converts double-newline paragraph boundaries to `<p>` tags and single newlines to `<br/>`, fixing broken paragraph spacing in article posts.
  - Fixed word-break, line-height, and margin CSS for `.post-content p` elements.

## 2.23.1

- **Anti-Loop Defense Hardening**:
  - Excluded messages starting with card and relay prefixes (`📰`, `📷`, `💬`, `🌐`, `🤖`, `/`) from direct Telegram link processing.
  - Hardened bot sender detection: checks `msg.from_id == 1` (standard DC self contact ID) as well as strict boolean verification of `msg.is_bot is True` and `contact.is_bot is True` to ensure the bridge never echoes or re-processes bot cards or its own messages.
  - Added unit test coverage for loop prevention (`test_handle_dc_message_skips_bot_card_prefixes`, `test_handle_dc_message_skips_bot_sender_and_self`).

## 2.23.0

- **Direct Telegram Post Link Previews & WebXDC Delivery**:
  - Added direct Telegram post link detection (`TG_POST_URL_RE`) in `handle_dc_message` for both group chats and 1:1 direct chats.
  - Implemented `_async_handle_direct_tg_post` with native MTProto userbot extraction (Layer 229+ `RichMessage`, media groups, polls, and photos) and fallback to public embed rich extraction (`_extract_public_tg_post_rich`).
  - Delivered posts strictly aligned with `/richmode`: plain text for text-only posts, photo with caption for single-image posts, and interactive standalone WebXDC apps (`.xdc`) for rich posts, multi-photo albums, and videos.
- **SQLite Post Caching**:
  - Created `telegram_post_cache` table and helper functions (`get_cached_tg_post`, `add_cached_tg_post`, `clear_expired_tg_post_cache`) with 24-hour default TTL and persistent on-disk file verification, enabling instant 0ms responses on repeated links and preventing Telegram MTProto FloodWait rate limits.
- **Unit Tests (`tests/test_post_preview.py`)**:
  - Added unit test suite covering post cache round-tripping, missing file invalidation, TTL cleanup, URL regex matching, cache hit delivery, and WebXDC/photo/text delivery dispatching.

## 2.22.1

- **Security & Media Protection**:
  - Enhanced SSRF guard (`_is_safe_telegram_url`) with DNS resolution to block domains resolving to loopback, private, link-local, multicast, or cloud metadata IP ranges, plus rejection of raw IP literals and `.lan` hostnames.
  - Added strict input validation for Telegram channel usernames and post IDs in `_extract_public_tg_post_rich`, preventing directory traversal and malformed embed URLs.
  - Enforced a 20 MB download size cap on remote images in `_download_image_to_file` and `_download_image_url`.
- **Dependency Hardening**:
  - Pinned `telethon`, `qrcode`, `Pillow`, and `httpx` to secure version ranges in `requirements.txt`.

## 2.22.0

- **Security & Authorization Hardening**:
  - Closed fail-open authorization vulnerabilities in `/id`, `/bridge`, `/unbridge`, and channel administrative commands. Permission checks now strictly fail-closed when API lookups fail or user permissions cannot be verified.
  - Restricted Telegram `/bridge`, `/unbridge`, and channel management to private chats with the configured bot owner, disallowing unauthorized configuration attempts in private chats when `admin_tg_id` is unset.
  - Masked internal technical IDs in channel addition confirmation messages and sanitized exception messages returned to users across channel bridging and catchup commands.
  - Hardened WebXDC HTML sanitizer (`_clean_html_for_webxdc`): disarmed `iframe`, `object`, `embed`, and `applet` tags, stripped inline event handlers (`on*`), and blocked dangerous URI schemes (`javascript:`, `data:`, `vbscript:`).
  - Added SSRF protection (`_is_safe_telegram_url`) for remote media downloads in `_download_image_to_file` and `_download_video_with_limit`, restricting remote targets to verified Telegram and CDN domains.
  - Added permission validation for `/userbotjoin` and `/userbotsync` commands, preventing non-admins from triggering background syncs.
- **Performance & Concurrency Optimization**:
  - Implemented persistent SQLite connection management with thread safety (`_SharedConnectionProxy`) to eliminate expensive per-query file re-opening and lock contention across high-throughput operations.
  - Replaced unthrottled thread creation in `AdminLogHandler` with a dedicated asynchronous queue worker and 60-second duplicate message TTL cache, preventing thread exhaustion during error storms.
  - Pre-compiled message filter patterns into a unified case-insensitive regular expression (`_filter_regex`) for O(1) keyword filtering.
  - Added in-memory channel ID caching (`_get_cached_dc_channel_chat_id`) with thread-safe invalidation to reduce database reads on incoming posts and edits.
  - Offloaded blocking Delta Chat JSON-RPC calls (`send_msg`, `send_edit_request`, `send_reaction`) inside `async` handlers to worker threads via `asyncio.to_thread`, keeping the asyncio event loop responsive.
- **UI/UX & Localization**:
  - Translated Russian WebXDC video overflow button text to English: «View all videos in Telegram ↗».
  - Cleaned up `/help` command output in Delta Chat: removed duplicate `/catchup` documentation, added `/locupdate` documentation, and clarified private chat command requirements.
  - Truncated long channel titles in `/channels` listings on both Delta Chat and Telegram sides to 40 characters to prevent message layout wrapping.
  - Standardized feedback emoji in `/resilient` disabled response to `ℹ️`.
  - Added completion notifications when `/userbotsync` finishes synchronizing channels.

## 2.21.4

- **Clean In-Place Post Edits for Broadcast Channels**:
  - Restored `send_edit_request` in-place message updates for Delta Chat broadcast channels and groups. When an existing post is edited in Telegram, the message text in Delta Chat is updated in-place on the existing message bubble with native Delta Chat `Edited` status.
  - Stripped `✏️ [Edited]` prefix when editing in-place to prevent nested blockquotes or clutter on edited posts.
  - Guaranteed zero duplicate messages: for existing messages in broadcast channels, if in-place edit request fails or cannot be applied (e.g. attachment modification), the bridge gracefully logs a warning, updates the content hash and watermark, and **never** falls through to `send_msg`.
  - Optimized media handling during edits: skips re-downloading media files or re-packaging WebXDC when editing existing posts in-place, conserving network bandwidth and CPU.
  - Added unit test suite covering in-place broadcast channel edits, clean text assertions, and failure resilience.

## 2.21.3

- **Channel Post De-duplication & Broadcast Channel Edit Suppression**:
  - Normalized Telegram channel and chat IDs with and without `-100` prefix across all database queries (`_normalize_tg_id_variants`) and memory caches. Resolves ID representation mismatches between Telethon (`3408...`), Telegram Bot API (`-1003408...`), and database records.
  - Suppressed in-place edit requests (`send_edit_request`) and duplicate message re-sends for broadcast channels in Delta Chat. In Delta Chat, broadcast channels are SMTP mailing lists where calling `send_edit_request` generates an email quoting the original post (`> ...`) and appending modified text. For broadcast channels, existing posts now update content hashes in SQLite and advance the channel watermark silently without re-sending duplicate emails.
  - If an edit event arrives for a channel post that was never relayed before, it is now cleanly relayed as a fresh post without `[Edited]` prefix.
  - Added direct `message_map` verification in `_process_userbot_event_internal`, `handle_tg_channel_post`, and `reconcile_channel` to ensure already relayed Telegram messages are never re-sent as new messages even if `last_msg_id` was lagging.
  - Ensured channel watermark (`last_msg_id`) unconditionally advances upon relaying channel posts, preventing startup reconciliation and catchup sweeps from re-forwarding delivered posts across bot restarts.
  - Added unit test suite covering Telegram ID normalization, cross-format database lookups, broadcast channel edit suppression, and reconciliation de-duplication.

## 2.21.2

- **Sanitize Poll Questions and Options Formatting**:
  - Added `_format_poll_text` helper to safely handle Telegram polls where questions or options are represented as `TextWithEntities` objects (introduced in MTProto Layer 229+ / Telethon 1.45+).
  - Extracted formatted text and mapped Telegram inline entities (`MessageEntity*`) into Delta Chat Markdown, preventing raw `TextWithEntities(text='...', entities=[])` string representations from leaking into messages.
  - Applied sanitized poll formatting across all poll handlers: userbot relay (`MessageMediaPoll`), channel posts (`handle_tg_channel_post`), incoming messages (`handle_tg_message`), and poll closure results (`handle_tg_poll`).
  - Added non-file media check in userbot media handler and `_get_media_size` to prevent unnecessary media download attempts for poll objects.
  - Added unit test suite covering `_format_poll_text` and userbot poll forwarding with `TextWithEntities`.

## 2.21.1

- **Fix SyntaxError on Python < 3.12**:
  - Fixed nested single quote within single-quoted f-string in `_rich_text_to_html` (`TextSpoiler` handler) to maintain backward compatibility with Python 3.9, 3.10, and 3.11 runtimes in Docker containers.

## 2.21.0

- **Native Telegram RichMessage & Inline Media Support**:
  - Upgraded `telethon` dependency to `>=1.45.0` (raising the MTProto protocol layer to Layer 229). This unlocks native support for Telegram's Rich Text Editor and inline media messages without falling back to MTProto's downgraded `MessageMediaUnsupported` placeholder.
  - Implemented `TypeRichText` decoders (`_rich_text_to_markdown` and `_rich_text_to_html`) supporting formatted text components: `TextBold`, `TextItalic`, `TextUnderline`, `TextStrike`, `TextFixed`, `TextSpoiler`, `TextUrl`, and `TextConcat`.
  - Added native block parser `_extract_telethon_rich_message` to extract and format `PageBlock` structures into rich post content:
    - `PageBlockParagraph` for text paragraphs.
    - `PageBlockHeader`, `PageBlockSubheader`, and `PageBlockHeading1`..`6` for hierarchical section headings.
    - `PageBlockBlockquote` and `PageBlockPullquote` for blockquotes.
    - `PageBlockPreformatted` for code blocks with language highlighting.
    - `PageBlockList` and `PageBlockOrderedList` for bulleted and numbered lists.
    - `PageBlockDivider` for thematic breaks.
    - `PageBlockTable` for tables with wrapped layout.
    - `PageBlockPhoto` and `PageBlockVideo` for inline media downloaded directly via Telethon MTProto client without relying on Telegram's web widget.
  - Extended `_download_image_to_file`, `_download_video_with_limit`, and `_download_image_url` to seamlessly handle local file paths downloaded by Telethon.
  - Seamlessly relayed `RichMessage` posts via WebXDC apps (with interleaved text and embedded images) in `webxdc` mode, or as photo messages with full formatted captions in `split` / standard mode.
  - Added full test coverage for `TypeRichText` AST formatting, `RichMessage` block extraction, and Userbot relay in both WebXDC and split modes.

## 2.20.2

- **Prevent Empty WebXDC Applications on Unsupported Media**:
  - Added strict displayable content check (`has_displayable_content`) to `_package_tg_post_webxdc`: immediately rejects creating WebXDC packages when posts contain 0 text, 0 images, and 0 videos.
  - Fixed false-positive `is_rich = True` detection in `_extract_public_tg_post_rich`: removed `text_not_supported_wrap` from the rich heuristic, since Telegram applies this class when the web widget itself cannot display the media (e.g. Stories, Gifts, live streams, or widget-unsupported objects like `qwerty_live/8889`).
  - Guaranteed that unsupported media posts with no displayable content smoothly trigger the standard Telegram fallback card (`[📰 Post with rich formatting / unsupported media — open in Telegram to view: https://t.me/...]`) instead of an empty WebXDC card.
  - Added dedicated unit tests for empty post rejection, embed markup validation, and unsupported media fallback messaging.

## 2.20.1

- **Persistent Media Group Deduplication & Album Mapping**:
  - Added persistent SQLite table `processed_media_groups` and index `idx_pmg_created` to store media group / album IDs across bot restarts and beyond the initial in-memory window.
  - Automatically extracts all album message IDs (`?single` links) in public post embeds (`album_post_ids`) and maps every individual post ID to the forwarded Delta Chat message ID in `message_map`.
  - Enforced monotonic updates for channel `last_msg_id` via `MAX(COALESCE(last_msg_id, 0), ?)` in SQLite to prevent out-of-order album messages from rewinding the channel watermark.
  - Expanded `message_map` composite primary key to `(dc_msg_id, dc_chat_id, tg_msg_id, tg_chat_id)` with automatic schema migration, allowing multiple Telegram album post IDs to be associated with a single WebXDC Delta Chat message.
  - Suppressed duplicate messages for edit events on posts belonging to already processed albums or mapped in broadcast channels when in-place edits are not possible.
  - Fixed missing `✏️ [Edited]` prefix on newly relayed edited posts.
- **WebXDC App Title Formatting**:
  - Formatted WebXDC application card title (`manifest.toml` `name` and HTML `<title>`) as `Channel Title #PostID` (e.g. `Фото и путешествия #1629` or `QWERTY #8888`) instead of truncating the post text teaser.

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
