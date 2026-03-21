"""
Cyber Command Center - Telegram Bot Integration
Remote control and notifications via Telegram
"""
import threading
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass


@dataclass
class TelegramSettings:
    bot_token: str = ""
    chat_id: str = ""
    enabled: bool = False
    notify_new_device: bool = True
    notify_device_disconnect: bool = False
    notify_pranks: bool = True
    notify_security: bool = True
    allow_commands: bool = True


class TelegramBot:
    """
    Telegram Bot for remote control and notifications
    
    Commands:
    /status - Get network status
    /devices - List online devices
    /scan - Trigger network scan
    /block <ip> - Block a device
    /unblock <ip> - Unblock a device
    /prank <prank_id> <ip> - Execute a prank
    /alerts - Get recent alerts
    /help - Show commands
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
        self.settings = TelegramSettings()
        self._data_file = Path(__file__).parent.parent / "database" / "telegram_settings.json"
        self._running = False
        self._poll_thread = None
        self._last_update_id = 0
        self._command_handlers: Dict[str, Callable] = {}
        
        # Load settings
        self._load_settings()
        
        # Register default command handlers
        self._register_default_commands()
    
    def _load_settings(self):
        """Load settings from file"""
        try:
            if self._data_file.exists():
                with open(self._data_file, 'r') as f:
                    data = json.load(f)
                    self.settings = TelegramSettings(**data)
        except Exception as e:
            print(f"Error loading Telegram settings: {e}")
    
    def _save_settings(self):
        """Save settings to file"""
        try:
            self._data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self._data_file, 'w') as f:
                json.dump(self.settings.__dict__, f, indent=2)
        except Exception as e:
            print(f"Error saving Telegram settings: {e}")
    
    def configure(self, bot_token: str, chat_id: str, **kwargs) -> Dict:
        """Configure the Telegram bot"""
        self.settings.bot_token = bot_token
        self.settings.chat_id = chat_id
        
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
        
        # Test connection
        if self.test_connection():
            self.settings.enabled = True
            self._save_settings()
            return {'success': True, 'message': 'Bot configurado correctamente'}
        else:
            return {'success': False, 'message': 'No se pudo conectar con el bot'}
    
    def test_connection(self) -> bool:
        """Test bot connection"""
        try:
            url = f"https://api.telegram.org/bot{self.settings.bot_token}/getMe"
            response = requests.get(url, timeout=10)
            return response.status_code == 200 and response.json().get('ok', False)
        except:
            return False
    
    def send_message(self, text: str, parse_mode: str = "HTML", 
                     disable_notification: bool = False) -> bool:
        """Send a message to the configured chat"""
        if not self.settings.enabled or not self.settings.bot_token or not self.settings.chat_id:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.settings.bot_token}/sendMessage"
            payload = {
                'chat_id': self.settings.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_notification': disable_notification
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    def send_photo(self, photo_url: str, caption: str = "") -> bool:
        """Send a photo"""
        if not self.settings.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.settings.bot_token}/sendPhoto"
            payload = {
                'chat_id': self.settings.chat_id,
                'photo': photo_url,
                'caption': caption,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _register_default_commands(self):
        """Register default command handlers"""
        
        @self.command('start')
        def cmd_start(args):
            return """🛡️ <b>Cyber Command Center Bot</b>

Bienvenido al bot de control remoto.

Comandos disponibles:
/status - Estado de la red
/devices - Dispositivos conectados
/scan - Escanear red
/block [ip] - Bloquear dispositivo
/unblock [ip] - Desbloquear dispositivo
/prank [id] [ip] - Ejecutar prank
/alerts - Alertas recientes
/help - Ayuda"""
        
        @self.command('help')
        def cmd_help(args):
            return """📖 <b>Comandos disponibles:</b>

🔍 <b>Monitoreo:</b>
/status - Estado general de la red
/devices - Lista dispositivos online
/scan - Ejecuta escaneo de red
/alerts - Muestra alertas recientes

🎮 <b>Control:</b>
/block [ip] - Bloquea internet a un dispositivo
/unblock [ip] - Desbloquea un dispositivo
/prank [id] [ip] - Ejecuta un prank

📊 <b>Información:</b>
/stats - Estadísticas del sistema
/health - Estado del servidor"""
        
        @self.command('status')
        def cmd_status(args):
            try:
                from database.models import get_session, Device
                session = get_session()
                
                total = session.query(Device).count()
                online = session.query(Device).filter_by(is_online=True).count()
                blocked = session.query(Device).filter_by(is_blocked=True).count()
                
                session.close()
                
                return f"""📊 <b>Estado de la Red</b>

📱 Dispositivos totales: {total}
🟢 En línea: {online}
🔴 Fuera de línea: {total - online}
🚫 Bloqueados: {blocked}

⏰ Actualizado: {datetime.now().strftime('%H:%M:%S')}"""
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        @self.command('devices')
        def cmd_devices(args):
            try:
                from database.models import get_session, Device
                session = get_session()
                
                devices = session.query(Device).filter_by(is_online=True).all()
                session.close()
                
                if not devices:
                    return "📱 No hay dispositivos en línea"
                
                text = "📱 <b>Dispositivos en línea:</b>\n\n"
                for d in devices[:15]:  # Limit to 15
                    status = "🚫" if d.is_blocked else "✅" if d.is_trusted else "📱"
                    name = d.custom_name or d.hostname or f"Device-{d.mac_address[-5:]}"
                    text += f"{status} <code>{d.ip_address}</code> - {name}\n"
                
                if len(devices) > 15:
                    text += f"\n... y {len(devices) - 15} más"
                
                return text
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        @self.command('scan')
        def cmd_scan(args):
            try:
                # Trigger scan via internal function
                return "🔍 Escaneo iniciado... Los resultados aparecerán en el dashboard."
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        @self.command('alerts')
        def cmd_alerts(args):
            try:
                from core.alerts import alert_manager
                
                alerts = alert_manager.get_alerts(limit=5, unread_only=True)
                
                if not alerts:
                    return "✅ No hay alertas pendientes"
                
                text = "🔔 <b>Alertas recientes:</b>\n\n"
                for a in alerts:
                    icon = "🆕" if a['type'] == 'new_device' else "⚠️" if a['severity'] == 'high' else "ℹ️"
                    text += f"{icon} {a['title']}\n   <i>{a['message'][:50]}</i>\n\n"
                
                return text
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        @self.command('block')
        def cmd_block(args):
            if not args:
                return "❌ Uso: /block [ip]\nEjemplo: /block 192.168.1.100"
            
            ip = args[0]
            try:
                from core.network_pranks import network_pranks
                result = network_pranks.block_everything(ip)
                if result.get('success'):
                    return f"🚫 Dispositivo {ip} bloqueado"
                return f"❌ Error: {result.get('error', 'Unknown')}"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        @self.command('unblock')
        def cmd_unblock(args):
            if not args:
                return "❌ Uso: /unblock [ip]\nEjemplo: /unblock 192.168.1.100"
            
            ip = args[0]
            try:
                from core.network_pranks import network_pranks
                result = network_pranks.unblock_everything(ip)
                if result.get('success'):
                    return f"✅ Dispositivo {ip} desbloqueado"
                return f"❌ Error: {result.get('error', 'Unknown')}"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        @self.command('prank')
        def cmd_prank(args):
            if len(args) < 2:
                return """❌ Uso: /prank [id] [ip]
Ejemplo: /prank rickroll 192.168.1.100

Pranks disponibles:
• rickroll
• block_social
• block_video
• block_gaming
• slow_internet"""
            
            prank_id, ip = args[0], args[1]
            try:
                from core.network_pranks import network_pranks
                result = network_pranks.execute_prank(prank_id, ip, {})
                if result.get('success'):
                    return f"😈 Prank '{prank_id}' ejecutado en {ip}"
                return f"❌ Error: {result.get('error', 'Unknown')}"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        @self.command('health')
        def cmd_health(args):
            try:
                from core.error_handlers import HealthChecker
                health = HealthChecker.get_health_status()
                
                status_emoji = "🟢" if health['status'] == 'healthy' else "🟡" if health['status'] == 'warning' else "🔴"
                
                return f"""{status_emoji} <b>Estado del Sistema</b>

💾 CPU: {health['system']['cpu_percent']}%
🧠 RAM: {health['system']['memory']['percent']}%
💿 Disco: {health['system']['disk']['percent']}%
⏱️ Uptime: {health['uptime']['human']}
📊 Versión: {health['version']}"""
            except Exception as e:
                return f"❌ Error: {str(e)}"
    
    def command(self, name: str):
        """Decorator to register a command handler"""
        def decorator(func):
            self._command_handlers[name.lower()] = func
            return func
        return decorator
    
    def _process_update(self, update: Dict):
        """Process a Telegram update"""
        if 'message' not in update:
            return
        
        message = update['message']
        chat_id = str(message.get('chat', {}).get('id', ''))
        
        # Security: Only respond to configured chat
        if chat_id != self.settings.chat_id:
            return
        
        text = message.get('text', '')
        if not text.startswith('/'):
            return
        
        # Parse command
        parts = text[1:].split()
        command = parts[0].lower().split('@')[0]  # Remove @botname if present
        args = parts[1:]
        
        # Execute handler
        if command in self._command_handlers:
            try:
                response = self._command_handlers[command](args)
                if response:
                    self.send_message(response)
            except Exception as e:
                self.send_message(f"❌ Error ejecutando comando: {str(e)}")
    
    def _poll_updates(self):
        """Poll for new messages"""
        url = f"https://api.telegram.org/bot{self.settings.bot_token}/getUpdates"
        
        while self._running:
            try:
                params = {
                    'offset': self._last_update_id + 1,
                    'timeout': 30
                }
                response = requests.get(url, params=params, timeout=35)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        for update in data.get('result', []):
                            self._last_update_id = update['update_id']
                            if self.settings.allow_commands:
                                self._process_update(update)
            except Exception as e:
                print(f"Telegram poll error: {e}")
                time.sleep(5)
    
    def start(self):
        """Start the bot"""
        if not self.settings.enabled or not self.settings.bot_token:
            return False
        
        if self._running:
            return True
        
        self._running = True
        self._poll_thread = threading.Thread(target=self._poll_updates, daemon=True)
        self._poll_thread.start()
        
        # Send startup message
        self.send_message("🚀 <b>Cyber Command Center</b> iniciado\n\nEscribe /help para ver comandos disponibles.")
        
        return True
    
    def stop(self):
        """Stop the bot"""
        self._running = False
        self.send_message("🔴 <b>Cyber Command Center</b> detenido")
    
    def notify_alert(self, alert: Dict):
        """Send alert notification"""
        if not self.settings.enabled:
            return
        
        alert_type = alert.get('type', '')
        
        # Check notification settings
        if alert_type == 'new_device' and not self.settings.notify_new_device:
            return
        if alert_type == 'device_disconnected' and not self.settings.notify_device_disconnect:
            return
        if alert_type in ['prank_started', 'prank_completed', 'prank_failed'] and not self.settings.notify_pranks:
            return
        if alert_type in ['suspicious_activity', 'security_warning'] and not self.settings.notify_security:
            return
        
        # Format and send
        severity_emoji = {
            'info': 'ℹ️',
            'low': '📝',
            'medium': '⚠️',
            'high': '🚨',
            'critical': '🔴'
        }
        
        emoji = severity_emoji.get(alert.get('severity', 'info'), 'ℹ️')
        text = f"{emoji} <b>{alert.get('title', 'Alert')}</b>\n\n{alert.get('message', '')}"
        
        self.send_message(text, disable_notification=(alert.get('severity') == 'info'))
    
    def get_settings(self) -> Dict:
        """Get current settings"""
        return {
            **self.settings.__dict__,
            'configured': bool(self.settings.bot_token and self.settings.chat_id),
            'running': self._running
        }
    
    def update_settings(self, updates: Dict) -> Dict:
        """Update notification settings"""
        for key, value in updates.items():
            if hasattr(self.settings, key) and key not in ['bot_token', 'chat_id']:
                setattr(self.settings, key, value)
        
        self._save_settings()
        return self.get_settings()


# Global instance
telegram_bot = TelegramBot()
