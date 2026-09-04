# Delta Chat ntfy Bot

Delta Chat ntfy Bot bridges [ntfy.sh](https://ntfy.sh) (and self-hosted ntfy instances) with Delta Chat, enabling bidirectional pub/sub notifications.

## Features

- **Push Notifications**: Receive alerts from home automation, bash scripts, and monitoring systems directly in Delta Chat.
- **Webhook Receiver**: Webhook endpoint at `http://your-ha-ip:8080/webhook`.
- **Bidirectional**: Publish messages from Delta Chat directly to ntfy topics.

## Configuration

In the **Configuration** tab:

1. **Account**:
   - `chatmail_qr`: Paste a Chatmail QR string (`DCACCOUNT:...`) or URI.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Security**:
   - `auth_token`: Optional secret authentication token for webhook protection.
3. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to manage bot topics.
   - `display_name`: Display name shown in Delta Chat.
   - `status_text`: Bot status/bio.
