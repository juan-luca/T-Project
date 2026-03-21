"""
Cyber Command Center - Network Traffic Monitor
Real-time bandwidth monitoring and traffic analysis
"""
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque
from dataclasses import dataclass, field
import psutil


@dataclass
class TrafficSnapshot:
    """Snapshot of network traffic at a point in time"""
    timestamp: datetime
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'bytes_sent': self.bytes_sent,
            'bytes_recv': self.bytes_recv,
            'packets_sent': self.packets_sent,
            'packets_recv': self.packets_recv,
            'mbps_sent': round(self.bytes_sent / 1024 / 1024, 2),
            'mbps_recv': round(self.bytes_recv / 1024 / 1024, 2)
        }


@dataclass
class DeviceTraffic:
    """Traffic data for a specific device"""
    ip: str
    mac: str = ""
    name: str = ""
    bytes_sent: int = 0
    bytes_recv: int = 0
    connections: int = 0
    last_activity: datetime = None
    
    def to_dict(self):
        return {
            'ip': self.ip,
            'mac': self.mac,
            'name': self.name,
            'bytes_sent': self.bytes_sent,
            'bytes_recv': self.bytes_recv,
            'mb_sent': round(self.bytes_sent / 1024 / 1024, 2),
            'mb_recv': round(self.bytes_recv / 1024 / 1024, 2),
            'connections': self.connections,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }


class TrafficMonitor:
    """
    Real-time network traffic monitoring
    
    Features:
    - Total bandwidth monitoring
    - Per-device traffic tracking
    - Historical data (last 24 hours)
    - Traffic spike detection
    - Connection tracking
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        
        # Traffic history (per second snapshots, keep last hour)
        self.history_second: deque = deque(maxlen=3600)
        # Per minute (keep last 24 hours)
        self.history_minute: deque = deque(maxlen=1440)
        # Per hour (keep last 7 days)
        self.history_hour: deque = deque(maxlen=168)
        
        # Device traffic
        self.device_traffic: Dict[str, DeviceTraffic] = {}
        
        # Current rates
        self.current_rate = {
            'download_bps': 0,
            'upload_bps': 0,
            'download_mbps': 0,
            'upload_mbps': 0
        }
        
        # Previous counters for rate calculation
        self._prev_counters = None
        self._prev_time = None
        
        # Spike detection
        self.spike_threshold_mbps = 50  # Alert if > 50 Mbps
        self.spike_callback = None
        
        # Running state
        self._running = False
        self._monitor_thread = None
        self._lock = threading.Lock()
        
        # Start monitoring
        self.start()
    
    def start(self):
        """Start traffic monitoring"""
        if self._running:
            return
        
        self._running = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
    
    def stop(self):
        """Stop traffic monitoring"""
        self._running = False
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        last_minute = datetime.now().minute
        last_hour = datetime.now().hour
        
        while self._running:
            try:
                # Get current counters
                counters = psutil.net_io_counters()
                now = datetime.now()
                
                # Calculate rates
                if self._prev_counters and self._prev_time:
                    elapsed = (now - self._prev_time).total_seconds()
                    if elapsed > 0:
                        download_bps = (counters.bytes_recv - self._prev_counters.bytes_recv) / elapsed
                        upload_bps = (counters.bytes_sent - self._prev_counters.bytes_sent) / elapsed
                        
                        with self._lock:
                            self.current_rate = {
                                'download_bps': int(download_bps),
                                'upload_bps': int(upload_bps),
                                'download_mbps': round(download_bps / 1024 / 1024, 2),
                                'upload_mbps': round(upload_bps / 1024 / 1024, 2)
                            }
                        
                        # Store snapshot
                        snapshot = TrafficSnapshot(
                            timestamp=now,
                            bytes_sent=int(upload_bps),
                            bytes_recv=int(download_bps),
                            packets_sent=counters.packets_sent - self._prev_counters.packets_sent,
                            packets_recv=counters.packets_recv - self._prev_counters.packets_recv
                        )
                        
                        with self._lock:
                            self.history_second.append(snapshot)
                        
                        # Check for spikes
                        total_mbps = (download_bps + upload_bps) / 1024 / 1024
                        if total_mbps > self.spike_threshold_mbps:
                            self._alert_spike(total_mbps)
                
                self._prev_counters = counters
                self._prev_time = now
                
                # Aggregate to minute data
                if now.minute != last_minute:
                    self._aggregate_minute()
                    last_minute = now.minute
                
                # Aggregate to hour data
                if now.hour != last_hour:
                    self._aggregate_hour()
                    last_hour = now.hour
                
                # Update device traffic
                self._update_device_traffic()
                
            except Exception as e:
                print(f"Traffic monitor error: {e}")
            
            time.sleep(1)
    
    def _aggregate_minute(self):
        """Aggregate second data to minute"""
        if not self.history_second:
            return
        
        # Get last 60 seconds of data
        recent = list(self.history_second)[-60:]
        if not recent:
            return
        
        avg_sent = sum(s.bytes_sent for s in recent) / len(recent)
        avg_recv = sum(s.bytes_recv for s in recent) / len(recent)
        
        snapshot = TrafficSnapshot(
            timestamp=datetime.now(),
            bytes_sent=int(avg_sent),
            bytes_recv=int(avg_recv),
            packets_sent=sum(s.packets_sent for s in recent),
            packets_recv=sum(s.packets_recv for s in recent)
        )
        
        with self._lock:
            self.history_minute.append(snapshot)
    
    def _aggregate_hour(self):
        """Aggregate minute data to hour"""
        if not self.history_minute:
            return
        
        recent = list(self.history_minute)[-60:]
        if not recent:
            return
        
        avg_sent = sum(s.bytes_sent for s in recent) / len(recent)
        avg_recv = sum(s.bytes_recv for s in recent) / len(recent)
        
        snapshot = TrafficSnapshot(
            timestamp=datetime.now(),
            bytes_sent=int(avg_sent),
            bytes_recv=int(avg_recv),
            packets_sent=sum(s.packets_sent for s in recent),
            packets_recv=sum(s.packets_recv for s in recent)
        )
        
        with self._lock:
            self.history_hour.append(snapshot)
    
    def _update_device_traffic(self):
        """Update per-device traffic data"""
        try:
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                if conn.raddr:
                    ip = conn.raddr.ip
                    
                    # Skip local and broadcast
                    if ip.startswith('127.') or ip.startswith('0.') or ip == '255.255.255.255':
                        continue
                    
                    with self._lock:
                        if ip not in self.device_traffic:
                            self.device_traffic[ip] = DeviceTraffic(ip=ip)
                        
                        self.device_traffic[ip].connections += 1
                        self.device_traffic[ip].last_activity = datetime.now()
        except:
            pass
    
    def _alert_spike(self, mbps: float):
        """Alert on traffic spike"""
        if self.spike_callback:
            try:
                self.spike_callback(mbps)
            except:
                pass
        
        # Also create alert
        try:
            from core.alerts import alert_manager, AlertType, AlertSeverity
            alert_manager.create_alert(
                AlertType.TRAFFIC_SPIKE,
                "📈 Pico de tráfico detectado",
                f"Tráfico anormalmente alto: {mbps:.1f} Mbps",
                AlertSeverity.MEDIUM,
                data={'mbps': mbps}
            )
        except:
            pass
    
    def get_current_rate(self) -> Dict:
        """Get current bandwidth rate"""
        with self._lock:
            return self.current_rate.copy()
    
    def get_history(self, period: str = 'hour', limit: int = 60) -> List[Dict]:
        """
        Get historical traffic data
        
        Args:
            period: 'second', 'minute', or 'hour'
            limit: Maximum number of records
        """
        with self._lock:
            if period == 'second':
                data = list(self.history_second)
            elif period == 'minute':
                data = list(self.history_minute)
            else:
                data = list(self.history_hour)
        
        return [s.to_dict() for s in data[-limit:]]
    
    def get_device_traffic(self, top_n: int = 10) -> List[Dict]:
        """Get top devices by traffic"""
        with self._lock:
            devices = list(self.device_traffic.values())
        
        # Sort by total traffic
        devices.sort(key=lambda d: d.bytes_sent + d.bytes_recv, reverse=True)
        
        return [d.to_dict() for d in devices[:top_n]]
    
    def get_stats(self) -> Dict:
        """Get traffic statistics"""
        counters = psutil.net_io_counters()
        
        with self._lock:
            # Calculate averages from history
            recent_minute = list(self.history_second)[-60:] if self.history_second else []
            recent_hour = list(self.history_minute)[-60:] if self.history_minute else []
        
        avg_minute_down = sum(s.bytes_recv for s in recent_minute) / len(recent_minute) if recent_minute else 0
        avg_minute_up = sum(s.bytes_sent for s in recent_minute) / len(recent_minute) if recent_minute else 0
        avg_hour_down = sum(s.bytes_recv for s in recent_hour) / len(recent_hour) if recent_hour else 0
        avg_hour_up = sum(s.bytes_sent for s in recent_hour) / len(recent_hour) if recent_hour else 0
        
        return {
            'current': self.current_rate.copy(),
            'totals': {
                'bytes_sent': counters.bytes_sent,
                'bytes_recv': counters.bytes_recv,
                'gb_sent': round(counters.bytes_sent / (1024**3), 2),
                'gb_recv': round(counters.bytes_recv / (1024**3), 2),
                'packets_sent': counters.packets_sent,
                'packets_recv': counters.packets_recv,
                'errors_in': counters.errin,
                'errors_out': counters.errout,
                'drops_in': counters.dropin,
                'drops_out': counters.dropout
            },
            'averages': {
                'last_minute': {
                    'download_mbps': round(avg_minute_down / 1024 / 1024, 2),
                    'upload_mbps': round(avg_minute_up / 1024 / 1024, 2)
                },
                'last_hour': {
                    'download_mbps': round(avg_hour_down / 1024 / 1024, 2),
                    'upload_mbps': round(avg_hour_up / 1024 / 1024, 2)
                }
            },
            'devices_tracked': len(self.device_traffic),
            'spike_threshold_mbps': self.spike_threshold_mbps
        }
    
    def set_spike_threshold(self, mbps: float):
        """Set spike detection threshold"""
        self.spike_threshold_mbps = mbps
    
    def reset_device_traffic(self):
        """Reset device traffic counters"""
        with self._lock:
            self.device_traffic.clear()
    
    def get_interface_stats(self) -> List[Dict]:
        """Get per-interface statistics"""
        stats = []
        
        try:
            io_counters = psutil.net_io_counters(pernic=True)
            addrs = psutil.net_if_addrs()
            
            for iface, counters in io_counters.items():
                # Get IP address for this interface
                ip = None
                mac = None
                if iface in addrs:
                    for addr in addrs[iface]:
                        if addr.family.name == 'AF_INET':
                            ip = addr.address
                        elif addr.family.name == 'AF_PACKET' or addr.family.value == -1:
                            mac = addr.address
                
                stats.append({
                    'interface': iface,
                    'ip': ip,
                    'mac': mac,
                    'bytes_sent': counters.bytes_sent,
                    'bytes_recv': counters.bytes_recv,
                    'mb_sent': round(counters.bytes_sent / (1024**2), 2),
                    'mb_recv': round(counters.bytes_recv / (1024**2), 2),
                    'packets_sent': counters.packets_sent,
                    'packets_recv': counters.packets_recv,
                    'errors_in': counters.errin,
                    'errors_out': counters.errout
                })
        except Exception as e:
            print(f"Error getting interface stats: {e}")
        
        return stats


# Global instance
traffic_monitor = TrafficMonitor()
