You are invited to contribute to development and testing of **MeshNet** (an existing, in-progress project). Please read this context carefully, preserve existing work, and collaborate in a test-driven, practical way.

## Repository / starting point
- GitHub: https://github.com/shek-hrd/datehere
- Branch to work from: `kilo/fancy-gecko-bz1` (latest: `33049b8`)
- Key contents:
  - `meshnet_colab_envelope.ipynb` — complete Colab envelope (**Runtime → Run all**): builds project, runs tests, starts live simulation/session, generates artifacts, and includes best-effort Colab APK-build + download-initiation cells.
  - `meshnet_project/` — Python package/core (`meshnet/`) + CLI (`meshctl`) + tests (`pytest`).
  - `dist/` — generated artifacts: `meshnet.html` (launchable live session client), `meshnet_terminal_installable.tar.gz`, `meshnet_android_apk_project.tar.gz`, `meshnet_release_artifacts.tar.gz` (and `meshnet-debug.apk` if/when built).
  - `android_apk_project/` — buildable/launch-ready Android APK scaffold (Gradle/Kotlin, bundled UI asset).
  - `server/` — **pre-existing** WebRTC network-dating-signaler; **do not break or remove it**.

## Complete project objective (must guide all work)
Build and demonstrate MeshNet as a **test-driven**, Colab-importable, Hamachi/Skype-like **router-node-each** peer mesh:
- **Channels/transports:** clever use of available communication channels — Wi-Fi, Bluetooth, near-neighbors sensing tricks (if allowed) — with channel abstraction/simulation and a real-transport integration path. Higher usage/density → higher bandwidth/baudrate/stability (adaptive capacity model).
- **Connectivity/protocol:** IPv6-first; slow/bootstrap contact signals (QR/NFC/BLE/manual paste/local beacon invite) exchange signed invitation material, then establish peer-to-peer **one-UDP-port, compression-encrypted** connections. **No fixed ports** (OS-assigned `port=0` by default; actual endpoint in invite/UI; optional prime-port preference in dynamic range 49152–65535). **No pi-sync/time-server chain** (use monotonic clocks + peer heartbeat/ACK/liveness/RTT). **Two connected nodes suffice with no Internet required**; transparent across networks where possible. Routes visualized in common chat; physical location secondary/no importance.
- **Identity/chat/proof:** P2P chat showing ping distance (hops/path/latency) and pregenerated/accepted unique nicknames; common chat and invite/group chats. On connect each node **hails** others in common chat with details (nickname, platform, node_id, udp_port/endpoint, peers) to prove communication. **`?` in every client** reveals the complete objective and commands.
- **Common chat ledger/UI:** **Blockchain of messages** (append-only, hash-linked: index, timestamp, prev_hash, hash, author/kind/payload/route/hops), visible in the live session. Live HTML session shows **Sensei Network Map** (responsive animation; newly joined nodes smoothly pop in) and multi-browser join.
- **Platforms/outputs:** simulate several nodes of different types/platforms (Android, bash/terminal, web/browser). Goals: several browser sessions, several terminals, and one Android app exchanging messages. Outputs: **APK** (buildable/compiled), **terminal-installable** production package, and **launchable HTML**.
- **Runtime:** keep simulation running and provide a testing link openable in several browsers to join and see the Blockchain of messages in the live session node.

## Current implementation status (what exists now)
- Core modules: `objective`, `blockchain`, `invite` (signed), `envelope` (authenticated encrypted, replay/sequence checks), `compression`, `port_selection`, `routing` (reroute/heal), `node`, `mesh` (chat/groups/ping/hail/blockchain/snapshot), `transport_udp` (asyncio scaffold), `web_beacon` (live session server: `/`, `/api/state`, `/api/join`, `/api/chat`, `/api/help`, polling UI), `cli` (`meshctl`).
- Tests: `test_objective`, `test_blockchain`, `test_invite`, `test_envelope`, `test_compression`, `test_port_selection`, `test_routing`, `test_mesh`, `test_transport`, `test_beacon`.
- Live session: OS-assigned beacon port, multi-browser join, hail on join, hash-linked common-chat blockchain view, animated Sensei Network Map pop-in, background simulation.
- Artifacts/project scaffolds: launchable HTML, terminal-installable package, Android Gradle/Kotlin APK project scaffold (compiled APK requires Android SDK/JDK/Gradle; notebook includes Colab best-effort build + download initiation).

## Known gaps / high-value next work (production hardening)
- Real end-to-end encrypted UDP session establishment/handshake from signed invites (key agreement), ACK/retransmission, fragmentation/congestion handling, and heartbeat/liveness over actual sockets.
- Signed route announcements (TTL/sequence), richer density-aware link quality, and robust multi-hop relay over real transports.
- Browser real-time relay (WebSocket) backed by the same protocol core; terminal interactive chat/join flow beyond scaffold.
- Native Android implementation: QR/NFC/BLE bootstrap, foreground UDP service, secure key storage, real mesh integration (not only WebView shell), and signed release APK.
- Broaden TDD coverage for failure/rejoin, replay/dup/loss, multi-browser concurrency, and cross-platform integration.

## How to run and test
- **Colab:** open `meshnet_colab_envelope.ipynb` → **Runtime → Run all**. Use the printed testing link (Colab proxy/local) in several browsers, click “Join as browser node”, observe Blockchain of messages and Sensei Network Map.
- **Local/Codespaces/devcontainer:**
  - `python -m venv .venv && source .venv/bin/activate` (or Windows equivalent)
  - `pip install -e meshnet_project[dev]`
  - `pytest`
  - `meshctl help` / `meshctl demo` / `meshctl serve-web` (OS-assigned port; open printed URL)
- **Android APK (when toolchain available):** build from `android_apk_project/` with Android SDK/JDK/Gradle (`./gradlew assembleDebug` or `assembleRelease`).

## How I’d like you to contribute
1. Start by exploring the repo/branch and running the tests and live session to confirm baseline behavior.
2. Propose a focused plan (prioritized, small increments) for the area you’ll improve (e.g. protocol/transport, beacon/multi-browser UX, Android, terminal, tests/CI, or APK build).
3. Work **test-first** where feasible: add/adjust tests, implement, and verify (`pytest`, and manual/live checks as relevant).
4. Keep changes **minimal, consistent, and compatible** with the objective and existing APIs; do not break `server/`; avoid fixed ports and do not reintroduce Internet/time-server dependencies for core mesh operation.
5. Report clearly: what you changed, what you tested (commands/results), what remains, and any risks/assumptions.

Please begin by summarizing your understanding of the current state, the top gaps you see, and the first increment you recommend implementing and testing.
