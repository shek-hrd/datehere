"""Shared complete project objective and help text for all clients (terminal/web/Android)."""

FULL_OBJECTIVE = r"""COMPLETE PROJECT OBJECTIVE
(Extracted and consolidated from the project specification prompts)

MISSION
Build and demonstrate MeshNet as a test-driven, Colab-importable project (single .ipynb envelope, Runtime -> Run all) that launches the whole development, testing, debug, simulation, and packaging flow. Preserve existing repository work and produce/download launch-ready outputs: APK build project, launchable HTML, and terminal-installable production package.

NETWORK CONCEPT
- Hamachi/Skype-like router-node-each infrastructure: every participant is a node that can route/relay for others.
- Clever use of all available communication channels: Wi-Fi, Bluetooth, and near-neighbors sensing tricks (if allowed by the user), with channel abstraction/simulation and a real-transport integration path.
- Density-aware capacity: where higher usage and density exist, higher bandwidth/baudrate and stability are achieved (adaptive channel scoring/capacity model).
- Resilience: easily recognize and incorporate new nodes; maintain stability regardless of some nodes disappearing unexpectedly (reroute/heal).

CONNECTIVITY AND PROTOCOL
- IPv6-first peer networking: transfer contact signals using slow/bootstrap methods, then establish peer-to-peer one-UDP-port, compression-encrypted connections.
- Slow/bootstrap contact channels: QR code, NFC exchange, Bluetooth advertisement, manual paste, or local beacon/invite exchange carrying compact signed invitation material (node identity, nickname, endpoint/key info as appropriate).
- No fixed ports: do not hardcode ports (e.g. 8000). Bind UDP/HTTP to OS-assigned available ports (port=0) by default; invitations/UI carry the actual assigned endpoint. Optional prime-port preference may be applied within the dynamic/private range 49152-65535 (nearest/selected prime) as a preference only - networking simplicity is paramount.
- No pi-sync / no time-server chain: do not require Internet time servers or chained time sync. Use monotonic clocks, local timestamps, and peer heartbeat/ACK semantics for liveness/RTT/timeouts.
- Transparent and simple: work across networks where possible; two connected nodes suffice as a complete connection/mesh with no Internet required.
- Routes, not location: routes are visualized with common chat; physical location is secondary or of no importance.

IDENTITY, CHAT, AND PROOF OF COMMUNICATION
- Peer-to-peer chat showing ping distance (hops/path/latency) and pregenerated/accepted unique nicknames.
- Common chat and invite/group chats (emulated/supported across node types).
- Hail on connect: to prove communication, each newly connected node hails others in common chat with details (nickname, platform/type, node ID, transport/port/endpoint details, peers/context).
- '?' in every client: reveals the detailed complete objective and commands/help (terminal, browser/HTML, Android).
- Blockchain of messages (common chat): common chat is represented as an append-only, hash-linked message chain (index, timestamp, previous hash, hash, author, payload/kind/route metadata) so message history/integrity is visible in the running session.

PLATFORMS AND OUTPUTS
- Simulation: simulate the whole network on several nodes of different type/platform (Android, bash/terminal, web/browser), demonstrating join, hail, chat, ping, groups, reroute, and stability.
- Browser sessions: several browser sessions can open the running session node/page, join, and participate; new nodes smoothly pop in on the Sensei Network Map (responsive animation).
- Terminal: terminal-installable production client/package (meshctl) for invite/join/chat/peers/routes/ping/serve-web/help.
- Android: one Android app/client path exchanging messages with browser/terminal nodes; provide buildable/launch-ready APK project (and compiled APK artifact when toolchain is available).
- Website/HTML: beacon/session HTML page displays common chat and blockchain, serves as joinable session node UI, and is provided as a launchable/downloadable artifact.

OPERATIONAL/RUNTIME GOALS
- Keep simulation running and provide a testing link openable in several browsers to join and see the Blockchain of messages of common chat in the live HTML session node.
- Sensei Network Map: responsive animated network map where nodes/links update and newly joined nodes smoothly pop in.
- Security: signed invitations, authenticated/compression-aware encrypted envelopes, replay/sequence protection, local private keys, no sensitive data leakage in beacon/public views.
- TDD discipline: tests define/validate core behaviors (identity/invites/envelopes/compression/ports/routing/mesh/hail/blockchain/beacon/session APIs); implementation satisfies them.
- Publishing: publish all project materials to GitHub.
"""

OBJECTIVE = FULL_OBJECTIVE

HELP_TEXT = """?
MeshNet complete objective and commands

""" + FULL_OBJECTIVE + """

COMMANDS
  ?                  Show this complete objective/help
  /help              Show this complete objective/help
  /peers             List connected peers and transports
  /routes            Show known routes
  /ping <nickname>   Ping a peer (hops/path/latency)
  /join <room>       Join or create a group chat
  /leave <room>      Leave a group chat
  /invite            Show this node's signed invitation

RUNTIME BEHAVIOR
- On connect, each node sends a HAIL to common chat with details (nickname, platform, node ID, udp_port/endpoint, peers).
- Common chat is an append-only hash-linked Blockchain of messages (index, prev_hash, hash, timestamp, source, payload, route metadata).
- Session UI shows the Sensei Network Map (responsive animation; new nodes pop in smoothly).
- Two connected nodes suffice without Internet; no fixed ports; OS-assigned ports by default.
"""


def show_help() -> str:
    return HELP_TEXT
