# Delta Chat Publisher Bot

Delta Chat Publisher Bot allows community creators to broadcast announcements, newsletters, and channel messages to an unlimited number of Delta Chat subscribers with full read-only channel protection.

## Features

- **Public Channels**: Subscribers join via invite link or QR code without exposing their identities to each other.
- **Admin Broadcast**: Only administrators can broadcast to subscribers.
- **Rich Media**: Support for formatted Markdown, photos, videos, and documents.

## Configuration

In the **Configuration** tab:

1. **Account**:
   - `chatmail_qr`: Paste a Chatmail QR string (`DCACCOUNT:...`) or URI.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to manage the broadcast channel.
   - `display_name`: Display name shown in Delta Chat.
   - `status_text`: Bot status/bio.
