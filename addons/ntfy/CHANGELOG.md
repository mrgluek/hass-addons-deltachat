# Changelog

## 1.5.0

### Added
- **The bot creates its own account.** `serve` without a configured account (a new install) lets the Delta Chat core (2.62+) create one: it probes its built-in chatmail relay list, configures the fastest relay and later adds further relays in the background. The new address is logged. If that fails, the error is logged and the bot exits, so the container restart retries. `bot.py init <addr> <password>` and `bot.py init DCACCOUNT:server.tld` still choose the account explicitly; `bot.py init transport ...` is unchanged. The README's account setup step is now optional.

### Changed
- **The server runs releases, not the tip of `main`.** `update.sh` deploys the newest `vX.Y.Z` tag, so a merge into `main` reaches the server only once it is released; several PRs can go out together. `UPDATE_REF` in `.env.local` pins a release (`UPDATE_REF=v1.4.0` - a rollback; empty again = newest) or follows a branch as before (`UPDATE_REF=main`). A release tag moved on GitHub or Forgejo makes the update fail instead of deploying the changed code. Errors that stopped the script with a message (both remotes unreachable, an unknown `UPDATE_REF`) now also ping the healthcheck's `/fail`, not only failed commands. The script now runs as one function, so the `git reset` that rewrites `update.sh` cannot confuse the running copy.
- **Releases are published by a tag** (new `.github/workflows/release.yml`): pushing `vX.Y.Z` checks that `bot.py` has that version, creates the GitHub release with the version's section of this file as its notes (an existing release is left alone), then sends the ntfy notification and the `bot-updated` dispatch to `hass-addons-deltachat` (now with `"version"` in the payload). Both used to go out on every push to `main` (`ntfy-changelog.yml`, removed), so Home Assistant users got unreleased code.
- Releasing: merge, then `git tag -a vX.Y.Z -m "..." <commit> && git push origin vX.Y.Z`.
- **Upgrading:** tag `v1.5.0` right after merging this. Until then the new `update.sh` would deploy `v1.4.0`, which still has the old script that follows `main` - and the server would switch back and forth on every run.

## 1.4.0

- **Paced sending below the relay's limit**: chatmail relays allow each sender 60 messages a minute with a burst of 10 and answer `450 Too much mail` above it; the core retries, the retries count too, and everything after a burst arrives minutes late. A notification goes to every subscribed chat (up to 5 per topic today), so a publisher posting several at once could get there. All sends - notifications, daily stats, command replies - now go through one queue (`outbox.py`, the same module as in Uptime Bot): 50 a minute with bursts of 5, in one sending thread.
  - **Priorities**: ntfy priority 4-5 notifications first, then command replies, then priority 3 (default), then 1-2 and the daily stats. Within a priority in arrival order, so a topic's notifications keep their order in a chat. Notifications are never dropped or merged.
  - **Attachments**: the temp file of an uploaded or downloaded attachment is deleted after its last queued send (the core copies it when it sends), not right after the HTTP request. A temp file of a notification without subscribers is now deleted too (it was left behind).
  - The HTTP request returns as soon as the notification is queued. A backlog of 20+ messages is logged once a minute with an estimate of how long it takes to send.

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
