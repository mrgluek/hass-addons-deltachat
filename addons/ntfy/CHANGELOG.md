# Changelog

## 1.1.1

### Added
- **Configurable Display Name & Status Text**:
  - `on_init` now checks `DISPLAY_NAME` and `STATUS_TEXT` environment variables with `/data/options.json` fallback instead of overwriting display name with static strings.

## 1.1.0
- Initial Home Assistant Add-on release.
- Emulates ntfy.sh backend to receive HTTP webhooks and relay to Delta Chat topics.
- Web dashboard with Home Assistant Ingress integration on port 8082.
