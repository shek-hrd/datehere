# MeshNet (complete project)

Foregrounds the full extracted project objective: TDD, Hamachi/Skype-like router-node-each mesh, Wi-Fi/BT/near-neighbors channel model, IPv6-first 1-UDP-port compression-encrypted peer links, slow bootstrap invites (QR/NFC/BLE/paste), no fixed ports (OS-assigned, optional prime preference 49152-65535), no pi-sync/time-server chain, 2 nodes suffice without Internet, `?` in every client, hail on connect, routes visualized, and a live session beacon showing **Blockchain of messages (common chat)** and **Sensei Network Map** (responsive animated pop-in for new nodes).

## Install (terminal-installable)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .[dev]
```

## CLI
```bash
meshctl help
meshctl invite --nickname terminal-node --host ::1
meshctl serve-web
meshctl demo
```

## Tests
```bash
pytest
```

## Live session
`meshctl serve-web` starts an OS-assigned session beacon. Open the printed URL in several browsers, click **Join as browser node**, and observe the Blockchain of messages and Sensei Network Map updates.

## Outputs
- Launchable HTML session client: `dist/meshnet.html` (or served by beacon)
- Terminal installable package/project: `meshnet_project/` (+ distributable archive)
- Android APK build project: `android_apk_project/` (+ archive); build APK with Android/Gradle toolchain

## Android APK build
```bash
cd android_apk_project
./gradlew assembleDebug
./gradlew assembleRelease
```
(Requires Android SDK/JDK/Gradle environment.)
