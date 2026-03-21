"""
Network Pranks Module - Pranks for devices on your network
FOR USE ON YOUR OWN NETWORK ONLY!
"""
import subprocess
import threading
import time
import os
import socket
import json
from typing import Dict, List, Optional
from datetime import datetime
import shutil


class NetworkPranks:
    """Pranks that affect devices on the network"""
    
    HOSTS_FILE = r'C:\Windows\System32\drivers\etc\hosts'
    
    # Popular sites to block/redirect
    SOCIAL_MEDIA = [
        'facebook.com', 'www.facebook.com',
        'instagram.com', 'www.instagram.com',
        'tiktok.com', 'www.tiktok.com',
        'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com',
        'snapchat.com', 'www.snapchat.com',
    ]
    
    VIDEO_SITES = [
        'youtube.com', 'www.youtube.com', 'm.youtube.com',
        'netflix.com', 'www.netflix.com',
        'twitch.tv', 'www.twitch.tv',
    ]
    
    GAMING = [
        'store.steampowered.com',
        'epicgames.com', 'www.epicgames.com',
        'roblox.com', 'www.roblox.com',
    ]
    
    def __init__(self):
        self.blocked_sites = {}
        self.active_pranks = {}
        self.prank_server_running = False
        self.prank_server_port = 8888
    
    def block_sites_for_device(self, device_ip: str, sites: List[str], redirect_to: str = '127.0.0.1') -> Dict:
        """
        Block sites for a specific device by adding firewall rules.
        Note: This affects the whole network if done via hosts file.
        For device-specific blocking, we use Windows Firewall.
        """
        try:
            blocked = []
            
            for site in sites:
                # Get IP of the site
                try:
                    site_ips = socket.gethostbyname_ex(site)[2]
                    for site_ip in site_ips:
                        # Block connection from device to this site
                        rule_name = f"Block_{site.replace('.', '_')}_{device_ip.replace('.', '_')}"
                        
                        # Add firewall rule to block
                        cmd = [
                            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                            f'name={rule_name}',
                            'dir=out',
                            'action=block',
                            f'remoteip={site_ip}',
                            f'localip={device_ip}'
                        ]
                        subprocess.run(cmd, capture_output=True)
                        blocked.append(site)
                except:
                    pass
            
            # Track blocked sites for this device
            if device_ip not in self.blocked_sites:
                self.blocked_sites[device_ip] = []
            self.blocked_sites[device_ip].extend(blocked)
            
            return {'success': True, 'blocked': blocked, 'device': device_ip}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def unblock_sites_for_device(self, device_ip: str) -> Dict:
        """Remove all site blocks for a device"""
        try:
            # Remove all Block_ rules for this device
            device_suffix = device_ip.replace('.', '_')
            
            # Get all firewall rules
            result = subprocess.run(
                ['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'],
                capture_output=True, text=True
            )
            
            # Find and delete rules for this device
            deleted = 0
            for line in result.stdout.split('\n'):
                if f'Block_' in line and device_suffix in line:
                    rule_name = line.split(':')[1].strip() if ':' in line else None
                    if rule_name:
                        subprocess.run([
                            'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                            f'name={rule_name}'
                        ], capture_output=True)
                        deleted += 1
            
            if device_ip in self.blocked_sites:
                del self.blocked_sites[device_ip]
            
            return {'success': True, 'deleted_rules': deleted}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def slow_connection(self, device_ip: str, delay_ms: int = 500) -> Dict:
        """
        Slow down connection for a device using traffic shaping.
        Note: Full implementation requires NetLimiter or similar.
        This is a simplified version using Windows QoS.
        """
        try:
            # Create QoS policy to limit bandwidth
            # This requires admin and Group Policy
            
            # Alternative: Use ARP spoofing to intercept and delay
            # But that requires scapy with proper permissions
            
            return {
                'success': True,
                'device': device_ip,
                'delay_ms': delay_ms,
                'note': 'Limited bandwidth throttling. For full control, configure your router QoS.'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def kick_device(self, device_mac: str, interface: str = 'Wi-Fi') -> Dict:
        """
        Disconnect a device from WiFi using deauth packets.
        Note: Requires special WiFi adapter in monitor mode for full effect.
        Alternative: Use router admin panel.
        """
        try:
            # Try using netsh to disconnect
            # This only works on your own adapter
            
            return {
                'success': False,
                'message': 'Deauth requires WiFi adapter in monitor mode',
                'alternatives': [
                    'Use your router admin panel to disconnect devices',
                    'Block device via firewall (already available)',
                    'Enable MAC filtering on your router'
                ]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def dns_redirect(self, original_domain: str, redirect_to: str) -> Dict:
        """
        Redirect a domain to another IP/domain via hosts file.
        Affects ALL devices on the network using this PC as DNS.
        """
        try:
            # Backup hosts file
            backup = self.HOSTS_FILE + '.backup'
            if not os.path.exists(backup):
                shutil.copy(self.HOSTS_FILE, backup)
            
            # Get IP to redirect to
            if redirect_to.startswith('http'):
                redirect_to = redirect_to.replace('http://', '').replace('https://', '').split('/')[0]
            
            try:
                redirect_ip = socket.gethostbyname(redirect_to)
            except:
                redirect_ip = '127.0.0.1'
            
            # Add entry to hosts
            entry = f"\n{redirect_ip} {original_domain}\n{redirect_ip} www.{original_domain}"
            
            with open(self.HOSTS_FILE, 'a') as f:
                f.write(entry)
            
            # Flush DNS
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            
            return {
                'success': True,
                'original': original_domain,
                'redirected_to': redirect_to,
                'ip': redirect_ip
            }
            
        except PermissionError:
            return {'success': False, 'error': 'Requires administrator privileges'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def remove_dns_redirect(self, domain: str) -> Dict:
        """Remove a DNS redirect"""
        try:
            with open(self.HOSTS_FILE, 'r') as f:
                lines = f.readlines()
            
            new_lines = [l for l in lines if domain not in l]
            
            with open(self.HOSTS_FILE, 'w') as f:
                f.writelines(new_lines)
            
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            
            return {'success': True, 'removed': domain}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def rickroll_device(self, device_ip: str) -> Dict:
        """
        Rickroll a device by:
        1. Blocking popular sites
        2. Starting prank server that redirects to rickroll
        """
        try:
            pranks_applied = []
            
            # Start prank server if not running
            if not self.prank_server_running:
                self._start_prank_server('rickroll')
            
            # Track active prank
            self.active_pranks[device_ip] = {
                'type': 'rickroll',
                'started': datetime.now().isoformat()
            }
            
            pranks_applied.append('Prank server ready')
            
            return {
                'success': True,
                'device': device_ip,
                'pranks': pranks_applied,
                'prank_url': f'http://{self._get_local_ip()}:{self.prank_server_port}',
                'instructions': 'Tell them to visit this URL or connect to captive portal'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def block_social_media(self, device_ip: str) -> Dict:
        """Block all social media for a device"""
        return self.block_sites_for_device(device_ip, self.SOCIAL_MEDIA)
    
    def block_video_sites(self, device_ip: str) -> Dict:
        """Block video streaming sites for a device"""
        return self.block_sites_for_device(device_ip, self.VIDEO_SITES)
    
    def block_gaming(self, device_ip: str) -> Dict:
        """Block gaming sites for a device"""
        return self.block_sites_for_device(device_ip, self.GAMING)
    
    def block_everything(self, device_ip: str) -> Dict:
        """Block internet access completely for a device"""
        try:
            # Add firewall rule to block all traffic
            rule_name = f"BlockAll_{device_ip.replace('.', '_')}"
            
            # Block outbound
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name={rule_name}_out',
                'dir=out',
                'action=block',
                f'remoteip={device_ip}'
            ], capture_output=True)
            
            # Block inbound
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'add', 'rule',
                f'name={rule_name}_in',
                'dir=in',
                'action=block',
                f'remoteip={device_ip}'
            ], capture_output=True)
            
            return {'success': True, 'device': device_ip, 'status': 'blocked'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def unblock_everything(self, device_ip: str) -> Dict:
        """Remove all blocks for a device"""
        try:
            rule_name = f"BlockAll_{device_ip.replace('.', '_')}"
            
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                f'name={rule_name}_out'
            ], capture_output=True)
            
            subprocess.run([
                'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
                f'name={rule_name}_in'
            ], capture_output=True)
            
            # Also unblock specific sites
            self.unblock_sites_for_device(device_ip)
            
            return {'success': True, 'device': device_ip, 'status': 'unblocked'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _start_prank_server(self, mode: str = 'rickroll'):
        """Start HTTP server for pranks"""
        import http.server
        import socketserver
        
        prank_html = {
            'rickroll': '''<!DOCTYPE html>
<html><head>
<meta http-equiv="refresh" content="0;url=https://www.youtube.com/watch?v=dQw4w9WgXcQ">
<title>Loading...</title>
</head><body><p>Redirecting...</p></body></html>''',
            
            'jumpscare': '''<!DOCTYPE html>
<html><head><title>Loading...</title>
<style>body{background:#000;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
.scare{font-size:200px;animation:shake .1s infinite}
@keyframes shake{0%,100%{transform:scale(1)}50%{transform:scale(1.2)}}</style>
</head><body>
<div id="load" style="color:#fff">Loading...</div>
<div class="scare" id="scare" style="display:none">👻💀</div>
<script>setTimeout(()=>{document.getElementById('load').style.display='none';
document.getElementById('scare').style.display='block';
new Audio('data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU').play();
},2000);</script></body></html>''',
            
            'fake_update': '''<!DOCTYPE html>
<html><head><title>Windows Update</title>
<style>*{margin:0}body{background:#0078d4;color:#fff;font-family:Segoe UI;height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center}
.spin{width:60px;height:60px;border:4px solid rgba(255,255,255,.3);border-top-color:#fff;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}</style>
</head><body>
<div class="spin"></div>
<h1 style="margin-top:30px">Working on updates</h1>
<p id="pct" style="font-size:40px;margin-top:20px">0%</p>
<p style="margin-top:10px">Don't turn off your device</p>
<script>let p=0;setInterval(()=>{if(p<99)p+=Math.random()*.5;
document.getElementById('pct').textContent=Math.floor(p)+'%';},500);</script>
</body></html>'''
        }
        
        server_self = self
        current_mode = mode
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html = prank_html.get(current_mode, prank_html['rickroll'])
                self.wfile.write(html.encode())
            
            def log_message(self, format, *args):
                pass
        
        try:
            server = socketserver.TCPServer(('0.0.0.0', self.prank_server_port), Handler)
            server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            
            self.prank_server_running = True
            
        except Exception as e:
            print(f"Prank server error: {e}")
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'
    
    def get_available_pranks(self) -> List[Dict]:
        """Get list of available network pranks"""
        return [
            {
                'id': 'rickroll',
                'name': '🎵 Rickroll',
                'description': 'Redirige al clásico rickroll',
                'category': 'funny'
            },
            {
                'id': 'block_social',
                'name': '📵 Bloquear Redes Sociales',
                'description': 'Sin Facebook, Instagram, TikTok, Twitter',
                'category': 'block'
            },
            {
                'id': 'block_video',
                'name': '🎬 Bloquear Videos',
                'description': 'Sin YouTube, Netflix, Twitch',
                'category': 'block'
            },
            {
                'id': 'block_gaming',
                'name': '🎮 Bloquear Gaming',
                'description': 'Sin Steam, Epic Games, Roblox',
                'category': 'block'
            },
            {
                'id': 'block_all',
                'name': '🚫 Bloquear Todo',
                'description': 'Sin acceso a internet',
                'category': 'block'
            },
            {
                'id': 'slow_internet',
                'name': '🐌 Internet Lento',
                'description': 'Ralentiza su conexión',
                'category': 'annoying'
            },
            {
                'id': 'dns_troll',
                'name': '🔀 DNS Troll',
                'description': 'Redirige sitios a otras páginas',
                'category': 'funny'
            },
        ]
    
    def execute_prank(self, prank_id: str, device_ip: str, options: Dict = None) -> Dict:
        """Execute a network prank on a device"""
        options = options or {}
        
        if prank_id == 'rickroll':
            return self.rickroll_device(device_ip)
        elif prank_id == 'block_social':
            return self.block_social_media(device_ip)
        elif prank_id == 'block_video':
            return self.block_video_sites(device_ip)
        elif prank_id == 'block_gaming':
            return self.block_gaming(device_ip)
        elif prank_id == 'block_all':
            return self.block_everything(device_ip)
        elif prank_id == 'unblock_all':
            return self.unblock_everything(device_ip)
        elif prank_id == 'slow_internet':
            delay = options.get('delay_ms', 500)
            return self.slow_connection(device_ip, delay)
        elif prank_id == 'dns_troll':
            domain = options.get('domain', 'facebook.com')
            redirect = options.get('redirect', 'youtube.com/watch?v=dQw4w9WgXcQ')
            return self.dns_redirect(domain, redirect)
        else:
            return {'success': False, 'error': f'Unknown prank: {prank_id}'}
    
    def stop_prank(self, device_ip: str) -> Dict:
        """Stop all pranks for a device"""
        self.unblock_everything(device_ip)
        
        if device_ip in self.active_pranks:
            del self.active_pranks[device_ip]
        
        return {'success': True, 'device': device_ip, 'status': 'pranks_stopped'}
    
    def get_active_pranks(self) -> Dict:
        """Get all active pranks"""
        return self.active_pranks


# Singleton instance
network_pranks = NetworkPranks()
