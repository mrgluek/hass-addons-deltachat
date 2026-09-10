# Changelog

## 2.9.2

### Performance & Database Architecture
- **Persistent Writer Connection**:
  - Replaced ad-hoc connection creation on every write with a dedicated persistent writer connection protected by `_write_lock` and standard transactional context manager (`_writer_transaction()`), eliminating connection teardown churn and disk sync overhead.
- **Strict `PRAGMA synchronous = NORMAL` & `busy_timeout`**:
  - Enforced `PRAGMA synchronous = NORMAL;`, `PRAGMA journal_mode = WAL;`, and `PRAGMA busy_timeout = 5000;` on all database connections across the entire codebase.
- **Concurrent Non-Blocking WAL Reads**:
  - Replaced global `_lock` on read operations with independent read connections, allowing concurrent readers to execute simultaneously alongside writer without lock contention.
- **Batch Contact Seeding**:
  - Replaced N+1 individual insert queries in catalog member count refresh (`_refresh_catalog_member_counts`) with `ensure_contacts_first_seen_batch()`, recording contacts in a single atomic transaction.

## 2.9.1

### Security Hardening & Concurrency Fixes
- **Fix Undefined `resilient_lock`**:
  - Declared `resilient_lock` globally, fixing runtime `NameError` crash during resilient sending and message failover.
  - Synchronized transport switching and message sending during resilient delivery.
- **Server Domain Input Validation (`/cmping`)**:
  - Added strict regex domain validation (`DOMAIN_REGEX`) to `/cmping`, `/cmpingadd`, and `/cmpingdel` commands to prevent command injection and malformed subprocess parameters.
- **Credential Protection (`/addtransport`)**:
  - Enforced that `/addtransport` can only be executed in private 1-on-1 chats with the bot, preventing accidental password leakage in group chats.
- **Rate Limiting (`/slap`)**:
  - Added 15-second cooldown per chat for `/slap` commands.
- **Sanitized User Error Messages**:
  - Removed internal exception and traceback disclosures from user-facing error messages in `/kick`, `/invite`, `/relays`, `/approve`, `/decline`, and `/addtransport`.
- **Bounded Message Deduplication**:
  - Replaced full set clearing with an `OrderedDict` maintaining up to 2000 recent message IDs with FIFO eviction, preventing duplicate command execution.

### High-Load & Database Optimizations
- **SQLite WAL & Concurrency PRAGMAs**:
  - Enabled `PRAGMA journal_mode = WAL`, `PRAGMA synchronous = NORMAL`, `cache_size = -4000`, and `busy_timeout = 5000` for high concurrency and performance under load.
- **Buffered Transport Statistics**:
  - Buffered sent/received message statistics in memory, flushed to SQLite in a single transaction every 30 seconds instead of executing database writes on every individual message.
- **Database Indexes**:
  - Added indexes on `autokick_warnings(chat_id)`, `pending_requests(chat_id, approved)`, `away_notifications(away_updated_at)`, and `cmping_history(checked_at)`.
- **Automated Data Pruning**:
  - Added periodic pruning in background monitor loop for `away_notifications` and `cmping_history` older than 30 days.
  - Added periodic in-memory cleanup of stale anti-spam timestamps and unused domain locks.

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
