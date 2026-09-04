# Delta Chat Telegram Bridge

Delta Chat Telegram Bridge connects Telegram groups/channels and Delta Chat chats, relaying messages, media (photos, videos, audio, files), reactions, edits, and deletions bidirectionally in real time.

## Features

- **Bidirectional Relaying**: Seamless two-way forwarding between Delta Chat and Telegram.
- **Media & File Support**: High-speed forwarding of images, documents, videos, voice messages, and stickers.
- **Message Edits & Deletions**: Sync message modifications and deletions across platforms.
- **Channel Feeds**: Subscribe Delta Chat groups to public Telegram channels.

## Configuration

In the **Configuration** tab:

1. **Account**:
   - `chatmail_qr`: Paste a Chatmail QR string (`DCACCOUNT:...`) or URI.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Telegram**:
   - `telegram_token`: Telegram Bot Token obtained from [@BotFather](https://t.me/BotFather).
3. **Admin & Identity**:
   - `admin_email`: Your personal Delta Chat email to manage bridge settings.
   - `display_name`: Display name shown in Delta Chat.
   - `status_text`: Bot status/bio.

## How to Bridge Chats

1. Start the add-on and scan the **ASCII QR code** in the logs to connect with the bot in Delta Chat.
2. Add your Telegram bot to a Telegram group and make it an admin. Get the Telegram group ID.
3. Add the Delta Chat bot to your Delta Chat group.
4. Send `/bridge <telegram_group_id>` in the Delta Chat group to link them together!
