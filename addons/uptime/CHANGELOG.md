# Changelog

## 2.25.3

### Fixed
- **Delta Chat Core at 40-65% CPU**: Peer chats carry only protocol messages, handled as they arrive, but they were kept for the account's `delete_device_after` (a day, which incident edits in user chats need): 65k messages, a 175 MB database, and the core spent ~0.5 s CPU per message (~0.1 s in a bot with a small database). Every 10 minutes (and at start) all but the newest 20 messages of each peer chat are deleted on this device.
- **Reports Their Own Sender No Longer Confirmed Started a Vote Every Few Minutes**: Older peers (smtp targets checked as web pages, degraded after one burst) reported a target in telemetry and answered UP when asked a minute later; the target stayed UP and the next report started the next vote: 273 cross-check batches an hour to each of 5 peers, mostly one target each. When the reporter itself answers UP to the vote its report started, its reports of that target are ignored for 10 minutes (30 minutes for unstable nodes, as before).

### Added
- **`/health` Endpoint**: `{"status": "ok", "version": "2.25.3"}` (also for `HEAD`), without database or page, for monitors and other nodes.

## 2.25.2

### Fixed
- **Peers Checked `smtp://` Targets as Web Pages**: A peer stored the `smtp://` targets it mirrors with the type `http` (only http/tcp/ping were accepted), so it checked `smtp://chatmail.uk` with an HTTP request, always got DOWN and reported it in telemetry, making the main node ask all peers again and again. The type is kept now; mirrored targets stored wrongly are fixed at start and their false DOWN is forgotten.
- **Ping in Docker Desktop**: Docker Desktop's network proxy (macOS / Windows) drops ICMP replies as soon as several echoes are in flight: 68% lost with 5 targets at once, 89% with 20, 17% even one at a time next to the running bot, against 0% on a Linux host. A home node there voted degraded (`loss 80%`) and DOWN (`Timeout`) on most ping targets. A node in Docker Desktop (kernel `linuxkit`) now abstains on ping targets, like a node without ICMP, and logs why once; `PING_ON_DOCKER_DESKTOP=1` checks them anyway.
- **Reports of Unstable Nodes Started a Vote Every Two Minutes**: A node marked unstable has its votes masked, so the target stayed UP and the node's next telemetry report started another vote: the main node asked all peers about 450 times an hour (each time encrypted mail to every peer, the Delta Chat core at 10-65% CPU). When a vote that a report started finds the reporter's vote masked as unstable, its reports of that target are ignored for 30 minutes. A reporter whose vote counts is still heard, so a target only one node fails still becomes DEGRADED after two reports.
- **Private Addresses at a Peer**: A name resolving to a private address on a peer (split-horizon DNS at home, a VPN) made the peer vote DOWN with "Target blocked". The peer abstains now in cross-check answers and mirrored targets; the node's own monitors still show the error.

## 2.25.1

### Fixed
- **IPv4 Fallback Did Not Happen After a Failed A Query**: The A and AAAA queries run together and their answers were cached for the record TTL. When the A query failed (timeout, SERVFAIL - seen from a home resolver) and AAAA answered, only the IPv6 address was cached; an HTTP check over a broken IPv6 then failed with `Connect call failed ('2a01:...')`, and the IPv4 recheck found no IPv4 in the cache and treated the host as IPv6-only, so the node voted DOWN (a partial outage notice for `delta.chat`). A partial answer (one query failed, not "no such record") is now cached for 30 s only, and the IPv4 recheck resolves the host again once when the cached answer has no IPv4.
- **Degraded Paths Need 3 Bad Series Over 3 Minutes**: A node that is a few ms from its targets voted degraded after a single short spike (2 ms usual, 107 ms once, on two targets at the same moment - its own uplink, not the paths). A node now calls a path degraded only after 3 bad ping series in a row spanning at least 3 minutes; checks asked for by peers count, but cannot shorten the time. Until then the check stays UP and its details show the slow round trip (`178 ms, usual 4 ms`). With the 2 quorum confirmations a DEGRADED notice now takes about 5 minutes.

## 2.25.0

### Changed
- **The server runs releases, not the tip of `main`.** `update.sh` deploys the newest `vX.Y.Z` tag, so a merge into `main` reaches the server only once it is released; several PRs can go out together. `UPDATE_REF` in `.env.local` pins a release (`UPDATE_REF=v2.24.0` - a rollback; empty again = newest) or follows a branch as before (`UPDATE_REF=main`). A release tag moved on GitHub or Forgejo makes the update fail instead of deploying the changed code. Errors that stopped the script with a message (both remotes unreachable, an unknown `UPDATE_REF`) now also ping the healthcheck's `/fail`, not only failed commands. The script now runs as one function, so the `git reset` that rewrites `update.sh` cannot confuse the running copy.
- **Releases are published by a tag** (new `.github/workflows/release.yml`): pushing `vX.Y.Z` checks that `bot.py` has that version, creates the GitHub release with the version's section of this file as its notes (an existing release is left alone), then sends the ntfy notification and the `bot-updated` dispatch to `hass-addons-deltachat` (now with `"version"` in the payload). Both used to go out on every push to `main` (`uptime-changelog.yml`, removed), so Home Assistant users got unreleased code.
- Releasing: merge, then `git tag -a vX.Y.Z -m "..." <commit> && git push origin vX.Y.Z`.
- **Upgrading:** tag `v2.25.0` right after merging this. Until then the new `update.sh` would deploy `v2.24.0`, which still has the old script that follows `main` - and the server would switch back and forth on every run.

## 2.24.0

### Added
- **Degraded Path Detection for Ping Monitors**: A ping check sent a single echo, so a target behind a lossy or congested path (2026-10-24: 50-80% loss and 550 ms instead of 60 ms from a home connection to a relay, due to a bad peering on the way) was simply UP. A ping check now sends 5 echoes 200 ms apart (about 3 s at most) and reports the median round trip. With 2 or more lost, or a median at least 3 times this node's usual round trip for that address and 100 ms above it, the check is DEGRADED: the target is reachable, so it is not DOWN, but the node votes 🟠 degraded. In quorum chats one degraded vote makes a DEGRADED notice (never an incident or downtime), and the vote line tells why: `🟠 HOME (561 ms, loss 80%, usual 60 ms; trace: +589 ms between hop 6 ... and hop 7 ...)`. The usual round trip is learned from healthy checks only and stored in the new `ping_baselines` table. The `trace:` hint comes from one `traceroute` of the degraded path (cached 15 min, run in the background, so it arrives with the confirming vote) and names the link where the round trip rises most. Degraded results travel in cross-check answers and telemetry, so a peer whose own path is bad (e.g. a node at home) triggers the vote. Nodes that degrade 5 or more targets alone count as unstable like nodes that fail them. The Docker image now includes `traceroute`.
- **Automatic Account Creation**: `serve` without a configured account no longer exits with "There are no configured accounts to serve". The bot asks the core (`init_transports`, core 2.62+) to create an account on the fastest chatmail relay of its built-in list; the core adds further relays in the background. `bot.py init <addr> <password>` and `bot.py init DCACCOUNT:server.tld` still choose the account explicitly.

## 2.23.0

### Added
- **SMTP / STARTTLS Monitors (`smtp://host[:port]`)**: A `host:25` TCP check only showed that the port is open. An `smtp://` monitor talks to the server like a sending mail server: greeting `220`, `EHLO`, `STARTTLS` must be offered, TLS handshake with the certificate verified against trusted CAs and the target host name, `QUIT`. It is DOWN with the reason (`SMTP: STARTTLS not offered`, `SSL: certificate has expired`, `SSL: Hostname mismatch, ...`, `SMTP: greeting 554 ...`) - exactly what makes MTA-STS senders (`mode: enforce`) stop delivering. Port 25 is the default, 587 works the same way, 465 uses implicit TLS. The certificate expiry is tracked like for HTTPS (alerts at 7 / 3 / 1 days, countdown in `/list`, `/ping` and on the dashboard). `/ping smtp://host` shows the certificate too. The session ends with `QUIT`, so the server logs an ordinary connection (`ehlo=1 starttls=1 quit=1`) and fail2ban does not count it. `SMTP_EHLO_NAME` sets the `EHLO` name (default: the host's FQDN, or `localhost`).
- **Peer Capability `smtp_check`**: `smtp://` targets are only sent for cross-checks to peers that announce it, so older nodes neither vote on them nor make `/ping` wait for their timeout.

### Fixed
- **`/probeignore *:25` Covers `smtp://` Targets**: The ignore patterns now know the default SMTP port, so a node with outbound port 25 blocked can abstain on `smtp://host` monitors with the same pattern as on `host:25` TCP monitors.

## 2.22.2

### Fixed
- **Admin Notifications Were Not Delivered**: The admin chat was created with `create_contact(admin address)`, which gives the address-only contact. Current cores only send encrypted, so every admin notification (probe offline, unstable node, paused chats) failed with `e2e encryption unavailable`. The bot now finds the admin's contact with their key (the fingerprint saved by `/initadmin`), sends to the 1:1 chat with that contact and replaces a cached admin chat that pointed elsewhere. The "admin" peer share scope uses the same contact, so groups the admin is in are recognized again.

## 2.22.1

### Fixed
- **1:1 Chats Paused by Mistake**: The chat audit of 2.22.0 treated every 1:1 chat as "bot removed from the group": the core reports `self_in_group = false` for 1:1 chats (and for channels the bot sends), although the bot can write there. All monitors of private chats, including the admin's, were paused at start. Only groups are checked for membership now; chats paused by mistake resume at the next audit (at start).

## 2.22.0

### Added
- **Monitors of Chats the Bot Left Are Paused**: When the bot was removed from a group, the chat was deleted or a 1:1 contact blocked the bot, its monitors were still checked every minute and shared with peers, so every node in the mesh kept checking them, and any alert failed to send (one node checked 4 monitors of two groups it had left in August and October). Every hour, and at start, the bot now asks the core whether it can still write to each chat with monitors. If not, the chat's monitors are paused: not checked, not alerted, not shared with peers (their copies expire there within a day), and its ongoing incidents are no longer updated. If the bot is added back, they resume with all settings. After 30 days they are deleted together with their history and incidents. The admin gets a notice for each step, and `/peers` shows how many chats are paused.

## 2.21.0

### Added
- **Unstable Nodes Do Not Flood Chats with Partial Outages**: A node whose own network has trouble fails many targets at once that the other nodes reach, and each became a separate "Partial Outage" notice: in one week a home node caused 97 and another node 104, mostly in bursts of 14–29 targets within two minutes. A node that fails 5 or more targets within 5 minutes alone (at least two other nodes reach them, and DOWN is the minority) is now marked unstable for 10 minutes, extended while it keeps failing. Its DOWN votes abstain, partial outage notices it alone caused that are still waiting to be sent are dropped (and their "resolved" notices too), and vote lines show `⚪ RU (node network unstable, not counted)`. The admin gets one notice when a node becomes unstable and one when it is stable again. Outages that most nodes see are reported as before.

### Fixed
- **Misleading IPv6 Error for Dual-Stack Hosts**: When all connection attempts of an HTTP check failed, aiohttp reported only the last one, often an IPv6 address (`Connect call failed ('2a06:98c1:...', 443)`), so a node looked like it had an IPv6 problem while IPv4 had failed as well. The check is now repeated over IPv4 only: if that works the target is up, otherwise the error shows both families (`IPv4: Timeout · IPv6: Connect call failed`).

## 2.20.0

### Added
- **Slower Checks for Long Outages**: A resource that stays down was checked at its normal interval for up to 30 days, and every peer kept checking it every minute: DNS queries, retries and peer votes for a target nobody waits for. Now checks slow down the longer it is down: every 5 minutes after 1 day, every 15 minutes after 7 days, every hour after 14 days (never more often than the resource's own interval). A recovery is noticed within that time and the normal interval applies again. `/list`, incident messages and the 7/14-day notices show the slower interval (`🐢 checked every 15 min`).
- **Peers' Targets Slow Down Too**: Targets mirrored from a peer had no limit at all: a peer whose user never removed a dead resource made every node check it every minute, indefinitely (a domain gone for 50 days caused about 12 DNS queries a minute on each node). Each node now tracks how long a mirrored target has been down for itself and applies the same steps, then checks it only once a day after 30 days.

### Changed
- **Stale Notices and Auto-Cleanup Count Uptime, Not Continuous Downtime**: The 7-day notice, 14-day warning and 30-day removal counted from the last status change, so a single short "up" (a flap, or a peer that could still reach the target) restarted the count and a dead target could stay monitored forever. A resource is now unreachable for N days when its uptime over the last N days is under 1%, as the README already described ("0% uptime for 30 days").
- **Auto-Cleanup Always Warns First**: A resource is removed at least 3 days after the 14-day warning was sent, also for resources that already qualify when this version starts.
- **Notices Do Not Repeat After a Flap**: Stale notices were reset by any recovery, so a flapping target would get the 7-day notice again. They now start over only after a resource has been up for a full day.

## 2.19.1

### Added
- **Why a Node Failed, in Vote Lines**: Partial outage notices, incident messages, the status page and the quorum log showed only which nodes could not reach a target (`🔴 🇮🇹 · 🟢 🇩🇪 (57ms)`), although every node already reports its error. The reason is now shown next to the node: `🔴 🇮🇹 (Timeout)`, once for all nodes when they failed the same way (`🔴 DE, RU (Timeout)`). A timeout points to the network between node and target, `Connection refused`, SSL or HTTP errors to the service itself. Long aiohttp errors are shortened (`SSL: self-signed certificate`, `Connection refused`, no `[Errno N]`), at most 60 characters.

### Fixed
- `test_batch_request_is_answered_in_one_message` failed now and then: its mock answered by call order while the checks run concurrently.

## 2.19.0

### Added
- **Paced outbox for everything the bot sends** (`outbox.py`): chatmail relays allow each sender 60 messages a minute with a burst of 10 and answer `450 Too much mail` above it; the core retries, the retries count too, and alerts arrive minutes late. Measured on the relay the bot sends ~2.3 messages a minute normally, but an outage across all 14 chats with 3 peers came to an estimated 80-115 in the first minutes (new incidents, live edits every 15-60 s, cross-checks both ways). Now every message, edit and reaction goes through one queue:
  - **Token bucket** of 50 a minute with bursts of 5 (headroom for what the core sends itself), in one sending thread.
  - **Priorities**: alerts (new and resolved incidents, status changes, SSL, stale reminders, partial outage notices, admin notifications) → command replies and reactions → duration-only incident refreshes → peer protocol (cross-checks, hello) → telemetry. Same priority: arrival order.
  - **Merging**: a job with the same key as a waiting one replaces it, keeps its place in line, takes the more urgent priority, and goes out once with the newest content - the incident message (by incident), the reaction on one message (`⏳` still waiting is replaced by `☑️`), telemetry to one peer.
  - **Expiry**: cross-check requests and answers that waited past the time the other side waits for them are dropped without using a send token; queued telemetry expires after 2 minutes (the next one replaces it anyway).
  - The minute summary in the log shows a backlog: `outbox waiting 12 (alert 2, peer 10)`.

### Changed
- **Incident messages are queued per incident**: the message id is read when the job runs, so an incident whose first message is still waiting gets one message with all monitors that failed meanwhile; an outage that ended before its first message went out still gets the resolved message (before: nothing, if the first send had failed). Telemetry bookkeeping (which status changes a peer already got) now happens only after the message really went out.
- **Live incident edits every 5 minutes** (hourly after a day) instead of every 15 s / 30 s / 1 min in the first hour. Status changes are still edited in right away, as alerts; the message shows the start time.

## 2.18.1

### Fixed
- **Ping Checks DOWN on Nodes Without Raw Sockets**: On hosted containers without `CAP_NET_RAW` and without a `ping` binary (seen on the Botkeep.cloud node), aioping could not open its raw socket and the fallback failed with `[Errno 2] No such file or directory: 'ping'`, so every ping target was reported DOWN from that region. Ping now falls back to an unprivileged ICMP datagram socket ("ping socket", allowed by `net.ipv4.ping_group_range`, which Docker opens to all groups), which needs neither. Works over IPv4 and IPv6.
- **No Way to Ping Is "Not Checked", Not DOWN**: If a node has no raw socket, no ping socket and no `ping` binary, its ping checks return "Ping not available on this node" and are skipped like IPv6 targets on a node without IPv6 (⚪ in `/ping`, abstains in peer votes, no alert). A warning is logged once.

## 2.18.0

### Added
- **`/probeignore` Accepts Hosts and Patterns**: A node that cannot reach whole groups of targets (a residential ISP blocking outgoing port 25, a domain blocked in its region) had to ignore every target one by one, exactly as written, and every new such target raised a partial outage notice again. An entry can now be:
  - a target as shown in alerts: `https://nine.testrun.org/` (with or without the trailing slash), `dnd.wb.ru:25`;
  - a host: `nine.testrun.org` — every target on it (HTTP, TCP ports, ping);
  - a pattern with `*`, matched against the target, its host and its host:port (HTTP/HTTPS with their default port): `*:25` (all SMTP port checks), `*.testrun.org`, `*:443`.
  Matching targets are no longer probed or reported by this node, and it abstains (`skip`) when peers vote on them, also for targets added later. Entries are case-insensitive; adding one reports how many mirrored targets it matched.

### Changed
- `/probeignore example.org` (no scheme) now ignores the host with all its targets instead of only `https://example.org`. Existing entries keep working.

## 2.17.2

### Fixed
- **Renamed Nodes Kept Their Old Names on Peers**: Since 2.12.0 the `node_name` in a peer's messages was ignored (the sender was only identified by address then), and the stored name changed only with a new HELLO, which `/nodename` does not send. A node renamed with `/nodename` therefore stayed under its old name in votes, alerts, `/ping` and status pages of its peers. Peers are now bound to their key, so a key-verified peer's announced name (in telemetry and cross-check messages) is taken over, together with its cached measurements. It is refused if it is this node's name or another peer's name (case-insensitive), so a peer cannot pose as a different node.
- **`/nodename` Moves This Node's Cached Measurements** to the new name and sends telemetry on the next scheduler tick, so peers see the new name within seconds instead of up to 2 minutes.
- **Partial Outage Nodes Not Cleared**: When the nodes that could not reach a DEGRADED target stopped answering, its partial outage was updated with an empty list of nodes; the last known nodes are now kept.

## 2.17.1

### Fixed
- **Same Monitor Checked Twice in a Row**: The scheduler's cached monitor rows (refreshed every 10 s) could be re-read from the database while a long check was still running (retries, peer votes: up to a minute) and still carry the previous `last_checked`, so the same check started again seconds after it finished, with the old status. Seen on de2 as two "DOWN -> UP" transitions 3 s apart. The scheduler now also remembers when each check finished.

## 2.17.0

### Added
- **Quorum Also When Only Peers See the Failure**: In 2.16.0 the vote started only when this node's own check failed, so a target this node reached but most other nodes did not (e.g. blocked in one country, broken routing) raised nothing. Now, when a peer's telemetry reports a target DOWN (a result at most 5 minutes old) that is UP here, in a `quorum` chat, the target's next regular check asks all peers and votes: most nodes cannot reach it → 🔴 DOWN; some cannot → 🟠 DEGRADED after two votes (about two telemetry rounds). Peers are asked about such a target at most once per 2 minutes, however many of them report it.
- **Status Page**: DEGRADED monitors are shown in orange with their last vote (`🔴 RU · 🟢 DE (40ms), IT (9ms)`), the header says "N Service(s) Unreachable From Some Regions" when nothing is down but something is degraded, and a "Partial Outages" section lists recent ones (ongoing and ended, with the nodes that could not reach the target).
- **`/events` and `/history <id>`** list partial outages too, marked as not counted as downtime. `/events` no longer says only "No incidents" when there were partial outages.

### Changed
- In quorum results the check error and the vote are separated by " — " instead of nested parentheses, e.g. `timeout — Unreachable from 🇩🇪 DE, 🇷🇺 RU; reachable from 🇮🇹 IT`.

## 2.16.0

### Added
- **Quorum Alerting (`/alertmode quorum`, default for every chat)**: Whether a target is down was decided by this node alone; peers' cross-check answers were only appended to the error text. A problem on this node's own network raised a full DOWN incident even when every other node reached the target. Now, when a target fails here (after the usual two retries and the host connectivity check), this node and its live peers vote:
  - more than half of the voting nodes cannot reach it → 🔴 **DOWN**, an incident as before;
  - some, but not most, cannot reach it → 🟠 **DEGRADED**: a notice in the chat ("Partial Outage"), no incident, not counted as downtime. Entered and left only after two consecutive votes, so a single flap does not notify;
  - fewer than two voters (no live peers, no answers, monitor not shared by `/peershare`) → this node decides alone, as before.
  Votes are per node (RU and RU2 count separately). Offline peers, peers that cannot check the target (IPv6) and peers that `/probeignore` it abstain.
- **Who Can Reach It, in Every Alert**: Incident messages, `/list` and DEGRADED notices show the vote, e.g. `🔴 DE, RU, RU2 · 🟢 IT (196ms)`. The answers are also kept for monitors in `local` mode.
- **`/alertmode [quorum|local]`**: Per chat. `local` keeps the previous behaviour. Without arguments it explains the current mode, how many nodes vote and the majority needed, and warns when the chat's monitors are not shared with peers.
- **Partial outage history**: DEGRADED periods are recorded (`partial_outages`) for the status page and history in the next release.

### Changed
- **`/probeignore` Targets Abstain in Cross-Checks**: A node that ignores a target (e.g. blocked in its region) used to answer cross-checks for it with `down`. It now answers `skip`, so it does not vote.
- **Offline Peers Are Not Asked**: Cross-checks skip peers marked offline instead of waiting for them to time out.
- **DOWN/DEGRADED Targets Ask Peers Less Often**: While a target stays down or degraded and this node's own result does not change, peers are asked again at most every 2 minutes (every 10 minutes after the first hour), not on every check. Retries are no longer repeated every minute for DEGRADED targets.
- `/status` shows degraded monitors and the alert mode; `/list` shows 🟠 DEGRADED.

### Upgrade Notes
- Chats switch to `quorum` automatically. Run `/alertmode local` in a chat to keep the old behaviour.
- Quorum needs peers: with none (or none live) nothing changes. Monitors outside `/peershare` are decided locally.
- Nodes on older versions still vote (they answer cross-checks); only the `/probeignore` abstention needs this version on the ignoring node.

## 2.15.0

Ready for 1000+ monitors. Measured on de2 (148 monitors) the bot used 1.5 % of one core, and a local benchmark put the bot's own work at about 0.15 ms of CPU per check (plus 1-3 ms for a TLS handshake), so CPU is not what limits it; the changes below address what does.

### Changed
- **Hung targets no longer block the queue**: a `HEAD` request that times out (or cannot connect: refused, DNS, certificate) is no longer repeated as `GET`, which held a check slot for a second full timeout. Up to 200 checks run at once instead of 50 (`CHECK_CONCURRENCY`; HTTP connection pool 250, since aiohttp counts the wait for a pooled connection against the timeout), and `docker-compose.yml` raises the open-file limit from 1024 to 8192. 300 targets that accept connections but never answer: 131 s before, 21 s now - before, they delayed every other check past its one-minute interval.
- **Batched peer cross-checks**: failing monitors found within 5 seconds are sent to each peer in one `[UPTIME_PEER_CHECK_BATCH_REQ]` message (up to 100 targets, identical targets once), answered with one `[UPTIME_PEER_CHECK_BATCH_RESP]`; the peer runs them 20 at a time. Before, each failing target sent a message to every peer and got one back - 600 mails per peer a minute for 300 failing targets, far over the relays' 60 messages a minute. Bots announce support with `caps: ["batch_check"]` in telemetry and check messages; until a peer has announced it, it gets the old one-target requests, so mixed versions keep working. Answers are only accepted from the chat the batch went to; URLs are taken from the request, the peer's answer only fills positions; refused targets keep their position as "Target refused".
- **Telemetry with changes first**: with more than 200 targets per peer, each message starts with the targets whose status changed since the last one and fills the rest by rotation over the whole list, so a status change reaches peers within 2 minutes even with 1000+ monitors (before: up to 10 minutes). 200 per message stays, as receivers take no more.
- **Quiet logs**: `Check result` lines are INFO only for DOWN results and status changes, routine UP results and `Triggering N target checks` are DEBUG, and a summary is logged once a minute: `Checks in the last 60s: 148 (146 up, 2 down, 0 skipped), avg latency 87 ms, slowest … ; running now: 3`. At 1000 monitors the per-check lines alone filled Docker's 30 MB log rotation in 2-3 hours.
- **One DB transaction per check**: the status of every monitor of a target and the local peer measurement are written together (`database.record_check_results`) instead of in 2+ transactions. Results are still written right away: deferring them would let the scheduler re-read an old `last_checked` and run the same check twice.

## 2.14.0

### Added
- **IPv6 targets**: `/ping` and `/add` accept IPv6 addresses - `2a00::1` or `[2a00::1]` (ICMP ping), `[2a00::1]:443` (TCP; with a port the address goes in brackets, as in URLs, because `2a00::1:22` is itself a valid address). Addresses are stored normalized (compressed, lowercase). Private, link-local and loopback IPv6 addresses stay blocked.
- **`/ping -4` / `/ping -6`**: check a name only over IPv4 / IPv6, like `ping -4/-6`. The flag is sent to the other regions too (older peers ignore it and check either family); a name without an address of that family gets "has no IPv6 address". The `/add` hint is left out, since monitors have no family setting; `/add -6` explains to add the address itself.

### Fixed
- **IPv6 address read as host:port**: `/ping 2a00:da00:f443:e900::1` was parsed as a TCP check of `2a00:da00:f443:e900:` on port 1 and failed with "Name or service not known".
- **No IPv6 on a node is not an outage**: before connecting, the bot asks the kernel for a route to each IPv6 address (a UDP `connect()`, which sends nothing). Unroutable IPv6 addresses are dropped, so a host with A and AAAA records is checked over IPv4 instead of failing with `[Errno 101] Connect call failed ('2a00:…', 22)`. An IPv6-only target on such a node is skipped - no retries, no peer cross-check, no alert, status unchanged - and `/ping` shows ⚪ "Not checked" with the verdict of the other regions. Peers answer such requests with status `skip` (shown as ⚪). `/add` of an IPv6 target warns when this node has no IPv6.
- **TCP error of the preferred address**: when every address of a host fails, the error of the first one (IPv4 first) is reported instead of the last one.
- **Peer measurements of IPv6 targets**: check responses were classified as TCP whenever the target contained ":", so IPv6 ping targets were dropped as unsafe; the type now comes from the same parser as `/add`.

## 2.13.0

### Changed
- **Peers Identified by Key Fingerprint, Not Address**: Since Delta Chat 2.61 a bot can have several relays and sends from whichever one is reachable. Peers were stored and matched by email address, so as soon as a peer switched relays (e.g. `ruptimebo@chat.gluek.info` → `ruptimebot@chatmail.uk`) its telemetry, cross-check requests and answers were dropped as coming from an "untrusted sender", although they arrived end-to-end encrypted, from the same key, in the same 1:1 chat. Each peer now stores its OpenPGP fingerprint:
  - taken from the invite when adding a peer with `/addpeer <link>`, from an encrypted `HELLO` when a bot pairs with an `/invitepeer` token, or from the first encrypted message for existing peers;
  - incoming peer messages are matched by fingerprint first; the stored address and 1:1 chat follow the peer, and probe targets it mirrored to this node move with it;
  - once a key is bound, a message from the peer's address signed by another key (or unencrypted) is rejected, which is stricter than the address check before.
- **Cross-Check Answers Matched by Chat**: Answers are expected from the 1:1 chats the request was sent to instead of from the addresses, so a peer answering via another relay is still counted.
- **`/peers` Shows Keys, `/rmpeer` Accepts Them**: `/peers` shows the first 16 hex digits of each peer's key (or "not bound yet"). `/rmpeer` accepts the current address, the full fingerprint or a unique prefix of at least 8 hex digits.
- **Re-adding a Known Bot**: `/addpeer <link>` for a bot whose key is already a peer updates that peer instead of creating a second entry.

### Upgrade Notes
- No action needed. Existing peers are bound to their key on their first encrypted message: in their 1:1 chat (also when they already send from a new address) or from their stored address. Peers that switched relays before this release recover on the next telemetry round (every 2 minutes).
- All nodes should run 2.13.0: an older node still drops this node's messages once this node sends from another relay.

## 2.12.1

### Added
- **MIT License**: the project is now licensed under MIT (`LICENSE`).

### Fixed
- **Crash Risk in DNS Pinning**: 2.12.0 created and closed a new aiodns/pycares resolver for every lookup. Queries cancelled by a timeout were torn down mid-flight, and pycares destroys channels in a background thread that can crash the interpreter at shutdown (the test run on `main` ended with SIGBUS, exit code 135, after the PR run had passed). Lookups now share one long-lived resolver per event loop, which is how aiodns is meant to be used.
- **Tests Made Hermetic**: Some peer and redirect tests performed real DNS queries, which only happened in CI (where the network is reachable). All tests now stub DNS, and CI runs with `-X faulthandler` so a native crash prints a traceback.

## 2.12.0

### Security
- **No More Automatic Peering**: Any Delta Chat user could send a `[UPTIME_PEER_HELLO]` message to the bot, be added as a peer automatically and from then on receive every monitor of every chat every 2 minutes. An unknown bot is now only accepted as a peer if it presents a single-use token from `/invitepeer` (valid 24h); the admin is notified when that happens. `HELLO_ACK` is only accepted from bots the admin added. Without a token, both admins have to run `/addpeer` for each other.
- **Peer Messages Only From Peers**: `CHECK_REQ`, `CHECK_RESP` and `METRICS` were processed from any sender, so anyone could make the bot probe arbitrary hosts, plant up to 200 probe targets per message and inject fake per-node results into public status pages. They are now accepted only from configured peers, in a 1:1 chat and end-to-end encrypted (padlock). The sender is taken from the Delta Chat contact only; `sender_email` and `node_name` in the payload are no longer trusted.
- **Cross-Check Responses Bound to Requests**: A response is only accepted for a pending `req_id`, from a peer the request was sent to, once per peer. Request IDs are now 96-bit.
- **Controlled Disclosure (`/peershare admin|all|none`)**: Telemetry and cross-check requests now include only monitors from chats the administrator is a member of (`admin`, default). `all` restores the previous behaviour, `none` shares no local monitors. Monitor names are no longer sent. `/ping` from non-admin users reaches peers only with `all`.
- **No Relaying of Mirrored Targets**: Targets one peer asked this node to probe are reported back only to that peer instead of being forwarded to every other peer (and from there further across the mesh). Each peer can make this node probe at most 200 targets; `/rmpeer` removes the targets mirrored from that peer.
- **SSRF via Redirects**: HTTP checks and `/ping` title fetches followed redirects without re-validating them, so a public URL could redirect the probe to `127.0.0.1` or cloud metadata addresses. Redirects are now followed manually (at most 10) and every hop is checked by the SSRF filter.

- **DNS Rebinding Protection**: Targets were validated with one DNS lookup and then connected to after a second, independent lookup, so a hostname could answer with a public address during validation and with `127.0.0.1` or a cloud metadata address at connect time. All probe connections (HTTP checks, redirects, TCP, ping, SSL expiry, `/ping` title fetch) now go through one resolver that checks every address and pins the validated answer for the record's TTL (clamped to 30–300 s, 60 s when the TTL is unknown). After expiry the new answer is validated again. HTTP checks use a custom aiohttp resolver; TCP, ping and SSL checks connect to the validated IP; the title fetch connects to the pinned IP with the original hostname for SNI and no longer uses environment proxies. DNS is now resolved asynchronously (aiodns, falling back to the system resolver for `/etc/hosts`) instead of blocking the event loop on every check.

### Fixed
- **TCP Targets With IPv6 Literals**: `[::1]:22` style targets were not recognised as IP literals by the SSRF filter.
- **SecureJoin Peers With Unknown Address**: A peer stored under the `peer_<chat>@securejoin` placeholder never matched incoming messages. The placeholder is now replaced with the real address on the first message in that chat.

### Upgrade Notes
- Existing peers keep working. Pairing with a new bot requires the `/addpeer ... token=...` command printed by `/invitepeer` (or `/addpeer` on both sides).
- Unencrypted peer telemetry is dropped. Bots exchange keys during the HELLO handshake, so this only affects peers on classic email providers without Autocrypt.
- If you relied on peers seeing monitors of all chats, run `/peershare all`.

## 2.11.1

- **User-Agent No Longer Contains "Bot"**: HTTP checks now send `Delta Chat Uptime Monitor/<version> (+https://git.gluek.info/gluek/deltachat_uptime)` instead of `DeltaChat-Uptime-Bot/...`. Hiddify Manager (and other services that block crawlers) answered `400 Bad Request` to any User-Agent containing "bot", so working subscription links showed as down while they opened fine in a browser.

## 2.11.0

- **`/transports` Shows the Relay Actually Used for Sending**: Since core 2.61 the core sends through the relay that last worked and switches only when it cannot connect, so the main address (`configured_addr`) says nothing about where mail goes out. `/transports` now lists relays in the order the core tries them, with the current sending relay first, shows the core's send queue (waiting messages and retries) and outgoing status, and per relay the incoming status, when the last message arrived, mailbox storage usage (⚠️ from 80%) and when it was added. The sending order and queue are read from the core's account database (read-only); the report is built by the shared `transports_view.py`.
- **Removed Misleading Per-Relay Sent/Received Counters**: They credited every message to `configured_addr` (or, in some places, the wrong address), so the numbers and "last sent" dates were wrong once the core sent through another relay. Counting them also cost extra RPC calls per message. The `transport_stats` table is left in place but no longer updated.

## 2.10.0

### Removed
- **Bot-Side Relay Failover**: Removed the `MSG_FAILED` failover handler and the resilient-send `send_msg` patch. Both switched `configured_addr` and called `resend_messages`, but since Delta Chat core 2.61 the SMTP relay is no longer chosen by `configured_addr`: the core tries the newest relay first and falls back to the next one if a relay is unreachable. The old logic could no longer switch relays and only caused delayed duplicate resends.

### Changed
- **`/setprimary` and `/resilient` Deprecated**: Both commands are disabled and only reply with an explanation of how the core picks relays now. They are removed from `/help` and the README.
- **`/transports` Sending Order**: Relays are listed newest first, in the order the core tries them for sending, instead of marking `configured_addr` as "Used for sending".
- **Core Requirement**: `requirements.txt` now requires `deltachat-rpc-server>=2.62.0`.

## 2.9.7

### Fixed
- **`update.sh` Deployed the Wrong Branch**: Branch detection took the first remote branch in alphabetical order, so a leftover PR branch such as `origin/claude/...` sorted before `origin/master` and was deployed instead (and new `master` commits were reported as "Already up to date"). It now follows the checked-out branch, falling back to `main`/`master`.

## 2.9.6

### Changed
- **Private `/help` in Groups**: A plain `/help` sent in a group chat is now answered in a private 1:1 chat with the sender instead of the group, so several bots don't flood it with help texts (the reply ends with a note on how to show it in the group). Addressed `/help@uptime` is still answered in the group. Previously a plain `/help` was answered in the group, or silently ignored when other bots were present.

## 2.9.5

### Fixed
- **False SSRF block for hosts with Yggdrasil IPv6 records**: Domains publishing an AAAA record in the Yggdrasil mesh range (`200::/7`, e.g. `cm1.wwire.su`) were rejected with "Target blocked: internal or private network address", because Python's `ipaddress` flags that range as reserved. Yggdrasil addresses are now treated as routable, while other reserved ranges stay blocked. IP checks are consolidated in a new `_is_blocked_ip()` helper.

## 2.9.4

### Security
- **SSRF & DNS Rebinding Hardening**: Added DNS resolution check in `is_safe_target_url()` ensuring domains resolving to loopback, private, link-local, cloud metadata, or reserved ranges are rejected. Blocked `.local`, `.internal`, `.lan`, `.localdomain` suffixes. Added SSRF validation to `/add`, `fetch_html_title`, and `run_single_check`.
- **Request Body Limits & Rate Limiting**: Added `client_max_size=256KB` on web server and sliding-window rate limiting on public web endpoints with HTTP 429 `Retry-After: 60`.
- **Dependency Pinning**: Pinned dependencies to secure ranges in `requirements.txt`.

## 2.9.3

### Added
- **Auto-Memorization of GET Method on HTTP 405 (Method Not Allowed)**:
  - When a target server responds with `405 Method Not Allowed` to a lightweight `HEAD` probe (common on GoToSocial, Mastodon, and specialized web frameworks that disallow HEAD on root or API endpoints), the bot now automatically remembers `GET` as the preferred method for that monitor and URL.
  - Persisted to database via new `http_method` column in `resources` and `probe_targets` tables, and synchronized with active in-memory scheduler caches.
  - Subsequent minute checks bypass the `HEAD` attempt and directly issue `GET` requests, eliminating redundant `405` error log entries on target servers and halving network overhead for those endpoints.

## 2.9.2

### Fixed
- **Persistent SQLite Writer Connection & Elimination of Continuous Disk Writes**:
  - Resolved root cause of continuous disk I/O (~500 kB/s on Linux ext4 / `jbd2` journal): SQLite in WAL mode defaults to connection-scoped `synchronous = FULL`, causing `fdatasync()` on every single commit. When combined with ephemeral per-operation database connections, every monitor check caused repeated WAL header synchronizations and ext4 journal commits.
  - Implemented a dedicated persistent writer connection (`_writer_conn`) and `_writer_transaction()` context manager under `_write_lock`, eliminating per-check connection open/close churn and reusing the connection across all database writes.
  - Enforced `PRAGMA synchronous = NORMAL;` across all reader and writer connections. In WAL mode, `NORMAL` guarantees full ACID durability and WAL crash-safety while eliminating `fdatasync()` during transaction commits, reducing fsync operations by >98% (from 400+ calls per 100 commits to 0 during commits).
  - Added `close_db()` lifecycle helper for clean connection teardown and test isolation.

## 2.9.1

### Fixed
- **Container Environment Compatibility (`socket.getprotobyname("icmp")` / `OSError: protocol not found`)**:
  - Added a defensive IANA protocol number fallback (`IPPROTO_ICMP = 1`, `IPPROTO_ICMPV6 = 58`) for `socket.getprotobyname` during `aioping` initialization, preventing startup crashes in minimal container base images lacking `/etc/protocols` (such as Debian minimal without `netbase` or minimal Alpine in Home Assistant Add-ons).
  - Widened `import aioping` and `import aiodns` exception handling to catch all `Exception`/`OSError` types, guaranteeing safe fallback to `/bin/ping` subprocesses if socket initialization fails for any reason.
  - Added `netbase` to `Dockerfile` dependencies to supply `/etc/protocols` out-of-the-box.

## 2.9.0

### Added
- **Native Async ICMP Ping (`aioping`)**:
  - Integrated `aioping` for native in-process ICMP echo requests, avoiding OS subprocess spawning overhead on ping monitors.
  - Implemented graceful fallback: automatically falls back to system `/bin/ping` subprocess if `aioping` is unavailable or if raw socket permissions (`CAP_NET_RAW`) are restricted.
- **Asynchronous DNS Resolver & 5-Minute DNS TTL Caching (`aiodns`)**:
  - Added `aiodns` integration with `aiohttp.AsyncResolver`, eliminating blocking system `getaddrinfo` calls from thread pools during routine HTTP/HTTPS checks.
  - Configured 5-minute DNS caching (`ttl_dns_cache=300, use_dns_cache=True`) across the shared monitoring session.
- **Deterministic Time Slot Staggering**:
  - Implemented uniform deterministic phase staggering (`(r_id * 11) % interval`) to evenly distribute monitor checks across 5-second execution windows, eliminating thundering-herd CPU/network spikes on bot startup and synchronized intervals without expensive hashing.
- **Concurrent Lock-Free SQLite WAL Reads (`_write_lock`)**:
  - Separated SQLite synchronization into a dedicated `_write_lock` for database mutations (`INSERT`, `UPDATE`, `DELETE`, batch updates, and pruning).
  - Unlocked all read-only queries (`SELECT`) with `_connect()` and `PRAGMA busy_timeout = 5000`, enabling parallel non-blocking reads across web status dashboards, commands (`/status`, `/list`), and background workers.
  - Maintained `_lock = _write_lock` alias for full backwards compatibility.

### Changed
- **Two-Tier HTTP Monitoring Strategy (`HEAD` -> `GET`)**:
  - For standard HTTP/HTTPS monitors without keyword assertions, the bot now issues a lightweight `HEAD` request first (transferring 0 body bytes and 0 CPU decode overhead).
  - Automatically falls back to `GET` reading at most 16 KB (`16384` bytes) if the server returns non-2xx/3xx (e.g. `405 Method Not Allowed`) or on connection errors.
  - When custom keyword assertions are configured, direct `GET` is used with body reading capped at 128 KB (`131072` bytes, reduced from 256 KB).
  - `fetch_html_title` buffer reduced from 64 KB to 16 KB (`16384` bytes).

## 2.8.0

### Added
- **Performance Indexes for SQLite**:
  - Added indexes on `downtime_events` (`went_up_at`, `(resource_id, went_down_at, went_up_at)`), `incidents` (`(dc_chat_id, status)`, `resolved_at`), `resources` (`(dc_chat_id, status)`, `url`, `status`), `peers` (`last_seen`), and `peer_measurements` (`last_checked`) to eliminate full table scans during checks, audits, and cleanup.
- **Dedicated Thread Pools for DB vs RPC**:
  - Introduced separate `db_executor` (for fast non-blocking SQLite operations) and `rpc_executor` (for Delta Chat JSON-RPC and SMTP network operations) via `run_db` and `run_rpc`, preventing slow email delivery from exhausting worker threads.
- **In-Memory Uptime TTL Cache & Batch Calculation**:
  - Implemented `_uptime_cache` with a 60-second TTL and `get_resources_uptime_30d` for single-query batch calculation across all monitors in a chat, eliminating N+1 query patterns on web status dashboards, `/list`, and `/status`.
  - Added cache invalidation on status transitions, resource deletions, and maintenance cleanup.
- **Batch Check Status Updates**:
  - Implemented `batch_update_resource_status` to commit grouped check results in a single transaction under the database lock.
- **Non-Blocking Check Concurrency Semaphore**:
  - Refactored `check_group_task` with `check_network_probe` to hold the concurrency semaphore only during physical network probes. Retry backoff sleeps (30s) and remote peer cross-checks now run without holding semaphore slots, preventing failing endpoints from starving healthy monitors.
- **Incident Sync Lock Pruning**:
  - Added `prune_incident_sync_locks` to automatically evict idle, unlocked chat incident synchronization locks, preventing unbounded in-memory dictionary growth over long operational periods.
- **Standardized Admin Authentication**:
  - Added standardized `get_admin_email`, `set_admin_email`, `get_admin_fingerprint`, `set_admin_fingerprint`, and `is_authorized_sender` in `database.py`.
- **New Unit Test Suite**:
  - Added `tests/test_database.py` covering schema indexes, batch uptime calculation, caching, status updates, and admin handling, bringing test coverage to 88 automated tests.

## 2.7.7

### Security
- **Credential Protection in `/addtransport`:**
  - Restricted `/addtransport` exclusively to private 1:1 chats with the bot, protecting passwords and chatmail tokens from accidental exposure in group chats.
- **Sanitized Command Error Messages:**
  - Sanitized exception disclosures across administrative commands (`/rmaccount`, `/addtransport`, `/rmtransport`, `/setprimary`, `/resilient`, `/invite`, `/addpeer`) to prevent internal system or credential leakages in chat replies.
- **Resilient Sending Concurrency Protection:**
  - Synchronized initial message queueing inside `resilient_lock` to eliminate data races with background transport failover workers.

### Performance & Optimization
- **Single Atomic Write for Status & Latency:**
  - Merged routine check latency and status updates into a single atomic SQLite transaction, cutting database disk write operations in half.
- **Shared HTTP Connection Pooling:**
  - Transitioned routine monitoring HTTP checks to a persistent shared `aiohttp.ClientSession` with connection pooling, DNS caching, and TCP keep-alive, significantly reducing socket and SSL handshake CPU overhead.
- **Buffered Transport Stats:**
  - Introduced in-memory buffering for transport send/receive statistics with periodic flushing (and automatic flush-on-read), eliminating per-message synchronous disk writes.
- **Scheduler Cache Optimization:**
  - Preserved resource schedule cache across active checks instead of invalidating it every 5-second tick, drastically reducing full-table database scans.
- **Automated Database Maintenance:**
  - Added scheduled pruning (`database.cleanup_old_records`) of resolved downtime events, closed incidents older than 90 days, and stale peer measurements older than 7 days.
- **Rate Limiting on Diagnostic Checks:**
  - Added a 15-second per-chat anti-spam cooldown on `/ping`, `/check`, and `/test` commands with administrator bypass to prevent resource exhaustion.

## 2.7.6

### Fixed
- **Home Assistant Display Name & Status Text Configuration:**
  - Added direct fallback reading of `/data/options.json` in `on_init` for `display_name` and `status_text`, ensuring custom display names configured in Home Assistant Add-on settings are always applied even if environment variables are not exported.

## 2.7.3
### Added
- **ASCII QR Code in Startup Logs:**
  - Render ASCII QR code directly into stdout on bot startup for easy terminal and container log onboarding.
  - Added line-buffering and explicit flushing for container environments (Docker, Home Assistant Add-on).

### Fixed
- **Relative Web Asset URLs for Ingress:**
  - Changed absolute `/icon.png` and `/favicon.ico` paths to relative (`icon.png`, `favicon.ico`) in both dashboard and index HTML templates so logos and favicons load correctly under Home Assistant Ingress reverse proxy paths.
- Set default `chatmail_qr` server (`dcaccount:https://chat.gluek.info/new`) for zero-configuration startup.

## 2.7.2
- Initial Home Assistant Add-on release.
- Home Assistant Ingress web dashboard integration on port 8081.
- Automatic account provisioning and ASCII QR code invite logging.
- Parallel multi-region cross-checks in `/ping`.
