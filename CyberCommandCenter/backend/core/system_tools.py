"""
Cyber Command Center - System Tools
Advanced network tools that work on Windows
"""
import subprocess
import platform
import re
import socket
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    SPEEDTEST_AVAILABLE = False


class SpeedTester:
    """Internet speed test utility"""
    
    def __init__(self):
        self.last_result = None
        self.is_testing = False
    
    def run_test(self, include_upload: bool = True) -> Dict:
        """Run a speed test"""
        if not SPEEDTEST_AVAILABLE:
            # Fallback: use speedtest-cli command
            return self._run_cli_test()
        
        self.is_testing = True
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'server': {
                    'name': st.best['name'],
                    'country': st.best['country'],
                    'sponsor': st.best['sponsor'],
                    'latency': st.best['latency']
                },
                'download': 0,
                'upload': 0,
                'ping': st.best['latency']
            }
            
            # Download test
            download = st.download()
            result['download'] = round(download / 1_000_000, 2)  # Mbps
            
            # Upload test
            if include_upload:
                upload = st.upload()
                result['upload'] = round(upload / 1_000_000, 2)  # Mbps
            
            self.last_result = result
            return result
            
        except Exception as e:
            return {'error': str(e)}
        finally:
            self.is_testing = False
    
    def _run_cli_test(self) -> Dict:
        """Fallback using CLI"""
        try:
            result = subprocess.run(
                ['speedtest-cli', '--json'],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    'timestamp': datetime.now().isoformat(),
                    'download': round(data['download'] / 1_000_000, 2),
                    'upload': round(data['upload'] / 1_000_000, 2),
                    'ping': data['ping'],
                    'server': {
                        'name': data['server']['name'],
                        'country': data['server']['country'],
                        'sponsor': data['server']['sponsor']
                    }
                }
        except Exception as e:
            return {'error': str(e)}


class WiFiPasswordRecovery:
    """Recover saved WiFi passwords from Windows"""
    
    @staticmethod
    def get_saved_networks() -> List[Dict]:
        """Get list of saved WiFi networks with passwords"""
        networks = []
        
        if platform.system().lower() != 'windows':
            return [{'error': 'Only available on Windows'}]
        
        try:
            # Get list of profiles
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'profiles'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            # Extract profile names
            profile_pattern = r"All User Profile\s*:\s*(.+)|Perfil de todos los usuarios\s*:\s*(.+)"
            matches = re.findall(profile_pattern, result.stdout)
            profile_names = [m[0] or m[1] for m in matches if m[0] or m[1]]
            
            for name in profile_names:
                name = name.strip()
                network = {
                    'name': name,
                    'password': None,
                    'security': None,
                    'authentication': None
                }
                
                # Get password for each profile
                try:
                    detail_result = subprocess.run(
                        ['netsh', 'wlan', 'show', 'profile', f'name={name}', 'key=clear'],
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    
                    # Extract password
                    pwd_pattern = r"Key Content\s*:\s*(.+)|Contenido de la clave\s*:\s*(.+)"
                    pwd_match = re.search(pwd_pattern, detail_result.stdout)
                    if pwd_match:
                        network['password'] = (pwd_match.group(1) or pwd_match.group(2)).strip()
                    
                    # Extract security type
                    sec_pattern = r"Authentication\s*:\s*(.+)|Autenticación\s*:\s*(.+)"
                    sec_match = re.search(sec_pattern, detail_result.stdout)
                    if sec_match:
                        network['authentication'] = (sec_match.group(1) or sec_match.group(2)).strip()
                    
                    # Extract cipher
                    cipher_pattern = r"Cipher\s*:\s*(.+)|Cifrado\s*:\s*(.+)"
                    cipher_match = re.search(cipher_pattern, detail_result.stdout)
                    if cipher_match:
                        network['security'] = (cipher_match.group(1) or cipher_match.group(2)).strip()
                        
                except Exception:
                    pass
                
                networks.append(network)
            
            return networks
            
        except Exception as e:
            return [{'error': str(e)}]


class ConnectionsMonitor:
    """Monitor active network connections"""
    
    @staticmethod
    def get_active_connections() -> List[Dict]:
        """Get all active network connections"""
        connections = []
        
        if not PSUTIL_AVAILABLE:
            return ConnectionsMonitor._get_connections_netstat()
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                connection = {
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'status': conn.status,
                    'pid': conn.pid,
                    'process_name': None,
                    'type': 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP'
                }
                
                # Get process name
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        connection['process_name'] = proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                connections.append(connection)
            
            return connections
            
        except psutil.AccessDenied:
            return ConnectionsMonitor._get_connections_netstat()
        except Exception as e:
            return [{'error': str(e)}]
    
    @staticmethod
    def _get_connections_netstat() -> List[Dict]:
        """Fallback using netstat command"""
        connections = []
        try:
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
            
            lines = result.stdout.strip().split('\n')[4:]  # Skip header
            for line in lines:
                parts = line.split()
                if len(parts) >= 4:
                    conn = {
                        'type': parts[0],
                        'local_address': parts[1],
                        'remote_address': parts[2] if parts[2] != '*:*' else None,
                        'status': parts[3] if len(parts) > 4 else 'LISTENING',
                        'pid': int(parts[-1]) if parts[-1].isdigit() else None,
                        'process_name': None
                    }
                    connections.append(conn)
            
            return connections
        except Exception as e:
            return [{'error': str(e)}]
    
    @staticmethod
    def get_connection_stats() -> Dict:
        """Get connection statistics"""
        if not PSUTIL_AVAILABLE:
            return {'error': 'psutil not available'}
        
        try:
            connections = psutil.net_connections(kind='inet')
            stats = {
                'total': len(connections),
                'established': 0,
                'listening': 0,
                'time_wait': 0,
                'close_wait': 0,
                'other': 0
            }
            
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    stats['established'] += 1
                elif conn.status == 'LISTEN':
                    stats['listening'] += 1
                elif conn.status == 'TIME_WAIT':
                    stats['time_wait'] += 1
                elif conn.status == 'CLOSE_WAIT':
                    stats['close_wait'] += 1
                else:
                    stats['other'] += 1
            
            return stats
        except Exception as e:
            return {'error': str(e)}


class ProcessNetworkMonitor:
    """Monitor network usage by process"""
    
    @staticmethod
    def get_process_network_usage() -> List[Dict]:
        """Get network usage per process"""
        if not PSUTIL_AVAILABLE:
            return [{'error': 'psutil not available'}]
        
        processes = []
        
        try:
            # Get all processes with network connections
            connections = psutil.net_connections(kind='inet')
            
            # Group by PID
            pid_connections = {}
            for conn in connections:
                if conn.pid:
                    if conn.pid not in pid_connections:
                        pid_connections[conn.pid] = []
                    pid_connections[conn.pid].append(conn)
            
            # Get process details
            for pid, conns in pid_connections.items():
                try:
                    proc = psutil.Process(pid)
                    io_counters = proc.io_counters() if hasattr(proc, 'io_counters') else None
                    
                    process_info = {
                        'pid': pid,
                        'name': proc.name(),
                        'status': proc.status(),
                        'connections': len(conns),
                        'established': sum(1 for c in conns if c.status == 'ESTABLISHED'),
                        'listening': sum(1 for c in conns if c.status == 'LISTEN'),
                        'cpu_percent': proc.cpu_percent(interval=0.1),
                        'memory_mb': round(proc.memory_info().rss / 1024 / 1024, 2),
                        'bytes_sent': io_counters.write_bytes if io_counters else 0,
                        'bytes_recv': io_counters.read_bytes if io_counters else 0
                    }
                    processes.append(process_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by connections
            processes.sort(key=lambda x: x['connections'], reverse=True)
            return processes
            
        except Exception as e:
            return [{'error': str(e)}]


class PingMonitor:
    """Real-time ping monitor"""
    
    def __init__(self):
        self.is_monitoring = False
        self.results = []
        self._monitor_thread = None
    
    def ping_host(self, host: str, count: int = 1, timeout: int = 1000) -> Dict:
        """Ping a single host"""
        try:
            if platform.system().lower() == 'windows':
                cmd = ['ping', '-n', str(count), '-w', str(timeout), host]
            else:
                cmd = ['ping', '-c', str(count), '-W', str(timeout // 1000), host]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout/1000 + 5)
            
            # Parse result
            output = result.stdout
            
            # Extract latency
            if platform.system().lower() == 'windows':
                # Windows format: "tiempo=XXms" or "time=XXms"
                match = re.search(r'(?:tiempo|time)[=<](\d+)ms', output, re.IGNORECASE)
            else:
                match = re.search(r'time=(\d+\.?\d*)\s*ms', output)
            
            latency = float(match.group(1)) if match else None
            
            # Check if reachable
            is_reachable = result.returncode == 0 and latency is not None
            
            return {
                'host': host,
                'timestamp': datetime.now().isoformat(),
                'reachable': is_reachable,
                'latency_ms': latency,
                'ttl': self._extract_ttl(output)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'host': host,
                'timestamp': datetime.now().isoformat(),
                'reachable': False,
                'latency_ms': None,
                'error': 'Timeout'
            }
        except Exception as e:
            return {
                'host': host,
                'timestamp': datetime.now().isoformat(),
                'reachable': False,
                'latency_ms': None,
                'error': str(e)
            }
    
    def _extract_ttl(self, output: str) -> Optional[int]:
        """Extract TTL from ping output"""
        match = re.search(r'TTL[=:](\d+)', output, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    def ping_multiple(self, hosts: List[str]) -> List[Dict]:
        """Ping multiple hosts in parallel"""
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self.ping_host, host): host for host in hosts}
            for future in futures:
                results.append(future.result())
        return results


class ARPTableViewer:
    """View and manage ARP table"""
    
    @staticmethod
    def get_arp_table() -> List[Dict]:
        """Get system ARP table"""
        entries = []
        
        try:
            result = subprocess.run(
                ['arp', '-a'],
                capture_output=True,
                text=True
            )
            
            # Parse ARP table
            current_interface = None
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                # Check for interface line
                if 'Interface:' in line or 'Interfaz:' in line:
                    match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                    if match:
                        current_interface = match.group(1)
                    continue
                
                # Parse entry
                match = re.match(
                    r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F-]+)\s+(\w+)',
                    line
                )
                if match:
                    entry = {
                        'ip': match.group(1),
                        'mac': match.group(2).replace('-', ':').upper(),
                        'type': match.group(3),
                        'interface': current_interface
                    }
                    entries.append(entry)
            
            return entries
            
        except Exception as e:
            return [{'error': str(e)}]
    
    @staticmethod
    def flush_arp_cache() -> Dict:
        """Flush ARP cache (requires admin)"""
        try:
            result = subprocess.run(
                ['netsh', 'interface', 'ip', 'delete', 'arpcache'],
                capture_output=True,
                text=True
            )
            return {
                'success': result.returncode == 0,
                'message': result.stdout or result.stderr
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class DNSTools:
    """DNS utilities"""
    
    @staticmethod
    def get_dns_cache() -> List[Dict]:
        """Get DNS cache (Windows only)"""
        entries = []
        
        if platform.system().lower() != 'windows':
            return [{'error': 'Only available on Windows'}]
        
        try:
            result = subprocess.run(
                ['ipconfig', '/displaydns'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            current_entry = {}
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                if 'Record Name' in line or 'Nombre de registro' in line:
                    if current_entry:
                        entries.append(current_entry)
                    current_entry = {'name': line.split(':')[-1].strip()}
                elif 'Record Type' in line or 'Tipo de registro' in line:
                    current_entry['type'] = line.split(':')[-1].strip()
                elif 'Time To Live' in line or 'Tiempo de vida' in line:
                    current_entry['ttl'] = line.split(':')[-1].strip()
                elif ('A (Host) Record' in line or 'Registro de (host)' in line or 
                      'AAAA Record' in line):
                    current_entry['address'] = line.split(':')[-1].strip()
            
            if current_entry:
                entries.append(current_entry)
            
            return entries[:100]  # Limit to 100 entries
            
        except Exception as e:
            return [{'error': str(e)}]
    
    @staticmethod
    def flush_dns_cache() -> Dict:
        """Flush DNS cache"""
        try:
            result = subprocess.run(
                ['ipconfig', '/flushdns'],
                capture_output=True,
                text=True
            )
            return {
                'success': result.returncode == 0,
                'message': result.stdout.strip()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def dns_lookup(domain: str, record_type: str = 'A') -> Dict:
        """Perform DNS lookup"""
        try:
            result = subprocess.run(
                ['nslookup', '-type=' + record_type, domain],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                'domain': domain,
                'type': record_type,
                'result': result.stdout,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {'domain': domain, 'error': str(e)}


class SystemNetworkInfo:
    """System network information"""
    
    @staticmethod
    def get_network_interfaces() -> List[Dict]:
        """Get all network interfaces"""
        if not PSUTIL_AVAILABLE:
            return [{'error': 'psutil not available'}]
        
        interfaces = []
        
        try:
            # Get addresses
            addrs = psutil.net_if_addrs()
            # Get stats
            stats = psutil.net_if_stats()
            # Get IO counters
            io = psutil.net_io_counters(pernic=True)
            
            for name, addr_list in addrs.items():
                iface = {
                    'name': name,
                    'addresses': [],
                    'is_up': stats[name].isup if name in stats else False,
                    'speed': stats[name].speed if name in stats else 0,
                    'mtu': stats[name].mtu if name in stats else 0,
                    'bytes_sent': io[name].bytes_sent if name in io else 0,
                    'bytes_recv': io[name].bytes_recv if name in io else 0,
                    'packets_sent': io[name].packets_sent if name in io else 0,
                    'packets_recv': io[name].packets_recv if name in io else 0,
                    'errors_in': io[name].errin if name in io else 0,
                    'errors_out': io[name].errout if name in io else 0
                }
                
                for addr in addr_list:
                    addr_info = {
                        'family': str(addr.family.name),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    }
                    iface['addresses'].append(addr_info)
                
                interfaces.append(iface)
            
            return interfaces
            
        except Exception as e:
            return [{'error': str(e)}]
    
    @staticmethod
    def get_network_io_stats() -> Dict:
        """Get overall network IO statistics"""
        if not PSUTIL_AVAILABLE:
            return {'error': 'psutil not available'}
        
        try:
            io = psutil.net_io_counters()
            return {
                'bytes_sent': io.bytes_sent,
                'bytes_recv': io.bytes_recv,
                'packets_sent': io.packets_sent,
                'packets_recv': io.packets_recv,
                'errors_in': io.errin,
                'errors_out': io.errout,
                'drops_in': io.dropin,
                'drops_out': io.dropout,
                'bytes_sent_mb': round(io.bytes_sent / 1024 / 1024, 2),
                'bytes_recv_mb': round(io.bytes_recv / 1024 / 1024, 2)
            }
        except Exception as e:
            return {'error': str(e)}
