import React, { useState, useEffect } from 'react'
import { 
  Activity, Play, Pause, Download, Filter,
  ArrowUpRight, ArrowDownLeft, Wifi, AlertTriangle
} from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import api from '../services/api'

function Traffic() {
  const [sniffing, setSniffing] = useState(false)
  const [packets, setPackets] = useState([])
  const [stats, setStats] = useState({
    totalPackets: 0,
    bytesIn: 0,
    bytesOut: 0,
    protocols: {}
  })
  const [filter, setFilter] = useState('')

  const trafficData = [
    { time: '00:00', in: 45, out: 32 },
    { time: '00:05', in: 52, out: 41 },
    { time: '00:10', in: 38, out: 25 },
    { time: '00:15', in: 65, out: 48 },
    { time: '00:20', in: 71, out: 55 },
    { time: '00:25', in: 48, out: 38 },
    { time: '00:30', in: 55, out: 42 },
  ]

  const protocolData = [
    { name: 'TCP', value: 45, color: '#00f0ff' },
    { name: 'UDP', value: 25, color: '#a855f7' },
    { name: 'HTTP', value: 15, color: '#22c55e' },
    { name: 'DNS', value: 10, color: '#f59e0b' },
    { name: 'Otros', value: 5, color: '#6b7280' },
  ]

  const toggleSniffing = async () => {
    try {
      if (sniffing) {
        await api.post('/traffic/stop')
      } else {
        await api.post('/traffic/start')
      }
      setSniffing(!sniffing)
    } catch (error) {
      console.error('Error toggling sniffer:', error)
    }
  }

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <Activity className="w-8 h-8 text-cyber-accent" />
            Análisis de Tráfico
          </h1>
          <p className="text-gray-400 mt-1">Monitoreo de paquetes en tiempo real</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={toggleSniffing}
            className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${
              sniffing 
                ? 'bg-cyber-danger text-white' 
                : 'bg-cyber-accent text-gray-900'
            }`}
          >
            {sniffing ? (
              <>
                <Pause className="w-4 h-4" />
                Detener Captura
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Iniciar Captura
              </>
            )}
          </button>
        </div>
      </div>

      {/* Live Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="cyber-card p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <Wifi className="w-4 h-4" />
            Estado
          </div>
          <p className={`text-xl font-bold mt-1 ${sniffing ? 'text-cyber-accent' : 'text-gray-500'}`}>
            {sniffing ? 'Capturando' : 'Detenido'}
          </p>
        </div>
        
        <div className="cyber-card p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <Activity className="w-4 h-4" />
            Paquetes
          </div>
          <p className="text-xl font-bold mt-1">{stats.totalPackets.toLocaleString()}</p>
        </div>
        
        <div className="cyber-card p-4">
          <div className="flex items-center gap-2 text-green-400 text-sm">
            <ArrowDownLeft className="w-4 h-4" />
            Entrada
          </div>
          <p className="text-xl font-bold mt-1">{formatBytes(stats.bytesIn)}</p>
        </div>
        
        <div className="cyber-card p-4">
          <div className="flex items-center gap-2 text-cyber-accent text-sm">
            <ArrowUpRight className="w-4 h-4" />
            Salida
          </div>
          <p className="text-xl font-bold mt-1">{formatBytes(stats.bytesOut)}</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Traffic Timeline */}
        <div className="cyber-card p-6 lg:col-span-2">
          <h3 className="font-semibold mb-4">Tráfico en Tiempo Real</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={trafficData}>
              <defs>
                <linearGradient id="colorIn" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorOut" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#00f0ff" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="time" stroke="#6b7280" fontSize={12} />
              <YAxis stroke="#6b7280" fontSize={12} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#1f2937', 
                  border: '1px solid #374151',
                  borderRadius: '8px'
                }}
              />
              <Area 
                type="monotone" 
                dataKey="in" 
                stroke="#22c55e" 
                fill="url(#colorIn)" 
                name="Entrada"
              />
              <Area 
                type="monotone" 
                dataKey="out" 
                stroke="#00f0ff" 
                fill="url(#colorOut)" 
                name="Salida"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Protocol Distribution */}
        <div className="cyber-card p-6">
          <h3 className="font-semibold mb-4">Distribución por Protocolo</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={protocolData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={70}
                dataKey="value"
              >
                {protocolData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap justify-center gap-3 mt-4">
            {protocolData.map((item) => (
              <div key={item.name} className="flex items-center gap-2 text-sm">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-gray-400">{item.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Packet List */}
      <div className="cyber-card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold">Paquetes Capturados</h3>
          <div className="flex items-center gap-3">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Filtrar (ej: tcp, 192.168.1.1)"
                className="bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2 
                         focus:outline-none focus:border-cyber-accent text-sm w-64"
              />
            </div>
            <button className="cyber-btn-secondary text-sm">
              <Download className="w-4 h-4 mr-2" />
              Exportar PCAP
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Tiempo</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Origen</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Destino</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Protocolo</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Tamaño</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Info</th>
              </tr>
            </thead>
            <tbody>
              {packets.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-8 text-gray-500">
                    {sniffing 
                      ? 'Esperando paquetes...' 
                      : 'Inicia la captura para ver paquetes'}
                  </td>
                </tr>
              ) : (
                packets.map((pkt, i) => (
                  <tr key={i} className="border-b border-gray-800 hover:bg-gray-800/30">
                    <td className="py-3 px-4 font-mono text-xs">{pkt.time}</td>
                    <td className="py-3 px-4 font-mono text-xs">{pkt.src}</td>
                    <td className="py-3 px-4 font-mono text-xs">{pkt.dst}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 rounded text-xs bg-cyber-accent/20 text-cyber-accent">
                        {pkt.protocol}
                      </span>
                    </td>
                    <td className="py-3 px-4">{pkt.size} B</td>
                    <td className="py-3 px-4 text-gray-400">{pkt.info}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Warning */}
      <div className="p-4 rounded-lg bg-cyber-warning/10 border border-cyber-warning/30">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-cyber-warning flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-cyber-warning">Aviso Legal</p>
            <p className="text-sm text-gray-400 mt-1">
              El análisis de tráfico de red solo debe realizarse en redes propias o con autorización explícita.
              Capturar tráfico de terceros sin permiso puede ser ilegal.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Traffic
