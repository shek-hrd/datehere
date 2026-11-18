"""Live session beacon: multi-browser join, Blockchain of messages, Sensei Network Map."""

from __future__ import annotations

import json
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from .objective import HELP_TEXT


class BeaconHandle:
    def __init__(self, server: ThreadingHTTPServer, thread: threading.Thread, url: str, port: int):
        self.server = server
        self.thread = thread
        self.url = url
        self.port = port

    def stop(self) -> None:
        try:
            self.server.shutdown()
            self.server.server_close()
        except Exception:
            pass
        if self.thread.is_alive():
            self.thread.join(timeout=2.0)


def _json_response(handler, obj: Any, status: int = 200):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler) -> dict:
    try:
        length = int(handler.headers.get("Content-Length", "0") or "0")
    except Exception:
        length = 0
    raw = handler.rfile.read(length) if length > 0 else b"{}"
    try:
        return json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        return {}


HTML_PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>MeshNet Live Session — Blockchain & Sensei Network Map</title>
<style>
:root { --bg:#0b1020; --card:#141b33; --muted:#93a4c7; --text:#eaf0ff; --accent:#6ee7ff; --accent2:#a78bfa; --ok:#34d399; --warn:#fbbf24; }
*{box-sizing:border-box} body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:linear-gradient(180deg,#070b17,#0b1020);color:var(--text)}
header{padding:14px 18px;border-bottom:1px solid #243055;display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}
h1{font-size:18px;margin:0} .sub{color:var(--muted);font-size:13px}
.container{padding:14px;display:grid;grid-template-columns:1.2fr 1fr;gap:14px}
.card{background:rgba(20,27,51,.9);border:1px solid #243055;border-radius:14px;padding:12px;min-height:120px}
.card h2{margin:0 0 8px 0;font-size:15px}
@media (max-width: 980px){.container{grid-template-columns:1fr}}
#mapWrap{width:100%;height:420px;position:relative;border-radius:10px;background:radial-gradient(circle at 30% 20%,#111a33,#0a1022);overflow:hidden;border:1px solid #223055}
svg{width:100%;height:100%;display:block}
.node circle{fill:url(#nodeGrad);stroke:#bfefff;stroke-width:1.5;filter:drop-shadow(0 0 6px rgba(110,231,255,.35));transform-origin:center;transform-box:fill-box}
.node text{fill:#eaf0ff;font-size:11px;pointer-events:none;text-anchor:middle}
.node .meta{fill:#93a4c7;font-size:9px}
.node.pop circle{animation:popin .55s cubic-bezier(.2,.9,.2,1.2)}
@keyframes popin{0%{transform:scale(0.1);opacity:0}60%{transform:scale(1.18);opacity:1}100%{transform:scale(1);opacity:1}}
.link{stroke:rgba(167,139,250,.55);stroke-width:2;stroke-linecap:round;opacity:.9}
.link.new{animation:linkin .6s ease}
@keyframes linkin{from{opacity:0}to{opacity:.9}}
.controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
button,input{border-radius:10px;border:1px solid #2a3a66;background:#0e1630;color:var(--text);padding:8px 10px}
button{cursor:pointer;background:linear-gradient(180deg,#18244a,#101938)} button:hover{border-color:#4b6cb7}
input{min-width:180px}
.pill{display:inline-block;padding:2px 8px;border-radius:999px;background:#102044;border:1px solid #2b3f70;color:#cfe3ff;font-size:12px;margin-left:6px}
#chat{max-height:420px;overflow:auto;display:flex;flex-direction:column;gap:8px;padding-right:4px}
.block{border:1px solid #2a3a66;border-radius:10px;padding:8px;background:#0e1630}
.block .top{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;font-size:12px;color:var(--muted)}
.block .payload{margin-top:4px;white-space:pre-wrap;word-break:break-word}
.hash{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;color:#a5b4fc}
.muted{color:var(--muted)} .ok{color:var(--ok)} .warn{color:var(--warn)}
#helpPanel{display:none;position:fixed;inset:5% 6%;background:#0b1124;border:1px solid #334155;border-radius:14px;padding:14px;z-index:50;overflow:auto;box-shadow:0 20px 60px rgba(0,0,0,.6)}
#helpPanel pre{white-space:pre-wrap;color:#dbe7ff;font-family:ui-monospace,Menlo,monospace;font-size:12px}
#overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:40}
.row{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.small{font-size:12px}
footer{padding:8px 14px;color:var(--muted);font-size:12px}
</style>
</head>
<body>
<header>
  <div>
    <h1>MeshNet Live Session <span class="pill">Blockchain of messages</span> <span class="pill">Sensei Network Map</span></h1>
    <div class="sub">No fixed ports · OS-assigned endpoint · 2 nodes suffice · No Internet required for mesh core · Live multi-browser join</div>
  </div>
  <div class="controls">
    <button id="helpBtn">?</button>
    <button id="joinBtn">Join as browser node</button>
    <span id="me" class="muted">not joined</span>
  </div>
</header>
<div class="container">
  <section class="card">
    <h2>Sensei Network Map <span id="nodeCount" class="pill">0 nodes</span> <span id="linkCount" class="pill">0 links</span></h2>
    <div id="mapWrap">
      <svg id="map" viewBox="0 0 900 420" preserveAspectRatio="xMidYMid meet">
        <defs>
          <radialGradient id="nodeGrad" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stop-color="#9ff3ff"/><stop offset="100%" stop-color="#4f46e5"/>
          </radialGradient>
        </defs>
        <g id="links"></g>
        <g id="nodes"></g>
      </svg>
    </div>
    <div class="row small muted">
      <span>New nodes smoothly pop in when they join. Routes/links update responsively.</span>
      <span id="status"></span>
    </div>
    <div class="row">
      <input id="chatInput" placeholder="Type message and press Enter (join as browser node to send as yourself)" />
      <button id="sendBtn">Send</button>
    </div>
  </section>
  <section class="card">
    <h2>Blockchain of messages (common chat) <span id="chainInfo" class="pill">verifying…</span></h2>
    <div id="chat"></div>
  </section>
</div>
<div id="overlay"></div>
<div id="helpPanel"><div style="display:flex;justify-content:space-between;align-items:center"><h2 style="margin:0">? Complete Objective &amp; Commands</h2><button id="closeHelp">Close</button></div><pre id="helpText"></pre></div>
<footer>Open this same testing link in several browsers, click "Join as browser node", and watch nodes pop into the Sensei Network Map while the message blockchain grows.</footer>
<script>
const state = {data:null, knownNodes:new Set(), knownLinks:new Set(), joinedId:null};
const el = id => document.getElementById(id);
async function api(path, opts){
  opts = opts || {};
  const base = {headers:{'Content-Type':'application/json'}};
  const r = await fetch(path, Object.assign(base, opts));
  return r.json();
}
function esc(s){return (s==null?'':String(s)).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];});}
function shortHash(h){return h? (h.slice(0,10)+'…'+h.slice(-8)) : '';}
function hashCode(s){s=String(s||''); var h=0; for(var i=0;i<s.length;i++){h=((h<<5)-h)+s.charCodeAt(i); h|=0;} return Math.abs(h);}
function layout(nodes){
  var w=900,h=420,cx=w/2,cy=h/2; var n=nodes.length||1; var R=Math.min(w,h)*0.33 + Math.min(40,n*2);
  var pos={};
  nodes.forEach(function(node,i){
    var a=(Math.PI*2*i)/n - Math.PI/2;
    var jitter=((hashCode(node.nickname)%7)-3)*6;
    pos[node.nickname]={x:cx + (R+jitter)*Math.cos(a), y:cy + (R+jitter)*Math.sin(a)};
  });
  return pos;
}
function renderMap(data){
  var nodes = data.nodes||[]; var links=data.links||[];
  var pos = layout(nodes);
  var linksG = el('links'); var nodesG = el('nodes');
  linksG.innerHTML = links.map(function(l){
    var a=pos[l.source], b=pos[l.target]; if(!a||!b) return '';
    var k=l.source+'--'+l.target; var cls = state.knownLinks.has(k)?'link':'link new'; state.knownLinks.add(k);
    return '<line class="'+cls+'" x1="'+a.x+'" y1="'+a.y+'" x2="'+b.x+'" y2="'+b.y+'" />';
  }).join('');
  nodesG.innerHTML = nodes.map(function(n){
    var p=pos[n.nickname]||{x:450,y:210}; var isNew=!state.knownNodes.has(n.nickname); state.knownNodes.add(n.nickname);
    var cls = 'node' + (isNew?' pop':'');
    var label = esc(n.nickname);
    var meta = esc(n.platform + ' · udp:' + (n.udp_port!=null?n.udp_port:'n/a') + ' · peers:' + ((n.peers||[]).length));
    var shortLabel = label.length>14?label.slice(0,13)+'…':label;
    var shortMeta = meta.length>30?meta.slice(0,29)+'…':meta;
    return '<g class="'+cls+'" transform="translate('+p.x+','+p.y+')">' +
      '<circle r="22"></circle>' +
      '<text y="4">'+shortLabel+'</text>' +
      '<text class="meta" y="38">'+shortMeta+'</text>' +
    '</g>';
  }).join('');
  el('nodeCount').textContent = nodes.length + ' nodes';
  el('linkCount').textContent = links.length + ' links';
}
function renderChain(data){
  var chain = (data.chain||[]).slice().reverse();
  var valid = !!data.chain_valid;
  el('chainInfo').textContent = (valid?'valid':'INVALID') + ' · ' + (data.chain?data.chain.length:0) + ' blocks';
  el('chainInfo').className = 'pill ' + (valid?'ok':'warn');
  el('chat').innerHTML = chain.map(function(b){
    var route = (b.path&&b.path.length)?(' · route: ' + esc(b.path.join(' -> ')) + ' (hops ' + (b.hops||0) + ')') : '';
    var t = b.timestamp ? new Date(b.timestamp*1000).toLocaleTimeString() : '';
    return '<div class="block">' +
      '<div class="top"><span>#'+b.index+' · <strong>'+esc(b.source)+'</strong> · '+esc(b.kind)+route+'</span><span>'+esc(t)+'</span></div>' +
      '<div class="payload">'+esc(b.payload)+'</div>' +
      '<div class="hash">hash: '+shortHash(b.hash)+' · prev: '+shortHash(b.prev_hash)+'</div>' +
    '</div>';
  }).join('');
}
async function refresh(){
  try{
    var data = await api('/api/state');
    state.data = data;
    renderMap(data); renderChain(data);
    if(data.help && !el('helpText').textContent) el('helpText').textContent = data.help;
    el('status').textContent = ' · head ' + shortHash(data.chain_head) + ' · ' + new Date().toLocaleTimeString();
  }catch(e){ el('status').textContent = ' · reconnecting…'; }
}
async function join(){
  try{
    var res = await api('/api/join', {method:'POST', body: JSON.stringify({platform:'web'})});
    if(res && res.node){ state.joinedId = res.node.nickname; el('me').textContent = 'joined as ' + res.node.nickname; el('me').className='ok'; }
    await refresh();
  }catch(e){ console.error(e); }
}
async function send(){
  var text = el('chatInput').value.trim(); if(!text) return;
  try{
    if(text === '?' || text === '/help'){ el('helpPanel').style.display='block'; el('overlay').style.display='block'; el('chatInput').value=''; return; }
    await api('/api/chat', {method:'POST', body: JSON.stringify({from: state.joinedId, text: text})});
    el('chatInput').value='';
    await refresh();
  }catch(e){ console.error(e); }
}
el('joinBtn').onclick = join; el('sendBtn').onclick = send;
el('chatInput').addEventListener('keydown', function(e){ if(e.key==='Enter') send(); });
el('helpBtn').onclick = function(){ el('helpPanel').style.display='block'; el('overlay').style.display='block'; };
el('closeHelp').onclick = function(){ el('helpPanel').style.display='none'; el('overlay').style.display='none'; };
el('overlay').onclick = function(){ el('helpPanel').style.display='none'; el('overlay').style.display='none'; };
refresh(); setInterval(refresh, 1200);
</script>
</body>
</html>
"""


def start_beacon(network, host: str = "127.0.0.1", port: int = 0) -> BeaconHandle:
    """Start live session beacon on OS-assigned port by default (port=0)."""
    state_lock = threading.RLock()

    def ensure_host():
        with state_lock:
            if not network.nodes:
                host_node = network.add_node(nickname="session-host", platform="terminal", udp_port=None)
                network.hail(host_node)

    ensure_host()

    class Handler(BaseHTTPRequestHandler):
        def _send_html(self, body: str, status: int = 200):
            data = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):  # noqa: N802
            try:
                parsed = urlparse(self.path)
                if parsed.path in ("/", "/index.html"):
                    return self._send_html(HTML_PAGE)
                if parsed.path in ("/api/state", "/state.json"):
                    snap = network.snapshot()
                    snap["help"] = HELP_TEXT
                    return _json_response(self, snap)
                if parsed.path == "/api/help":
                    return _json_response(self, {"help": HELP_TEXT})
                self.send_error(404)
            except Exception:
                traceback.print_exc()
                try:
                    self.send_error(500)
                except Exception:
                    pass

        def do_POST(self):  # noqa: N802
            try:
                parsed = urlparse(self.path)
                payload = _read_json(self)
                if parsed.path == "/api/join":
                    with state_lock:
                        ensure_host()
                        platform = str(payload.get("platform") or "web")
                        nickname = payload.get("nickname")
                        node = network.add_node(nickname=nickname, platform=platform, udp_port=None, host="browser")
                        candidates = [n for n in network.nodes.values() if n.node_id != node.node_id]
                        if candidates:
                            target = None
                            for c in candidates:
                                if c.nickname == "session-host":
                                    target = c
                                    break
                            if target is None:
                                target = candidates[0]
                            network.connect(node, target)
                        network.hail(node)
                        snap = network.snapshot()
                        snap["help"] = HELP_TEXT
                    return _json_response(self, {"ok": True, "node": {
                        "id": node.node_id, "nickname": node.nickname, "platform": node.platform,
                        "udp_port": node.udp_port,
                        "peers": [network.nodes[p].nickname for p in node.neighbors if p in network.nodes]
                    }, "state": snap})

                if parsed.path == "/api/chat":
                    text = str(payload.get("text", "")).strip()
                    frm = payload.get("from")
                    if not text:
                        return _json_response(self, {"ok": False, "error": "empty text"}, status=400)
                    with state_lock:
                        if not frm or (frm not in network.nick_to_id and frm not in network.nodes):
                            frm = "session-host" if "session-host" in network.nick_to_id else (next(iter(network.nick_to_id), None))
                        if not frm:
                            return _json_response(self, {"ok": False, "error": "unknown sender; join first"}, status=400)
                        if text in ("?", "/help"):
                            msg = {"kind": "help", "payload": HELP_TEXT}
                        else:
                            msg = network.broadcast_common_chat(frm, text)
                        snap = network.snapshot()
                        snap["help"] = HELP_TEXT
                    return _json_response(self, {"ok": True, "message": msg, "state": snap})

                self.send_error(404)
            except Exception as e:
                traceback.print_exc()
                return _json_response(self, {"ok": False, "error": str(e)}, status=500)

        def log_message(self, fmt, *args):
            return

    try:
        server = ThreadingHTTPServer((host, port), Handler)
    except Exception:
        fallback = "127.0.0.1"
        server = ThreadingHTTPServer((fallback, 0), Handler)
        host = fallback

    actual_host, actual_port = server.server_address[0], server.server_address[1]
    if ":" in str(actual_host):
        url = f"http://[{actual_host}]:{actual_port}/"
    else:
        url = f"http://{actual_host}:{actual_port}/"

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return BeaconHandle(server=server, thread=thread, url=url, port=actual_port)
