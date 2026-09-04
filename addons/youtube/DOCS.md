# Delta Chat YouTube Bot

Delta Chat YouTube Bot allows you to download videos, audio tracks, and playlists from YouTube and hundreds of supported sites using `yt-dlp` and `ffmpeg`, delivering them directly to your Delta Chat chats.

## Features

- **Audio & Video Extraction**: Extract MP3/AAC audio or MP4 video by sending any media link.
- **Deno Runtime Engine**: Solves modern YouTube JavaScript challenges reliably.
- **Inline Format Choices**: Choose format, quality, and resolution via Delta Chat command options.

## Configuration

In the **Configuration** tab:

1. **Account**:
   - `chatmail_qr`: Paste a Chatmail QR string (`DCACCOUNT:...`) or URI.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to manage bot permissions.
   - `display_name`: Display name shown in Delta Chat.
   - `status_text`: Bot status/bio.
