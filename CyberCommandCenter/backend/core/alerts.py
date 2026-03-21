"""
Cyber Command Center - Real-time Alert System
Push notifications, sound alerts, and notification center
"""
import threading
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from collections import deque
from dataclasses import dataclass, asdict
from enum import Enum


class AlertType(Enum):
    NEW_DEVICE = "new_device"
    DEVICE_DISCONNECTED = "device_disconnected"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    PRANK_STARTED = "prank_started"
    PRANK_COMPLETED = "prank_completed"
    PRANK_FAILED = "prank_failed"
    TRAFFIC_SPIKE = "traffic_spike"
    BLOCKED_ATTEMPT = "blocked_attempt"
    SECURITY_WARNING = "security_warning"
    SYSTEM_INFO = "system_info"


class AlertSeverity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Alert:
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    message: str
    timestamp: datetime
    data: Dict = None
    read: bool = False
    sound: bool = True
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type.value,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'timestamp': self.timestamp.isoformat(),
            'data': self.data or {},
            'read': self.read,
            'sound': self.sound
        }


class AlertManager:
    """
    Centralized alert management system with real-time notifications
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
        self.alerts: deque = deque(maxlen=1000)  # Keep last 1000 alerts
        self.subscribers: List[Callable] = []
        self.settings = {
            'sound_enabled': True,
            'push_enabled': True,
            'email_enabled': False,
            'telegram_enabled': False,
            'min_severity': AlertSeverity.INFO.value,
            'quiet_hours': {'enabled': False, 'start': '22:00', 'end': '08:00'}
        }
        self._alert_counter = 0
        self._lock = threading.Lock()
    
    def _generate_id(self) -> str:
        """Generate unique alert ID"""
        with self._lock:
            self._alert_counter += 1
            return f"alert_{int(time.time())}_{self._alert_counter}"
    
    def _is_quiet_hours(self) -> bool:
        """Check if currently in quiet hours"""
        if not self.settings['quiet_hours']['enabled']:
            return False
        
        now = datetime.now().time()
        start = datetime.strptime(self.settings['quiet_hours']['start'], '%H:%M').time()
        end = datetime.strptime(self.settings['quiet_hours']['end'], '%H:%M').time()
        
        if start <= end:
            return start <= now <= end
        else:  # Overnight quiet hours (e.g., 22:00 to 08:00)
            return now >= start or now <= end
    
    def create_alert(
        self,
        alert_type: AlertType,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.INFO,
        data: Dict = None,
        sound: bool = True
    ) -> Alert:
        """Create and dispatch a new alert"""
        
        # Check minimum severity
        severity_order = [s.value for s in AlertSeverity]
        if severity_order.index(severity.value) < severity_order.index(self.settings['min_severity']):
            return None
        
        # Check quiet hours (only suppress sound, not the alert)
        if self._is_quiet_hours():
            sound = False
        
        alert = Alert(
            id=self._generate_id(),
            type=alert_type,
            severity=severity,
            title=title,
            message=message,
            timestamp=datetime.now(),
            data=data,
            sound=sound and self.settings['sound_enabled']
        )
        
        # Store alert
        self.alerts.appendleft(alert)
        
        # Notify subscribers (WebSocket, Telegram, etc.)
        self._notify_subscribers(alert)
        
        return alert
    
    def _notify_subscribers(self, alert: Alert):
        """Notify all registered subscribers"""
        for subscriber in self.subscribers:
            try:
                subscriber(alert)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")
    
    def subscribe(self, callback: Callable):
        """Subscribe to alert notifications"""
        if callback not in self.subscribers:
            self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from alerts"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def get_alerts(
        self,
        limit: int = 50,
        unread_only: bool = False,
        alert_type: AlertType = None,
        severity: AlertSeverity = None,
        since: datetime = None
    ) -> List[Dict]:
        """Get alerts with filtering"""
        results = []
        
        for alert in self.alerts:
            if len(results) >= limit:
                break
            
            if unread_only and alert.read:
                continue
            
            if alert_type and alert.type != alert_type:
                continue
            
            if severity and alert.severity != severity:
                continue
            
            if since and alert.timestamp < since:
                continue
            
            results.append(alert.to_dict())
        
        return results
    
    def mark_read(self, alert_id: str) -> bool:
        """Mark an alert as read"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.read = True
                return True
        return False
    
    def mark_all_read(self) -> int:
        """Mark all alerts as read"""
        count = 0
        for alert in self.alerts:
            if not alert.read:
                alert.read = True
                count += 1
        return count
    
    def get_unread_count(self) -> int:
        """Get count of unread alerts"""
        return sum(1 for a in self.alerts if not a.read)
    
    def clear_old_alerts(self, days: int = 7):
        """Clear alerts older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)
        self.alerts = deque(
            (a for a in self.alerts if a.timestamp >= cutoff),
            maxlen=1000
        )
    
    def update_settings(self, settings: Dict):
        """Update alert settings"""
        self.settings.update(settings)
    
    def get_settings(self) -> Dict:
        """Get current settings"""
        return self.settings.copy()
    
    # Convenience methods for common alerts
    def alert_new_device(self, device_info: Dict):
        """Alert for new device detected"""
        return self.create_alert(
            AlertType.NEW_DEVICE,
            "🆕 Nuevo dispositivo detectado",
            f"Dispositivo {device_info.get('hostname', device_info.get('mac', 'Desconocido'))} se conectó a la red",
            AlertSeverity.MEDIUM,
            data=device_info
        )
    
    def alert_device_disconnected(self, device_info: Dict):
        """Alert for device disconnection"""
        return self.create_alert(
            AlertType.DEVICE_DISCONNECTED,
            "📴 Dispositivo desconectado",
            f"Dispositivo {device_info.get('hostname', device_info.get('mac', 'Desconocido'))} se desconectó",
            AlertSeverity.LOW,
            data=device_info,
            sound=False
        )
    
    def alert_prank_completed(self, prank_info: Dict):
        """Alert for completed prank"""
        return self.create_alert(
            AlertType.PRANK_COMPLETED,
            "✅ Prank completado",
            f"Prank '{prank_info.get('name', 'Unknown')}' ejecutado exitosamente",
            AlertSeverity.INFO,
            data=prank_info
        )
    
    def alert_suspicious_activity(self, details: Dict):
        """Alert for suspicious network activity"""
        return self.create_alert(
            AlertType.SUSPICIOUS_ACTIVITY,
            "⚠️ Actividad sospechosa",
            details.get('description', 'Se detectó actividad sospechosa en la red'),
            AlertSeverity.HIGH,
            data=details
        )
    
    def alert_traffic_spike(self, device: str, bandwidth: float):
        """Alert for unusual traffic spike"""
        return self.create_alert(
            AlertType.TRAFFIC_SPIKE,
            "📈 Pico de tráfico",
            f"Dispositivo {device} tiene uso anormal de bandwidth: {bandwidth:.1f} MB/s",
            AlertSeverity.MEDIUM,
            data={'device': device, 'bandwidth': bandwidth}
        )


# Global instance
alert_manager = AlertManager()


# Convenience functions
def new_alert(alert_type: AlertType, title: str, message: str, 
              severity: AlertSeverity = AlertSeverity.INFO, data: Dict = None):
    """Quick function to create an alert"""
    return alert_manager.create_alert(alert_type, title, message, severity, data)

def get_alerts(limit: int = 50, unread_only: bool = False):
    """Quick function to get alerts"""
    return alert_manager.get_alerts(limit, unread_only)
