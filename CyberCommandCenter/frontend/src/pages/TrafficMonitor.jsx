import { useState, useEffect } from 'react';
import api from '../services/api';

export default function Traffic() {
  const [currentRate, setCurrentRate] = useState(null);
  const [stats, setStats] = useState(null);
  const [history, setHistory] = useState([]);
  const [deviceTraffic, setDeviceTraffic] = useState([]);
  const [interfaces, setInterfaces] = useState([]);
  const [period, setPeriod] = useState('minute');
  const [loading, setLoading] = useState(true);
  const [spikeThreshold, setSpikeThreshold] = useState(50);

  useEffect(() => {
    loadTrafficData();
    const interval = setInterval(loadCurrentRate, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    loadHistory();
  }, [period]);

  const loadTrafficData = async () => {
    setLoading(true);
    try {
      const [statsRes, devicesRes, interfacesRes] = await Promise.all([
        api.get('/api/v1/traffic/stats'),
        api.get('/api/v1/traffic/devices'),
        api.get('/api/v1/traffic/interfaces')
      ]);
      
      setStats(statsRes.data);
      setCurrentRate(statsRes.data.current);
      setDeviceTraffic(devicesRes.data);
      setInterfaces(interfacesRes.data);
      setSpikeThreshold(statsRes.data.spike_threshold_mbps || 50);
    } catch (err) {
      console.error('Error loading traffic data:', err);
    }
    setLoading(false);
  };

  const loadCurrentRate = async () => {
    try {
      const res = await api.get('/api/v1/traffic/current');
      setCurrentRate(res.data);
    } catch (err) {
      console.error('Error loading current rate:', err);
    }
  };

  const loadHistory = async () => {
    try {
      const res = await api.get(`/api/v1/traffic/history?period=${period}&limit=60`);
      setHistory(res.data.data || []);
    } catch (err) {
      console.error('Error loading history:', err);
    }
  };

  const updateSpikeThreshold = async () => {
    try {
      await api.put('/api/v1/traffic/spike-threshold', { mbps: spikeThreshold });
    } catch (err) {
      console.error('Error updating threshold:', err);
    }
  };

  const formatBytes = (bytes) => {
    if (bytes >= 1024 * 1024 * 1024) {
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    }
    if (bytes >= 1024 * 1024) {
      return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
    }
    if (bytes >= 1024) {
      return `${(bytes / 1024).toFixed(2)} KB`;
    }
    return `${bytes} B`;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <span className="text-3xl">📊</span>
          Monitoreo de Tráfico
        </h1>
        <button
          onClick={loadTrafficData}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
        >
          Actualizar
        </button>
      </div>

      {/* Current Speed */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-400">Descarga</span>
            <span className="text-2xl">⬇️</span>
          </div>
          <div className="text-3xl font-bold text-green-400">
            {currentRate?.download_mbps?.toFixed(2) || '0.00'} Mbps
          </div>
          <div className="text-sm text-gray-500 mt-2">
            {formatBytes(currentRate?.download_bps || 0)}/s
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-400">Subida</span>
            <span className="text-2xl">⬆️</span>
          </div>
          <div className="text-3xl font-bold text-blue-400">
            {currentRate?.upload_mbps?.toFixed(2) || '0.00'} Mbps
          </div>
          <div className="text-sm text-gray-500 mt-2">
            {formatBytes(currentRate?.upload_bps || 0)}/s
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-400">Total Descargado</span>
            <span className="text-2xl">📥</span>
          </div>
          <div className="text-3xl font-bold text-purple-400">
            {stats?.totals?.gb_recv?.toFixed(2) || '0.00'} GB
          </div>
          <div className="text-sm text-gray-500 mt-2">
            Desde inicio del sistema
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-400">Total Subido</span>
            <span className="text-2xl">📤</span>
          </div>
          <div className="text-3xl font-bold text-orange-400">
            {stats?.totals?.gb_sent?.toFixed(2) || '0.00'} GB
          </div>
          <div className="text-sm text-gray-500 mt-2">
            Desde inicio del sistema
          </div>
        </div>
      </div>

      {/* Averages */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">📈 Promedio Último Minuto</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-gray-400 text-sm">Descarga</div>
              <div className="text-xl font-bold text-green-400">
                {stats?.averages?.last_minute?.download_mbps?.toFixed(2) || '0.00'} Mbps
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Subida</div>
              <div className="text-xl font-bold text-blue-400">
                {stats?.averages?.last_minute?.upload_mbps?.toFixed(2) || '0.00'} Mbps
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h3 className="text-lg font-semibold mb-4">📊 Promedio Última Hora</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-gray-400 text-sm">Descarga</div>
              <div className="text-xl font-bold text-green-400">
                {stats?.averages?.last_hour?.download_mbps?.toFixed(2) || '0.00'} Mbps
              </div>
            </div>
            <div>
              <div className="text-gray-400 text-sm">Subida</div>
              <div className="text-xl font-bold text-blue-400">
                {stats?.averages?.last_hour?.upload_mbps?.toFixed(2) || '0.00'} Mbps
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Network Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
          <div className="text-2xl mb-2">📦</div>
          <div className="text-gray-400 text-sm">Paquetes Recibidos</div>
          <div className="text-lg font-semibold">{stats?.totals?.packets_recv?.toLocaleString() || 0}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
          <div className="text-2xl mb-2">📤</div>
          <div className="text-gray-400 text-sm">Paquetes Enviados</div>
          <div className="text-lg font-semibold">{stats?.totals?.packets_sent?.toLocaleString() || 0}</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
          <div className="text-2xl mb-2">⚠️</div>
          <div className="text-gray-400 text-sm">Errores</div>
          <div className="text-lg font-semibold text-red-400">
            {(stats?.totals?.errors_in || 0) + (stats?.totals?.errors_out || 0)}
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
          <div className="text-2xl mb-2">🖥️</div>
          <div className="text-gray-400 text-sm">Dispositivos</div>
          <div className="text-lg font-semibold">{stats?.devices_tracked || 0}</div>
        </div>
      </div>

      {/* History Period Selector */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">📜 Historial de Tráfico</h3>
          <div className="flex gap-2">
            {['second', 'minute', 'hour'].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1 rounded ${
                  period === p
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {p === 'second' ? 'Segundos' : p === 'minute' ? 'Minutos' : 'Horas'}
              </button>
            ))}
          </div>
        </div>

        <div className="overflow-x-auto">
          <div className="h-40 flex items-end gap-1">
            {history.slice(-60).map((item, index) => {
              const maxBps = Math.max(...history.map(h => h.bytes_recv + h.bytes_sent)) || 1;
              const height = ((item.bytes_recv + item.bytes_sent) / maxBps) * 100;
              
              return (
                <div
                  key={index}
                  className="flex-1 bg-gradient-to-t from-blue-600 to-green-400 rounded-t"
                  style={{ height: `${Math.max(height, 2)}%` }}
                  title={`${new Date(item.timestamp).toLocaleTimeString()}: ${formatBytes(item.bytes_recv + item.bytes_sent)}`}
                />
              );
            })}
          </div>
        </div>
      </div>

      {/* Interfaces */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">🌐 Interfaces de Red</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 border-b border-gray-700">
                <th className="text-left py-2">Interfaz</th>
                <th className="text-left py-2">IP</th>
                <th className="text-right py-2">Recibido</th>
                <th className="text-right py-2">Enviado</th>
                <th className="text-right py-2">Paquetes In</th>
                <th className="text-right py-2">Paquetes Out</th>
              </tr>
            </thead>
            <tbody>
              {interfaces.map((iface, index) => (
                <tr key={index} className="border-b border-gray-700/50">
                  <td className="py-2 font-medium">{iface.interface}</td>
                  <td className="py-2 text-gray-400">{iface.ip || '-'}</td>
                  <td className="py-2 text-right text-green-400">{formatBytes(iface.bytes_recv)}</td>
                  <td className="py-2 text-right text-blue-400">{formatBytes(iface.bytes_sent)}</td>
                  <td className="py-2 text-right">{iface.packets_recv?.toLocaleString()}</td>
                  <td className="py-2 text-right">{iface.packets_sent?.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Device Traffic */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">📱 Tráfico por Dispositivo</h3>
        <div className="space-y-3">
          {deviceTraffic.length > 0 ? (
            deviceTraffic.map((device, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg">
                <div>
                  <div className="font-medium">{device.name || device.ip}</div>
                  <div className="text-sm text-gray-400">{device.mac || 'Sin MAC'}</div>
                </div>
                <div className="flex gap-6 text-sm">
                  <div>
                    <span className="text-gray-400">⬇️</span>
                    <span className="ml-1 text-green-400">{device.mb_recv} MB</span>
                  </div>
                  <div>
                    <span className="text-gray-400">⬆️</span>
                    <span className="ml-1 text-blue-400">{device.mb_sent} MB</span>
                  </div>
                  <div className="text-gray-400">
                    {device.connections} conexiones
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center text-gray-400 py-4">
              No hay datos de tráfico por dispositivo
            </div>
          )}
        </div>
      </div>

      {/* Spike Threshold */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold mb-4">⚡ Umbral de Alerta de Picos</h3>
        <div className="flex items-center gap-4">
          <input
            type="range"
            min="10"
            max="500"
            value={spikeThreshold}
            onChange={(e) => setSpikeThreshold(Number(e.target.value))}
            className="flex-1"
          />
          <span className="text-xl font-bold w-24 text-center">{spikeThreshold} Mbps</span>
          <button
            onClick={updateSpikeThreshold}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
          >
            Guardar
          </button>
        </div>
        <p className="text-sm text-gray-400 mt-2">
          Se generará una alerta cuando el tráfico supere este umbral
        </p>
      </div>
    </div>
  );
}
