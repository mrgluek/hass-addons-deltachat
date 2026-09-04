# Changelog

## 2.9.7
- **Prebuilt Monolith Binary in Docker:**
  - Replaced multi-stage Rust compilation (`cargo install monolith`) with direct download of the official prebuilt `monolith` binary (v2.10.1) for x86_64 and aarch64.
  - Drastically speeds up Docker image builds from several minutes down to seconds and avoids heavy Rust toolchain dependencies.
- Set default `chatmail_qr` server (`dcaccount:https://chat.gluek.info/new`) for zero-configuration startup.

## 2.9.6
- Initial Home Assistant Add-on release.
- Saves web pages as offline HTML (`monolith`), reader mode views, and WebXDC apps.
- Clean Instagram preview formatting and Gemini AI `/tldr` summaries.
