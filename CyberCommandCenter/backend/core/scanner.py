"""
Cyber Command Center - Network Scanner
Core module for discovering and monitoring devices on the local network
"""
import socket
import subprocess
import platform
import re
import threading
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from scapy.all import ARP, Ether, srp, conf, get_if_list, get_if_addr
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

try:
    import netifaces
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False


class NetworkScanner:
    """
    Network scanner for discovering devices on the local network
    """
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.gateway_ip = None
        self.local_ip = None
        self.subnet_mask = None
        self.network_range = None
        self._setup_network_info()
    
    def _setup_network_info(self):
        """Setup network information"""
        try:
            # Get default gateway and local IP
            if NETIFACES_AVAILABLE:
                gateways = netifaces.gateways()
                if 'default' in gateways and netifaces.AF_INET in gateways['default']:
                    self.gateway_ip = gateways['default'][netifaces.AF_INET][0]
                    self.interface = self.interface or gateways['default'][netifaces.AF_INET][1]
                
                if self.interface:
                    addrs = netifaces.ifaddresses(self.interface)
                    if netifaces.AF_INET in addrs:
                        self.local_ip = addrs[netifaces.AF_INET][0].get('addr')
                        self.subnet_mask = addrs[netifaces.AF_INET][0].get('netmask')
            
            # Fallback: try socket method
            if not self.local_ip:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                self.local_ip = s.getsockname()[0]
                s.close()
            
            # Calculate network range
            if self.local_ip:
                ip_parts = self.local_ip.split('.')
                self.network_range = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
                
                if not self.gateway_ip:
                    self.gateway_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.1"
                    
        except Exception as e:
            print(f"Error setting up network info: {e}")
            self.network_range = "192.168.1.0/24"
            self.gateway_ip = "192.168.1.1"
    
    def get_network_info(self) -> Dict:
        """Get current network information"""
        return {
            'interface': self.interface,
            'local_ip': self.local_ip,
            'gateway_ip': self.gateway_ip,
            'subnet_mask': self.subnet_mask,
            'network_range': self.network_range,
            'scapy_available': SCAPY_AVAILABLE,
            'nmap_available': NMAP_AVAILABLE
        }
    
    def scan_arp(self, timeout: int = 3) -> List[Dict]:
        """
        Scan network using ARP requests (fastest method)
        """
        devices = []
        
        if not SCAPY_AVAILABLE:
            return self.scan_ping()
        
        try:
            # Disable verbose output
            conf.verb = 0
            
            # Create ARP request
            arp_request = ARP(pdst=self.network_range)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast / arp_request
            
            # Send and receive
            answered, _ = srp(packet, timeout=timeout, verbose=False)
            
            for sent, received in answered:
                device = {
                    'ip': received.psrc,
                    'mac': received.hwsrc.upper(),
                    'hostname': self._get_hostname(received.psrc),
                    'vendor': self._get_vendor(received.hwsrc),
                    'is_gateway': received.psrc == self.gateway_ip
                }
                devices.append(device)
                
        except Exception as e:
            print(f"ARP scan error: {e}")
            return self.scan_ping()
        
        return devices
    
    def scan_ping(self, timeout: int = 1) -> List[Dict]:
        """
        Scan network using ping (fallback method)
        """
        devices = []
        
        if not self.local_ip:
            return devices
        
        ip_base = '.'.join(self.local_ip.split('.')[:-1])
        
        def ping_host(ip: str) -> Optional[Dict]:
            try:
                # Platform-specific ping command
                if platform.system().lower() == 'windows':
                    cmd = ['ping', '-n', '1', '-w', str(timeout * 1000), ip]
                else:
                    cmd = ['ping', '-c', '1', '-W', str(timeout), ip]
                
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=timeout + 1
                )
                
                if result.returncode == 0:
                    mac = self._get_mac_from_ip(ip)
                    return {
                        'ip': ip,
                        'mac': mac or 'Unknown',
                        'hostname': self._get_hostname(ip),
                        'vendor': self._get_vendor(mac) if mac else 'Unknown',
                        'is_gateway': ip == self.gateway_ip
                    }
            except Exception:
                pass
            return None
        
        # Scan in parallel
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {
                executor.submit(ping_host, f"{ip_base}.{i}"): i 
                for i in range(1, 255)
            }
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    devices.append(result)
        
        return devices
    
    def scan_nmap(self, scan_type: str = 'quick') -> List[Dict]:
        """
        Scan network using nmap (most detailed)
        """
        devices = []
        
        if not NMAP_AVAILABLE:
            return self.scan_arp()
        
        try:
            nm = nmap.PortScanner()
            
            if scan_type == 'quick':
                nm.scan(hosts=self.network_range, arguments='-sn')
            elif scan_type == 'detailed':
                nm.scan(hosts=self.network_range, arguments='-sV -O')
            else:
                nm.scan(hosts=self.network_range, arguments='-sn')
            
            for host in nm.all_hosts():
                device = {
                    'ip': host,
                    'mac': nm[host]['addresses'].get('mac', 'Unknown'),
                    'hostname': nm[host].hostname() or self._get_hostname(host),
                    'vendor': nm[host].get('vendor', {}).get(
                        nm[host]['addresses'].get('mac', ''), 'Unknown'
                    ),
                    'is_gateway': host == self.gateway_ip,
                    'state': nm[host].state()
                }
                
                # Add OS info if available
                if 'osmatch' in nm[host] and nm[host]['osmatch']:
                    device['os'] = nm[host]['osmatch'][0].get('name', 'Unknown')
                
                # Add open ports if available
                if 'tcp' in nm[host]:
                    device['ports'] = list(nm[host]['tcp'].keys())
                
                devices.append(device)
                
        except Exception as e:
            print(f"Nmap scan error: {e}")
            return self.scan_arp()
        
        return devices
    
    def _get_hostname(self, ip: str) -> str:
        """Get hostname for an IP address"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except (socket.herror, socket.gaierror):
            return ""
    
    def _get_mac_from_ip(self, ip: str) -> Optional[str]:
        """Get MAC address from IP using ARP table"""
        try:
            if platform.system().lower() == 'windows':
                output = subprocess.check_output(['arp', '-a', ip], text=True)
                match = re.search(r'([0-9a-fA-F]{2}[:-]){5}[0-9a-fA-F]{2}', output)
                if match:
                    return match.group().replace('-', ':').upper()
            else:
                output = subprocess.check_output(['arp', '-n', ip], text=True)
                match = re.search(r'([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}', output)
                if match:
                    return match.group().upper()
        except Exception:
            pass
        return None
    
    def _get_vendor(self, mac: str) -> str:
        """Get vendor from MAC address"""
        if not mac or mac == 'Unknown':
            return 'Unknown'
        
        # Use first 3 octets (OUI)
        mac_prefix = mac.upper().replace('-', ':')[:8]
        
        # Check against known vendors
        from config import MAC_VENDORS
        
        for prefix, vendor in MAC_VENDORS.items():
            if mac_prefix.startswith(prefix):
                return vendor
        
        # Try online lookup
        try:
            from mac_vendor_lookup import MacLookup
            mac_lookup = MacLookup()
            return mac_lookup.lookup(mac)
        except Exception:
            pass
        
        return 'Unknown'
    
    def get_device_type(self, device: Dict) -> str:
        """Guess device type based on available info"""
        hostname = (device.get('hostname') or '').lower()
        vendor = (device.get('vendor') or '').lower()
        mac = device.get('mac', '')
        
        # Check hostname patterns
        if any(x in hostname for x in ['iphone', 'ipad', 'android', 'galaxy', 'pixel']):
            return 'mobile'
        if any(x in hostname for x in ['macbook', 'laptop', 'desktop', 'pc', 'windows']):
            return 'computer'
        if any(x in hostname for x in ['tv', 'roku', 'chromecast', 'firestick', 'appletv']):
            return 'tv'
        if any(x in hostname for x in ['playstation', 'xbox', 'nintendo', 'switch']):
            return 'gaming'
        if any(x in hostname for x in ['printer', 'print']):
            return 'printer'
        if any(x in hostname for x in ['camera', 'cam', 'nest', 'ring']):
            return 'camera'
        if any(x in hostname for x in ['alexa', 'echo', 'google-home', 'homepod']):
            return 'smart_speaker'
        
        # Check vendor
        if any(x in vendor for x in ['apple']):
            return 'apple_device'
        if any(x in vendor for x in ['samsung', 'huawei', 'xiaomi', 'oppo']):
            return 'mobile'
        if any(x in vendor for x in ['dell', 'hp', 'lenovo', 'asus', 'acer']):
            return 'computer'
        if any(x in vendor for x in ['raspberry']):
            return 'raspberry_pi'
        if any(x in vendor for x in ['espressif', 'tuya']):
            return 'iot'
        
        return 'unknown'
    
    def port_scan(self, ip: str, ports: List[int] = None, timeout: float = 0.5) -> List[Dict]:
        """
        Scan ports on a specific IP
        """
        if ports is None:
            # Common ports
            ports = [
                20, 21, 22, 23, 25, 53, 80, 110, 119, 123, 135, 139, 143, 161,
                194, 443, 445, 993, 995, 1433, 1521, 1723, 3306, 3389, 5432,
                5900, 5901, 8000, 8080, 8443, 8888, 9000, 9090, 27017
            ]
        
        open_ports = []
        
        def check_port(port: int) -> Optional[Dict]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                
                if result == 0:
                    service = self._get_service_name(port)
                    return {
                        'port': port,
                        'state': 'open',
                        'service': service,
                        'protocol': 'tcp'
                    }
            except Exception:
                pass
            return None
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(check_port, port): port for port in ports}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)
        
        return sorted(open_ports, key=lambda x: x['port'])
    
    def _get_service_name(self, port: int) -> str:
        """Get service name for common ports"""
        services = {
            20: 'FTP Data', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
            25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
            119: 'NNTP', 123: 'NTP', 135: 'MS-RPC', 139: 'NetBIOS',
            143: 'IMAP', 161: 'SNMP', 194: 'IRC', 443: 'HTTPS',
            445: 'SMB', 993: 'IMAPS', 995: 'POP3S', 1433: 'MSSQL',
            1521: 'Oracle', 1723: 'PPTP', 3306: 'MySQL', 3389: 'RDP',
            5432: 'PostgreSQL', 5900: 'VNC', 5901: 'VNC', 8000: 'HTTP-Alt',
            8080: 'HTTP-Proxy', 8443: 'HTTPS-Alt', 8888: 'HTTP-Alt',
            9000: 'HTTP-Alt', 9090: 'HTTP-Alt', 27017: 'MongoDB'
        }
        
        try:
            return services.get(port) or socket.getservbyport(port)
        except OSError:
            return 'Unknown'


class NetworkMonitor:
    """
    Continuous network monitoring
    """
    
    def __init__(self, scanner: NetworkScanner, callback=None):
        self.scanner = scanner
        self.callback = callback
        self.known_devices = {}
        self.is_running = False
        self._thread = None
    
    def start(self, interval: int = 30):
        """Start continuous monitoring"""
        self.is_running = True
        self._thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self._thread.daemon = True
        self._thread.start()
    
    def stop(self):
        """Stop monitoring"""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def _monitor_loop(self, interval: int):
        """Main monitoring loop"""
        while self.is_running:
            try:
                current_devices = {d['mac']: d for d in self.scanner.scan_arp()}
                
                # Check for new devices
                for mac, device in current_devices.items():
                    if mac not in self.known_devices:
                        if self.callback:
                            self.callback('new_device', device)
                        self.known_devices[mac] = device
                        self.known_devices[mac]['online'] = True
                    else:
                        # Device came back online
                        if not self.known_devices[mac].get('online'):
                            if self.callback:
                                self.callback('device_online', device)
                            self.known_devices[mac]['online'] = True
                
                # Check for disconnected devices
                for mac in self.known_devices:
                    if mac not in current_devices:
                        if self.known_devices[mac].get('online'):
                            if self.callback:
                                self.callback('device_offline', self.known_devices[mac])
                            self.known_devices[mac]['online'] = False
                
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(interval)
    
    def get_online_devices(self) -> List[Dict]:
        """Get list of online devices"""
        return [d for d in self.known_devices.values() if d.get('online')]
    
    def get_all_devices(self) -> List[Dict]:
        """Get all known devices"""
        return list(self.known_devices.values())


if __name__ == "__main__":
    # Test the scanner
    scanner = NetworkScanner()
    print("Network Info:")
    print(scanner.get_network_info())
    print("\nScanning network...")
    devices = scanner.scan_arp()
    print(f"\nFound {len(devices)} devices:")
    for device in devices:
        print(f"  {device['ip']:15} | {device['mac']:17} | {device.get('hostname', 'N/A'):20} | {device.get('vendor', 'Unknown')}")
