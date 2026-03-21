import { useState, useEffect } from 'react';
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
      setInterfaces(res.data);
    } catch (err) {
      console.error('Error loading interfaces:', err);
    }
  };

  const loadWordlists = async () => {
    try {
      const res = await api.get('/api/v1/wifi-hacker/wordlists');
      setWordlists(res.data);
    } catch (err) {
      console.error('Error loading wordlists:', err);
    }
  };

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
      addLog(res.data.success ? 'Modo monitor actualizado' : 'Error actualizando modo monitor', 
             res.data.success ? 'success' : 'error');
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
    addLog(`Iniciando ataque Pixie Dust en ${network.ssid || network.bssid}...`);
    
    try {
      const res = await api.post('/api/v1/wifi-hacker/attack/wps-pixie', {
        bssid: network.bssid,
        channel: network.channel
      });
      setAttackResult(res.data);
      if (res.data.success) {
        addLog(`PIN WPS encontrado: ${res.data.wps_pin}`, 'success');
        if (res.data.password) {
          addLog(`Contraseña WiFi: ${res.data.password}`, 'success');
        }
      } else {
        addLog(`Ataque fallido: ${res.data.error || 'Sin resultado'}`, 'error');
      }
    } catch (err) {
      addLog(`Error en ataque: ${err.message}`, 'error');
    }
    setAttacking(false);
  };

  const captureHandshake = async (network) => {
    setAttacking(true);
    setAttackResult(null);
    addLog(`Capturando handshake de ${network.ssid || network.bssid}...`);
    
    try {
      const res = await api.post('/api/v1/wifi-hacker/capture/handshake', {
        bssid: network.bssid,
        channel: network.channel,
        timeout: 120
      });
      setAttackResult(res.data);
      if (res.data.success) {
        addLog(`Handshake capturado: ${res.data.capture_file}`, 'success');
        setCaptureFile(res.data.capture_file);
      } else {
        addLog(`No se pudo capturar handshake`, 'error');
      }
    } catch (err) {
      addLog(`Error: ${err.message}`, 'error');
    }
    setAttacking(false);
  };

  const capturePMKID = async (network) => {
    setAttacking(true);
    setAttackResult(null);
    addLog(`Capturando PMKID de ${network.ssid || network.bssid}...`);
    
    try {
      const res = await api.post('/api/v1/wifi-hacker/capture/pmkid', {
        bssid: network.bssid,
        channel: network.channel,
        timeout: 60
      });
      setAttackResult(res.data);
      if (res.data.success) {
        addLog(`PMKID capturado: ${res.data.pmkid_file}`, 'success');
        setCaptureFile(res.data.pmkid_file);
      } else {
        addLog(`No se pudo capturar PMKID`, 'error');
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
      });
      setAttackResult(res.data);
      if (res.data.success) {
        addLog(`Contraseña encontrada: ${res.data.password}`, 'success');
      } else {
        addLog(`Contraseña no encontrada`, 'error');
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
    } catch (err) {
      addLog(`Error deteniendo ataque: ${err.message}`, 'error');
    }
  };

  const downloadWordlist = async (name) => {
    addLog(`Descargando wordlist ${name}...`);
    try {
      const res = await api.post('/api/v1/wifi-hacker/download-wordlist', { name });
      if (res.data.success) {
        addLog(`Wordlist descargada: ${res.data.path}`, 'success');
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
    setLogs(prev => [...prev.slice(-50), { timestamp, message, type }]);
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'success': return 'text-green-400';
      case 'error': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      default: return 'text-gray-300';
    }
  };

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
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">🛠️ Estado del Sistema</h3>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Aircrack-ng</span>
              <span className={status?.tools?.aircrack ? 'text-green-400' : 'text-red-400'}>
                {status?.tools?.aircrack ? '✓ Instalado' : '✗ No encontrado'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Reaver</span>
              <span className={status?.tools?.reaver ? 'text-green-400' : 'text-red-400'}>
                {status?.tools?.reaver ? '✓ Instalado' : '✗ No encontrado'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Hashcat</span>
              <span className={status?.tools?.hashcat ? 'text-green-400' : 'text-red-400'}>
                {status?.tools?.hashcat ? '✓ Instalado' : '✗ No encontrado'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Modo Monitor</span>
              <span className={status?.monitor_mode ? 'text-green-400' : 'text-gray-400'}>
                {status?.monitor_mode ? 'Habilitado' : 'Deshabilitado'}
              </span>
            </div>
          </div>
        </div>

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
                <option key={idx} value={iface.interface}>
                  {iface.interface} - {iface.driver || 'Unknown'} ({iface.chipset || 'N/A'})
                </option>
              ))}
            </select>

            <div className="flex gap-2">
              <button
                onClick={() => toggleMonitorMode(true)}
                disabled={!selectedInterface}
                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg"
              >
                Habilitar Monitor
              </button>
              <button
                onClick={() => toggleMonitorMode(false)}
                disabled={!status?.monitor_mode}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded-lg"
              >
                Deshabilitar Monitor
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Attack Buttons */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">🎯 Acciones</h3>
          {attacking && (
            <button
              onClick={stopAttack}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg"
            >
              Detener Ataque
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
            ) : (
              <>📶 Escanear Redes WPS</>
            )}
          </button>
        </div>
      </div>

      {/* Networks List */}
      {wpsNetworks.length > 0 && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">📡 Redes WPS Encontradas</h3>
          
          <div className="space-y-3">
            {wpsNetworks.map((network, idx) => (
              <div key={idx} className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg">
                <div>
                  <div className="font-semibold">{network.ssid || 'Hidden Network'}</div>
                  <div className="text-sm text-gray-400">
                    {network.bssid} | CH {network.channel} | {network.signal}dBm
                  </div>
                  <div className="text-xs text-gray-500">
                    WPS: {network.wps_locked ? '🔒 Bloqueado' : '🔓 Abierto'} | 
                    {network.encryption}
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => attackPixieDust(network)}
                    disabled={attacking || network.wps_locked}
                    className="px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded text-sm"
                    title="Pixie Dust Attack (rápido)"
                  >
                    ⚡ Pixie
                  </button>
                  <button
                    onClick={() => captureHandshake(network)}
                    disabled={attacking}
                    className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded text-sm"
                    title="Capturar Handshake"
                  >
                    🤝 Handshake
                  </button>
                  <button
                    onClick={() => capturePMKID(network)}
                    disabled={attacking}
                    className="px-3 py-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded text-sm"
                    title="Capturar PMKID"
                  >
                    🔑 PMKID
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Crack Section */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">🔓 Crackear Captura</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            value={captureFile}
            onChange={(e) => setCaptureFile(e.target.value)}
            placeholder="Ruta del archivo de captura..."
            className="bg-gray-700 border border-gray-600 rounded-lg p-2"
          />
          
          <select
            value={selectedWordlist}
            onChange={(e) => setSelectedWordlist(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded-lg p-2"
          >
            <option value="">Wordlist por defecto</option>
            {wordlists.map((wl, idx) => (
              <option key={idx} value={wl.path}>
                {wl.name} ({(wl.size / 1024 / 1024).toFixed(1)} MB)
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

        <div className="mt-4 flex gap-2">
          <button
            onClick={() => downloadWordlist('rockyou')}
            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
          >
            📥 Descargar RockYou
          </button>
        </div>
      </div>

      {/* Attack Result */}
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
            {attackResult.wps_pin && (
              <div className="flex items-center gap-2">
                <span className="text-gray-400">PIN WPS:</span>
                <span className="font-mono text-blue-400">{attackResult.wps_pin}</span>
              </div>
            )}
            {attackResult.capture_file && (
              <div className="flex items-center gap-2">
                <span className="text-gray-400">Archivo:</span>
                <span className="font-mono text-gray-300">{attackResult.capture_file}</span>
              </div>
            )}
            {attackResult.error && (
              <div className="text-red-400">{attackResult.error}</div>
            )}
          </div>
        </div>
      )}

      {/* Logs */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">📜 Logs</h3>
          <button
            onClick={() => setLogs([])}
            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
          >
            Limpiar
          </button>
        </div>
        
        <div className="bg-black rounded-lg p-4 h-48 overflow-y-auto font-mono text-sm">
          {logs.length > 0 ? (
            logs.map((log, idx) => (
              <div key={idx} className={getLogColor(log.type)}>
                <span className="text-gray-500">[{log.timestamp}]</span> {log.message}
              </div>
            ))
          ) : (
            <span className="text-gray-500">No hay logs...</span>
          )}
        </div>
      </div>
    </div>
  );
}
