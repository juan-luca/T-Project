"""
Cyber Command Center - Packet Sniffer
Module for capturing and analyzing network traffic
"""
import threading
import time
from datetime import datetime
from typing import Optional, List, Dict, Callable
from collections import defaultdict

try:
    from scapy.all import (
        sniff, IP, TCP, UDP, ICMP, DNS, DNSQR, Raw,
        ARP, Ether, conf, get_if_list
    )
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


class PacketSniffer:
    """
    Network packet sniffer for traffic analysis
    """
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.is_sniffing = False
        self.packets = []
        self.stats = defaultdict(int)
        self._thread = None
        self._callbacks = []
        
        if SCAPY_AVAILABLE:
            conf.verb = 0
    
    def add_callback(self, callback: Callable):
        """Add a callback function for new packets"""
        self._callbacks.append(callback)
    
    def start(self, filter_str: str = None, packet_count: int = 0):
        """
        Start packet capture
        
        Args:
            filter_str: BPF filter string (e.g., "tcp port 80")
            packet_count: Number of packets to capture (0 = unlimited)
        """
        if not SCAPY_AVAILABLE:
            raise Exception("Scapy not available")
        
        if self.is_sniffing:
            return False
        
        self.is_sniffing = True
        self.packets = []
        self.stats = defaultdict(int)
        
        def capture_packets():
            try:
                sniff(
                    iface=self.interface,
                    prn=self._process_packet,
                    filter=filter_str,
                    count=packet_count if packet_count > 0 else 0,
                    store=False,
                    stop_filter=lambda x: not self.is_sniffing
                )
            except Exception as e:
                print(f"Sniffer error: {e}")
            finally:
                self.is_sniffing = False
        
        self._thread = threading.Thread(target=capture_packets)
        self._thread.daemon = True
        self._thread.start()
        
        return True
    
    def stop(self):
        """Stop packet capture"""
        self.is_sniffing = False
        if self._thread:
            self._thread.join(timeout=5)
    
    def _process_packet(self, packet):
        """Process captured packet"""
        try:
            packet_info = self._parse_packet(packet)
            
            if packet_info:
                self.packets.append(packet_info)
                self.stats['total'] += 1
                self.stats[packet_info.get('protocol', 'other')] += 1
                
                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(packet_info)
                    except Exception:
                        pass
                
                # Limit stored packets
                if len(self.packets) > 10000:
                    self.packets = self.packets[-5000:]
                    
        except Exception as e:
            pass
    
    def _parse_packet(self, packet) -> Optional[Dict]:
        """Parse packet and extract relevant information"""
        info = {
            'timestamp': datetime.now().isoformat(),
            'length': len(packet),
            'protocol': 'unknown'
        }
        
        # Ethernet layer
        if packet.haslayer(Ether):
            info['src_mac'] = packet[Ether].src
            info['dst_mac'] = packet[Ether].dst
        
        # ARP
        if packet.haslayer(ARP):
            info['protocol'] = 'ARP'
            info['arp_op'] = 'request' if packet[ARP].op == 1 else 'reply'
            info['arp_src_ip'] = packet[ARP].psrc
            info['arp_dst_ip'] = packet[ARP].pdst
            return info
        
        # IP layer
        if packet.haslayer(IP):
            info['src_ip'] = packet[IP].src
            info['dst_ip'] = packet[IP].dst
            info['ttl'] = packet[IP].ttl
        
        # TCP
        if packet.haslayer(TCP):
            info['protocol'] = 'TCP'
            info['src_port'] = packet[TCP].sport
            info['dst_port'] = packet[TCP].dport
            info['flags'] = str(packet[TCP].flags)
            
            # Identify common services
            port = packet[TCP].dport
            if port == 80 or port == 8080:
                info['service'] = 'HTTP'
            elif port == 443:
                info['service'] = 'HTTPS'
            elif port == 22:
                info['service'] = 'SSH'
            elif port == 21:
                info['service'] = 'FTP'
            elif port == 25:
                info['service'] = 'SMTP'
            elif port == 3389:
                info['service'] = 'RDP'
        
        # UDP
        elif packet.haslayer(UDP):
            info['protocol'] = 'UDP'
            info['src_port'] = packet[UDP].sport
            info['dst_port'] = packet[UDP].dport
            
            port = packet[UDP].dport
            if port == 53:
                info['service'] = 'DNS'
            elif port == 67 or port == 68:
                info['service'] = 'DHCP'
        
        # ICMP
        elif packet.haslayer(ICMP):
            info['protocol'] = 'ICMP'
            info['icmp_type'] = packet[ICMP].type
            info['icmp_code'] = packet[ICMP].code
        
        # DNS
        if packet.haslayer(DNS):
            info['service'] = 'DNS'
            if packet.haslayer(DNSQR):
                info['dns_query'] = packet[DNSQR].qname.decode() if packet[DNSQR].qname else None
        
        # HTTP data (if available)
        if packet.haslayer(Raw) and info.get('service') == 'HTTP':
            try:
                payload = packet[Raw].load.decode('utf-8', errors='ignore')
                if 'HTTP' in payload or 'GET' in payload or 'POST' in payload:
                    # Extract HTTP method and path
                    lines = payload.split('\r\n')
                    if lines:
                        first_line = lines[0]
                        if first_line.startswith(('GET', 'POST', 'PUT', 'DELETE')):
                            parts = first_line.split(' ')
                            if len(parts) >= 2:
                                info['http_method'] = parts[0]
                                info['http_path'] = parts[1]
                        
                        # Extract host header
                        for line in lines:
                            if line.lower().startswith('host:'):
                                info['http_host'] = line.split(':', 1)[1].strip()
                                break
            except Exception:
                pass
        
        return info
    
    def get_packets(self, limit: int = 100, filter_protocol: str = None) -> List[Dict]:
        """Get captured packets"""
        packets = self.packets
        
        if filter_protocol:
            packets = [p for p in packets if p.get('protocol') == filter_protocol]
        
        return packets[-limit:]
    
    def get_stats(self) -> Dict:
        """Get capture statistics"""
        return dict(self.stats)
    
    def get_dns_queries(self) -> List[Dict]:
        """Get all DNS queries"""
        dns_packets = [p for p in self.packets if p.get('dns_query')]
        return dns_packets
    
    def get_http_requests(self) -> List[Dict]:
        """Get all HTTP requests"""
        http_packets = [p for p in self.packets 
                       if p.get('service') == 'HTTP' and p.get('http_path')]
        return http_packets
    
    def get_connections(self) -> List[Dict]:
        """Get unique connections"""
        connections = {}
        
        for packet in self.packets:
            if 'src_ip' in packet and 'dst_ip' in packet:
                key = f"{packet['src_ip']}:{packet.get('src_port', '?')} -> {packet['dst_ip']}:{packet.get('dst_port', '?')}"
                
                if key not in connections:
                    connections[key] = {
                        'src_ip': packet['src_ip'],
                        'dst_ip': packet['dst_ip'],
                        'src_port': packet.get('src_port'),
                        'dst_port': packet.get('dst_port'),
                        'protocol': packet.get('protocol'),
                        'service': packet.get('service'),
                        'packet_count': 0,
                        'bytes': 0
                    }
                
                connections[key]['packet_count'] += 1
                connections[key]['bytes'] += packet.get('length', 0)
        
        return list(connections.values())


class TrafficAnalyzer:
    """
    Analyze network traffic patterns
    """
    
    def __init__(self, sniffer: PacketSniffer = None):
        self.sniffer = sniffer
        self.bandwidth_history = []
        self._monitor_thread = None
        self._is_monitoring = False
    
    def start_bandwidth_monitor(self, interval: int = 1):
        """Start bandwidth monitoring"""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        
        def monitor():
            last_stats = self.sniffer.get_stats().copy() if self.sniffer else {}
            last_time = time.time()
            
            while self._is_monitoring:
                time.sleep(interval)
                
                if self.sniffer:
                    current_stats = self.sniffer.get_stats()
                    current_time = time.time()
                    
                    # Calculate bandwidth
                    delta_time = current_time - last_time
                    packets = current_stats.get('total', 0) - last_stats.get('total', 0)
                    
                    # Rough bandwidth estimate (assumes avg packet size of 500 bytes)
                    bandwidth_bps = (packets * 500 * 8) / delta_time
                    
                    self.bandwidth_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'packets_per_sec': packets / delta_time,
                        'bandwidth_bps': bandwidth_bps,
                        'bandwidth_mbps': bandwidth_bps / 1_000_000
                    })
                    
                    # Limit history size
                    if len(self.bandwidth_history) > 3600:
                        self.bandwidth_history = self.bandwidth_history[-1800:]
                    
                    last_stats = current_stats.copy()
                    last_time = current_time
        
        self._monitor_thread = threading.Thread(target=monitor)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    
    def stop_bandwidth_monitor(self):
        """Stop bandwidth monitoring"""
        self._is_monitoring = False
    
    def get_bandwidth_history(self, minutes: int = 5) -> List[Dict]:
        """Get bandwidth history for last N minutes"""
        # Return last N minutes of data (assuming 1 sample per second)
        samples = minutes * 60
        return self.bandwidth_history[-samples:]
    
    def get_top_talkers(self, limit: int = 10) -> List[Dict]:
        """Get top bandwidth consumers"""
        if not self.sniffer:
            return []
        
        ip_stats = defaultdict(lambda: {'packets': 0, 'bytes': 0})
        
        for packet in self.sniffer.packets:
            src_ip = packet.get('src_ip')
            if src_ip:
                ip_stats[src_ip]['packets'] += 1
                ip_stats[src_ip]['bytes'] += packet.get('length', 0)
        
        # Sort by bytes
        sorted_ips = sorted(
            ip_stats.items(),
            key=lambda x: x[1]['bytes'],
            reverse=True
        )
        
        return [
            {'ip': ip, 'packets': data['packets'], 'bytes': data['bytes']}
            for ip, data in sorted_ips[:limit]
        ]
    
    def get_protocol_distribution(self) -> Dict:
        """Get distribution of protocols"""
        if not self.sniffer:
            return {}
        
        stats = self.sniffer.get_stats()
        total = stats.get('total', 1)
        
        distribution = {}
        for protocol, count in stats.items():
            if protocol != 'total':
                distribution[protocol] = {
                    'count': count,
                    'percentage': round(count / total * 100, 2)
                }
        
        return distribution


if __name__ == "__main__":
    print("Packet Sniffer module loaded")
    print(f"Scapy available: {SCAPY_AVAILABLE}")
    
    if SCAPY_AVAILABLE:
        print("\nAvailable interfaces:")
        for iface in get_if_list():
            print(f"  - {iface}")
