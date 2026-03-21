import React, { useState, useEffect } from 'react'
import { 
  Monitor, Smartphone, Tv, Gamepad2, Cpu, Printer, Camera, Speaker,
  RefreshCw, Search, MoreVertical, Shield, ShieldOff, Ban, Eye,
  Wifi, WifiOff, Clock, Info
} from 'lucide-react'
import { getDevices, scanNetwork, updateDevice, scanPorts } from '../services/api'

const deviceIcons = {
  computer: Monitor,
  mobile: Smartphone,
  tv: Tv,
  gaming: Gamepad2,
  iot: Cpu,
  printer: Printer,
  camera: Camera,
  smart_speaker: Speaker,
  raspberry_pi: Cpu,
  apple_device: Smartphone,
  unknown: Monitor
}

function DeviceCard({ device, onUpdate, onScanPorts }) {
  const [showMenu, setShowMenu] = useState(false)
  const [showDetails, setShowDetails] = useState(false)
  
  const Icon = deviceIcons[device.device_type] || Monitor

  return (
    <div className="cyber-card-hover p-4 relative">
      {/* Status indicator */}
      <div className={`absolute top-4 right-4 ${device.is_online ? 'status-online' : 'status-offline'}`} />
      
      <div className="flex items-start gap-4">
        {/* Icon */}
        <div className={`p-3 rounded-xl ${device.is_online ? 'bg-cyber-accent/10' : 'bg-gray-800'}`}>
          <Icon className={`w-6 h-6 ${device.is_online ? 'text-cyber-accent' : 'text-gray-500'}`} />
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold truncate">{device.custom_name}</h3>
          <p className="text-sm text-gray-400 font-mono">{device.ip_address}</p>
          <p className="text-xs text-gray-500 font-mono truncate">{device.mac_address}</p>
          
          {device.vendor && device.vendor !== 'Unknown' && (
            <p className="text-xs text-cyber-accent2 mt-1">{device.vendor}</p>
          )}

          {/* Tags */}
          <div className="flex items-center gap-2 mt-2">
            {device.is_trusted && (
              <span className="px-2 py-0.5 rounded-full text-xs bg-cyber-accent/20 text-cyber-accent">
                Confiable
              </span>
            )}
            {device.is_blocked && (
              <span className="px-2 py-0.5 rounded-full text-xs bg-cyber-danger/20 text-cyber-danger">
                Bloqueado
              </span>
            )}
            {device.category && (
              <span className="px-2 py-0.5 rounded-full text-xs bg-gray-700 text-gray-300">
                {device.category}
              </span>
            )}
          </div>
        </div>

        {/* Menu Button */}
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
          >
            <MoreVertical className="w-5 h-5" />
          </button>

          {/* Dropdown Menu */}
          {showMenu && (
            <div className="absolute right-0 top-full mt-1 w-48 bg-cyber-dark border border-gray-800 rounded-lg shadow-xl z-10 overflow-hidden">
              <button
                onClick={() => {
                  setShowDetails(true)
                  setShowMenu(false)
                }}
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-800 flex items-center gap-2"
              >
                <Info className="w-4 h-4" />
                Ver detalles
              </button>
              <button
                onClick={() => {
                  onScanPorts(device)
                  setShowMenu(false)
                }}
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-800 flex items-center gap-2"
              >
                <Eye className="w-4 h-4" />
                Escanear puertos
              </button>
              <button
                onClick={() => {
                  onUpdate(device.id, { is_trusted: !device.is_trusted })
                  setShowMenu(false)
                }}
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-800 flex items-center gap-2"
              >
                {device.is_trusted ? (
                  <>
                    <ShieldOff className="w-4 h-4" />
                    Quitar confianza
                  </>
                ) : (
                  <>
                    <Shield className="w-4 h-4" />
                    Marcar confiable
                  </>
                )}
              </button>
              <button
                onClick={() => {
                  onUpdate(device.id, { is_blocked: !device.is_blocked })
                  setShowMenu(false)
                }}
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-800 flex items-center gap-2 text-cyber-danger"
              >
                <Ban className="w-4 h-4" />
                {device.is_blocked ? 'Desbloquear' : 'Bloquear'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Details Modal */}
      {showDetails && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowDetails(false)}>
          <div className="bg-cyber-dark border border-gray-800 rounded-xl p-6 max-w-md w-full mx-4" onClick={e => e.stopPropagation()}>
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 rounded-xl bg-cyber-accent/10">
                <Icon className="w-8 h-8 text-cyber-accent" />
              </div>
              <div>
                <h3 className="text-xl font-bold">{device.custom_name}</h3>
                <p className="text-gray-400">{device.vendor || 'Desconocido'}</p>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-gray-800">
                <span className="text-gray-400">IP</span>
                <span className="font-mono">{device.ip_address}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-800">
                <span className="text-gray-400">MAC</span>
                <span className="font-mono text-sm">{device.mac_address}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-800">
                <span className="text-gray-400">Hostname</span>
                <span>{device.hostname || 'N/A'}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-800">
                <span className="text-gray-400">Primera vez</span>
                <span className="text-sm">{new Date(device.first_seen).toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-800">
                <span className="text-gray-400">Última vez</span>
                <span className="text-sm">{new Date(device.last_seen).toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-gray-400">Estado</span>
                <span className={device.is_online ? 'text-cyber-accent' : 'text-gray-500'}>
                  {device.is_online ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>

            <button
              onClick={() => setShowDetails(false)}
              className="w-full mt-6 cyber-btn-secondary"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function Devices() {
  const [devices, setDevices] = useState([])
  const [isScanning, setIsScanning] = useState(false)
  const [filter, setFilter] = useState('all') // all, online, offline, trusted, unknown
  const [search, setSearch] = useState('')
  const [scanResults, setScanResults] = useState(null)

  useEffect(() => {
    loadDevices()
  }, [])

  const loadDevices = async () => {
    try {
      const res = await getDevices()
      setDevices(res.data)
    } catch (err) {
      console.error('Error loading devices:', err)
    }
  }

  const handleScan = async () => {
    setIsScanning(true)
    try {
      const res = await scanNetwork('arp')
      await loadDevices()
    } catch (err) {
      console.error('Scan error:', err)
    }
    setIsScanning(false)
  }

  const handleUpdateDevice = async (id, data) => {
    try {
      await updateDevice(id, data)
      await loadDevices()
    } catch (err) {
      console.error('Update error:', err)
    }
  }

  const handleScanPorts = async (device) => {
    try {
      const res = await scanPorts(device.id)
      setScanResults({
        device,
        ports: res.data.open_ports
      })
    } catch (err) {
      console.error('Port scan error:', err)
    }
  }

  const filteredDevices = devices.filter(device => {
    // Filter
    if (filter === 'online' && !device.is_online) return false
    if (filter === 'offline' && device.is_online) return false
    if (filter === 'trusted' && !device.is_trusted) return false
    if (filter === 'unknown' && (device.is_trusted || device.category)) return false

    // Search
    if (search) {
      const searchLower = search.toLowerCase()
      return (
        device.custom_name?.toLowerCase().includes(searchLower) ||
        device.ip_address?.includes(search) ||
        device.mac_address?.toLowerCase().includes(searchLower) ||
        device.hostname?.toLowerCase().includes(searchLower) ||
        device.vendor?.toLowerCase().includes(searchLower)
      )
    }

    return true
  })

  const onlineCount = devices.filter(d => d.is_online).length
  const offlineCount = devices.filter(d => !d.is_online).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Dispositivos</h1>
          <p className="text-gray-400 mt-1">
            {onlineCount} online • {offlineCount} offline • {devices.length} total
          </p>
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

      {/* Filters & Search */}
      <div className="flex flex-col md:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="Buscar por nombre, IP, MAC..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="cyber-input pl-10"
          />
        </div>

        {/* Filter Buttons */}
        <div className="flex gap-2">
          {[
            { id: 'all', label: 'Todos' },
            { id: 'online', label: 'Online' },
            { id: 'offline', label: 'Offline' },
            { id: 'trusted', label: 'Confiables' },
            { id: 'unknown', label: 'Desconocidos' },
          ].map(f => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === f.id
                  ? 'bg-cyber-accent/20 text-cyber-accent border border-cyber-accent/30'
                  : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Devices Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredDevices.map(device => (
          <DeviceCard
            key={device.id}
            device={device}
            onUpdate={handleUpdateDevice}
            onScanPorts={handleScanPorts}
          />
        ))}
      </div>

      {filteredDevices.length === 0 && (
        <div className="text-center py-12">
          <Monitor className="w-16 h-16 mx-auto text-gray-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-400">No hay dispositivos</h3>
          <p className="text-gray-500 mt-2">
            {search ? 'No se encontraron resultados' : 'Haz click en "Escanear Red" para buscar dispositivos'}
          </p>
        </div>
      )}

      {/* Port Scan Results Modal */}
      {scanResults && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setScanResults(null)}>
          <div className="bg-cyber-dark border border-gray-800 rounded-xl p-6 max-w-lg w-full mx-4 max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
            <h3 className="text-xl font-bold mb-4">
              Puertos abiertos en {scanResults.device.custom_name}
            </h3>
            <p className="text-gray-400 mb-4 font-mono">{scanResults.device.ip_address}</p>
            
            {scanResults.ports.length > 0 ? (
              <table className="cyber-table">
                <thead>
                  <tr>
                    <th>Puerto</th>
                    <th>Servicio</th>
                    <th>Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {scanResults.ports.map((port, i) => (
                    <tr key={i}>
                      <td className="font-mono text-cyber-accent">{port.port}</td>
                      <td>{port.service}</td>
                      <td className="text-cyber-accent">{port.state}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p className="text-gray-500 text-center py-4">No se encontraron puertos abiertos</p>
            )}

            <button
              onClick={() => setScanResults(null)}
              className="w-full mt-6 cyber-btn-secondary"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Devices
