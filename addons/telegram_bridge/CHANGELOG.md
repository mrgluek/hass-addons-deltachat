# Changelog

## 2.18.5

- **Fixed Telethon Infinite Reconnection Loop on NoneType Connection**:
  - Monkey-patched `MTProtoSender._reconnect` (`_safe_telethon_reconnect`) to immediately abort reconnection attempts when `_connection` is `None` (sender was already disconnected or abandoned), preventing infinite loop crashes (`AttributeError: 'NoneType' object has no attribute 'connect'`).
  - Changed `connection_retries` from `None` (unbounded infinite attempts) to `5` in `TelegramClient`, allowing dead senders to terminate cleanly so the userbot watchdog can re-initialize a fresh session.
  - Added `telethon.network.mtprotosender` to `PollingErrorFilter`.

## 2.18.4
- Initial Home Assistant Add-on release.
- Bidirectional Telegram <-> Delta Chat bridge with media and edit sync.
- Interactive Home Assistant configuration tab for bot tokens and mail credentials.
