# Delta Chat Web Preview Bot

Delta Chat Web Preview Bot automatically generates beautiful OpenGraph link previews (titles, descriptions, thumbnails) and full-page HTML/screenshot archives for links shared in Delta Chat conversations.

## Features

- **Rich Link Previews**: Extracts OpenGraph metadata, title, favicon, and preview images from shared links.
- **Monolith Archives**: Bundles web pages into single self-contained HTML files.
- **Fast & Private**: Cached link lookups with privacy-respecting scraping.

## Configuration

In the **Configuration** tab:

1. **Account**:
   - `chatmail_qr`: Paste a Chatmail QR string (`DCACCOUNT:...`) or URI.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to manage bot settings.
   - `display_name`: Display name shown in Delta Chat.
   - `status_text`: Bot status/bio.

## How to Use

1. Start the add-on and scan the **ASCII QR code** in the logs.
2. Add the bot to your Delta Chat groups, or send it any web link in a direct message.
3. The bot will automatically reply with the preview card!
