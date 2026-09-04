# Delta Chat YT Bot (`deltachat_yt`)

`deltachat_yt` is a Delta Chat bot that downloads video, audio tracks, and music via `yt-dlp`. It is designed to stay within email delivery limits (50 MB) and ensure maximum compatibility across platforms.

## Key Features

- **Multi-Service Support**: Downloads from **Yandex Music, PeerTube, Rutube, Dzen, OK.ru, SoundCloud, VK, Twitter, Reddit, TikTok, Twitch, Bilibili**, and more.
- **Track & Chapter Slicing**: Automatically detects tracklists and chapters in video metadata or descriptions. Downloads specific tracks or sections via `yt-dlp --download-sections` with embedded metadata tags and album art.
- **Video & Audio Trimming**: Trims media based on URL start time parameters (e.g. `?t=1m20s`).
- **Automatic 50 MB Chunking (`/yt`)**: Long videos are automatically offered in 10-minute chunks or chapter tracks to guarantee delivery within 50 MB email size limits, with clickable `▶️ Next track/chunk` navigation.
- **High-Quality Audio Extraction (`/ytm`)**: Extracts audio as Opus with embedded metadata (Artist, Title, Album, Track Number, Cover Art, plain-text lyrics).
- **Subtitles & Lyrics Extraction**: Downloads official and auto-generated subtitles and produces synchronized `.lrc` karaoke files.
- **Navidrome / Subsonic Integration (`/ytms`)**: Admin command to save downloaded tagged audio directly into a Navidrome music directory and trigger a Subsonic API library scan.
- **Visual Progress**: Real-time reaction indicators (`⏳` downloading, `⌛` sending, `☑️` delivered, `❌` error).

## Configuration

In the **Configuration** tab:

1. **Account Credentials**:
   - `chatmail_qr`: Paste your Chatmail QR string (`DCACCOUNT:...`) or URI for instant 1-click account setup.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to gain owner privileges.
   - `admin_fingerprint`: Optional cryptographic OpenPGP fingerprint.
   - `display_name`: Display name shown in Delta Chat profile.
   - `status_text`: Bot status/bio shown in Delta Chat profile.

## Commands

- `/yt <url>` — Download video (MP4).
- `/ytm <url>` — Download audio track (Opus with tags & cover art).
- `/ytms <url>` — Save audio directly to Navidrome music library (Admin only).
- `/stats` — Usage statistics, disk space, and service diagnostics (Admin only).
- `/help` — List all available commands.
