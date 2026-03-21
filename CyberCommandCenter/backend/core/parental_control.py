"""
Cyber Command Center - Parental Control System
Time limits, content filters, bedtime mode, usage reports
"""
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


class ContentCategory(Enum):
    SOCIAL_MEDIA = "social_media"
    GAMING = "gaming"
    VIDEO_STREAMING = "video_streaming"
    ADULT_CONTENT = "adult_content"
    GAMBLING = "gambling"
    SHOPPING = "shopping"
    NEWS = "news"
    EDUCATION = "education"


# Domain lists for each category
CATEGORY_DOMAINS = {
    ContentCategory.SOCIAL_MEDIA: [
        "facebook.com", "instagram.com", "twitter.com", "x.com", "tiktok.com",
        "snapchat.com", "reddit.com", "linkedin.com", "pinterest.com", "tumblr.com"
    ],
    ContentCategory.GAMING: [
        "twitch.tv", "steampowered.com", "epicgames.com", "roblox.com",
        "minecraft.net", "ea.com", "playstation.com", "xbox.com", "nintendo.com",
        "itch.io", "gog.com", "origin.com", "ubisoft.com"
    ],
    ContentCategory.VIDEO_STREAMING: [
        "youtube.com", "netflix.com", "hulu.com", "disneyplus.com", "hbomax.com",
        "primevideo.com", "twitch.tv", "vimeo.com", "dailymotion.com", "crunchyroll.com"
    ],
    ContentCategory.ADULT_CONTENT: [
        # Placeholder - would include adult site domains
    ],
    ContentCategory.GAMBLING: [
        "bet365.com", "pokerstars.com", "draftkings.com", "fanduel.com"
    ],
    ContentCategory.SHOPPING: [
        "amazon.com", "ebay.com", "aliexpress.com", "wish.com", "mercadolibre.com"
    ]
}


@dataclass
class DeviceProfile:
    """Profile for a device with parental controls"""
    device_ip: str
    device_name: str
    device_mac: str
    
    # Time limits (minutes per day)
    daily_limit_minutes: int = 0  # 0 = unlimited
    time_used_today: int = 0
    
    # Blocked categories
    blocked_categories: List[str] = field(default_factory=list)
    
    # Custom blocked sites
    custom_blocked_sites: List[str] = field(default_factory=list)
    
    # Bedtime mode
    bedtime_enabled: bool = False
    bedtime_start: str = "22:00"  # HH:MM
    bedtime_end: str = "07:00"
    
    # Internet access schedule
    allowed_days: List[str] = field(default_factory=lambda: [
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
    ])
    allowed_hours_start: str = "00:00"
    allowed_hours_end: str = "23:59"
    
    # Status
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def to_dict(self):
        return {
            'device_ip': self.device_ip,
            'device_name': self.device_name,
            'device_mac': self.device_mac,
            'daily_limit_minutes': self.daily_limit_minutes,
            'time_used_today': self.time_used_today,
            'blocked_categories': self.blocked_categories,
            'custom_blocked_sites': self.custom_blocked_sites,
            'bedtime_enabled': self.bedtime_enabled,
            'bedtime_start': self.bedtime_start,
            'bedtime_end': self.bedtime_end,
            'allowed_days': self.allowed_days,
            'allowed_hours_start': self.allowed_hours_start,
            'allowed_hours_end': self.allowed_hours_end,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class UsageRecord:
    """Daily usage record for a device"""
    device_mac: str
    date: str  # YYYY-MM-DD
    minutes_used: int = 0
    sites_visited: Dict[str, int] = field(default_factory=dict)
    blocked_attempts: int = 0
    categories_accessed: Dict[str, int] = field(default_factory=dict)


class ParentalControl:
    """
    Parental Control System for managing device access and content filtering
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
        self.profiles: Dict[str, DeviceProfile] = {}  # keyed by MAC
        self.usage_records: Dict[str, UsageRecord] = {}  # keyed by MAC_DATE
        self._data_file = Path(__file__).parent.parent / "database" / "parental_control.json"
        self._usage_file = Path(__file__).parent.parent / "database" / "usage_records.json"
        self._lock = threading.Lock()
        self._blocker_callback = None  # Function to block sites
        
        self._load_data()
        self._start_tracker()
    
    def _load_data(self):
        """Load profiles and usage from files"""
        try:
            if self._data_file.exists():
                with open(self._data_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        item['created_at'] = datetime.fromisoformat(item['created_at']) if item.get('created_at') else datetime.now()
                        item['updated_at'] = datetime.fromisoformat(item['updated_at']) if item.get('updated_at') else None
                        profile = DeviceProfile(**item)
                        self.profiles[profile.device_mac] = profile
        except Exception as e:
            print(f"Error loading parental control data: {e}")
        
        try:
            if self._usage_file.exists():
                with open(self._usage_file, 'r') as f:
                    data = json.load(f)
                    for key, item in data.items():
                        self.usage_records[key] = UsageRecord(**item)
        except Exception as e:
            print(f"Error loading usage records: {e}")
    
    def _save_data(self):
        """Save profiles to file"""
        try:
            self._data_file.parent.mkdir(parents=True, exist_ok=True)
            data = [p.to_dict() for p in self.profiles.values()]
            with open(self._data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving parental control data: {e}")
    
    def _save_usage(self):
        """Save usage records to file"""
        try:
            self._usage_file.parent.mkdir(parents=True, exist_ok=True)
            data = {k: v.__dict__ for k, v in self.usage_records.items()}
            with open(self._usage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving usage records: {e}")
    
    def set_blocker_callback(self, callback):
        """Set the callback function to block/unblock sites"""
        self._blocker_callback = callback
    
    def create_profile(
        self,
        device_ip: str,
        device_name: str,
        device_mac: str,
        daily_limit_minutes: int = 0,
        blocked_categories: List[str] = None,
        bedtime_enabled: bool = False,
        bedtime_start: str = "22:00",
        bedtime_end: str = "07:00"
    ) -> DeviceProfile:
        """Create or update a device profile"""
        
        with self._lock:
            profile = DeviceProfile(
                device_ip=device_ip,
                device_name=device_name,
                device_mac=device_mac,
                daily_limit_minutes=daily_limit_minutes,
                blocked_categories=blocked_categories or [],
                bedtime_enabled=bedtime_enabled,
                bedtime_start=bedtime_start,
                bedtime_end=bedtime_end,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.profiles[device_mac] = profile
            self._save_data()
            
            # Apply blocks immediately
            self._apply_profile_blocks(profile)
            
            return profile
    
    def update_profile(self, device_mac: str, updates: Dict) -> Optional[DeviceProfile]:
        """Update a device profile"""
        if device_mac not in self.profiles:
            return None
        
        with self._lock:
            profile = self.profiles[device_mac]
            
            for key, value in updates.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            profile.updated_at = datetime.now()
            self._save_data()
            
            # Re-apply blocks
            self._apply_profile_blocks(profile)
            
            return profile
    
    def delete_profile(self, device_mac: str) -> bool:
        """Delete a device profile"""
        if device_mac not in self.profiles:
            return False
        
        with self._lock:
            # Unblock everything for this device
            profile = self.profiles[device_mac]
            self._remove_profile_blocks(profile)
            
            del self.profiles[device_mac]
            self._save_data()
            return True
    
    def get_profile(self, device_mac: str) -> Optional[Dict]:
        """Get a device profile"""
        if device_mac in self.profiles:
            return self.profiles[device_mac].to_dict()
        return None
    
    def get_all_profiles(self) -> List[Dict]:
        """Get all device profiles"""
        return [p.to_dict() for p in self.profiles.values()]
    
    def _apply_profile_blocks(self, profile: DeviceProfile):
        """Apply content blocks for a profile"""
        if not self._blocker_callback or not profile.is_active:
            return
        
        # Collect all domains to block
        domains_to_block = set(profile.custom_blocked_sites)
        
        for category_name in profile.blocked_categories:
            try:
                category = ContentCategory(category_name)
                domains_to_block.update(CATEGORY_DOMAINS.get(category, []))
            except ValueError:
                pass
        
        if domains_to_block:
            try:
                self._blocker_callback(profile.device_ip, list(domains_to_block))
            except Exception as e:
                print(f"Error applying blocks for {profile.device_name}: {e}")
    
    def _remove_profile_blocks(self, profile: DeviceProfile):
        """Remove all blocks for a profile"""
        # This would call an unblock function
        pass
    
    def _is_bedtime(self, profile: DeviceProfile) -> bool:
        """Check if it's currently bedtime for a profile"""
        if not profile.bedtime_enabled:
            return False
        
        now = datetime.now().time()
        start = datetime.strptime(profile.bedtime_start, '%H:%M').time()
        end = datetime.strptime(profile.bedtime_end, '%H:%M').time()
        
        if start <= end:
            return start <= now <= end
        else:  # Overnight (e.g., 22:00 to 07:00)
            return now >= start or now <= end
    
    def _is_allowed_time(self, profile: DeviceProfile) -> bool:
        """Check if current time is within allowed hours"""
        now = datetime.now()
        day = now.strftime('%A').lower()
        
        # Check allowed days
        if day not in [d.lower() for d in profile.allowed_days]:
            return False
        
        # Check bedtime
        if self._is_bedtime(profile):
            return False
        
        # Check allowed hours
        current_time = now.time()
        start = datetime.strptime(profile.allowed_hours_start, '%H:%M').time()
        end = datetime.strptime(profile.allowed_hours_end, '%H:%M').time()
        
        return start <= current_time <= end
    
    def check_access(self, device_mac: str) -> Dict:
        """Check if a device should have internet access"""
        if device_mac not in self.profiles:
            return {'allowed': True, 'reason': 'no_profile'}
        
        profile = self.profiles[device_mac]
        
        if not profile.is_active:
            return {'allowed': True, 'reason': 'profile_inactive'}
        
        # Check time limits
        if profile.daily_limit_minutes > 0:
            if profile.time_used_today >= profile.daily_limit_minutes:
                return {'allowed': False, 'reason': 'daily_limit_reached', 
                        'limit': profile.daily_limit_minutes,
                        'used': profile.time_used_today}
        
        # Check bedtime
        if self._is_bedtime(profile):
            return {'allowed': False, 'reason': 'bedtime',
                    'bedtime_end': profile.bedtime_end}
        
        # Check allowed time
        if not self._is_allowed_time(profile):
            return {'allowed': False, 'reason': 'outside_allowed_hours'}
        
        return {'allowed': True, 'reason': 'ok'}
    
    def record_usage(self, device_mac: str, minutes: int = 1, site: str = None):
        """Record usage for a device"""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"{device_mac}_{today}"
        
        with self._lock:
            if key not in self.usage_records:
                self.usage_records[key] = UsageRecord(
                    device_mac=device_mac,
                    date=today
                )
            
            record = self.usage_records[key]
            record.minutes_used += minutes
            
            if site:
                record.sites_visited[site] = record.sites_visited.get(site, 0) + 1
            
            # Update profile's daily usage
            if device_mac in self.profiles:
                self.profiles[device_mac].time_used_today = record.minutes_used
            
            self._save_usage()
    
    def get_usage_report(self, device_mac: str, days: int = 7) -> Dict:
        """Get usage report for a device"""
        reports = []
        today = datetime.now()
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            key = f"{device_mac}_{date}"
            
            if key in self.usage_records:
                record = self.usage_records[key]
                reports.append({
                    'date': date,
                    'minutes_used': record.minutes_used,
                    'hours_used': round(record.minutes_used / 60, 1),
                    'sites_visited': len(record.sites_visited),
                    'top_sites': sorted(
                        record.sites_visited.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5],
                    'blocked_attempts': record.blocked_attempts
                })
            else:
                reports.append({
                    'date': date,
                    'minutes_used': 0,
                    'hours_used': 0,
                    'sites_visited': 0,
                    'top_sites': [],
                    'blocked_attempts': 0
                })
        
        total_minutes = sum(r['minutes_used'] for r in reports)
        
        return {
            'device_mac': device_mac,
            'period_days': days,
            'total_minutes': total_minutes,
            'total_hours': round(total_minutes / 60, 1),
            'average_daily_minutes': round(total_minutes / days, 1),
            'daily_reports': reports
        }
    
    def reset_daily_usage(self):
        """Reset daily usage counters (call at midnight)"""
        with self._lock:
            for profile in self.profiles.values():
                profile.time_used_today = 0
            self._save_data()
    
    def _start_tracker(self):
        """Start background tracker for time limits"""
        def tracker():
            last_reset_day = datetime.now().day
            
            while True:
                # Check for day change to reset counters
                current_day = datetime.now().day
                if current_day != last_reset_day:
                    self.reset_daily_usage()
                    last_reset_day = current_day
                
                # Check each profile for bedtime/limits
                for profile in self.profiles.values():
                    if not profile.is_active:
                        continue
                    
                    access = self.check_access(profile.device_mac)
                    if not access['allowed']:
                        # Trigger block - this would call network_pranks.block_everything
                        try:
                            from core.alerts import alert_manager, AlertType, AlertSeverity
                            if access['reason'] == 'bedtime':
                                alert_manager.create_alert(
                                    AlertType.SYSTEM_INFO,
                                    "🌙 Modo hora de dormir",
                                    f"Acceso bloqueado para {profile.device_name}",
                                    AlertSeverity.INFO
                                )
                            elif access['reason'] == 'daily_limit_reached':
                                alert_manager.create_alert(
                                    AlertType.SYSTEM_INFO,
                                    "⏱️ Límite diario alcanzado",
                                    f"{profile.device_name} ha alcanzado su límite de {profile.daily_limit_minutes} minutos",
                                    AlertSeverity.INFO
                                )
                        except:
                            pass
                
                time.sleep(60)  # Check every minute
        
        thread = threading.Thread(target=tracker, daemon=True)
        thread.start()
    
    def get_categories(self) -> List[Dict]:
        """Get available content categories"""
        return [
            {'id': c.value, 'name': c.name.replace('_', ' ').title(), 'domains_count': len(CATEGORY_DOMAINS.get(c, []))}
            for c in ContentCategory
        ]


# Global instance
parental_control = ParentalControl()
