"""
Cyber Command Center - Configuration
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_PATH = BASE_DIR / "database" / "cyber_command.db"

# Network Settings
DEFAULT_INTERFACE = None  # Auto-detect
SCAN_INTERVAL = 30  # seconds
SCAN_TIMEOUT = 3  # seconds per host

# Web Server
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "cyber-command-center-2024-secret-key")

# Notifications
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# WiFi Audit Settings
HANDSHAKE_DIR = BASE_DIR / "captures" / "handshakes"
WORDLIST_DIR = BASE_DIR / "wordlists"

# Logging
LOG_DIR = BASE_DIR / "logs"
LOG_LEVEL = "INFO"

# API Settings
API_PREFIX = "/api/v1"
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5000"]

# Device Categories
DEVICE_CATEGORIES = {
    "computer": ["windows", "mac", "linux", "pc"],
    "mobile": ["iphone", "android", "ipad", "tablet", "phone"],
    "iot": ["smart", "camera", "thermostat", "speaker", "alexa", "google-home"],
    "gaming": ["playstation", "xbox", "nintendo", "steam"],
    "network": ["router", "switch", "ap", "access-point"],
    "tv": ["tv", "chromecast", "roku", "firestick", "apple-tv"],
}

# MAC Vendor prefixes (top manufacturers)
MAC_VENDORS = {
    "00:00:0C": "Cisco",
    "00:1A:2B": "Ayecom",
    "00:1B:63": "Apple",
    "00:1E:C2": "Apple",
    "00:23:12": "Apple",
    "00:25:00": "Apple",
    "00:26:B0": "Apple",
    "00:26:BB": "Apple",
    "3C:5A:B4": "Google",
    "F4:F5:D8": "Google",
    "54:60:09": "Google",
    "00:50:56": "VMware",
    "00:0C:29": "VMware",
    "08:00:27": "VirtualBox",
    "B8:27:EB": "Raspberry Pi",
    "DC:A6:32": "Raspberry Pi",
    "00:1A:79": "Dell",
    "00:14:22": "Dell",
    "00:21:9B": "Dell",
    "3C:D9:2B": "HP",
    "00:1E:0B": "HP",
    "00:17:A4": "HP",
    "00:0D:3A": "Microsoft",
    "28:18:78": "Microsoft",
    "00:15:5D": "Microsoft Hyper-V",
    "00:1D:D8": "Microsoft Xbox",
    "7C:ED:8D": "Microsoft Xbox",
    "00:04:4B": "Nvidia",
    "00:1F:3B": "Intel",
    "00:1E:67": "Intel",
    "00:19:D1": "Intel",
    "AC:DE:48": "Intel",
    "00:24:D7": "Intel",
    "34:02:86": "Intel",
    "00:0C:6E": "ASUSTek",
    "00:1A:92": "ASUSTek",
    "00:15:F2": "ASUSTek",
    "00:24:8C": "ASUSTek",
    "08:60:6E": "ASUSTek",
    "00:16:6F": "Samsung",
    "00:1D:F6": "Samsung",
    "00:26:37": "Samsung",
    "5C:0A:5B": "Samsung",
    "00:1E:75": "LG",
    "00:1C:62": "LG",
    "00:1F:6B": "LG",
    "00:1F:E2": "LG",
    "B8:8D:12": "Apple",
    "DC:2B:2A": "Apple",
    "F0:B4:79": "Apple",
    "00:CD:FE": "Apple",
    "14:10:9F": "Apple",
    "C8:69:CD": "Apple",
    "98:D6:BB": "Apple",
    "A4:5E:60": "Apple",
    "50:32:75": "Apple",
}
