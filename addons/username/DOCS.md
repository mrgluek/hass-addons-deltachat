# Delta Chat Username Bot

Delta Chat Username Bot provides a community phonebook/directory service. Users can register easy-to-remember handles/aliases (e.g. `@alice`) linked to their Delta Chat address, search for other users, and share verified contact cards.

## Features

- **Handle Registration**: Reserve unique usernames in Delta Chat.
- **Search & Discovery**: Find users by username or alias.
- **Web Directory**: Optional read-only web directory at `http://your-ha-ip:8080`.

## Configuration

In the **Configuration** tab:

1. **Account**:
   - `chatmail_qr`: Paste a Chatmail QR string (`DCACCOUNT:...`) or URI.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to manage registered aliases.
   - `display_name`: Display name shown in Delta Chat.
   - `status_text`: Bot status/bio.
