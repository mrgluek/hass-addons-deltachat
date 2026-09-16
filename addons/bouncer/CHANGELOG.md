# Changelog

## 2.13.2

### Security & Hardening
- **Rate Limiting on All Public Web Endpoints** (`#5`):
  - Extended `@rate_limited` decorator coverage to every public-facing HTTP handler: `handle_icon`, `handle_background`, `handle_index`, `handle_qr_svg`, `handle_qr_png`, `handle_channel_qr_png`, `handle_channel_qr_svg`, `handle_channel_avatar`, `handle_channel_rss`, `handle_media_file`, `handle_ap_actor`, `handle_ap_outbox`, `handle_ap_followers`, `handle_ap_following`, `handle_ap_post`, `handle_webfinger`, `handle_nodeinfo_discovery`, `handle_nodeinfo`, `handle_api_v1_instance`.
  - Removed duplicate inline `check_rate_limit` calls from previously partially-protected handlers.
- **Trusted Proxy IP Extraction** (`#7`):
  - Added `_get_client_ip()` function: only honours `X-Forwarded-For` when the direct peer IP belongs to a trusted local reverse proxy (`127.0.0.1`, `::1`, `localhost`), preventing IP spoofing by external clients.
  - Added `_TRUSTED_PROXIES` set for configurable trusted proxy list.
- **ActivityPub Key Ownership Verification** (`#8`):
  - Added `is_key_owned_by_actor(key_id, key_doc, actor)` function in `activitypub.py` to verify that a resolved signing public key actually belongs to the claiming actor (via `owner`, embedded publicKey, actor `id`/`url` matching, or key URI fragment).
  - Integrated ownership check into `handle_ap_inbox()` after successful key resolution; rejects requests where the key's declared owner does not match the activity actor with HTTP 401.
- **Caddy X-Forwarded-Proto Header** (`#6`):
  - Added `header_up X-Forwarded-Proto {scheme}` to `Caddyfile` reverse proxy configuration so the upstream application can reliably detect HTTPS.

### Bounded Memory & SQL Queries
- **Bounded `_qr_cache`** (`#1`): Capped QR code cache at 200 items with FIFO eviction.
- **Bounded `_cmping_server_status`/`_cmping_server_errors`** (`#4`): Added `_set_cmping_server_status()` helper capping those dicts at 500 entries.
- **Bounded SQL Queries** (`#3`):
  - `get_all_cmping_results()` now adds `ORDER BY checked_at DESC LIMIT ?` (default 500).
  - `get_cmping_incident_downtime_events()` now adds `LIMIT ?` (default 500).

### Performance & Debug
- **Guarded Debug Logging** (`#2`): Wrapped hot-path `logger.debug()` calls with `logger.isEnabledFor(logging.DEBUG)` guards to avoid f-string evaluation overhead when debug is off.

### Web & Accessibility
- **QR Modal Focus Trap** (`#9`):
  - Added `openQrModal()` / `closeQrModal()` JS functions to both landing page and channel preview page that capture the opener button's focus, move focus into the modal on open, trap Tab/Shift-Tab within modal focusable elements, and restore focus on close.
  - Pressing Escape now correctly calls `closeQrModal()` and returns focus.
- **Inline Copy Feedback on QR Modal** (`#10`):
  - Replaced `alert('Link copied to clipboard!')` with inline `✓ Copied!` button-text feedback via new `copyJoinLink()` function; reverts after 2 seconds without blocking the page.
- **RSS Language Tag Removed** (`#13`):
  - Removed hardcoded `<language>en</language>` tag from RSS channel XML, since channel content language is user-determined.

## 2.13.1

### Security & Hardening
- **Restricted Database File Permissions**:
  - Enforced POSIX `0o600` permissions on the primary SQLite database file and WAL sidecars (`-wal`, `-shm`) during database initialization and connection setup, protecting stored plaintext ActivityPub private keys and configuration data.
- **Strict Static Asset Whitelisting**:
  - Restricted `handle_icon` and `handle_background` to explicit filename allowlists (`_ALLOWED_ICON_FILENAMES`, `_ALLOWED_BG_FILENAMES`) to prevent unauthorized file access or path disclosure.
- **ActivityPub Foreign Target Inbox Validation & Backfill Rate Limiting**:
  - Enforced host matching between the follower actor URI and target delivery inbox URI in `handle_ap_inbox()`, rejecting delivery and backfill attempts to foreign/victim inboxes.
  - Added concurrency throttling (`asyncio.Semaphore(2)`) and a 10-second per-channel cooldown to follower post backfilling to prevent inbox bombing and outbound resource exhaustion.
- **RSS CDATA Breakout Prevention**:
  - Implemented `_escape_cdata()` to escape `]]>` sequences into `]]]]><![CDATA[>` across channel titles, descriptions, and post contents in RSS XML generation, preventing feed breakage and malformed XML.

### Bug Fixes & API Consistency
- **Mastodon/Pleroma `GET /api/v1/instance` Admin Email Resolution**:
  - Fixed configuration key lookup in `handle_api_v1_instance()` to check `admin_dc_email` prior to `admin_email`, accurately returning the bot administrator's contact email.

### Web & RSS Polish
- **Per-Post Permalinks & HTML Anchors**:
  - Added unique per-post permalink URIs (`<link>` and `<guid isPermaLink="true">` with `#post-{msg_id}`) to RSS 2.0 items and matching `id="post-{msg_id}"` anchor attributes to web preview articles for direct message linking.
- **Zero-Repaint Background Rendering**:
  - Replaced `background-attachment: fixed` with a fixed pseudo-element (`body::before`) across landing, preview, and error page templates, eliminating high scrolling repaint costs.
- **Responsive Layout & Accessibility Polish**:
  - Improved channel grid layout responsiveness on small viewports (<340px) using `minmax(min(280px, 100%), 1fr)`.
  - Upgraded `--text-muted` color to `#aebac1` achieving WCAG AA contrast ratio (>4.5:1).
  - Added `@media (prefers-color-scheme: light)` support for automated light theme rendering across landing and preview pages.

## 2.13.0

### Security & Hardening
- **Environment File Gitignore (`S4`)**:
  - Added `.env` to `.gitignore` to prevent accidental credential, token, and API key exposure while retaining `.env.example`.
- **Host Header & Base-URL Poisoning Protection (`S5`)**:
  - Validated incoming `X-Forwarded-Host` and `Host` headers in `_get_base_url()` against strict URL scheme and hostname syntax rules (`SAFE_HOST_REGEX`), preventing cache and link poisoning when `BASE_URL` is unset.
  - Added `header_up Host {host}` and `header_up X-Forwarded-Host {host}` to `Caddyfile` reverse proxy configuration.
- **ActivityPub Replay Prevention & KeyId/Actor Binding (`S6`)**:
  - Implemented 300s TTL HTTP signature anti-replay cache (`check_and_record_signature_replay()`) in `activitypub.py` tracking signature digests.
  - Enforced strict origin matching between signing `keyId` URI and activity `actor` URI in `handle_ap_inbox()`, rejecting spoofed cross-origin signatures.

### UI & UX Improvements
- **Independent Command Cooldowns (`U5`)**:
  - Decoupled cooldown state tracking into separate dictionaries (`_chat_bounce_anti_spam`, `_chat_top_anti_spam`, `_chat_invite_anti_spam`) so executing `/bounce`, `/top`, or `/invite` never blocks another command.
- **Safe Bare `/away` Query (`U6`)**:
  - Invoking bare `/away` without arguments now safely displays the user's current away status or usage instructions without inadvertently clearing away state or sending `_is back_` notifications.
- **Community Multi-Chat Age Indicators (`U7`)**:
  - Replaced circle emojis with colored squares (`🟥🟧🟨🟩🟦🟪🟫⬛⬜`) for contacts who are active across multiple community chats, visually distinguishing experienced community members.
  - Streamlined new member welcome greetings by removing redundant `(💬 X)` tokens.
- **Social Media Metadata for Web Previews (`U8`)**:
  - Added OpenGraph (`og:title`, `og:description`, `og:image`, `og:type`) and Twitter Card (`twitter:card`) meta tags to the channel directory landing page.
- **Accurate RSS Enclosure Sizes (`U9`)**:
  - Resolved true file byte sizes on disk or in-memory buffers for `<enclosure length="...">` attributes in `generate_rss_xml()`, replacing placeholder zero values.
- **Accessible QR Code Modals (`U10`)**:
  - Added ARIA accessibility attributes (`role="dialog"`, `aria-modal="true"`, `aria-labelledby="qr-modal-title"`) and ESC key event listener to QR join modals across landing and channel preview pages.
- **Dynamic Fediverse Domain Resolution (`U11`)**:
  - Resolved Fediverse domain dynamically from server configuration without hardcoded `dc.gluek.info` fallbacks, hiding the Fediverse button gracefully if no public domain is configured.
- **Whole-Word Away Mention Matching (`U12`)**:
  - Replaced substring matching in group mention detection with word-boundary regex (`(?i)(?<!\w)name(?!\w)`), eliminating false positive away alerts (e.g. "Dan" matching "Daniel").
- **Command Documentation Clarifications (`U13`, `U14`)**:
  - Updated `/help` descriptions: `/contact<ID>` clearly indicates sharing a contact card, and `/relays` accurately reflects scanning for public Russian mail providers.
- **Role and Status Badges (`U15`)**:
  - Added visual user badges in `/search` and `/bounce` output: `👑` (Bot Administrator), `⭐` (Autokick Ignored), and `💤` (Away).

### Performance & Resource Optimization
- **Adaptive Polling Backoff (`P3`)**:
  - Implemented adaptive sleep intervals in background channel join and message resend workers (`bg_channel_join_worker`, `bg_resend_worker`), scaling sleep up to 30s when queues are idle.
- **Bounded Read Query Limits (`P4`)**:
  - Added default safety `limit` parameters to database read functions (`get_all_catalog_chats`, `get_all_catalog_channels`, `get_all_transport_stats`, `get_all_autokick_ignored_fingerprints`, `get_all_active_cmping_incidents`, `get_ap_followers`, `get_ap_follower_inboxes`).
- **In-Memory Cache Pruning (`P5`)**:
  - Bounded `_cmping_last_results` cache to 500 entries with automatic pruning of oldest entries.
  - Pruned server status and error records from `_cmping_server_status` and `_cmping_server_errors` when servers are removed via `/cmpingdel`.
- **Lazy Debug Log Formatting (`P6`)**:
  - Protected expensive key fingerprint formatting and admin lookup debug logging behind `logger.isEnabledFor(logging.DEBUG)` guards.

## 2.12.9

### Performance & Scalability
- **SQLite Reader Connection Pooling (`P1`)**:
  - Implemented thread-safe LIFO read connection pool (`_ReaderConnectionPool`) and connection wrapper (`_PooledConnection`) with automatic pool invalidation on dynamic database switches.
  - Added `_reader_connection()` context manager and refactored all 46 read operations in `database.py` to reuse pooled connections.
  - Accelerated unit test suite execution from 33.0s down to 2.7s (>12x speedup) while guaranteeing concurrent reader isolation under SQLite WAL mode without thread contention.
  - Updated `close_db()` to safely drain and close pooled reader handles alongside the primary writer handle.
- **Non-Blocking Background Workers & Offloaded I/O (`P2`)**:
  - **VirusTotal Inspection (`/virus`)**: Decoupled message quote resolution and file attachment downloads (`_get_msg_file_info`) from the Delta Chat event handler thread into background daemon worker `bg_virus_worker`. Command handler responds immediately with `⏳` reaction (or synchronous usage message for empty invocations) without stalling incoming message processing.
  - **Channel Post Media Ingestion**: Offloaded `_ingest_channel_post` (file attachment downloading and Pillow WebP image compression) from `handle_all_messages` to a dedicated daemon thread, preventing media uploads from blocking the main Delta Chat event loop.
  - **CMPing Worker Concurrency Bounding**: Pinned `_run_cmping_subprocess` strictly to background worker thread and capped multi-server relay check thread pool (`ThreadPoolExecutor`) concurrency to `min(4, len(bot_domains))`, preventing system load and process spikes.
  - **Async-Safe QR Code Generation**: Wrapped synchronous Pillow and SVG QR generation calls (`_generate_qr_bytes`) in `handle_qr_svg`, `handle_qr_png`, `handle_channel_qr_png`, and `handle_channel_qr_svg` with `await asyncio.to_thread(...)`, keeping the aiohttp web server event loop responsive.

## 2.12.8

### ActivityPub Federation & Resilience
- **RFC 9421 HTTP Message Signatures Support**:
  - Implemented `extract_signature_info()` and full verification for RFC 9421 signatures (`Signature-Input` + `Signature: sig1=...`), including `@method`, `@target-uri`, `@path`, `@authority`, `created` timestamp verification, and signature parameters base string construction.
  - Eliminated `Missing keyId in Signature header` errors when modern Fediverse instances (e.g. Mastodon 4.3+, 4.4-alpha) retry or send requests using RFC 9421.
- **Graceful Handling of Deletion Activities for Gone/Suspended Remote Actors**:
  - Prevented infinite retry loops and 401 spam when remote instances send `Delete(Actor)` for deleted or suspended accounts whose actor endpoints return HTTP 410 (Gone) or 403 (Forbidden).
  - Cleaned up matching follower records from SQLite database and responded with `202 Accepted` after validating that the deletion request and keyId share the same origin host.
  - Downranked expected actor lookup status codes (403, 404, 410) from `WARNING` to `INFO` in logging.
- **Follower Public Key Local Caching**:
  - Added `follower_public_key` storage in `ap_followers` database table with automatic schema migration.
  - Caches follower public key PEM upon initial `Follow` activity to allow immediate local cryptographic verification for subsequent requests (`Undo`, `Delete`) without requiring outbound network requests.

## 2.12.7

### UI & UX Improvements
- **Cooldown Accuracy (`U1`)**: Updated `/help` and documentation to accurately state real command cooldowns (60s general, 15s cmping/slap, 10s search).
- **Graceful Empty Invites (`U2`)**: Render disabled button and omit QR modal when channel has no invite link.
- **Landing Page Fallback (`U3`)**: Render disabled button and clear fallback notice when bot invite link is unavailable.
- **Silent Cooldown & Queue (`U4`)**: Replaced chat text spam with `⏳` reaction on cooldown, queueing delayed execution and transitioning reaction to `☑️` upon completion.

## 2.12.6

### Security & Hardening
- **SSRF Mitigation (`S1`)**: Block private/reserved/loopback/cloud-metadata IP fetches (`is_safe_url()`) across remote actor and key resolution.
- **Cheap Signature Rejection (`S1`)**: Validate Date freshness window (±300s) and body Digest (SHA-256) prior to outbound remote `keyId` resolution.
- **Request Body Limits & Rate Limiting (`S2`)**: Limit `client_max_size` to 256 KB on `web.Application`, 64 KB on ActivityPub inbox (`413`), and apply sliding-window rate limiting (`429`): inbox (60 r/min), preview & media (120 r/min).
- **Dependency Pinning (`S3`)**: Pinned CVE-free dependency floors in `requirements.txt` and pinned `cmping` to exact commit SHA.

## 2.12.5

### Fediverse / ActivityPub Improvements
- **Recent Posts Backfill on Follow**: Deliver up to 10 recent channel posts to new followers after `Accept(Follow)`.
- **Delta Chat Wallpaper as Header Banner**: Added `"image"` field pointing to `/background.jpg`.
- **Standalone Note `@context`**: Added JSON-LD context to Note objects for direct search and dereferencing in GoToSocial.
- **Mastodon Instance Metadata (`GET /api/v1/instance`)**: Added instance metadata endpoint for Fediverse discovery.

## 2.12.4

### Fediverse / ActivityPub Fixes
- **Trailing Slash Sanitization & Multi-Slash Route Normalization**:
  - Automatically strip trailing slashes and whitespace from `BASE_URL` and `database.get_config("base_url")` across `_ingest_channel_post`, `build_actor_json`, `build_note`, and `_deliver_post` to prevent double slashes in actor URLs (`//c/{token}`) and public key identifiers.
  - Added multi-slash route patterns (`/{slash:/*}c/{token}`, `/{slash:/*}c/{token}/actor`, `/{slash:/*}inbox`, etc.) so that requests with leading multiple slashes (e.g. `////c/{token}`) sent by reverse proxies or Go HTTP clients resolve with 200 OK instead of failing with 404.

## 2.12.3

### Fediverse / ActivityPub Federation
- **Shared Inbox Support (`POST /inbox`)**:
  - Added route `POST /inbox` to receive activities sent to the instance-level `sharedInbox` advertised in Actor JSON.
  - Automatically extracts target channel token from the incoming activity's `object` / `target` properties (supporting `Follow`, `Undo`, and `Delete`).
- **Following Endpoint (`GET /c/{token}/following`)**:
  - Implemented `GET /c/{token}/following` returning an empty `OrderedCollection` (`totalItems: 0`) as requested by GoToSocial and other Fediverse servers during actor profile discovery.
- **Robust Remote Key Resolution & Authorized Fetch**:
  - Added `resolve_public_key` with support for standalone PublicKey endpoints (like GoToSocial `/main-key`) and embedded `publicKey` objects (like Mastodon `#main-key`).
  - Added support for Authorized Fetch (HTTP Signatures on GET) when resolving remote follower profiles to obtain their personal `inbox` and `sharedInbox`.
  - Addressed `Accept(Follow)` activity directly with `to: [follower_id]` and delivered to the follower's inbox.
  - Supported SHA-512 in HTTP signature verification alongside SHA-256.

## 2.12.2

### Web Preview & Fediverse UI
- **Fediverse Handle Tag with 1-Click Copy in Web Preview Header**:
  - Replaced duplicate `📡 RSS Feed` link in the top-right header with an interactive Fediverse channel tag (`@<token>@<domain>`, e.g., `@twniAE9eNajd@dc.gluek.info`).
  - Clicking the tag copies the handle to clipboard and provides immediate visual feedback (`✓ Copied!`), allowing users to easily paste the handle into their Mastodon or Fediverse search bar to follow the channel.
  - The dedicated `📡 RSS Feed` action button remains in the main channel action row.

## 2.12.1

### Bug Fixes
- **Python 3.11 Module-Level Type Annotation Fix**:
  - Added `from __future__ import annotations` to `activitypub.py`.
  - Removed evaluated string-union annotations on private module globals (`_http_session`, `_delivery_queue`, `_web_loop`) to resolve `TypeError: unsupported operand type(s) for |: 'str' and 'NoneType'` when starting the bot in Docker (Python 3.11).

## 2.12.0

### Fediverse / ActivityPub Federation
- **Full Fediverse Channel Federation (`@<token>@<domain>`)**:
  - Every cataloged Delta Chat channel functions as an autonomous Fediverse actor of type `Service` (displaying the 🤖 Bot badge on Mastodon and compatible platforms).
  - Users on Mastodon, Pleroma, Misskey, Friendica, and other Fediverse instances can discover channels using standard WebFinger queries (`RFC 7033`) via `GET /.well-known/webfinger?resource=acct:<token>@<domain>`.
  - Channel preview URLs (`/c/{token}`) implement standard Content Negotiation: requests with `Accept: application/activity+json` or `application/ld+json` return the full ActivityStreams 2.0 Actor representation with public key, avatar icon, inbox, outbox, and followers collection endpoints.
- **Cryptographic HTTP Signatures (`draft-cavage-http-signatures`)**:
  - Independent RSA-2048 keypairs generated per channel actor and persisted in the SQLite database (`ap_actor_keys`).
  - Strict verification of incoming `Signature`, `Digest` (SHA-256), and `Date` (±300s window) headers on Actor inboxes to guard against replay and spoofing attacks.
  - Automatic outgoing request signing for deliveries and `Accept(Follow)` notifications.
- **Federated Follower Management & Outbox**:
  - `POST /c/{token}/inbox` handles `Follow` activities by recording the follower in `ap_followers` and asynchronously returning a cryptographically signed `Accept` activity to the follower's inbox.
  - Handles `Undo(Follow)` and `Delete(Actor)` events to keep follower rosters clean and GDPR-compliant.
  - `GET /c/{token}/outbox` serves an `OrderedCollection` of recent notes; `GET /c/{token}/followers` reports total follower count.
  - `GET /c/{token}/posts/{msg_id}` returns individual Note objects.
- **Asynchronous Background Delivery Pipeline**:
  - New channel posts ingested via `_ingest_channel_post` are automatically queued and broadcast as `Create(Note)` activities to remote follower inboxes with deduplicated `sharedInbox` delivery.
  - Rich text formatting with autolinked URLs and media enclosures (WebP images, MP4 videos, audio, and documents).
- **GoToSocial-Modeled `robots.txt` & NodeInfo 2.0**:
  - Replaced simple disallow-all `robots.txt` with a comprehensive, GoToSocial-modeled configuration blocking abusive AI scrapers and SEO crawlers while permitting channel previews (`/c/`) and media (`/media/`).
  - Added NodeInfo 2.0 discovery (`/.well-known/nodeinfo` and `/nodeinfo/2.0`) for discovery by Fediverse crawlers and directory indexers.

## 2.11.6

### Channel Catalog & Privacy
- **Unlisted Channels by Default (`/dchanneladd`)**:
  - Channels added via `/dchanneladd <URL>` are now initialized in **unlisted** mode by default (`is_public = 0`).
  - Unlisted channels retain their own unique web preview page (`/c/{token}`) and standard RSS feed (`/c/{token}/rss.xml`), and the bot ingests new messages and attachments continuously.
  - Excluded from public directory listings: unlisted channels are hidden from the bot's web landing page (`/` and `/c/`) and the public `/dchannels` command in group chats and for non-admin users.
- **Dynamic Catalog Visibility Toggles (`/dchannelpub<ID>on` & `/dchannelpub<ID>off`)**:
  - Added administrative commands to toggle channels between public and unlisted at any time.
  - Toggling public status automatically updates the catalog and invalidates web preview and landing page caches immediately.
  - `/dchanneladd` confirmation message now directly provides the preview link, RSS link, and suggests `/dchannelpub<ID>on` if the administrator wishes to make the channel publicly discoverable.
- **Admin Direct Message Catalog Visibility**:
  - When the bot administrator queries `/dchannels` in a private 1-on-1 direct message, all registered channels are shown, with unlisted channels clearly marked with `🔒 [Unlisted]` and quick-action `/dchannelpub<ID>on` command links.
  - In group chats or when queried by non-admin members, only public channels are displayed to prevent leakage.
  - Direct queries via `/dchannel<ID>` for unlisted channels are restricted to bot administrators, preventing numeric ID enumeration by regular users.

## 2.11.5

### Web Preview & Landing Redesign
- **Authentic Delta Chat Styling & System Typography**:
  - Replaced generic AI-generated neon gradients and external Google Fonts (`Outfit`) with clean, privacy-respecting native system typography (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif`) inspired by [gluek.info](https://gluek.info).
  - Integrated official Delta Chat dark wallpaper pattern with doodle envelopes, speech bubbles, and symbols on `#19232b`, served with immutable caching via `/background.jpg` and `/static/background.jpg`.
  - Formatted channel posts into authentic Delta Chat messenger message bubbles (`#232d36`, rounded 12px) with sender names highlighted in Delta Chat blue (`#53bdeb`), quotes styled with vertical accent bars, monospace code blocks, and bottom-right timestamps with checkmarks (`✓`).
  - Unified aesthetics across the channel catalog landing page, channel preview view, tombstone, and 404 pages with zero third-party font tracking.

## 2.11.4

### Channel Catalog Automation
- **Automatic Channel Removal on Bot Ejection**:
  - Automatically detects when the bot is removed from a channel by the channel owner/admin (via `SystemMessageType.MEMBER_REMOVED_FROM_GROUP`, self contact ID `1`, or system removal messages).
  - Soft-deletes the channel from the public catalog (`/dchannels`, `/c/`), invalidates preview and RSS caches immediately, and serves a graceful tombstone message on preview URLs without attempting to re-join.
  - Automatically keeps catalog channel member counts synchronized on member join/leave events.

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
