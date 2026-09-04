# Delta Chat Bouncer Bot

Delta Chat Bouncer Bot acts as a gateway and anti-spam firewall for your Delta Chat accounts. It filters incoming messages, enforces verification challenges, auto-replies, and forwards authorized messages to your real personal chat.

## Features

- **Spam Filtering & Gatekeeping**: Requires new contacts to pass verification before contacting you.
- **Auto-Responder**: Send configurable automated replies to new or existing contacts.
- **Message Forwarding**: Forward messages from unknown senders to an administrator for approval.
- **Whitelist & Blacklist**: Flexible access control via Delta Chat commands.

## Configuration

In the **Configuration** tab:

1. **Account**:
   - `chatmail_qr`: Paste a Chatmail QR string (`DCACCOUNT:...`) or URI.
   - Or `email` and `password`: Standard IMAP/SMTP credentials.
2. **Admin & Identity**:
   - `admin_email`: Your Delta Chat email address to receive forwarded messages and manage the bouncer.
   - `display_name`: Display name shown in Delta Chat.
   - `status_text`: Bot status/bio.
