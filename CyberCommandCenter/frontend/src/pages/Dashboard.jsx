import React, { useState, useEffect } from 'react'
import { 
  Monitor, Shield, Wifi, AlertTriangle, Ghost,
  ArrowUp, ArrowDown, RefreshCw, Activity, Users
} from 'lucide-react'
import { getDashboardStats, scanNetwork, getAlerts } from '../services/api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

function StatCard({ icon: Icon, label, value, subvalue, color, trend }) {
  const colors = {
    green: 'from-cyber-accent/20 to-transparent border-cyber-accent/30 text-cyber-accent',
    blue: 'from-cyber-accent2/20 to-transparent border-cyber-accent2/30 text-cyber-accent2',
    orange: 'from-cyber-warning/20 to-transparent border-cyber-warning/30 text-cyber-warning',
    red: 'from-cyber-danger/20 to-transparent border-cyber-danger/30 text-cyber-danger',
    purple: 'from-cyber-purple/20 to-transparent border-cyber-purple/30 text-cyber-purple',
  }

  return (
    <div className={`cyber-card p-6 bg-gradient-to-br ${colors[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-400 text-sm font-medium">{label}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
          {subvalue && (
            <p className="text-sm text-gray-500 mt-1">{subvalue}</p>
          )}
        </div>
        <div className={`p-3 rounded-xl bg-gradient-to-br ${colors[color].split(' ')[0]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      {trend !== undefined && (
        <div className="mt-4 flex items-center gap-2">
          {trend >= 0 ? (
            <ArrowUp className="w-4 h-4 text-cyber-accent" />
          ) : (
            <ArrowDown className="w-4 h-4 text-cyber-danger" />
          )}
          <span className={trend >= 0 ? 'text-cyber-accent' : 'text-cyber-danger'}>
            {Math.abs(trend)}%
          </span>
          <span className="text-gray-500 text-sm">vs última hora</span>
        </div>
      )}
    </div>
  )
}

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [isScanning, setIsScanning] = useState(false)
  const [trafficData, setTrafficData] = useState([])

  useEffect(() => {
    loadData()
    // Generate mock traffic data
    generateTrafficData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [statsRes, alertsRes] = await Promise.all([
        getDashboardStats(),
        getAlerts(10)
      ])
      setStats(statsRes.data)
      setAlerts(alertsRes.data)
    } catch (err) {
      console.error('Error loading dashboard:', err)
    }
  }

  const generateTrafficData = () => {
    const data = []
    for (let i = 0; i < 24; i++) {
      data.push({
        time: `${i}:00`,
        download: Math.floor(Math.random() * 100) + 20,
        upload: Math.floor(Math.random() * 50) + 10,
      })
    }
    setTrafficData(data)
  }

  const handleScan = async () => {
    setIsScanning(true)
    try {
      await scanNetwork('arp')
      await loadData()
    } catch (err) {
      console.error('Scan error:', err)
    }
    setIsScanning(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-gray-400 mt-1">Resumen de tu red y seguridad</p>
        </div>
        <button
          onClick={handleScan}
          disabled={isScanning}
          className="cyber-btn-primary flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${isScanning ? 'animate-spin' : ''}`} />
          {isScanning ? 'Escaneando...' : 'Escanear Red'}
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={Monitor}
          label="Dispositivos Online"
          value={stats?.online_devices || 0}
          subvalue={`${stats?.total_devices || 0} totales`}
          color="green"
        />
        <StatCard
          icon={Shield}
          label="Dispositivos Seguros"
          value={stats?.trusted_devices || 0}
          subvalue="Verificados"
          color="blue"
        />
        <StatCard
          icon={AlertTriangle}
          label="Alertas"
          value={stats?.unread_alerts || 0}
          subvalue="Sin leer"
          color={stats?.unread_alerts > 0 ? 'orange' : 'green'}
        />
        <StatCard
          icon={Ghost}
          label="Pranks Activos"
          value={stats?.active_pranks || 0}
          subvalue="En ejecución"
          color="purple"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Traffic Chart */}
        <div className="lg:col-span-2 cyber-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Tráfico de Red (24h)</h2>
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-cyber-accent" />
                <span className="text-gray-400">Download</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-cyber-accent2" />
                <span className="text-gray-400">Upload</span>
              </div>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trafficData}>
                <defs>
                  <linearGradient id="colorDownload" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00ff88" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00ff88" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorUpload" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00d4ff" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#4b5563" fontSize={12} />
                <YAxis stroke="#4b5563" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: '#0a0a0f',
                    border: '1px solid #1f2937',
                    borderRadius: '8px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="download"
                  stroke="#00ff88"
                  fillOpacity={1}
                  fill="url(#colorDownload)"
                />
                <Area
                  type="monotone"
                  dataKey="upload"
                  stroke="#00d4ff"
                  fillOpacity={1}
                  fill="url(#colorUpload)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Network Info */}
        <div className="cyber-card p-6">
          <h2 className="text-lg font-semibold mb-4">Info de Red</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center py-2 border-b border-gray-800">
              <span className="text-gray-400">IP Local</span>
              <span className="font-mono text-cyber-accent">
                {stats?.network_info?.local_ip || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-800">
              <span className="text-gray-400">Gateway</span>
              <span className="font-mono text-cyber-accent">
                {stats?.network_info?.gateway_ip || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-800">
              <span className="text-gray-400">Rango</span>
              <span className="font-mono text-cyber-accent2">
                {stats?.network_info?.network_range || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-gray-800">
              <span className="text-gray-400">Interfaz</span>
              <span className="font-mono text-gray-300">
                {stats?.network_info?.interface || 'Auto'}
              </span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-gray-400">Scapy</span>
              <span className={stats?.network_info?.scapy_available ? 'text-cyber-accent' : 'text-cyber-danger'}>
                {stats?.network_info?.scapy_available ? '✓ Disponible' : '✗ No disponible'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="cyber-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Alertas Recientes</h2>
          <a href="/logs" className="text-cyber-accent hover:underline text-sm">
            Ver todas →
          </a>
        </div>
        <div className="space-y-3">
          {alerts.length > 0 ? (
            alerts.slice(0, 5).map((alert, i) => (
              <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-gray-800/30 hover:bg-gray-800/50 transition-colors">
                <div className={`w-2 h-2 rounded-full ${
                  alert.severity === 'high' || alert.severity === 'critical' ? 'bg-cyber-danger' :
                  alert.severity === 'medium' ? 'bg-cyber-warning' :
                  'bg-cyber-accent'
                }`} />
                <div className="flex-1">
                  <p className="font-medium">{alert.title}</p>
                  <p className="text-sm text-gray-400">{alert.description}</p>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(alert.timestamp).toLocaleTimeString()}
                </span>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No hay alertas recientes</p>
              <p className="text-sm mt-1">Tu red está segura</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
