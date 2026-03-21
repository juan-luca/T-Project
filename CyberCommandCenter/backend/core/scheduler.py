"""
Cyber Command Center - Prank Scheduler
Schedule pranks to run at specific times, recurring pranks
"""
import threading
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import schedule
from pathlib import Path


class ScheduleType(Enum):
    ONCE = "once"           # Run once at specific time
    DAILY = "daily"         # Run every day at specific time
    WEEKLY = "weekly"       # Run on specific days of week
    INTERVAL = "interval"   # Run every X minutes/hours


@dataclass
class ScheduledPrank:
    id: str
    prank_id: str
    device_ip: str
    device_name: str
    schedule_type: ScheduleType
    time: str                    # HH:MM format
    days: List[str] = None       # For weekly: ['monday', 'wednesday']
    interval_minutes: int = None  # For interval type
    enabled: bool = True
    created_at: datetime = None
    last_run: datetime = None
    next_run: datetime = None
    run_count: int = 0
    options: Dict = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'prank_id': self.prank_id,
            'device_ip': self.device_ip,
            'device_name': self.device_name,
            'schedule_type': self.schedule_type.value,
            'time': self.time,
            'days': self.days,
            'interval_minutes': self.interval_minutes,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'run_count': self.run_count,
            'options': self.options or {}
        }


class PrankScheduler:
    """
    Schedule pranks to run automatically at specified times
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
        self.scheduled_pranks: Dict[str, ScheduledPrank] = {}
        self.prank_executor: Callable = None  # Set by app.py
        self._scheduler_thread = None
        self._running = False
        self._counter = 0
        self._lock = threading.Lock()
        self._data_file = Path(__file__).parent.parent / "database" / "scheduled_pranks.json"
        
        # Load saved schedules
        self._load_schedules()
    
    def _generate_id(self) -> str:
        """Generate unique schedule ID"""
        with self._lock:
            self._counter += 1
            return f"sched_{int(time.time())}_{self._counter}"
    
    def set_prank_executor(self, executor: Callable):
        """Set the function to execute pranks"""
        self.prank_executor = executor
    
    def _load_schedules(self):
        """Load scheduled pranks from file"""
        try:
            if self._data_file.exists():
                with open(self._data_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        item['schedule_type'] = ScheduleType(item['schedule_type'])
                        item['created_at'] = datetime.fromisoformat(item['created_at']) if item.get('created_at') else datetime.now()
                        item['last_run'] = datetime.fromisoformat(item['last_run']) if item.get('last_run') else None
                        item['next_run'] = datetime.fromisoformat(item['next_run']) if item.get('next_run') else None
                        prank = ScheduledPrank(**item)
                        self.scheduled_pranks[prank.id] = prank
        except Exception as e:
            print(f"Error loading schedules: {e}")
    
    def _save_schedules(self):
        """Save scheduled pranks to file"""
        try:
            self._data_file.parent.mkdir(parents=True, exist_ok=True)
            data = [p.to_dict() for p in self.scheduled_pranks.values()]
            with open(self._data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving schedules: {e}")
    
    def add_schedule(
        self,
        prank_id: str,
        device_ip: str,
        device_name: str,
        schedule_type: str,
        time_str: str,
        days: List[str] = None,
        interval_minutes: int = None,
        options: Dict = None
    ) -> ScheduledPrank:
        """Add a new scheduled prank"""
        
        sched = ScheduledPrank(
            id=self._generate_id(),
            prank_id=prank_id,
            device_ip=device_ip,
            device_name=device_name,
            schedule_type=ScheduleType(schedule_type),
            time=time_str,
            days=days or [],
            interval_minutes=interval_minutes,
            enabled=True,
            created_at=datetime.now(),
            options=options or {}
        )
        
        # Calculate next run
        sched.next_run = self._calculate_next_run(sched)
        
        self.scheduled_pranks[sched.id] = sched
        self._save_schedules()
        
        return sched
    
    def _calculate_next_run(self, sched: ScheduledPrank) -> Optional[datetime]:
        """Calculate the next run time for a schedule"""
        now = datetime.now()
        
        if sched.schedule_type == ScheduleType.ONCE:
            # Parse time and set for today or tomorrow
            hour, minute = map(int, sched.time.split(':'))
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        
        elif sched.schedule_type == ScheduleType.DAILY:
            hour, minute = map(int, sched.time.split(':'))
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        
        elif sched.schedule_type == ScheduleType.WEEKLY:
            if not sched.days:
                return None
            
            hour, minute = map(int, sched.time.split(':'))
            day_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2,
                'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
            }
            
            target_days = [day_map[d.lower()] for d in sched.days if d.lower() in day_map]
            if not target_days:
                return None
            
            for i in range(8):  # Check next 7 days
                check_date = now + timedelta(days=i)
                if check_date.weekday() in target_days:
                    next_run = check_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if next_run > now:
                        return next_run
            return None
        
        elif sched.schedule_type == ScheduleType.INTERVAL:
            if sched.interval_minutes:
                return now + timedelta(minutes=sched.interval_minutes)
        
        return None
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """Remove a scheduled prank"""
        if schedule_id in self.scheduled_pranks:
            del self.scheduled_pranks[schedule_id]
            self._save_schedules()
            return True
        return False
    
    def toggle_schedule(self, schedule_id: str) -> Optional[bool]:
        """Toggle a schedule on/off"""
        if schedule_id in self.scheduled_pranks:
            sched = self.scheduled_pranks[schedule_id]
            sched.enabled = not sched.enabled
            if sched.enabled:
                sched.next_run = self._calculate_next_run(sched)
            self._save_schedules()
            return sched.enabled
        return None
    
    def get_schedules(self, device_ip: str = None) -> List[Dict]:
        """Get all scheduled pranks"""
        schedules = list(self.scheduled_pranks.values())
        
        if device_ip:
            schedules = [s for s in schedules if s.device_ip == device_ip]
        
        # Sort by next run
        schedules.sort(key=lambda s: s.next_run or datetime.max)
        
        return [s.to_dict() for s in schedules]
    
    def get_schedule(self, schedule_id: str) -> Optional[Dict]:
        """Get a specific schedule"""
        if schedule_id in self.scheduled_pranks:
            return self.scheduled_pranks[schedule_id].to_dict()
        return None
    
    def _execute_scheduled_prank(self, sched: ScheduledPrank):
        """Execute a scheduled prank"""
        if not self.prank_executor:
            print(f"No prank executor set for schedule {sched.id}")
            return
        
        try:
            print(f"[Scheduler] Executing prank {sched.prank_id} on {sched.device_ip}")
            result = self.prank_executor(sched.prank_id, sched.device_ip, sched.options)
            
            sched.last_run = datetime.now()
            sched.run_count += 1
            
            # Calculate next run for recurring schedules
            if sched.schedule_type != ScheduleType.ONCE:
                sched.next_run = self._calculate_next_run(sched)
            else:
                sched.enabled = False  # Disable one-time schedules after running
            
            self._save_schedules()
            
            # Send alert
            try:
                from core.alerts import alert_manager, AlertType, AlertSeverity
                alert_manager.create_alert(
                    AlertType.PRANK_COMPLETED,
                    "⏰ Prank programado ejecutado",
                    f"Prank '{sched.prank_id}' ejecutado en {sched.device_name}",
                    AlertSeverity.INFO,
                    data={'schedule_id': sched.id, 'result': result}
                )
            except:
                pass
            
        except Exception as e:
            print(f"[Scheduler] Error executing prank: {e}")
    
    def _check_schedules(self):
        """Check and execute due schedules"""
        now = datetime.now()
        
        for sched in list(self.scheduled_pranks.values()):
            if not sched.enabled or not sched.next_run:
                continue
            
            if now >= sched.next_run:
                # Execute in thread to not block scheduler
                threading.Thread(
                    target=self._execute_scheduled_prank,
                    args=(sched,),
                    daemon=True
                ).start()
    
    def start(self):
        """Start the scheduler service"""
        if self._running:
            return
        
        self._running = True
        
        def run_scheduler():
            while self._running:
                self._check_schedules()
                time.sleep(30)  # Check every 30 seconds
        
        self._scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self._scheduler_thread.start()
        print("[Scheduler] Started")
    
    def stop(self):
        """Stop the scheduler service"""
        self._running = False
        print("[Scheduler] Stopped")
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics"""
        total = len(self.scheduled_pranks)
        enabled = sum(1 for s in self.scheduled_pranks.values() if s.enabled)
        
        upcoming = []
        now = datetime.now()
        for sched in sorted(
            self.scheduled_pranks.values(),
            key=lambda s: s.next_run or datetime.max
        )[:5]:
            if sched.enabled and sched.next_run:
                upcoming.append({
                    'id': sched.id,
                    'prank': sched.prank_id,
                    'device': sched.device_name,
                    'next_run': sched.next_run.isoformat(),
                    'time_until': str(sched.next_run - now)
                })
        
        return {
            'total_schedules': total,
            'enabled': enabled,
            'disabled': total - enabled,
            'upcoming': upcoming
        }


# Global instance
prank_scheduler = PrankScheduler()
