# Changelog

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
