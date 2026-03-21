import React, { useState, useEffect } from 'react'
import { 
  Wrench, Terminal, Globe, Search, Zap, Wifi, Key, Network, Activity,
  Play, Loader2, CheckCircle, XCircle, Download, Upload, Clock, Cpu,
  RefreshCw, Trash2, Eye, EyeOff, Copy, Server, BarChart3, ArrowRight
} from 'lucide-react'
import api from '../services/api'

function Tools() {
  const [activeTab, setActiveTab] = useState('speedtest')
  const [running, setRunning] = useState(false)
  const [results, setResults] = useState(null)
  
  // Speed Test
  const [speedTestResult, setSpeedTestResult] = useState(null)
  const [testingSpeed, setTestingSpeed] = useState(false)
  
  // WiFi Passwords
  const [wifiPasswords, setWifiPasswords] = useState([])
  const [showPasswords, setShowPasswords] = useState({})
  const [loadingPasswords, setLoadingPasswords] = useState(false)
  
  // Connections
  const [connections, setConnections] = useState([])
  const [connectionStats, setConnectionStats] = useState(null)
  const [loadingConnections, setLoadingConnections] = useState(false)
  
  // Processes
  const [processes, setProcesses] = useState([])
  const [loadingProcesses, setLoadingProcesses] = useState(false)
  
  // Ping
  const [pingTarget, setPingTarget] = useState('')
  const [pingResults, setPingResults] = useState([])
  
  // Network Interfaces
  const [interfaces, setInterfaces] = useState([])
  
  // ARP Table
  const [arpTable, setArpTable] = useState([])
  
  // DNS Cache
  const [dnsCache, setDnsCache] = useState([])

  const tools = [
    { id: 'speedtest', name: 'Speed Test', icon: Zap, description: 'Test de velocidad' },
    { id: 'wifipass', name: 'WiFi Pass', icon: Key, description: 'Contraseñas guardadas' },
    { id: 'connections', name: 'Conexiones', icon: Network, description: 'Conexiones activas' },
    { id: 'processes', name: 'Procesos', icon: Cpu, description: 'Uso de red por proceso' },
    { id: 'ping', name: 'Ping Monitor', icon: Activity, description: 'Monitor de latencia' },
    { id: 'interfaces', name: 'Interfaces', icon: Server, description: 'Interfaces de red' },
    { id: 'arp', name: 'ARP Table', icon: BarChart3, description: 'Tabla ARP del sistema' },
    { id: 'dns', name: 'DNS Cache', icon: Globe, description: 'Caché DNS local' },
  ]

  // Speed Test
  const runSpeedTest = async () => {
    setTestingSpeed(true)
    setSpeedTestResult(null)
    try {
      const response = await api.post('/system/speed-test', { include_upload: true })
      setSpeedTestResult(response.data)
    } catch (error) {
      setSpeedTestResult({ error: error.response?.data?.error || 'Error en speed test' })
    } finally {
      setTestingSpeed(false)
    }
  }

  // WiFi Passwords
  const loadWifiPasswords = async () => {
    setLoadingPasswords(true)
    try {
      const response = await api.get('/system/wifi-passwords')
      setWifiPasswords(response.data)
    } catch (error) {
      console.error('Error loading WiFi passwords:', error)
    } finally {
      setLoadingPasswords(false)
    }
  }

  const togglePassword = (name) => {
    setShowPasswords(prev => ({ ...prev, [name]: !prev[name] }))
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
  }

  // Connections
  const loadConnections = async () => {
    setLoadingConnections(true)
    try {
      const [connResponse, statsResponse] = await Promise.all([
        api.get('/system/connections'),
        api.get('/system/connections/stats')
      ])
      setConnections(connResponse.data)
      setConnectionStats(statsResponse.data)
    } catch (error) {
      console.error('Error loading connections:', error)
    } finally {
      setLoadingConnections(false)
    }
  }

  // Processes
  const loadProcesses = async () => {
    setLoadingProcesses(true)
    try {
      const response = await api.get('/system/processes')
      setProcesses(response.data)
    } catch (error) {
      console.error('Error loading processes:', error)
    } finally {
      setLoadingProcesses(false)
    }
  }

  // Ping
  const runPing = async () => {
    if (!pingTarget) return
    setRunning(true)
    try {
      const response = await api.post('/system/ping', { host: pingTarget, count: 4 })
      setPingResults(prev => [response.data, ...prev].slice(0, 20))
    } catch (error) {
      setPingResults(prev => [{ host: pingTarget, error: error.message, timestamp: new Date().toISOString() }, ...prev].slice(0, 20))
    } finally {
      setRunning(false)
    }
  }

  // Interfaces
  const loadInterfaces = async () => {
    try {
      const response = await api.get('/system/interfaces')
      setInterfaces(response.data)
    } catch (error) {
      console.error('Error loading interfaces:', error)
    }
  }

  // ARP Table
  const loadArpTable = async () => {
    try {
      const response = await api.get('/system/arp-table')
      setArpTable(response.data)
    } catch (error) {
      console.error('Error loading ARP table:', error)
    }
  }

  const flushArp = async () => {
    try {
      await api.post('/system/arp-flush')
      loadArpTable()
    } catch (error) {
      console.error('Error flushing ARP:', error)
    }
  }

  // DNS Cache
  const loadDnsCache = async () => {
    try {
      const response = await api.get('/system/dns-cache')
      setDnsCache(response.data)
    } catch (error) {
      console.error('Error loading DNS cache:', error)
    }
  }

  const flushDns = async () => {
    try {
      await api.post('/system/dns-flush')
      setDnsCache([])
      loadDnsCache()
    } catch (error) {
      console.error('Error flushing DNS:', error)
    }
  }

  // Load data based on active tab
  useEffect(() => {
    switch (activeTab) {
      case 'wifipass':
        loadWifiPasswords()
        break
      case 'connections':
        loadConnections()
        break
      case 'processes':
        loadProcesses()
        break
      case 'interfaces':
        loadInterfaces()
        break
      case 'arp':
        loadArpTable()
        break
      case 'dns':
        loadDnsCache()
        break
    }
  }, [activeTab])

  const renderSpeedTest = () => (
    <div className="space-y-6">
      <div className="text-center">
        <button
          onClick={runSpeedTest}
          disabled={testingSpeed}
          className={`w-48 h-48 rounded-full border-4 transition-all duration-300 flex flex-col items-center justify-center mx-auto ${
            testingSpeed 
              ? 'border-cyber-accent animate-pulse bg-cyber-accent/20' 
              : 'border-gray-600 hover:border-cyber-accent hover:bg-cyber-accent/10'
          }`}
        >
          {testingSpeed ? (
            <>
              <Loader2 className="w-12 h-12 animate-spin text-cyber-accent mb-2" />
              <span className="text-sm text-gray-400">Testeando...</span>
            </>
          ) : (
            <>
              <Zap className="w-12 h-12 text-cyber-accent mb-2" />
              <span className="text-lg font-semibold">Iniciar Test</span>
            </>
          )}
        </button>
      </div>

      {speedTestResult && !speedTestResult.error && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="cyber-card p-6 text-center">
            <Download className="w-8 h-8 text-cyber-accent mx-auto mb-2" />
            <p className="text-gray-400 text-sm">Descarga</p>
            <p className="text-4xl font-bold text-cyber-accent">
              {speedTestResult.download}
            </p>
            <p className="text-gray-500">Mbps</p>
          </div>
          
          <div className="cyber-card p-6 text-center">
            <Upload className="w-8 h-8 text-cyber-accent2 mx-auto mb-2" />
            <p className="text-gray-400 text-sm">Subida</p>
            <p className="text-4xl font-bold text-cyber-accent2">
              {speedTestResult.upload}
            </p>
            <p className="text-gray-500">Mbps</p>
          </div>
          
          <div className="cyber-card p-6 text-center">
            <Clock className="w-8 h-8 text-cyber-warning mx-auto mb-2" />
            <p className="text-gray-400 text-sm">Ping</p>
            <p className="text-4xl font-bold text-cyber-warning">
              {speedTestResult.ping?.toFixed(0) || speedTestResult.server?.latency?.toFixed(0)}
            </p>
            <p className="text-gray-500">ms</p>
          </div>
        </div>
      )}

      {speedTestResult?.server && (
        <div className="cyber-card p-4 text-center text-gray-400">
          <Server className="w-4 h-4 inline mr-2" />
          Servidor: {speedTestResult.server.name} ({speedTestResult.server.country})
        </div>
      )}

      {speedTestResult?.error && (
        <div className="cyber-card p-4 text-center text-cyber-danger">
          <XCircle className="w-5 h-5 inline mr-2" />
          {speedTestResult.error}
        </div>
      )}
    </div>
  )

  const renderWifiPasswords = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-gray-400 text-sm">
          Contraseñas WiFi guardadas en este equipo
        </p>
        <button 
          onClick={loadWifiPasswords}
          className="cyber-btn-secondary px-4 py-2 flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loadingPasswords ? 'animate-spin' : ''}`} />
          Actualizar
        </button>
      </div>

      {loadingPasswords ? (
        <div className="text-center py-8">
          <Loader2 className="w-8 h-8 animate-spin mx-auto text-cyber-accent" />
        </div>
      ) : (
        <div className="space-y-3">
          {wifiPasswords.map((network, idx) => (
            <div key={idx} className="cyber-card p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Wifi className="w-5 h-5 text-cyber-accent" />
                  <div>
                    <h3 className="font-semibold">{network.name}</h3>
                    <p className="text-sm text-gray-500">
                      {network.authentication} • {network.security}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {network.password ? (
                    <>
                      <code className="bg-gray-800 px-3 py-1 rounded font-mono text-sm">
                        {showPasswords[network.name] ? network.password : '••••••••••'}
                      </code>
                      <button
                        onClick={() => togglePassword(network.name)}
                        className="p-2 hover:bg-gray-700 rounded"
                      >
                        {showPasswords[network.name] ? (
                          <EyeOff className="w-4 h-4" />
                        ) : (
                          <Eye className="w-4 h-4" />
                        )}
                      </button>
                      <button
                        onClick={() => copyToClipboard(network.password)}
                        className="p-2 hover:bg-gray-700 rounded"
                        title="Copiar"
                      >
                        <Copy className="w-4 h-4" />
                      </button>
                    </>
                  ) : (
                    <span className="text-gray-500 text-sm">Sin contraseña</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )

  const renderConnections = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        {connectionStats && (
          <div className="flex gap-4 text-sm">
            <span className="text-cyber-accent">
              Total: {connectionStats.total}
            </span>
            <span className="text-green-400">
              Establecidas: {connectionStats.established}
            </span>
            <span className="text-blue-400">
              Escuchando: {connectionStats.listening}
            </span>
          </div>
        )}
        <button 
          onClick={loadConnections}
          className="cyber-btn-secondary px-4 py-2 flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loadingConnections ? 'animate-spin' : ''}`} />
          Actualizar
        </button>
      </div>

      <div className="cyber-card overflow-hidden">
        <div className="overflow-x-auto max-h-96">
          <table className="w-full text-sm">
            <thead className="bg-gray-800 sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left">Tipo</th>
                <th className="px-4 py-3 text-left">Local</th>
                <th className="px-4 py-3 text-left">Remoto</th>
                <th className="px-4 py-3 text-left">Estado</th>
                <th className="px-4 py-3 text-left">Proceso</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {connections.slice(0, 100).map((conn, idx) => (
                <tr key={idx} className="hover:bg-gray-800/50">
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded text-xs ${
                      conn.type === 'TCP' ? 'bg-blue-500/20 text-blue-400' : 'bg-green-500/20 text-green-400'
                    }`}>
                      {conn.type}
                    </span>
                  </td>
                  <td className="px-4 py-2 font-mono text-xs">{conn.local_address}</td>
                  <td className="px-4 py-2 font-mono text-xs">{conn.remote_address || '-'}</td>
                  <td className="px-4 py-2">
                    <span className={`text-xs ${
                      conn.status === 'ESTABLISHED' ? 'text-green-400' :
                      conn.status === 'LISTEN' ? 'text-blue-400' :
                      conn.status === 'TIME_WAIT' ? 'text-yellow-400' : 'text-gray-400'
                    }`}>
                      {conn.status}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-gray-400">{conn.process_name || conn.pid || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderProcesses = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-gray-400 text-sm">
          Procesos con conexiones de red activas
        </p>
        <button 
          onClick={loadProcesses}
          className="cyber-btn-secondary px-4 py-2 flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loadingProcesses ? 'animate-spin' : ''}`} />
          Actualizar
        </button>
      </div>

      <div className="grid gap-3">
        {processes.slice(0, 20).map((proc, idx) => (
          <div key={idx} className="cyber-card p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-cyber-accent/20 flex items-center justify-center">
                  <Cpu className="w-5 h-5 text-cyber-accent" />
                </div>
                <div>
                  <h3 className="font-semibold">{proc.name}</h3>
                  <p className="text-sm text-gray-500">PID: {proc.pid}</p>
                </div>
              </div>
              <div className="flex gap-6 text-right">
                <div>
                  <p className="text-sm text-gray-400">Conexiones</p>
                  <p className="font-semibold text-cyber-accent">{proc.connections}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Establecidas</p>
                  <p className="font-semibold text-green-400">{proc.established}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">CPU</p>
                  <p className="font-semibold">{proc.cpu_percent?.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">RAM</p>
                  <p className="font-semibold">{proc.memory_mb} MB</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  const renderPingMonitor = () => (
    <div className="space-y-4">
      <div className="flex gap-4">
        <input
          type="text"
          value={pingTarget}
          onChange={(e) => setPingTarget(e.target.value)}
          placeholder="Host o IP (ej: google.com, 8.8.8.8)"
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 
                   focus:outline-none focus:border-cyber-accent"
          onKeyDown={(e) => e.key === 'Enter' && runPing()}
        />
        <button
          onClick={runPing}
          disabled={running || !pingTarget}
          className="cyber-btn-primary px-6 flex items-center gap-2"
        >
          {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          Ping
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {['8.8.8.8', '1.1.1.1', 'google.com', '192.168.1.1'].map(host => (
          <button
            key={host}
            onClick={() => { setPingTarget(host); }}
            className="p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-colors text-left"
          >
            <p className="font-mono text-sm">{host}</p>
          </button>
        ))}
      </div>

      <div className="space-y-2">
        {pingResults.map((result, idx) => (
          <div key={idx} className={`cyber-card p-3 flex items-center justify-between ${
            result.reachable ? 'border-green-500/30' : 'border-red-500/30'
          }`}>
            <div className="flex items-center gap-3">
              {result.reachable ? (
                <CheckCircle className="w-5 h-5 text-green-400" />
              ) : (
                <XCircle className="w-5 h-5 text-red-400" />
              )}
              <span className="font-mono">{result.host}</span>
            </div>
            <div className="flex items-center gap-4 text-sm">
              {result.latency_ms && (
                <span className={`font-semibold ${
                  result.latency_ms < 50 ? 'text-green-400' :
                  result.latency_ms < 100 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {result.latency_ms}ms
                </span>
              )}
              {result.ttl && <span className="text-gray-500">TTL: {result.ttl}</span>}
              <span className="text-gray-500 text-xs">
                {new Date(result.timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )

  const renderInterfaces = () => (
    <div className="space-y-4">
      {interfaces.map((iface, idx) => (
        <div key={idx} className="cyber-card p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${iface.is_up ? 'bg-green-400' : 'bg-red-400'}`} />
              <h3 className="font-semibold">{iface.name}</h3>
            </div>
            <div className="flex gap-4 text-sm text-gray-400">
              <span>Speed: {iface.speed} Mbps</span>
              <span>MTU: {iface.mtu}</span>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            {iface.addresses?.filter(a => a.family === 'AF_INET').map((addr, i) => (
              <div key={i}>
                <p className="text-gray-500">IPv4</p>
                <p className="font-mono">{addr.address}</p>
              </div>
            ))}
            <div>
              <p className="text-gray-500">Enviados</p>
              <p className="text-cyber-accent">{(iface.bytes_sent / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <div>
              <p className="text-gray-500">Recibidos</p>
              <p className="text-cyber-accent2">{(iface.bytes_recv / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )

  const renderArpTable = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-gray-400 text-sm">
          Tabla ARP del sistema (mapeo IP → MAC)
        </p>
        <div className="flex gap-2">
          <button 
            onClick={flushArp}
            className="cyber-btn-secondary px-4 py-2 flex items-center gap-2 text-cyber-danger"
          >
            <Trash2 className="w-4 h-4" />
            Limpiar
          </button>
          <button 
            onClick={loadArpTable}
            className="cyber-btn-secondary px-4 py-2 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Actualizar
          </button>
        </div>
      </div>

      <div className="cyber-card overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-800">
            <tr>
              <th className="px-4 py-3 text-left">IP</th>
              <th className="px-4 py-3 text-left">MAC</th>
              <th className="px-4 py-3 text-left">Tipo</th>
              <th className="px-4 py-3 text-left">Interface</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {arpTable.map((entry, idx) => (
              <tr key={idx} className="hover:bg-gray-800/50">
                <td className="px-4 py-2 font-mono">{entry.ip}</td>
                <td className="px-4 py-2 font-mono text-cyber-accent">{entry.mac}</td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-1 rounded text-xs ${
                    entry.type === 'dynamic' || entry.type === 'dinámico' 
                      ? 'bg-green-500/20 text-green-400' 
                      : 'bg-blue-500/20 text-blue-400'
                  }`}>
                    {entry.type}
                  </span>
                </td>
                <td className="px-4 py-2 text-gray-400">{entry.interface}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )

  const renderDnsCache = () => (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <p className="text-gray-400 text-sm">
          Caché DNS local del sistema
        </p>
        <div className="flex gap-2">
          <button 
            onClick={flushDns}
            className="cyber-btn-secondary px-4 py-2 flex items-center gap-2 text-cyber-danger"
          >
            <Trash2 className="w-4 h-4" />
            Limpiar DNS
          </button>
          <button 
            onClick={loadDnsCache}
            className="cyber-btn-secondary px-4 py-2 flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Actualizar
          </button>
        </div>
      </div>

      <div className="cyber-card overflow-hidden">
        <div className="max-h-96 overflow-y-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-800 sticky top-0">
              <tr>
                <th className="px-4 py-3 text-left">Nombre</th>
                <th className="px-4 py-3 text-left">Tipo</th>
                <th className="px-4 py-3 text-left">TTL</th>
                <th className="px-4 py-3 text-left">Dirección</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {dnsCache.map((entry, idx) => (
                <tr key={idx} className="hover:bg-gray-800/50">
                  <td className="px-4 py-2 font-mono text-xs">{entry.name}</td>
                  <td className="px-4 py-2">{entry.type}</td>
                  <td className="px-4 py-2 text-gray-400">{entry.ttl}</td>
                  <td className="px-4 py-2 font-mono text-cyber-accent">{entry.address}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )

  const renderContent = () => {
    switch (activeTab) {
      case 'speedtest': return renderSpeedTest()
      case 'wifipass': return renderWifiPasswords()
      case 'connections': return renderConnections()
      case 'processes': return renderProcesses()
      case 'ping': return renderPingMonitor()
      case 'interfaces': return renderInterfaces()
      case 'arp': return renderArpTable()
      case 'dns': return renderDnsCache()
      default: return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-3">
          <Wrench className="w-8 h-8 text-cyber-accent" />
          Herramientas del Sistema
        </h1>
        <p className="text-gray-400 mt-1">Utilidades avanzadas de red y sistema</p>
      </div>

      {/* Tool Selection */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
        {tools.map((tool) => {
          const Icon = tool.icon
          return (
            <button
              key={tool.id}
              onClick={() => setActiveTab(tool.id)}
              className={`cyber-card p-3 text-center transition-all ${
                activeTab === tool.id 
                  ? 'border-cyber-accent bg-cyber-accent/10' 
                  : 'hover:border-gray-600'
              }`}
            >
              <Icon className={`w-6 h-6 mx-auto mb-1 ${
                activeTab === tool.id ? 'text-cyber-accent' : 'text-gray-400'
              }`} />
              <h3 className="font-medium text-sm">{tool.name}</h3>
            </button>
          )
        })}
      </div>

      {/* Tool Content */}
      <div className="cyber-card p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          {tools.find(t => t.id === activeTab)?.icon && 
            React.createElement(tools.find(t => t.id === activeTab).icon, { className: 'w-5 h-5 text-cyber-accent' })}
          {tools.find(t => t.id === activeTab)?.name}
        </h2>
        {renderContent()}
      </div>
    </div>
  )
}

export default Tools
