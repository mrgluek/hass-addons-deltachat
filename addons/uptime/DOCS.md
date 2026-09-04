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
- 🛰️ **Distributed Multi-Node Peering**: Link multiple bot instances as remote probes via private 1:1 Delta Chat DMs (`/addpeer`) for cross-probe verification.

## Configuration

In the **Configuration** tab:

1. **Account Credentials**:
   - `chatmail_qr`: Paste your Chatmail QR string (`DCACCOUNT:...`) or URI for instant 1-click account setup.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
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
