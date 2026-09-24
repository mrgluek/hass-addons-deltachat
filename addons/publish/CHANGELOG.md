# Changelog

## 1.0.5

### Fixed
- **`update.sh` Deployed the Wrong Branch**: Branch detection took the first remote branch in alphabetical order, so a leftover PR branch such as `origin/claude/...` sorted before `origin/master` and was deployed instead (and new `master` commits were reported as "Already up to date"). It now follows the checked-out branch, falling back to `main`/`master`.

## 1.0.4

### Security
- **SSRF Protection in Forgejo Client**: Added URL validation (`is_safe_url`) in `ForgejoClient.commit_files` and `ForgejoClient.check_connection` with DNS resolution to block loopback, private, link-local, multicast, and cloud metadata IP ranges (`169.254.169.254`, `127.0.0.0/8`, etc.), plus `.local`, `.internal`, and `.lan` domains.
- **Bounded Response Reads**: Enforced read byte limits on Forgejo API responses (10 MB for commits, 64 KB for errors and connectivity checks) to prevent memory exhaustion.
- **Dependency Pinning**: Pinned dependencies to secure version bounds in `requirements.txt` (`deltabot-cli>=8.1.2,<9.0.0`, `aiohttp>=3.10.11,<4.0.0`, `qrcode>=7.4.2,<8.0.0`).

## 1.0.3

### Added
- **Private Chat Enforcement**: Enforce private 1:1 chat for `/addtransport` and `/initadmin` to prevent credential exposure in group chats.
- **Resilient Transport Sending**: Integrated `_setup_resilient_mode` with concurrency lock and automatic fallback transport resending.
- **Automated Retention & Pruning**: Periodic background cleanup task in `on_start` for database records and transport statistics.
- **Transport Command Unit Tests**: Added `tests/test_transport_commands.py` covering private chat constraints, resilient mode toggle, and error sanitization.

### Fixed
- **Transport Command Error Sanitization**: Sanitized error output in `/transports`, `/addtransport`, `/rmtransport`, `/setprimary`, and `/resilient`.

### Changed
- **SQLite Performance Optimization**: Enabled WAL mode (`journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=5000`) and in-memory buffered transport statistics.

## 1.0.2

### Added
- **Options.json Fallback for Display Name & Status Text**:
  - `on_init` now checks `/data/options.json` fallback when `DISPLAY_NAME` or `STATUS_TEXT` are not set in environment variables.

## 1.0.1
- Initial Home Assistant Add-on release of `deltachat_publish`.
- Publishes blog posts and attached images to Astro blogs via Forgejo / Gitea REST API.
- Single-commit multi-file API publishing with automatic slugification.
