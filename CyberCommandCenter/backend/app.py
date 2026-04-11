"""
Cyber Command Center - Main Flask Application
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
import threading
import time

from config import HOST, PORT, DEBUG, SECRET_KEY, CORS_ORIGINS
from database.models import init_db, get_session, Device, Alert, ConnectionLog, WiFiNetwork, NetworkStats
from core.scanner import NetworkScanner, NetworkMonitor
from core.deauth import WiFiScanner
from core.pranks import PrankManager
from core.device_control import DeviceManager
from core.network_pranks import network_pranks
from core.system_tools import (
    SpeedTester, WiFiPasswordRecovery, ConnectionsMonitor,
    ProcessNetworkMonitor, PingMonitor, ARPTableViewer,
    DNSTools, SystemNetworkInfo
)
from core.logger import app_logger, audit, RequestLogger, info, warning, error
from core.validators import Validators, validate_request, is_valid_ip, is_valid_mac, sanitize
from core.error_handlers import (
    register_error_handlers, success_response, error_response, 
    handle_errors, rate_limit, HealthChecker, APIError, Errors
)

# New modules
from core.alerts import alert_manager, AlertType, AlertSeverity
from core.scheduler import prank_scheduler
from core.traffic_monitor import traffic_monitor
from core.theme_manager import theme_manager
from core.device_profiles import profile_manager
from core.config_manager import config_manager
from core.parental_control import parental_control
from core.wifi_hacker import wifi_hacker
from api.wifi_audit_routes import wifi_audit_bp

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
app.config['SECRET_KEY'] = SECRET_KEY
CORS(app, origins=CORS_ORIGINS)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Register blueprints
app.register_blueprint(wifi_audit_bp)

# Provide SocketIO to wifi_hacker for real-time capture events
wifi_hacker.set_socketio(socketio)

# Initialize core components
scanner = NetworkScanner()
wifi_scanner = WiFiScanner()
prank_manager = PrankManager()
device_manager = DeviceManager()
monitor = None

# Initialize system tools
speed_tester = SpeedTester()
ping_monitor = PingMonitor()

# ============================================
# Database Initialization
# ============================================

@app.before_request
def initialize():
    """Initialize database on first request"""
    if not hasattr(app, '_db_initialized'):
        init_db()
        app._db_initialized = True

# ============================================
# API Routes - Dashboard
# ============================================

@app.route('/api/v1/dashboard/stats')
def get_dashboard_stats():
    """Get dashboard statistics"""
    session = get_session()
    try:
        total_devices = session.query(Device).count()
        online_devices = session.query(Device).filter_by(is_online=True).count()
        trusted_devices = session.query(Device).filter_by(is_trusted=True).count()
        blocked_devices = session.query(Device).filter_by(is_blocked=True).count()
        unread_alerts = session.query(Alert).filter_by(is_read=False).count()
        
        return jsonify({
            'total_devices': total_devices,
            'online_devices': online_devices,
            'trusted_devices': trusted_devices,
            'blocked_devices': blocked_devices,
            'unread_alerts': unread_alerts,
            'network_info': scanner.get_network_info(),
            'active_pranks': len(prank_manager.get_active_pranks())
        })
    finally:
        session.close()

@app.route('/api/v1/dashboard/network-info')
def get_network_info():
    """Get network information"""
    return jsonify(scanner.get_network_info())

# ============================================
# API Routes - Devices
# ============================================

@app.route('/api/v1/devices')
def get_devices():
    """Get all devices"""
    session = get_session()
    try:
        devices = session.query(Device).all()
        return jsonify([d.to_dict() for d in devices])
    finally:
        session.close()

@app.route('/api/v1/devices/<int:device_id>')
def get_device(device_id):
    """Get single device"""
    session = get_session()
    try:
        device = session.query(Device).get(device_id)
        if device:
            return jsonify(device.to_dict())
        return jsonify({'error': 'Device not found'}), 404
    finally:
        session.close()

@app.route('/api/v1/devices/<int:device_id>', methods=['PUT'])
def update_device(device_id):
    """Update device properties"""
    session = get_session()
    try:
        device = session.query(Device).get(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        data = request.json
        if 'custom_name' in data:
            device.custom_name = data['custom_name']
        if 'category' in data:
            device.category = data['category']
        if 'is_trusted' in data:
            device.is_trusted = data['is_trusted']
        if 'is_blocked' in data:
            device.is_blocked = data['is_blocked']
        if 'notes' in data:
            device.notes = data['notes']
        
        session.commit()
        return jsonify(device.to_dict())
    finally:
        session.close()

@app.route('/api/v1/devices/scan', methods=['POST'])
def scan_network():
    """Trigger network scan"""
    scan_type = request.json.get('type', 'arp') if request.json else 'arp'
    
    try:
        if scan_type == 'arp':
            devices = scanner.scan_arp()
        elif scan_type == 'nmap':
            devices = scanner.scan_nmap()
        else:
            devices = scanner.scan_ping()
        
        # Update database
        session = get_session()
        try:
            for device_data in devices:
                # Check if device exists
                device = session.query(Device).filter_by(
                    mac_address=device_data['mac']
                ).first()
                
                if device:
                    # Update existing device
                    device.ip_address = device_data['ip']
                    device.hostname = device_data.get('hostname') or device.hostname
                    device.vendor = device_data.get('vendor') or device.vendor
                    device.last_seen = datetime.utcnow()
                    device.is_online = True
                else:
                    # Create new device
                    device = Device(
                        mac_address=device_data['mac'],
                        ip_address=device_data['ip'],
                        hostname=device_data.get('hostname'),
                        vendor=device_data.get('vendor'),
                        device_type=scanner.get_device_type(device_data),
                        is_online=True
                    )
                    session.add(device)
                    
                    # Create alert for new device
                    alert = Alert(
                        alert_type='new_device',
                        severity='medium',
                        title='New Device Detected',
                        description=f"New device {device_data.get('hostname') or device_data['mac']} connected to network",
                        device_mac=device_data['mac']
                    )
                    session.add(alert)
            
            # Mark offline devices
            current_macs = [d['mac'] for d in devices]
            session.query(Device).filter(
                ~Device.mac_address.in_(current_macs)
            ).update({Device.is_online: False}, synchronize_session=False)
            
            session.commit()
            
            # Emit update via WebSocket
            socketio.emit('devices_updated', {'count': len(devices)})
            
        finally:
            session.close()
        
        return jsonify({
            'success': True,
            'devices_found': len(devices),
            'devices': devices
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/devices/<int:device_id>/ports', methods=['POST'])
def scan_ports(device_id):
    """Scan ports on a device"""
    session = get_session()
    try:
        device = session.query(Device).get(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404
        
        ports = request.json.get('ports') if request.json else None
        results = scanner.port_scan(device.ip_address, ports)
        
        return jsonify({
            'device_id': device_id,
            'ip': device.ip_address,
            'open_ports': results
        })
    finally:
        session.close()

# ============================================
# API Routes - Alerts
# ============================================

@app.route('/api/v1/alerts')
def get_alerts():
    """Get all alerts"""
    session = get_session()
    try:
        limit = request.args.get('limit', 50, type=int)
        unread_only = request.args.get('unread', 'false').lower() == 'true'
        
        query = session.query(Alert).order_by(Alert.timestamp.desc())
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        alerts = query.limit(limit).all()
        return jsonify([a.to_dict() for a in alerts])
    finally:
        session.close()

@app.route('/api/v1/alerts/<int:alert_id>/read', methods=['POST'])
def mark_alert_read(alert_id):
    """Mark alert as read"""
    session = get_session()
    try:
        alert = session.query(Alert).get(alert_id)
        if alert:
            alert.is_read = True
            session.commit()
            return jsonify({'success': True})
        return jsonify({'error': 'Alert not found'}), 404
    finally:
        session.close()

@app.route('/api/v1/alerts/read-all', methods=['POST'])
def mark_all_alerts_read():
    """Mark all alerts as read"""
    session = get_session()
    try:
        session.query(Alert).filter_by(is_read=False).update({'is_read': True})
        session.commit()
        return jsonify({'success': True})
    finally:
        session.close()

# ============================================
# API Routes - WiFi
# ============================================

@app.route('/api/v1/wifi/networks')
def get_wifi_networks():
    """Get nearby WiFi networks"""
    try:
        networks = wifi_scanner.scan_networks()
        return jsonify({
            'networks': networks,
            'connected': wifi_scanner.get_connected_network()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/wifi/connected')
def get_connected_wifi():
    """Get currently connected WiFi network"""
    try:
        return jsonify(wifi_scanner.get_connected_network() or {})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# API Routes - Pranks
# ============================================

@app.route('/api/v1/pranks')
def get_pranks():
    """Get available pranks"""
    return jsonify({
        'available': prank_manager.get_available_pranks(),
        'active': prank_manager.get_active_pranks(),
        'history': prank_manager.get_prank_history(20)
    })

@app.route('/api/v1/pranks/execute', methods=['POST'])
def execute_prank():
    """Execute a prank"""
    data = request.json
    prank_id = data.get('prank_id')
    options = data.get('options', {})
    
    result = prank_manager.execute_prank(prank_id, options)
    
    return jsonify(result)

@app.route('/api/v1/pranks/start', methods=['POST'])
def start_prank():
    """Start a prank (alias for execute)"""
    data = request.json
    prank_id = data.get('prank_id')
    options = data.get('options', {})
    
    result = prank_manager.execute_prank(prank_id, options)
    
    return jsonify({
        'success': result.get('success', False),
        'result': result,
        'active_pranks': prank_manager.get_active_pranks()
    })

@app.route('/api/v1/pranks/stop', methods=['POST'])
def stop_prank():
    """Stop a prank"""
    data = request.json
    prank_id = data.get('prank_id')
    
    if prank_id == 'prank_server':
        result = prank_manager.execute_prank('prank_server', {'action': 'stop'})
    elif prank_id == 'fake_shutdown':
        result = prank_manager.execute_prank('cancel_shutdown', {})
    else:
        result = {'success': True}
    
    return jsonify({
        'success': result.get('success', True),
        'active_pranks': prank_manager.get_active_pranks()
    })

@app.route('/api/v1/pranks/stop-all', methods=['POST'])
def stop_all_pranks():
    """Stop all active pranks"""
    prank_manager.stop_all()
    return jsonify({'success': True})

@app.route('/api/v1/pranks/history')
def get_prank_history():
    """Get prank history"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify(prank_manager.get_prank_history(limit))

# ============================================
# API Routes - Tools
# ============================================

@app.route('/api/v1/tools/wake-on-lan', methods=['POST'])
def wake_on_lan():
    """Send Wake-on-LAN packet"""
    mac = request.json.get('mac')
    if not mac:
        return jsonify({'error': 'MAC address required'}), 400
    
    try:
        from wakeonlan import send_magic_packet
        send_magic_packet(mac)
        return jsonify({'success': True, 'mac': mac})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/tools/ping', methods=['POST'])
def ping_host():
    """Ping a host"""
    import subprocess
    import platform
    
    host = request.json.get('host')
    if not host:
        return jsonify({'error': 'Host required'}), 400
    
    try:
        if platform.system().lower() == 'windows':
            cmd = ['ping', '-n', '4', host]
        else:
            cmd = ['ping', '-c', '4', host]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/tools/traceroute', methods=['POST'])
def traceroute():
    """Traceroute to a host"""
    import subprocess
    import platform
    
    host = request.json.get('host')
    if not host:
        return jsonify({'error': 'Host required'}), 400
    
    try:
        if platform.system().lower() == 'windows':
            cmd = ['tracert', '-d', host]
        else:
            cmd = ['traceroute', '-n', host]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        return jsonify({
            'success': True,
            'output': result.stdout
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/tools/dns-lookup', methods=['POST'])
def dns_lookup():
    """DNS lookup"""
    import socket
    
    domain = request.json.get('domain')
    if not domain:
        return jsonify({'error': 'Domain required'}), 400
    
    try:
        # Get IP
        ip = socket.gethostbyname(domain)
        
        # Get all IPs
        _, _, ips = socket.gethostbyname_ex(domain)
        
        return jsonify({
            'domain': domain,
            'ip': ip,
            'all_ips': ips
        })
    except socket.gaierror as e:
        return jsonify({'error': f'DNS lookup failed: {e}'}), 400

# ============================================
# API Routes - System Tools
# ============================================

@app.route('/api/v1/system/speed-test', methods=['POST'])
def run_speed_test():
    """Run internet speed test"""
    include_upload = request.json.get('include_upload', True) if request.json else True
    
    if speed_tester.is_testing:
        return jsonify({'error': 'Speed test already in progress'}), 400
    
    result = speed_tester.run_test(include_upload)
    return jsonify(result)

@app.route('/api/v1/system/wifi-passwords')
def get_wifi_passwords():
    """Get saved WiFi passwords"""
    networks = WiFiPasswordRecovery.get_saved_networks()
    return jsonify(networks)

@app.route('/api/v1/system/connections')
def get_connections():
    """Get active network connections"""
    connections = ConnectionsMonitor.get_active_connections()
    return jsonify(connections)

@app.route('/api/v1/system/connections/stats')
def get_connection_stats():
    """Get connection statistics"""
    stats = ConnectionsMonitor.get_connection_stats()
    return jsonify(stats)

@app.route('/api/v1/system/processes')
def get_process_network():
    """Get network usage by process"""
    processes = ProcessNetworkMonitor.get_process_network_usage()
    return jsonify(processes)

@app.route('/api/v1/system/ping', methods=['POST'])
def system_ping_host():
    """Ping a host using system tools"""
    host = request.json.get('host')
    count = request.json.get('count', 4)
    
    if not host:
        return jsonify({'error': 'Host required'}), 400
    
    result = ping_monitor.ping_host(host, count)
    return jsonify(result)

@app.route('/api/v1/system/ping-multiple', methods=['POST'])
def ping_multiple():
    """Ping multiple hosts"""
    hosts = request.json.get('hosts', [])
    
    if not hosts:
        return jsonify({'error': 'Hosts required'}), 400
    
    results = ping_monitor.ping_multiple(hosts)
    return jsonify(results)

@app.route('/api/v1/system/arp-table')
def get_arp_table():
    """Get ARP table"""
    entries = ARPTableViewer.get_arp_table()
    return jsonify(entries)

@app.route('/api/v1/system/arp-flush', methods=['POST'])
def flush_arp():
    """Flush ARP cache"""
    result = ARPTableViewer.flush_arp_cache()
    return jsonify(result)

@app.route('/api/v1/system/dns-cache')
def get_dns_cache():
    """Get DNS cache"""
    entries = DNSTools.get_dns_cache()
    return jsonify(entries)

@app.route('/api/v1/system/dns-flush', methods=['POST'])
def flush_dns():
    """Flush DNS cache"""
    result = DNSTools.flush_dns_cache()
    return jsonify(result)

@app.route('/api/v1/system/interfaces')
def get_interfaces():
    """Get network interfaces"""
    interfaces = SystemNetworkInfo.get_network_interfaces()
    return jsonify(interfaces)

@app.route('/api/v1/system/network-stats')
def get_system_network_stats():
    """Get network IO statistics"""
    stats = SystemNetworkInfo.get_network_io_stats()
    return jsonify(stats)

# ============================================
# API Routes - Device Control
# ============================================

@app.route('/api/v1/device-control/scan')
def device_control_scan():
    """Scan for all devices on network"""
    force = request.args.get('force', 'false').lower() == 'true'
    devices = device_manager.scan(force=force)
    return jsonify({
        'devices': devices,
        'total': len(devices),
        'apple_count': len([d for d in devices if d.get('is_apple')]),
        'android_count': len([d for d in devices if 'samsung' in d.get('manufacturer', '').lower() 
                             or 'xiaomi' in d.get('manufacturer', '').lower()
                             or 'huawei' in d.get('manufacturer', '').lower()])
    })

@app.route('/api/v1/device-control/devices')
def device_control_list():
    """Get all discovered devices"""
    device_type = request.args.get('type', 'all')  # all, apple, android
    devices = device_manager.get_devices_by_type(device_type)
    return jsonify(devices)

@app.route('/api/v1/device-control/apple')
def device_control_apple():
    """Get Apple/iOS devices only"""
    devices = device_manager.get_devices_by_type('apple')
    return jsonify({
        'devices': devices,
        'count': len(devices),
        'info': device_manager.get_ios_info()
    })

@app.route('/api/v1/device-control/device/<identifier>')
def device_control_info(identifier):
    """Get detailed info about a specific device"""
    device = device_manager.get_device(identifier)
    if device:
        detailed_info = device_manager.controller.get_device_info(identifier)
        device.update(detailed_info)
        return jsonify(device)
    return jsonify({'error': 'Device not found'}), 404

@app.route('/api/v1/device-control/action', methods=['POST'])
def device_control_action():
    """Perform action on a device"""
    data = request.get_json() or {}
    action = data.get('action')  # info, block, unblock, disconnect
    identifier = data.get('identifier')  # IP or MAC
    options = data.get('options', {})
    
    if not action or not identifier:
        return jsonify({'error': 'Missing action or identifier'}), 400
    
    result = device_manager.device_action(action, identifier, options)
    return jsonify(result)

@app.route('/api/v1/device-control/ios-info')
def device_control_ios_info():
    """Get information about iOS device control capabilities"""
    return jsonify(device_manager.get_ios_info())

# ============================================
# API Routes - Network Pranks (for mobile devices)
# ============================================

@app.route('/api/v1/network-pranks/available')
@handle_errors
def get_network_pranks():
    """Get available network pranks"""
    return jsonify(network_pranks.get_available_pranks())

@app.route('/api/v1/network-pranks/execute', methods=['POST'])
@handle_errors
@rate_limit(requests_per_minute=30)
def execute_network_prank():
    """Execute a network prank on a device"""
    data = request.get_json() or {}
    prank_id = sanitize(data.get('prank_id', ''), max_length=50)
    device_ip = data.get('device_ip', '')
    options = data.get('options', {})
    
    # Validate inputs
    if not prank_id:
        return error_response(error=Errors.validation_error("Missing prank_id"))
    
    if not device_ip:
        return error_response(error=Errors.validation_error("Missing device_ip"))
    
    valid, msg = Validators.validate_ip(device_ip)
    if not valid:
        return error_response(error=Errors.validation_error(msg))
    
    # Log the action
    audit("network_prank_execute", {
        'prank_id': prank_id,
        'device_ip': device_ip
    })
    
    result = network_pranks.execute_prank(prank_id, device_ip, options)
    return jsonify(result)

@app.route('/api/v1/network-pranks/stop', methods=['POST'])
@handle_errors
def stop_network_prank():
    """Stop pranks for a device"""
    data = request.get_json() or {}
    device_ip = data.get('device_ip', '')
    
    if not device_ip:
        return error_response(error=Errors.validation_error("Missing device_ip"))
    
    valid, msg = Validators.validate_ip(device_ip)
    if not valid:
        return error_response(error=Errors.validation_error(msg))
    
    audit("network_prank_stop", {'device_ip': device_ip})
    
    result = network_pranks.stop_prank(device_ip)
    return jsonify(result)

@app.route('/api/v1/network-pranks/active')
@handle_errors
def get_active_network_pranks():
    """Get active network pranks"""
    return jsonify(network_pranks.get_active_pranks())

@app.route('/api/v1/network-pranks/block-sites', methods=['POST'])
@handle_errors
@rate_limit(requests_per_minute=20)
def block_sites():
    """Block specific sites for a device"""
    data = request.get_json() or {}
    device_ip = data.get('device_ip', '')
    sites = data.get('sites', [])
    
    if not device_ip:
        return error_response(error=Errors.validation_error("Missing device_ip"))
    
    valid, msg = Validators.validate_ip(device_ip)
    if not valid:
        return error_response(error=Errors.validation_error(msg))
    
    if not sites or not isinstance(sites, list):
        return error_response(error=Errors.validation_error("Missing or invalid sites list"))
    
    # Sanitize site names
    sites = [sanitize(s, max_length=200, allow_special=True) for s in sites[:50]]
    
    audit("block_sites", {'device_ip': device_ip, 'sites_count': len(sites)})
    
    result = network_pranks.block_sites_for_device(device_ip, sites)
    return jsonify(result)

@app.route('/api/v1/network-pranks/unblock', methods=['POST'])
@handle_errors
def unblock_device_sites():
    """Unblock all sites for a device"""
    data = request.get_json() or {}
    device_ip = data.get('device_ip', '')
    
    if not device_ip:
        return error_response(error=Errors.validation_error("Missing device_ip"))
    
    valid, msg = Validators.validate_ip(device_ip)
    if not valid:
        return error_response(error=Errors.validation_error(msg))
    
    audit("unblock_sites", {'device_ip': device_ip})
    
    result = network_pranks.unblock_everything(device_ip)
    return jsonify(result)

# ============================================
# API Routes - Real-time Alerts
# ============================================

@app.route('/api/v1/alerts/realtime')
@handle_errors
def get_realtime_alerts():
    """Get real-time alerts from AlertManager"""
    limit = request.args.get('limit', 50, type=int)
    unread_only = request.args.get('unread', 'false').lower() == 'true'
    severity = request.args.get('severity')
    
    alerts = alert_manager.get_alerts(limit, unread_only, severity)
    return jsonify({
        'alerts': alerts,
        'total': len(alerts),
        'settings': alert_manager.get_settings()
    })

@app.route('/api/v1/alerts/settings', methods=['GET', 'PUT'])
@handle_errors
def alert_settings():
    """Get or update alert settings"""
    if request.method == 'GET':
        return jsonify(alert_manager.get_settings())
    
    data = request.get_json() or {}
    
    if 'enabled' in data:
        alert_manager.settings.notifications_enabled = data['enabled']
    if 'sound' in data:
        alert_manager.settings.sound_enabled = data['sound']
    if 'quietHoursEnabled' in data:
        alert_manager.settings.quiet_hours_enabled = data['quietHoursEnabled']
    if 'quietHoursStart' in data:
        alert_manager.settings.quiet_hours_start = data['quietHoursStart']
    if 'quietHoursEnd' in data:
        alert_manager.settings.quiet_hours_end = data['quietHoursEnd']
    
    alert_manager._save_settings()
    return jsonify({'success': True, 'settings': alert_manager.get_settings()})

@app.route('/api/v1/alerts/<alert_id>/dismiss', methods=['POST'])
@handle_errors
def dismiss_alert(alert_id):
    """Dismiss a real-time alert"""
    result = alert_manager.dismiss_alert(alert_id)
    return jsonify({'success': result})

@app.route('/api/v1/alerts/dismiss-all', methods=['POST'])
@handle_errors
def dismiss_all_alerts():
    """Dismiss all alerts"""
    alert_manager.dismiss_all()
    return jsonify({'success': True})

# ============================================
# API Routes - Prank Scheduler
# ============================================

@app.route('/api/v1/scheduler/pranks')
@handle_errors
def get_scheduled_pranks():
    """Get all scheduled pranks"""
    return jsonify({
        'scheduled': prank_scheduler.get_all_scheduled(),
        'pending': prank_scheduler.get_pending()
    })

@app.route('/api/v1/scheduler/pranks', methods=['POST'])
@handle_errors
def schedule_prank():
    """Schedule a new prank"""
    data = request.get_json() or {}
    
    prank_id = data.get('prank_id')
    schedule_type = data.get('schedule_type', 'once')
    execute_at = data.get('execute_at')
    recurrence = data.get('recurrence', {})
    options = data.get('options', {})
    
    if not prank_id or not execute_at:
        return error_response(error=Errors.validation_error("Missing prank_id or execute_at"))
    
    result = prank_scheduler.schedule_prank(prank_id, schedule_type, execute_at, recurrence, options)
    
    audit("prank_scheduled", {
        'prank_id': prank_id,
        'schedule_type': schedule_type,
        'execute_at': execute_at
    })
    
    return jsonify(result)

@app.route('/api/v1/scheduler/pranks/<schedule_id>', methods=['DELETE'])
@handle_errors
def cancel_scheduled_prank(schedule_id):
    """Cancel a scheduled prank"""
    result = prank_scheduler.cancel_scheduled(schedule_id)
    return jsonify({'success': result})

@app.route('/api/v1/scheduler/pause', methods=['POST'])
@handle_errors
def pause_scheduler():
    """Pause all scheduled pranks"""
    prank_scheduler.pause_all()
    return jsonify({'success': True, 'status': 'paused'})

@app.route('/api/v1/scheduler/resume', methods=['POST'])
@handle_errors
def resume_scheduler():
    """Resume scheduled pranks"""
    prank_scheduler.resume_all()
    return jsonify({'success': True, 'status': 'running'})

# ============================================
# API Routes - Traffic Monitor
# ============================================

@app.route('/api/v1/traffic/current')
@handle_errors
def get_current_traffic():
    """Get current traffic rates"""
    return jsonify(traffic_monitor.get_current_rate())

@app.route('/api/v1/traffic/stats')
@handle_errors
def get_traffic_stats():
    """Get comprehensive traffic statistics"""
    return jsonify(traffic_monitor.get_stats())

@app.route('/api/v1/traffic/history')
@handle_errors
def get_traffic_history():
    """Get traffic history"""
    period = request.args.get('period', 'minute')
    limit = request.args.get('limit', 60, type=int)
    
    return jsonify({
        'period': period,
        'data': traffic_monitor.get_history(period, limit)
    })

@app.route('/api/v1/traffic/devices')
@handle_errors
def get_device_traffic():
    """Get traffic by device"""
    top_n = request.args.get('top', 10, type=int)
    return jsonify(traffic_monitor.get_device_traffic(top_n))

@app.route('/api/v1/traffic/interfaces')
@handle_errors
def get_interface_traffic():
    """Get traffic per network interface"""
    return jsonify(traffic_monitor.get_interface_stats())

@app.route('/api/v1/traffic/spike-threshold', methods=['PUT'])
@handle_errors
def set_spike_threshold():
    """Set traffic spike alert threshold"""
    data = request.get_json() or {}
    mbps = data.get('mbps', 50)
    traffic_monitor.set_spike_threshold(mbps)
    return jsonify({'success': True, 'threshold_mbps': mbps})

# ============================================
# API Routes - Theme & Preferences
# ============================================

@app.route('/api/v1/preferences')
@handle_errors
def get_preferences():
    """Get user preferences"""
    return jsonify(theme_manager.get_preferences())

@app.route('/api/v1/preferences', methods=['PUT'])
@handle_errors
def update_preferences():
    """Update user preferences"""
    data = request.get_json() or {}
    theme_manager.update_preferences(data)
    return jsonify({'success': True, 'preferences': theme_manager.get_preferences()})

@app.route('/api/v1/themes')
@handle_errors
def get_themes():
    """Get available themes"""
    return jsonify({
        'themes': theme_manager.get_available_themes(),
        'current': theme_manager.get_current_theme()
    })

@app.route('/api/v1/themes/current', methods=['PUT'])
@handle_errors
def set_theme():
    """Set current theme"""
    data = request.get_json() or {}
    theme_name = data.get('theme')
    
    if theme_name:
        result = theme_manager.set_theme(theme_name)
        if result:
            return jsonify({'success': True, 'theme': theme_manager.get_current_theme()})
    
    return error_response(error=Errors.validation_error("Invalid theme"))

@app.route('/api/v1/themes/custom', methods=['POST'])
@handle_errors
def set_custom_theme():
    """Set custom theme colors"""
    data = request.get_json() or {}
    result = theme_manager.set_custom_theme(data)
    return jsonify({'success': result, 'theme': theme_manager.get_current_theme()})

@app.route('/api/v1/themes/css')
@handle_errors
def get_theme_css():
    """Get CSS variables for current theme"""
    return theme_manager.generate_css_variables(), 200, {'Content-Type': 'text/css'}

# ============================================
# API Routes - Device Profiles
# ============================================

@app.route('/api/v1/profiles')
@handle_errors
def get_profiles():
    """Get all device profiles"""
    return jsonify({
        'profiles': profile_manager.get_all_profiles(),
        'templates': profile_manager.get_templates()
    })

@app.route('/api/v1/profiles/<mac>')
@handle_errors
def get_profile(mac):
    """Get profile for a specific device"""
    profile = profile_manager.get_profile(mac)
    if profile:
        return jsonify(profile.to_dict())
    return jsonify({'error': 'Profile not found'}), 404

@app.route('/api/v1/profiles', methods=['POST'])
@handle_errors
def create_profile():
    """Create new device profile"""
    data = request.get_json() or {}
    mac = data.get('mac')
    name = data.get('name', '')
    category = data.get('category', 'unknown')
    template = data.get('template')
    
    if not mac:
        return error_response(error=Errors.validation_error("Missing MAC address"))
    
    valid, msg = Validators.validate_mac(mac)
    if not valid:
        return error_response(error=Errors.validation_error(msg))
    
    profile = profile_manager.create_profile(mac, name, category, template)
    
    audit("profile_created", {'mac': mac, 'name': name, 'template': template})
    
    return jsonify(profile.to_dict())

@app.route('/api/v1/profiles/<mac>', methods=['PUT'])
@handle_errors
def update_profile(mac):
    """Update device profile"""
    data = request.get_json() or {}
    
    profile = profile_manager.update_profile(mac, data)
    if profile:
        audit("profile_updated", {'mac': mac})
        return jsonify(profile.to_dict())
    
    return jsonify({'error': 'Profile not found'}), 404

@app.route('/api/v1/profiles/<mac>', methods=['DELETE'])
@handle_errors
def delete_profile(mac):
    """Delete device profile"""
    result = profile_manager.delete_profile(mac)
    if result:
        audit("profile_deleted", {'mac': mac})
    return jsonify({'success': result})

@app.route('/api/v1/profiles/<mac>/check-access')
@handle_errors
def check_device_access(mac):
    """Check if device has network access based on profile"""
    return jsonify(profile_manager.check_access_allowed(mac))

@app.route('/api/v1/profiles/templates')
@handle_errors
def get_profile_templates():
    """Get available profile templates"""
    return jsonify(profile_manager.get_templates())

# ============================================
# API Routes - Parental Control
# ============================================

@app.route('/api/v1/parental/devices')
@handle_errors
def get_parental_devices():
    """Get devices with parental control enabled"""
    return jsonify(parental_control.get_all_devices())

@app.route('/api/v1/parental/devices/<mac>')
@handle_errors
def get_parental_device(mac):
    """Get parental control settings for device"""
    profile = parental_control.get_device_profile(mac)
    if profile:
        return jsonify(profile.to_dict())
    return jsonify({'error': 'Device not found'}), 404

@app.route('/api/v1/parental/devices/<mac>', methods=['PUT'])
@handle_errors
def update_parental_device(mac):
    """Update parental control settings"""
    data = request.get_json() or {}
    profile = parental_control.update_device(mac, data)
    if profile:
        return jsonify(profile.to_dict())
    return jsonify({'error': 'Device not found'}), 404

@app.route('/api/v1/parental/devices/<mac>/usage')
@handle_errors
def get_device_usage(mac):
    """Get usage statistics for device"""
    period = request.args.get('period', 'today')
    return jsonify(parental_control.get_usage_stats(mac, period))

@app.route('/api/v1/parental/devices/<mac>/check-access')
@handle_errors
def check_parental_access(mac):
    """Check if device currently has access"""
    category = request.args.get('category')
    return jsonify(parental_control.check_access(mac, category))

@app.route('/api/v1/parental/bedtime')
@handle_errors
def check_bedtime_status():
    """Check bedtime status for all devices"""
    statuses = {}
    for mac, profile in parental_control.devices.items():
        statuses[mac] = {
            'name': profile.name,
            'is_bedtime': parental_control._check_bedtime(profile),
            'bedtime_enabled': profile.bedtime_enabled,
            'bedtime_start': profile.bedtime_start,
            'bedtime_end': profile.bedtime_end
        }
    return jsonify(statuses)

# ============================================
# API Routes - Config Export/Import
# ============================================

@app.route('/api/v1/config/export')
@handle_errors
def export_config():
    """Export configuration as JSON"""
    components = request.args.getlist('components') or None
    return jsonify(config_manager.export_config(components=components))

@app.route('/api/v1/config/export/download')
@handle_errors
def download_config():
    """Download configuration as ZIP file"""
    from flask import Response
    
    zip_data = config_manager.export_to_zip()
    
    return Response(
        zip_data,
        mimetype='application/zip',
        headers={'Content-Disposition': 'attachment; filename=cyber_command_center_config.zip'}
    )

@app.route('/api/v1/config/import', methods=['POST'])
@handle_errors
def import_config_route():
    """Import configuration from JSON"""
    data = request.get_json() or {}
    overwrite = data.get('overwrite', True)
    components = data.get('components')
    config_data = data.get('config', data)
    
    result = config_manager.import_config(config_data, overwrite, components)
    
    if result['success']:
        audit("config_imported", {'imported': result['imported']})
    
    return jsonify(result)

@app.route('/api/v1/config/components')
@handle_errors
def get_config_components():
    """Get available config components"""
    return jsonify(config_manager.get_available_components())

@app.route('/api/v1/config/backup', methods=['POST'])
@handle_errors
def create_backup():
    """Create a backup"""
    data = request.get_json() or {}
    name = data.get('name')
    
    result = config_manager.create_backup(name)
    
    if result['success']:
        audit("config_backup_created", {'name': result['name']})
    
    return jsonify(result)

@app.route('/api/v1/config/backups')
@handle_errors
def list_backups():
    """List available backups"""
    return jsonify(config_manager.list_backups())

@app.route('/api/v1/config/backups/<name>/restore', methods=['POST'])
@handle_errors
def restore_backup(name):
    """Restore from backup"""
    data = request.get_json() or {}
    overwrite = data.get('overwrite', True)
    
    result = config_manager.restore_backup(name, overwrite)
    
    if result['success']:
        audit("config_backup_restored", {'name': name})
    
    return jsonify(result)

@app.route('/api/v1/config/backups/<name>', methods=['DELETE'])
@handle_errors
def delete_backup(name):
    """Delete backup"""
    result = config_manager.delete_backup(name)
    return jsonify({'success': result})

# ============================================
# API Routes - WiFi Hacking (Ethical Testing)
# ============================================

@app.route('/api/v1/wifi-hacker/status')
@handle_errors
def wifi_hacker_status():
    """Get WiFi hacker status and capabilities"""
    current = wifi_hacker.current_attack
    return jsonify({
        'available': wifi_hacker.is_available(),
        'tools': wifi_hacker.check_requirements(),
        'interface': wifi_hacker.interface,
        'monitor_mode': wifi_hacker.monitor_mode_enabled,
        'current_attack': current.value if current else None
    })

@app.route('/api/v1/wifi-hacker/interfaces')
@handle_errors
def get_wifi_interfaces():
    """Get available WiFi interfaces"""
    return jsonify(wifi_hacker.get_wireless_interfaces())

@app.route('/api/v1/wifi-hacker/interface', methods=['PUT'])
@handle_errors
def set_wifi_interface():
    """Set WiFi interface for attacks"""
    data = request.get_json() or {}
    interface = data.get('interface')
    
    if not interface:
        return error_response(error=Errors.validation_error("Missing interface"))
    
    wifi_hacker.set_interface(interface)
    return jsonify({'success': True, 'interface': interface})

@app.route('/api/v1/wifi-hacker/monitor-mode', methods=['POST'])
@handle_errors
def toggle_monitor_mode():
    """Enable/disable monitor mode"""
    data = request.get_json() or {}
    enable = data.get('enable', True)
    
    if enable:
        result = wifi_hacker.enable_monitor_mode()
    else:
        result = wifi_hacker.disable_monitor_mode()
    
    return jsonify(result)

@app.route('/api/v1/wifi-hacker/scan-wps')
@handle_errors
def scan_wps_networks():
    """Scan for WPS-enabled networks"""
    timeout = request.args.get('timeout', 30, type=int)
    
    networks = wifi_hacker.scan_wps_networks(timeout)
    return jsonify({
        'networks': [n.__dict__ for n in networks],
        'count': len(networks)
    })

@app.route('/api/v1/wifi-hacker/attack/wps-pixie', methods=['POST'])
@handle_errors
@rate_limit(requests_per_minute=5)
def attack_wps_pixie():
    """WPS Pixie Dust attack"""
    data = request.get_json() or {}
    bssid = data.get('bssid')
    channel = data.get('channel', 1)
    
    if not bssid:
        return error_response(error=Errors.validation_error("Missing BSSID"))
    
    audit("wifi_attack_pixie", {'bssid': bssid})
    
    result = wifi_hacker.attack_wps_pixie(bssid, channel)
    return jsonify(result.to_dict())

@app.route('/api/v1/wifi-hacker/attack/wps-bruteforce', methods=['POST'])
@handle_errors
@rate_limit(requests_per_minute=2)
def attack_wps_bruteforce():
    """WPS PIN brute force attack"""
    data = request.get_json() or {}
    bssid = data.get('bssid')
    channel = data.get('channel', 1)
    timeout = data.get('timeout', 3600)
    
    if not bssid:
        return error_response(error=Errors.validation_error("Missing BSSID"))
    
    audit("wifi_attack_bruteforce", {'bssid': bssid})
    
    result = wifi_hacker.attack_wps_bruteforce(bssid, channel, timeout)
    return jsonify(result.to_dict())

@app.route('/api/v1/wifi-hacker/capture/handshake', methods=['POST'])
@handle_errors
@rate_limit(requests_per_minute=5)
def capture_handshake():
    """Capture WPA handshake"""
    data = request.get_json() or {}
    bssid = data.get('bssid')
    channel = data.get('channel', 1)
    client_mac = data.get('client_mac')
    timeout = data.get('timeout', 120)
    
    if not bssid:
        return error_response(error=Errors.validation_error("Missing BSSID"))
    
    audit("wifi_capture_handshake", {'bssid': bssid})
    
    result = wifi_hacker.capture_handshake(bssid, channel, client_mac, timeout)
    return jsonify(result.to_dict())

@app.route('/api/v1/wifi-hacker/capture/pmkid', methods=['POST'])
@handle_errors
@rate_limit(requests_per_minute=5)
def capture_pmkid():
    """Capture PMKID"""
    data = request.get_json() or {}
    bssid = data.get('bssid')
    channel = data.get('channel', 1)
    timeout = data.get('timeout', 60)
    
    if not bssid:
        return error_response(error=Errors.validation_error("Missing BSSID"))
    
    audit("wifi_capture_pmkid", {'bssid': bssid})
    
    result = wifi_hacker.capture_pmkid(bssid, channel, timeout)
    return jsonify(result.to_dict())

@app.route('/api/v1/wifi-hacker/crack', methods=['POST'])
@handle_errors
@rate_limit(requests_per_minute=5)
def crack_handshake():
    """Crack captured handshake"""
    data = request.get_json() or {}
    capture_file = data.get('capture_file')
    wordlist = data.get('wordlist')
    use_gpu = data.get('use_gpu', False)
    
    if not capture_file:
        return error_response(error=Errors.validation_error("Missing capture file"))
    
    audit("wifi_crack_attempt", {'capture_file': capture_file})
    
    result = wifi_hacker.crack_handshake(capture_file, wordlist, use_gpu)
    return jsonify(result.to_dict())

@app.route('/api/v1/wifi-hacker/stop', methods=['POST'])
@handle_errors
def stop_wifi_attack():
    """Stop current WiFi attack"""
    result = wifi_hacker.stop_attack()
    return jsonify(result)

@app.route('/api/v1/wifi-hacker/wordlists')
@handle_errors
def get_wordlists():
    """Get available wordlists"""
    import os
    
    wordlist_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'wordlists'
    )
    
    wordlists = []
    if os.path.exists(wordlist_dir):
        for f in os.listdir(wordlist_dir):
            if f.endswith('.txt'):
                path = os.path.join(wordlist_dir, f)
                wordlists.append({
                    'name': f,
                    'path': path,
                    'size': os.path.getsize(path)
                })
    
    return jsonify(wordlists)

@app.route('/api/v1/wifi-hacker/download-wordlist', methods=['POST'])
@handle_errors
def download_wordlist():
    """Download a popular wordlist"""
    data = request.get_json() or {}
    name = data.get('name', 'rockyou')
    
    result = wifi_hacker.download_wordlist(name)
    return jsonify(result)

# ============================================
# WebSocket Events
# ============================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'status': 'Connected to Cyber Command Center'})

@socketio.on('start_monitoring')
def handle_start_monitoring():
    """Start network monitoring"""
    global monitor
    
    def on_event(event_type, device):
        socketio.emit('network_event', {
            'type': event_type,
            'device': device
        })
    
    if monitor is None:
        monitor = NetworkMonitor(scanner, callback=on_event)
        monitor.start(interval=30)
        emit('monitoring_started', {'status': 'Monitoring started'})
    else:
        emit('monitoring_started', {'status': 'Already monitoring'})

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """Stop network monitoring"""
    global monitor
    if monitor:
        monitor.stop()
        monitor = None
        emit('monitoring_stopped', {'status': 'Monitoring stopped'})

# ============================================
# Static Files (Frontend)
# ============================================

@app.route('/')
def serve_frontend():
    """Serve frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# ============================================
# Error Handlers
# ============================================
# API Routes - Health Check
# ============================================

@app.route('/api/v1/health')
def health_check():
    """Get system health status"""
    return jsonify(HealthChecker.get_health_status())

@app.route('/api/v1/health/simple')
def health_simple():
    """Simple health check for monitoring"""
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat() + 'Z'})

# ============================================
# Request Logging Middleware
# ============================================

@app.before_request
def log_request_info():
    """Log incoming requests"""
    request.start_time = datetime.now()

@app.after_request
def log_response_info(response):
    """Log response and calculate duration"""
    if hasattr(request, 'start_time'):
        duration = (datetime.now() - request.start_time).total_seconds() * 1000
        RequestLogger.log_request(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration,
            client_ip=request.remote_addr
        )
    return response

# ============================================
# Register Error Handlers
# ============================================

register_error_handlers(app, debug_mode=DEBUG)

# ============================================
# Main Entry Point
# ============================================

def main():
    """Main entry point"""
    info("╔══════════════════════════════════════════════════════════════╗")
    info("║                                                              ║")
    info("║   🛡️  CYBER COMMAND CENTER v1.0                              ║")
    info("║                                                              ║")
    info("║   Network Security Dashboard                                 ║")
    info("║   FOR EDUCATIONAL USE ONLY ON YOUR OWN NETWORK               ║")
    info("║                                                              ║")
    info("╚══════════════════════════════════════════════════════════════╝")
    
    info(f"Starting server on http://{HOST}:{PORT}")
    info(f"Network: {scanner.network_range}")
    info(f"Gateway: {scanner.gateway_ip}")
    info(f"Local IP: {scanner.local_ip}")
    info("Press Ctrl+C to stop")
    
    # Initialize database
    init_db()
    
    # Log startup
    audit("server_start", {
        'host': HOST,
        'port': PORT,
        'network': scanner.network_range,
        'debug': DEBUG
    })
    
    # Run server
    socketio.run(app, host=HOST, port=PORT, debug=DEBUG, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()
