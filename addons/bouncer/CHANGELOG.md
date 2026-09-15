# Changelog

## 2.11.3

### Media Optimization & Post Cleanup
- **Automatic WebP Image Compression**:
  - Attached images (`.jpg`, `.jpeg`, `.png`, `.bmp`) in channel posts are automatically compressed to modern WebP format (`quality=80`, `method=3`, `max_dim=1600`) via Pillow on ingestion.
  - Reduces media traffic by 70–90% for web preview pages and RSS feed readers.
  - Animated GIFs and SVGs are preserved in their native formats.
  - Graceful fallback to original image format and file serving if compression fails or Pillow is unavailable.
  - Backwards-compatible resolution in `handle_media_file` allows requests for `.jpg`/`.png` to seamlessly serve `.webp` when available.
- **Delta Chat Attachment Fallback Stripping (`DC_FALLBACK_PATTERN`)**:
  - Automatically filters out Delta Chat core email fallback placeholders (e.g. `[Image – 304.26 KiB]`, `[Document - file.pdf]`) from message text, preventing redundant metadata labels from cluttering post previews when attachments are displayed natively while preserving authentic author text.

## 2.11.2

### Improvements & UI
- **Spacious `/dchannels` Catalog Layout**:
  - Re-architected `/dchannels` output with a clear multi-line format separating command/title, description, and preview link onto distinct lines.
  - Channels are now cleanly delineated with blank lines (`\n\n`) for optimal readability in Delta Chat mobile and desktop clients.
- **Forgejo Mirror in Channel Previews**:
  - Added the Forgejo repository mirror link (`https://git.gluek.info/gluek/deltachat_bouncer`) alongside version number in the footer of public channel preview pages (`/c/{token}`).

## 2.11.1

### Web Service & Channel Previews
- **Rich Markdown Post Formatting (`format_markdown_html`)**:
  - Full CommonMark and Delta Chat formatting engine with support for bold (`**text**`, `__text__`), italic (`*text*`, `_text_`), strikethrough (`~~text~~`), inline code (`` `code` ``), fenced code blocks with syntax styling (` ```lang ... ``` `), blockquotes (`> text`), spoilers (`||spoiler||` with click-to-reveal), and links (`[label](url)` and autolinked URLs).
  - 100% XSS immunity via strict HTML escaping and javascript/data URI protocol stripping.
  - Channel preview post timeline and RSS feed item descriptions (`<![CDATA[ ... ]]>`) now render rich markdown identically to ArcaneChat / Delta Chat clients.
- **In-Memory Caching Layer & High Load Optimization**:
  - Added fast in-memory response caches with TTL and ETag headers for channel web preview pages (60s TTL) and RSS feeds (120s TTL), returning `304 Not Modified` on matching `If-None-Match`.
  - Added in-memory binary caching for QR code generation (SVG and PNG) to eliminate repeated CPU-bound QR rendering.
  - Event-driven cache invalidation hooks automatically purge channel caches on new incoming posts (`_ingest_channel_post`), channel removals (`/dchannelremove`), or base URL changes (`/url`).
- **Crawler & Bot Blocking (`robots.txt`)**:
  - Configured `robots.txt` (`/robots.txt`) with `User-agent: *\nDisallow: /\n` to block search engine scrapers and AI crawlers from generating unnecessary traffic.

## 2.11.0

### Web Service & Channel Previews
- **Home Assistant Ingress Support**:
  - Integrated Home Assistant Ingress on port 8080 with seamless sidebar navigation (`Open Web UI`).
  - Added support for `X-Ingress-Path` dynamic header for proper subpath asset resolution (logos, avatars, QR codes, links).
- **Public Channel Web Preview (`/c/{token}`)**:
  - Implemented an embedded, lightweight aiohttp web server providing instant web preview pages for channels registered in `/dchannels`.
  - Each channel is assigned a unique, unguessable 12-character base62 token.
  - Channel preview pages feature a modern dark-mode aesthetic (matching Uptime Bot), displaying channel name, description, member count, avatar, and a live message timeline.
  - Interactive Delta Chat join dialog with dynamic QR code generation (SVG and PNG download options), deep links (`https://i.delta.chat/#...` and `OPEN-CHAT:...`), and one-click clipboard copying.
  - Media file support: attached photos, videos, voice notes, audio, and documents are displayed inline and served directly from a dedicated media cache directory (`CHANNEL_MEDIA_DIR`).
- **Standard RSS 2.0 Feeds (`/c/{token}/rss.xml`)**:
  - Full-fidelity RSS feed at `/c/{token}/rss.xml` (with convenient `/c/{token}/rss` redirect).
  - Includes channel metadata, item timestamps (RFC 822), author names, message contents, and media enclosures for RSS readers.
- **Graceful Channel Removal & Tombstone**:
  - Channels removed from the catalog via `/dchannelremove` are soft-deleted (`is_deleted = 1`).
  - Accessing a removed channel's preview URL displays a clean tombstone notice (*"The channel has been removed from the public catalog and is no longer available for preview."*) instead of a generic 404.
- **Core Handshake Backfill**:
  - Automatically backfills the initial batch of up to 10 messages provided by the Delta Chat core handshake upon joining via `/dchanneladd <url>`.
  - Real-time ingestion stores subsequent incoming channel messages up to a sliding window of 100 posts per channel.
- **Base Web URL Configuration (`base_url`)**:
  - Added `base_url` add-on configuration option and `/url` admin command to view or configure the public base URL stored in database settings.
  - Supports fallback to `BASE_URL` environment variable.
  - Updated `/dchannels` and `/dchannel<ID>` commands to provide preview URLs alongside join links.
- **Optional Direct Access (Port 8080)**:
  - Exposed port `8080/tcp` in add-on configuration for optional direct external reverse proxy access.
- **Landing Page (`/`)**:
  - Public landing page introducing Bouncer Bot capabilities, active channel counts, and Delta Chat connection instructions.

## 2.10.1

### Improvements
- **In-Place Live Message Updates for VirusTotal Scans (`send_edit_request`)**:
  - When submitting a new URL or file for analysis (404 in VirusTotal database), the bot now posts an immediate interim status message (`Analysis is in progress...`) and sets the `⏳` reaction.
  - The worker polls VirusTotal in the background for up to 12 attempts (~3 minutes with the 15-second rate limiter).
  - Upon completion, the bot updates the interim message in-place via Delta Chat RPC `send_edit_request` with the complete vendor detections and analysis report, and sets the final reaction (`☑️`, `⚠️`, `🚨`).
  - If analysis exceeds 12 polling attempts, the message is updated with a timeout notice directing the user to the web report (`⚪️`).
- **Clean Markdown URL Formatting**:
  - Removed enclosing backticks around URLs in reports to prevent Delta Chat markdown parsers from appending `%60` to links.

## 2.10.0

### Security & VirusTotal Inspection
- **VirusTotal Link & File Inspection (`/virus`)**:
  - Added `/virus <url>` command to inspect links for phishing, malware, and threats via VirusTotal API v3.
  - Added reply inspection: replying to a message with `/virus` automatically detects and scans either an attached file or the first URL in the quoted message.
  - Added direct file inspection: sending a message with an attached file and `/virus` caption triggers a file scan.
  - **On-Demand Attachment Download**: Automatically downloads full message attachments via Delta Chat RPC (`download_full_message`) when messages arrive without auto-downloaded blobs (`download_limit=1`).
  - **Hash-First Querying**: Computes SHA-256 locally and checks existing VirusTotal reports first, avoiding redundant file uploads and conserving bandwidth.
  - **Direct Upload Fallback**: If a file (up to 32 MB) is not present in the VirusTotal database, it is uploaded via multipart/form-data and polled until analysis completes.
  - **Global Rate Limiting & Queueing**: Enforces a strict 1-check-per-15-seconds rate limit across the entire bot to safely respect VirusTotal free tier limits (4 lookups/min). Additional incoming requests receive a queue notification (`⏳ Another VirusTotal check is in progress, your request is queued...`) and are processed in FIFO order.
  - **Visual Progress & Reactions**: Sets `⏳` reaction on trigger message during queuing and scanning, updating to `☑️` (clean), `⚠️` (suspicious), `🚨` (malicious), or `❌` (error) upon completion.
  - Configurable via `VIRUSTOTAL_API_KEY` in `.env` or container environment.

## 2.9.3

### User Experience & Command Reporting
- **Transparent Observation Progress in `/bounce`**:
  - In group chats with `/autokick` enabled, `/bounce` now distinguishes between truly active members and silent members under observation.
  - When members have not reached the warning threshold yet, `/bounce` displays an **Observation in progress** status reporting the number of silent members and the countdown to the earliest warning window (e.g. at day 83 of observation) instead of misleadingly claiming all users are active.
  - Added total member count to the all-active report when every member has verified recent activity.
  - Added observation summary note to the warning report when additional silent members remain under observation.
- **Informative Metrics in `/autokick` Status**:
  - Displays the number of days the bot has monitored the group.
  - Displays the count of silent members under observation and the countdown until their earliest warning.
  - Reports the count of members currently in the warning window (< 7d to kick).
- **Accurate Candidate Reason Formatting**:
  - Updated candidate descriptions from `never seen in Xd since joined` to `never seen in Xd of observation`, reflecting actual observation time rather than join time.
- **Autokick Overview Helper (`_get_chat_autokick_overview`)**:
  - Unified autokick metrics collection and candidate evaluation into a single-pass helper reused across `/bounce`, `/autokick`, and background monitor routines.

## 2.9.2

### Performance & Database Architecture
- **Persistent Writer Connection**:
  - Replaced ad-hoc connection creation on every write with a dedicated persistent writer connection protected by `_write_lock` and standard transactional context manager (`_writer_transaction()`), eliminating connection teardown churn and disk sync overhead.
- **Strict `PRAGMA synchronous = NORMAL` & `busy_timeout`**:
  - Enforced `PRAGMA synchronous = NORMAL;`, `PRAGMA journal_mode = WAL;`, and `PRAGMA busy_timeout = 5000;` on all database connections across the entire codebase.
- **Concurrent Non-Blocking WAL Reads**:
  - Replaced global `_lock` on read operations with independent read connections, allowing concurrent readers to execute simultaneously alongside writer without lock contention.
- **Batch Contact Seeding**:
  - Replaced N+1 individual insert queries in catalog member count refresh (`_refresh_catalog_member_counts`) with `ensure_contacts_first_seen_batch()`, recording contacts in a single atomic transaction.

## 2.9.1

### Security Hardening & Concurrency Fixes
- **Fix Undefined `resilient_lock`**:
  - Declared `resilient_lock` globally, fixing runtime `NameError` crash during resilient sending and message failover.
  - Synchronized transport switching and message sending during resilient delivery.
- **Server Domain Input Validation (`/cmping`)**:
  - Added strict regex domain validation (`DOMAIN_REGEX`) to `/cmping`, `/cmpingadd`, and `/cmpingdel` commands to prevent command injection and malformed subprocess parameters.
- **Credential Protection (`/addtransport`)**:
  - Enforced that `/addtransport` can only be executed in private 1-on-1 chats with the bot, preventing accidental password leakage in group chats.
- **Rate Limiting (`/slap`)**:
  - Added 15-second cooldown per chat for `/slap` commands.
- **Sanitized User Error Messages**:
  - Removed internal exception and traceback disclosures from user-facing error messages in `/kick`, `/invite`, `/relays`, `/approve`, `/decline`, and `/addtransport`.
- **Bounded Message Deduplication**:
  - Replaced full set clearing with an `OrderedDict` maintaining up to 2000 recent message IDs with FIFO eviction, preventing duplicate command execution.

### High-Load & Database Optimizations
- **SQLite WAL & Concurrency PRAGMAs**:
  - Enabled `PRAGMA journal_mode = WAL`, `PRAGMA synchronous = NORMAL`, `cache_size = -4000`, and `busy_timeout = 5000` for high concurrency and performance under load.
- **Buffered Transport Statistics**:
  - Buffered sent/received message statistics in memory, flushed to SQLite in a single transaction every 30 seconds instead of executing database writes on every individual message.
- **Database Indexes**:
  - Added indexes on `autokick_warnings(chat_id)`, `pending_requests(chat_id, approved)`, `away_notifications(away_updated_at)`, and `cmping_history(checked_at)`.
- **Automated Data Pruning**:
  - Added periodic pruning in background monitor loop for `away_notifications` and `cmping_history` older than 30 days.
  - Added periodic in-memory cleanup of stale anti-spam timestamps and unused domain locks.

## 2.9.0

### Added
- **Two-Stage Inactivity Warning System for `/autokick`:**
  - Inactive members now receive a direct 1-on-1 private notification from the bot before being kicked, warning them of impending removal and inviting them to stay by posting in the group.
  - The group chat receives a daily summary broadcast (at most once every 24 hours) listing all members in the warning zone with days remaining until removal.
  - **Kick Protection:** Members are now strictly kicked only after receiving a warning and passing a minimum 24-hour grace period.
  - Dynamic warning threshold: warnings begin at `autokick_days - 7` days for thresholds $> 7$ days (i.e. 7 days before kick), and at `autokick_days - 1` days for thresholds $\le 7$ days.
  - Warnings are automatically cleared as soon as a user sends a message in any shared chat.
- **Cryptographic Fingerprint Ignore List (`/autokick ignore`):**
  - Added `/autokick ignore <email/nick/id>` for bot administrators to look up a member, extract their cryptographic key fingerprint, and permanently exempt them (e.g. service bots or quiet system accounts) from auto-kick.
  - Added `/autokick unignore <fingerprint/email/nick>` to remove exemptions.
  - Added `/autokick ignore` / `/autokick ignore list` to display all currently exempted fingerprints and notes.
- **Exemption for `/away` Users:**
  - Members with an active `/away` vacation/absence status are automatically exempt from inactivity warnings and auto-kicks.
- **`/bounce` Integration with `/autokick` Thresholds:**
  - In group chats where `/autokick` is active, `/bounce` now shows members currently in the warning window (< 7 days or < 1 day remaining until auto-kick).
  - In groups where `/autokick` is disabled, `/bounce` continues to report inactivity based on the default 21-day threshold.
- **Grace Period Protection for New Members:**
  - Utilizes `contact_first_seen` tracking so newly joined members who have not yet spoken (`last_seen == 0`) are protected by a grace period based on their join time, preventing premature autokicking.
- **Database Schema Upgrades:**
  - Added `last_autokick_warn_at` column to `chats` table.
  - Added `autokick_warnings` and `autokick_ignored_fingerprints` tables.

## 2.8.2

### Added
- **Options.json Fallback for Display Name & Status Text**:
  - `on_init` now checks `/data/options.json` fallback when `DISPLAY_NAME` or `STATUS_TEXT` are not set in environment variables.

## 2.8.1
- Initial Home Assistant Add-on release.
- Group inactivity monitoring, `/autokick` of stale members, and chat/channel catalogs.
- Mail relay testing and connectivity monitoring via `cmping`.
