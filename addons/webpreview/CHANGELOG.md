# Changelog

## 2.15.1

### Fixed
- **Minutes-Long AI Replies During Gemini Outages**: Each Gemini model could wait 20s, so a chain of timing-out models took about 2 minutes before reaching the OpenRouter fallback. The whole Gemini chain now has a total time budget (`GEMINI_TIME_BUDGET`, default 30s) and stops after 2 timeouts in a row.
- **Gemma Reasoning Leaked into Answers**: Gemma 4 returns its reasoning as separate response parts flagged `thought`, and the bot showed that reasoning instead of the answer. Reasoning parts are now dropped.

## 2.15.0
- Upstream update to version 2.15.0.

## 2.14.1

### Fixed
- **Empty OpenRouter Answers**: `openrouter/free` can route to reasoning models that spend the whole token budget thinking and return no text. Requests now ask for low reasoning effort with 2048 tokens of headroom, and an empty answer is retried once (re-routed to another free model). Auth/credit errors (401/402/403) stop the fallback immediately.

## 2.14.0

### Added
- **OpenRouter Fallback (`OPENROUTER_API_KEY`, `OPENROUTER_MODELS`)**: When every Gemini model is rate-limited, overloaded or timing out, `/tldr`, `/ai` and preview TL;DRs now fall back to OpenRouter (default model `openrouter/free`, which routes to any available free model). Supports text and image prompts; audio stays Gemini-only. It also works as the only AI backend when `GEMINI_API_KEY` is empty. `/stats` shows OpenRouter request counts.

### Changed
- **Retired Model Removed**: Dropped `gemini-2.5-flash-lite` (no longer served, HTTP 404) from the default `GEMINI_MODELS` chain.
- **404 Cooldown**: A Gemini model answering HTTP 404 is placed on a 24-hour cooldown instead of being retried on every request.

## 2.13.2

### Fixed
- **`update.sh` Deployed the Wrong Branch**: Branch detection took the first remote branch in alphabetical order, so a leftover PR branch such as `origin/claude/...` sorted before `origin/master` and was deployed instead (and new `master` commits were reported as "Already up to date"). It now follows the checked-out branch, falling back to `main`/`master`.

## 2.13.1

### Changed
- **Private `/help` in Groups**: A plain `/help` sent in a group chat is now answered in a private 1:1 chat with the sender instead of the group, so several bots don't flood it with help texts (the reply ends with a note on how to show it in the group). Addressed `/help@web` is still answered in the group. Previously a plain `/help` was answered in the group, or silently ignored when other bots were present.

## 2.13.0

### Added & Improved
- **24-Hour Unified Cache Retention (`CACHE_MAX_AGE = 86400`)**:
  - Elevated OpenGraph preview cards (`og_cache`) and compiled reader mode HTML / WebXDC files (`url_cache`) from 1 hour to 24 hours, matching `tldr_cache` and other bots in the fleet (`TG Bridge`, `YT Bot`).
  - Greatly reduces outbound network traffic, protects against external rate limits and anti-bot captchas, and delivers instant 0ms responses for previously requested links.
- **Cache Hit / Miss Tracking & Efficiency Metrics**:
  - Added `cache_log` SQLite table with indexes on `created_at` and `cache_type`.
  - Added `log_cache_event(cache_type, hit)` and `get_cache_stats()` tracking 24-hour hits, misses, overall hit ratio percentage, and granular breakdowns across `og` preview cards, `article` reader files, and `tldr` AI summaries.
  - Enhanced `/stats` command output to display live cache efficiency metrics over the last 24 hours.
  - Added automatic 30-day retention cleanup for `cache_log` records in `cleanup_old_records`.
- **Unit Tests (`tests/test_database.py`, `tests/test_transport_commands.py`)**:
  - Added comprehensive test suites verifying cache logging, 24h stats calculation, hit ratio formatting, breakdown accuracy, retention cleanup, and `/stats` command presentation.

## 2.12.1

### Security & Robustness
- **Anti-Loop Defense Hardening**:
  - Excluded messages starting with bot card and message prefixes (`📰`, `🌐`, `🤖`, `📷`, `💬`) from URL auto-parsing.
  - Hardened `_is_bot_blocked` with strict boolean evaluation on both message snapshots and contact RPC objects (`contact.is_bot is True`) to prevent bot-to-bot echo loops and MagicMock false positives in test environments.
  - Added unit test coverage for anti-loop prefix filtering and contact bot evaluation in `tests/test_telegram_parser.py`.

## 2.12.0

### Added
- **Telegram Post Link Delegation to TG Bridge**:
  - Added `_is_tg_bridge_in_chat` detection checking for active `TG Bridge` / `Telegram Bridge` bot contacts in the current chat.
  - Added `_is_telegram_post_url` to accurately identify direct channel post URLs (`t.me/{channel}/{post_id}` and `t.me/s/{channel}/{post_id}`).
  - In `on_new_message`, automatically skips link auto-preview for Telegram posts if `TG Bridge` is present in the chat, yielding handling to TG Bridge's native MTProto / WebXDC pipeline to avoid duplicate previews and ensure complete delivery of rich posts, media albums, and videos.
- **Unit Tests (`tests/test_telegram_parser.py`)**:
  - Added `TestTgBridgeDelegation` suite covering Telegram post URL detection, `_is_tg_bridge_in_chat` contact lookup, and `on_new_message` skip verification.

## 2.11.0

### Added
- **Audio & Voice Message Support for `/ai` and `/tldr`**:
  - Added support for summarizing audio and Delta Chat voice messages via `/tldr` (by replying to a voice note or attaching audio).
  - Added voice message transcription, Q&A, and analysis via `/ai` (by replying to an audio note with or without a prompt, or sending `/ai` with an audio attachment).
  - Implemented audio MIME detection (`_detect_audio_mime`) supporting OGG/Opus, MP3, WAV, AAC, M4A/MP4, FLAC, and WebM via magic header bytes, declared message MIME types, and file extensions.
  - Implemented multimodal media extraction (`_extract_media_from_msg_or_quote`, `_extract_audio_from_msg_or_quote`) supporting direct attachments, quoted messages (`quote.message_id`), and parent messages (`parent_id`).
  - Generalized `_call_gemini_api` to send audio data using Google Gemini's native `inline_data` multimodal payload format with automatic text-only model exclusion (`gemma-*`).
  - Added `_summarize_audio_with_gemini` with 24-hour SQLite caching per audio hash and target language (`/lang`).
  - Added 20 MB file size limit enforcement (`MediaTooLargeError`) with polite user rejection messages for oversized media.
  - Increased media attachment download timeout from 15s to 30s to reliably fetch voice recordings across slower mail relays.
- **Unit Tests (`tests/test_audio.py`)**:
  - Added 13 comprehensive unit tests covering audio MIME detection, 20MB limit checks, Gemini audio summarization, 24h caching, `/tldr` voice summarization, and `/ai` voice message processing.

## 2.10.1

### Security
- **Image URL SSRF & DNS Rebinding Hardening**: Added DNS resolution checks to `_is_valid_image_url()` to verify that candidate preview image domains do not resolve to private, loopback, link-local, cloud metadata, or reserved IP ranges.
- **Archive Command URL Protection**: Enforced `_is_internal_or_invalid_url` check in `_handle_keep_command` to reject local, internal, or private endpoints.
- **Dependency Pinning**: Pinned dependencies to secure ranges in `requirements.txt`.

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
