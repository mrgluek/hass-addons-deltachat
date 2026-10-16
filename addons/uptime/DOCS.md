# Delta Chat Uptime Bot (`deltachat_uptime`)

`deltachat_uptime` is a self-hosted uptime monitoring bot (similar to Uptime Kuma) integrated directly with Delta Chat. It monitors resources (websites, APIs, TCP ports, or ping targets) and alerts you inside Delta Chat if they go offline.

Additionally, it automatically generates a secure, beautiful web status dashboard for each chat.

## Key Features

- 🚨 **Incident-Based Alerting & In-Place Dynamic Updates**: Outages trigger a unified Incident per chat. As multiple monitors fail or recover, the bot edits the same incident message in-place with real-time status and duration metrics, eliminating chat notification spam.
- 🔍 **Content & Keyword Assertion**: Scans HTTP responses for silent failure signatures wrapped in `200 OK` responses, and supports custom keyword matching (`/add https://api.site.com Health "status:ok"`).
- ⏸️ **Smart Maintenance Windows (`/pause`)**: Pause monitoring and mute outage alerts during planned maintenance without skewing 30-day uptime metrics.
- ⚡ **Universal Latency Measurement**: Measures probe latency in milliseconds for HTTP/HTTPS, TCP sockets, and ICMP Ping.
- 🔒 **SSL Certificate Expiration Monitoring**: Automatically tracks SSL/TLS expiration for HTTPS targets with staged proactive alerts at 7 days, 3 days, and 24 hours.
- 📊 **Per-Chat Web Status Dashboards**: Generates an unguessable 12-character URL (e.g. `http://your-ha-ip:8081/k8D2x9mPqL1a` or via Ingress) hosting a modern dark-themed web status dashboard.
- 🛰️ **Distributed Multi-Node Peering**: Link multiple bot instances as remote probes via private 1:1 Delta Chat DMs for cross-probe verification. Peering is closed: a bot becomes a peer only if the admin added it with `/addpeer` or it presents a single-use `/invitepeer` token (valid 24h), and peer messages are accepted only end-to-end encrypted from configured peers.
- 🔒 **Controlled Disclosure (`/peershare`)**: By default peers only see monitors from chats the administrator is a member of (`admin`); `all` shares every chat, `none` shares no local monitors.
- 🧱 **SSRF & DNS Rebinding Protection**: Every redirect hop is checked, and probes connect to the validated, pinned DNS answer, so a monitor cannot be turned against local or cloud metadata addresses.

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

## Bot Commands

- `/add <target> [name] ["keyword"]` — Add a monitor (HTTP, HTTPS, TCP, or Ping).
- `/remove <id|url>` — Stop monitoring a resource.
- `/pause <id|url> [dur]` — Mute outage alerts during maintenance.
- `/list` — View all monitored resources in current chat.
- `/status` — View status overview and link to chat's Web Status Dashboard.
- `/ping <target>` — Immediate on-demand reachability check.
- `/invitepeer` — Invite link with a single-use pairing token (valid 24h) for linking another Uptime bot.
- `/addpeer <email|link> [token=<token>] [node_name]` — Link another Uptime bot as a remote probe (use the command its `/invitepeer` prints; without a token both admins must add each other).
- `/rmpeer <email>` — Remove a remote peer probe.
- `/peershare [admin|all|none]` — Choose which local monitors are disclosed to peers (default `admin`).
