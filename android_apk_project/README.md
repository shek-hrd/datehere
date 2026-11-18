# MeshNet Android APK Build Project

Buildable/launch-ready scaffold aligned with the complete MeshNet objective:
- QR/NFC/BLE/manual-paste signed invite bootstrap
- One UDP socket per node on OS-assigned port; optional prime-port preference (49152-65535); no fixed port
- Two connected nodes suffice without Internet; no pi-sync/time-server chain
- Compression-encrypted authenticated envelopes, replay/sequence protection, local private keys
- Hail on connect: nickname, platform, node_id, udp_port/endpoint, peers
- '?' complete objective/help, chat/groups, routes/ping visualization
- Blockchain of messages (common chat) and Sensei Network Map responsive UI

## Build APK
Requires Android SDK, JDK 17+, and Gradle (wrapper recommended).

Commands:
    gradle wrapper        # if wrapper not present
    ./gradlew assembleDebug
    ./gradlew assembleRelease

Outputs (when built):
- app/build/outputs/apk/debug/app-debug.apk
- app/build/outputs/apk/release/app-release-unsigned.apk (sign for distribution)

The bundled UI asset (app/src/main/assets/meshnet.html) can connect to a live MeshNet session beacon via ?api=http://host:port.
