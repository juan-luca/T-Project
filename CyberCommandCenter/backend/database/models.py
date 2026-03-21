"""
Cyber Command Center - Database Models
"""
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "database" / "cyber_command.db"

# Ensure database directory exists
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Device(Base):
    """Discovered network devices"""
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True)
    mac_address = Column(String(17), unique=True, nullable=False)
    ip_address = Column(String(15))
    hostname = Column(String(255))
    vendor = Column(String(255))
    device_type = Column(String(50))  # computer, mobile, iot, etc.
    os_info = Column(String(255))
    custom_name = Column(String(255))
    category = Column(String(50))  # family, guest, unknown
    is_trusted = Column(Boolean, default=False)
    is_blocked = Column(Boolean, default=False)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_online = Column(Boolean, default=True)
    notes = Column(Text)
    
    # Relationships
    connections = relationship("ConnectionLog", back_populates="device")
    port_scans = relationship("PortScan", back_populates="device")
    
    def to_dict(self):
        return {
            'id': self.id,
            'mac_address': self.mac_address,
            'ip_address': self.ip_address,
            'hostname': self.hostname,
            'vendor': self.vendor,
            'device_type': self.device_type,
            'os_info': self.os_info,
            'custom_name': self.custom_name or self.hostname or f"Device-{self.mac_address[-5:]}",
            'category': self.category,
            'is_trusted': self.is_trusted,
            'is_blocked': self.is_blocked,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'is_online': self.is_online,
            'notes': self.notes
        }


class ConnectionLog(Base):
    """Device connection history"""
    __tablename__ = 'connection_logs'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    event_type = Column(String(20))  # connected, disconnected
    ip_address = Column(String(15))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    device = relationship("Device", back_populates="connections")
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'event_type': self.event_type,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class PortScan(Base):
    """Port scan results"""
    __tablename__ = 'port_scans'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    port = Column(Integer)
    protocol = Column(String(10))
    state = Column(String(20))
    service = Column(String(100))
    version = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    device = relationship("Device", back_populates="port_scans")
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'port': self.port,
            'protocol': self.protocol,
            'state': self.state,
            'service': self.service,
            'version': self.version,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class Alert(Base):
    """Security alerts"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    alert_type = Column(String(50))  # new_device, intrusion, port_scan, etc.
    severity = Column(String(20))  # low, medium, high, critical
    title = Column(String(255))
    description = Column(Text)
    device_mac = Column(String(17))
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'device_mac': self.device_mac,
            'is_read': self.is_read,
            'is_resolved': self.is_resolved,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'data': self.data
        }


class WiFiNetwork(Base):
    """Discovered WiFi networks"""
    __tablename__ = 'wifi_networks'
    
    id = Column(Integer, primary_key=True)
    bssid = Column(String(17), unique=True)
    ssid = Column(String(255))
    channel = Column(Integer)
    frequency = Column(Integer)
    signal_strength = Column(Integer)
    encryption = Column(String(50))
    cipher = Column(String(50))
    authentication = Column(String(50))
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    handshake_captured = Column(Boolean, default=False)
    handshake_path = Column(String(500))
    is_cracked = Column(Boolean, default=False)
    password = Column(String(255))
    notes = Column(Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'bssid': self.bssid,
            'ssid': self.ssid,
            'channel': self.channel,
            'frequency': self.frequency,
            'signal_strength': self.signal_strength,
            'encryption': self.encryption,
            'cipher': self.cipher,
            'authentication': self.authentication,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'handshake_captured': self.handshake_captured,
            'is_cracked': self.is_cracked,
            'password': self.password if self.is_cracked else None,
            'notes': self.notes
        }


class PrankLog(Base):
    """Prank activity log"""
    __tablename__ = 'prank_logs'
    
    id = Column(Integer, primary_key=True)
    prank_type = Column(String(50))  # throttle, redirect, deauth, etc.
    target_mac = Column(String(17))
    target_ip = Column(String(15))
    status = Column(String(20))  # active, stopped, completed
    parameters = Column(JSON)
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prank_type': self.prank_type,
            'target_mac': self.target_mac,
            'target_ip': self.target_ip,
            'status': self.status,
            'parameters': self.parameters,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'stopped_at': self.stopped_at.isoformat() if self.stopped_at else None
        }


class NetworkStats(Base):
    """Network statistics snapshots"""
    __tablename__ = 'network_stats'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_devices = Column(Integer)
    online_devices = Column(Integer)
    bytes_sent = Column(Float)
    bytes_recv = Column(Float)
    packets_sent = Column(Integer)
    packets_recv = Column(Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'total_devices': self.total_devices,
            'online_devices': self.online_devices,
            'bytes_sent': self.bytes_sent,
            'bytes_recv': self.bytes_recv,
            'packets_sent': self.packets_sent,
            'packets_recv': self.packets_recv
        }


class Settings(Base):
    """Application settings"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


def init_db():
    """Initialize the database"""
    Base.metadata.create_all(engine)
    
    # Add default settings
    session = Session()
    try:
        default_settings = [
            ('scan_interval', '30', 'Network scan interval in seconds'),
            ('auto_scan', 'true', 'Enable automatic network scanning'),
            ('alert_new_device', 'true', 'Alert on new device detection'),
            ('alert_sound', 'true', 'Play sound on alerts'),
            ('theme', 'dark', 'UI theme (dark/light)'),
        ]
        
        for key, value, description in default_settings:
            if not session.query(Settings).filter_by(key=key).first():
                setting = Settings(key=key, value=value, description=description)
                session.add(setting)
        
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error initializing settings: {e}")
    finally:
        session.close()


def get_session():
    """Get a new database session"""
    return Session()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
