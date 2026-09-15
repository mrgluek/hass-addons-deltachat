# Delta Chat Bouncer Bot (`deltachat_bouncer`)

`deltachat_bouncer` is a Delta Chat bot designed to maintain group quality by monitoring inactivity and saving server resources by avoiding sending emails to stale users. It scans group members and reports users who haven't been seen online for over 21 days.

## Features

- ⚠️ **Inactivity Reports (`/bounce`)**: Trigger a manual scan for inactive group members with member counts and inactive lists (default threshold: 21 days).
- 🧹 **Automatic Inactivity Kick (`/autokick`)**: Automatically purge stale, inactive members from group chats in the background (configurable threshold, e.g. `/autokick 30`).
- 👞 **Manual Member Kick (`/kick <userid>`)**: Remove members from a group chat by contact ID, search query, or by replying to their message.
- 📖 **Group Chat Catalog (`/chats`)**: Browse registered group chats with member counts, descriptions, and join request links.
- 📢 **Channels Catalog (`/dchannels`)**: Browse all registered Delta Chat broadcast channels with preview links.
- 🌐 **Channel Web Previews & RSS Feeds (`/c/{token}`)**: Embedded web server providing modern web previews for public channels, live message history, media attachments, QR join modals, and standard RSS 2.0 feeds (`/c/{token}/rss.xml`).
- 🚪 **Home Assistant Ingress**: Direct access to Bouncer Bot's landing page and channel previews from the Home Assistant sidebar without exposing ports to the public.
- 🔐 **Join Approval Workflows**: Private groups (`🔐`) require approvals from existing members via dynamic `/approve<ID>` commands.
- 👋🏻 **Custom Welcome Messages (`/welcome`)**: Configurable greetings for new members joining groups with common chat statistics.
- 🔗 **Invite Link & QR Code (`/invite`)**: Generate SecureJoin invite links and QR codes directly in chat.
- 🔍 **Member Search (`/search <query>`)**: Find group members across active transports by email or substring.
- 📬 **Relay Check (`/relays`)**: Scan group members using standard webmail providers (Yandex, Mail.ru, Gmail, etc.).
- 🏓 **ChatMail Ping (`/cmping`)**: Ping mail relays (transports) to/from specified target servers using the `cmping` utility with real-time reaction progress.
- 🛡️ **VirusTotal Inspection (`/virus`)**: Check URLs and files (attachments or reply messages) against VirusTotal threat database.
- 📡 **Server Connectivity Monitoring**: Periodic background monitoring of server connectivity with incident-based alerting.

## Configuration

In the **Configuration** tab:

1. **Account Credentials**:
   - `chatmail_qr`: Paste a Chatmail QR string (`DCACCOUNT:...`) or URI for instant 1-click account setup.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to gain owner privileges.
   - `admin_fingerprint`: Optional cryptographic OpenPGP fingerprint.
   - `display_name`: Display name shown in Delta Chat profile.
   - `status_text`: Bot status/bio shown in Delta Chat profile.
3. **Web Service & Base URL**:
   - `base_url`: Public base URL for channel preview links and RSS feeds (e.g. `https://dc.yourdomain.com` or `https://my-ha.duckdns.org:8080`).
   - If port `8080` is forwarded on your router or exposed in the add-on's network settings, channel preview links can be accessed directly from the internet.
4. **VirusTotal (Optional)**:
   - `virustotal_api_key`: Free API key from VirusTotal (virustotal.com) for `/virus` URL and file scanning.

## Getting Started

1. Start the add-on and scan the **ASCII QR code** in the logs (or click **Open Web UI** in Home Assistant to see the bot landing page).
2. Add the bot to any group chat where you want inactivity monitoring and member catalogs.
3. Send `/help` in the chat to see all available commands!
