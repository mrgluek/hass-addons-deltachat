# Changelog

## 1.9.1

- **Time Range From the Link Is Kept in the Menu**: For a link with a time range (e.g. `?t=34-41`) on a video shorter than 10 minutes, the menu showed the right duration but offered `/yt_ID` and `/ytm_ID` for the whole video. The video, audio and Navidrome commands now carry the range (`/yt_ID_34_41`), and the header shows it. For longer videos the end time is no longer replaced by "start + 10 minutes"; ranges over 10 minutes are offered as video in 10-minute chunks.

## 1.9.0

- **Fixed Lower-Resolution Retry for Tracks and Chunks**: When a video section (`/yt_ID_start_end`) came out over 50 MB, the bot retried at 240p and 144p, but the format selector always picked YouTube's 360p MP4 (format 18) first, so every retry downloaded the same file and failed with "even at lower resolutions". Format 18 is now only preferred at 360p and above; the 240p/144p retries pick a stream of that height.
- **Long Chapters Offered in Parts for Video**: Chapters longer than 10 minutes are offered as video in equal parts of at most 10 minutes (e.g. a 13:27 track becomes two ~6:44 parts). The link menu shows `Track N part 1/2`, each delivered part names itself in the caption, and `▶️ Next part` / `▶️ Next track` links lead through all parts and tracks. Audio (`/ytm`) still downloads the whole chapter, since Opus is small.
- **Size-Limit Error Offers Halves**: If a video section still exceeds 50 MB at the lowest resolution, the error now links its two halves and the audio of the same section instead of the whole video's audio.

## 1.8.1

- **MIT License**: the project is now licensed under MIT (`LICENSE`).

## 1.8.0

- **`/transports` Shows the Relay Actually Used for Sending**: Since core 2.61 the core sends through the relay that last worked and switches only when it cannot connect, so the main address (`configured_addr`) says nothing about where mail goes out. `/transports` now lists relays in the order the core tries them, with the current sending relay first, shows the core's send queue (waiting messages and retries) and outgoing status, and per relay the incoming status, when the last message arrived, mailbox storage usage (⚠️ from 80%) and when it was added. The sending order and queue are read from the core's account database (read-only); the report is built by the shared `transports_view.py`.
- **Removed Misleading Per-Relay Sent/Received Counters**: They credited every message to `configured_addr` (or, in some places, the wrong address), so the numbers and "last sent" dates were wrong once the core sent through another relay. Counting them also cost extra RPC calls per message. The `transport_stats` table is left in place but no longer updated.

## 1.7.0

### Removed
- **Bot-Side Relay Failover**: Removed the `MSG_FAILED` failover handler and the resilient-send `send_msg` patch. Both switched `configured_addr` and called `resend_messages`, but since Delta Chat core 2.61 the SMTP relay is no longer chosen by `configured_addr`: the core tries the newest relay first and falls back to the next one if a relay is unreachable. The old logic could no longer switch relays and only caused delayed duplicate resends.

### Changed
- **`/setprimary` and `/resilient` Deprecated**: Both commands are disabled and only reply with an explanation of how the core picks relays now. They are removed from `/help` and the README.
- **`/transports` Sending Order**: Relays are listed newest first, in the order the core tries them for sending, instead of marking `configured_addr` as "Used for sending".
- **Core Requirement**: `requirements.txt` now requires `deltachat-rpc-server>=2.62.0`.

## 1.6.61

### Fixed
- **`update.sh` Deployed the Wrong Branch**: Branch detection took the first remote branch in alphabetical order, so a leftover PR branch such as `origin/claude/...` sorted before `origin/master` and was deployed instead (and new `master` commits were reported as "Already up to date"). It now follows the checked-out branch, falling back to `main`/`master`.

## 1.6.60

### Changed
- **Private `/help` in Groups**: A plain `/help` sent in a group chat is now answered in a private 1:1 chat with the sender instead of the group, so several bots don't flood it with help texts (the reply ends with a note on how to show it in the group). Addressed `/help@yt` is still answered in the group. Previously a plain `/help` was answered in the group, or silently ignored when other bots were present.

## 1.6.59

### Security
- **SSRF & DNS Rebinding Hardening**: Added `is_safe_url()` with DNS resolution and private IP checks. Tightened PeerTube URL pattern to require valid domain with TLD. Added URL safety checks in `_handle_link_info`, `_do_download`, and `_download_thumbnail` (with 5MB read limit).
- **Dependency Pinning**: Pinned dependencies to secure ranges in `requirements.txt`.

## 1.6.58

### Fixed
- **Float Duration Formatting & Next Chunk Offer Bug**:
  - Safely handle floating-point durations and time parameters in `_format_duration`, `_format_time_range`, and `_parse_single_time_str`, resolving `ValueError: Unknown format code 'd' for object of type 'float'`.
  - Normalize extracted `duration` from yt-dlp metadata to integer across download and cache handlers.
  - Require range parameters (`start_time` or `end_time`) before offering sequential video chunks in `_send_from_cache`, preventing spurious "Next chunk" buttons and duration formatting crashes on whole non-sliced video downloads (e.g. Twitter/X or other hosts with fractional second durations).

## 1.6.57

### Fixed
- **Cache Cleaner NameError**:
  - Define `CACHE_MAX_SIZE` (with `MAX_CACHE_SIZE` backward compatibility alias) matching references in `_cache_cleaner_loop`, resolving runtime `NameError: name 'CACHE_MAX_SIZE' is not defined`.
  - Extract `_clean_cache_once()` helper for deterministic cache pruning execution and isolated testing.
  - Add dedicated test suite `tests/test_cache.py` covering cache expiration, size limit enforcement, thumbnail cleanup, and database retention integration.

## 1.6.56

### Security
- **Private Chat Enforcement**:
  - Restrict `/addtransport` to 1:1 private chats with the bot to prevent leaking mail passwords and chatmail tokens in group chats.
  - Restrict `/initadmin` to 1:1 private chats to prevent ownership claims in group chats.
- **Error Sanitization**:
  - Mask raw exception messages in user replies for `/transports`, `/addtransport`, `/setprimary`, `/resilient`, and `/rmtransport` to prevent leaking internal error details or paths.

### Fixed
- **Resilient Mode & Message Failover Concurrency**:
  - Wrap initial message dispatch and `configured_addr` lookup under `resilient_lock` to avoid transport misconfiguration during concurrent background resends.
  - Wrap sequential resending in `try...finally` to guarantee restoration of the primary transport address upon errors.
  - Fix message failover restoration running inside `with resilient_lock:`.
  - Protect `_message_failover_attempts` with `_message_failover_lock` and enforce FIFO bounding.

### Performance & Database
- **SQLite WAL & Busy Timeout**:
  - Enabled SQLite WAL mode (`PRAGMA journal_mode = WAL`), `synchronous = NORMAL`, `cache_size = -4000`, and `busy_timeout = 5000` for high concurrency without database lock contention.
  - Added indexes on `url_map(created_at)` and `info_cache(created_at)`.
- **Buffered Transport Statistics**:
  - Implemented thread-safe in-memory buffer `_transport_stats_buffer` with 30-second periodic flush, eliminating synchronous SQLite writes on every message.
- **True FIFO Bounded Message Deduplication & Rate Limiting**:
  - Refactored `_processed_msg_ids` to `collections.OrderedDict` (capped at 1000) for deterministic O(1) FIFO eviction.
  - Added thread-safe `_user_rate_limits_lock` with automated pruning of stale rate limit entries.
- **Automated Record Retention Cleanup**:
  - Added `cleanup_old_records(retention_days=30)` in `database.py` integrated into `_cache_cleaner_loop`.

### Tests
- Added `tests/test_database.py` and `tests/test_transport_commands.py` adhering to `AGENTS.md`.

## 1.6.55

### Added
- **Configurable Display Name & Status Text**:
  - `on_init` now checks `DISPLAY_NAME` and `STATUS_TEXT` environment variables with `/data/options.json` fallback instead of overwriting display name with static strings.

## 1.6.54
- Initial Home Assistant Add-on release.
- Audio and music downloads, track slicing, chunked delivery, and Navidrome integration.
- Automatic direct download for Instagram Reels.
