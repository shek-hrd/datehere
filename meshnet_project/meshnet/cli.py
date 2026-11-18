"""Terminal CLI (meshctl) - protocol-aligned production scaffold."""

from __future__ import annotations

import argparse
import json

from .invite import create_invite
from .mesh import MeshNetwork
from .objective import HELP_TEXT
from .port_selection import reserve_udp_port
from .web_beacon import start_beacon


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="meshctl", description="MeshNet terminal client")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("help", help="Show complete objective and commands")

    p_inv = sub.add_parser("invite", help="Generate a signed invitation (allocates OS UDP port)")
    p_inv.add_argument("--nickname", default="terminal-node")
    p_inv.add_argument("--host", default="::1")
    p_inv.add_argument("--prefer-prime", action="store_true")

    p_serve = sub.add_parser("serve-web", help="Start live session beacon on OS-assigned port")
    p_serve.add_argument("--host", default="127.0.0.1")

    sub.add_parser("demo", help="Run local demo")

    args = parser.parse_args(argv)

    if args.cmd in (None, "help"):
        print(HELP_TEXT)
        return 0

    if args.cmd == "invite":
        sock, port = reserve_udp_port(host="::", prefer_prime=args.prefer_prime)
        sock.close()
        token, _key = create_invite(node_id="node-cli", nickname=args.nickname, host=args.host, port=port)
        print(json.dumps({"nickname": args.nickname, "host": args.host, "udp_port": port, "token": token}, indent=2))
        return 0

    if args.cmd == "serve-web":
        net = MeshNetwork()
        beacon = start_beacon(net, host=args.host, port=0)
        print(f"Session beacon: {beacon.url}")
        print("Open in browsers to join, view Blockchain of messages and Sensei Network Map. Ctrl+C to stop.")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            beacon.stop()
        return 0

    if args.cmd == "demo":
        net = MeshNetwork()
        a = net.add_node("android-node", platform="android", udp_port=52417)
        b = net.add_node("terminal-node", platform="terminal", udp_port=53128)
        net.connect(a, b)
        net.hail(a); net.hail(b)
        print(net.render_route(a, b))
        print(json.dumps(net.ping(a, b).to_dict(), indent=2))
        print("chain_valid:", net.blockchain.verify(), "blocks:", len(net.blockchain.chain))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
