"""
Cyber Command Center - WiFi Audit API Routes
"""
from flask import Blueprint, jsonify, request
from core.wifi_audit import HandshakeCapture, PasswordCracker, WPSAttack
from core.deauth import WiFiDeauth, WiFiScanner
from database.models import get_session, WiFiNetwork
from datetime import datetime

wifi_audit_bp = Blueprint('wifi_audit', __name__, url_prefix='/api/v1/wifi-audit')

# Initialize components
handshake_capture = HandshakeCapture()
password_cracker = PasswordCracker()
wifi_deauth = WiFiDeauth()

# ============================================
# Requirements Check
# ============================================

@wifi_audit_bp.route('/requirements')
def check_requirements():
    """Check system requirements for WiFi auditing"""
    capture_reqs = handshake_capture.check_requirements()
    deauth_reqs = wifi_deauth.check_requirements()
    
    return jsonify({
        'capture': capture_reqs,
        'deauth': deauth_reqs,
        'interfaces': wifi_deauth.get_interfaces(),
        'wordlists': password_cracker.get_wordlists()
    })

# ============================================
# Network Scanning
# ============================================

@wifi_audit_bp.route('/scan')
def scan_wifi():
    """Scan for WiFi networks"""
    scanner = WiFiScanner()
    networks = scanner.scan_networks()
    
    # Save to database
    session = get_session()
    try:
        for net in networks:
            bssid = net.get('bssid')
            if not bssid:
                continue
            
            wifi = session.query(WiFiNetwork).filter_by(bssid=bssid).first()
            
            if wifi:
                wifi.ssid = net.get('ssid') or wifi.ssid
                wifi.channel = net.get('channel') or wifi.channel
                wifi.signal_strength = net.get('signal') or wifi.signal_strength
                wifi.encryption = net.get('encryption') or wifi.encryption
                wifi.last_seen = datetime.utcnow()
            else:
                wifi = WiFiNetwork(
                    bssid=bssid,
                    ssid=net.get('ssid'),
                    channel=net.get('channel'),
                    signal_strength=net.get('signal'),
                    encryption=net.get('encryption'),
                    cipher=net.get('cipher')
                )
                session.add(wifi)
        
        session.commit()
    finally:
        session.close()
    
    return jsonify({
        'networks': networks,
        'count': len(networks)
    })

@wifi_audit_bp.route('/networks')
def get_saved_networks():
    """Get saved WiFi networks from database"""
    session = get_session()
    try:
        networks = session.query(WiFiNetwork).all()
        return jsonify([n.to_dict() for n in networks])
    finally:
        session.close()

# ============================================
# Handshake Capture
# ============================================

@wifi_audit_bp.route('/capture/start', methods=['POST'])
def start_capture():
    """Start handshake capture"""
    data = request.json
    
    target_bssid = data.get('bssid')
    channel = data.get('channel')
    timeout = data.get('timeout', 300)
    
    if not target_bssid or not channel:
        return jsonify({'error': 'BSSID and channel required'}), 400
    
    try:
        success = handshake_capture.start_capture(
            target_bssid=target_bssid,
            channel=channel,
            timeout=timeout
        )
        
        return jsonify({
            'success': success,
            'message': 'Capture started' if success else 'Capture already running'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wifi_audit_bp.route('/capture/stop', methods=['POST'])
def stop_capture():
    """Stop handshake capture"""
    result = handshake_capture.stop_capture()
    
    # Update database if handshake was captured
    if result.get('handshake_complete'):
        session = get_session()
        try:
            bssid = result.get('target_bssid')
            wifi = session.query(WiFiNetwork).filter_by(bssid=bssid).first()
            if wifi:
                wifi.handshake_captured = True
                wifi.handshake_path = result.get('output_file')
                session.commit()
        finally:
            session.close()
    
    return jsonify(result)

@wifi_audit_bp.route('/capture/status')
def capture_status():
    """Get current capture status - returns only JSON-serializable fields."""
    if not handshake_capture.is_capturing:
        return jsonify({'is_capturing': False, 'current': None})

    cap = handshake_capture.current_capture
    # Build a safe, serializable snapshot (Scapy Packet objects are NOT serializable)
    serializable = {
        'target_bssid': cap.get('target_bssid'),
        'channel': cap.get('channel'),
        'eapol_count': cap.get('eapol_count', 0),
        # Keys of eapol_messages dict = ['M1', 'M2', ...] - always strings
        'eapol_messages': sorted(cap.get('eapol_messages', {}).keys()),
        'handshake_complete': cap.get('handshake_complete', False),
        'handshake_messages': cap.get('handshake_messages', []),
        'packets_captured': len(cap.get('packets', [])),
        'output_file': cap.get('output_file'),
        'start_time': cap.get('start_time').isoformat() if cap.get('start_time') else None,
    }
    return jsonify({'is_capturing': True, 'current': serializable})

@wifi_audit_bp.route('/capture/deauth', methods=['POST'])
def send_deauth_for_capture():
    """Send deauth packets to force handshake"""
    data = request.json
    
    target_bssid = data.get('bssid')
    client_mac = data.get('client_mac', 'ff:ff:ff:ff:ff:ff')
    count = data.get('count', 5)
    
    if not target_bssid:
        return jsonify({'error': 'BSSID required'}), 400
    
    try:
        success = handshake_capture.send_deauth_for_handshake(
            target_bssid=target_bssid,
            client_mac=client_mac,
            count=count
        )
        
        return jsonify({
            'success': success,
            'packets_sent': count if success else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# Password Cracking
# ============================================

@wifi_audit_bp.route('/crack/wordlists')
def get_wordlists():
    """Get available wordlists"""
    return jsonify(password_cracker.get_wordlists())

@wifi_audit_bp.route('/crack/wordlists/download', methods=['POST'])
def download_wordlist():
    """Download a wordlist"""
    name = request.json.get('name', 'rockyou')
    
    try:
        success = password_cracker.download_wordlist(name)
        return jsonify({
            'success': success,
            'wordlists': password_cracker.get_wordlists()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wifi_audit_bp.route('/crack/start', methods=['POST'])
def start_crack():
    """Start password cracking"""
    data = request.json
    
    capture_file = data.get('capture_file')
    wordlist = data.get('wordlist')
    method = data.get('method', 'aircrack')
    bssid = data.get('bssid')
    
    if not capture_file or not wordlist:
        return jsonify({'error': 'Capture file and wordlist required'}), 400
    
    try:
        if method == 'aircrack':
            result = password_cracker.crack_with_aircrack(
                capture_file=capture_file,
                wordlist=wordlist,
                bssid=bssid
            )
        elif method == 'hashcat':
            result = password_cracker.crack_with_hashcat(
                capture_file=capture_file,
                wordlist=wordlist
            )
        else:
            return jsonify({'error': 'Invalid method'}), 400
        
        # Update database if cracked
        if result.get('cracked') and bssid:
            session = get_session()
            try:
                wifi = session.query(WiFiNetwork).filter_by(bssid=bssid).first()
                if wifi:
                    wifi.is_cracked = True
                    wifi.password = result.get('password')
                    session.commit()
            finally:
                session.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wifi_audit_bp.route('/crack/generate-wordlist', methods=['POST'])
def generate_wordlist():
    """Generate custom wordlist"""
    data = request.json
    
    base_words = data.get('words', [])
    output_file = data.get('output_file')
    
    if not base_words:
        return jsonify({'error': 'Base words required'}), 400
    
    try:
        output = password_cracker.generate_custom_wordlist(base_words, output_file)
        return jsonify({
            'success': True,
            'output_file': output,
            'wordlists': password_cracker.get_wordlists()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# Deauthentication
# ============================================

@wifi_audit_bp.route('/deauth/interfaces')
def get_deauth_interfaces():
    """Get available wireless interfaces"""
    return jsonify({
        'interfaces': wifi_deauth.get_interfaces(),
        'requirements': wifi_deauth.check_requirements()
    })

@wifi_audit_bp.route('/deauth/start', methods=['POST'])
def start_deauth():
    """Start deauth attack"""
    data = request.json
    
    target_mac = data.get('target_mac')
    ap_mac = data.get('ap_mac')
    interval = data.get('interval', 0.1)
    
    if not target_mac or not ap_mac:
        return jsonify({'error': 'Target MAC and AP MAC required'}), 400
    
    try:
        success = wifi_deauth.start_deauth_attack(
            target_mac=target_mac,
            ap_mac=ap_mac,
            interval=interval
        )
        
        return jsonify({
            'success': success,
            'active_attacks': wifi_deauth.get_active_attacks()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wifi_audit_bp.route('/deauth/stop', methods=['POST'])
def stop_deauth():
    """Stop deauth attack"""
    target_mac = request.json.get('target_mac')
    
    if target_mac:
        success = wifi_deauth.stop_deauth_attack(target_mac)
    else:
        wifi_deauth.stop_all_attacks()
        success = True
    
    return jsonify({
        'success': success,
        'active_attacks': wifi_deauth.get_active_attacks()
    })

@wifi_audit_bp.route('/deauth/status')
def deauth_status():
    """Get deauth status"""
    return jsonify({
        'active_attacks': wifi_deauth.get_active_attacks(),
        'is_monitor_mode': wifi_deauth.is_monitor_mode
    })

# ============================================
# WPS Attack
# ============================================

@wifi_audit_bp.route('/wps/check', methods=['POST'])
def check_wps():
    """Check if WPS is enabled on target"""
    bssid = request.json.get('bssid')
    
    if not bssid:
        return jsonify({'error': 'BSSID required'}), 400
    
    wps = WPSAttack()
    enabled = wps.check_wps_enabled(bssid)
    
    return jsonify({
        'bssid': bssid,
        'wps_enabled': enabled
    })

@wifi_audit_bp.route('/wps/attack', methods=['POST'])
def wps_attack():
    """Start WPS attack"""
    data = request.json
    
    bssid = data.get('bssid')
    channel = data.get('channel')
    
    if not bssid or not channel:
        return jsonify({'error': 'BSSID and channel required'}), 400
    
    try:
        wps = WPSAttack()
        result = wps.start_attack(bssid, channel)
        
        # Update database if cracked
        if result.get('cracked'):
            session = get_session()
            try:
                wifi = session.query(WiFiNetwork).filter_by(bssid=bssid).first()
                if wifi:
                    wifi.is_cracked = True
                    wifi.password = result.get('password')
                    session.commit()
            finally:
                session.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
