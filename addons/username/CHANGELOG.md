# Changelog

## 1.8.2

### Added
- **Options.json Fallback for Display Name & Status Text**:
  - `configure_bot_profile` now checks `/data/options.json` fallback when `DISPLAY_NAME` or `STATUS_TEXT` are not set in environment variables.

---

## 1.8.1
- Initial Home Assistant Add-on release.
- Registers custom usernames and short invite redirect links (`deltachat.id`).
- Web interface with Home Assistant Ingress integration on port 8084.
