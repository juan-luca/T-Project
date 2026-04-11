import { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import api from '../services/api';

export default function WiFiHacker() {
  const [status, setStatus] = useState(null);
  const [interfaces, setInterfaces] = useState([]);
  const [selectedInterface, setSelectedInterface] = useState('');
  const [wpsNetworks, setWpsNetworks] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [attacking, setAttacking] = useState(false);
  const [attackResult, setAttackResult] = useState(null);
  const [wordlists, setWordlists] = useState([]);
  const [selectedWordlist, setSelectedWordlist] = useState('');
  const [captureFile, setCaptureFile] = useState('');
  const [logs, setLogs] = useState([]);
  const [captureStatus, setCaptureStatus] = useState(null); // real-time capture info
  const socketRef = useRef(null);
  const logsEndRef = useRef(null);

  // ── Socket.io: real-time capture progress ────────────────────────
  useEffect(() => {
    const socket = io(window.location.origin, { transports: ['websocket', 'polling'] });
    socketRef.current = socket;

    socket.on('connect', () => {
      addLog('Conectado al servidor (tiempo real)', 'success');
    });

    socket.on('wifi_capture_status', (data) => {
      setCaptureStatus(data);

      switch (data.status) {
        case 'started':
          addLog(`Captura iniciada para ${data.bssid} (canal ${data.channel})`, 'info');
          break;
        case 'capturing':
          addLog(`Capturando... ${data.elapsed}s transcurridos`, 'info');
          break;
        case 'deauth_sent':
          addLog(`Deauth #${data.deauth_count} enviado para forzar reconexión`, 'warning');
          break;
        case 'captured':
          addLog(`Handshake capturado en ${data.elapsed}s`, 'success');
          addLog(`Archivo: ${data.file}`, 'success');
          setCaptureFile(data.file || '');
          setAttacking(false);
          break;
        case 'timeout':
          addLog(`Timeout tras ${data.elapsed}s - no se capturó handshake`, 'error');
          setAttacking(false);
          break;
        case 'error':
          addLog(`Error en captura: ${data.error}`, 'error');
          setAttacking(false);
          break;
        default:
          break;
      }
    });

    socket.on('disconnect', () => {
      addLog('Desconectado del servidor', 'warning');
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // ── Initial data load ─────────────────────────────────────────────
  useEffect(() => {
    loadStatus();
    loadInterfaces();
    loadWordlists();
  }, []);

  const loadStatus = async () => {
    try {
      const res = await api.get('/api/v1/wifi-hacker/status');
      setStatus(res.data);
      if (res.data.interface) {
        setSelectedInterface(res.data.interface);
      }
    } catch (err) {
      console.error('Error loading status:', err);
    }
  };

  const loadInterfaces = async () => {
    try {
      const res = await api.get('/api/v1/wifi-hacker/interfaces');
      // Backend returns List[str] — normalize to array of strings
      const data = Array.isArray(res.data) ? res.data : [];
      setInterfaces(data);
    } catch (err) {
      console.error('Error loading interfaces:', err);
    }
  };

  const loadWordlists = async () => {
    try {
      const res = await api.get('/api/v1/wifi-hacker/wordlists');
      setWordlists(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error('Error loading wordlists:', err);
    }
  };

  // ── Actions ───────────────────────────────────────────────────────

  const setInterface = async (iface) => {
    try {
      await api.put('/api/v1/wifi-hacker/interface', { interface: iface });
      setSelectedInterface(iface);
      addLog(`Interfaz configurada: ${iface}`);
      loadStatus();
    } catch (err) {
      addLog(`Error configurando interfaz: ${err.message}`, 'error');
    }
  };

  const toggleMonitorMode = async (enable) => {
    try {
      addLog(`${enable ? 'Habilitando' : 'Deshabilitando'} modo monitor...`);
      const res = await api.post('/api/v1/wifi-hacker/monitor-mode', { enable });
      if (res.data.success) {
        addLog(`Modo monitor ${enable ? 'habilitado' : 'deshabilitado'}: ${res.data.interface || ''}`, 'success');
      } else {
        addLog(`Error: ${res.data.error || 'Sin respuesta'}`, 'error');
      }
      loadStatus();
    } catch (err) {
      addLog(`Error: ${err.message}`, 'error');
    }
  };

  const scanWPSNetworks = async () => {
    setScanning(true);
    setWpsNetworks([]);
    addLog('Iniciando escaneo de redes WPS...');

    try {
      const res = await api.get('/api/v1/wifi-hacker/scan-wps?timeout=30');
      setWpsNetworks(res.data.networks || []);
      addLog(`Encontradas ${res.data.count} redes con WPS`, 'success');
    } catch (err) {
      addLog(`Error en escaneo: ${err.message}`, 'error');
    }
    setScanning(false);
  };

  const attackPixieDust = async (network) => {
    setAttacking(true);
    setAttackResult(null);
    addLog(`Iniciando ataque Pixie Dust en ${network.essid || network.bssid}...`);

    try {
      const res = await api.post('/api/v1/wifi-hacker/attack/wps-pixie', {
        bssid: network.bssid,
        channel: network.channel
      });
      setAttackResult(res.data);
      if (res.data.success) {
        addLog(`PIN WPS encontrado: ${res.data.pin}`, 'success');
        if (res.data.password) {
          addLog(`Contraseña WiFi: ${res.data.password}`, 'success');
        }
      } else {
        addLog(`Ataque fallido: ${res.data.error || 'Router no vulnerable a Pixie Dust'}`, 'error');
      }
    } catch (err) {
      addLog(`Error en ataque: ${err.message}`, 'error');
    }
    setAttacking(false);
  };

  const captureHandshake = async (network) => {
    setAttacking(true);
    setAttackResult(null);
    setCaptureStatus(null);
    addLog(`Iniciando captura de handshake: ${network.essid || network.bssid} (puede tardar hasta 2 min)...`);

    try {
      const res = await api.post('/api/v1/wifi-hacker/capture/handshake', {
        bssid: network.bssid,
        channel: network.channel,
        timeout: 120
      }, { timeout: 150000 }); // 2.5 min HTTP timeout

      setAttackResult(res.data);
      if (res.data.success) {
        const file = res.data.details?.capture_file;
        addLog(`Handshake capturado${file ? ': ' + file : ''}`, 'success');
        if (file) setCaptureFile(file);
      } else {
        addLog(`No se pudo capturar handshake: ${res.data.error || ''}`, 'error');
      }
    } catch (err) {
      addLog(`Error: ${err.message}`, 'error');
    }
    setAttacking(false);
  };

  const capturePMKID = async (network) => {
    setAttacking(true);
    setAttackResult(null);
    addLog(`Capturando PMKID de ${network.essid || network.bssid}...`);

    try {
      const res = await api.post('/api/v1/wifi-hacker/capture/pmkid', {
        bssid: network.bssid,
        channel: network.channel,
        timeout: 60
      }, { timeout: 90000 });

      setAttackResult(res.data);
      if (res.data.success) {
        const file = res.data.details?.hash_file;
        addLog(`PMKID capturado${file ? ': ' + file : ''}`, 'success');
        if (file) setCaptureFile(file);
      } else {
        addLog(`No se pudo capturar PMKID: ${res.data.error || ''}`, 'error');
      }
    } catch (err) {
      addLog(`Error: ${err.message}`, 'error');
    }
    setAttacking(false);
  };

  const crackCapture = async () => {
    if (!captureFile) {
      addLog('No hay archivo de captura seleccionado', 'error');
      return;
    }

    setAttacking(true);
    addLog(`Crackeando ${captureFile}...`);

    try {
      const res = await api.post('/api/v1/wifi-hacker/crack', {
        capture_file: captureFile,
        wordlist: selectedWordlist || null,
        use_gpu: false
      }, { timeout: 3700000 }); // up to 1h

      setAttackResult(res.data);
      if (res.data.success) {
        addLog(`Contraseña encontrada: ${res.data.password}`, 'success');
      } else {
        addLog(`Contraseña no encontrada en el diccionario`, 'error');
      }
    } catch (err) {
      addLog(`Error: ${err.message}`, 'error');
    }
    setAttacking(false);
  };

  const stopAttack = async () => {
    try {
      await api.post('/api/v1/wifi-hacker/stop');
      addLog('Ataque detenido', 'warning');
      setAttacking(false);
      setCaptureStatus(null);
    } catch (err) {
      addLog(`Error deteniendo ataque: ${err.message}`, 'error');
    }
  };

  const downloadWordlist = async (name) => {
    addLog(`Descargando wordlist ${name}...`);
    try {
      const res = await api.post('/api/v1/wifi-hacker/download-wordlist', { name });
      if (res.data.success) {
        addLog(`Wordlist descargada (${res.data.size_mb} MB)`, 'success');
        loadWordlists();
      } else {
        addLog(`Error descargando: ${res.data.error}`, 'error');
      }
    } catch (err) {
      addLog(`Error: ${err.message}`, 'error');
    }
  };

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev.slice(-100), { timestamp, message, type }]);
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      default: return 'text-gray-300';
    }
  };

  // ── Render ────────────────────────────────────────────────────────

  const toolsData = status?.tools?.tools || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <span className="text-3xl">🔓</span>
          WiFi Hacker - Auditoría Ética
        </h1>
        <span className={`px-3 py-1 rounded-full text-sm ${
          status?.available ? 'bg-green-600' : 'bg-red-600'
        }`}>
          {status?.available ? 'Herramientas Disponibles' : 'Herramientas No Disponibles'}
        </span>
      </div>

      {/* Warning */}
      <div className="bg-yellow-900/30 border border-yellow-600/50 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <h3 className="font-semibold text-yellow-400">Uso Ético Obligatorio</h3>
            <p className="text-sm text-gray-300 mt-1">
              Esta herramienta es exclusivamente para auditoría de seguridad en redes de tu propiedad
              o con autorización explícita del propietario. El acceso no autorizado a redes WiFi
              es ilegal en la mayoría de jurisdicciones.
            </p>
          </div>
        </div>
      </div>

      {/* Status & Interface */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Tools status */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">🛠️ Estado del Sistema</h3>
          <div className="space-y-2">
            {[
              ['aircrack-ng', 'Aircrack-ng'],
              ['airodump-ng', 'Airodump-ng'],
              ['aireplay-ng', 'Aireplay-ng'],
              ['airmon-ng', 'Airmon-ng'],
              ['reaver', 'Reaver'],
              ['hashcat', 'Hashcat'],
              ['hcxdumptool', 'hcxdumptool'],
            ].map(([key, label]) => (
              <div key={key} className="flex justify-between items-center">
                <span className="text-gray-400">{label}</span>
                <span className={toolsData[key] ? 'text-green-400' : 'text-red-400'}>
                  {toolsData[key] ? '✓ Instalado' : '✗ No encontrado'}
                </span>
              </div>
            ))}
            <div className="flex justify-between items-center pt-2 border-t border-gray-700">
              <span className="text-gray-400">Modo Monitor</span>
              <span className={status?.monitor_mode ? 'text-green-400' : 'text-gray-400'}>
                {status?.monitor_mode
                  ? `Habilitado${status.interface ? ' (' + status.interface + 'mon)' : ''}`
                  : 'Deshabilitado'}
              </span>
            </div>
          </div>
        </div>

        {/* Interface selector */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">📡 Interfaz WiFi</h3>
          <div className="space-y-4">
            <select
              value={selectedInterface}
              onChange={(e) => setInterface(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg p-2"
            >
              <option value="">Seleccionar interfaz...</option>
              {interfaces.map((iface, idx) => (
                <option key={idx} value={typeof iface === 'string' ? iface : iface.interface}>
                  {typeof iface === 'string' ? iface : `${iface.interface} ${iface.driver ? '- ' + iface.driver : ''}`}
                </option>
              ))}
            </select>

            <div className="flex gap-2">
              <button
                onClick={() => toggleMonitorMode(true)}
                disabled={!selectedInterface || status?.monitor_mode}
                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg text-sm"
              >
                Habilitar Monitor
              </button>
              <button
                onClick={() => toggleMonitorMode(false)}
                disabled={!status?.monitor_mode}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded-lg text-sm"
              >
                Deshabilitar Monitor
              </button>
            </div>

            <button
              onClick={() => { loadStatus(); loadInterfaces(); }}
              className="w-full px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
            >
              🔄 Actualizar
            </button>
          </div>
        </div>
      </div>

      {/* Real-time capture status banner */}
      {captureStatus && attacking && (
        <div className="bg-blue-900/30 border border-blue-600/50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="animate-pulse h-3 w-3 rounded-full bg-blue-400"></div>
              <div>
                <span className="font-semibold text-blue-300">Captura en progreso</span>
                {captureStatus.bssid && (
                  <span className="text-gray-400 ml-2 text-sm">{captureStatus.bssid}</span>
                )}
              </div>
            </div>
            <div className="text-sm text-gray-400">
              {captureStatus.elapsed != null && `${captureStatus.elapsed}s`}
              {captureStatus.deauth_count > 0 && ` | Deauths: ${captureStatus.deauth_count}`}
            </div>
          </div>
        </div>
      )}

      {/* Action buttons */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">🎯 Acciones</h3>
          {attacking && (
            <button
              onClick={stopAttack}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm"
            >
              Detener
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={scanWPSNetworks}
            disabled={scanning || !status?.monitor_mode}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg flex items-center gap-2"
          >
            {scanning ? (
              <>
                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                Escaneando...
              </>
            ) : '📶 Escanear Redes WPS'}
          </button>
        </div>

        {!status?.monitor_mode && (
          <p className="text-yellow-400 text-sm mt-3">
            ⚠️ Selecciona una interfaz y habilita el modo monitor antes de escanear.
          </p>
        )}
      </div>

      {/* WPS Networks */}
      {wpsNetworks.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">
            📡 Redes WPS Encontradas ({wpsNetworks.length})
          </h3>
          <div className="space-y-3">
            {wpsNetworks.map((network, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg">
                <div>
                  <div className="font-semibold">{network.essid || 'Hidden Network'}</div>
                  <div className="text-sm text-gray-400">
                    {network.bssid} | CH {network.channel} | {network.signal} dBm
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    WPS {network.wps_version}: {network.wps_locked ? '🔒 Bloqueado' : '🔓 Activo'}
                    {network.manufacturer && ` | ${network.manufacturer}`}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => attackPixieDust(network)}
                    disabled={attacking || network.wps_locked}
                    className="px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded text-sm"
                    title="Pixie Dust (1-5 min, solo routers vulnerables)"
                  >
                    ⚡ Pixie
                  </button>
                  <button
                    onClick={() => captureHandshake(network)}
                    disabled={attacking}
                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded text-sm"
                    title="Capturar Handshake WPA (tiempo real via WebSocket)"
                  >
                    🤝 Handshake
                  </button>
                  <button
                    onClick={() => capturePMKID(network)}
                    disabled={attacking}
                    className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded text-sm"
                    title="Capturar PMKID (sin necesidad de cliente)"
                  >
                    🔑 PMKID
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Crack section */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">🔓 Crackear Captura (Offline)</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            value={captureFile}
            onChange={(e) => setCaptureFile(e.target.value)}
            placeholder="Ruta del archivo .cap / .hash..."
            className="bg-gray-700 border border-gray-600 rounded-lg p-2 text-sm"
          />
          <select
            value={selectedWordlist}
            onChange={(e) => setSelectedWordlist(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded-lg p-2"
          >
            <option value="">-- Seleccionar wordlist --</option>
            {wordlists.map((wl, idx) => (
              <option key={idx} value={wl.path}>
                {wl.name} ({wl.size_mb} MB)
              </option>
            ))}
          </select>
          <button
            onClick={crackCapture}
            disabled={attacking || !captureFile}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded-lg"
          >
            🔓 Iniciar Cracking
          </button>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {['rockyou', 'common_passwords', 'wifi_passwords'].map((wl) => (
            <button
              key={wl}
              onClick={() => downloadWordlist(wl)}
              className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
            >
              📥 {wl}
            </button>
          ))}
        </div>
      </div>

      {/* Attack result */}
      {attackResult && (
        <div className={`bg-gray-800 rounded-lg p-6 border ${
          attackResult.success ? 'border-green-500' : 'border-red-500'
        }`}>
          <h3 className="text-lg font-semibold mb-4">
            {attackResult.success ? '✅ Ataque Exitoso' : '❌ Ataque Fallido'}
          </h3>
          <div className="space-y-2">
            {attackResult.password && (
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Contraseña:</span>
                <span className="font-mono text-green-400 text-lg">{attackResult.password}</span>
                <button
                  onClick={() => navigator.clipboard.writeText(attackResult.password)}
                  className="px-2 py-1 bg-gray-700 rounded text-sm"
                >
                  📋 Copiar
                </button>
              </div>
            )}
            {attackResult.pin && (
              <div className="flex items-center gap-2">
                <span className="text-gray-400">PIN WPS:</span>
                <span className="font-mono text-blue-400">{attackResult.pin}</span>
              </div>
            )}
            {attackResult.details?.capture_file && (
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Archivo captura:</span>
                <span className="font-mono text-gray-300 text-sm">{attackResult.details.capture_file}</span>
              </div>
            )}
            {attackResult.error && (
              <div className="text-red-400 text-sm">{attackResult.error}</div>
            )}
            {attackResult.duration_seconds && (
              <div className="text-gray-500 text-sm">
                Duración: {attackResult.duration_seconds.toFixed(1)}s
              </div>
            )}
          </div>
        </div>
      )}

      {/* Real-time logs */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">📜 Logs (tiempo real)</h3>
          <button
            onClick={() => setLogs([])}
            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
          >
            Limpiar
          </button>
        </div>
        <div className="bg-black rounded-lg p-4 h-56 overflow-y-auto font-mono text-sm">
          {logs.length > 0 ? (
            <>
              {logs.map((log, idx) => (
                <div key={idx} className={getLogColor(log.type)}>
                  <span className="text-gray-500">[{log.timestamp}]</span> {log.message}
                </div>
              ))}
              <div ref={logsEndRef} />
            </>
          ) : (
            <span className="text-gray-500">No hay logs...</span>
          )}
        </div>
      </div>
    </div>
  );
}
