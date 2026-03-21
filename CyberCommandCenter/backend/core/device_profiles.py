"""
Cyber Command Center - Device Profiles
Custom settings and profiles per device
"""
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class DeviceCategory(Enum):
    MOBILE = "mobile"
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    TABLET = "tablet"
    SMART_TV = "smart_tv"
    GAME_CONSOLE = "game_console"
    IOT = "iot"
    UNKNOWN = "unknown"


class AccessLevel(Enum):
    FULL = "full"
    LIMITED = "limited"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


@dataclass
class NetworkSchedule:
    """Network access schedule"""
    enabled: bool = True
    weekday_start: str = "06:00"
    weekday_end: str = "23:00"
    weekend_start: str = "08:00"
    weekend_end: str = "00:00"
    
    def to_dict(self) -> Dict:
        return {
            'enabled': self.enabled,
            'weekdayStart': self.weekday_start,
            'weekdayEnd': self.weekday_end,
            'weekendStart': self.weekend_start,
            'weekendEnd': self.weekend_end
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NetworkSchedule':
        return cls(
            enabled=data.get('enabled', True),
            weekday_start=data.get('weekdayStart', '06:00'),
            weekday_end=data.get('weekdayEnd', '23:00'),
            weekend_start=data.get('weekendStart', '08:00'),
            weekend_end=data.get('weekendEnd', '00:00')
        )


@dataclass
class BandwidthLimit:
    """Bandwidth restrictions"""
    enabled: bool = False
    download_mbps: float = 100.0
    upload_mbps: float = 50.0
    
    def to_dict(self) -> Dict:
        return {
            'enabled': self.enabled,
            'downloadMbps': self.download_mbps,
            'uploadMbps': self.upload_mbps
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BandwidthLimit':
        return cls(
            enabled=data.get('enabled', False),
            download_mbps=data.get('downloadMbps', 100.0),
            upload_mbps=data.get('uploadMbps', 50.0)
        )


@dataclass
class DeviceProfile:
    """Complete device profile with settings"""
    mac: str
    name: str = ""
    icon: str = "device"
    category: DeviceCategory = DeviceCategory.UNKNOWN
    owner: str = ""
    notes: str = ""
    
    # Access control
    access_level: AccessLevel = AccessLevel.FULL
    schedule: NetworkSchedule = field(default_factory=NetworkSchedule)
    bandwidth: BandwidthLimit = field(default_factory=BandwidthLimit)
    
    # Content filtering
    blocked_categories: List[str] = field(default_factory=list)
    blocked_domains: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)  # Whitelist mode
    
    # Parental control
    parental_enabled: bool = False
    safe_search_enforced: bool = False
    max_daily_hours: float = 0  # 0 = unlimited
    
    # Alerts
    alert_on_connect: bool = False
    alert_on_unusual_activity: bool = True
    
    # Metadata
    created_at: datetime = None
    updated_at: datetime = None
    last_seen: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            'mac': self.mac,
            'name': self.name,
            'icon': self.icon,
            'category': self.category.value,
            'owner': self.owner,
            'notes': self.notes,
            'accessLevel': self.access_level.value,
            'schedule': self.schedule.to_dict(),
            'bandwidth': self.bandwidth.to_dict(),
            'blockedCategories': self.blocked_categories,
            'blockedDomains': self.blocked_domains,
            'allowedDomains': self.allowed_domains,
            'parentalEnabled': self.parental_enabled,
            'safeSearchEnforced': self.safe_search_enforced,
            'maxDailyHours': self.max_daily_hours,
            'alertOnConnect': self.alert_on_connect,
            'alertOnUnusualActivity': self.alert_on_unusual_activity,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'lastSeen': self.last_seen.isoformat() if self.last_seen else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DeviceProfile':
        return cls(
            mac=data['mac'],
            name=data.get('name', ''),
            icon=data.get('icon', 'device'),
            category=DeviceCategory(data.get('category', 'unknown')),
            owner=data.get('owner', ''),
            notes=data.get('notes', ''),
            access_level=AccessLevel(data.get('accessLevel', 'full')),
            schedule=NetworkSchedule.from_dict(data.get('schedule', {})),
            bandwidth=BandwidthLimit.from_dict(data.get('bandwidth', {})),
            blocked_categories=data.get('blockedCategories', []),
            blocked_domains=data.get('blockedDomains', []),
            allowed_domains=data.get('allowedDomains', []),
            parental_enabled=data.get('parentalEnabled', False),
            safe_search_enforced=data.get('safeSearchEnforced', False),
            max_daily_hours=data.get('maxDailyHours', 0),
            alert_on_connect=data.get('alertOnConnect', False),
            alert_on_unusual_activity=data.get('alertOnUnusualActivity', True),
            created_at=datetime.fromisoformat(data['createdAt']) if data.get('createdAt') else None,
            updated_at=datetime.fromisoformat(data['updatedAt']) if data.get('updatedAt') else None,
            last_seen=datetime.fromisoformat(data['lastSeen']) if data.get('lastSeen') else None
        )


# Predefined profile templates
PROFILE_TEMPLATES = {
    'child': DeviceProfile(
        mac='template',
        name='Niño',
        category=DeviceCategory.MOBILE,
        access_level=AccessLevel.LIMITED,
        schedule=NetworkSchedule(
            enabled=True,
            weekday_start="07:00",
            weekday_end="21:00",
            weekend_start="09:00",
            weekend_end="22:00"
        ),
        bandwidth=BandwidthLimit(enabled=True, download_mbps=50, upload_mbps=10),
        blocked_categories=['adult', 'gambling', 'violence', 'drugs'],
        parental_enabled=True,
        safe_search_enforced=True,
        max_daily_hours=3
    ),
    'teen': DeviceProfile(
        mac='template',
        name='Adolescente',
        category=DeviceCategory.MOBILE,
        access_level=AccessLevel.LIMITED,
        schedule=NetworkSchedule(
            enabled=True,
            weekday_start="06:00",
            weekday_end="23:00",
            weekend_start="08:00",
            weekend_end="00:00"
        ),
        blocked_categories=['adult', 'gambling'],
        parental_enabled=True,
        safe_search_enforced=True,
        max_daily_hours=5
    ),
    'guest': DeviceProfile(
        mac='template',
        name='Invitado',
        category=DeviceCategory.UNKNOWN,
        access_level=AccessLevel.RESTRICTED,
        bandwidth=BandwidthLimit(enabled=True, download_mbps=20, upload_mbps=5),
        alert_on_connect=True
    ),
    'work': DeviceProfile(
        mac='template',
        name='Trabajo',
        category=DeviceCategory.LAPTOP,
        access_level=AccessLevel.FULL,
        blocked_categories=['social_media', 'gaming', 'streaming'],
        alert_on_unusual_activity=True
    ),
    'iot': DeviceProfile(
        mac='template',
        name='IoT Device',
        category=DeviceCategory.IOT,
        access_level=AccessLevel.RESTRICTED,
        bandwidth=BandwidthLimit(enabled=True, download_mbps=10, upload_mbps=5),
        alert_on_unusual_activity=True
    )
}


class DeviceProfileManager:
    """
    Device profile management
    
    Features:
    - Per-device configuration
    - Profile templates
    - Access scheduling
    - Bandwidth limits
    - Content filtering
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
        
        self.profiles_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'database',
            'device_profiles.json'
        )
        
        self.profiles: Dict[str, DeviceProfile] = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """Load profiles from file"""
        try:
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                
                for mac, profile_data in data.items():
                    try:
                        self.profiles[mac] = DeviceProfile.from_dict(profile_data)
                    except Exception as e:
                        print(f"Error loading profile {mac}: {e}")
        except Exception as e:
            print(f"Error loading profiles: {e}")
    
    def _save_profiles(self):
        """Save profiles to file"""
        try:
            os.makedirs(os.path.dirname(self.profiles_file), exist_ok=True)
            
            data = {}
            for mac, profile in self.profiles.items():
                data[mac] = profile.to_dict()
            
            with open(self.profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving profiles: {e}")
    
    def get_profile(self, mac: str) -> Optional[DeviceProfile]:
        """Get profile by MAC address"""
        mac = mac.upper()
        return self.profiles.get(mac)
    
    def create_profile(self, mac: str, name: str = "", 
                      category: str = "unknown", template: str = None) -> DeviceProfile:
        """Create new device profile"""
        mac = mac.upper()
        
        if template and template in PROFILE_TEMPLATES:
            # Copy from template
            tmpl = PROFILE_TEMPLATES[template]
            profile = DeviceProfile(
                mac=mac,
                name=name or tmpl.name,
                icon=tmpl.icon,
                category=DeviceCategory(category) if category != "unknown" else tmpl.category,
                access_level=tmpl.access_level,
                schedule=NetworkSchedule(
                    enabled=tmpl.schedule.enabled,
                    weekday_start=tmpl.schedule.weekday_start,
                    weekday_end=tmpl.schedule.weekday_end,
                    weekend_start=tmpl.schedule.weekend_start,
                    weekend_end=tmpl.schedule.weekend_end
                ),
                bandwidth=BandwidthLimit(
                    enabled=tmpl.bandwidth.enabled,
                    download_mbps=tmpl.bandwidth.download_mbps,
                    upload_mbps=tmpl.bandwidth.upload_mbps
                ),
                blocked_categories=tmpl.blocked_categories.copy(),
                parental_enabled=tmpl.parental_enabled,
                safe_search_enforced=tmpl.safe_search_enforced,
                max_daily_hours=tmpl.max_daily_hours,
                alert_on_connect=tmpl.alert_on_connect,
                alert_on_unusual_activity=tmpl.alert_on_unusual_activity
            )
        else:
            profile = DeviceProfile(
                mac=mac,
                name=name,
                category=DeviceCategory(category)
            )
        
        self.profiles[mac] = profile
        self._save_profiles()
        
        return profile
    
    def update_profile(self, mac: str, updates: Dict) -> Optional[DeviceProfile]:
        """Update device profile"""
        mac = mac.upper()
        
        profile = self.profiles.get(mac)
        if not profile:
            return None
        
        # Update basic fields
        if 'name' in updates:
            profile.name = updates['name']
        if 'icon' in updates:
            profile.icon = updates['icon']
        if 'category' in updates:
            profile.category = DeviceCategory(updates['category'])
        if 'owner' in updates:
            profile.owner = updates['owner']
        if 'notes' in updates:
            profile.notes = updates['notes']
        
        # Access control
        if 'accessLevel' in updates:
            profile.access_level = AccessLevel(updates['accessLevel'])
        
        # Schedule
        if 'schedule' in updates:
            profile.schedule = NetworkSchedule.from_dict(updates['schedule'])
        
        # Bandwidth
        if 'bandwidth' in updates:
            profile.bandwidth = BandwidthLimit.from_dict(updates['bandwidth'])
        
        # Content filtering
        if 'blockedCategories' in updates:
            profile.blocked_categories = updates['blockedCategories']
        if 'blockedDomains' in updates:
            profile.blocked_domains = updates['blockedDomains']
        if 'allowedDomains' in updates:
            profile.allowed_domains = updates['allowedDomains']
        
        # Parental
        if 'parentalEnabled' in updates:
            profile.parental_enabled = updates['parentalEnabled']
        if 'safeSearchEnforced' in updates:
            profile.safe_search_enforced = updates['safeSearchEnforced']
        if 'maxDailyHours' in updates:
            profile.max_daily_hours = updates['maxDailyHours']
        
        # Alerts
        if 'alertOnConnect' in updates:
            profile.alert_on_connect = updates['alertOnConnect']
        if 'alertOnUnusualActivity' in updates:
            profile.alert_on_unusual_activity = updates['alertOnUnusualActivity']
        
        profile.updated_at = datetime.now()
        self._save_profiles()
        
        return profile
    
    def delete_profile(self, mac: str) -> bool:
        """Delete device profile"""
        mac = mac.upper()
        
        if mac in self.profiles:
            del self.profiles[mac]
            self._save_profiles()
            return True
        return False
    
    def get_all_profiles(self) -> List[Dict]:
        """Get all profiles"""
        return [p.to_dict() for p in self.profiles.values()]
    
    def get_templates(self) -> List[Dict]:
        """Get available profile templates"""
        templates = []
        for name, profile in PROFILE_TEMPLATES.items():
            templates.append({
                'id': name,
                'name': profile.name,
                'description': f"Template para {profile.name}",
                'accessLevel': profile.access_level.value,
                'blockedCategories': profile.blocked_categories,
                'maxDailyHours': profile.max_daily_hours
            })
        return templates
    
    def update_last_seen(self, mac: str):
        """Update last seen timestamp"""
        mac = mac.upper()
        
        profile = self.profiles.get(mac)
        if profile:
            profile.last_seen = datetime.now()
            # Don't save on every last_seen update to reduce IO
    
    def check_access_allowed(self, mac: str) -> Dict:
        """Check if device is currently allowed to access network"""
        mac = mac.upper()
        
        profile = self.profiles.get(mac)
        if not profile:
            return {'allowed': True, 'reason': 'No profile configured'}
        
        # Check access level
        if profile.access_level == AccessLevel.BLOCKED:
            return {'allowed': False, 'reason': 'Device is blocked'}
        
        # Check schedule
        if profile.schedule.enabled:
            now = datetime.now()
            is_weekend = now.weekday() >= 5
            current_time = now.strftime("%H:%M")
            
            if is_weekend:
                start = profile.schedule.weekend_start
                end = profile.schedule.weekend_end
            else:
                start = profile.schedule.weekday_start
                end = profile.schedule.weekday_end
            
            # Handle overnight windows (end < start means crosses midnight)
            if end < start:
                # e.g., 22:00 - 08:00
                if not (current_time >= start or current_time < end):
                    return {
                        'allowed': False, 
                        'reason': f'Fuera del horario permitido ({start} - {end})'
                    }
            else:
                if not (start <= current_time < end):
                    return {
                        'allowed': False,
                        'reason': f'Fuera del horario permitido ({start} - {end})'
                    }
        
        return {'allowed': True, 'reason': 'Access permitted'}
    
    def get_devices_by_category(self, category: str) -> List[Dict]:
        """Get all devices of a specific category"""
        try:
            cat = DeviceCategory(category)
            return [p.to_dict() for p in self.profiles.values() if p.category == cat]
        except:
            return []
    
    def get_devices_by_owner(self, owner: str) -> List[Dict]:
        """Get all devices owned by a person"""
        return [p.to_dict() for p in self.profiles.values() 
                if p.owner.lower() == owner.lower()]


# Global instance
profile_manager = DeviceProfileManager()
