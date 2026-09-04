# Delta Chat Username & Short Link Bot (`deltachat_username`)

`deltachat_username` is a Delta Chat bot and FastAPI web service for registering custom usernames and generating short invite links (`https://deltachat.id/<username>`) that redirect (via HTTP 307 Temporary Redirect) to standard Delta Chat invite URLs (`https://i.delta.chat/#...`).

## Key Features

- 👤 **Custom Usernames**: Claim a short username (`/username myname`) for your personal profile or group chat.
- 🔐 **Visual Cryptographic Verification**: Anti-impersonation verification displaying 10-group formatted PGP fingerprints, 5x5 symmetric Unicode block Identicons, and 5-emoji visual badges.
- 🖼️ **Social OpenGraph & Twitter Cards**: Smart crawler detection serving rich metadata and cached dynamic PNG cards (`1200x630`) on Telegram, Discord, Twitter, WhatsApp, etc.
- 📇 **Web Profile Cards & Avatars**: Dynamic endpoints (`/{username}/og.png`, `/{username}/avatar.svg`, and `/{username}/card`) for visual badges, QR codes, and web verification.
- ⚡️ **Group Chat Auto-Binding**: Use `/username myname` directly inside any group chat — the bot instantly generates the group's invite URL without manual link pasting.
- 🔀 **HTTP 307 Temporary Redirect**: Guarantees browsers and proxies always fetch the newest invite link without aggressive caching.
- 🌐 **Web Landing Page**: Dark-mode glassmorphism interface on `GET /` displaying bot description, QR code, and interactive command hints.

## Configuration

In the **Configuration** tab:

1. **Account Credentials**:
   - `chatmail_qr`: Paste a Chatmail QR string (`DCACCOUNT:...`) or URI for instant 1-click account setup.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Domain & URLs**:
   - `base_url`: Public base URL for your short link service (e.g. `https://deltachat.id` or your reverse proxy domain).
   - `invite_base_url`: Prefix for Delta Chat invite links (default: `https://i.deltachat.id/#`).
3. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to manage bot permissions.
   - `admin_fingerprint`: Optional cryptographic OpenPGP fingerprint.
   - `display_name`: Display name shown in Delta Chat profile.
   - `status_text`: Bot status/bio shown in Delta Chat profile.

## Bot Commands

- `/username` — Check your current chat's registered username and short link.
- `/username <name>` — Look up short link for any registered username.
- `/link <name> <url>` — Bind custom username & invite link in private chat.
- `/link <name>` — Auto-generate group invite link and bind username in group chat.
- `/unlink` — Remove username binding for current chat.
