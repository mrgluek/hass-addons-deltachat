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
- 🔔 **@Mentions With Notifications**: Delta Chat has no real mentions, so a group message that starts with `@Nick` is sent again by the bot as a reply to Nick's last message in the chat, under the author's name. A reply to your own message is what makes Delta Chat notify you, also in a muted chat. If nobody in the group has that nick and Username Bot is a member, the author gets the person's invite link privately.
- ➕ **New Group (`/newgroup <name>`)**: Create a new group with the bot in it and get its join link. Anyone can use it, with a 1-minute cooldown per sender (admins are exempt). In a group where Ntfy Bot is a member, plain `/newgroup` is left to Ntfy Bot so one command does not create two groups (`/newgroup@bouncer` still works).
- 🔍 **Member Search (`/search <query>`)**: Find group members across active transports by email or substring.
- 📬 **Relay Check (`/relays`)**: Scan group members using standard webmail providers (Yandex, Mail.ru, Gmail, etc.).
- 🏓 **ChatMail Ping (`/cmping`)**: Ping mail relays (transports) to/from specified target servers using the `cmping` utility with real-time reaction progress.
- 📞 **Echo Calls**: Call the bot from any Delta Chat app: it answers, echoes your voice back and, after you hang up, sends a call report (media path, packet loss, jitter, round trip). `/callstats` shows your recent calls.
- 📲 **Call Test (`/cmcall`)**: Test a Delta Chat call between two relays (signaling, TURN, audio) using the `cmcall` utility.
- 🌐 **IP / Network / AS Lookup (`/ip`)**: Location, organization / AS, announced prefix, open ports and known CVEs for an IP, block, AS number or host name (ipinfo.io, Shodan InternetDB, RIPEstat; works without a key).
- 🧭 **DNS Lookup & Mail / Chatmail Check (`/dns`, `/dig`)**: dig-like lookups and a full report for a domain: addresses, reverse DNS, DNSSEC, MX, SPF, DKIM, DMARC, MTA-STS, TLS-RPT, plus the records `cmdeploy dns` expects for a chatmail relay.
- 📇 **WHOIS / RDAP (`/whois`)**: Registrar, expiry dates, status and name servers for any TLD (RDAP or port-43 WHOIS); for an IP / AS the holder and abuse contact.
- 🛡️ **VirusTotal Inspection (`/virus`)**: Check URLs and files (attachments or reply messages) against VirusTotal threat database.
- 📡 **Server Connectivity Monitoring**: Periodic background monitoring of server connectivity with incident-based alerting.

## Configuration

In the **Configuration** tab:

1. **Account Credentials**:
   - `auto_server` *(default: on)*: Select the closest server automatically. **Optional** - if you leave `chatmail_qr`, `email` and `password` empty, the Delta Chat core probes its built-in list of Chatmail servers and configures the closest one that answers, then adds more relays in the background (core 2.61+).
   - `chatmail_qr`: *Optional.* Paste a Chatmail QR string (`DCACCOUNT:...`) or URI to use a specific server instead.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
   - Only used on first start; an already created account is kept.
2. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to gain owner privileges.
   - `admin_fingerprint`: Optional cryptographic OpenPGP fingerprint.
   - `display_name`: Display name shown in Delta Chat profile.
   - `status_text`: Bot status/bio shown in Delta Chat profile.
3. **Web Service & Base URL**:
   - `base_url`: Public base URL for channel preview links and RSS feeds (e.g. `https://dc.yourdomain.com` or `https://my-ha.duckdns.org:8080`).
   - If port `8080` is forwarded on your router or exposed in the add-on's network settings, channel preview links can be accessed directly from the internet.
4. **Lookups & Integrations (Optional)**:
   - `virustotal_api_key`: Free API key from VirusTotal (virustotal.com) for `/virus` URL and file scanning.
   - `ipinfo_token`: Optional [ipinfo.io](https://ipinfo.io) token for `/ip`. `/ip` works without it; a paid token adds VPN / proxy / Tor / hosting flags.
   - `mention_reply` *(default: on)*: Resend `@Nick` messages as replies so the mentioned member gets a notification.
   - `username_bot_addrs`: Addresses of Username Bot, comma-separated full addresses or local parts (default `usernamebot`).
   - `username_lookup_url`: Username Bot web service used to look up nicks of people not in the group (default `https://deltachat.id`).
   - `ntfy_bot_addrs`: Addresses of Ntfy Bot, comma-separated full addresses or local parts (default `ntfydcbot`). In groups where one of them is a member, plain `/newgroup` is left to Ntfy Bot.

5. **Echo Calls (Optional)**:
   - `call_echo`: Answer calls with an echo (default on).
   - `call_echo_who`: `everybody` (default) or `contacts`.
   - `call_echo_delay`: Echo playback delay in seconds (default `0`, live).
   - `call_echo_max_seconds` / `call_echo_max_concurrent`: Call length cap (default 300 s) and parallel calls (default 2).
   - Call media goes through the TURN server of the bot's relay, so no extra ports are needed.

## Getting Started

1. Start the add-on and scan the **ASCII QR code** in the logs (or click **Open Web UI** in Home Assistant to see the bot landing page).
2. Add the bot to any group chat where you want inactivity monitoring and member catalogs.
3. Send `/help` in the chat to see all available commands!
