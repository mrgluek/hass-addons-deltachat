# Delta Chat Web Preview Bot (`deltachat_webpreview`)

`deltachat_webpreview` is a Delta Chat bot designed to save web pages as complete, single self-contained HTML files (including images, CSS, fonts, and assets) using `monolith` and send them back to the chat as attachments.

## Key Features

- 📄 **Compressed Reader Mode (`/preview <url>`)**: Compile webpages into clutter-free reader views using Mozilla Readability with optimized Base64 inlined images.
- 📱 **WebXDC App Packaging (`/webxdc <url>`)**: Generate a standalone WebXDC application (`.xdc` ZIP container with `index.html`, `manifest.toml`, and `icon.png`) from any webpage for interactive offline viewing.
- ⚡ **AI Summarization (`/tldr [url]` & Previews)**: Generate 1-2 paragraph summaries or bullet points of articles using the Google Gemini API (`gemini_api_key`).
- 🌐 **Per-Chat Language (`/lang <code>`)**: Set target summary language per chat (`AUTO`, `RU`, `EN`, `DE`).
- ⚡ **Full Page Archiving (`/archive <url>`)**: Save complete pages as full interactive archives with JavaScript enabled using `monolith`.
- 🏛️ **Multi-Service Archiving (`/keep <url>`)**: Save webpages to KaraKeep, Wayback Machine (SPN2), Archive.today, and Ghostarchive.
- 💾 **Direct File Downloads**: Automatically detects URLs pointing to documents (PDF, EPUB, DjVu, MS Office, LibreOffice) and delivers them directly (up to 50 MB).
- 📱 **Telegram (`t.me`) & Instagram Embeds**: Scrapes public Telegram channel previews and resolves Instagram links via OGInstagram proxy.

## Configuration

In the **Configuration** tab:

1. **Account Credentials**:
   - `auto_server` *(default: on)*: Select the closest server automatically. **Optional** - if you leave `chatmail_qr`, `email` and `password` empty, the Delta Chat core probes its built-in list of Chatmail servers and configures the closest one that answers, then adds more relays in the background (core 2.61+).
   - `chatmail_qr`: *Optional.* Paste a Chatmail QR string (`DCACCOUNT:...`) or URI to use a specific server instead.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
   - Only used on first start; an already created account is kept.
2. **AI & Proxy Settings (Optional)**:
   - `gemini_api_key`: Google Gemini API key for article TL;DR summaries (`/tldr`) and preview summaries.
   - `proxy_url`: Optional HTTP or SOCKS5 proxy URL (e.g. `http://127.0.0.1:8118` or `socks5://127.0.0.1:9050`).
   - `jina_api_key`: Optional API key for Jina Reader (`r.jina.ai`) fallback parser.
3. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to gain owner privileges.
   - `admin_fingerprint`: Optional cryptographic OpenPGP fingerprint.
   - `display_name`: Display name shown in Delta Chat profile.
   - `status_text`: Bot status/bio shown in Delta Chat profile.

## How to Use

1. Start the add-on and scan the **ASCII QR code** in the logs.
2. Add the bot to your Delta Chat groups, or send it any web link in a direct message.
3. Use `/preview <url>`, `/archive <url>`, `/webxdc <url>`, or `/tldr <url>`!
