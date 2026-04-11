# AGENTS.md — Cyber Command Center

> **Audience:** AI coding agents and senior developers onboarding to this codebase.
> Read this file first. It describes every module, every API endpoint, every
> WebSocket event, all security constraints, and the conventions you must follow
> when adding or modifying code.

---

## 1. Project Overview

**Cyber Command Center** is a home-lab cybersecurity dashboard built for
educational use in network-security coursework. It provides:

- Live network device discovery and monitoring
- WiFi auditing: WPA/WPA2 handshake capture, PMKID capture, WPS attacks,
  password cracking (CPU + GPU)
- Deauthentication testing
- Traffic monitoring, parental controls, device management
- A React single-page application served by the Flask backend

**Ethical boundary:** All WiFi attack features operate only on the network the
operator owns or has explicit written permission to test. The codebase enforces
input validation on every external value before it is forwarded to a subprocess.

---

## 2. Repository Layout

```
T-Project/
└── CyberCommandCenter/
    ├── backend/                   # Flask + Flask-SocketIO server
    │   ├── app.py                 # Application entry point, all routes
    │   ├── config.py              # Host, port, secret key, CORS origins
    │   ├── api/
    │   │   └── wifi_audit_routes.py   # Blueprint: /api/v1/wifi-audit/*
    │   ├── core/
    │   │   ├── wifi_hacker.py     # HIGH-LEVEL WiFi attack orchestrator
    │   │   ├── wifi_audit.py      # Low-level handshake / EAPOL / cracking
    │   │   ├── deauth.py          # 802.11 deauthentication + network scan
    │   │   ├── scanner.py         # ARP/IP network device scanner
    │   │   ├── pranks.py          # Network-level client disruption
    │   │   ├── device_control.py  # Device blocking, bandwidth shaping
    │   │   ├── system_tools.py    # Speed test, ping, DNS, ARP, processes
    │   │   ├── traffic_monitor.py # Real-time bandwidth counter
    │   │   ├── parental_control.py # Time-based access control
    │   │   ├── alerts.py          # Alert bus (new device, intrusion, etc.)
    │   │   ├── scheduler.py       # Cron-style prank scheduler
    │   │   ├── validators.py      # Structural validators (IP, MAC, JSON)
    │   │   ├── error_handlers.py  # Flask error handlers, response helpers
    │   │   ├── logger.py          # Structured logger + audit trail
    │   │   ├── config_manager.py  # Runtime config CRUD + backups
    │   │   ├── device_profiles.py # Custom device categories and tags
    │   │   └── theme_manager.py   # UI theme persistence
    │   └── database/
    │       └── models.py          # SQLAlchemy ORM (SQLite)
    └── frontend/                  # Vite + React 18 + Tailwind CSS
        └── src/
            ├── pages/             # One file per page (see §6)
            ├── components/        # Shared UI components
            └── services/
                └── api.js         # Axios client + all named API wrappers
```

---

## 3. Backend Architecture

### 3.1 Entry Point — `app.py`

- Creates the Flask app, registers CORS, and wraps it with `flask-socketio`
  (`async_mode='threading'`).
- Registers `wifi_audit_bp` blueprint (prefix `/api/v1/wifi-audit`).
- Hands the `socketio` instance to `wifi_hacker` so it can emit real-time
  events during long-running captures.
- All routes use the `@handle_errors` decorator (catches unhandled exceptions,
  returns structured JSON) and `@rate_limit` on attack endpoints (5 req/min).

### 3.2 Input Validation — `core/wifi_audit.py` (module-level)

Four validation functions are **imported by every WiFi module** before any
subprocess call. Never pass raw user input to `subprocess` without calling one:

| Function | Validates | Raises |
|---|---|---|
| `validate_mac(mac, allow_broadcast=True)` | MAC address, normalises to uppercase colons | `ValueError` |
| `validate_bssid(bssid)` | BSSID (MAC, no broadcast) | `ValueError` |
| `validate_interface(iface)` | Alphanumeric interface name ≤32 chars | `ValueError` |
| `validate_channel(channel)` | Integer 1-14 | `ValueError` |

### 3.3 Security Constraints

- **No raw subprocess with user input.** All user-supplied strings pass through
  a validator before reaching `subprocess.run()` / `subprocess.Popen()`.
- **Rate limiting** on all attack endpoints: `@rate_limit(requests_per_minute=5)`.
- **Audit logging** on every attack action via `audit(event, data)`.
- **No eval, no exec, no shell=True with user data.**
- SQLite queries use SQLAlchemy ORM — no raw SQL interpolation.

---

## 4. Core Modules

### 4.1 `core/wifi_hacker.py` — WiFi Attack Orchestrator

**Singleton instance:** `wifi_hacker` (imported by `app.py`)

**Key attributes:**

| Attribute | Type | Purpose |
|---|---|---|
| `interface` | `str \| None` | Base wireless interface (e.g. `wlan0`) |
| `monitor_interface` | `str \| None` | Monitor-mode interface (e.g. `wlan0mon`) |
| `current_attack` | `AttackType \| None` | Currently running attack enum value |
| `tools_available` | `Dict[str, bool]` | Tool availability map (aircrack, hashcat…) |
| `_socketio` | SocketIO instance | Set by `set_socketio()` for real-time events |

**Public methods:**

| Method | Description |
|---|---|
| `is_available() -> bool` | True if at least one external tool is present |
| `check_requirements() -> Dict` | Alias for `get_requirements()` — full tool inventory |
| `get_wireless_interfaces() -> List[str]` | Lists interfaces via `iw dev` / `iwconfig` |
| `set_interface(iface: str)` | Store chosen base interface |
| `monitor_mode_enabled -> bool` (property) | True when monitor interface is active |
| `enable_monitor_mode() -> Dict` | Calls `airmon-ng`, parses real interface name |
| `disable_monitor_mode() -> Dict` | Calls `airmon-ng stop`, restarts NetworkManager |
| `scan_wps_networks(timeout) -> List[WPSNetwork]` | `wash` scan for WPS APs |
| `attack_wps_pixie(bssid, channel) -> AttackResult` | Reaver Pixie Dust |
| `attack_wps_bruteforce(bssid, channel, timeout) -> AttackResult` | Reaver PIN |
| `capture_handshake(bssid, channel, client_mac, timeout) -> AttackResult` | airodump-ng + periodic aireplay-ng deauth every 15 s; emits `wifi_capture_status` |
| `capture_pmkid(bssid, channel, timeout) -> AttackResult` | hcxdumptool PMKID |
| `crack_handshake(capture_file, wordlist, use_gpu) -> AttackResult` | Routes to hashcat (GPU) or aircrack-ng (CPU) |
| `_crack_with_hashcat(capture_file, wordlist) -> AttackResult` | `.cap` → `.hc22000` via `hcxpcapngtool`, then `hashcat -m 22000`; streams speed via `wifi_crack_progress` |
| `stop_attack() -> Dict` | Terminates the active subprocess |
| `set_socketio(socketio)` | Inject SocketIO instance post-init |
| `list_captures() -> List[Dict]` | Metadata for all `.cap/.pcapng/.hc22000` files |
| `cleanup_old_captures(days=7) -> Dict` | Deletes capture files older than N days |

**Monitor mode detection** (robust, multi-pattern):
`enable_monitor_mode()` parses `airmon-ng start <iface>` stdout+stderr with
four regex patterns, then falls back to `ip link show <iface>mon` to confirm
the interface actually exists.

### 4.2 `core/wifi_audit.py` — Low-Level Audit Tools

Three classes for detailed audit work:

#### `HandshakeCapture`

Scapy-based packet capture. Key design decisions:

- **`_classify_eapol(packet) -> Optional[str]`** — classifies EAPOL frames as
  M1/M2/M3/M4 using 802.11 Key Information bit analysis:
  - Bit 3 = Key Type (must be 1 = Pairwise)
  - Bit 6 = Install, Bit 7 = ACK, Bit 8 = MIC, Bit 9 = Secure
  - M1: ACK=1, MIC=0 | M2: ACK=0, MIC=1, Secure=0 | M3: ACK=1, MIC=1, Install=1 | M4: ACK=0, MIC=1, Secure=1
- A capture is **crackable** when `{M1,M2}` or `{M2,M3}` are both present.
- No circular import: deauth is done inline via Scapy or via an injected
  `_deauth_func` callable.

#### `PasswordCracker`

CPU-based cracking via `aircrack-ng`. Returns the found password or `None`.

#### `WPSAttack`

Thin wrapper around `reaver` for WPS PIN enumeration.

### 4.3 `core/deauth.py` — 802.11 Deauthentication

**`WiFiDeauth`** — sends 802.11 deauth frames via Scapy.

- `deauth(target_mac, ap_mac, count, reason)` — validates both MACs with inline
  regex before building the frame. Requires monitor mode on Linux.
- `start_deauth_attack(target_mac, ap_mac, interval)` — threaded loop.
- `stop_deauth_attack(target_mac)` / `stop_all_attacks()` — graceful teardown.

**`WiFiScanner`** — passive network discovery.

- `scan_networks_linux()` — runs `iwlist scan` (tries without sudo first,
  then falls back), converts dBm to 0-100% signal, detects WPA2 > WPA priority.
- `scan_networks_windows()` — `netsh wlan show networks mode=bssid`.

### 4.4 `core/scanner.py` — Network Device Scanner

- `NetworkScanner` — ARP scan via `scapy.srp`, OS fingerprinting, vendor lookup.
- `NetworkMonitor` — threading loop; emits `network_event` on device change.

### 4.5 `core/system_tools.py`

Stateless utilities: `SpeedTester`, `WiFiPasswordRecovery`, `ConnectionsMonitor`,
`ProcessNetworkMonitor`, `PingMonitor`, `ARPTableViewer`, `DNSTools`,
`SystemNetworkInfo`.

### 4.6 `database/models.py` — ORM

| Model | Table | Notes |
|---|---|---|
| `Device` | `devices` | MAC, IP, vendor, trust/block flags |
| `ConnectionLog` | `connection_logs` | Connection/disconnection events |
| `PortScan` | `port_scans` | Per-port results tied to a device |
| `Alert` | `alerts` | Security alerts with JSON payload |
| `WiFiNetwork` | `wifi_networks` | BSSID, SSID, handshake path, cracked password |
| `PrankLog` | `prank_logs` | Prank activity history |
| `NetworkStats` | `network_stats` | Periodic bandwidth snapshots |
| `Settings` | `settings` | Key-value runtime settings |

**`WiFiNetwork.to_dict()`** serializes all columns including
`handshake_path` and exposes `password` only when `is_cracked=True`.

---

## 5. API Reference

### Authentication
No authentication is implemented — this is a single-user home-lab tool.
Do **not** expose the server port to the public internet.

### Response envelope
- Success: `{ ...data... }` or `{ "success": true, ... }`
- Error: `{ "error": { "code": "ERROR_CODE", "message": "..." } }`

### Blueprint: `/api/v1/wifi-audit/*`  (`api/wifi_audit_routes.py`)

| Method | Path | Description |
|---|---|---|
| GET | `/requirements` | Check Scapy, aircrack-ng, tool availability |
| GET | `/scan` | Scan visible WiFi networks (saves to DB) |
| POST | `/capture/start` | Start Scapy handshake capture (`bssid`, `channel`, `timeout`) |
| POST | `/capture/stop` | Stop active capture |
| GET | `/capture/status` | Current capture state — EAPOL M1/M2/M3/M4, `handshake_complete` |
| POST | `/capture/deauth` | Send deauth to force handshake (`bssid`, `client_mac`, `count`) |
| GET | `/crack/wordlists` | List available wordlists on disk |
| POST | `/crack/wordlists/download` | Download a wordlist by name |
| POST | `/crack/start` | CPU crack via aircrack-ng (`capture_file`, `wordlist`, `method`, `bssid`) |
| POST | `/deauth/start` | Start continuous deauth loop (`target_mac`, `ap_mac`, `interval`) |
| POST | `/deauth/stop` | Stop deauth loop (`target_mac` or null = stop all) |
| GET | `/deauth/status` | List active deauth attacks |

### Routes in `app.py`

#### Health
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Full system health (CPU, memory, disk) |
| GET | `/api/v1/health/simple` | `{"status":"ok","timestamp":"..."}` |

#### Dashboard
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/dashboard/stats` | Device counts, alerts, network info |
| GET | `/api/v1/dashboard/network-info` | Gateway, local IP, subnet |

#### Devices
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/devices` | All known devices |
| GET | `/api/v1/devices/<id>` | Single device |
| PUT | `/api/v1/devices/<id>` | Update device name/category/trust/block |
| POST | `/api/v1/devices/scan` | Trigger ARP/IP network scan |
| POST | `/api/v1/devices/<id>/ports` | Port scan a device |

#### Alerts
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/alerts` | List alerts (`?limit=&unread=`) |
| POST | `/api/v1/alerts/<id>/read` | Mark alert as read |
| POST | `/api/v1/alerts/read-all` | Mark all alerts as read |

#### WiFi (passive, no monitor mode)
| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/wifi/networks` | Known WiFi networks from DB |
| GET | `/api/v1/wifi/connected` | Currently connected SSID/BSSID |

#### WiFi Hacker (active, requires monitor mode)
| Method | Path | Rate | Description |
|---|---|---|---|
| GET | `/api/v1/wifi-hacker/status` | — | Tool availability, interface, attack state |
| GET | `/api/v1/wifi-hacker/interfaces` | — | Wireless interface list |
| PUT | `/api/v1/wifi-hacker/interface` | — | Set active interface (`{interface}`) |
| POST | `/api/v1/wifi-hacker/monitor-mode` | — | Enable/disable monitor mode (`{enable}`) |
| GET | `/api/v1/wifi-hacker/scan-wps` | — | Scan WPS-enabled APs (`?timeout=30`) |
| POST | `/api/v1/wifi-hacker/attack/wps-pixie` | 5/min | Pixie Dust (`bssid`, `channel`) |
| POST | `/api/v1/wifi-hacker/attack/wps-bruteforce` | 2/min | WPS PIN brute (`bssid`, `channel`, `timeout`) |
| POST | `/api/v1/wifi-hacker/capture/handshake` | 5/min | Capture WPA handshake (`bssid`, `channel`, `client_mac`, `timeout`) |
| POST | `/api/v1/wifi-hacker/capture/pmkid` | 5/min | Capture PMKID (`bssid`, `channel`, `timeout`) |
| POST | `/api/v1/wifi-hacker/crack` | 5/min | Crack capture (`capture_file`, `wordlist`, `use_gpu`) |
| POST | `/api/v1/wifi-hacker/stop` | — | Stop current attack |
| GET | `/api/v1/wifi-hacker/wordlists` | — | List wordlists |
| POST | `/api/v1/wifi-hacker/download-wordlist` | — | Download wordlist by name |
| GET | `/api/v1/wifi-hacker/captures` | — | Metadata for all capture files on disk |
| POST | `/api/v1/wifi-hacker/captures/cleanup` | 5/min | Delete captures older than N days (`{days}`) |

---

## 6. WebSocket Events (Flask-SocketIO)

All events use the default `/` namespace.

### Client → Server

| Event | Payload | Description |
|---|---|---|
| `start_monitoring` | — | Start `NetworkMonitor` loop (emits `network_event`) |
| `stop_monitoring` | — | Stop `NetworkMonitor` loop |

### Server → Client

| Event | Payload | Emitted by |
|---|---|---|
| `connected` | `{status}` | On websocket handshake |
| `network_event` | `{type, device}` | `NetworkMonitor` on device change |
| `wifi_capture_status` | `{status, bssid?, elapsed?, deauth_count?, file?}` | `wifi_hacker.capture_handshake()` |
| `wifi_crack_progress` | `{speed_khs, progress_pct?, status}` | `wifi_hacker._crack_with_hashcat()` |

**`wifi_capture_status.status` values:**
`started` → `checking` → `deauth_sent` → `captured` (or `failed`/`timeout`)

---

## 7. Frontend Architecture

**Stack:** Vite + React 18 + Tailwind CSS + Socket.io-client + Axios

### Pages

| File | Route | Description |
|---|---|---|
| `Dashboard.jsx` | `/` | Device summary, alerts, network stats |
| `Devices.jsx` | `/devices` | Device table with scan, port-scan, edit |
| `WiFiAudit.jsx` | `/wifi-audit` | Handshake capture UI with M1/M2/M3/M4 pills |
| `WiFiHackerPage.jsx` | `/wifi-hacker` | WPS/handshake/crack with real-time log stream |
| `Pranks.jsx` | `/pranks` | Prank scheduler and execution |
| `DeviceControl.jsx` | `/device-control` | Per-device block / bandwidth shaping |
| `Traffic.jsx` | `/traffic` | Live traffic meter |
| `TrafficMonitor.jsx` | `/traffic-monitor` | Historical traffic chart |
| `Tools.jsx` | `/tools` | Ping, speed test, DNS, ARP table |
| `Logs.jsx` | `/logs` | Request and audit log viewer |
| `Settings.jsx` | `/settings` | Key-value settings editor |

### `services/api.js`

Single Axios instance (`baseURL=/api/v1`, `timeout=30 000 ms`).

**Named exports (all actively used):**

```
getDashboardStats  getDevices  updateDevice  scanNetwork  scanPorts
getAlerts          getWiFiNetworks  getConnectedWiFi
getWiFiAuditRequirements  scanWiFiNetworks
startHandshakeCapture  stopHandshakeCapture  getCaptureStatus
sendDeauthForCapture   getWordlists  downloadWordlist  startCrack
startDeauth  stopDeauth  getDeauthStatus
```

Pages that need other endpoints call `api.get(...)` / `api.post(...)` via the
default export directly rather than through named wrappers.

---

## 8. Development Setup

```bash
# Backend
cd CyberCommandCenter/backend
pip install -r requirements.txt
python app.py                # http://localhost:5000

# Frontend (separate terminal)
cd CyberCommandCenter/frontend
npm install
npm run dev                  # http://localhost:5173 (proxied to :5000)
```

**Required system tools for WiFi features (Linux only):**

```
sudo apt install aircrack-ng reaver hashcat hcxtools
# Optional (faster PMKID capture):
sudo apt install hcxdumptool
# Python driver:
pip install scapy
```

---

## 9. Adding a New Feature

1. **Backend module** → create `core/my_feature.py`; add input validation at
   the top using the pattern in §3.2.
2. **API route** → add to `app.py` or a new Blueprint registered in `app.py`.
   Decorate attack routes with `@handle_errors @rate_limit(requests_per_minute=5)`.
3. **Audit** → call `audit("event_name", {...})` at the start of every
   potentially sensitive operation.
4. **Frontend page** → add to `src/pages/`, register in the router.
5. **API wrapper** → if the new endpoint is called from a named import, add the
   wrapper to `src/services/api.js`; otherwise call `api.get/post` directly.
6. **Database model** → add a column to the appropriate model in `models.py`;
   update `to_dict()` to include it.

### Security checklist for new attack endpoints
- [ ] Validate all user-supplied strings before `subprocess` (use validators from `wifi_audit.py`)
- [ ] Use `@rate_limit` decorator
- [ ] Call `audit()` with event name and sanitized payload
- [ ] Return structured error with `error_response()` on validation failure
- [ ] No `shell=True` with user data

---

## 10. Key Invariants (never break these)

| Rule | Reason |
|---|---|
| `wifi_hacker.set_socketio(socketio)` called in `app.py` after both are initialized | Real-time events won't emit otherwise |
| `wifi_audit_bp` registered before the first request | Blueprint routes return 404 if skipped |
| `validate_bssid()` / `validate_mac()` called before every `subprocess` that takes a MAC | Prevents command injection |
| `WiFiNetwork.to_dict()` must include `handshake_path` | Frontend uses it to locate the capture file for cracking |
| Monitor-mode interface resolved from `airmon-ng` output, not assumed to be `<iface>mon` | Some drivers use different naming |
| EAPOL classified by Key Information bits, not by count | 4 arbitrary EAPOL frames do not guarantee a crackable handshake |
