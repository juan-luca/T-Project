import React, { useState, useEffect } from 'react'
import { 
  FileText, Search, Filter, Download, Trash2,
  AlertTriangle, CheckCircle, Info, XCircle,
  Calendar, Clock
} from 'lucide-react'
import api from '../services/api'

function Logs() {
  const [logs, setLogs] = useState([])
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')
  const [dateRange, setDateRange] = useState('today')

  useEffect(() => {
    fetchLogs()
  }, [filter, dateRange])

  const fetchLogs = async () => {
    try {
      const response = await api.get('/logs', { params: { filter, dateRange } })
      setLogs(response.data.logs || [])
    } catch (error) {
      // Mock data for demo
      setLogs([
        { id: 1, timestamp: '2024-01-15 14:32:15', type: 'info', category: 'network', message: 'Escaneo de red completado - 8 dispositivos encontrados' },
        { id: 2, timestamp: '2024-01-15 14:30:00', type: 'warning', category: 'security', message: 'Nuevo dispositivo detectado: iPhone-Unknown (192.168.1.45)' },
        { id: 3, timestamp: '2024-01-15 14:25:30', type: 'success', category: 'prank', message: 'Rickroll ejecutado en dispositivo: Desktop-Gaming' },
        { id: 4, timestamp: '2024-01-15 14:20:00', type: 'error', category: 'wifi', message: 'Error capturando handshake: interface no encontrada' },
        { id: 5, timestamp: '2024-01-15 14:15:45', type: 'info', category: 'deauth', message: 'Ataque deauth iniciado en: TV-Samsung' },
        { id: 6, timestamp: '2024-01-15 14:10:00', type: 'warning', category: 'security', message: 'Puerto 22 (SSH) abierto detectado en router' },
        { id: 7, timestamp: '2024-01-15 14:05:00', type: 'success', category: 'network', message: 'Dispositivo bloqueado exitosamente: Unknown-Device' },
        { id: 8, timestamp: '2024-01-15 14:00:00', type: 'info', category: 'system', message: 'Sistema iniciado correctamente' },
      ])
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-cyber-accent" />
      case 'warning': return <AlertTriangle className="w-4 h-4 text-cyber-warning" />
      case 'error': return <XCircle className="w-4 h-4 text-cyber-danger" />
      default: return <Info className="w-4 h-4 text-cyber-accent2" />
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'success': return 'border-cyber-accent/30 bg-cyber-accent/5'
      case 'warning': return 'border-cyber-warning/30 bg-cyber-warning/5'
      case 'error': return 'border-cyber-danger/30 bg-cyber-danger/5'
      default: return 'border-gray-700 bg-gray-800/30'
    }
  }

  const getCategoryBadge = (category) => {
    const colors = {
      network: 'bg-blue-500/20 text-blue-400',
      security: 'bg-red-500/20 text-red-400',
      prank: 'bg-purple-500/20 text-purple-400',
      wifi: 'bg-green-500/20 text-green-400',
      deauth: 'bg-orange-500/20 text-orange-400',
      system: 'bg-gray-500/20 text-gray-400',
    }
    return colors[category] || 'bg-gray-500/20 text-gray-400'
  }

  const filteredLogs = logs.filter(log => {
    const matchesFilter = filter === 'all' || log.type === filter
    const matchesSearch = log.message.toLowerCase().includes(search.toLowerCase()) ||
                         log.category.toLowerCase().includes(search.toLowerCase())
    return matchesFilter && matchesSearch
  })

  const exportLogs = () => {
    const data = JSON.stringify(filteredLogs, null, 2)
    const blob = new Blob([data], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `logs-${new Date().toISOString().split('T')[0]}.json`
    a.click()
  }

  const clearLogs = async () => {
    if (confirm('¿Estás seguro de que quieres eliminar todos los logs?')) {
      try {
        await api.delete('/logs')
        setLogs([])
      } catch (error) {
        console.error('Error clearing logs:', error)
      }
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <FileText className="w-8 h-8 text-cyber-accent" />
            Registro de Actividad
          </h1>
          <p className="text-gray-400 mt-1">Historial de todas las acciones del sistema</p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={exportLogs} className="cyber-btn-secondary text-sm">
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </button>
          <button onClick={clearLogs} className="cyber-btn-danger text-sm">
            <Trash2 className="w-4 h-4 mr-2" />
            Limpiar
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="cyber-card p-4">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar en logs..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-2 
                       focus:outline-none focus:border-cyber-accent"
            />
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 
                       focus:outline-none focus:border-cyber-accent"
            >
              <option value="all">Todos los tipos</option>
              <option value="info">Info</option>
              <option value="success">Éxito</option>
              <option value="warning">Advertencia</option>
              <option value="error">Error</option>
            </select>
          </div>

          {/* Date Range */}
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-gray-500" />
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 
                       focus:outline-none focus:border-cyber-accent"
            >
              <option value="today">Hoy</option>
              <option value="week">Última semana</option>
              <option value="month">Último mes</option>
              <option value="all">Todo</option>
            </select>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="cyber-card p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <Info className="w-4 h-4 text-cyber-accent2" />
            Info
          </div>
          <p className="text-2xl font-bold mt-1">
            {logs.filter(l => l.type === 'info').length}
          </p>
        </div>
        <div className="cyber-card p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <CheckCircle className="w-4 h-4 text-cyber-accent" />
            Éxito
          </div>
          <p className="text-2xl font-bold mt-1 text-cyber-accent">
            {logs.filter(l => l.type === 'success').length}
          </p>
        </div>
        <div className="cyber-card p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <AlertTriangle className="w-4 h-4 text-cyber-warning" />
            Advertencias
          </div>
          <p className="text-2xl font-bold mt-1 text-cyber-warning">
            {logs.filter(l => l.type === 'warning').length}
          </p>
        </div>
        <div className="cyber-card p-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <XCircle className="w-4 h-4 text-cyber-danger" />
            Errores
          </div>
          <p className="text-2xl font-bold mt-1 text-cyber-danger">
            {logs.filter(l => l.type === 'error').length}
          </p>
        </div>
      </div>

      {/* Log List */}
      <div className="cyber-card p-6">
        <div className="space-y-3">
          {filteredLogs.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No hay logs que mostrar</p>
            </div>
          ) : (
            filteredLogs.map((log) => (
              <div 
                key={log.id} 
                className={`p-4 rounded-lg border ${getTypeColor(log.type)} transition-all hover:bg-gray-800/50`}
              >
                <div className="flex items-start gap-3">
                  {getTypeIcon(log.type)}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 flex-wrap">
                      <span className={`text-xs px-2 py-1 rounded ${getCategoryBadge(log.category)}`}>
                        {log.category}
                      </span>
                      <span className="text-xs text-gray-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {log.timestamp}
                      </span>
                    </div>
                    <p className="mt-2 text-gray-300">{log.message}</p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default Logs
