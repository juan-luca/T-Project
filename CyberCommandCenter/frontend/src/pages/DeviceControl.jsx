import React, { useState, useEffect } from 'react'
import { 
  Smartphone, RefreshCw, Apple, Tablet, Monitor, Wifi, WifiOff,
  Shield, ShieldOff, Info, AlertTriangle, Check, X, Search,
  Ban, Lock, Unlock, Eye, Signal, Clock, HelpCircle, Music,
  Ghost, Video, Gamepad2, Globe, Zap, Play, Square
} from 'lucide-react'
import api from '../services/api'

// Device type icons
const deviceIcons = {
  'Apple Device': Apple,
  'iPhone': Smartphone,
  'iPad': Tablet,
  'MacBook': Monitor,
  'Samsung Device': Smartphone,
  'Xiaomi Device': Smartphone,
  'Huawei Device': Smartphone,
  'Router/Gateway': Wifi,
  'Unknown Device': Monitor,
}

// Prank definitions with icons
const NETWORK_PRANKS = [
  { id: 'rickroll', name: '🎵 Rickroll', icon: Music, color: 'text-pink-400', bg: 'bg-pink-500/20' },
  { id: 'block_social', name: '📵 Sin Redes Sociales', icon: Globe, color: 'text-blue-400', bg: 'bg-blue-500/20' },
  { id: 'block_video', name: '🎬 Sin Videos', icon: Video, color: 'text-red-400', bg: 'bg-red-500/20' },
  { id: 'block_gaming', name: '🎮 Sin Gaming', icon: Gamepad2, color: 'text-purple-400', bg: 'bg-purple-500/20' },
  { id: 'block_all', name: '🚫 Sin Internet', icon: Ban, color: 'text-red-500', bg: 'bg-red-600/20' },
  { id: 'slow_internet', name: '🐌 Internet Lento', icon: Zap, color: 'text-yellow-400', bg: 'bg-yellow-500/20' },
]

function DeviceControl() {
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [deviceInfo, setDeviceInfo] = useState(null)
  const [iosInfo, setIosInfo] = useState(null)
  const [filter, setFilter] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [stats, setStats] = useState({ total: 0, apple_count: 0, android_count: 0 })
  const [actionLoading, setActionLoading] = useState(false)
  const [showInfoModal, setShowInfoModal] = useState(false)
  const [activePranks, setActivePranks] = useState({})
  const [prankLoading, setPrankLoading] = useState(null)
  const [prankResult, setPrankResult] = useState(null)

  useEffect(() => {
    loadDevices()
    loadIosInfo()
    loadActivePranks()
  }, [])

  const loadDevices = async (force = false) => {
    setScanning(true)
    try {
      const response = await api.get(`/device-control/scan?force=${force}`)
      setDevices(response.data.devices || [])
      setStats({
        total: response.data.total || 0,
        apple_count: response.data.apple_count || 0,
        android_count: response.data.android_count || 0
      })
    } catch (error) {
      console.error('Error loading devices:', error)
    }
    setScanning(false)
  }

  const loadIosInfo = async () => {
    try {
      const response = await api.get('/device-control/ios-info')
      setIosInfo(response.data)
    } catch (error) {
      console.error('Error loading iOS info:', error)
    }
  }

  const loadActivePranks = async () => {
    try {
      const response = await api.get('/network-pranks/active')
      setActivePranks(response.data || {})
    } catch (error) {
      console.error('Error loading active pranks:', error)
    }
  }

  const loadDeviceDetails = async (device) => {
    setSelectedDevice(device)
    setLoading(true)
    try {
      const response = await api.get(`/device-control/device/${device.ip}`)
      setDeviceInfo(response.data)
    } catch (error) {
      console.error('Error loading device details:', error)
      setDeviceInfo(null)
    }
    setLoading(false)
  }

  const performAction = async (action, identifier) => {
    setActionLoading(true)
    try {
      const response = await api.post('/device-control/action', {
        action,
        identifier
      })
      
      if (response.data.success) {
        loadDevices(true)
      }
      
      return response.data
    } catch (error) {
      console.error('Action error:', error)
      return { success: false, error: error.message }
    } finally {
      setActionLoading(false)
    }
  }

  const executePrank = async (prankId, deviceIp) => {
    setPrankLoading(prankId)
    setPrankResult(null)
    try {
      const response = await api.post('/network-pranks/execute', {
        prank_id: prankId,
        device_ip: deviceIp
      })
      
      setPrankResult({
        success: response.data.success,
        message: response.data.success 
          ? `¡Prank "${prankId}" ejecutado!` 
          : response.data.error || 'Error al ejecutar prank'
      })
      
      loadActivePranks()
      
      setTimeout(() => setPrankResult(null), 3000)
      
      return response.data
    } catch (error) {
      console.error('Prank error:', error)
      setPrankResult({ success: false, message: error.message })
      return { success: false, error: error.message }
    } finally {
      setPrankLoading(null)
    }
  }

  const stopPranks = async (deviceIp) => {
    setPrankLoading('stop')
    try {
      const response = await api.post('/network-pranks/stop', {
        device_ip: deviceIp
      })
      
      if (response.data.success) {
        setPrankResult({ success: true, message: 'Pranks detenidos' })
        loadActivePranks()
      }
      
      setTimeout(() => setPrankResult(null), 3000)
    } catch (error) {
      console.error('Stop prank error:', error)
    } finally {
      setPrankLoading(null)
    }
  }

  const filteredDevices = devices.filter(device => {
    if (filter === 'apple' && !device.is_apple) return false
    if (filter === 'android' && device.is_apple) return false
    
    if (searchTerm) {
      const search = searchTerm.toLowerCase()
      return (
        device.ip.includes(search) ||
        device.mac.toLowerCase().includes(search) ||
        device.manufacturer.toLowerCase().includes(search) ||
        (device.hostname && device.hostname.toLowerCase().includes(search))
      )
    }
    
    return true
  })

  const getDeviceIcon = (device) => {
    return deviceIcons[device.device_type] || Monitor
  }

  const hasActivePrank = (deviceIp) => {
    return activePranks[deviceIp] !== undefined
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Smartphone className="w-8 h-8 text-cyber-accent" />
            Control de Dispositivos iOS/Android
          </h1>
          <p className="text-gray-400 mt-1">Gestiona y haz pranks a dispositivos móviles en tu red</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowInfoModal(true)}
            className="px-4 py-2 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition flex items-center gap-2"
          >
            <HelpCircle className="w-4 h-4" />
            ¿Qué puedo hacer?
          </button>
          <button
            onClick={() => loadDevices(true)}
            disabled={scanning}
            className="px-4 py-2 bg-cyber-accent text-cyber-dark rounded-lg hover:bg-cyber-accent/80 transition flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
            {scanning ? 'Escaneando...' : 'Escanear Red'}
          </button>
        </div>
      </div>

      {/* Prank Result Toast */}
      {prankResult && (
        <div className={`fixed top-4 right-4 z-50 px-6 py-3 rounded-lg shadow-lg animate-pulse ${
          prankResult.success ? 'bg-green-600' : 'bg-red-600'
        }`}>
          <p className="text-white font-medium">{prankResult.message}</p>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-cyber-card rounded-xl p-4 border border-gray-800">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-gray-700/50">
              <Monitor className="w-6 h-6 text-gray-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.total}</p>
              <p className="text-sm text-gray-400">Total Dispositivos</p>
            </div>
          </div>
        </div>
        
        <div className="bg-cyber-card rounded-xl p-4 border border-gray-800">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-gray-700/50">
              <Apple className="w-6 h-6 text-gray-300" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.apple_count}</p>
              <p className="text-sm text-gray-400">Dispositivos Apple</p>
            </div>
          </div>
        </div>
        
        <div className="bg-cyber-card rounded-xl p-4 border border-gray-800">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-green-500/20">
              <Smartphone className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{stats.android_count}</p>
              <p className="text-sm text-gray-400">Dispositivos Android</p>
            </div>
          </div>
        </div>
        
        <div className="bg-cyber-card rounded-xl p-4 border border-gray-800">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-lg bg-purple-500/20">
              <Ghost className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{Object.keys(activePranks).length}</p>
              <p className="text-sm text-gray-400">Pranks Activos</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex gap-2">
          {[
            { id: 'all', label: 'Todos', icon: Monitor },
            { id: 'apple', label: 'Apple/iOS', icon: Apple },
            { id: 'android', label: 'Android', icon: Smartphone },
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setFilter(id)}
              className={`px-4 py-2 rounded-lg flex items-center gap-2 transition ${
                filter === id
                  ? 'bg-cyber-accent text-cyber-dark'
                  : 'bg-cyber-card text-gray-400 hover:text-white border border-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>
        
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Buscar por IP, MAC, fabricante..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-cyber-card border border-gray-700 rounded-lg text-white focus:border-cyber-accent focus:outline-none"
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Device List */}
        <div className="lg:col-span-2 space-y-3">
          <h2 className="text-lg font-semibold text-white">
            Dispositivos Encontrados ({filteredDevices.length})
          </h2>
          
          {filteredDevices.length === 0 ? (
            <div className="bg-cyber-card rounded-xl p-8 text-center border border-gray-800">
              <Smartphone className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400">No se encontraron dispositivos</p>
              <button
                onClick={() => loadDevices(true)}
                className="mt-4 text-cyber-accent hover:underline"
              >
                Escanear red
              </button>
            </div>
          ) : (
            <div className="space-y-2 max-h-[600px] overflow-y-auto">
              {filteredDevices.map((device, index) => {
                const Icon = getDeviceIcon(device)
                const hasPrank = hasActivePrank(device.ip)
                
                return (
                  <div
                    key={device.mac || index}
                    onClick={() => loadDeviceDetails(device)}
                    className={`bg-cyber-card rounded-xl p-4 border cursor-pointer transition-all hover:border-cyber-accent ${
                      selectedDevice?.mac === device.mac
                        ? 'border-cyber-accent bg-cyber-accent/5'
                        : hasPrank
                        ? 'border-purple-500/50 bg-purple-500/5'
                        : 'border-gray-800 hover:bg-gray-800/30'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-lg ${
                          hasPrank 
                            ? 'bg-purple-500/20'
                            : device.is_apple 
                            ? 'bg-gray-700/50' 
                            : 'bg-green-500/20'
                        }`}>
                          {hasPrank ? (
                            <Ghost className="w-6 h-6 text-purple-400" />
                          ) : (
                            <Icon className={`w-6 h-6 ${
                              device.is_apple ? 'text-gray-300' : 'text-green-400'
                            }`} />
                          )}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-semibold text-white">
                              {device.hostname || device.device_type}
                            </p>
                            {device.is_apple && (
                              <span className="px-2 py-0.5 bg-gray-700 text-gray-300 text-xs rounded">
                                Apple
                              </span>
                            )}
                            {device.is_blocked && (
                              <span className="px-2 py-0.5 bg-red-500/20 text-red-400 text-xs rounded">
                                Bloqueado
                              </span>
                            )}
                            {hasPrank && (
                              <span className="px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs rounded animate-pulse">
                                😈 Prank
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-4 text-sm text-gray-400">
                            <span>{device.ip}</span>
                            <span className="text-gray-600">|</span>
                            <span className="font-mono text-xs">{device.mac}</span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{device.manufacturer}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        {device.online ? (
                          <Signal className="w-5 h-5 text-green-400" />
                        ) : (
                          <WifiOff className="w-5 h-5 text-gray-600" />
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Device Details & Pranks Panel */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-white">Detalles y Pranks</h2>
          
          {!selectedDevice ? (
            <div className="bg-cyber-card rounded-xl p-8 text-center border border-gray-800">
              <Ghost className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400">Selecciona un dispositivo para ver opciones y pranks</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Device Info Card */}
              <div className="bg-cyber-card rounded-xl border border-gray-800">
                <div className="p-4 border-b border-gray-800">
                  <div className="flex items-center gap-3">
                    {React.createElement(getDeviceIcon(selectedDevice), {
                      className: `w-8 h-8 ${selectedDevice.is_apple ? 'text-gray-300' : 'text-green-400'}`
                    })}
                    <div>
                      <p className="font-semibold text-white">
                        {selectedDevice.hostname || selectedDevice.device_type}
                      </p>
                      <p className="text-sm text-gray-400">{selectedDevice.manufacturer}</p>
                    </div>
                  </div>
                </div>
                
                <div className="p-4 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">IP</span>
                    <span className="text-white font-mono">{selectedDevice.ip}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Estado</span>
                    <span className={selectedDevice.online ? 'text-green-400' : 'text-gray-500'}>
                      {selectedDevice.online ? '● Online' : '○ Offline'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Network Pranks Card */}
              <div className="bg-cyber-card rounded-xl border border-gray-800">
                <div className="p-4 border-b border-gray-800">
                  <h3 className="font-semibold text-white flex items-center gap-2">
                    <Ghost className="w-5 h-5 text-purple-400" />
                    Pranks de Red
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">Afectan la conexión del dispositivo</p>
                </div>
                
                <div className="p-4 grid grid-cols-2 gap-2">
                  {NETWORK_PRANKS.map(prank => (
                    <button
                      key={prank.id}
                      onClick={() => executePrank(prank.id, selectedDevice.ip)}
                      disabled={prankLoading !== null}
                      className={`p-3 rounded-lg ${prank.bg} ${prank.color} hover:opacity-80 transition flex flex-col items-center gap-1 text-center disabled:opacity-50`}
                    >
                      {prankLoading === prank.id ? (
                        <RefreshCw className="w-5 h-5 animate-spin" />
                      ) : (
                        <prank.icon className="w-5 h-5" />
                      )}
                      <span className="text-xs font-medium">{prank.name}</span>
                    </button>
                  ))}
                </div>
                
                {/* Stop Pranks Button */}
                {hasActivePrank(selectedDevice.ip) && (
                  <div className="p-4 pt-0">
                    <button
                      onClick={() => stopPranks(selectedDevice.ip)}
                      disabled={prankLoading !== null}
                      className="w-full py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition flex items-center justify-center gap-2"
                    >
                      <Square className="w-4 h-4" />
                      Detener Pranks
                    </button>
                  </div>
                )}
              </div>

              {/* Quick Actions */}
              <div className="bg-cyber-card rounded-xl border border-gray-800">
                <div className="p-4 border-b border-gray-800">
                  <h3 className="font-semibold text-white">Acciones Rápidas</h3>
                </div>
                <div className="p-4 space-y-2">
                  {selectedDevice.is_blocked ? (
                    <button
                      onClick={() => performAction('unblock', selectedDevice.ip)}
                      disabled={actionLoading}
                      className="w-full px-4 py-2 bg-green-600/20 text-green-400 rounded-lg hover:bg-green-600/30 transition flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      <Unlock className="w-4 h-4" />
                      Desbloquear Internet
                    </button>
                  ) : (
                    <button
                      onClick={() => performAction('block', selectedDevice.ip)}
                      disabled={actionLoading}
                      className="w-full px-4 py-2 bg-red-600/20 text-red-400 rounded-lg hover:bg-red-600/30 transition flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      <Ban className="w-4 h-4" />
                      Bloquear Internet
                    </button>
                  )}
                  
                  <button
                    onClick={() => loadDeviceDetails(selectedDevice)}
                    disabled={loading}
                    className="w-full px-4 py-2 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    <Eye className="w-4 h-4" />
                    Escanear Puertos
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Info Modal */}
      {showInfoModal && iosInfo && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-cyber-card rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto border border-gray-700">
            <div className="p-6 border-b border-gray-800">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white flex items-center gap-3">
                  <Info className="w-6 h-6 text-cyber-accent" />
                  {iosInfo.title}
                </h2>
                <button
                  onClick={() => setShowInfoModal(false)}
                  className="p-2 hover:bg-gray-700 rounded-lg transition"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-green-400 mb-3 flex items-center gap-2">
                  <Check className="w-5 h-5" />
                  Lo que SÍ puedes hacer
                </h3>
                <ul className="space-y-2">
                  {iosInfo.what_you_can_do.map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-gray-300">
                      <Check className="w-4 h-4 text-green-500 mt-1 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-red-400 mb-3 flex items-center gap-2">
                  <X className="w-5 h-5" />
                  Lo que NO puedes hacer
                </h3>
                <ul className="space-y-2">
                  {iosInfo.what_you_cannot_do.map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-gray-300">
                      <X className="w-4 h-4 text-red-500 mt-1 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="bg-purple-500/10 rounded-lg p-4 border border-purple-500/30">
                <div className="flex gap-3">
                  <Ghost className="w-6 h-6 text-purple-400 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-purple-400">Pranks Disponibles</p>
                    <p className="text-sm text-gray-300 mt-1">
                      Puedes hacer pranks de red como: Rickroll, bloquear redes sociales, 
                      bloquear YouTube/Netflix, bloquear gaming, ralentizar internet, 
                      o bloquear completamente el acceso.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="bg-yellow-500/10 rounded-lg p-4 border border-yellow-500/30">
                <div className="flex gap-3">
                  <AlertTriangle className="w-6 h-6 text-yellow-500 flex-shrink-0" />
                  <div>
                    <p className="font-semibold text-yellow-500">Aviso Legal</p>
                    <p className="text-sm text-gray-300 mt-1">{iosInfo.legal_notice}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="p-4 border-t border-gray-800">
              <button
                onClick={() => setShowInfoModal(false)}
                className="w-full py-3 bg-cyber-accent text-cyber-dark rounded-lg font-semibold hover:bg-cyber-accent/80 transition"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DeviceControl
