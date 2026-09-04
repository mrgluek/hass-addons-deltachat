# Delta Chat ntfy Bot (`deltachat_ntfy`)

`deltachat_ntfy` is a Delta Chat bot that emulates the backend of [ntfy.sh](https://ntfy.sh) and broadcasts incoming HTTP POST/PUT requests to subscribed Delta Chat users and groups.

It provides a modern web interface for each topic (e.g., `http://your-ha-ip:8082/mytopic` or via Home Assistant Ingress sidebar) displaying historical notifications, streaming new notifications in real-time, and allowing users to publish notifications directly from their browser.

## Key Features

- **Push Notifications from Anything**: Send alerts from Home Assistant automations, bash scripts, curl, GitHub webhooks, and monitoring systems directly to Delta Chat.
- **ntfy-Compatible HTTP API**: Send notifications via simple `curl` commands with Priority (1–5 emojis), Titles, and Tags.
- **Topic Web UI & Ingress**: View topic notification history and send notifications directly from the browser inside Home Assistant.
- **JSON Stream API (`/mytopic/json`)**: Programmatic JSON streaming for automated agents or scripts (`since=all`, `poll=1`).
- **Subscription Management**: Users subscribe/unsubscribe to topics directly in Delta Chat (`/sub <topic>`, `/unsub <topic>`, `/list`).

## Configuration

In the **Configuration** tab:

1. **Account Credentials**:
   - `chatmail_qr`: Paste your Chatmail QR string (`DCACCOUNT:...`) or URI for instant 1-click account setup.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Security**:
   - `auth_token`: Optional secret authentication token to restrict publishing.
3. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to gain owner privileges.
   - `admin_fingerprint`: Optional cryptographic OpenPGP fingerprint.
   - `display_name`: Display name shown in Delta Chat profile.
   - `status_text`: Bot status/bio shown in Delta Chat profile.

## Sending Notifications

### Via HTTP `curl`

```bash
# Basic message
curl -d 'Backup successful 😀' http://your-ha-ip:8082/mytopic

# With Title and Priority
curl -H 'Title: Backup Status' -H 'Priority: high' -d 'Backup completed!' http://your-ha-ip:8082/mytopic
```

### In Home Assistant Automations (REST Command)

```yaml
rest_command:
  send_deltachat_alert:
    url: "http://localhost:8082/alerts"
    method: POST
    payload: "{{ message }}"
```
