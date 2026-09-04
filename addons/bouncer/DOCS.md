# Delta Chat Bouncer Bot (`deltachat_bouncer`)

`deltachat_bouncer` is a Delta Chat bot designed to maintain group quality by monitoring inactivity and saving server resources by avoiding sending emails to stale users. It scans group members and reports users who haven't been seen online for over 21 days.

## Features

- ⚠️ **Inactivity Reports (`/bounce`)**: Trigger a manual scan for inactive group members with member counts and inactive lists (default threshold: 21 days).
- 🧹 **Automatic Inactivity Kick (`/autokick`)**: Automatically purge stale, inactive members from group chats in the background (configurable threshold, e.g. `/autokick 30`).
- 👞 **Manual Member Kick (`/kick <userid>`)**: Remove members from a group chat by contact ID, search query, or by replying to their message.
- 📖 **Group Chat Catalog (`/chats`)**: Browse registered group chats with member counts, descriptions, and join request links.
- 📢 **Channels Catalog (`/dchannels`)**: Browse all registered Delta Chat broadcast channels.
- 🔐 **Join Approval Workflows**: Private groups (`🔐`) require approvals from existing members via dynamic `/approve<ID>` commands.
- 👋🏻 **Custom Welcome Messages (`/welcome`)**: Configurable greetings for new members joining groups with common chat statistics.
- 🔗 **Invite Link & QR Code (`/invite`)**: Generate SecureJoin invite links and QR codes directly in chat.
- 🔍 **Member Search (`/search <query>`)**: Find group members across active transports by email or substring.
- 📬 **Relay Check (`/relays`)**: Scan group members using standard webmail providers (Yandex, Mail.ru, Gmail, etc.).
- 🏓 **ChatMail Ping (`/cmping`)**: Ping mail relays (transports) to/from specified target servers using the `cmping` utility with real-time reaction progress.
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

## Getting Started

1. Start the add-on and scan the **ASCII QR code** in the logs.
2. Add the bot to any group chat where you want inactivity monitoring and member catalogs.
3. Send `/help` in the chat to see all available commands!
