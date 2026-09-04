# Delta Chat ↔ Telegram Bridge Bot (`deltachat_telegram_bridge`)

`deltachat_telegram_bridge` acts as a bridge between Delta Chat groups and Telegram groups/channels. It relays messages sent in mapped Telegram groups to corresponding Delta Chat groups, and vice-versa.

## Key Features

- 🔄 **Bidirectional Group Bridging**: Sync messages between Telegram groups and Delta Chat groups.
- 🗑️ **Bidirectional Deletion Sync**: Sync message deletions between both platforms with built-in safety guards.
- ✏️ **Bidirectional Edit Handling**: In-place edit synchronization in both directions.
- 📢 **Public Telegram Channels**: Bridge any public channel to a Delta Chat broadcast group.
- ✨ **Rich Text & Formatting**: Full conversion of Telegram rich text (bold, italic, underline, strikethrough, spoiler, inline code, code blocks, blockquotes, expandable blockquotes, and links) into native Delta Chat Markdown.
- ⭐ **Telegram Paid Media & Extended Types**: Full support for Telegram Paid Media (posts/photos/videos locked with Telegram Stars), Stories, Giveaways, Polls, Contacts, and Invoices without skipping posts.
- 📜 **Historical Context**: Pre-fills newly bridged channels with the last 3 historical posts.
- 👤 **Userbot Mode**: Bridge channels without needing administrator permissions.
- 🛡️ **Watchdog & Auto-Reconnection**: Detects and recovers from connection hangs and polling timeouts automatically.
- 🧹 **Automatic Cleanup Worker**: Purges orphaned records and dead ghost groups.

## Configuration

In the **Configuration** tab:

1. **Account Credentials**:
   - `chatmail_qr`: Paste your Chatmail QR string (`DCACCOUNT:...`) or URI for instant 1-click account setup.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Telegram Bot Token**:
   - `telegram_token`: Telegram Bot API token obtained from [@BotFather](https://t.me/BotFather).
3. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to gain owner privileges.
   - `admin_fingerprint`: Optional cryptographic OpenPGP fingerprint.
   - `display_name`: Display name shown in Delta Chat profile.
   - `status_text`: Bot status/bio shown in Delta Chat profile.

## How to Bridge Chats

1. Start the add-on and scan the **ASCII QR code** in the logs.
2. Add your Telegram bot to a Telegram group and make it an admin. Note the Telegram group ID.
3. Add the Delta Chat bot to your Delta Chat group.
4. In the Delta Chat group, send `/bridge <telegram_group_id>` to link them together!
