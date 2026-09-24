# Changelog

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
