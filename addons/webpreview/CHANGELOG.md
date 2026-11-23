# Changelog

## 2.32.4

### Fixed
- The bot's own key fingerprint is now read from the core once per process instead of on every admin check. Each read made the core create a new invite token that is never removed, and the check runs for every link, preview, command and reaction of a non-cached user. Measured with a fake core and 1,000 requests from 1,000 different users: 1,000 invite-token requests before, 1 after. A failed lookup is not cached. `dc_fingerprint.py` is the shared copy from the other bots (adds `forget_self_fingerprint()`).

## 2.32.3

### Fixed
- Link preview cards posted in group chats were not tracked, so 👎 reactions never reached the administrator and 🗑️ could not delete them. They are now tracked like other answers.

## 2.32.2

### Changed
- When several people save the same message (💾 KaraKeep, 🏛️ Web Archive), the bot's single reaction now combines the results, e.g. “💾 KaraKeep · 🏛️ Archive”, instead of the last one overwriting the others. The KaraKeep reaction uses 💾.

## 2.32.1

### Changed
- Deleting a bot answer with 🗑️ now replaces the ☑️ on the original request with “🗑️ Deleted by user request”.
- The downvote report to the admin now fires at 3 👎 (was: more than 3), as `DOWNVOTE_THRESHOLD` says.

## 2.32.0

### Added
- **Downvotes Report Bad Previews**: when more than 3 people react 👎 (any skin tone) to a bot answer for a link, the bot privately sends the administrator the link and a ready `/preview_exclude <domain>` command. It is sent once per message. The number is set with `DOWNVOTE_THRESHOLD` (default 3).

## 2.31.0

### Added
- **Emoji Reactions**: react to a message instead of typing a command.
  - 🗑️ on a bot answer (preview, TL;DR, download) deletes it for everyone; only the person who asked for it, or the bot admin, can do this.
  - ⚡ runs `/tldr`, 🖥️ runs `/preview`, 📦 runs `/webxdc` for the first link in the reacted message.
  - 🏛️ saves the link to the Web Archive; the bot answers with the reaction “🏛️ Saved to Web Archive!” (❌ on failure) and sends no message.
  - 💾 saves the link to KaraKeep (admin only, when KaraKeep is configured); the bot answers with the reaction “☑️ Saved to KaraKeep!” (❌ on failure).
  - Same rate limit and exclusion rules as the commands.

## 2.30.0

### Added
- **Real Map for Google Maps Links**: links to Google Maps (`maps.app.goo.gl`, `goo.gl/maps`, `google.*/maps`, `maps.google.*`) now get a preview with a map of the place and a marker, instead of Google's generic Europe map. The place is taken from the coordinates in the link or, if there are none, looked up by name on OpenStreetMap Nominatim. The map is drawn from OpenStreetMap tiles (with attribution) and cached like other preview images.

## 2.29.0

### Added
- **`/google` Cost Estimate in `/stats`**: each paid `/google` search now logs its token counts and number of search queries (answers from the cache are not logged). For the bot admin `/stats` shows the searches, tokens and search queries of the last 24 hours and 30 days, an estimated token cost from Google's list prices (the introductory prices of Flash 3.8 and Gemini 4 Argon/Carbon switch on their end dates), and how many of the 5000 free search queries of the month are used, with about $14 per 1000 beyond that. It is an estimate; the real bill is in AI Studio. The usage history is kept for 400 days.

## 2.28.0

### Added
- **Cost Controls for `/google`** (it runs on the paid key):
  - `GEMINI_SEARCH_THINKING` sets the reasoning depth (default `low`). In a test the same question took 28 s and about 4400 output tokens at the model default, and 9 s and about 1300 at `low`.
  - Identical questions (same text and chat language) are answered from memory for `GOOGLE_CACHE_MINUTES` (default 60) instead of a new paid request.
  - `GOOGLE_DAILY_LIMIT` (default 100, all users, rolling 24 h) and `GOOGLE_USER_DAILY_LIMIT` (default 10 per user, the admin is exempt) stop runaway use; cached answers do not count.
  - `GEMINI_SEARCH_MODELS` chooses the models `/google` uses and their order, separately from `GEMINI_MODELS`.

### Fixed
- `/google` no longer tries Gemma models, which cannot use Google Search and would have answered without searching.

## 2.27.1

### Fixed
- **No Wasted Request for PDF and Video**: Gemini's code execution tool rejects PDF and video input with an HTTP 400, so `/ai` on those files made one failed request before the retry without tools. Tools are now left out for them from the start.

## 2.27.0

### Added
- **PDF and Video Attachments for `/ai`**: send `/ai` with a PDF or a video (MP4, MOV, WebM, MPEG, AVI, 3GP, FLV, WMV), or reply `/ai` to one, to get a summary or ask a question about it. The file is sent to Gemini inline, so PDFs and videos are limited to 14 MB (photos and audio keep 20 MB), and a failed size check says both limits. These requests get a 90 second time budget and 60 seconds per call, because the model needs longer for them. A PDF is recognised by its header; a video needs a video type or file extension, so an MP4 voice recording is still treated as audio. Videos stay usable with `/tldr`, as before.

## 2.26.2

### Fixed
- **Long `/google` and `/ai` Answers No Longer Cut Off**: Delta Chat shows only the first 3800 characters or 38 lines of a message and hides the rest behind "Show Full Message", which in a `/google` answer also hid the source links. The bot now shortens only the answer text so the whole message (header, answer and sources or link) stays inside both limits, cutting at a paragraph, line or sentence end and marking it with an ellipsis. The default answer style also asks the model to stay under about 2800 characters, so the conclusion is not the part that gets cut.

## 2.26.1

### Fixed
- **Real Source Links in `/google`**: the sources under a `/google` answer were long `vertexaisearch.cloud.google.com/grounding-api-redirect/...` links. The bot now reads where each redirect points (only Google's own redirect host is contacted, the source pages themselves are not fetched) and shows the real page URLs, with the old link kept if that fails. Sources that point to the same page are listed once.

## 2.26.0

### Changed
- **Answer Style for `/ai` and `/google`**: the prompt no longer caps answers at 2-3 paragraphs. Simple or factual questions now get a direct answer in a word or a sentence or two without filler, and complex questions get a reasoned answer (key considerations, steps, then the conclusion) with as much space as it needs. The wording is the new optional `AI_ANSWER_STYLE` setting in `.env`; empty keeps the built-in default. `/tldr` and previews are unchanged.

## 2.25.0

### Added
- **Adjustable `/ai` Limits**: `AI_CONTEXT_CHARS` (article or quoted text sent as context, default 16000, up to 200000) and `AI_MAX_OUTPUT_TOKENS` (answer cap, default 4096, up to 16384) can now be set in `.env`. The defaults are the old fixed values, so nothing changes until they are raised. `/tldr`, previews and `/google` are not affected.

## 2.24.0

### Added
- **`/google` Command**: answers a question from live Google Search results (Gemini grounded in Google Search) and lists up to 3 source links. It also works as a reply to any message. It needs the new `GEMINI_SEARCH_API_KEY`, a paid Gemini key, because Search is not available on the free tier; that key is used for `/google` only, while `/ai`, `/tldr`, previews and captions stay on `GEMINI_API_KEY`. There is no fallback to the free key or OpenRouter, since they would answer without searching. If the key is rejected (for example prepaid credits run out) `/google` pauses for an hour. Answers are never cached.

### Changed
- **`GEMINI_AI_API_KEY` Is Now `GEMINI_SEARCH_API_KEY`**: the paid key no longer serves all of `/ai`; it serves `/google` only, so `/ai` is back on `GEMINI_API_KEY`. Rename the variable in `.env`.
- The Gemini API key is now sent only in the `x-goog-api-key` header, no longer also in the request URL.

## 2.23.0

### Added
- **Separate Gemini Key for `/ai`**: the new optional `GEMINI_AI_API_KEY` is used only for `/ai`, so a paid key can serve `/ai` while `/tldr`, previews and captions stay on the free `GEMINI_API_KEY`. The two keys have separate per-model cooldowns and share one time budget. If the `/ai` key is rejected (HTTP 401, 402 or 403, for example when prepaid credits run out), `/ai` goes back to the main key for an hour instead of failing.

### Changed
- The Gemini API key is now sent only in the `x-goog-api-key` header, no longer also in the request URL.

## 2.22.0

### Added
- **Optional Gemini Tools for `/ai`**: the new `GEMINI_TOOLS` setting (empty by default) turns on built-in Gemini tools for `/ai` one at a time: `code_execution`, `url_context` and `google_search`. `/tldr`, previews and captions never use them. Gemma models are sent no tools. If a model or key rejects the tools (for example Google Search on a free key), the same model is retried at once without them and skipped for tools for an hour, so the model stays in the fallback chain. Answers are not cached for 24 hours while `google_search` is on.

## 2.21.0

### Added
- **Gemini 4 Hydrogen First in the Chain**: `gemini-4-hydrogen` is now the first model tried for `/tldr`, `/ai` and preview captions. `gemini-3.8-flash` and the older models stay behind it, so if Hydrogen is rate limited, overloaded or times out, the usual fallback applies. The model name is still shown under each AI answer. A `GEMINI_MODELS` set in `.env` overrides the new default.

## 2.20.1

### Changed
- **Current Chrome User-Agent**: the standard browser User-Agent now says Chrome 158 instead of Chrome 120, which had not changed since the first release and could look outdated to sites that check it.

## 2.20.0

### Added
- Private Delta Chat warnings to the bot administrator when Jina tokens fall below 1,000,000 or Reader returns HTTP 402. Balance is checked only on Reader requests, in a background thread that does not delay the reply, at most once an hour. Each warning has a separate 24-hour cooldown persisted across restarts, and is sent to the admin's key contact so it stays encrypted.

## 2.19.0

### Changed
- **Delta Chat Core 2.66.0**: `deltachat-rpc-server` is pinned to 2.66.0 (was 2.65.0). Core 2.66 removes the `configured_addr` config: `get_config("configured_addr")` now fails with "unknown key", and `addr` has been empty since core 2.61. The bot's own address now comes from its self contact (`dc_fingerprint.get_self_addr()`), which the core fills from the primary relay; this also works on older cores.

## 2.18.2

### Security
- **Admin Check No Longer Fooled by a Display Name**: The contact's key fingerprint was found by searching the whole `get_contact_encryption_info()` text for hex strings, including the line with the contact's display name, so a contact named `x<admin fingerprint>x` passed the admin check. The fingerprint is now read only from the lines under each key header, and the bot's own key is recognised by the fingerprint in its invite link instead of by its address. When the keys cannot be told apart the check fails instead of guessing. The code is in `dc_fingerprint.py`, shared verbatim between the bots.

### Changed
- **Ready for the Core 2.66 Fingerprint Format**: Core 2.66 prints `Me:` instead of `Me (address):` and sorts the key blocks by fingerprint, so finding a key block by address stops working. The new parser handles both formats.
- **Core Pinned to 2.65.0**: `deltachat-rpc-server` was `>=2.62.0`, so any image rebuild pulled core 2.66.0, which removes the `configured_addr` option the bot still reads. Core upgrades are now made on purpose, after reading the core changelog.

## 2.18.1

### Changed
- **Download Limit 64 KB Instead of 1 Byte**: The intent was to skip attachments, but with a limit of 1 byte the Delta Chat core treats every incoming message, plain text too, as too large and fetches it later one by one instead of in the normal batch, which delayed previews of links. With 64 KB links arrive at once, while photos and files (over 64 KB) are still not downloaded. `DOWNLOAD_LIMIT` (default now `65536`) still overrides it.

## 2.18.0

### Added
- **Automatic account creation**: `serve` without a configured account no longer exits with "account not configured". The bot creates its own account: `init_transports` (core 2.62+) without a QR code lets the core probe its built-in chatmail relay list, configure the fastest relay and add further relays in the background. The new address is logged. If creation fails, the error is logged and `serve` exits as before, so the container restart retries. `bot.py init <addr> <password>` and `bot.py init DCACCOUNT:server.tld` still work and take precedence; the "Initialize Account" setup step is now optional.

### Changed
- **The server runs releases, not the tip of `main`.** `update.sh` deploys the newest `vX.Y.Z` tag, so a merge into `main` reaches the server only once it is released; several PRs can go out together. `UPDATE_REF` in `.env.local` pins a release (`UPDATE_REF=v2.17.1` - a rollback; empty again = newest) or follows a branch as before (`UPDATE_REF=main`). A release tag moved on GitHub or Forgejo makes the update fail instead of deploying the changed code. Errors that stopped the script with a message (both remotes unreachable, an unknown `UPDATE_REF`) now also ping the healthcheck's `/fail`, not only failed commands. The script now runs as one function, so the `git reset` that rewrites `update.sh` cannot confuse the running copy.
- **Releases are published by a tag** (new `.github/workflows/release.yml`): pushing `vX.Y.Z` checks that `bot.py` has that version, creates the GitHub release with the version's section of this file as its notes (an existing release is left alone), then sends the ntfy notification and the `bot-updated` dispatch to `hass-addons-deltachat` (now with `"version"` in the payload). Both used to go out on every push to `main` (`webpreview-changelog.yml`, removed), so Home Assistant users got unreleased code.
- Releasing: merge, then `git tag -a vX.Y.Z -m "..." <commit> && git push origin vX.Y.Z`.
- **Upgrading:** tag `v2.18.0` right after merging this. Until then the new `update.sh` would deploy `v2.17.1`, which still has the old script that follows `main` - and the server would switch back and forth on every run.

## 2.17.1

- **MIT License**: the project is now licensed under MIT (`LICENSE`).

## 2.17.0

- **`/transports` Shows the Relay Actually Used for Sending**: Since core 2.61 the core sends through the relay that last worked and switches only when it cannot connect, so the main address (`configured_addr`) says nothing about where mail goes out. `/transports` now lists relays in the order the core tries them, with the current sending relay first, shows the core's send queue (waiting messages and retries) and outgoing status, and per relay the incoming status, when the last message arrived, mailbox storage usage (⚠️ from 80%) and when it was added. The sending order and queue are read from the core's account database (read-only); the report is built by the shared `transports_view.py`.
- **Removed Misleading Per-Relay Sent/Received Counters**: They credited every message to `configured_addr` (or, in some places, the wrong address), so the numbers and "last sent" dates were wrong once the core sent through another relay. Counting them also cost extra RPC calls per message. The `transport_stats` table is left in place but no longer updated.

## 2.16.0

### Removed
- **Bot-Side Relay Failover**: Removed the `MSG_FAILED` failover handler and the resilient-send `send_msg` patch. Both switched `configured_addr` and called `resend_messages`, but since Delta Chat core 2.61 the SMTP relay is no longer chosen by `configured_addr`: the core tries the newest relay first and falls back to the next one if a relay is unreachable. The old logic could no longer switch relays and only caused delayed duplicate resends.

### Changed
- **`/setprimary` and `/resilient` Deprecated**: Both commands are disabled and only reply with an explanation of how the core picks relays now. They are removed from `/help` and the README.
- **`/transports` Sending Order**: Relays are listed newest first, in the order the core tries them for sending, instead of marking `configured_addr` as "Used for sending".
- **Core Requirement**: `requirements.txt` now requires `deltachat-rpc-server>=2.62.0`.

## 2.15.2

### Fixed
- **Odd OpenRouter Models**: `openrouter/free` alone could route to a moderation classifier (`nvidia/nemotron-3.5-content-safety:free` answered "User Safety: safe") or a coding model. The default `OPENROUTER_MODELS` is now an ordered list of free chat models tested with Russian prompts (Nemotron 3 Ultra/Super, Qwen 3.8, Gemma 4 31B, dots-3), with `openrouter/free` as the last resort, and answers from `*safety*`/`*guard*` models are discarded.
- **403 Stopped the Whole Fallback**: A model-specific HTTP 403 aborted OpenRouter entirely; now only 401/402 (bad key / no credits) do, and 403 moves on to the next model.
- **OpenRouter Time Cap**: The OpenRouter chain is capped at 60s in total (30s per request).

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
