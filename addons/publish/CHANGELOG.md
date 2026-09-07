# Changelog

## 1.0.2

### Added
- **Options.json Fallback for Display Name & Status Text**:
  - `on_init` now checks `/data/options.json` fallback when `DISPLAY_NAME` or `STATUS_TEXT` are not set in environment variables.

## 1.0.1
- Initial Home Assistant Add-on release of `deltachat_publish`.
- Publishes blog posts and attached images to Astro blogs via Forgejo / Gitea REST API.
- Single-commit multi-file API publishing with automatic slugification.
