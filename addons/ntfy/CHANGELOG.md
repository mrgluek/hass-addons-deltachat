# Changelog

## 1.3.2

- **Shorter `/newgroup` Reply**: dropped the "Share this link or scan the QR code…" line; the reply is now just the confirmation and the join link.
- **MIT License**: the project is now licensed under MIT (`LICENSE`).

## 1.3.1

- **Fixed HTTP 500 on Non-UTF-8 Notifications**: Posts whose body was not valid UTF-8 (e.g. Windows PowerShell 5.1 `Invoke-RestMethod` without a charset, which sends Windows-1251) crashed `request.text()` with `UnicodeDecodeError`, so the notification was lost. The body is now read as bytes and decoded with the `Content-Type` charset if given, else UTF-8, else Windows-1251, else UTF-8 with replacement characters, so a notification is never rejected because of its encoding. JSON bodies are decoded the same way, and Topic/Title/Tags/Filename headers with non-UTF-8 bytes are re-decoded too.

## 1.3.0

- **`/transports` Shows the Relay Actually Used for Sending**: Since core 2.61 the core sends through the relay that last worked and switches only when it cannot connect, so the main address (`configured_addr`) says nothing about where mail goes out. `/transports` now lists relays in the order the core tries them, with the current sending relay first, shows the core's send queue (waiting messages and retries) and outgoing status, and per relay the incoming status, when the last message arrived, mailbox storage usage (⚠️ from 80%) and when it was added. The sending order and queue are read from the core's account database (read-only); the report is built by the shared `transports_view.py`.
- **Removed Misleading Per-Relay Sent/Received Counters**: They credited every message to `configured_addr` (or, in some places, the wrong address), so the numbers and "last sent" dates were wrong once the core sent through another relay. Counting them also cost extra RPC calls per message. The `transport_stats` table is left in place but no longer updated.
- **Clearer Log Line**: "Successfully sent msg_id …" is now "Queued msg_id … for sending": at that point the message is only handed to the core's send queue.

## 1.2.0

### Removed
- **Bot-Side Relay Failover**: Removed the `MSG_FAILED` failover handler and the resilient-send `send_msg` patch. Both switched `configured_addr` and called `resend_messages`, but since Delta Chat core 2.61 the SMTP relay is no longer chosen by `configured_addr`: the core tries the newest relay first and falls back to the next one if a relay is unreachable. The old logic could no longer switch relays and only caused delayed duplicate resends.

### Changed
- **`/setprimary` and `/resilient` Deprecated**: Both commands are disabled and only reply with an explanation of how the core picks relays now. They are removed from `/help` and the README.
- **`/transports` Sending Order**: Relays are listed newest first, in the order the core tries them for sending, instead of marking `configured_addr` as "Used for sending".
- **Core Requirement**: `requirements.txt` now requires `deltachat-rpc-server>=2.62.0`.

## 1.1.5

### Fixed
- **`update.sh` Deployed the Wrong Branch**: Branch detection took the first remote branch in alphabetical order, so a leftover PR branch such as `origin/claude/...` sorted before `origin/master` and was deployed instead (and new `master` commits were reported as "Already up to date"). It now follows the checked-out branch, falling back to `main`/`master`.

## 1.1.4

### Changed
- **Private `/help` in Groups**: A plain `/help` sent in a group chat is now answered in a private 1:1 chat with the sender instead of the group, so several bots don't flood it with help texts (the reply ends with a note on how to show it in the group). Addressed `/help@ntfy` is still answered in the group. Previously a plain `/help` was answered in the group, or silently ignored when other bots were present.

## 1.1.3

### Security
- **SSRF Defense**: Added rigorous IP and DNS validation via `is_safe_url()` before fetching external attachments to block loopback, private, link-local, cloud metadata, and DNS rebinding.
- **Unbounded Attachment & Body Protection**: Enforced `client_max_size = 15MB` on web server and capped streaming attachment downloads to 15MB.
- **Rate Limiting**: Added thread-safe sliding-window rate limiting on all public web endpoints with HTTP 429 `Retry-After: 60`.
- **Dependency Hardening**: Pinned `aiohttp>=3.10.5,<4.0.0`, `qrcode>=7.4.2,<8.0.0`, and `emoji>=2.12.0,<3.0.0`.

## 1.1.2

### Added
- **Private Chat Enforcement**: Enforce private 1:1 chat for `/addtransport` and `/initadmin` to prevent credential exposure in group chats.
- **Bot Ownership Claiming (`/initadmin`)**: Added `/initadmin` command handler to allow the bot owner to claim admin ownership in private chat with cryptographic fingerprint binding.
- **Automated Data Retention & Pruning**: Periodic background cleanup task pruning notification history and flushing transport stats.
- **Comprehensive Unit Test Suite**: Added `tests/test_database.py` and `tests/test_transport_commands.py` with mock fallbacks for headless CI/offline environments.

### Fixed
- **Resilient Send Concurrency**: Protected initial transport send with `resilient_lock` and guaranteed `try...finally` restoration of `configured_addr` in background resend workers.
- **Transport Command Error Sanitization**: Sanitized error output in `/transports`, `/addtransport`, `/rmtransport`, `/setprimary`, and `/resilient`.

### Changed
- **SQLite Performance Optimization**: Enabled WAL mode (`journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=5000`) and in-memory buffered transport statistics.

## 1.1.1

### Added
- **Configurable Display Name & Status Text**:
  - `on_init` now checks `DISPLAY_NAME` and `STATUS_TEXT` environment variables with `/data/options.json` fallback instead of overwriting display name with static strings.

## 1.1.0
- Initial Home Assistant Add-on release.
- Emulates ntfy.sh backend to receive HTTP webhooks and relay to Delta Chat topics.
- Web dashboard with Home Assistant Ingress integration on port 8082.
