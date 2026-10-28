# Changelog

## 2.46.0

### Changed
- **cmping 0.19.0**: adds `--both`, `--json` and `--grace`; it no longer stops itself with SIGINT 60 s after the last ping.
- **`/cmping` Pings Both Ways in One Run**: each server pair is one cmping run with `--both` (90 s limit) instead of two runs, so the profiles are set up once.
- **Results Read from JSON**: the monitor and `/cmping` read cmping's `--json` result instead of guessing from its text. Setup failures ("<address> not online after 30s") are reported as errors about the relay; lost pings as "N of M pings lost". `--grace` (a sixth of the time limit) keeps cmping from being killed while waiting for lost pings. When the output is not JSON (killed, crashed) the text is parsed as before.

## 2.45.1

### Changed
- **cmping 0.17.6**: fixes ported from upstream chatmail/cmping: a time limit for profiles to come online, `[ip]` in dclogin links for IP relays with 9-character logins, and a warning when a profile uses more than one relay.
- **Relay Check Errors Name the Relay**: cmping runs now get `-w` with half their time limit (30 s of 60, 45 s of 90). A relay that never lets a profile in is reported as "<address> not online after 30s" instead of the whole run being killed with "Timeout expired (60s)". The command line is built in one place, `cmping.cmping_cmd()`.

## 2.45.0

### Changed
- **Delta Chat Core 2.66.0**: `deltachat-rpc-server` is pinned to 2.66.0 (was 2.65.0). Core 2.66 removes the `configured_addr` config: `get_config("configured_addr")` now fails with "unknown key", and `addr` has been empty since core 2.61. The bot's own address now comes from its self contact (`dc_fingerprint.get_self_addr()`), which the core fills from the primary relay; this also works on older cores.
- **cmping 0.17.5 and cmcall 0.1.7**: Both read their profiles' addresses from `configured_addr` and would fail on core 2.66 (relay monitoring and call checks). `deltachat-rpc-client` is pinned to 2.66.0 too, so the client the tools use matches the server.

## 2.44.3

### Fixed
- **Info Messages Handled Again**: Since v2.38.0 the info-message decorator sat on a helper inserted above its handler (`_expire_invite_message`), so every info message raised a `TypeError` and `handle_dc_info_message` never ran. Catalog channel renames and new pictures, member counts after joins and leaves, removing chats the bot was removed from, welcome messages for new members and withdrawing used single-use invites all work again. A new test checks that every `@dc_cli.on` hook takes `(bot, accid, event)` and that the info-message handler is registered.

## 2.44.2

### Security
- **Admin Check No Longer Fooled by a Display Name**: The contact's key fingerprint was found by searching the whole `get_contact_encryption_info()` text for hex strings, including the line with the contact's display name, so a contact named `x<admin fingerprint>x` passed the admin check. The fingerprint is now read only from the lines under each key header, and the bot's own key is recognised by the fingerprint in its invite link instead of by its address. When the keys cannot be told apart the check fails instead of guessing. The code is in `dc_fingerprint.py`, shared verbatim between the bots.

### Changed
- **Ready for the Core 2.66 Fingerprint Format**: Core 2.66 prints `Me:` instead of `Me (address):` and sorts the key blocks by fingerprint, so finding a key block by address stops working. The new parser handles both formats.
- **Core Pinned to 2.65.0**: `deltachat-rpc-server` was `>=2.62.0`, so any image rebuild pulled core 2.66.0, which removes the `configured_addr` option the bot still reads. Core upgrades are now made on purpose, after reading the core changelog.

## 2.44.1

### Changed
- **Download Limit 64 KB Instead of 1 Byte**: The intent was to skip attachments, but with a limit of 1 byte the Delta Chat core treats every incoming message, plain text too, as too large and fetches it later one by one instead of in the normal batch, which delayed replies to commands. With 64 KB commands arrive at once; larger attachments are still downloaded only on demand (`/sticker`, `/virus`, `/save`).

## 2.44.0

### Added
- **The bot creates its own account at first start.** `serve` without a configured account (a fresh `data/` directory) no longer exits with "no configured accounts": the bot asks the Delta Chat core (2.62+) to create one, and the core picks the fastest chatmail relay from its built-in list and later adds further relays in the background. The new address is logged (`Account created: …`). If no relay answers, the error is logged, the bot exits and the container restart tries again. `bot.py init <addr> <password>` and `bot.py init DCACCOUNT:server.tld` still choose the account, and the admin is still set with `set_admin.py` or `/initadmin`.

## 2.43.2

### Fixed
- **`/cmcall` and the call monitor failed at `setup` with "Could not find DNS resolutions" for a relay that resolved fine** ([#7](https://github.com/mrgluek/deltachat_bouncer/issues/7)). While the relay's DNS was broken, profile setup outlasted the 240 s subprocess timeout; every killed `cmcall` left a half-created profile in `data/cmcall_cache/<relay>/` (144 for cm2.wwire.su), until deltachat-rpc-server ran out of file descriptors and every DNS lookup failed with EMFILE. cmcall [0.1.6](https://github.com/mrgluek/cmcall/releases/tag/v0.1.6) removes such leftovers when it opens a relay's profiles, and the container's open-files limit is raised from 1024 to 65536 (`ulimits` in `docker-compose.yml`).

## 2.43.1

### Fixed
- **`/ip` and `/dns` could hang for minutes on the RU mobile whitelist.** The first lookup after a restart (and every 6 hours after) downloaded the list inside the lookup, and the 20 s timeout only covered each socket read: a throttled connection that trickles bytes kept the download, the lookup and every `/ip` queued behind it waiting, with nothing in the log. The list is now downloaded in its own thread: a lookup waits at most 15 s for the first copy (then shows `list unavailable, try later`), a stale copy answers right away while the refresh runs, and a download is stopped after 2 minutes. The log shows `RU whitelist: downloading …` and `loaded N … in X s`.

## 2.43.0

### Changed
- **The server runs releases, not the tip of `master`.** `update.sh` deploys the newest `vX.Y.Z` tag, so a merge into `master` reaches the server only once it is released; several PRs can go out together. `UPDATE_REF` in `.env.local` pins a release (`UPDATE_REF=v2.42.0` - a rollback; empty again = newest) or follows a branch as before (`UPDATE_REF=master`). A release tag moved on GitHub or Forgejo makes the update fail instead of deploying the changed code. Errors that stopped the script with a message (both remotes unreachable, an unknown `UPDATE_REF`) now also ping the healthcheck's `/fail`, not only failed commands. The script now runs as one function, so the `git reset` that rewrites `update.sh` cannot confuse the running copy.
- **Releases are published by a tag** (new `.github/workflows/release.yml`): pushing `vX.Y.Z` checks that `config.py` has that version, creates the GitHub release with the version's section of this file as its notes (an existing release is left alone), then sends the ntfy notification and the `bot-updated` dispatch to `hass-addons-deltachat` (now with `"version"` in the payload). Both used to go out on every push to `master` (`bouncer-changelog.yml`, removed), so Home Assistant users got unreleased code.
- Releasing: merge, then `git tag -a vX.Y.Z -m "..." <commit> && git push origin vX.Y.Z`.
- **Upgrading:** tag `v2.43.0` right after merging this. Until then the new `update.sh` would deploy `v2.42.1`, which still has the old script that follows `master` - and the server would switch back and forth on every run.

## 2.42.1

### Changed
- **RU mobile whitelist: fresher IP subnets.** The IP check now uses `ru-mobile-whitelist-ip.txt` of [ancored/ru-mobile-whitelist](https://github.com/ancored/ru-mobile-whitelist) instead of hxehex's `cidrwhitelist.txt`, whose subnets had not changed since May 2026. The ancored list is rebuilt daily from several public lists (hxehex, roscomvpn, d010b, overskye, escapingworm) and drops the subnets reported as removed from the whitelists. The domain check keeps hxehex's `whitelist.txt`: the ancored SNI list folds hosts into parent domains, so `/dns` could no longer tell a listed host from a listed subdomain. `/ruwhitelist` names both sources. `RU_WHITELIST_URL` in `.env` still overrides the default.

## 2.42.0

### Added
- **`/ip` and `/dns` check the Russian mobile internet whitelists** (new `whitelist.py`). When Russian operators restrict mobile internet, only whitelisted resources stay reachable, so it matters whether a relay is listed. Data: the community lists [hxehex/russia-mobile-internet-whitelist](https://github.com/hxehex/russia-mobile-internet-whitelist) - `cidrwhitelist.txt` (IPv4 subnets; its `ipwhitelist.txt` lies entirely inside them) and `whitelist.txt` (exact host names, the SNI the filters let through).
  - `/ip <address>`: `📶 RU mobile whitelist: ✅ in 2.63.0.0/17` or `❌ not listed` (IPv6: not checked, the list is IPv4 only).
  - `/ip <block>`: listed as a whole, partly (how many addresses, which subnets) or not at all; `/ip AS<n>`: how many of the announced IPv4 prefixes are listed in whole or part.
  - `/dns <domain>`: in the Addresses section, one line for the IPv4 addresses of the domain and of its MX hosts, and one for the name: `✅ … is listed` (with its listed subdomains), `⚠️ … is not listed, only N of its subdomains: …` or `❌ … is not listed`.
- **`/ruwhitelist [ip|domains] [on|off]`** (admin): switches the IP check, the domain check or both, stored in the database; without arguments it shows the state and how many entries are loaded. Switching drops cached `/ip` and `/dns` answers. Until the admin sets it, `RU_WHITELIST_URL` / `RU_WHITELIST_DOMAINS_URL` in `.env` decide: unset means on with the default list, another URL a list in the same format, an empty value off.
- Each list is downloaded on first use and refreshed every 6 hours; a failed download keeps the old copy and is retried after 10 minutes.

### Fixed
- ActivityPub requests (Fediverse deliveries, follows, actor fetches) sent `User-Agent: BouncerBot/2.14.2`: `activitypub.py` kept its own stale version number. It now uses the bot's version from `config.py`, like everything else.

## 2.41.1

### Fixed
- `/dns`: a DKIM key published as several separate TXT records (e.g. a long key pasted in three parts into a DNS panel) was reported as "key is not valid base64". It now says `❌ DKIM <selector>: split into N separate TXT records - it must be one record`. Records of a set have no order and receivers never join them, so such a key never verifies; a long key belongs in one TXT record split into strings of up to 255 characters.

## 2.41.0

### Added
- **`/dns` shows the domain's certificates from Certificate Transparency logs** (new `certs.py`, data from SSLMate Cert Spotter): the number of valid certificates and their CAs, the date of the latest one, until when the domain itself is covered (⚠️ under 10 days: renewal may be failing), a ⚠️ for certificates from a CA the current CAA record does not allow, a note for Cloudflare Universal SSL (Cloudflare issues wildcard certificates for zones on its DNS by itself and adds its CAs to the CAA answer - so `chatmail.uk`'s `*.chatmail.uk` from SSL.com is expected), and the subdomain names found in certificates (often names that are nowhere in DNS).
- Chatmail relay check: whether one valid Let's Encrypt certificate covers the domain, `mta-sts.` and `www.`.
- Optional `CERTSPOTTER_API_KEY` in `.env` (free Small plan: 10 full-domain and 100 single-hostname queries an hour). The bot counts its queries per hour, falls back to a single-hostname query (no subdomains) when the full-domain budget is spent, pauses after HTTP 429 and caches CT answers for an hour. If Cert Spotter does not answer, the rest of the report is unchanged.
- Censys is not used for this: its free plan cannot search certificates by domain and every lookup costs a credit.

## 2.40.0

### Added
- **`/ip` asks Censys when Shodan has nothing**: Shodan InternetDB has no record for many hosts whose networks block Shodan's scanners (e.g. a Selectel server with ports 80 and 443 open for years showed "none seen by Shodan"). With `CENSYS_API_TOKEN` in `.env` (free Censys account), the bot then looks the IP up in the Censys Platform API and shows `🔌 Open ports (Censys): ...`, the software, web page titles per port (`📄 8083: LOGIN - ... - Hestia Control Panel`) and a link to the Censys host page. If Censys sees nothing either: "none seen by Shodan or Censys".
- Censys credits are limited (free: 100 per 30 days, 1 per lookup, shared with the web UI), so the bot calls it only as a fallback, caches answers for a day, makes at most `CENSYS_MONTHLY_LIMIT` (default 90) lookups in any 30 days (rolling window: Censys resets 30 days after sign-up, not on the 1st) and pauses for a day on HTTP 401/402/403. Each lookup is logged with the credits used.

## 2.39.4

### Fixed
- **Catalog notices to the admin were not delivered**: The admin chat was opened with `lookup_contact_id_by_addr(admin address)`, which gives the address-only contact. Current cores only send encrypted, so catalog review notices failed with `e2e encryption unavailable`. The bot now sends to the admin's contact with their key: the one with the fingerprint saved by `/initadmin`, otherwise the most recently seen key contact of the admin address.

## 2.39.3

### Fixed
- Update cmping to v0.17.4: creating a test profile is limited to 20 s per attempt and falls back to `/new` + `dclogin` with the standard ports (IMAP 993, SMTP 465, SSL). Relays whose autoconfig lists ports unreachable from the bot's server (chat.chudppl.org) no longer hang until the 60 s timeout, and failed attempts no longer pile up unconfigured profiles in `data/cmping_cache`.

## 2.39.2

### Fixed
- `/chats` and `/dchannels` show only the first non-empty line of a description, with spaces collapsed and cut at a word boundary (100 / 200 characters, `…`). Multi-line chat descriptions (rules, links) used to spill into the list. The full description is still stored; existing entries are fixed too.

## 2.39.1

### Fixed
- **cmping profiles grew without bound** (cmping `v0.17.3`): every run created a new "cmping" group on the sender and receivers and never deleted it. The monitor's cached profiles reached ~20k groups and 20+ MB `dc.db` each (487 MB in `data/cmping_cache`), read on every run every 30 minutes; the page cache this kept hot showed up as ~105 MB of the container's memory. cmping now deletes chats from earlier runs before each ping (10 s budget per run, so an old big profile is cleaned over several runs).

## 2.39.0

### Added
- **Catalog submissions by users** (`catalog_review.py`): `/chatadd` (inside a group) and `/dchanneladd <link>` work for everyone, not only the admin. The admin path is unchanged.
  - **Eligibility:** the bot must have known the submitter for 3+ days (`CATALOG_MIN_AGE_DAYS`); at most 2 pending and 5 per week per user, 50 pending in total; banned submitters are refused.
  - **Red flags:** stop words (`CATALOG_STOPWORDS`) in name, description and recent channel posts; VirusTotal verdicts for up to 3 links (new quiet `virustotal.url_verdict()`). Flags only stop auto-approval.
  - **Auto-approval** for submitters known for 30+ days (`CATALOG_AUTO_APPROVE_DAYS`, 0 = never) without red flags; a channel whose join is not finished is always reviewed.
  - **Review card** in the admin's private chat: submitter with age, owner check, flags, review preview link, `/chatapprove<ID>`, `/chatreject<ID> [reason]`, `/chatban<ID>` (same with `/dchannel…`). `/catalogqueue` lists what waits.
  - **Groups** submitted by a member are private by default (joining from the catalog needs the members' approval); members of such a group may use `/private` and `/chatremove`. A pending group hands out no invites from `/chat<ID>`.
  - **Channels** submitted by someone who did not create the invite link are listed without web preview, RSS and Fediverse (`web_enabled = 0`); `/dchannelweb<ID>on|off` for the admin. A rejected channel is left, its cached posts and media deleted.
  - **Reports:** `/chatreport<ID>`, `/dchannelreport<ID> [reason]`; 3 reports (`CATALOG_REPORT_THRESHOLD`) from contacts of the minimum age hide the entry until the admin decides.
  - `/catalogsubmit on|off` (runtime switch, overrides `CATALOG_SUBMISSIONS`), `/catalogban <addr>`, `/catalogunban <addr>`.
- Database: `status`, `submitted_by`, `submitted_at` on `catalog_chats` and `catalog_channels`, `web_enabled` on `catalog_channels`; new tables `catalog_submissions`, `catalog_reports`, `catalog_banned_submitters`. Existing entries stay approved.

### Changed
- Web preview, RSS, media, QR, ActivityPub actor/inbox/outbox and WebFinger look channels up through `database.get_web_channel_by_token()`, which hides channels without web mirroring; the landing page lists only mirrored channels.
- `/dchannels` and `/dchannel<ID>` show the preview link only for mirrored channels, mark pending ones for the admin, and offer `/dchannelreport<ID>`; the `/chat<ID>` invite reply offers `/chatreport<ID>`.

## 2.38.0

### Added
- **Paced outbox for everything the bot sends** (`outbox.py`, the module from Uptime Bot 2.19.0): chatmail relays allow each sender 60 messages a minute with a burst of 10 and answer `450 Too much mail` above it; the core retries, the retries count too, and everything after a burst arrives minutes late. Bouncer is in ~70 chats, and cmping / cmcall alerts with their live edits go to every report chat at once, on top of replies, mentions and welcome messages. Now all of it goes through one queue:
  - **Token bucket** of 50 a minute with bursts of 5, in one sending thread.
  - **Priorities**: cmping and cmcall monitoring alerts and their edits → replies and everything a user started (commands, reactions, mentions, welcome messages, VirusTotal reports) → background posts (auto-kick warnings, deleting used single-use invites). Same priority: arrival order.
  - **Merging**: alert messages are queued per incident (cmcall: per event) and report chat, and the message id is read when the job runs - a first message still waiting is merged with later updates and goes out once, with the latest text, then later updates edit it. Edits of one message and reactions on one message (`⏳` → final) merge the same way.
  - A backlog of 20+ messages is logged once a minute.
- `dc_helpers._edit_or_send()`: edit a message, or send a new one if there is none or the edit fails - one queue job (cmping, cmcall and VirusTotal had this logic three times).

### Changed
- `dc_helpers._send()` queues and returns `None`; `wait=True` waits for the send and returns the msg_id. Used where the id is needed (VirusTotal status message, single-use invites) or a temp file is deleted right after sending (invite QR code, vCard, stickers - the core reads the file when it sends).
- Deleting a used single-use invite for everyone (a message, too) goes through the queue at background priority.

## 2.37.0

### Added
- **`/host` Command**: a short lookup like the `host` tool. `/host chatmail.uk` lists the CNAME it follows (`www.x is an alias for x.`), addresses (`has address`, `has IPv6 address`) and mail servers (`mail is handled by 10 …`, sorted by preference; a null MX shows as "accepts no mail"); `/host 213.165.89.146` gives the reverse name (`… domain name pointer …`). A missing name prints `Host … not found: 3(NXDOMAIN)`, a name without any of these records says so, and a type that failed (e.g. AAAA timed out) is listed. `@1.1.1.1` and `@auth` work as in `/dns`. Asking for a record type (`/host x TXT`) points to `/dns x TXT`.
  - `/host` runs on the `/dns` worker pool and shares its queue limit and 5-minute cache (under its own keys, so `/host` and `/dns` answers for one name do not mix).

## 2.36.0

### Added
- **@Mentions With Notifications**: a group message that starts with `@Nick` (e.g. `@Gluek посмотри?`) is sent again by the bot as a reply to Nick's last message in the chat, under the author's name (`override_sender_name`, shown as `~Alice`, like TG Bridge). Delta Chat has no real mentions; a reply to your own message is what makes the apps notify you, also in a muted chat.
  - The nick is compared, case-insensitively, with each member's name (also without spaces), display name, address and address local part; a prefix of 3+ letters works when only one member fits (`@Gle` for Gleb). Ambiguous or unknown nicks, mentions of yourself or the bot, and messages that already reply to that person are ignored; so are 1:1 chats and channels.
  - The last 500 messages are searched for the person's latest one; without one nothing is sent. Only the text is copied, not attachments. One mention reply per sender every 10 seconds per group; the lookup runs off the event thread. `MENTION_REPLY=0` turns the feature off.
- **Mentions of People Not in the Chat**: if nobody in the group has the nick and Username Bot is a member, the nick is looked up with Username Bot's new `/api/username/<name>` endpoint (`USERNAME_LOOKUP_URL`, default `https://deltachat.id`) and only the author gets a private message with the invite link on `i.delta.chat`, which Delta Chat apps open directly, plus the short link `https://deltachat.id/<name>` to share (person, group or channel). Only an `invite_link` on `https://i.delta.chat/#` is used; with an older Username Bot that has none, the short link alone is sent, so they can write to them or invite them. The bot never messages the mentioned person and posts nothing in the group. Username Bot is recognized by address (`USERNAME_BOT_ADDRS`, default `usernamebot`), not by display name. Only names Username Bot allows (3-32 letters, digits, `_`, `-`) are looked up, not `@all` / `@here`; answers (also "not registered") are cached for an hour, errors are not; the 10-second per-sender cooldown applies. Unknown nicks get no reply.

### Fixed
- **Settings From `.env` Ignored in Docker**: `docker-compose.yml` passes only listed variables to the container, and `IPINFO_TOKEN`, `DNS_RESOLVERS` and `NTFY_BOT_ADDRS` were missing, so values set in `.env` never reached the bot. They are passed now, together with the new `MENTION_REPLY`, `USERNAME_BOT_ADDRS` and `USERNAME_LOOKUP_URL`.

## 2.35.0

### Added
- **New Group (`/newgroup <name>`)**: creates a new group with the bot in it and replies with its join link, like Ntfy Bot's command (without its "Share this link…" line). Without a name it shows the usage. Anyone can use it, with a 1-minute cooldown per sender (admins are exempt) so one user cannot make the bot create many groups.
- **No Double Groups with Ntfy Bot**: in a group where Ntfy Bot is a member, plain `/newgroup` is left to Ntfy Bot; `/newgroup@bouncer` still reaches this bot. Ntfy Bot is recognized by address, not display name (anyone can call themselves "Ntfy Bot"); `NTFY_BOT_ADDRS` takes full addresses or local parts, default `ntfydcbot`, which matches it on every relay.
- **MIT License**: the project is now licensed under MIT (`LICENSE`).

## 2.34.0

- **`/transports` Shows the Relay Actually Used for Sending**: Since core 2.61 the core sends through the relay that last worked and switches only when it cannot connect, so the main address (`configured_addr`) says nothing about where mail goes out. `/transports` now lists relays in the order the core tries them, with the current sending relay first, shows the core's send queue (waiting messages and retries) and outgoing status, and per relay the incoming status, when the last message arrived, mailbox storage usage (⚠️ from 80%) and when it was added. The sending order and queue are read from the core's account database (read-only); the report is built by the shared `transports_view.py`.
- **Removed Misleading Per-Relay Sent/Received Counters**: They credited every message to `configured_addr` (or, in some places, the wrong address), so the numbers and "last sent" dates were wrong once the core sent through another relay. Counting them also cost extra RPC calls per message. The `transport_stats` table is left in place but no longer updated.

## 2.33.1

### Fixed
- **`/dchanneladd` Catalogued the Wrong Chat**: when the bot had joined a channel before (its chat already existed), the join worker found no new chat and fell back to the 1:1 chat with the channel owner, registered that as the channel and reported success - the web preview and RSS stayed empty forever. The worker now uses the chat id returned by `secure_join` (the channel chat itself) and refuses to catalogue a private chat for a group/channel link.
- **Pending Join Reported as Joined**: the bot only becomes a channel member once the owner's device answers the handshake. `/dchanneladd` now checks membership: if the join is not done after 30 seconds it says so, keeps the entry (unlisted) so posts are cached as soon as they arrive, watches for 30 more minutes and reports when the join completes (or that it is still pending). The recent posts that a channel join delivers are backfilled into the web preview once the bot is a member.
- **Re-added Channel Kept Old Visibility**: adding a channel that had been removed from the catalog revived it with its old public flag although the reply said "unlisted"; it now takes the new (unlisted) visibility. A channel that was not removed keeps the visibility the admin set.

## 2.33.0

### Added
- **WHOIS / RDAP (`/whois`)**: `/whois <domain | IP | prefix | AS>`, or reply `/whois` to a message (its first address, AS or link).
  - **Domains, any TLD**: RDAP where the TLD has it (.com, .net, .org, .info, .cc, .xyz, .uk, .app, most new gTLDs - the server comes from IANA's RDAP bootstrap list), classic WHOIS on port 43 otherwise (.ru, .su, .рф, .io, .me, .de, .eu, .co ... - the server named by whois.iana.org); if RDAP is down the port-43 server is tried too. Both are shown in the same fields: registrar, created / updated / expires (⚠️ under 30 days left, ❌ expired), `free-date` for .ru / .рф, status, name servers, DNSSEC, the registrar's abuse contact, and the registrant's organization / country when the registry publishes them ("not public" when redacted). A name the registry does not know is reported as not registered.
  - **Subdomains** are looked up as their registered domain, found with the ICANN section of the Public Suffix List (downloaded daily, a copy kept in `./data/` for when publicsuffix.org is unreachable): `mail.chatmail.uk` -> `chatmail.uk`, `x.example.msk.ru` -> `example.msk.ru`. A TLD or public suffix (`/whois ru`, `/whois co.uk`) shows who runs the zone from IANA's root database.
  - **IP addresses, prefixes and AS numbers** go to the regional registry's RDAP (RIPE NCC, ARIN, APNIC, LACNIC, AFRINIC): block and its name, type, holder (the registrant, not an admin contact), country, dates and the **abuse contact** - where to report an address (ipinfo has this only on Enterprise).
  - Registries such as tcinet.ru and DENIC block clients that query too often, so one server is asked at most every 5 seconds (different servers in parallel); three lookups run at a time, the rest wait in a queue (up to 50); answers are cached for an hour.
- **`/dig`**: alias of `/dns`.

### Changed
- **Commands Work In Any Case**: `/DNS`, `/Ip`, `/HELP`, `/WhoIs` ... now work like their lower-case form - deltachat2 matched the command word exactly. Only the command word is compared case-insensitively; the arguments stay as typed.
- `/ip`, `/dns` and `/whois` point to each other in their replies.

## 2.32.2

### Fixed
- **Every CMPing Check Failed With `TypeError: sequence item 0: expected str instance, NoneType found`**: the bundled `cmping` read the account address via `get_config("addr")`, which returns nothing on core 2.61+ (multi-transport). `cmping` is bumped to a build that reads `configured_addr` first.

## 2.32.1
- Upstream update to version 2.32.1.

## 2.32.0

### Added
- **DNS Lookup (`/dns`)**: dig-like syntax with arguments in any order - `/dns <domain> [TYPE] [@server|@auth]`.
  - `/dns chatmail.uk` - **full report**: addresses with reverse DNS; zone name servers (found at the zone apex, so `nine.testrun.org` shows `testrun.org`'s), DNSSEC (DS in the parent), CAA grouped by tag; and for a mail domain: MX hosts with forward-confirmed reverse DNS (PTR resolving back to the same address - big providers reject mail without it), SPF (exactly one record, the `all` policy, whether `a` / `mx` / `ip4` / `ip6` / `a:` cover the MX addresses; `include` / `redirect` are named, not expanded), DKIM at common selectors with key type and size, DMARC policy and alignment, MTA-STS (the policy is fetched from `https://mta-sts.<domain>/.well-known/mta-sts.txt` and its `mx:` lines checked against the real MX hosts), TLS-RPT and client SRV records. Null MX and domains without MX are recognized.
  - **Chatmail relays** (MX = the domain itself and a DKIM key at selector `opendkim`) also get the records `cmdeploy dns` expects: required (A/AAAA, MX, `_mta-sts` TXT, `mta-sts` and `www` CNAME, DKIM, MTA-STS policy `enforce` listing the domain) and recommended (SPF, DMARC `p=reject; adkim=s; aspf=s`, CAA `letsencrypt.org`, `_adsp`, the four SRV records), as counts with what is missing. Other domains don't get this block.
  - `/dns chatmail.uk MX` - one record type with TTL and CNAME chain; `/dns 213.165.89.146` - reverse DNS (PTR). Types: A, AAAA, CNAME, MX, NS, TXT, SOA, CAA, SRV, PTR, DS, DNSKEY, TLSA, HTTPS, SVCB; `ANY` is refused (RFC 8482).
  - `@1.1.1.1` / `@dns.google` asks that resolver (public addresses only); `@auth` asks the zone's authoritative name server, bypassing caches - as `cmdeploy` does - e.g. right after changing records.
  - Reports run three at a time and the rest wait in a queue (up to 50, a spam guard); answers are cached for 5 minutes. The MTA-STS policy request goes only to a public address (checked before connecting, then pinned), without redirects, at most 64 KB.
- **`dnspython`** is now an explicit dependency (it was already installed by aiortc).

### Changed
- **`/ip`**: host names from reverse DNS are shown in Unicode (`кц.рф` rather than `xn--j1ay.xn--p1ai`); a host name lookup ends with a `/dns <name>` hint, and `/dns` reports with an `/ip` hint.

## 2.31.0

### Added
- **Host Names in `/ip`**: `/ip chatmail.uk` (also a link like `/ip https://delta.chat/en/`, `host:port`, or an internationalized name like `пример.рф`) resolves the name with the bot's DNS and runs the full IP lookup on its first public address - IPv4 first, since Shodan rarely scans IPv6. The other addresses are listed on an "also:" line to check separately. When the name points to a CDN (Cloudflare, Akamai, Fastly, CDN77, Imperva, or Shodan's `cdn` tag) the reply says that this is the CDN's address, not the real server. Replying `/ip` to a message now falls back to the host of its first link when there is no IP address, block or AS in it; bare words with dots ("v2.0") and e-mail addresses are not taken for names. Names resolving only to private addresses, or not at all, get a clear error.

## 2.30.0

### Added
- **Open Ports in `/ip`**: IP lookups now also show what Shodan InternetDB (free, no key) knows about the address: open ports with service names (`22 SSH`, `443 HTTPS`, `1194 OpenVPN`, ...), software from CPEs (`nginx 1.18.0`), Shodan tags (`tor`, `vpn`, `proxy`, `cloud`, `self-signed` ...), known CVEs by software version, and the host names Shodan saw when ipinfo has none. Two hint lines: **VPN / proxy / Tor ports** (IPsec, OpenVPN, L2TP, PPTP, WireGuard, SOCKS, HTTP proxy, Shadowsocks, Tor) and **router management ports** (TR-069, MikroTik Winbox, UPnP - a home / office router). These are hints, not verdicts: the data is a snapshot of Shodan's periodic scans (can be weeks old and miss ports), only shows servers on the address itself - a VPN user's own address looks like any home connection - and IPv6 is rarely scanned. A link to the Shodan host page is added when ports were found.

## 2.29.0

### Added
- **IP / Network / AS Lookup (`/ip`)**: `/ip <address>`, `/ip <prefix>` (e.g. `84.64.0.0/13`) or `/ip AS<number>` (also `/ip 5378`). Reply `/ip` to a message to check the first public IP address, block or AS number in it - a log line like `10.0.0.5 -> 84.65.49.143` gives the public one. An IP shows city / region / country, organization and AS, host name, time zone and its announced BGP prefix; a block shows the announcing AS (or the bigger announced prefix it belongs to), more specific announcements, country and registry allocation; an AS shows holder, country and its announced prefixes, largest first. Links to the matching ipinfo.io pages are included. Data: ipinfo.io for IPs, RIPEstat (free, no key, global BGP data) for prefixes and AS numbers - ipinfo's ASN and IP-range APIs are paid only.
- **`IPINFO_TOKEN`** (optional, `.env`): tried first for IP lookups, then no token, then the free Lite API (country + AS, unlimited). ipinfo's current free token only gives country-level data, so the tokenless endpoint (city level, rate-limited) stays in use; a paid token adds VPN / proxy / Tor / hosting flags.
- Available to everyone with one global queue: one lookup every 15 seconds (both services rate-limit the bot's IP), at most 5 waiting - more are refused with "try again in a minute". Answers are cached for an hour and a cached answer is sent right away.

## 2.28.0

### Added
- **Group FAQ (`/faq`, `/save`, `/remove`)**: The FAQ Bot's features, built in. Reply to a message with `/save <topic>` to make it the answer to a topic; sending the topic name (case-insensitive) gets the answer, as a reply to the person the question replied to if any. `{faq}` and `{name}` placeholders work as in the FAQ Bot. Additions: `/faq <topic>` shows one answer; only the topic's author or the bot admin can overwrite or remove it; the same topic (and the `/faq` list) is answered at most once per 30 s per chat (admin exempt); topics can't start with `/`. Answers are copies - text in the database (`faq_entries`), attachments downloaded on demand and kept in `./data/faq/` (up to 25 MB) - so they survive the 36-hour message cleanup.
- **FAQ Bot Coexistence**: While a FAQ Bot (a member with the bot flag and "FAQ" in its name) is in the group, Bouncer does not answer FAQ commands or topics, so nothing is answered twice, but mirrors `/save` and `/remove` silently; once the FAQ Bot is removed (detected within a minute) its topics saved in the meantime work right away. `/faq@boun` is always answered.

## 2.27.0

### Added
- **Channel Name & Avatar Follow Delta Chat**: When a channel owner renames the channel or changes its picture, the bot now picks it up on its own - the catalog (`/dchannels`), web preview, RSS feed and Fediverse actor show the new name, and the cached avatar is replaced (or dropped, so the default is shown, if the picture was removed). Triggered by the channel's "name changed" / "image changed" system message, and re-checked on every new post as a safety net in case that message was missed. Previously the name was frozen at the time the channel was added and the avatar was cached forever.

### Fixed
- **`/dchanneldesc<ID>`**: The database function it relies on (`update_catalog_channel_description`) was missing, so the command failed; added.

## 2.26.1

### Fixed
- **Call Checks Failing At ICE**: cmcall 0.1.4 (shipped in 2.24.1) broke every call through a TURN relay - its closed-socket guard called `is_closing()` on aioice's `TurnTransport`, which has no such method, so no ICE connectivity check was ever sent and all CMCall monitor / `/cmcall` runs failed with "ICE/DTLS did not connect". Updated to cmcall 0.1.5, which fixes the guard.

## 2.26.0

### Changed
- **Echo Call Greeting Is Your Tune**: The bot now greets an echo call with the caller's own 5-note fingerprint tune - the same one `/join` plays when you enter a meeting (derived from your key fingerprint, so it is identical in every call and meeting). The old two-tone greeting remains as a fallback if the caller is unknown or the tune can't be built. The tune logic moved to `meet.contact_tune()`, shared by meetings and echo calls.

## 2.25.0

### Added
- **Callers' TURN Server in Echo Reports**: The bot reads the relay candidates of the caller's offer and those trickled in later (their address is the TURN server's), names them by forward DNS of the TURN hosts it knows (`turn.delta.chat`, its relays, the monitored relays, `CALL_TURN_HOSTS`; cached for an hour) and reports `Your app's TURN server: … ✅`, or that the app got no relay address — its TURN server is blocked or unreachable — with a link to the test page. Stored per call (`caller_turn`, plus the caller's address domain); the admin's `/callstats` shows a 7-day summary per TURN server and which domains got none, and the TURN server per recent call.
- **`/test-turn` Page**: A browser self-test (Russian/English): relay allocation on `turn.delta.chat` over UDP and TCP, and STUN reachability of the TURN servers the bot's relays announce, with a verdict (works / UDP blocked / unreachable). Runs entirely in the visitor's browser; nothing is reported back. `TURN_TEST_PAGE=0` turns it off.

## 2.24.1

### Fixed
- **Traceback after Failed Calls**: `cmcall` 0.1.4. When a call ended while aioice was still retransmitting an unanswered STUN request (the bot's query to its relay's STUN/TURN server), the retry hit the closed socket ~30 s later and asyncio logged `Exception in callback Transaction.__retry()` with an `AttributeError` traceback. Harmless, now silent.

## 2.24.0

### Added
- **Meeting Radio**: `/radio` lists the stations, `/radio <number>` plays one quietly under the conversation of this chat's meeting, `/radio 0` / `/radio off` stops it. The admin manages the list with `/radioadd <url> [name]` (http(s) streams only; the stream is played for a moment before it is added, and its `icy-name` becomes the default name) and `/radiodel <number>`; stations keep their numbers. Anyone who can use the room controls it (group rooms: the group's members).
- **`/play`**: Reply `/play` to an audio or video message (or use it as the caption) to play its sound once in this chat's meeting; videos contribute their audio track only. The radio pauses for it and comes back afterwards; `/play off` stops the file.
- **Ducking**: Background audio plays at `MEET_MUSIC_VOLUME` (0.35) and drops to `MEET_MUSIC_DUCK` (0.3) of that while someone talks (fast down, slow up). Everyone hears it, the speaker included.
- **`meet_media.py`**: Decoding (PyAV) in its own thread with a 0.5 s queue as the clock; files pause and radio stations drop their connection (after 10 s) while nobody is in the meeting; stations reconnect with back-off. ffmpeg runs with protocol and format whitelists (streams: http/https, files: local file only; audio/video formats only), so crafted files or playlists cannot read local files or fetch other URLs.

## 2.23.0

### Security
- **Meetings Belong to Their Chat**: A room is bound to the chat `/meet` was sent in. Before, an open room belonged to its creator, and `/meet` in any other chat replied with the existing `/join_<id>` link, leaking a meeting meant for one group into another. Now `/meet` in the room's chat shows its link again, and in any other chat the creator is only told to close their open meeting first.
- **Group Rooms for Members Only**: Rooms started in a group can only be joined by that group's members: checked on `/join`, on calls back into the room and every 30 s during the meeting (people who left or were removed drop out with a notice). Rooms started in a private chat with the bot stay open to whoever has the link. Meetings can no longer be started in channels or mailing lists.

### Added
- **`/meetclose` and `/meetnew`**: The creator (in the room's chat or privately) can close their meeting, or restart it with a new link when the old one leaked; the new link is posted only in the room's chat and disconnected participants are not sent it. The admin can do both for any room and close one by id or 4-character prefix from `/meets` (`/meetclose <id>`), e.g. when a slot is needed.
- **Invitations for Private Rooms**: `/meet` in a private chat also sends a message made for forwarding: the bot's invite link plus the `/join_<id>` command. Group rooms suggest *Reply Privately* to keep `/join` commands out of the group.

## 2.22.0

### Changed
- **`/stickernobg` at Idle CPU Priority**: The background-removal subprocess (`sticker_tool.py`) switches itself to Linux `SCHED_IDLE` (fallback: nice 19) before loading onnxruntime, whose worker threads inherit it. It now only gets CPU time nothing else wants, so it can no longer make voice meetings or echo calls stutter. `REMBG_PRIORITY=normal` restores the old behaviour.

### Fixed
- **`tests/bench_meet.py` Hung Above 8 Participants**: The benchmark used the bot's meeting limits, so the 9th participant was refused and the clients waited forever. It now raises `MEET_TOTAL_SLOTS` / `MEET_MAX_PARTICIPANTS` to the participant count, gives up after 30 s without an answer and shows progress when piped.

## 2.21.0

### Added
- **Join Tunes in Voice Meetings**: Instead of the same two tones for everybody, each participant is announced with their own 5-note tune (C major pentatonic, C4–A5, soft decaying bell tone, ~0.85 s) picked by a salted SHA-256 hash of their key fingerprint, falling back to their address. It is the same in every meeting, so people can tell by ear who joined; leaving plays it backwards. The newcomer hears their own tune too, and `/meet` / `/join` show it as note names (e.g. `E4 C5 A4 D5 G4`).

### Changed
- **Tunes No Longer Interrupt the Conversation**: Join/leave sounds are mixed on top of the meeting audio; before, the mix was dropped while a sound played.

## 2.20.0

### Added
- **Voice Meetings (prototype, off by default)**: `/meet` creates a room (12-character base62 id) and replies with `/join_<id>`; `/join_<id>` / `/join <id>` makes the bot call you into it (via `place_outgoing_call` + `OutgoingCallAccepted`), and while the room is open an incoming call from someone who joined goes into the room instead of the echo. The bot is the hub of a star of 1:1 calls and mixes every 20 ms: noise gate with 300 ms hold, participants whose app reports `mutedState` muted are left out, each one hears the others (mix-minus). Join/leave are announced with the echo greeting's tones (330→440 Hz / 440→330 Hz). Rooms close 60 min after the last person left (`MEET_IDLE_MINUTES`), at most `MEET_MAX_HOURS` (6) after creation, and live in memory only. Every room and join message says that the bot does not record voices, that meetings are not end-to-end encrypted between participants and that participants can record.
- **Capacity Budget**: `MEET_TOTAL_SLOTS` (8) places across at most `MEET_MAX_ROOMS` (2) rooms: one room of 8, or two of 4; a second room is refused while the first has more than 4 people. `MEET_MAX_PARTICIPANTS`, `MEET_RING_SECONDS`, `MEET_MAX_ROOMS_PER_USER` (1).
- **Admin Switch**: `/meets on|off` (or `1|0`); `off` closes all rooms. `/meets` shows the status and open rooms. Off by default because every participant costs ~10 % of a core (8 participants ≈ 0.7–0.9 core, ~95 MB; `tests/bench_meet.py`).
- **Dependencies**: `cmcall` 0.1.3 (`EchoPeer` with own outgoing track, audio callback, `mutedState` callback and outgoing calls).

## 2.19.2

### Fixed
- **False "media connection dropped" After a Normal Hangup**: Hanging up closes the caller's media within ~0.1 s, but the "call ended" message reaches the bot through the relays a second or more later. The watchdog saw the closed connection first and reported `⚠️ The media connection dropped during the call.` for ordinary hangups. It now waits up to 15 s for the hangup message before reporting a drop, and call durations end when the media stopped rather than when the hangup message arrived.

## 2.19.1

### Privacy
- **Caller IP Addresses No Longer Logged**: aioice logs every ICE candidate pair it checks at INFO level, so the container logs kept the IP addresses of everyone who called the echo service. aiortc/aioice now log at WARNING; `CALL_DEBUG_LOG=1` restores INFO for troubleshooting.
- **Call Message Deleted After the Call**: The incoming call message carries the caller's SDP offer with their ICE candidates (local and public IPs). The bot now deletes it as soon as the call ends instead of keeping it for 36 h (`delete_device_after`).
- **Call Statistics Retention**: New `CALL_ECHO_LOG_DAYS` (default 30): `call_echo_log` rows older than that are deleted (at start, after each call and on `/callstats`); `0` keeps no call history at all.
- **Privacy Notes**: `/callstats` and `/help` state that calls are not recorded and how long statistics are kept; new "Echo Call Privacy" section in the README.

## 2.19.0

### Changed
- **Echo Calls Can Connect Peer-to-Peer**: The bot runs behind NAT (Docker bridge) and chatmail relays announce only a TURN server, so its only reachable ICE candidate was the TURN relay and every echo call went through TURN. The Delta Chat apps avoid this because libwebrtc also queries the TURN server as STUN; aiortc does not. New `CALL_ECHO_STUN` (default `auto`) does the same, giving the bot a server-reflexive candidate so calls can connect peer-to-peer through the NAT, with TURN as fallback. `off` restores TURN-only, or set an explicit `host:port`. The `Path:` line of the call report now reflects the caller's network rather than the bot's limitation.
- **Dependencies**: `cmcall` 0.1.2 (`turn_as_stun`). `/cmcall` and call monitoring still test TURN only.

## 2.18.0

### Added
- **Call Monitoring Between Relays**: A second monitor next to cmping, over the same server list (bot transports + `/cmpingadd`, minus `/cmcallskip`). Every `CMCALL_MONITOR_INTERVAL` seconds (default 3600, `0` disables) a round-robin source relay calls every other relay with `cmcall --json` (TURN-only media, `CMCALL_MONITOR_DURATION` = 5 s of audio). One call per pair, direction alternating per cycle; a lone relay calls itself. Hard failures are retried once; if the source fails with all of ≥ 2 targets the source is blamed, otherwise the failing target. Packet loss ≥ `CMCALL_DEGRADED_LOSS_PCT` (10 %) in two checks in a row marks a relay degraded; relays announcing no TURN server are `n/a` and never alert. Monitoring and `/cmcall` share one lock, since they use the same cmcall test profiles.
- **Call Alerts**: Each failing/degraded episode is one `📞🚨 Calls failing` / `📞⚠️ Calls degraded` message per `/cmreport` chat, edited in place when the error changes and when it resolves (`📞✅ Calls restored`).
- **Commands**: `/cmcallstatus [server]`, `/cmcallhistory [server]`, `/cmcallskip [server]` and `/cmcallunskip <server>` (admin). `/cmpinglist` shows a call badge per server.
- New tables `cmcall_results`, `cmcall_servers`, `cmcall_skip`, `cmcall_events`, `cmcall_event_messages`.

## 2.16.0

### Removed
- **Bot-Side Relay Failover**: Removed the `MSG_FAILED` failover handler and the resilient-send `send_msg` patch. Both switched `configured_addr` and called `resend_messages`, but since Delta Chat core 2.61 the SMTP relay is no longer chosen by `configured_addr`: the core tries the newest relay first and falls back to the next one if a relay is unreachable. The old logic could no longer switch relays and only caused delayed duplicate resends.

### Changed
- **`/setprimary` and `/resilient` Deprecated**: Both commands are disabled and only reply with an explanation of how the core picks relays now. They are removed from `/help` and the README.
- **`/transports` Sending Order**: Relays are listed newest first, in the order the core tries them for sending, instead of marking `configured_addr` as "Used for sending".
- **Core Requirement**: `requirements.txt` now requires `deltachat-rpc-server>=2.62.0`.

## 2.15.3

### Fixed
- **`update.sh` Deployed the Wrong Branch**: Branch detection took the first remote branch in alphabetical order, so a leftover PR branch such as `origin/claude/...` sorted before `origin/master` and was deployed instead (and new `master` commits were reported as "Already up to date"). It now follows the checked-out branch, falling back to `main`/`master`.

## 2.14.7

### UI & Branding Improvements
- **Delta Chat Identity Icon**:
  - Replaced the custom broadcast-tower SVG with the official Delta Chat `identity.svg` icon for the default channel avatar (shown when a channel has no avatar set).
  - Added `/icon.svg` route serving the same Delta Chat identity SVG, used as the browser tab favicon (`<link rel="icon" type="image/svg+xml">`) across all web pages (landing, tombstone, 404). PNG favicon retained as fallback.
- **Light Theme Background**:
  - Replaced the previous small `background-light.png` (772×744) with the official i.delta.chat colorful doodle wallpaper (`background-light.jpg`, 860×1345), matching the dimensions of the dark-mode background for consistent tile sizing across themes.

## 2.14.6

### UI & Theming Improvements
- **Direct Bot Invite Link on Landing Page**:
  - The hero CTA button on the landing page now links directly to the bot's Delta Chat invite link (`i.delta.chat`) with speech bubble icon `🗨️` ("Add Bot to Delta Chat"), streamlining onboarding.
  - The QR modal remains instantly accessible via the `📱 QR Code` button in the top navigation header.
- **Fixed Light Theme Modal Overlay & Dialog Styling**:
  - Removed solid white override (`background: #ffffff !important;`) on `.modal` which was washing out the entire viewport on light theme.
  - Configured high-contrast translucent darkened backdrop with blur (`background: rgba(17, 27, 33, 0.55); backdrop-filter: blur(6px);`) across light mode on landing and preview pages, providing depth and focus.
  - Enhanced modal dialog card (`.modal-content`) with refined drop shadow (`0 20px 48px rgba(0, 0, 0, 0.22)`), rounded corners (`16px`), styled QR image frame, and modern neutral action buttons (`.close-btn`).

## 2.14.5

### UI & Theming Enhancements
- **Light / Dark / System Theme Switcher**:
  - Implemented an elegant 3-way theme switcher (Light ☀️, Dark 🌙, System 💻) across all web pages (landing page, channel previews, tombstone, and 404 pages), matching the design and behavior of `gluek.info`.
  - Added inline head preload script (`_THEME_PRELOAD_SCRIPT`) reading `localStorage.theme` with fallback to system preference, completely eliminating Flash of Unstyled Content (FOUC).
  - Added zero-latency transition suppression during theme switches to prevent sluggish background or text transition artifacts.
  - Implemented dynamic system preference listeners (`matchMedia("(prefers-color-scheme: dark)")`) updating the page in real-time when in System mode.
- **Fixed Feature Card Headings in Light Theme**:
  - Fixed white-on-white text in Core Capabilities cards (`.feature-text h3`) by binding heading colors to `var(--text-main)` with explicit light theme color `#111b21`.
  - Ensured code pills, tables, hero text, and subtitle colors have crisp high-contrast styling in both dark and light modes.

## 2.14.4

### Improvements & Bug Fixes
- **Dedicated Channel Avatar Placeholder (`channel-default.svg`)**:
  - Channels without an avatar now render a dedicated broadcast channel SVG icon instead of falling back to the bot's own avatar (`icon.png`).
- **Robust Delta Chat Channel Avatar Extraction**:
  - Fixed channel avatar retrieval across Delta Chat Rust core by checking both camelCase (`profileImage`) and snake_case (`profile_image`) in `get_basic_chat_info`, `get_full_chat_by_id`, and channel contacts.
- **Dynamic Bot Avatar Customization (`AVATAR_PATH`)**:
  - Bot web endpoints (`/icon.png`, `/{AVATAR_PATH}`) now dynamically serve custom bot avatars configured via `AVATAR_PATH`, Delta Chat `selfavatar`, or `bot_avatar_path` in SQLite.
- **Accurate MIME Type Delivery (WebP & Media)**:
  - Added deterministic MIME type headers (`image/webp`, `image/jpeg`, `image/png`, `video/mp4`, etc.) and magic header sniffing across all media and avatar handlers, ensuring browsers display WebP images inline rather than downloading them as generic `application/octet-stream`.
- **Channel Preview CTA Emoji Update**:
  - Replaced airplane `✈️` with speech bubble `🗨️` in "Open in Delta Chat" and fallback buttons.

## 2.14.3

### UI & Theming Enhancements
- **Delta Chat Client Native Light Theme**:
  - Aligned light theme primary button colors to Delta Chat client styling (`#415e6b`, hover `#354e59`) across landing, channel preview, tombstone, and 404 pages.
  - Added official Delta Chat light doodle wallpaper (`/background-light.png` and `/static/background-light.png`), rendered with zero-repaint fixed `body::before` architecture.
- **Landing Page Header & Hero Redesign**:
  - Replaced bot logo and generic title in the top navigation header with the instance URL domain (e.g. `dc.gluek.info`).
  - Added quick `📱 QR Code` modal launcher in the top header replacing the GitHub link (code repository links remain accessible in the footer).
  - Promoted bot branding to hero badge (`🛡️ Delta Chat Bouncer Bot`).
  - Added seamless `Copy Link` clipboard action button in landing page QR modal with inline `✓ Copied!` visual feedback.

## 2.14.2

### Performance & Memory Optimization
- **Isolated Subprocess Execution for Background Removal (`sticker_tool.py`)**:
  - Offloaded AI background removal (`rembg`) to a standalone, short-lived subprocess (`sticker_tool.py`).
  - Completely prevents the main `bot.py` daemon process from importing heavy scientific and machine learning libraries (`onnxruntime`, `scipy`, `numpy`, `pymatting`).
  - Preserves baseline memory of `deltachat_bouncer` at **~75–80 MB** permanently.
  - Upon completion of `/stickernobg`, the operating system kernel immediately and unconditionally reclaims 100% of memory allocated during inference.
- **Disabled ONNX Memory Arena Bloat**:
  - Configured `SessionOptions` in `sticker_tool.py` with `enable_cpu_mem_arena = False`, `enable_mem_pattern = False`, and `intra_op_num_threads = 2`.
  - Cuts peak memory usage during the 2–3 seconds of subprocess execution from >700 MB down to **~250 MB**.

## 2.14.1

### Performance & Optimization
- **Sticker Pre-Scaling Before Matting**:
  - Automatically downscale input images to max 512px *before* feeding them into `rembg` neural network matting.
  - Reduces CPU and RAM consumption by over 90% when users submit multi-megapixel smartphone photos (12–48 MP), cutting processing time down to under a second.
- **Lightweight Model Default (`u2netp`)**:
  - Switched default `rembg` model from the heavy `bria-rmbg-2.0` (~1.02 GB download) to `u2netp` (**only 4.7 MB**).
  - Configurable via `REMBG_MODEL` environment variable (defaults to `u2netp`).
- **Persistent Model Cache Storage**:
  - Configured `U2NET_HOME` and `REMBG_HOME` pointing to `/app/data/u2net` (`./data/u2net` on the host).
  - Models are downloaded exactly once and persist across container restarts, rebuilds, and updates.
- **Optional Background Removal (`ENABLE_REMBG`)**:
  - Background removal can be completely disabled for resource-constrained hosts via `ENABLE_REMBG=false`.
- **Global Concurrency Lock & Dedicated Cooldown**:
  - Added global concurrency lock (`_rembg_global_lock`) ensuring only one background removal runs at a time across the bot.
  - Split cooldowns: 5 seconds for `/sticker` and 15 seconds for `/stickernobg` with independent anti-spam tracking.

### Bug Fixes
- **Virus Command Attachment Detection**:
  - Added strict type checking (`isinstance(..., (str, int))`) for `view_type` and `download_state` to prevent false positive attachment detections in unit tests.

## 2.14.0

### Features
- **Sticker Generation (`/sticker` & `/stickernobg`)**:
  - Convert any attached or replied image into a WebP sticker formatted to standard 512px dimensions compatible with Delta Chat, Telegram, and Signal.
  - `/sticker`: Generates a sticker preserving the original image and background.
  - `/stickernobg`: Generates a sticker with background removed via `rembg` (also accepts `/sticker nobg` or `/sticker --nobg`).
  - Supports invocation as a reply/quote to an image message or as the caption of a newly sent image.
  - Automatic EXIF orientation transpose (`ImageOps.exif_transpose`) to keep smartphone photos correctly oriented.
  - Non-blocking asynchronous worker thread with immediate `⏳` acknowledgment and `☑️`/`❌` reaction updates.
  - Independent 5-second anti-spam cooldown per chat with automatic delayed execution queuing.
  - Graceful degradation when `rembg` is not installed, recommending `/sticker` as a fallback.

### Dependencies & Containerization
- Added `rembg[cpu]>=2.0.50` to `requirements.txt` and relaxed `pillow>=10.4.0`.
- Added `libgomp1` to Debian package dependencies in `Dockerfile` for ONNX Runtime CPU inference support.

## 2.13.2

### Security & Hardening
- **Rate Limiting on All Public Web Endpoints** (`#5`):
  - Extended `@rate_limited` decorator coverage to every public-facing HTTP handler: `handle_icon`, `handle_background`, `handle_index`, `handle_qr_svg`, `handle_qr_png`, `handle_channel_qr_png`, `handle_channel_qr_svg`, `handle_channel_avatar`, `handle_channel_rss`, `handle_media_file`, `handle_ap_actor`, `handle_ap_outbox`, `handle_ap_followers`, `handle_ap_following`, `handle_ap_post`, `handle_webfinger`, `handle_nodeinfo_discovery`, `handle_nodeinfo`, `handle_api_v1_instance`.
  - Removed duplicate inline `check_rate_limit` calls from previously partially-protected handlers.
- **Trusted Proxy IP Extraction** (`#7`):
  - Added `_get_client_ip()` function: only honours `X-Forwarded-For` when the direct peer IP belongs to a trusted local reverse proxy (`127.0.0.1`, `::1`, `localhost`), preventing IP spoofing by external clients.
  - Added `_TRUSTED_PROXIES` set for configurable trusted proxy list.
- **ActivityPub Key Ownership Verification** (`#8`):
  - Added `is_key_owned_by_actor(key_id, key_doc, actor)` function in `activitypub.py` to verify that a resolved signing public key actually belongs to the claiming actor (via `owner`, embedded publicKey, actor `id`/`url` matching, or key URI fragment).
  - Integrated ownership check into `handle_ap_inbox()` after successful key resolution; rejects requests where the key's declared owner does not match the activity actor with HTTP 401.
- **Caddy X-Forwarded-Proto Header** (`#6`):
  - Added `header_up X-Forwarded-Proto {scheme}` to `Caddyfile` reverse proxy configuration so the upstream application can reliably detect HTTPS.

### Bounded Memory & SQL Queries
- **Bounded `_qr_cache`** (`#1`): Capped QR code cache at 200 items with FIFO eviction.
- **Bounded `_cmping_server_status`/`_cmping_server_errors`** (`#4`): Added `_set_cmping_server_status()` helper capping those dicts at 500 entries.
- **Bounded SQL Queries** (`#3`):
  - `get_all_cmping_results()` now adds `ORDER BY checked_at DESC LIMIT ?` (default 500).
  - `get_cmping_incident_downtime_events()` now adds `LIMIT ?` (default 500).

### Performance & Debug
- **Guarded Debug Logging** (`#2`): Wrapped hot-path `logger.debug()` calls with `logger.isEnabledFor(logging.DEBUG)` guards to avoid f-string evaluation overhead when debug is off.

### Web & Accessibility
- **QR Modal Focus Trap** (`#9`):
  - Added `openQrModal()` / `closeQrModal()` JS functions to both landing page and channel preview page that capture the opener button's focus, move focus into the modal on open, trap Tab/Shift-Tab within modal focusable elements, and restore focus on close.
  - Pressing Escape now correctly calls `closeQrModal()` and returns focus.
- **Inline Copy Feedback on QR Modal** (`#10`):
  - Replaced `alert('Link copied to clipboard!')` with inline `✓ Copied!` button-text feedback via new `copyJoinLink()` function; reverts after 2 seconds without blocking the page.
- **RSS Language Tag Removed** (`#13`):
  - Removed hardcoded `<language>en</language>` tag from RSS channel XML, since channel content language is user-determined.

## 2.13.1

### Security & Hardening
- **Restricted Database File Permissions**:
  - Enforced POSIX `0o600` permissions on the primary SQLite database file and WAL sidecars (`-wal`, `-shm`) during database initialization and connection setup, protecting stored plaintext ActivityPub private keys and configuration data.
- **Strict Static Asset Whitelisting**:
  - Restricted `handle_icon` and `handle_background` to explicit filename allowlists (`_ALLOWED_ICON_FILENAMES`, `_ALLOWED_BG_FILENAMES`) to prevent unauthorized file access or path disclosure.
- **ActivityPub Foreign Target Inbox Validation & Backfill Rate Limiting**:
  - Enforced host matching between the follower actor URI and target delivery inbox URI in `handle_ap_inbox()`, rejecting delivery and backfill attempts to foreign/victim inboxes.
  - Added concurrency throttling (`asyncio.Semaphore(2)`) and a 10-second per-channel cooldown to follower post backfilling to prevent inbox bombing and outbound resource exhaustion.
- **RSS CDATA Breakout Prevention**:
  - Implemented `_escape_cdata()` to escape `]]>` sequences into `]]]]><![CDATA[>` across channel titles, descriptions, and post contents in RSS XML generation, preventing feed breakage and malformed XML.

### Bug Fixes & API Consistency
- **Mastodon/Pleroma `GET /api/v1/instance` Admin Email Resolution**:
  - Fixed configuration key lookup in `handle_api_v1_instance()` to check `admin_dc_email` prior to `admin_email`, accurately returning the bot administrator's contact email.

### Web & RSS Polish
- **Per-Post Permalinks & HTML Anchors**:
  - Added unique per-post permalink URIs (`<link>` and `<guid isPermaLink="true">` with `#post-{msg_id}`) to RSS 2.0 items and matching `id="post-{msg_id}"` anchor attributes to web preview articles for direct message linking.
- **Zero-Repaint Background Rendering**:
  - Replaced `background-attachment: fixed` with a fixed pseudo-element (`body::before`) across landing, preview, and error page templates, eliminating high scrolling repaint costs.
- **Responsive Layout & Accessibility Polish**:
  - Improved channel grid layout responsiveness on small viewports (<340px) using `minmax(min(280px, 100%), 1fr)`.
  - Upgraded `--text-muted` color to `#aebac1` achieving WCAG AA contrast ratio (>4.5:1).
  - Added `@media (prefers-color-scheme: light)` support for automated light theme rendering across landing and preview pages.

## 2.13.0

### Security & Hardening
- **Environment File Gitignore (`S4`)**:
  - Added `.env` to `.gitignore` to prevent accidental credential, token, and API key exposure while retaining `.env.example`.
- **Host Header & Base-URL Poisoning Protection (`S5`)**:
  - Validated incoming `X-Forwarded-Host` and `Host` headers in `_get_base_url()` against strict URL scheme and hostname syntax rules (`SAFE_HOST_REGEX`), preventing cache and link poisoning when `BASE_URL` is unset.
  - Added `header_up Host {host}` and `header_up X-Forwarded-Host {host}` to `Caddyfile` reverse proxy configuration.
- **ActivityPub Replay Prevention & KeyId/Actor Binding (`S6`)**:
  - Implemented 300s TTL HTTP signature anti-replay cache (`check_and_record_signature_replay()`) in `activitypub.py` tracking signature digests.
  - Enforced strict origin matching between signing `keyId` URI and activity `actor` URI in `handle_ap_inbox()`, rejecting spoofed cross-origin signatures.

### UI & UX Improvements
- **Independent Command Cooldowns (`U5`)**:
  - Decoupled cooldown state tracking into separate dictionaries (`_chat_bounce_anti_spam`, `_chat_top_anti_spam`, `_chat_invite_anti_spam`) so executing `/bounce`, `/top`, or `/invite` never blocks another command.
- **Safe Bare `/away` Query (`U6`)**:
  - Invoking bare `/away` without arguments now safely displays the user's current away status or usage instructions without inadvertently clearing away state or sending `_is back_` notifications.
- **Community Multi-Chat Age Indicators (`U7`)**:
  - Replaced circle emojis with colored squares (`🟥🟧🟨🟩🟦🟪🟫⬛⬜`) for contacts who are active across multiple community chats, visually distinguishing experienced community members.
  - Streamlined new member welcome greetings by removing redundant `(💬 X)` tokens.
- **Social Media Metadata for Web Previews (`U8`)**:
  - Added OpenGraph (`og:title`, `og:description`, `og:image`, `og:type`) and Twitter Card (`twitter:card`) meta tags to the channel directory landing page.
- **Accurate RSS Enclosure Sizes (`U9`)**:
  - Resolved true file byte sizes on disk or in-memory buffers for `<enclosure length="...">` attributes in `generate_rss_xml()`, replacing placeholder zero values.
- **Accessible QR Code Modals (`U10`)**:
  - Added ARIA accessibility attributes (`role="dialog"`, `aria-modal="true"`, `aria-labelledby="qr-modal-title"`) and ESC key event listener to QR join modals across landing and channel preview pages.
- **Dynamic Fediverse Domain Resolution (`U11`)**:
  - Resolved Fediverse domain dynamically from server configuration without hardcoded `dc.gluek.info` fallbacks, hiding the Fediverse button gracefully if no public domain is configured.
- **Whole-Word Away Mention Matching (`U12`)**:
  - Replaced substring matching in group mention detection with word-boundary regex (`(?i)(?<!\w)name(?!\w)`), eliminating false positive away alerts (e.g. "Dan" matching "Daniel").
- **Command Documentation Clarifications (`U13`, `U14`)**:
  - Updated `/help` descriptions: `/contact<ID>` clearly indicates sharing a contact card, and `/relays` accurately reflects scanning for public Russian mail providers.
- **Role and Status Badges (`U15`)**:
  - Added visual user badges in `/search` and `/bounce` output: `👑` (Bot Administrator), `⭐` (Autokick Ignored), and `💤` (Away).

### Performance & Resource Optimization
- **Adaptive Polling Backoff (`P3`)**:
  - Implemented adaptive sleep intervals in background channel join and message resend workers (`bg_channel_join_worker`, `bg_resend_worker`), scaling sleep up to 30s when queues are idle.
- **Bounded Read Query Limits (`P4`)**:
  - Added default safety `limit` parameters to database read functions (`get_all_catalog_chats`, `get_all_catalog_channels`, `get_all_transport_stats`, `get_all_autokick_ignored_fingerprints`, `get_all_active_cmping_incidents`, `get_ap_followers`, `get_ap_follower_inboxes`).
- **In-Memory Cache Pruning (`P5`)**:
  - Bounded `_cmping_last_results` cache to 500 entries with automatic pruning of oldest entries.
  - Pruned server status and error records from `_cmping_server_status` and `_cmping_server_errors` when servers are removed via `/cmpingdel`.
- **Lazy Debug Log Formatting (`P6`)**:
  - Protected expensive key fingerprint formatting and admin lookup debug logging behind `logger.isEnabledFor(logging.DEBUG)` guards.

## 2.12.9

### Performance & Scalability
- **SQLite Reader Connection Pooling (`P1`)**:
  - Implemented thread-safe LIFO read connection pool (`_ReaderConnectionPool`) and connection wrapper (`_PooledConnection`) with automatic pool invalidation on dynamic database switches.
  - Added `_reader_connection()` context manager and refactored all 46 read operations in `database.py` to reuse pooled connections.
  - Accelerated unit test suite execution from 33.0s down to 2.7s (>12x speedup) while guaranteeing concurrent reader isolation under SQLite WAL mode without thread contention.
  - Updated `close_db()` to safely drain and close pooled reader handles alongside the primary writer handle.
- **Non-Blocking Background Workers & Offloaded I/O (`P2`)**:
  - **VirusTotal Inspection (`/virus`)**: Decoupled message quote resolution and file attachment downloads (`_get_msg_file_info`) from the Delta Chat event handler thread into background daemon worker `bg_virus_worker`. Command handler responds immediately with `⏳` reaction (or synchronous usage message for empty invocations) without stalling incoming message processing.
  - **Channel Post Media Ingestion**: Offloaded `_ingest_channel_post` (file attachment downloading and Pillow WebP image compression) from `handle_all_messages` to a dedicated daemon thread, preventing media uploads from blocking the main Delta Chat event loop.
  - **CMPing Worker Concurrency Bounding**: Pinned `_run_cmping_subprocess` strictly to background worker thread and capped multi-server relay check thread pool (`ThreadPoolExecutor`) concurrency to `min(4, len(bot_domains))`, preventing system load and process spikes.
  - **Async-Safe QR Code Generation**: Wrapped synchronous Pillow and SVG QR generation calls (`_generate_qr_bytes`) in `handle_qr_svg`, `handle_qr_png`, `handle_channel_qr_png`, and `handle_channel_qr_svg` with `await asyncio.to_thread(...)`, keeping the aiohttp web server event loop responsive.

## 2.12.8

### ActivityPub Federation & Resilience
- **RFC 9421 HTTP Message Signatures Support**:
  - Implemented `extract_signature_info()` and full verification for RFC 9421 signatures (`Signature-Input` + `Signature: sig1=...`), including `@method`, `@target-uri`, `@path`, `@authority`, `created` timestamp verification, and signature parameters base string construction.
  - Eliminated `Missing keyId in Signature header` errors when modern Fediverse instances (e.g. Mastodon 4.3+, 4.4-alpha) retry or send requests using RFC 9421.
- **Graceful Handling of Deletion Activities for Gone/Suspended Remote Actors**:
  - Prevented infinite retry loops and 401 spam when remote instances send `Delete(Actor)` for deleted or suspended accounts whose actor endpoints return HTTP 410 (Gone) or 403 (Forbidden).
  - Cleaned up matching follower records from SQLite database and responded with `202 Accepted` after validating that the deletion request and keyId share the same origin host.
  - Downranked expected actor lookup status codes (403, 404, 410) from `WARNING` to `INFO` in logging.
- **Follower Public Key Local Caching**:
  - Added `follower_public_key` storage in `ap_followers` database table with automatic schema migration.
  - Caches follower public key PEM upon initial `Follow` activity to allow immediate local cryptographic verification for subsequent requests (`Undo`, `Delete`) without requiring outbound network requests.

## 2.12.7

### UI & UX Improvements
- **Cooldown Accuracy (`U1`)**: Updated `/help` and documentation to accurately state real command cooldowns (60s general, 15s cmping/slap, 10s search).
- **Graceful Empty Invites (`U2`)**: Render disabled button and omit QR modal when channel has no invite link.
- **Landing Page Fallback (`U3`)**: Render disabled button and clear fallback notice when bot invite link is unavailable.
- **Silent Cooldown & Queue (`U4`)**: Replaced chat text spam with `⏳` reaction on cooldown, queueing delayed execution and transitioning reaction to `☑️` upon completion.

## 2.12.6

### Security & Hardening
- **SSRF Mitigation (`S1`)**: Block private/reserved/loopback/cloud-metadata IP fetches (`is_safe_url()`) across remote actor and key resolution.
- **Cheap Signature Rejection (`S1`)**: Validate Date freshness window (±300s) and body Digest (SHA-256) prior to outbound remote `keyId` resolution.
- **Request Body Limits & Rate Limiting (`S2`)**: Limit `client_max_size` to 256 KB on `web.Application`, 64 KB on ActivityPub inbox (`413`), and apply sliding-window rate limiting (`429`): inbox (60 r/min), preview & media (120 r/min).
- **Dependency Pinning (`S3`)**: Pinned CVE-free dependency floors in `requirements.txt` and pinned `cmping` to exact commit SHA.

## 2.12.5

### Fediverse / ActivityPub Improvements
- **Recent Posts Backfill on Follow**: Deliver up to 10 recent channel posts to new followers after `Accept(Follow)`.
- **Delta Chat Wallpaper as Header Banner**: Added `"image"` field pointing to `/background.jpg`.
- **Standalone Note `@context`**: Added JSON-LD context to Note objects for direct search and dereferencing in GoToSocial.
- **Mastodon Instance Metadata (`GET /api/v1/instance`)**: Added instance metadata endpoint for Fediverse discovery.

## 2.12.4

### Fediverse / ActivityPub Fixes
- **Trailing Slash Sanitization & Multi-Slash Route Normalization**:
  - Automatically strip trailing slashes and whitespace from `BASE_URL` and `database.get_config("base_url")` across `_ingest_channel_post`, `build_actor_json`, `build_note`, and `_deliver_post` to prevent double slashes in actor URLs (`//c/{token}`) and public key identifiers.
  - Added multi-slash route patterns (`/{slash:/*}c/{token}`, `/{slash:/*}c/{token}/actor`, `/{slash:/*}inbox`, etc.) so that requests with leading multiple slashes (e.g. `////c/{token}`) sent by reverse proxies or Go HTTP clients resolve with 200 OK instead of failing with 404.

## 2.12.3

### Fediverse / ActivityPub Federation
- **Shared Inbox Support (`POST /inbox`)**:
  - Added route `POST /inbox` to receive activities sent to the instance-level `sharedInbox` advertised in Actor JSON.
  - Automatically extracts target channel token from the incoming activity's `object` / `target` properties (supporting `Follow`, `Undo`, and `Delete`).
- **Following Endpoint (`GET /c/{token}/following`)**:
  - Implemented `GET /c/{token}/following` returning an empty `OrderedCollection` (`totalItems: 0`) as requested by GoToSocial and other Fediverse servers during actor profile discovery.
- **Robust Remote Key Resolution & Authorized Fetch**:
  - Added `resolve_public_key` with support for standalone PublicKey endpoints (like GoToSocial `/main-key`) and embedded `publicKey` objects (like Mastodon `#main-key`).
  - Added support for Authorized Fetch (HTTP Signatures on GET) when resolving remote follower profiles to obtain their personal `inbox` and `sharedInbox`.
  - Addressed `Accept(Follow)` activity directly with `to: [follower_id]` and delivered to the follower's inbox.
  - Supported SHA-512 in HTTP signature verification alongside SHA-256.

## 2.12.2

### Web Preview & Fediverse UI
- **Fediverse Handle Tag with 1-Click Copy in Web Preview Header**:
  - Replaced duplicate `📡 RSS Feed` link in the top-right header with an interactive Fediverse channel tag (`@<token>@<domain>`, e.g., `@twniAE9eNajd@dc.gluek.info`).
  - Clicking the tag copies the handle to clipboard and provides immediate visual feedback (`✓ Copied!`), allowing users to easily paste the handle into their Mastodon or Fediverse search bar to follow the channel.
  - The dedicated `📡 RSS Feed` action button remains in the main channel action row.

## 2.12.1

### Bug Fixes
- **Python 3.11 Module-Level Type Annotation Fix**:
  - Added `from __future__ import annotations` to `activitypub.py`.
  - Removed evaluated string-union annotations on private module globals (`_http_session`, `_delivery_queue`, `_web_loop`) to resolve `TypeError: unsupported operand type(s) for |: 'str' and 'NoneType'` when starting the bot in Docker (Python 3.11).

## 2.12.0

### Fediverse / ActivityPub Federation
- **Full Fediverse Channel Federation (`@<token>@<domain>`)**:
  - Every cataloged Delta Chat channel functions as an autonomous Fediverse actor of type `Service` (displaying the 🤖 Bot badge on Mastodon and compatible platforms).
  - Users on Mastodon, Pleroma, Misskey, Friendica, and other Fediverse instances can discover channels using standard WebFinger queries (`RFC 7033`) via `GET /.well-known/webfinger?resource=acct:<token>@<domain>`.
  - Channel preview URLs (`/c/{token}`) implement standard Content Negotiation: requests with `Accept: application/activity+json` or `application/ld+json` return the full ActivityStreams 2.0 Actor representation with public key, avatar icon, inbox, outbox, and followers collection endpoints.
- **Cryptographic HTTP Signatures (`draft-cavage-http-signatures`)**:
  - Independent RSA-2048 keypairs generated per channel actor and persisted in the SQLite database (`ap_actor_keys`).
  - Strict verification of incoming `Signature`, `Digest` (SHA-256), and `Date` (±300s window) headers on Actor inboxes to guard against replay and spoofing attacks.
  - Automatic outgoing request signing for deliveries and `Accept(Follow)` notifications.
- **Federated Follower Management & Outbox**:
  - `POST /c/{token}/inbox` handles `Follow` activities by recording the follower in `ap_followers` and asynchronously returning a cryptographically signed `Accept` activity to the follower's inbox.
  - Handles `Undo(Follow)` and `Delete(Actor)` events to keep follower rosters clean and GDPR-compliant.
  - `GET /c/{token}/outbox` serves an `OrderedCollection` of recent notes; `GET /c/{token}/followers` reports total follower count.
  - `GET /c/{token}/posts/{msg_id}` returns individual Note objects.
- **Asynchronous Background Delivery Pipeline**:
  - New channel posts ingested via `_ingest_channel_post` are automatically queued and broadcast as `Create(Note)` activities to remote follower inboxes with deduplicated `sharedInbox` delivery.
  - Rich text formatting with autolinked URLs and media enclosures (WebP images, MP4 videos, audio, and documents).
- **GoToSocial-Modeled `robots.txt` & NodeInfo 2.0**:
  - Replaced simple disallow-all `robots.txt` with a comprehensive, GoToSocial-modeled configuration blocking abusive AI scrapers and SEO crawlers while permitting channel previews (`/c/`) and media (`/media/`).
  - Added NodeInfo 2.0 discovery (`/.well-known/nodeinfo` and `/nodeinfo/2.0`) for discovery by Fediverse crawlers and directory indexers.

## 2.11.6

### Channel Catalog & Privacy
- **Unlisted Channels by Default (`/dchanneladd`)**:
  - Channels added via `/dchanneladd <URL>` are now initialized in **unlisted** mode by default (`is_public = 0`).
  - Unlisted channels retain their own unique web preview page (`/c/{token}`) and standard RSS feed (`/c/{token}/rss.xml`), and the bot ingests new messages and attachments continuously.
  - Excluded from public directory listings: unlisted channels are hidden from the bot's web landing page (`/` and `/c/`) and the public `/dchannels` command in group chats and for non-admin users.
- **Dynamic Catalog Visibility Toggles (`/dchannelpub<ID>on` & `/dchannelpub<ID>off`)**:
  - Added administrative commands to toggle channels between public and unlisted at any time.
  - Toggling public status automatically updates the catalog and invalidates web preview and landing page caches immediately.
  - `/dchanneladd` confirmation message now directly provides the preview link, RSS link, and suggests `/dchannelpub<ID>on` if the administrator wishes to make the channel publicly discoverable.
- **Admin Direct Message Catalog Visibility**:
  - When the bot administrator queries `/dchannels` in a private 1-on-1 direct message, all registered channels are shown, with unlisted channels clearly marked with `🔒 [Unlisted]` and quick-action `/dchannelpub<ID>on` command links.
  - In group chats or when queried by non-admin members, only public channels are displayed to prevent leakage.
  - Direct queries via `/dchannel<ID>` for unlisted channels are restricted to bot administrators, preventing numeric ID enumeration by regular users.

## 2.11.5

### Web Preview & Landing Redesign
- **Authentic Delta Chat Styling & System Typography**:
  - Replaced generic AI-generated neon gradients and external Google Fonts (`Outfit`) with clean, privacy-respecting native system typography (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif`) inspired by [gluek.info](https://gluek.info).
  - Integrated official Delta Chat dark wallpaper pattern with doodle envelopes, speech bubbles, and symbols on `#19232b`, served with immutable caching via `/background.jpg` and `/static/background.jpg`.
  - Formatted channel posts into authentic Delta Chat messenger message bubbles (`#232d36`, rounded 12px) with sender names highlighted in Delta Chat blue (`#53bdeb`), quotes styled with vertical accent bars, monospace code blocks, and bottom-right timestamps with checkmarks (`✓`).
  - Unified aesthetics across the channel catalog landing page, channel preview view, tombstone, and 404 pages with zero third-party font tracking.

## 2.11.4

### Channel Catalog Automation
- **Automatic Channel Removal on Bot Ejection**:
  - Automatically detects when the bot is removed from a channel by the channel owner/admin (via `SystemMessageType.MEMBER_REMOVED_FROM_GROUP`, self contact ID `1`, or system removal messages).
  - Soft-deletes the channel from the public catalog (`/dchannels`, `/c/`), invalidates preview and RSS caches immediately, and serves a graceful tombstone message on preview URLs without attempting to re-join.
  - Automatically keeps catalog channel member counts synchronized on member join/leave events.

## 2.11.3

### Media Optimization & Post Cleanup
- **Automatic WebP Image Compression**:
  - Attached images (`.jpg`, `.jpeg`, `.png`, `.bmp`) in channel posts are automatically compressed to modern WebP format (`quality=80`, `method=3`, `max_dim=1600`) via Pillow on ingestion.
  - Reduces media traffic by 70–90% for web preview pages and RSS feed readers.
  - Animated GIFs and SVGs are preserved in their native formats.
  - Graceful fallback to original image format and file serving if compression fails or Pillow is unavailable.
  - Backwards-compatible resolution in `handle_media_file` allows requests for `.jpg`/`.png` to seamlessly serve `.webp` when available.
- **Delta Chat Attachment Fallback Stripping (`DC_FALLBACK_PATTERN`)**:
  - Automatically filters out Delta Chat core email fallback placeholders (e.g. `[Image – 304.26 KiB]`, `[Document - file.pdf]`) from message text, preventing redundant metadata labels from cluttering post previews when attachments are displayed natively while preserving authentic author text.

## 2.11.2

### Improvements & UI
- **Spacious `/dchannels` Catalog Layout**:
  - Re-architected `/dchannels` output with a clear multi-line format separating command/title, description, and preview link onto distinct lines.
  - Channels are now cleanly delineated with blank lines (`\n\n`) for optimal readability in Delta Chat mobile and desktop clients.
- **Forgejo Mirror in Channel Previews**:
  - Added the Forgejo repository mirror link (`https://git.gluek.info/gluek/deltachat_bouncer`) alongside version number in the footer of public channel preview pages (`/c/{token}`).

## 2.11.1

### Web Service & Channel Previews
- **Rich Markdown Post Formatting (`format_markdown_html`)**:
  - Full CommonMark and Delta Chat formatting engine with support for bold (`**text**`, `__text__`), italic (`*text*`, `_text_`), strikethrough (`~~text~~`), inline code (`` `code` ``), fenced code blocks with syntax styling (` ```lang ... ``` `), blockquotes (`> text`), spoilers (`||spoiler||` with click-to-reveal), and links (`[label](url)` and autolinked URLs).
  - 100% XSS immunity via strict HTML escaping and javascript/data URI protocol stripping.
  - Channel preview post timeline and RSS feed item descriptions (`<![CDATA[ ... ]]>`) now render rich markdown identically to ArcaneChat / Delta Chat clients.
- **In-Memory Caching Layer & High Load Optimization**:
  - Added fast in-memory response caches with TTL and ETag headers for channel web preview pages (60s TTL) and RSS feeds (120s TTL), returning `304 Not Modified` on matching `If-None-Match`.
  - Added in-memory binary caching for QR code generation (SVG and PNG) to eliminate repeated CPU-bound QR rendering.
  - Event-driven cache invalidation hooks automatically purge channel caches on new incoming posts (`_ingest_channel_post`), channel removals (`/dchannelremove`), or base URL changes (`/url`).
- **Crawler & Bot Blocking (`robots.txt`)**:
  - Configured `robots.txt` (`/robots.txt`) with `User-agent: *\nDisallow: /\n` to block search engine scrapers and AI crawlers from generating unnecessary traffic.

## 2.11.0

### Web Service & Channel Previews
- **Home Assistant Ingress Support**:
  - Integrated Home Assistant Ingress on port 8080 with seamless sidebar navigation (`Open Web UI`).
  - Added support for `X-Ingress-Path` dynamic header for proper subpath asset resolution (logos, avatars, QR codes, links).
- **Public Channel Web Preview (`/c/{token}`)**:
  - Implemented an embedded, lightweight aiohttp web server providing instant web preview pages for channels registered in `/dchannels`.
  - Each channel is assigned a unique, unguessable 12-character base62 token.
  - Channel preview pages feature a modern dark-mode aesthetic (matching Uptime Bot), displaying channel name, description, member count, avatar, and a live message timeline.
  - Interactive Delta Chat join dialog with dynamic QR code generation (SVG and PNG download options), deep links (`https://i.delta.chat/#...` and `OPEN-CHAT:...`), and one-click clipboard copying.
  - Media file support: attached photos, videos, voice notes, audio, and documents are displayed inline and served directly from a dedicated media cache directory (`CHANNEL_MEDIA_DIR`).
- **Standard RSS 2.0 Feeds (`/c/{token}/rss.xml`)**:
  - Full-fidelity RSS feed at `/c/{token}/rss.xml` (with convenient `/c/{token}/rss` redirect).
  - Includes channel metadata, item timestamps (RFC 822), author names, message contents, and media enclosures for RSS readers.
- **Graceful Channel Removal & Tombstone**:
  - Channels removed from the catalog via `/dchannelremove` are soft-deleted (`is_deleted = 1`).
  - Accessing a removed channel's preview URL displays a clean tombstone notice (*"The channel has been removed from the public catalog and is no longer available for preview."*) instead of a generic 404.
- **Core Handshake Backfill**:
  - Automatically backfills the initial batch of up to 10 messages provided by the Delta Chat core handshake upon joining via `/dchanneladd <url>`.
  - Real-time ingestion stores subsequent incoming channel messages up to a sliding window of 100 posts per channel.
- **Base Web URL Configuration (`base_url`)**:
  - Added `base_url` add-on configuration option and `/url` admin command to view or configure the public base URL stored in database settings.
  - Supports fallback to `BASE_URL` environment variable.
  - Updated `/dchannels` and `/dchannel<ID>` commands to provide preview URLs alongside join links.
- **Optional Direct Access (Port 8080)**:
  - Exposed port `8080/tcp` in add-on configuration for optional direct external reverse proxy access.
- **Landing Page (`/`)**:
  - Public landing page introducing Bouncer Bot capabilities, active channel counts, and Delta Chat connection instructions.

## 2.10.1

### Improvements
- **In-Place Live Message Updates for VirusTotal Scans (`send_edit_request`)**:
  - When submitting a new URL or file for analysis (404 in VirusTotal database), the bot now posts an immediate interim status message (`Analysis is in progress...`) and sets the `⏳` reaction.
  - The worker polls VirusTotal in the background for up to 12 attempts (~3 minutes with the 15-second rate limiter).
  - Upon completion, the bot updates the interim message in-place via Delta Chat RPC `send_edit_request` with the complete vendor detections and analysis report, and sets the final reaction (`☑️`, `⚠️`, `🚨`).
  - If analysis exceeds 12 polling attempts, the message is updated with a timeout notice directing the user to the web report (`⚪️`).
- **Clean Markdown URL Formatting**:
  - Removed enclosing backticks around URLs in reports to prevent Delta Chat markdown parsers from appending `%60` to links.

## 2.10.0

### Security & VirusTotal Inspection
- **VirusTotal Link & File Inspection (`/virus`)**:
  - Added `/virus <url>` command to inspect links for phishing, malware, and threats via VirusTotal API v3.
  - Added reply inspection: replying to a message with `/virus` automatically detects and scans either an attached file or the first URL in the quoted message.
  - Added direct file inspection: sending a message with an attached file and `/virus` caption triggers a file scan.
  - **On-Demand Attachment Download**: Automatically downloads full message attachments via Delta Chat RPC (`download_full_message`) when messages arrive without auto-downloaded blobs (`download_limit=1`).
  - **Hash-First Querying**: Computes SHA-256 locally and checks existing VirusTotal reports first, avoiding redundant file uploads and conserving bandwidth.
  - **Direct Upload Fallback**: If a file (up to 32 MB) is not present in the VirusTotal database, it is uploaded via multipart/form-data and polled until analysis completes.
  - **Global Rate Limiting & Queueing**: Enforces a strict 1-check-per-15-seconds rate limit across the entire bot to safely respect VirusTotal free tier limits (4 lookups/min). Additional incoming requests receive a queue notification (`⏳ Another VirusTotal check is in progress, your request is queued...`) and are processed in FIFO order.
  - **Visual Progress & Reactions**: Sets `⏳` reaction on trigger message during queuing and scanning, updating to `☑️` (clean), `⚠️` (suspicious), `🚨` (malicious), or `❌` (error) upon completion.
  - Configurable via `VIRUSTOTAL_API_KEY` in `.env` or container environment.

## 2.9.3

### User Experience & Command Reporting
- **Transparent Observation Progress in `/bounce`**:
  - In group chats with `/autokick` enabled, `/bounce` now distinguishes between truly active members and silent members under observation.
  - When members have not reached the warning threshold yet, `/bounce` displays an **Observation in progress** status reporting the number of silent members and the countdown to the earliest warning window (e.g. at day 83 of observation) instead of misleadingly claiming all users are active.
  - Added total member count to the all-active report when every member has verified recent activity.
  - Added observation summary note to the warning report when additional silent members remain under observation.
- **Informative Metrics in `/autokick` Status**:
  - Displays the number of days the bot has monitored the group.
  - Displays the count of silent members under observation and the countdown until their earliest warning.
  - Reports the count of members currently in the warning window (< 7d to kick).
- **Accurate Candidate Reason Formatting**:
  - Updated candidate descriptions from `never seen in Xd since joined` to `never seen in Xd of observation`, reflecting actual observation time rather than join time.
- **Autokick Overview Helper (`_get_chat_autokick_overview`)**:
  - Unified autokick metrics collection and candidate evaluation into a single-pass helper reused across `/bounce`, `/autokick`, and background monitor routines.

## 2.9.2

### Performance & Database Architecture
- **Persistent Writer Connection**:
  - Replaced ad-hoc connection creation on every write with a dedicated persistent writer connection protected by `_write_lock` and standard transactional context manager (`_writer_transaction()`), eliminating connection teardown churn and disk sync overhead.
- **Strict `PRAGMA synchronous = NORMAL` & `busy_timeout`**:
  - Enforced `PRAGMA synchronous = NORMAL;`, `PRAGMA journal_mode = WAL;`, and `PRAGMA busy_timeout = 5000;` on all database connections across the entire codebase.
- **Concurrent Non-Blocking WAL Reads**:
  - Replaced global `_lock` on read operations with independent read connections, allowing concurrent readers to execute simultaneously alongside writer without lock contention.
- **Batch Contact Seeding**:
  - Replaced N+1 individual insert queries in catalog member count refresh (`_refresh_catalog_member_counts`) with `ensure_contacts_first_seen_batch()`, recording contacts in a single atomic transaction.

## 2.9.1

### Security Hardening & Concurrency Fixes
- **Fix Undefined `resilient_lock`**:
  - Declared `resilient_lock` globally, fixing runtime `NameError` crash during resilient sending and message failover.
  - Synchronized transport switching and message sending during resilient delivery.
- **Server Domain Input Validation (`/cmping`)**:
  - Added strict regex domain validation (`DOMAIN_REGEX`) to `/cmping`, `/cmpingadd`, and `/cmpingdel` commands to prevent command injection and malformed subprocess parameters.
- **Credential Protection (`/addtransport`)**:
  - Enforced that `/addtransport` can only be executed in private 1-on-1 chats with the bot, preventing accidental password leakage in group chats.
- **Rate Limiting (`/slap`)**:
  - Added 15-second cooldown per chat for `/slap` commands.
- **Sanitized User Error Messages**:
  - Removed internal exception and traceback disclosures from user-facing error messages in `/kick`, `/invite`, `/relays`, `/approve`, `/decline`, and `/addtransport`.
- **Bounded Message Deduplication**:
  - Replaced full set clearing with an `OrderedDict` maintaining up to 2000 recent message IDs with FIFO eviction, preventing duplicate command execution.

### High-Load & Database Optimizations
- **SQLite WAL & Concurrency PRAGMAs**:
  - Enabled `PRAGMA journal_mode = WAL`, `PRAGMA synchronous = NORMAL`, `cache_size = -4000`, and `busy_timeout = 5000` for high concurrency and performance under load.
- **Buffered Transport Statistics**:
  - Buffered sent/received message statistics in memory, flushed to SQLite in a single transaction every 30 seconds instead of executing database writes on every individual message.
- **Database Indexes**:
  - Added indexes on `autokick_warnings(chat_id)`, `pending_requests(chat_id, approved)`, `away_notifications(away_updated_at)`, and `cmping_history(checked_at)`.
- **Automated Data Pruning**:
  - Added periodic pruning in background monitor loop for `away_notifications` and `cmping_history` older than 30 days.
  - Added periodic in-memory cleanup of stale anti-spam timestamps and unused domain locks.

## 2.9.0

### Added
- **Two-Stage Inactivity Warning System for `/autokick`:**
  - Inactive members now receive a direct 1-on-1 private notification from the bot before being kicked, warning them of impending removal and inviting them to stay by posting in the group.
  - The group chat receives a daily summary broadcast (at most once every 24 hours) listing all members in the warning zone with days remaining until removal.
  - **Kick Protection:** Members are now strictly kicked only after receiving a warning and passing a minimum 24-hour grace period.
  - Dynamic warning threshold: warnings begin at `autokick_days - 7` days for thresholds $> 7$ days (i.e. 7 days before kick), and at `autokick_days - 1` days for thresholds $\le 7$ days.
  - Warnings are automatically cleared as soon as a user sends a message in any shared chat.
- **Cryptographic Fingerprint Ignore List (`/autokick ignore`):**
  - Added `/autokick ignore <email/nick/id>` for bot administrators to look up a member, extract their cryptographic key fingerprint, and permanently exempt them (e.g. service bots or quiet system accounts) from auto-kick.
  - Added `/autokick unignore <fingerprint/email/nick>` to remove exemptions.
  - Added `/autokick ignore` / `/autokick ignore list` to display all currently exempted fingerprints and notes.
- **Exemption for `/away` Users:**
  - Members with an active `/away` vacation/absence status are automatically exempt from inactivity warnings and auto-kicks.
- **`/bounce` Integration with `/autokick` Thresholds:**
  - In group chats where `/autokick` is active, `/bounce` now shows members currently in the warning window (< 7 days or < 1 day remaining until auto-kick).
  - In groups where `/autokick` is disabled, `/bounce` continues to report inactivity based on the default 21-day threshold.
- **Grace Period Protection for New Members:**
  - Utilizes `contact_first_seen` tracking so newly joined members who have not yet spoken (`last_seen == 0`) are protected by a grace period based on their join time, preventing premature autokicking.
- **Database Schema Upgrades:**
  - Added `last_autokick_warn_at` column to `chats` table.
  - Added `autokick_warnings` and `autokick_ignored_fingerprints` tables.

## 2.8.2

### Added
- **Options.json Fallback for Display Name & Status Text**:
  - `on_init` now checks `/data/options.json` fallback when `DISPLAY_NAME` or `STATUS_TEXT` are not set in environment variables.

## 2.8.1
- Initial Home Assistant Add-on release.
- Group inactivity monitoring, `/autokick` of stale members, and chat/channel catalogs.
- Mail relay testing and connectivity monitoring via `cmping`.
