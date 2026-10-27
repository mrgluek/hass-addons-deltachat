# Changelog

## 1.16.0

### Added
- **Relay sync (`r=`)**: personal invite links now carry the owner's full relay list. The bot reads it from the contact's key (`get_contact_encryption_info`, "Relays:"), keeps `a=` on the current address when it is still listed (else the first relay) and puts the other relays (up to 5 in all, as the core reads) into `r=`.
- **Hourly contact sync**: relay changes arrive as core keyupdate messages (core 2.60+), which the core trashes without a message event, so the bot now also re-checks every personal link once an hour (new `contact_sync.py`, first run 2 minutes after start). It only reads the core's local data, no network requests.

### Fixed
- **Links are only synced with their own key**: the sync now compares the contact's fingerprint with the link's. A link registered for another profile or another person is no longer rewritten with the sender's address and name.
- **Address sync never worked**: the old code read `contact.addr`, but the RPC contact field is `address`, so only the name was ever updated.
- **`n=` no longer becomes an address**: the name is taken from the name the contact set (`auth_name`), not from `display_name`, which falls back to the address.
- **`r=` kept intact**: rewriting a link whose `r=` lists several relays encoded the separating commas as `%2C`. The core splits `r=` on raw commas, so the result was one invalid address. Each address is now encoded on its own.

## 1.15.1

### Security
- **HTML/SVG escaping on the web pages**: the profile page (`/<name>`), the `/card` page, the 404 page and the `/og.svg` card inserted names, e-mail, the invite link and the requested path into the page without escaping. A group name like `"><script>…` registered with `/link`, or a crafted URL such as `/<img src=x onerror=…>` on the 404 page, ran script on the site's domain. All such values are now HTML-escaped (XML-escaped in the SVG), and the redirect script gets the invite link as a JSON string literal. A name with `&` no longer breaks the SVG/PNG card either.

### Changed
- **"Open in ArcaneChat" opens the app directly**: for ArcaneChat admin-group links, the button on the profile page and on `/card` now uses an `openpgp4fpr:FINGERPRINT#v=3&…&z=…` URI instead of `https://i.delta.chat/#…`, so the installed ArcaneChat app opens the invite without the i.delta.chat page in between (which offers Delta Chat, which can't join these groups). The `/card` QR code keeps the `https` link, which ArcaneChat scans fine.

## 1.15.0

### Added
- **ArcaneChat Admin Groups**: Invite links with the `z=` group-name parameter (ArcaneChat admin groups) are recognised as groups and flagged `arcanechat_only`. The chat card, the `/link` reply, the OpenGraph description and the SVG/PNG cards say "ArcaneChat only"; the web page no longer auto-redirects such links, shows a notice with a link to https://arcanechat.me and an "Open in ArcaneChat" button; `GET /api/username/<name>` has a new additive `arcanechat_only` field (`type` stays `group`).

### Fixed
- ArcaneChat admin-group links were classified as `contact` (shown as the inviter's email). Because of that, `update_invite_link_contact_info` could rewrite their `a=`/`n=` with the sender's address and name; links with `z=` are now never modified.

## 1.14.1

### Changed
- **Download Limit 64 KB**: Photos, videos and files over 64 KB sent to the bot are no longer downloaded automatically (the bot only reads commands), saving traffic and disk space. Plain text and small attachments arrive as before.

## 1.14.0

### Added
- **Automatic Account Creation**: `serve` without a configured account no longer exits with "There are no configured accounts to serve". The bot asks the core (`init_transports`, core 2.62+) to create an account on the fastest chatmail relay of its built-in list; the core adds further relays in the background. If that fails, the error is logged, `serve` exits and the container restart retries. `bot.py init <addr> <password>` and `bot.py init DCACCOUNT:server.tld` still choose the account explicitly.

### Changed
- **The server runs releases, not the tip of `main`.** `update.sh` deploys the newest `vX.Y.Z` tag, so a merge into `main` reaches the server only once it is released; several PRs can go out together. `UPDATE_REF` in `.env.local` pins a release (`UPDATE_REF=v1.13.0` - a rollback; empty again = newest) or follows a branch as before (`UPDATE_REF=main`). A release tag moved on GitHub or Forgejo makes the update fail instead of deploying the changed code. Errors that stopped the script with a message (both remotes unreachable, an unknown `UPDATE_REF`) now also ping the healthcheck's `/fail`, not only failed commands. The script now runs as one function, so the `git reset` that rewrites `update.sh` cannot confuse the running copy.
- **Releases are published by a tag** (new `.github/workflows/release.yml`): pushing `vX.Y.Z` checks that `commands.py` has that version, creates the GitHub release with the version's section of this file as its notes (an existing release is left alone), then sends the ntfy notification and the `bot-updated` dispatch to `hass-addons-deltachat` (now with `"version"` in the payload). Both used to go out on every push to `main` (`username-changelog.yml`, removed), so Home Assistant users got unreleased code.
- **README**: the "Configure Email and Admin" deployment step is optional now; new "Updates" section on `update.sh`, `UPDATE_REF` and releasing.
- Releasing: merge, then `git tag -a vX.Y.Z -m "..." <commit> && git push origin vX.Y.Z`.
- **Upgrading:** tag `v1.14.0` right after merging this. Until then the new `update.sh` would deploy `v1.13.0`, which still has the old script that follows `main` - and the server would switch back and forth on every run.

## 1.13.0

### Added
- **MIT License**: the project is now licensed under MIT (`LICENSE`).
- **Invite Link in the Lookup API**: `GET /api/username/<name>` now also returns `invite_link`, the invite on `i.delta.chat` (the same link `/username` sends as the card caption; mirror domains such as `i.deltachat.id` are turned into `i.delta.chat`). Delta Chat apps open it directly, while the short link `url` goes through the browser first. Like `/username` and the profile page, it contains the address and fingerprint the user published.

## 1.12.0

### Added
- **Lookup API for Bots (`GET /api/username/<name>`)**: JSON with the username, its type (`contact`, `group` or `channel`), display name and short link (`https://deltachat.id/<name>`); 404 `{"error": "not_found"}` for a name nobody claimed. Bouncer Bot uses it for `@mentions` of people who are not in a group. Unlike the profile page it returns no email address or fingerprint. Requests count against the same limit as profile pages (10 per minute per IP, 429 `{"error": "rate_limited"}`). Other bots cannot use `/username` for this: deltabot-cli ignores messages from bots, and the answer would arrive asynchronously.

## 1.11.0

- **`/transports` Shows the Relay Actually Used for Sending**: Since core 2.61 the core sends through the relay that last worked and switches only when it cannot connect, so the main address (`configured_addr`) says nothing about where mail goes out. `/transports` now lists relays in the order the core tries them, with the current sending relay first, shows the core's send queue (waiting messages and retries) and outgoing status, and per relay the incoming status, when the last message arrived, mailbox storage usage (⚠️ from 80%) and when it was added. The sending order and queue are read from the core's account database (read-only); the report is built by the shared `transports_view.py`.
- **Removed Misleading Per-Relay Sent/Received Counters**: They credited every message to `configured_addr` (or, in some places, the wrong address), so the numbers and "last sent" dates were wrong once the core sent through another relay. Counting them also cost extra RPC calls per message. The `transport_stats` table is left in place but no longer updated.

## 1.10.0

### Removed
- **Bot-Side Relay Failover**: Removed the `MSG_FAILED` failover handler and the resilient-send `send_msg` patch. Both switched `configured_addr` and called `resend_messages`, but since Delta Chat core 2.61 the SMTP relay is no longer chosen by `configured_addr`: the core tries the newest relay first and falls back to the next one if a relay is unreachable. The old logic could no longer switch relays and only caused delayed duplicate resends.

### Changed
- **`/setprimary` and `/resilient` Deprecated**: Both commands are disabled and only reply with an explanation of how the core picks relays now. They are removed from `/help` and the README.
- **`/transports` Sending Order**: Relays are listed newest first, in the order the core tries them for sending, instead of marking `configured_addr` as "Used for sending".
- **Core Requirement**: `requirements.txt` now requires `deltachat-rpc-server>=2.62.0`.

## 1.9.0

### Added
- **Target-Specific Commands in Group Chats**: Commands can be addressed to this bot with a suffix (`/help@username`, `/stats@user`, …); commands addressed to another bot (`/help@yt`) are ignored. Un-suffixed `/stats` is ignored in groups with several bots.

### Changed
- **Private `/help` in Groups**: A plain `/help` sent in a group chat is now answered in a private 1:1 chat with the sender instead of the group, so several bots don't flood it with help texts (the reply ends with a note on how to show it in the group). Addressed `/help@username` is still answered in the group.

## 1.8.6

### Fixed
- **`update.sh` Deployed the Wrong Branch**: Branch detection took the first remote branch in alphabetical order, so a leftover PR branch such as `origin/claude/...` sorted before `origin/master` and was deployed instead (and new `master` commits were reported as "Already up to date"). It now follows the checked-out branch, falling back to `main`/`master`.

## 1.8.4

### Security
- **Web Endpoint Rate Limiting**: Added sliding-window per-IP rate limiting to root homepage (`GET /`) and username card view (`GET /{username}/card`) with HTTP 429 `Retry-After: 60` response headers.
- **Dependency Pinning**: Pinned dependencies to secure ranges in `requirements.txt`.

## 1.8.3

### Security & Hardening
- **Private Chat Enforcement**: Enforced `_is_private_chat` on sensitive commands `/initadmin` and `/addtransport`, preventing credentials or admin claiming from leaking inside group chats.
- **Error Sanitization**: Sanitized user-facing error messages in transport administration commands (`/addtransport`, `/rmtransport`, `/setprimary`, `/transports`, `/resilient`), logging detailed diagnostics to server logs while replying with safe generic notices.
- **Resilient Sending Mode**: Added `_setup_resilient_mode(bot)` and `resilient_lock = threading.Lock()` with automatic failover transport resending and temporary primary address fallback restoration under `try...finally`.
- **Automatic Message Failover**: Added `on_msg_failed` handler with exponential backoff resend across configured mail relays.

### Performance & Concurrency
- **SQLite WAL & Concurrency**: Enabled WAL journal mode (`PRAGMA journal_mode = WAL`), `synchronous = NORMAL`, and `busy_timeout = 5000` via `get_connection()`.
- **Resource Cleanup**: Ensured all database connections strictly adhere to `try...finally: conn.close()`, resolving database connection leaks.
- **Buffered Transport Statistics**: Implemented in-memory write buffer (`_transport_stats_buffer` with `_transport_stats_lock`) and periodic background flushing (`flush_transport_stats`), slashing disk I/O under high traffic.
- **Automated Retention Worker**: Added background daemon worker in `on_start` running periodic stats flushing and expired pending claim cleanups (`cleanup_old_records`).
- **Comprehensive Test Suite**: Added `tests/test_database.py` and `tests/test_transport_commands.py` with 100% pass rate.

---

## 1.8.2

### Added
- **Options.json Fallback for Display Name & Status Text**:
  - `configure_bot_profile` now checks `/data/options.json` fallback when `DISPLAY_NAME` or `STATUS_TEXT` are not set in environment variables.

---

## 1.8.1
- Initial Home Assistant Add-on release.
- Registers custom usernames and short invite redirect links (`deltachat.id`).
- Web interface with Home Assistant Ingress integration on port 8084.
