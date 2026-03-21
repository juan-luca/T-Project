"""
Device Control Module - Cyber Command Center
Manage and control devices on your local network
FOR USE ON YOUR OWN NETWORK ONLY!
"""
import subprocess
import socket
import re
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime
import json


class DeviceControl:
    """Control devices on local network"""
    
    # Known manufacturer MAC prefixes
    MANUFACTURERS = {
        '00:1A:2B': 'Apple Inc.',
        '00:1E:C2': 'Apple Inc.',
        '00:21:E9': 'Apple Inc.',
        '00:23:12': 'Apple Inc.',
        '00:23:DF': 'Apple Inc.',
        '00:25:BC': 'Apple Inc.',
        '00:26:08': 'Apple Inc.',
        '00:26:4A': 'Apple Inc.',
        '00:26:B0': 'Apple Inc.',
        '00:26:BB': 'Apple Inc.',
        '00:3E:E1': 'Apple Inc.',
        '04:0C:CE': 'Apple Inc.',
        '04:15:52': 'Apple Inc.',
        '04:1E:64': 'Apple Inc.',
        '04:26:65': 'Apple Inc.',
        '04:48:9A': 'Apple Inc.',
        '04:52:F3': 'Apple Inc.',
        '04:54:53': 'Apple Inc.',
        '04:56:C5': 'Apple Inc.',
        '04:DB:56': 'Apple Inc.',
        '04:E5:36': 'Apple Inc.',
        '08:00:07': 'Apple Inc.',
        '10:40:F3': 'Apple Inc.',
        '10:93:E9': 'Apple Inc.',
        '10:9A:DD': 'Apple Inc.',
        '10:DD:B1': 'Apple Inc.',
        '14:10:9F': 'Apple Inc.',
        '14:5A:05': 'Apple Inc.',
        '14:8F:C6': 'Apple Inc.',
        '14:99:E2': 'Apple Inc.',
        '18:20:32': 'Apple Inc.',
        '18:34:51': 'Apple Inc.',
        '18:65:90': 'Apple Inc.',
        '18:81:0E': 'Apple Inc.',
        '18:E7:F4': 'Apple Inc.',
        '1C:1A:C0': 'Apple Inc.',
        '1C:36:BB': 'Apple Inc.',
        '1C:5C:F2': 'Apple Inc.',
        '1C:91:48': 'Apple Inc.',
        '20:3C:AE': 'Apple Inc.',
        '20:7D:74': 'Apple Inc.',
        '20:9B:CD': 'Apple Inc.',
        '24:1E:EB': 'Apple Inc.',
        '24:A2:E1': 'Apple Inc.',
        '28:6A:BA': 'Apple Inc.',
        '28:A0:2B': 'Apple Inc.',
        '28:CF:DA': 'Apple Inc.',
        '28:E1:4C': 'Apple Inc.',
        '2C:1F:23': 'Apple Inc.',
        '2C:33:61': 'Apple Inc.',
        '2C:54:CF': 'Apple Inc.',
        '2C:BE:08': 'Apple Inc.',
        '30:35:AD': 'Apple Inc.',
        '34:08:BC': 'Apple Inc.',
        '34:12:98': 'Apple Inc.',
        '34:AB:37': 'Apple Inc.',
        '34:C0:59': 'Apple Inc.',
        '38:0F:4A': 'Apple Inc.',
        '38:48:4C': 'Apple Inc.',
        '38:66:F0': 'Apple Inc.',
        '38:71:DE': 'Apple Inc.',
        '38:C9:86': 'Apple Inc.',
        '3C:07:54': 'Apple Inc.',
        '3C:15:C2': 'Apple Inc.',
        '3C:D0:F8': 'Apple Inc.',
        '3C:E0:72': 'Apple Inc.',
        '40:30:04': 'Apple Inc.',
        '40:33:1A': 'Apple Inc.',
        '40:6C:8F': 'Apple Inc.',
        '40:A6:D9': 'Apple Inc.',
        '40:D3:2D': 'Apple Inc.',
        '44:2A:60': 'Apple Inc.',
        '44:D8:84': 'Apple Inc.',
        '48:43:7C': 'Apple Inc.',
        '48:5D:60': 'Apple Inc.',
        '48:60:BC': 'Apple Inc.',
        '48:74:6E': 'Apple Inc.',
        '48:A9:1C': 'Apple Inc.',
        '4C:32:75': 'Apple Inc.',
        '4C:57:CA': 'Apple Inc.',
        '4C:74:BF': 'Apple Inc.',
        '4C:8D:79': 'Apple Inc.',
        '4C:B1:99': 'Apple Inc.',
        '50:1A:C5': 'Apple Inc.',
        '50:7A:55': 'Apple Inc.',
        '54:26:96': 'Apple Inc.',
        '54:4E:90': 'Apple Inc.',
        '54:72:4F': 'Apple Inc.',
        '54:E4:3A': 'Apple Inc.',
        '54:EA:A8': 'Apple Inc.',
        '54:EE:75': 'Apple Inc.',
        '58:1F:AA': 'Apple Inc.',
        '58:55:CA': 'Apple Inc.',
        '5C:59:48': 'Apple Inc.',
        '5C:8D:4E': 'Apple Inc.',
        '5C:95:AE': 'Apple Inc.',
        '5C:96:9D': 'Apple Inc.',
        '5C:F7:E6': 'Apple Inc.',
        '60:03:08': 'Apple Inc.',
        '60:33:4B': 'Apple Inc.',
        '60:69:44': 'Apple Inc.',
        '60:92:17': 'Apple Inc.',
        '60:C5:47': 'Apple Inc.',
        '60:D9:C7': 'Apple Inc.',
        '60:FA:CD': 'Apple Inc.',
        '60:FB:42': 'Apple Inc.',
        '64:20:0C': 'Apple Inc.',
        '64:70:33': 'Apple Inc.',
        '64:76:BA': 'Apple Inc.',
        '64:A3:CB': 'Apple Inc.',
        '64:B9:E8': 'Apple Inc.',
        '64:E6:82': 'Apple Inc.',
        '68:09:27': 'Apple Inc.',
        '68:5B:35': 'Apple Inc.',
        '68:64:4B': 'Apple Inc.',
        '68:96:7B': 'Apple Inc.',
        '68:A8:6D': 'Apple Inc.',
        '68:AB:1E': 'Apple Inc.',
        '68:AE:20': 'Apple Inc.',
        '68:D9:3C': 'Apple Inc.',
        '68:DB:CA': 'Apple Inc.',
        '68:FE:F7': 'Apple Inc.',
        '6C:19:C0': 'Apple Inc.',
        '6C:3E:6D': 'Apple Inc.',
        '6C:40:08': 'Apple Inc.',
        '6C:70:9F': 'Apple Inc.',
        '6C:72:E7': 'Apple Inc.',
        '6C:94:F8': 'Apple Inc.',
        '6C:C2:6B': 'Apple Inc.',
        '70:11:24': 'Apple Inc.',
        '70:14:A6': 'Apple Inc.',
        '70:3E:AC': 'Apple Inc.',
        '70:56:81': 'Apple Inc.',
        '70:73:CB': 'Apple Inc.',
        '70:81:EB': 'Apple Inc.',
        '70:CD:60': 'Apple Inc.',
        '70:DE:E2': 'Apple Inc.',
        '70:EC:E4': 'Apple Inc.',
        '70:F0:87': 'Apple Inc.',
        '74:8D:08': 'Apple Inc.',
        '74:E1:B6': 'Apple Inc.',
        '78:31:C1': 'Apple Inc.',
        '78:3A:84': 'Apple Inc.',
        '78:4F:43': 'Apple Inc.',
        '78:67:D7': 'Apple Inc.',
        '78:6C:1C': 'Apple Inc.',
        '78:7E:61': 'Apple Inc.',
        '78:88:6D': 'Apple Inc.',
        '78:9F:70': 'Apple Inc.',
        '78:A3:E4': 'Apple Inc.',
        '78:CA:39': 'Apple Inc.',
        '78:D7:5F': 'Apple Inc.',
        '78:FD:94': 'Apple Inc.',
        '7C:04:D0': 'Apple Inc.',
        '7C:11:BE': 'Apple Inc.',
        '7C:50:49': 'Apple Inc.',
        '7C:6D:62': 'Apple Inc.',
        '7C:C3:A1': 'Apple Inc.',
        '7C:C5:37': 'Apple Inc.',
        '7C:D1:C3': 'Apple Inc.',
        '7C:F0:5F': 'Apple Inc.',
        '7C:FA:DF': 'Apple Inc.',
        '80:00:6E': 'Apple Inc.',
        '80:49:71': 'Apple Inc.',
        '80:82:23': 'Apple Inc.',
        '80:92:9F': 'Apple Inc.',
        '80:BE:05': 'Apple Inc.',
        '80:E6:50': 'Apple Inc.',
        '80:EA:96': 'Apple Inc.',
        '80:ED:2C': 'Apple Inc.',
        '84:29:99': 'Apple Inc.',
        '84:38:35': 'Apple Inc.',
        '84:78:8B': 'Apple Inc.',
        '84:85:06': 'Apple Inc.',
        '84:8E:0C': 'Apple Inc.',
        '84:B1:53': 'Apple Inc.',
        '84:FC:FE': 'Apple Inc.',
        '88:19:08': 'Apple Inc.',
        '88:1F:A1': 'Apple Inc.',
        '88:53:95': 'Apple Inc.',
        '88:66:A5': 'Apple Inc.',
        '88:C6:63': 'Apple Inc.',
        '88:CB:87': 'Apple Inc.',
        '88:E8:7F': 'Apple Inc.',
        '8C:00:6D': 'Apple Inc.',
        '8C:29:37': 'Apple Inc.',
        '8C:2D:AA': 'Apple Inc.',
        '8C:58:77': 'Apple Inc.',
        '8C:7B:9D': 'Apple Inc.',
        '8C:85:90': 'Apple Inc.',
        '8C:8E:F2': 'Apple Inc.',
        '8C:FA:BA': 'Apple Inc.',
        '90:27:E4': 'Apple Inc.',
        '90:3C:92': 'Apple Inc.',
        '90:72:40': 'Apple Inc.',
        '90:84:0D': 'Apple Inc.',
        '90:8D:6C': 'Apple Inc.',
        '90:B0:ED': 'Apple Inc.',
        '90:B2:1F': 'Apple Inc.',
        '90:B9:31': 'Apple Inc.',
        '90:FD:61': 'Apple Inc.',
        '94:E9:6A': 'Apple Inc.',
        '94:F6:A3': 'Apple Inc.',
        '98:01:A7': 'Apple Inc.',
        '98:03:D8': 'Apple Inc.',
        '98:10:E8': 'Apple Inc.',
        '98:5A:EB': 'Apple Inc.',
        '98:B8:E3': 'Apple Inc.',
        '98:D6:BB': 'Apple Inc.',
        '98:F0:AB': 'Apple Inc.',
        '98:FE:94': 'Apple Inc.',
        '9C:04:EB': 'Apple Inc.',
        '9C:20:7B': 'Apple Inc.',
        '9C:29:3F': 'Apple Inc.',
        '9C:35:EB': 'Apple Inc.',
        '9C:4F:DA': 'Apple Inc.',
        '9C:84:BF': 'Apple Inc.',
        '9C:8B:A0': 'Apple Inc.',
        '9C:E6:5E': 'Apple Inc.',
        '9C:F3:87': 'Apple Inc.',
        'A0:18:28': 'Apple Inc.',
        'A0:99:9B': 'Apple Inc.',
        'A0:D7:95': 'Apple Inc.',
        'A0:ED:CD': 'Apple Inc.',
        'A4:5E:60': 'Apple Inc.',
        'A4:67:06': 'Apple Inc.',
        'A4:B8:05': 'Apple Inc.',
        'A4:C3:61': 'Apple Inc.',
        'A4:D1:8C': 'Apple Inc.',
        'A4:D1:D2': 'Apple Inc.',
        'A4:D9:31': 'Apple Inc.',
        'A8:20:66': 'Apple Inc.',
        'A8:51:5B': 'Apple Inc.',
        'A8:5B:78': 'Apple Inc.',
        'A8:5C:2C': 'Apple Inc.',
        'A8:66:7F': 'Apple Inc.',
        'A8:86:DD': 'Apple Inc.',
        'A8:8E:24': 'Apple Inc.',
        'A8:96:8A': 'Apple Inc.',
        'A8:BB:CF': 'Apple Inc.',
        'A8:FA:D8': 'Apple Inc.',
        'AC:29:3A': 'Apple Inc.',
        'AC:3C:0B': 'Apple Inc.',
        'AC:7F:3E': 'Apple Inc.',
        'AC:87:A3': 'Apple Inc.',
        'AC:BC:32': 'Apple Inc.',
        'AC:CF:5C': 'Apple Inc.',
        'AC:E4:B5': 'Apple Inc.',
        'AC:FD:EC': 'Apple Inc.',
        'B0:34:95': 'Apple Inc.',
        'B0:65:BD': 'Apple Inc.',
        'B0:70:2D': 'Apple Inc.',
        'B0:9F:BA': 'Apple Inc.',
        'B4:18:D1': 'Apple Inc.',
        'B4:8B:19': 'Apple Inc.',
        'B4:9C:DF': 'Apple Inc.',
        'B4:F0:AB': 'Apple Inc.',
        'B8:09:8A': 'Apple Inc.',
        'B8:17:C2': 'Apple Inc.',
        'B8:41:A4': 'Apple Inc.',
        'B8:44:D9': 'Apple Inc.',
        'B8:53:AC': 'Apple Inc.',
        'B8:63:4D': 'Apple Inc.',
        'B8:78:2E': 'Apple Inc.',
        'B8:8D:12': 'Apple Inc.',
        'B8:C1:11': 'Apple Inc.',
        'B8:C7:5D': 'Apple Inc.',
        'B8:E8:56': 'Apple Inc.',
        'B8:F6:B1': 'Apple Inc.',
        'B8:FF:61': 'Apple Inc.',
        'BC:3B:AF': 'Apple Inc.',
        'BC:4C:C4': 'Apple Inc.',
        'BC:52:B7': 'Apple Inc.',
        'BC:54:36': 'Apple Inc.',
        'BC:67:78': 'Apple Inc.',
        'BC:6C:21': 'Apple Inc.',
        'BC:92:6B': 'Apple Inc.',
        'BC:A9:20': 'Apple Inc.',
        'BC:E1:43': 'Apple Inc.',
        'BC:EC:5D': 'Apple Inc.',
        'BC:FE:D9': 'Apple Inc.',
        'C0:1A:DA': 'Apple Inc.',
        'C0:63:94': 'Apple Inc.',
        'C0:84:7A': 'Apple Inc.',
        'C0:9F:42': 'Apple Inc.',
        'C0:A5:3E': 'Apple Inc.',
        'C0:CE:CD': 'Apple Inc.',
        'C0:D0:12': 'Apple Inc.',
        'C0:F2:FB': 'Apple Inc.',
        'C4:2C:03': 'Apple Inc.',
        'C4:B3:01': 'Apple Inc.',
        'C8:1E:E7': 'Apple Inc.',
        'C8:2A:14': 'Apple Inc.',
        'C8:33:4B': 'Apple Inc.',
        'C8:69:CD': 'Apple Inc.',
        'C8:6F:1D': 'Apple Inc.',
        'C8:85:50': 'Apple Inc.',
        'C8:B5:B7': 'Apple Inc.',
        'C8:BC:C8': 'Apple Inc.',
        'C8:D0:83': 'Apple Inc.',
        'C8:E0:EB': 'Apple Inc.',
        'C8:F9:F9': 'Apple Inc.',
        'CC:08:8D': 'Apple Inc.',
        'CC:08:E0': 'Apple Inc.',
        'CC:20:E8': 'Apple Inc.',
        'CC:25:EF': 'Apple Inc.',
        'CC:29:F5': 'Apple Inc.',
        'CC:78:5F': 'Apple Inc.',
        'CC:C7:60': 'Apple Inc.',
        'D0:03:4B': 'Apple Inc.',
        'D0:23:DB': 'Apple Inc.',
        'D0:25:98': 'Apple Inc.',
        'D0:4F:7E': 'Apple Inc.',
        'D0:81:7A': 'Apple Inc.',
        'D0:A6:37': 'Apple Inc.',
        'D0:C5:F3': 'Apple Inc.',
        'D0:D2:B0': 'Apple Inc.',
        'D0:E1:40': 'Apple Inc.',
        'D4:61:9D': 'Apple Inc.',
        'D4:9A:20': 'Apple Inc.',
        'D4:DC:CD': 'Apple Inc.',
        'D4:F4:6F': 'Apple Inc.',
        'D8:00:4D': 'Apple Inc.',
        'D8:1D:72': 'Apple Inc.',
        'D8:30:62': 'Apple Inc.',
        'D8:8F:76': 'Apple Inc.',
        'D8:96:95': 'Apple Inc.',
        'D8:9E:3F': 'Apple Inc.',
        'D8:A2:5E': 'Apple Inc.',
        'D8:BB:2C': 'Apple Inc.',
        'D8:CF:9C': 'Apple Inc.',
        'D8:D1:CB': 'Apple Inc.',
        'DC:08:0F': 'Apple Inc.',
        'DC:0C:5C': 'Apple Inc.',
        'DC:2B:2A': 'Apple Inc.',
        'DC:2B:61': 'Apple Inc.',
        'DC:37:14': 'Apple Inc.',
        'DC:41:5F': 'Apple Inc.',
        'DC:56:E7': 'Apple Inc.',
        'DC:86:D8': 'Apple Inc.',
        'DC:9B:9C': 'Apple Inc.',
        'DC:A4:CA': 'Apple Inc.',
        'DC:A9:04': 'Apple Inc.',
        'E0:5F:45': 'Apple Inc.',
        'E0:66:78': 'Apple Inc.',
        'E0:AC:CB': 'Apple Inc.',
        'E0:B5:2D': 'Apple Inc.',
        'E0:B9:BA': 'Apple Inc.',
        'E0:C7:67': 'Apple Inc.',
        'E0:C9:7A': 'Apple Inc.',
        'E0:F5:C6': 'Apple Inc.',
        'E0:F8:47': 'Apple Inc.',
        'E4:25:E7': 'Apple Inc.',
        'E4:2B:34': 'Apple Inc.',
        'E4:8B:7F': 'Apple Inc.',
        'E4:98:D6': 'Apple Inc.',
        'E4:9A:79': 'Apple Inc.',
        'E4:9A:DC': 'Apple Inc.',
        'E4:C6:3D': 'Apple Inc.',
        'E4:CE:8F': 'Apple Inc.',
        'E8:04:0B': 'Apple Inc.',
        'E8:06:88': 'Apple Inc.',
        'E8:80:2E': 'Apple Inc.',
        'E8:8D:28': 'Apple Inc.',
        'E8:B2:AC': 'Apple Inc.',
        'EC:35:86': 'Apple Inc.',
        'EC:85:2F': 'Apple Inc.',
        'F0:24:75': 'Apple Inc.',
        'F0:4F:7C': 'Apple Inc.',
        'F0:5B:7B': 'Apple Inc.',
        'F0:79:60': 'Apple Inc.',
        'F0:98:9D': 'Apple Inc.',
        'F0:99:BF': 'Apple Inc.',
        'F0:B0:E7': 'Apple Inc.',
        'F0:B4:79': 'Apple Inc.',
        'F0:C1:F1': 'Apple Inc.',
        'F0:CB:A1': 'Apple Inc.',
        'F0:D1:A9': 'Apple Inc.',
        'F0:DB:E2': 'Apple Inc.',
        'F0:DC:E2': 'Apple Inc.',
        'F0:F6:1C': 'Apple Inc.',
        'F4:0F:24': 'Apple Inc.',
        'F4:1B:A1': 'Apple Inc.',
        'F4:31:C3': 'Apple Inc.',
        'F4:37:B7': 'Apple Inc.',
        'F4:5C:89': 'Apple Inc.',
        'F4:F1:5A': 'Apple Inc.',
        'F4:F9:51': 'Apple Inc.',
        'F8:1E:DF': 'Apple Inc.',
        'F8:27:93': 'Apple Inc.',
        'F8:62:14': 'Apple Inc.',
        'F8:95:C7': 'Apple Inc.',
        'FC:25:3F': 'Apple Inc.',
        'FC:E9:98': 'Apple Inc.',
        # Samsung
        '00:00:F0': 'Samsung',
        '00:02:78': 'Samsung',
        '00:07:AB': 'Samsung',
        '00:09:18': 'Samsung',
        '00:12:47': 'Samsung',
        '00:12:FB': 'Samsung',
        '00:13:77': 'Samsung',
        '00:15:99': 'Samsung',
        '00:15:B9': 'Samsung',
        '00:16:32': 'Samsung',
        '00:16:6B': 'Samsung',
        '00:16:6C': 'Samsung',
        '00:16:DB': 'Samsung',
        '00:17:C9': 'Samsung',
        '00:17:D5': 'Samsung',
        '00:18:AF': 'Samsung',
        '00:1A:8A': 'Samsung',
        '00:1B:98': 'Samsung',
        '00:1C:43': 'Samsung',
        '00:1D:25': 'Samsung',
        '00:1D:F6': 'Samsung',
        '00:1E:7D': 'Samsung',
        '00:1F:CC': 'Samsung',
        '00:21:4C': 'Samsung',
        '00:21:D1': 'Samsung',
        '00:21:D2': 'Samsung',
        '00:23:39': 'Samsung',
        '00:23:99': 'Samsung',
        '00:23:D6': 'Samsung',
        '00:23:D7': 'Samsung',
        '00:24:54': 'Samsung',
        '00:24:90': 'Samsung',
        '00:24:91': 'Samsung',
        '00:25:66': 'Samsung',
        '00:25:67': 'Samsung',
        '00:26:37': 'Samsung',
        '00:26:5D': 'Samsung',
        '00:26:5F': 'Samsung',
        # Xiaomi
        '00:9E:C8': 'Xiaomi',
        '04:CF:8C': 'Xiaomi',
        '0C:1D:AF': 'Xiaomi',
        '10:2A:B3': 'Xiaomi',
        '14:F6:5A': 'Xiaomi',
        '18:59:36': 'Xiaomi',
        '20:34:FB': 'Xiaomi',
        '28:6C:07': 'Xiaomi',
        '28:E3:1F': 'Xiaomi',
        '2C:AA:8E': 'Xiaomi',
        '34:80:B3': 'Xiaomi',
        '34:CE:00': 'Xiaomi',
        '38:A4:ED': 'Xiaomi',
        '3C:BD:D8': 'Xiaomi',
        '44:23:7C': 'Xiaomi',
        '4C:49:E3': 'Xiaomi',
        '50:64:2B': 'Xiaomi',
        '50:8F:4C': 'Xiaomi',
        '58:44:98': 'Xiaomi',
        '5C:0A:5B': 'Xiaomi',
        '64:09:80': 'Xiaomi',
        '64:B4:73': 'Xiaomi',
        '64:CC:2E': 'Xiaomi',
        '68:DF:DD': 'Xiaomi',
        '74:23:44': 'Xiaomi',
        '74:51:BA': 'Xiaomi',
        '78:02:F8': 'Xiaomi',
        '78:11:DC': 'Xiaomi',
        '7C:1D:D9': 'Xiaomi',
        '84:F3:EB': 'Xiaomi',
        '8C:BE:BE': 'Xiaomi',
        '94:E9:79': 'Xiaomi',
        '98:FA:E3': 'Xiaomi',
        '9C:99:A0': 'Xiaomi',
        'A0:86:C6': 'Xiaomi',
        'AC:C1:EE': 'Xiaomi',
        'AC:F7:F3': 'Xiaomi',
        'B0:E2:35': 'Xiaomi',
        'C4:0B:CB': 'Xiaomi',
        'C4:6A:B7': 'Xiaomi',
        'CC:B8:A8': 'Xiaomi',
        'D4:97:0B': 'Xiaomi',
        'E8:AB:F3': 'Xiaomi',
        'EC:D0:9F': 'Xiaomi',
        'F0:B4:29': 'Xiaomi',
        'FC:64:BA': 'Xiaomi',
        # Huawei
        '00:18:82': 'Huawei',
        '00:1E:10': 'Huawei',
        '00:25:9E': 'Huawei',
        '00:25:68': 'Huawei',
        '00:46:4B': 'Huawei',
        '00:66:4B': 'Huawei',
        '00:9A:CD': 'Huawei',
        '00:E0:FC': 'Huawei',
        '04:02:1F': 'Huawei',
        '04:25:C5': 'Huawei',
        '04:33:89': 'Huawei',
        '04:B0:E7': 'Huawei',
        '04:C0:6F': 'Huawei',
        '04:F9:38': 'Huawei',
        '08:19:A6': 'Huawei',
        '08:63:61': 'Huawei',
        '08:7A:4C': 'Huawei',
        '10:47:80': 'Huawei',
        '10:C6:1F': 'Huawei',
        '14:30:04': 'Huawei',
        '14:A0:F8': 'Huawei',
        '18:DE:D7': 'Huawei',
        '1C:1D:67': 'Huawei',
        '1C:8E:5C': 'Huawei',
        '20:08:ED': 'Huawei',
        '20:0B:C7': 'Huawei',
    }
    
    # Device type detection patterns
    DEVICE_PATTERNS = {
        'iPhone': ['iphone', 'apple'],
        'iPad': ['ipad', 'apple'],
        'MacBook': ['macbook', 'mac', 'apple'],
        'Apple Watch': ['watch', 'apple'],
        'Samsung Galaxy': ['samsung', 'galaxy'],
        'Xiaomi': ['xiaomi', 'redmi', 'poco'],
        'Huawei': ['huawei', 'honor'],
        'Smart TV': ['tv', 'smart', 'roku', 'fire'],
        'Router': ['router', 'gateway'],
        'Computer': ['pc', 'desktop', 'laptop', 'windows'],
    }
    
    def __init__(self):
        self.devices_db = {}
        self.blocked_devices = []
        self.bandwidth_limits = {}
    
    def scan_network(self) -> List[Dict]:
        """Scan network for all devices"""
        devices = []
        
        try:
            # Get ARP table
            result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                # Parse ARP entries
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]+)\s+(\w+)', line)
                if match:
                    ip = match.group(1)
                    mac = match.group(2).replace('-', ':').upper()
                    interface_type = match.group(3)
                    
                    if ip.startswith('224.') or ip.startswith('255.') or mac == 'FF:FF:FF:FF:FF:FF':
                        continue
                    
                    # Get manufacturer
                    mac_prefix = mac[:8]
                    manufacturer = self.MANUFACTURERS.get(mac_prefix, 'Unknown')
                    
                    # Determine device type
                    device_type = self._detect_device_type(manufacturer, ip)
                    
                    # Try to get hostname
                    hostname = self._get_hostname(ip)
                    
                    device = {
                        'ip': ip,
                        'mac': mac,
                        'manufacturer': manufacturer,
                        'hostname': hostname,
                        'device_type': device_type,
                        'is_apple': 'Apple' in manufacturer,
                        'is_blocked': ip in self.blocked_devices or mac in self.blocked_devices,
                        'online': True,
                        'last_seen': datetime.now().isoformat()
                    }
                    
                    devices.append(device)
                    self.devices_db[mac] = device
            
        except Exception as e:
            print(f"Scan error: {e}")
        
        return devices
    
    def _detect_device_type(self, manufacturer: str, ip: str) -> str:
        """Detect device type based on manufacturer and other info"""
        mfr_lower = manufacturer.lower()
        
        if 'apple' in mfr_lower:
            return 'Apple Device'
        elif 'samsung' in mfr_lower:
            return 'Samsung Device'
        elif 'xiaomi' in mfr_lower:
            return 'Xiaomi Device'
        elif 'huawei' in mfr_lower:
            return 'Huawei Device'
        elif ip.endswith('.1'):
            return 'Router/Gateway'
        else:
            return 'Unknown Device'
    
    def _get_hostname(self, ip: str) -> str:
        """Try to get hostname from IP"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return ''
    
    def get_device_info(self, ip: str) -> Dict:
        """Get detailed info about a device"""
        info = {
            'ip': ip,
            'reachable': False,
            'ports': [],
            'services': []
        }
        
        try:
            # Ping test
            result = subprocess.run(
                ['ping', '-n', '1', '-w', '1000', ip],
                capture_output=True,
                text=True
            )
            info['reachable'] = 'TTL=' in result.stdout
            
            # Basic port scan (common ports)
            common_ports = [80, 443, 22, 21, 8080, 62078]  # 62078 is iOS sync
            
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    result = sock.connect_ex((ip, port))
                    if result == 0:
                        service = self._port_to_service(port)
                        info['ports'].append(port)
                        info['services'].append(service)
                    sock.close()
                except:
                    pass
            
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    def _port_to_service(self, port: int) -> str:
        """Map port to service name"""
        services = {
            21: 'FTP',
            22: 'SSH',
            80: 'HTTP',
            443: 'HTTPS',
            445: 'SMB',
            548: 'AFP',
            3389: 'RDP',
            5000: 'AirPlay',
            5353: 'mDNS',
            8080: 'HTTP Alt',
            62078: 'iOS Sync'
        }
        return services.get(port, f'Port {port}')
    
    def block_device(self, identifier: str) -> Dict:
        """Block device from network access (requires admin + router access)"""
        # Note: This is a placeholder - actual implementation depends on router
        # For now, we'll block via Windows Firewall
        try:
            ip = identifier
            
            # Block inbound
            result = subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name=Block_{ip}', 'dir=in', 'action=block', f'remoteip={ip}'
            ], capture_output=True, text=True)
            
            # Block outbound
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name=Block_{ip}_out', 'dir=out', 'action=block', f'remoteip={ip}'
            ], capture_output=True, text=True)
            
            self.blocked_devices.append(ip)
            
            return {'success': True, 'blocked': ip}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def unblock_device(self, identifier: str) -> Dict:
        """Unblock a device"""
        try:
            ip = identifier
            
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                f'name=Block_{ip}'
            ], capture_output=True, text=True)
            
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                f'name=Block_{ip}_out'
            ], capture_output=True, text=True)
            
            if ip in self.blocked_devices:
                self.blocked_devices.remove(ip)
            
            return {'success': True, 'unblocked': ip}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def disconnect_device(self, mac: str, interface: str = 'Wi-Fi') -> Dict:
        """
        Attempt to disconnect a device using deauth packets.
        Note: This requires admin privileges and may not work on all networks.
        FOR EDUCATIONAL PURPOSES ONLY!
        """
        try:
            # This would require scapy for proper deauth
            # For now, return info about limitations
            return {
                'success': False,
                'message': 'Deauth requires specialized hardware (WiFi adapter in monitor mode)',
                'note': 'Consider using your router admin panel to disconnect devices'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_apple_devices(self) -> List[Dict]:
        """Get only Apple devices on the network"""
        all_devices = self.scan_network()
        return [d for d in all_devices if d.get('is_apple', False)]
    
    def get_bandwidth_usage(self, ip: str) -> Dict:
        """Get bandwidth usage for a device (requires advanced monitoring)"""
        # This would require packet capture and monitoring
        # Placeholder for future implementation
        return {
            'ip': ip,
            'note': 'Bandwidth monitoring requires packet capture setup',
            'suggestion': 'Use your router admin panel for detailed bandwidth info'
        }


class DeviceManager:
    """Main device management class"""
    
    def __init__(self):
        self.controller = DeviceControl()
        self.scan_interval = 30  # seconds
        self.last_scan = None
        self.cached_devices = []
    
    def scan(self, force: bool = False) -> List[Dict]:
        """Scan network for devices"""
        now = datetime.now()
        
        # Use cache if recent
        if not force and self.last_scan and (now - self.last_scan).seconds < self.scan_interval:
            return self.cached_devices
        
        self.cached_devices = self.controller.scan_network()
        self.last_scan = now
        return self.cached_devices
    
    def get_device(self, identifier: str) -> Optional[Dict]:
        """Get device by IP or MAC"""
        devices = self.scan()
        for d in devices:
            if d['ip'] == identifier or d['mac'] == identifier:
                return d
        return None
    
    def get_devices_by_type(self, device_type: str = 'apple') -> List[Dict]:
        """Get devices filtered by type"""
        devices = self.scan()
        
        if device_type.lower() == 'apple':
            return [d for d in devices if d.get('is_apple')]
        elif device_type.lower() == 'android':
            return [d for d in devices if 'samsung' in d.get('manufacturer', '').lower() 
                   or 'xiaomi' in d.get('manufacturer', '').lower()
                   or 'huawei' in d.get('manufacturer', '').lower()]
        else:
            return devices
    
    def device_action(self, action: str, identifier: str, options: Dict = None) -> Dict:
        """Perform action on device"""
        options = options or {}
        
        if action == 'info':
            return self.controller.get_device_info(identifier)
        elif action == 'block':
            return self.controller.block_device(identifier)
        elif action == 'unblock':
            return self.controller.unblock_device(identifier)
        elif action == 'disconnect':
            return self.controller.disconnect_device(identifier)
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}
    
    def get_ios_info(self) -> Dict:
        """Information about iOS device control limitations"""
        return {
            'title': 'iOS Device Control - Information',
            'what_you_can_do': [
                'See iOS devices on your network',
                'View IP address, MAC address, manufacturer',
                'Block internet access via firewall',
                'Monitor network traffic (amount, not content)',
                'Kick device from WiFi (requires special hardware)'
            ],
            'what_you_cannot_do': [
                'Access files on iOS devices - iOS is encrypted',
                'Read messages, photos, or personal data',
                'Install apps or modify the device remotely',
                'Bypass iOS security without physical access',
                'Access iCloud data without credentials'
            ],
            'legal_notice': 'Accessing someone else\'s device without permission is illegal. Only use these tools on your own network for legitimate purposes like parental controls.',
            'alternatives': [
                'For parental control: Use Screen Time (built into iOS)',
                'For device management: Use MDM solutions',
                'For family sharing: Use Apple Family Sharing',
                'For bandwidth control: Use your router\'s QoS settings'
            ]
        }


if __name__ == "__main__":
    manager = DeviceManager()
    
    print("\n=== Network Devices ===")
    devices = manager.scan(force=True)
    
    for d in devices:
        icon = "📱" if d.get('is_apple') else "💻"
        print(f"{icon} {d['ip']} - {d['mac']} - {d['manufacturer']} - {d['hostname'] or 'N/A'}")
    
    print(f"\nTotal: {len(devices)} devices")
    print(f"Apple devices: {len([d for d in devices if d.get('is_apple')])}")
    
    print("\n=== iOS Control Info ===")
    info = manager.get_ios_info()
    print(f"What you CAN do: {len(info['what_you_can_do'])} things")
    print(f"What you CANNOT do: {len(info['what_you_cannot_do'])} things")
