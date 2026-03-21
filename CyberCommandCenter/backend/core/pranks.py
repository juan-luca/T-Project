"""
Cyber Command Center - Pranks Module v3.0
Fun pranks that work on Windows - ALL work without external apps!
FOR USE ON YOUR OWN NETWORK/DEVICES ONLY!
"""
import subprocess
import threading
import time
import os
import socket
import http.server
import socketserver
import json
import ctypes
import webbrowser
import random
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Windows-specific imports
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False


class LocalPranks:
    """Pranks that run on the local computer (your own PC)"""
    
    @staticmethod
    def play_sound(sound_type: str = 'beep') -> Dict:
        """Play system sounds - NO external apps needed"""
        try:
            import winsound
            
            sounds = {
                'beep': lambda: winsound.Beep(1000, 200),
                'alert': lambda: winsound.Beep(2000, 500),
                'error': lambda: winsound.PlaySound("SystemHand", winsound.SND_ALIAS),
                'question': lambda: winsound.PlaySound("SystemQuestion", winsound.SND_ALIAS),
                'asterisk': lambda: winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS),
                'exclamation': lambda: winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS),
                'police': lambda: [winsound.Beep(f, 100) for f in [800, 1000, 800, 1000, 800, 1000]],
                'ufo': lambda: [winsound.Beep(f, 50) for f in range(200, 2000, 50)],
                'random': lambda: [winsound.Beep(random.randint(200, 3000), random.randint(50, 200)) for _ in range(10)],
                'alarm': lambda: [winsound.Beep(f, 150) for _ in range(5) for f in [600, 800]],
                'laugh': lambda: [winsound.Beep(f, 80) for f in [300, 350, 400, 350, 300, 400, 500]],
            }
            
            if sound_type in sounds:
                sounds[sound_type]()
                return {'success': True, 'sound': sound_type}
            
            return {'success': False, 'error': 'Unknown sound type'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def speak_text(text: str) -> Dict:
        """Use Windows text-to-speech - Built into Windows!"""
        try:
            # Escape quotes in text
            safe_text = text.replace('"', "'").replace('\n', ' ')
            ps_script = f'''
            Add-Type -AssemblyName System.Speech
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
            $synth.Speak("{safe_text}")
            '''
            
            subprocess.Popen(
                ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            return {'success': True, 'text': text}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def open_website(url: str) -> Dict:
        """Open a website in default browser"""
        try:
            webbrowser.open(url)
            return {'success': True, 'url': url}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def rickroll() -> Dict:
        """The classic rickroll!"""
        return LocalPranks.open_website('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
    
    @staticmethod
    def open_multiple_browsers(url: str, count: int = 10) -> Dict:
        """Open many browser windows"""
        try:
            for _ in range(min(count, 30)):  # Limit to 30
                webbrowser.open(url)
                time.sleep(0.15)
            return {'success': True, 'count': count, 'url': url}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def show_message_box(title: str, message: str, icon: str = 'error') -> Dict:
        """Show Windows message box - Built into Windows!"""
        try:
            icons = {
                'error': 0x10,      # MB_ICONERROR
                'warning': 0x30,    # MB_ICONWARNING
                'info': 0x40,       # MB_ICONINFORMATION
                'question': 0x20,   # MB_ICONQUESTION
            }
            icon_flag = icons.get(icon, 0x10)
            
            def show():
                ctypes.windll.user32.MessageBoxW(0, message, title, icon_flag)
            
            thread = threading.Thread(target=show)
            thread.start()
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def fake_virus_alert() -> Dict:
        """Show fake virus alert - Pure HTML, no apps needed!"""
        html = '''<!DOCTYPE html>
<html><head><title>Windows Defender Alert</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#1a1a2e;font-family:Segoe UI,sans-serif;color:#fff;min-height:100vh;display:flex;align-items:center;justify-content:center}
.container{background:#16213e;border:3px solid #e94560;border-radius:15px;padding:40px;max-width:600px;text-align:center;animation:shake 0.5s ease-in-out infinite}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-10px)}75%{transform:translateX(10px)}}
.icon{font-size:80px;margin-bottom:20px}
h1{color:#e94560;font-size:28px;margin-bottom:15px}
.threats{background:#0f0f23;padding:20px;border-radius:10px;margin:20px 0;text-align:left}
.threat{padding:8px 0;border-bottom:1px solid #333;display:flex;align-items:center;gap:10px}
.threat:last-child{border:none}
.threat-icon{color:#e94560}
p{color:#aaa;line-height:1.6;margin:15px 0}
.btn{background:#e94560;color:#fff;border:none;padding:15px 40px;font-size:18px;border-radius:8px;cursor:pointer;margin:10px;transition:all 0.3s}
.btn:hover{background:#ff6b6b;transform:scale(1.05)}
.btn-secondary{background:#333}
.fake{color:#666;font-size:12px;margin-top:30px}
</style></head>
<body>
<div class="container">
<div class="icon">🛡️⚠️</div>
<h1>WINDOWS DEFENDER - THREAT DETECTED!</h1>
<div class="threats">
<div class="threat"><span class="threat-icon">🦠</span> Trojan.Win32.GenericKD.46542381</div>
<div class="threat"><span class="threat-icon">🦠</span> Ransomware.WannaCry.variant</div>
<div class="threat"><span class="threat-icon">🦠</span> Spyware.Keylogger.PWS</div>
<div class="threat"><span class="threat-icon">🦠</span> Backdoor.RemoteAccess.RAT</div>
</div>
<p>Your computer has been compromised! Personal data, passwords, and banking information may be at risk.</p>
<p style="color:#e94560;font-weight:bold">Action required immediately!</p>
<button class="btn" onclick="alert('😂 GOTCHA! This was just a prank!\\n\\nYour PC is perfectly fine.')">🛡️ REMOVE THREATS NOW</button>
<button class="btn btn-secondary" onclick="alert('Nice try! But you should still click Remove Threats 😈')">Ignore Risk</button>
<p class="fake">(This is a prank - your computer is safe 😉)</p>
</div>
</body></html>'''
        
        return LocalPranks._open_html_prank(html, 'fake_virus')
    
    @staticmethod
    def fake_bsod() -> Dict:
        """Show fake Blue Screen of Death - Pure HTML!"""
        html = '''<!DOCTYPE html>
<html><head><title>:( Your PC ran into a problem</title>
<style>
*{margin:0;padding:0}
body{background:#0078d7;color:#fff;font-family:Segoe UI,sans-serif;height:100vh;padding:10%;overflow:hidden}
.sad{font-size:120px;margin-bottom:20px}
h1{font-size:24px;font-weight:300;margin-bottom:20px}
p{font-size:16px;font-weight:300;margin:10px 0;opacity:0.9}
.progress{margin:30px 0;font-size:18px}
.qr{display:flex;align-items:center;gap:20px;margin-top:40px;padding:20px;background:rgba(255,255,255,0.1);border-radius:5px}
.qr-code{width:100px;height:100px;background:#fff}
.small{font-size:12px;opacity:0.7}
#pct{font-weight:bold}
</style></head>
<body>
<div class="sad">:(</div>
<h1>Your PC ran into a problem and needs to restart.</h1>
<p>We're just collecting some error info, and then we'll restart for you.</p>
<p class="progress"><span id="pct">0</span>% complete</p>
<div class="qr">
<div class="qr-code" style="display:flex;align-items:center;justify-content:center;color:#000;font-size:10px">QR CODE</div>
<div>
<p class="small">For more information about this issue and possible fixes, visit:</p>
<p class="small">https://www.windows.com/stopcode</p>
<p style="margin-top:15px">Stop code: DRIVER_IRQL_NOT_LESS_OR_EQUAL</p>
<p class="small">What failed: ntoskrnl.exe</p>
</div>
</div>
<script>
let p=0;
setInterval(()=>{
if(p<99){p+=Math.random()*3;document.getElementById('pct').textContent=Math.min(99,Math.floor(p));}
else if(p>=99&&p<100){p=100;setTimeout(()=>{document.body.innerHTML='<div style="text-align:center;padding-top:30vh"><h1 style="font-size:48px">😂 GOTCHA!</h1><p style="font-size:24px;margin-top:20px">This was just a prank! Your PC is fine.</p><p style="margin-top:20px">Press F11 to exit fullscreen</p></div>';},2000);}
},500);
document.body.addEventListener('click',()=>document.documentElement.requestFullscreen?.());
</script>
</body></html>'''
        
        return LocalPranks._open_html_prank(html, 'fake_bsod')
    
    @staticmethod
    def fake_update() -> Dict:
        """Show fake Windows Update - Pure HTML!"""
        html = '''<!DOCTYPE html>
<html><head><title>Windows Update</title>
<style>
*{margin:0;padding:0}
body{background:#0078d4;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:Segoe UI Light,sans-serif;color:#fff}
.spinner{width:100px;height:100px;border:6px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
h1{margin-top:50px;font-weight:300;font-size:26px}
p{margin-top:15px;opacity:0.8;font-size:16px}
#pct{font-size:50px;font-weight:200;margin-top:30px}
.warning{position:fixed;bottom:30px;font-size:14px;opacity:0.6}
</style></head>
<body onclick="document.documentElement.requestFullscreen?.()">
<div class="spinner"></div>
<h1>Working on updates</h1>
<div id="pct">0%</div>
<p>Don't turn off your PC. This will take a while.</p>
<p>Your PC will restart several times.</p>
<p class="warning">This might take several minutes... or hours 😈</p>
<script>
let p=0;
setInterval(()=>{
if(p<95){
p+=Math.random()*0.5;
document.getElementById('pct').textContent=Math.floor(p)+'%';
}else if(p>=95&&p<100){
// Trolling: go backwards sometimes
if(Math.random()>0.7)p-=Math.random()*5;
p+=Math.random()*0.2;
document.getElementById('pct').textContent=Math.floor(Math.min(99,p))+'%';
}
},1000);
setTimeout(()=>{
document.body.innerHTML='<div style="text-align:center"><h1 style="font-size:60px">😂</h1><h2 style="font-size:30px;margin:20px">TROLLED!</h2><p>There was never an update. Press F11 to escape.</p></div>';
},60000);
</script>
</body></html>'''
        
        return LocalPranks._open_html_prank(html, 'fake_update')

    @staticmethod
    def matrix_screen() -> Dict:
        """Show Matrix rain effect - Pure HTML/JS!"""
        html = '''<!DOCTYPE html>
<html><head><title>Matrix</title>
<style>*{margin:0;padding:0}body{background:#000;overflow:hidden}canvas{display:block}</style>
</head><body>
<canvas id="c"></canvas>
<script>
const c=document.getElementById('c'),ctx=c.getContext('2d');
c.width=window.innerWidth;c.height=window.innerHeight;
const chars='アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン0123456789ABCDEF';
const fontSize=14,columns=c.width/fontSize,drops=[];
for(let i=0;i<columns;i++)drops[i]=Math.random()*-100;
function draw(){
ctx.fillStyle='rgba(0,0,0,0.05)';ctx.fillRect(0,0,c.width,c.height);
ctx.fillStyle='#0f0';ctx.font=fontSize+'px monospace';
for(let i=0;i<drops.length;i++){
const text=chars[Math.floor(Math.random()*chars.length)];
ctx.fillText(text,i*fontSize,drops[i]*fontSize);
if(drops[i]*fontSize>c.height&&Math.random()>0.975)drops[i]=0;
drops[i]++;
}}
setInterval(draw,33);
window.onresize=()=>{c.width=window.innerWidth;c.height=window.innerHeight};
document.body.onclick=()=>document.documentElement.requestFullscreen?.();
</script>
</body></html>'''
        
        return LocalPranks._open_html_prank(html, 'matrix')
    
    @staticmethod
    def jumpscare() -> Dict:
        """Jumpscare prank - Pure HTML!"""
        html = '''<!DOCTYPE html>
<html><head><title>Loading interesting content...</title>
<style>
*{margin:0;padding:0}
body{background:#111;color:#fff;font-family:Arial;display:flex;align-items:center;justify-content:center;height:100vh;cursor:none}
.loading{text-align:center}
.spinner{width:50px;height:50px;border:4px solid #333;border-top-color:#0af;border-radius:50%;animation:spin 1s linear infinite;margin:20px auto}
@keyframes spin{to{transform:rotate(360deg)}}
.scare{display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:#000;z-index:999}
.scare img{width:100%;height:100%;object-fit:cover}
.scare-text{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-size:150px;animation:pulse 0.1s infinite}
@keyframes pulse{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-50%) scale(1.2)}}
</style></head>
<body>
<div class="loading" id="loader">
<div class="spinner"></div>
<p>Loading content...</p>
<p style="font-size:12px;color:#666;margin-top:20px">Please wait...</p>
</div>
<div class="scare" id="scare">
<div class="scare-text">👻💀👻</div>
</div>
<script>
setTimeout(()=>{
document.getElementById('loader').style.display='none';
const scare=document.getElementById('scare');
scare.style.display='block';
// Play beep sound
try{
const ctx=new(window.AudioContext||window.webkitAudioContext)();
const osc=ctx.createOscillator();
osc.type='square';osc.frequency.value=200;
osc.connect(ctx.destination);osc.start();
setTimeout(()=>osc.stop(),500);
}catch(e){}
setTimeout(()=>{
document.body.innerHTML='<div style="text-align:center;padding-top:40vh;font-size:24px"><p>😈 BOO! Got you!</p><p style="margin-top:20px;font-size:16px;color:#888">Just a prank! Close this tab.</p></div>';
},2000);
},3000+Math.random()*2000);
</script>
</body></html>'''
        
        return LocalPranks._open_html_prank(html, 'jumpscare')
    
    @staticmethod
    def fake_hack() -> Dict:
        """Fake hacking screen - Pure HTML/JS!"""
        html = '''<!DOCTYPE html>
<html><head><title>ACCESS GRANTED</title>
<style>
*{margin:0;padding:0}
body{background:#0a0a0a;color:#0f0;font-family:'Courier New',monospace;padding:20px;overflow-x:hidden}
pre{font-size:12px;line-height:1.4;white-space:pre-wrap}
.cursor{animation:blink 0.5s infinite}
@keyframes blink{50%{opacity:0}}
.red{color:#f00}
.yellow{color:#ff0}
.cyan{color:#0ff}
</style></head>
<body>
<pre id="terminal"></pre>
<script>
const msgs=[
'[*] Initializing connection...',
'[*] Target acquired: '+navigator.userAgent.substring(0,50)+'...',
'[+] Bypassing firewall... <span class="yellow">SUCCESS</span>',
'[+] Exploiting vulnerability CVE-2024-1337...',
'[+] Injecting payload... <span class="yellow">DONE</span>',
'[*] Establishing reverse shell...',
'<span class="cyan">[!] CONNECTION ESTABLISHED</span>',
'',
'[+] Dumping browser cookies... 847 cookies found',
'[+] Extracting saved passwords...',
'    - Google: ********',
'    - Facebook: ********', 
'    - Instagram: ********',
'    - Bank Account: ********',
'[+] <span class="red">23 passwords extracted!</span>',
'',
'[+] Accessing webcam...',
'[+] <span class="red">WEBCAM ACTIVATED - Recording...</span>',
'',
'[+] Scanning files...',
'    - Documents: 1,247 files',
'    - Photos: 3,891 files',
'    - Downloads: 567 files',
'[+] <span class="yellow">Uploading to remote server...</span>',
'',
'████████████████████████████ 100%',
'',
'<span class="red">[!] ALL YOUR DATA HAS BEEN COMPROMISED!</span>',
'',
'','','',
'<span style="color:#888">Just kidding! 😂</span>',
'<span style="color:#888">This is only a prank. Your PC is safe!</span>',
'<span style="color:#888">Close this tab to continue.</span>',
];
let i=0,t=document.getElementById('terminal');
function type(){
if(i<msgs.length){
t.innerHTML+=msgs[i]+'\\n';
t.innerHTML=t.innerHTML.replace(/<span class="cursor">_<\\/span>/g,'');
t.innerHTML+='<span class="cursor">_</span>';
i++;
window.scrollTo(0,document.body.scrollHeight);
setTimeout(type,300+Math.random()*400);
}
}
type();
document.body.onclick=()=>document.documentElement.requestFullscreen?.();
</script>
</body></html>'''
        
        return LocalPranks._open_html_prank(html, 'fake_hack')
    
    @staticmethod
    def cracked_screen() -> Dict:
        """Cracked screen effect - Pure HTML/CSS!"""
        html = '''<!DOCTYPE html>
<html><head><title>CRACK!</title>
<style>
*{margin:0;padding:0}
body{background:#000;height:100vh;position:relative;overflow:hidden}
.crack{position:absolute;top:0;left:0;width:100%;height:100%;background:linear-gradient(45deg,transparent 40%,rgba(255,255,255,0.1) 45%,transparent 50%),
linear-gradient(-45deg,transparent 40%,rgba(255,255,255,0.1) 45%,transparent 50%),
linear-gradient(135deg,transparent 40%,rgba(255,255,255,0.05) 45%,transparent 50%)}
.cracks{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%)}
.cracks svg{width:100vw;height:100vh}
.text{position:absolute;bottom:15%;left:50%;transform:translateX(-50%);text-align:center;color:#fff;font-family:Arial}
.text h1{font-size:48px;margin-bottom:20px}
.text p{color:#888;font-size:18px}
.glass{position:absolute;top:0;left:0;width:100%;height:100%;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(255,255,255,0.03) 2px,rgba(255,255,255,0.03) 4px)}
</style></head>
<body>
<div class="crack"></div>
<div class="glass"></div>
<svg style="position:absolute;width:100%;height:100%" viewBox="0 0 100 100" preserveAspectRatio="none">
<path d="M50 0 L52 25 L60 30 L55 45 L70 50 L50 48 L58 65 L45 55 L30 80 L48 52 L20 45 L45 42 L35 25 L50 38 L48 15 Z" fill="none" stroke="rgba(255,255,255,0.5)" stroke-width="0.2"/>
<path d="M50 0 L48 20 L40 35 L30 50 L45 55 L40 70 L50 100" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="0.15"/>
<path d="M50 0 L55 30 L65 45 L75 60 L60 65 L70 85" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="0.15"/>
</svg>
<div class="text">
<h1>💥 CRACK! 💥</h1>
<p>Your screen just cracked!</p>
<p style="margin-top:30px;font-size:14px;color:#666">(Just kidding, it's a prank 😄)</p>
</div>
<script>
try{
const ctx=new(window.AudioContext||window.webkitAudioContext)();
const osc=ctx.createOscillator();const gain=ctx.createGain();
osc.type='sawtooth';osc.frequency.value=100;
gain.gain.value=0.3;gain.gain.exponentialRampToValueAtTime(0.01,ctx.currentTime+0.3);
osc.connect(gain);gain.connect(ctx.destination);
osc.start();setTimeout(()=>osc.stop(),300);
}catch(e){}
</script>
</body></html>'''
        
        return LocalPranks._open_html_prank(html, 'cracked')
    
    @staticmethod
    def fake_format() -> Dict:
        """Fake disk format dialog - Pure HTML!"""
        html = '''<!DOCTYPE html>
<html><head><title>Format Disk</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#f0f0f0;font-family:Segoe UI,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh}
.window{background:#fff;border-radius:8px;box-shadow:0 10px 40px rgba(0,0,0,0.2);width:450px;overflow:hidden}
.titlebar{background:linear-gradient(to right,#0078d4,#00a2ed);color:#fff;padding:12px 15px;display:flex;align-items:center;gap:10px}
.titlebar span{font-size:14px}
.content{padding:25px}
.icon-row{display:flex;gap:15px;margin-bottom:20px}
.icon{font-size:48px}
.warning{color:#333}
.warning strong{color:#c00}
.progress-container{background:#e0e0e0;border-radius:10px;height:25px;margin:25px 0;overflow:hidden}
.progress-bar{background:linear-gradient(to right,#c00,#f00);height:100%;width:0;transition:width 0.3s}
.status{text-align:center;margin:15px 0;font-size:14px}
.buttons{display:flex;justify-content:flex-end;gap:10px;padding:15px;border-top:1px solid #e0e0e0}
.btn{padding:10px 25px;border-radius:4px;cursor:pointer;font-size:14px}
.btn-cancel{background:#f0f0f0;border:1px solid #ccc;color:#333}
</style></head>
<body>
<div class="window">
<div class="titlebar"><span>⚠️</span><span>Format Local Disk (C:)</span></div>
<div class="content">
<div class="icon-row">
<div class="icon">💾</div>
<div class="warning">
<p><strong>WARNING: Formatting will erase ALL data!</strong></p>
<p style="margin-top:10px;color:#666">This action cannot be undone. All files, programs, and Windows will be permanently deleted.</p>
</div>
</div>
<div class="progress-container"><div class="progress-bar" id="progress"></div></div>
<p class="status" id="status">Formatting disk C: ... Please wait.</p>
</div>
<div class="buttons">
<button class="btn btn-cancel" onclick="alert('Too late! 😈\\n\\n...Just kidding! Your disk is safe.')">Cancel</button>
</div>
</div>
<script>
let p=0;
const bar=document.getElementById('progress'),status=document.getElementById('status');
const interval=setInterval(()=>{
p+=Math.random()*3;
bar.style.width=Math.min(p,100)+'%';
if(p>=100){
clearInterval(interval);
status.innerHTML='<span style="color:green">✓ Just kidding! Your disk is perfectly safe! 😄</span>';
bar.style.background='linear-gradient(to right,#0a0,#0f0)';
}
},200);
</script>
</body></html>'''
        
        return LocalPranks._open_html_prank(html, 'fake_format')
    
    @staticmethod
    def flip_screen() -> Dict:
        """Upside down webpage - Pure HTML/CSS!"""
        html = '''<!DOCTYPE html>
<html><head><title>Totally Normal Page</title>
<style>
*{margin:0;padding:0}
body{background:#f5f5f5;min-height:100vh;transform:rotate(180deg);font-family:Arial}
.container{max-width:800px;margin:50px auto;padding:30px;background:#fff;border-radius:10px;box-shadow:0 2px 10px rgba(0,0,0,0.1)}
h1{color:#333;margin-bottom:20px}
p{color:#666;line-height:1.8;margin-bottom:15px}
.hint{background:#fffbcc;padding:15px;border-radius:5px;margin-top:30px;border-left:4px solid #f0c000}
</style></head>
<body>
<div class="container">
<h1>🙃 Welcome to a Totally Normal Website!</h1>
<p>Nothing to see here, just a regular webpage with regular content.</p>
<p>Everything is perfectly fine and definitely not upside down.</p>
<p>Why would you even think something is wrong? This is how all websites look!</p>
<div class="hint">
<strong>Hint:</strong> If you think something looks weird, it's probably just your monitor. Have you tried turning it upside down? 😏
</div>
<p style="margin-top:30px;color:#999;font-size:14px">(Press Ctrl+Alt+↓ to fix... or just close this tab 😄)</p>
</div>
</body></html>'''
        
        return LocalPranks._open_html_prank(html, 'flip_screen')
    
    @staticmethod
    def _open_html_prank(html_content: str, name: str) -> Dict:
        """Save HTML to temp file and open in browser"""
        try:
            import tempfile
            
            # Create temp HTML file
            temp_dir = tempfile.gettempdir()
            file_path = os.path.join(temp_dir, f'prank_{name}.html')
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open in browser
            webbrowser.open(f'file:///{file_path}')
            
            return {'success': True, 'prank': name}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def caps_lock_toggle(times: int = 10) -> Dict:
        """Toggle caps lock rapidly"""
        try:
            ps_script = f'''
            $wsh = New-Object -ComObject WScript.Shell
            for ($i = 0; $i -lt {min(times, 20)}; $i++) {{
                $wsh.SendKeys("{{CAPSLOCK}}")
                Start-Sleep -Milliseconds 150
            }}
            '''
            subprocess.Popen(['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                           creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True, 'times': times}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def minimize_all_windows() -> Dict:
        """Minimize all windows"""
        try:
            subprocess.run(['powershell', '-WindowStyle', 'Hidden', '-Command', 
                '(New-Object -ComObject Shell.Application).MinimizeAll()'],
                creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def eject_cd_drive() -> Dict:
        """Eject CD/DVD drive"""
        try:
            ps_script = '''
            (New-Object -ComObject WMPlayer.OCX).cdromCollection.Item(0).Eject()
            '''
            subprocess.run(['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                          creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def crazy_mouse(duration: int = 5) -> Dict:
        """Move mouse randomly"""
        try:
            ps_script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $random = New-Object System.Random
            $endTime = (Get-Date).AddSeconds({min(duration, 15)})
            while ((Get-Date) -lt $endTime) {{
                $x = $random.Next(0, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width)
                $y = $random.Next(0, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height)
                [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x, $y)
                Start-Sleep -Milliseconds 50
            }}
            '''
            subprocess.Popen(['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                           creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True, 'duration': duration}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def fake_shutdown(seconds: int = 30) -> Dict:
        """Show fake shutdown warning (cancellable with shutdown /a)"""
        try:
            subprocess.run(
                ['shutdown', '/s', '/t', str(min(seconds, 120)), '/c', 
                 'Windows will shutdown. Save your work! (Prank - cancel with: shutdown /a)'],
                capture_output=True
            )
            return {'success': True, 'seconds': seconds, 'cancel': 'shutdown /a'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def cancel_shutdown() -> Dict:
        """Cancel shutdown"""
        try:
            subprocess.run(['shutdown', '/a'], capture_output=True)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def set_volume(level: int = 100) -> Dict:
        """Set system volume"""
        try:
            ps_script = f'''
            $obj = New-Object -ComObject WScript.Shell
            1..50 | ForEach-Object {{ $obj.SendKeys([char]174) }}
            1..{level // 2} | ForEach-Object {{ $obj.SendKeys([char]175) }}
            '''
            subprocess.run(['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                          creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True, 'level': level}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def toggle_mute() -> Dict:
        """Toggle mute"""
        try:
            ps_script = '''
            $obj = New-Object -ComObject WScript.Shell
            $obj.SendKeys([char]173)
            '''
            subprocess.run(['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                          creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def popup_bomb(count: int = 5, message: str = "Alert!", title: str = "Warning") -> Dict:
        """Show multiple popup messages"""
        try:
            def show_popups():
                for i in range(min(count, 10)):
                    ctypes.windll.user32.MessageBoxW(0, f"{message}\n\n(Popup {i+1}/{count})", title, 0x30)
                    time.sleep(0.3)
            
            thread = threading.Thread(target=show_popups)
            thread.start()
            return {'success': True, 'count': count}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod  
    def flash_keyboard_lights() -> Dict:
        """Flash keyboard LEDs (Caps, Num, Scroll Lock)"""
        try:
            ps_script = '''
            $wsh = New-Object -ComObject WScript.Shell
            for ($i = 0; $i -lt 10; $i++) {
                $wsh.SendKeys("{CAPSLOCK}{NUMLOCK}{SCROLLLOCK}")
                Start-Sleep -Milliseconds 100
            }
            # Reset
            $wsh.SendKeys("{CAPSLOCK}{NUMLOCK}{SCROLLLOCK}")
            '''
            subprocess.Popen(['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
                           creationflags=subprocess.CREATE_NO_WINDOW)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def creepy_whisper() -> Dict:
        """Speak creepy message"""
        whispers = [
            "I can see you",
            "I am watching",
            "Behind you",
            "Don't look now",
            "I know what you did",
            "You are not alone",
        ]
        return LocalPranks.speak_text(random.choice(whispers))
    
    @staticmethod
    def random_website() -> Dict:
        """Open random funny/annoying website"""
        sites = [
            'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # Rickroll
            'https://theuselessweb.com/',
            'https://pointerpointer.com/',
            'https://www.staggeringbeauty.com/',
            'https://www.fallingfalling.com/',
        ]
        return LocalPranks.open_website(random.choice(sites))


class NetworkPranks:
    """Network-based pranks"""
    
    HOSTS_FILE = r'C:\Windows\System32\drivers\etc\hosts'
    
    @staticmethod
    def block_website(domain: str) -> Dict:
        """Block website via hosts file (requires admin)"""
        try:
            # Backup first
            backup = NetworkPranks.HOSTS_FILE + '.backup'
            if not os.path.exists(backup):
                shutil.copy(NetworkPranks.HOSTS_FILE, backup)
            
            entry = f"\n127.0.0.1 {domain}\n127.0.0.1 www.{domain}"
            
            with open(NetworkPranks.HOSTS_FILE, 'a') as f:
                f.write(entry)
            
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            return {'success': True, 'blocked': domain}
        except PermissionError:
            return {'success': False, 'error': 'Requires administrator'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def unblock_website(domain: str) -> Dict:
        """Unblock website"""
        try:
            with open(NetworkPranks.HOSTS_FILE, 'r') as f:
                lines = f.readlines()
            
            new_lines = [l for l in lines if domain not in l]
            
            with open(NetworkPranks.HOSTS_FILE, 'w') as f:
                f.writelines(new_lines)
            
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
            return {'success': True, 'unblocked': domain}
        except PermissionError:
            return {'success': False, 'error': 'Requires administrator'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def disconnect_wifi() -> Dict:
        """Disconnect from WiFi"""
        try:
            result = subprocess.run(['netsh', 'wlan', 'disconnect'], capture_output=True, text=True)
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}


class WebPrankServer:
    """HTTP server for remote pranks"""
    
    PRANK_PAGES = {
        'rickroll': '''<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0;url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"></head><body>Redirecting...</body></html>''',
        
        'bsod': '''<!DOCTYPE html>
<html><head><title>:(</title>
<style>*{margin:0;padding:0}body{background:#0078d7;color:#fff;font-family:Segoe UI;height:100vh;padding:10%}
.sad{font-size:120px}.progress{margin-top:30px}</style></head>
<body onclick="document.documentElement.requestFullscreen()">
<div class="sad">:(</div>
<h1 style="margin:20px 0">Your PC ran into a problem.</h1>
<p>We're collecting error info...</p>
<p class="progress" id="p">0% complete</p>
<script>let p=0;setInterval(()=>{if(p<100){p+=Math.random()*2;document.getElementById('p').textContent=Math.floor(p)+'% complete'}},500)</script>
</body></html>''',
        
        'hacked': '''<!DOCTYPE html>
<html><head><title>HACKED</title>
<style>*{margin:0;padding:0}body{background:#000;color:#0f0;font-family:monospace;padding:20px}</style></head>
<body><pre id="t"></pre>
<script>
const m=['[*] Connection established...','[+] Bypassing security...','[+] Accessing data...','[!] YOU HAVE BEEN HACKED!','','(Just kidding 😄)'];
let i=0,t=document.getElementById('t');
setInterval(()=>{if(i<m.length){t.textContent+=m[i++]+'\\n'}},800);
</script></body></html>''',
        
        'jumpscare': '''<!DOCTYPE html>
<html><head><title>Loading...</title>
<style>*{margin:0}body{background:#111;color:#fff;font-family:Arial;height:100vh;display:flex;align-items:center;justify-content:center}
.scare{display:none;font-size:200px;animation:shake 0.1s infinite}
@keyframes shake{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}</style></head>
<body>
<div id="load">Loading...</div>
<div class="scare" id="scare">👻💀</div>
<script>
setTimeout(()=>{
document.getElementById('load').style.display='none';
document.getElementById('scare').style.display='block';
try{const c=new AudioContext(),o=c.createOscillator();o.frequency.value=200;o.connect(c.destination);o.start();setTimeout(()=>o.stop(),500)}catch(e){}
setTimeout(()=>{document.body.innerHTML='<h1 style="text-align:center;padding-top:40vh">😈 BOO!</h1>'},2000);
},3000);</script></body></html>'''
    }
    
    def __init__(self, port: int = 8888):
        self.port = port
        self.server = None
        self.thread = None
        self.is_running = False
        self.mode = 'rickroll'
    
    def start(self) -> bool:
        if self.is_running:
            return True
        
        server_self = self
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                page = server_self.PRANK_PAGES.get(server_self.mode, server_self.PRANK_PAGES['rickroll'])
                self.wfile.write(page.encode())
            
            def log_message(self, format, *args):
                pass  # Suppress logs
        
        try:
            self.server = socketserver.TCPServer(('0.0.0.0', self.port), Handler)
            self.server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            def serve():
                self.server.serve_forever()
            
            self.thread = threading.Thread(target=serve, daemon=True)
            self.thread.start()
            self.is_running = True
            return True
        except Exception as e:
            print(f"Server error: {e}")
            return False
    
    def stop(self):
        if self.server:
            self.server.shutdown()
            self.is_running = False
    
    def set_mode(self, mode: str) -> bool:
        if mode in self.PRANK_PAGES:
            self.mode = mode
            return True
        return False


class PrankManager:
    """Main prank manager"""
    
    def __init__(self):
        self.prank_server = WebPrankServer()
        self.history = []
    
    def get_available_pranks(self) -> List[Dict]:
        """Get all pranks organized by category"""
        return [
            # 😈 CLASSIC TROLLS
            {'id': 'rickroll', 'name': 'Rickroll', 'description': 'Never gonna give you up! 🎵', 
             'category': 'classic', 'icon': 'music', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'jumpscare', 'name': 'Jumpscare', 'description': 'Susto inesperado 👻', 
             'category': 'classic', 'icon': 'ghost', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'random_site', 'name': 'Random Site', 'description': 'Abre sitio web aleatorio raro', 
             'category': 'classic', 'icon': 'shuffle', 'danger_level': 'safe', 'requires_admin': False},
            
            # 🖥️ VISUAL
            {'id': 'fake_virus', 'name': 'Fake Virus Alert', 'description': 'Alerta de virus muy convincente', 
             'category': 'visual', 'icon': 'bug', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'fake_bsod', 'name': 'Fake BSOD', 'description': 'Pantalla azul de la muerte', 
             'category': 'visual', 'icon': 'monitor_x', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'fake_update', 'name': 'Fake Update', 'description': 'Windows Update eterno', 
             'category': 'visual', 'icon': 'refresh', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'matrix', 'name': 'Matrix Screen', 'description': 'Efecto Matrix', 
             'category': 'visual', 'icon': 'binary', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'fake_hack', 'name': 'Fake Hack', 'description': 'Pantalla de "hackeado"', 
             'category': 'visual', 'icon': 'skull', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'cracked', 'name': 'Cracked Screen', 'description': 'Pantalla rota', 
             'category': 'visual', 'icon': 'smartphone', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'fake_format', 'name': 'Fake Format', 'description': 'Formateo de disco falso', 
             'category': 'visual', 'icon': 'harddisk', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'flip_screen', 'name': 'Flip Screen', 'description': 'Página al revés', 
             'category': 'visual', 'icon': 'rotate', 'danger_level': 'safe', 'requires_admin': False},
            
            # 🔊 AUDIO
            {'id': 'speak', 'name': 'Text to Speech', 'description': 'Tu PC habla', 
             'category': 'audio', 'icon': 'speech', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'sound', 'name': 'Sound Effects', 'description': 'Sonidos variados', 
             'category': 'audio', 'icon': 'volume', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'volume_max', 'name': 'Max Volume', 'description': 'Volumen al máximo', 
             'category': 'audio', 'icon': 'volume_up', 'danger_level': 'medium', 'requires_admin': False},
            {'id': 'mute', 'name': 'Toggle Mute', 'description': 'Mute on/off', 
             'category': 'audio', 'icon': 'volume_off', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'creepy', 'name': 'Creepy Whisper', 'description': 'Susurros escalofriantes', 
             'category': 'audio', 'icon': 'ear', 'danger_level': 'safe', 'requires_admin': False},
            
            # 🖱️ INPUT
            {'id': 'crazy_mouse', 'name': 'Crazy Mouse', 'description': 'Mouse loco', 
             'category': 'input', 'icon': 'mouse', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'caps_lock', 'name': 'Caps Lock Spam', 'description': 'Caps lock spam', 
             'category': 'input', 'icon': 'keyboard', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'flash_keys', 'name': 'Flash Keyboard', 'description': 'LEDs parpadean', 
             'category': 'input', 'icon': 'lightbulb', 'danger_level': 'safe', 'requires_admin': False},
            
            # 💣 ANNOYING
            {'id': 'browser_bomb', 'name': 'Browser Bomb', 'description': 'Muchas ventanas', 
             'category': 'annoying', 'icon': 'bomb', 'danger_level': 'medium', 'requires_admin': False},
            {'id': 'popup_bomb', 'name': 'Popup Bomb', 'description': 'Muchos popups', 
             'category': 'annoying', 'icon': 'messages', 'danger_level': 'medium', 'requires_admin': False},
            {'id': 'minimize_all', 'name': 'Minimize All', 'description': 'Minimiza todo', 
             'category': 'annoying', 'icon': 'minimize', 'danger_level': 'safe', 'requires_admin': False},
            
            # ⚠️ FAKE ERRORS
            {'id': 'fake_error', 'name': 'Fake Error', 'description': 'Error de Windows', 
             'category': 'fake', 'icon': 'alert', 'danger_level': 'safe', 'requires_admin': False},
            {'id': 'fake_shutdown', 'name': 'Fake Shutdown', 'description': 'Apagado falso', 
             'category': 'fake', 'icon': 'power', 'danger_level': 'medium', 'requires_admin': False},
            
            # 💿 HARDWARE
            {'id': 'eject_cd', 'name': 'Eject CD', 'description': 'Abre bandeja CD', 
             'category': 'hardware', 'icon': 'disc', 'danger_level': 'safe', 'requires_admin': False},
            
            # 🌐 NETWORK
            {'id': 'block_site', 'name': 'Block Website', 'description': 'Bloquea sitio', 
             'category': 'network', 'icon': 'ban', 'danger_level': 'medium', 'requires_admin': True},
            {'id': 'disconnect_wifi', 'name': 'Disconnect WiFi', 'description': 'Desconecta WiFi', 
             'category': 'network', 'icon': 'wifi_off', 'danger_level': 'medium', 'requires_admin': False},
            {'id': 'prank_server', 'name': 'Prank Server', 'description': 'Servidor de pranks', 
             'category': 'network', 'icon': 'server', 'danger_level': 'safe', 'requires_admin': False},
        ]
    
    def execute_prank(self, prank_id: str, options: Dict = None) -> Dict:
        """Execute a prank"""
        options = options or {}
        result = {'prank_id': prank_id, 'timestamp': datetime.now().isoformat()}
        
        try:
            # Classic
            if prank_id == 'rickroll':
                result.update(LocalPranks.rickroll())
            elif prank_id == 'jumpscare':
                result.update(LocalPranks.jumpscare())
            elif prank_id == 'random_site':
                result.update(LocalPranks.random_website())
            
            # Visual
            elif prank_id == 'fake_virus':
                result.update(LocalPranks.fake_virus_alert())
            elif prank_id == 'fake_bsod':
                result.update(LocalPranks.fake_bsod())
            elif prank_id == 'fake_update':
                result.update(LocalPranks.fake_update())
            elif prank_id == 'matrix':
                result.update(LocalPranks.matrix_screen())
            elif prank_id == 'fake_hack':
                result.update(LocalPranks.fake_hack())
            elif prank_id == 'cracked':
                result.update(LocalPranks.cracked_screen())
            elif prank_id == 'fake_format':
                result.update(LocalPranks.fake_format())
            elif prank_id == 'flip_screen':
                result.update(LocalPranks.flip_screen())
            
            # Audio
            elif prank_id == 'speak':
                text = options.get('text', '¡Hola! Soy tu computadora.')
                result.update(LocalPranks.speak_text(text))
            elif prank_id == 'sound':
                sound = options.get('sound', 'beep')
                result.update(LocalPranks.play_sound(sound))
            elif prank_id == 'volume_max':
                result.update(LocalPranks.set_volume(100))
            elif prank_id == 'mute':
                result.update(LocalPranks.toggle_mute())
            elif prank_id == 'creepy':
                result.update(LocalPranks.creepy_whisper())
            
            # Input
            elif prank_id == 'crazy_mouse':
                duration = options.get('duration', 5)
                result.update(LocalPranks.crazy_mouse(duration))
            elif prank_id == 'caps_lock':
                times = options.get('times', 10)
                result.update(LocalPranks.caps_lock_toggle(times))
            elif prank_id == 'flash_keys':
                result.update(LocalPranks.flash_keyboard_lights())
            
            # Annoying
            elif prank_id == 'browser_bomb':
                count = options.get('count', 10)
                url = options.get('url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')
                result.update(LocalPranks.open_multiple_browsers(url, count))
            elif prank_id == 'popup_bomb':
                count = options.get('count', 5)
                result.update(LocalPranks.popup_bomb(count))
            elif prank_id == 'minimize_all':
                result.update(LocalPranks.minimize_all_windows())
            
            # Fake errors
            elif prank_id == 'fake_error':
                title = options.get('title', 'Error del Sistema')
                message = options.get('message', 'Ha ocurrido un error crítico.')
                result.update(LocalPranks.show_message_box(title, message, 'error'))
            elif prank_id == 'fake_shutdown':
                seconds = options.get('seconds', 60)
                result.update(LocalPranks.fake_shutdown(seconds))
            elif prank_id == 'cancel_shutdown':
                result.update(LocalPranks.cancel_shutdown())
            
            # Hardware
            elif prank_id == 'eject_cd':
                result.update(LocalPranks.eject_cd_drive())
            
            # Network
            elif prank_id == 'block_site':
                domain = options.get('domain')
                if domain:
                    result.update(NetworkPranks.block_website(domain))
                else:
                    result['success'] = False
                    result['error'] = 'Domain required'
            elif prank_id == 'unblock_site':
                domain = options.get('domain')
                if domain:
                    result.update(NetworkPranks.unblock_website(domain))
                else:
                    result['success'] = False
                    result['error'] = 'Domain required'
            elif prank_id == 'disconnect_wifi':
                result.update(NetworkPranks.disconnect_wifi())
            elif prank_id == 'prank_server':
                action = options.get('action', 'start')
                mode = options.get('mode', 'rickroll')
                
                if action == 'start':
                    self.prank_server.set_mode(mode)
                    success = self.prank_server.start()
                    result['success'] = success
                    result['port'] = self.prank_server.port
                    result['mode'] = mode
                    result['url'] = f'http://TU_IP:{self.prank_server.port}'
                elif action == 'stop':
                    self.prank_server.stop()
                    result['success'] = True
            
            else:
                result['success'] = False
                result['error'] = f'Unknown prank: {prank_id}'
            
            # Log
            self.history.append({
                'prank_id': prank_id,
                'options': options,
                'result': result.get('success', False),
                'timestamp': result['timestamp']
            })
            
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def get_active_pranks(self) -> List[Dict]:
        """Get active pranks"""
        active = []
        if self.prank_server.is_running:
            active.append({
                'id': 'prank_server',
                'mode': self.prank_server.mode,
                'port': self.prank_server.port
            })
        return active
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get prank history"""
        return self.history[-limit:]
    
    def stop_all(self):
        """Stop all active pranks"""
        self.prank_server.stop()
        LocalPranks.cancel_shutdown()


if __name__ == "__main__":
    manager = PrankManager()
    print(f"Available pranks: {len(manager.get_available_pranks())}")
    for p in manager.get_available_pranks():
        print(f"  [{p['category']}] {p['name']}")
