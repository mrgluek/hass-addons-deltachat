# Changelog

## 2.7.3
### Added
- **ASCII QR Code in Startup Logs:**
  - Render ASCII QR code directly into stdout on bot startup for easy terminal and container log onboarding.
  - Added line-buffering and explicit flushing for container environments (Docker, Home Assistant Add-on).

### Fixed
- **Relative Web Asset URLs for Ingress:**
  - Changed absolute `/icon.png` and `/favicon.ico` paths to relative (`icon.png`, `favicon.ico`) in both dashboard and index HTML templates so logos and favicons load correctly under Home Assistant Ingress reverse proxy paths.
- Set default `chatmail_qr` server (`dcaccount:https://chat.gluek.info/new`) for zero-configuration startup.

## 2.7.2
- Initial Home Assistant Add-on release.
- Home Assistant Ingress web dashboard integration on port 8081.
- Automatic account provisioning and ASCII QR code invite logging.
- Parallel multi-region cross-checks in `/ping`.
