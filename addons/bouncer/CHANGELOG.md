# Changelog

## 2.9.0

### Added
- **Two-Stage Inactivity Warning System for `/autokick`:**
  - Inactive members now receive a direct 1-on-1 private notification from the bot before being kicked, warning them of impending removal and inviting them to stay by posting in the group.
  - The group chat receives a daily summary broadcast (at most once every 24 hours) listing all members in the warning zone with days remaining until removal.
  - **Kick Protection:** Members are now strictly kicked only after receiving a warning and passing a minimum 24-hour grace period.
  - Dynamic warning threshold: warnings begin at `autokick_days - 7` days for thresholds $> 7$ days (i.e. 7 days before kick), and at `autokick_days - 1` days for thresholds $\le 7$ days.
  - Warnings are automatically cleared as soon as a user sends a message in any shared chat.
- **Cryptographic Fingerprint Ignore List (`/autokick ignore`):**
  - Added `/autokick ignore <email/nick/id>` for bot administrators to look up a member, extract their cryptographic key fingerprint, and permanently exempt them (e.g. service bots or quiet system accounts) from auto-kick.
  - Added `/autokick unignore <fingerprint/email/nick>` to remove exemptions.
  - Added `/autokick ignore` / `/autokick ignore list` to display all currently exempted fingerprints and notes.
- **Exemption for `/away` Users:**
  - Members with an active `/away` vacation/absence status are automatically exempt from inactivity warnings and auto-kicks.
- **`/bounce` Integration with `/autokick` Thresholds:**
  - In group chats where `/autokick` is active, `/bounce` now shows members currently in the warning window (< 7 days or < 1 day remaining until auto-kick).
  - In groups where `/autokick` is disabled, `/bounce` continues to report inactivity based on the default 21-day threshold.
- **Grace Period Protection for New Members:**
  - Utilizes `contact_first_seen` tracking so newly joined members who have not yet spoken (`last_seen == 0`) are protected by a grace period based on their join time, preventing premature autokicking.
- **Database Schema Upgrades:**
  - Added `last_autokick_warn_at` column to `chats` table.
  - Added `autokick_warnings` and `autokick_ignored_fingerprints` tables.

## 2.8.2

### Added
- **Options.json Fallback for Display Name & Status Text**:
  - `on_init` now checks `/data/options.json` fallback when `DISPLAY_NAME` or `STATUS_TEXT` are not set in environment variables.

## 2.8.1
- Initial Home Assistant Add-on release.
- Group inactivity monitoring, `/autokick` of stale members, and chat/channel catalogs.
- Mail relay testing and connectivity monitoring via `cmping`.
