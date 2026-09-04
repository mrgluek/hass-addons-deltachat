# Delta Chat Uptime Bot

Delta Chat Uptime Bot monitors websites, ping targets, TCP ports, and SSL certificates, sending instant alert notifications directly to your Delta Chat messenger! It also includes a modern, responsive web dashboard.

## Features

- **Multi-Protocol Monitoring**: HTTP/HTTPS status, ICMP ping latency, custom TCP ports, and SSL/TLS certificate expiry.
- **Delta Chat Native**: Receive real-time outage alerts, daily summaries, and control monitoring directly from Delta Chat commands (`/add`, `/rm`, `/list`, `/status`, `/stats`).
- **Web Dashboard**: View live uptime graphs, response times, and history at `http://your-ha-ip:8080`.
- **Peer Telemetry**: Supports distributed mesh monitoring across multiple peers.

## Configuration

In the **Configuration** tab:

1. **Account**:
   - `chatmail_qr`: Paste a Chatmail QR string (`DCACCOUNT:...`) or URI.
   - Or `email` and `password`: Standard IMAP/SMTP mail credentials.
2. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to gain owner privileges.
   - `display_name`: Display name shown in Delta Chat.
   - `status_text`: Bot status/bio.

## Connecting to the Bot

1. Start the add-on.
2. Check the **Log** tab in Home Assistant.
3. Scan the displayed **ASCII QR code** or copy the invitation link into Delta Chat.
4. Send `/help` to see available commands!
