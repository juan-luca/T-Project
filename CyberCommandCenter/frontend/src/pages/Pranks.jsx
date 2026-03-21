import React, { useState, useEffect } from 'react'
import { 
  Ghost, Play, Square, Wifi, Globe, Volume2, VolumeX, Monitor, MousePointer,
  MessageSquare, WifiOff, Music, RefreshCw, Loader2, CheckCircle, XCircle,
  AlertTriangle, Server, Disc, Minimize2, Keyboard, Power, Ban, History,
  Radio, Skull, Bug, Eye, EyeOff, Zap, RotateCcw, Smartphone, Image,
  Ear, HardDrive, Lightbulb, Bomb, Layers, Binary, 
  Volume1, Sparkles, Flame, AlertCircle, Clock,
  Snail, Key, MessageCircle
} from 'lucide-react'
import api from '../services/api'

// Custom MonitorX component (not in lucide by default)
const MonitorX = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" 
       fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" 
       strokeLinejoin="round" {...props}>
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
    <line x1="8" y1="21" x2="16" y2="21"/>
    <line x1="12" y1="17" x2="12" y2="21"/>
    <path d="m9 10 6-4"/>
    <path d="m9 6 6 4"/>
  </svg>
)

// Categorías con colores e iconos
const CATEGORIES = {
  'classic': {
    name: '😈 Classic Trolls',
    color: 'from-orange-500/20 to-transparent border-orange-500/30',
    icon: Flame,
    description: 'Los clásicos que nunca fallan'
  },
  'visual': {
    name: '🖥️ Visual / Pantalla',
    color: 'from-blue-500/20 to-transparent border-blue-500/30',
    icon: Monitor,
    description: 'Efectos visuales y pantallas falsas'
  },
  'audio': {
    name: '🔊 Audio / Sonido',
    color: 'from-green-500/20 to-transparent border-green-500/30',
    icon: Volume2,
    description: 'Sonidos, voces y control de volumen'
  },
  'input': {
    name: '🖱️ Mouse & Teclado',
    color: 'from-purple-500/20 to-transparent border-purple-500/30',
    icon: MousePointer,
    description: 'Pranks de mouse y teclado'
  },
  'annoying': {
    name: '💣 Molestas',
    color: 'from-red-500/20 to-transparent border-red-500/30',
    icon: Bomb,
    description: 'Las más molestas (úsalas con cuidado)'
  },
  'fake': {
    name: '⚠️ Errores Falsos',
    color: 'from-yellow-500/20 to-transparent border-yellow-500/30',
    icon: AlertTriangle,
    description: 'Alertas y errores falsos de Windows'
  },
  'hardware': {
    name: '💿 Hardware',
    color: 'from-cyan-500/20 to-transparent border-cyan-500/30',
    icon: Disc,
    description: 'Pranks que afectan hardware'
  },
  'network': {
    name: '🌐 Red / Network',
    color: 'from-pink-500/20 to-transparent border-pink-500/30',
    icon: Globe,
    description: 'Pranks de red (algunas requieren admin)'
  }
}

// Mapeo de iconos por ID de prank
const PRANK_ICONS = {
  // Classic
  'rickroll': Music,
  'fake_virus': Bug,
  'jumpscare': Ghost,
  // Visual
  'fake_bsod': MonitorX,
  'fake_update': RefreshCw,
  'matrix_screen': Binary,
  'flip_screen': RotateCcw,
  'cracked_screen': Smartphone,
  'fake_desktop': Image,
  // Audio
  'speak': MessageCircle,
  'sound_alert': Volume2,
  'volume_max': Volume1,
  'mute': VolumeX,
  'creepy_whisper': Ear,
  // Input
  'crazy_mouse': MousePointer,
  'caps_lock': Keyboard,
  'sticky_keys': Key,
  'slow_mouse': Snail,
  // Annoying
  'browser_bomb': Bomb,
  'message_bomb': MessageSquare,
  'minimize_all': Minimize2,
  'popup_loop': Layers,
  'taskbar_hide': EyeOff,
  // Fake
  'fake_error': AlertCircle,
  'fake_shutdown': Power,
  'fake_format': HardDrive,
  'fake_hack': Skull,
  // Hardware
  'eject_cd': Disc,
  'flash_keyboard': Lightbulb,
  // Network
  'block_site': Ban,
  'disconnect_wifi': WifiOff,
  'prank_server': Server,
  'change_dns': Snail,
}

function Pranks() {
  const [pranks, setPranks] = useState([])
  const [activePranks, setActivePranks] = useState([])
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [executing, setExecuting] = useState(null)
  const [result, setResult] = useState(null)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [expandedPrank, setExpandedPrank] = useState(null)
  
  // Options for pranks with inputs
  const [options, setOptions] = useState({
    speak_text: '¡Hola! Soy tu computadora.',
    error_title: 'Error del Sistema',
    error_message: 'Ha ocurrido un error crítico.',
    sound_type: 'beep',
    browser_count: 5,
    message_count: 3,
    block_domain: '',
    prank_server_mode: 'rickroll',
    crazy_duration: 5,
  })

  useEffect(() => {
    loadPranks()
    const interval = setInterval(loadPranks, 10000)
    return () => clearInterval(interval)
  }, [])

  const loadPranks = async () => {
    try {
      const response = await api.get('/pranks')
      setPranks(response.data.available || [])
      setActivePranks(response.data.active || [])
      setHistory(response.data.history || [])
    } catch (error) {
      console.error('Error loading pranks:', error)
    } finally {
      setLoading(false)
    }
  }

  const executePrank = async (prankId, prankOptions = {}) => {
    setExecuting(prankId)
    setResult(null)
    
    try {
      const response = await api.post('/pranks/execute', {
        prank_id: prankId,
        options: prankOptions
      })
      
      setResult({
        prankId,
        success: response.data.success,
        message: response.data.error || '¡Prank ejecutada!'
      })
      
      loadPranks()
      
    } catch (error) {
      setResult({
        prankId,
        success: false,
        message: error.response?.data?.error || error.message
      })
    } finally {
      setExecuting(null)
      setTimeout(() => setResult(null), 3000)
    }
  }

  const handleExecutePrank = (prank) => {
    let prankOptions = {}
    
    switch (prank.id) {
      case 'speak':
        prankOptions = { text: options.speak_text }
        break
      case 'fake_error':
        prankOptions = { title: options.error_title, message: options.error_message }
        break
      case 'sound_alert':
        prankOptions = { sound: options.sound_type }
        break
      case 'browser_bomb':
        prankOptions = { count: options.browser_count }
        break
      case 'message_bomb':
        prankOptions = { count: options.message_count, message: 'Alert!', title: 'Warning' }
        break
      case 'popup_loop':
        prankOptions = { count: options.message_count }
        break
      case 'block_site':
        if (!options.block_domain) {
          setResult({ prankId: prank.id, success: false, message: 'Ingresa un dominio' })
          setTimeout(() => setResult(null), 3000)
          return
        }
        prankOptions = { domain: options.block_domain }
        break
      case 'prank_server':
        prankOptions = { action: 'start', mode: options.prank_server_mode }
        break
      case 'crazy_mouse':
        prankOptions = { duration: options.crazy_duration }
        break
      default:
        break
    }
    
    executePrank(prank.id, prankOptions)
  }

  const stopPrank = async (prankId) => {
    try {
      await api.post('/pranks/stop', { prank_id: prankId })
      loadPranks()
    } catch (error) {
      console.error('Error stopping prank:', error)
    }
  }

  const stopAll = async () => {
    try {
      await api.post('/pranks/stop-all')
      loadPranks()
    } catch (error) {
      console.error('Error:', error)
    }
  }

  // Agrupar pranks por categoría
  const groupedPranks = pranks.reduce((acc, prank) => {
    const cat = prank.category || 'other'
    if (!acc[cat]) acc[cat] = []
    acc[cat].push(prank)
    return acc
  }, {})

  const filteredCategories = selectedCategory === 'all' 
    ? Object.keys(groupedPranks)
    : [selectedCategory]

  const renderPrankOptions = (prank) => {
    switch (prank.id) {
      case 'speak':
        return (
          <input
            type="text"
            value={options.speak_text}
            onChange={(e) => setOptions({...options, speak_text: e.target.value})}
            placeholder="Texto a decir..."
            className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm
                     focus:outline-none focus:border-cyber-accent mt-2"
          />
        )
      
      case 'fake_error':
        return (
          <div className="space-y-2 mt-2">
            <input
              type="text"
              value={options.error_title}
              onChange={(e) => setOptions({...options, error_title: e.target.value})}
              placeholder="Título del error"
              className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm
                       focus:outline-none focus:border-cyber-accent"
            />
            <input
              type="text"
              value={options.error_message}
              onChange={(e) => setOptions({...options, error_message: e.target.value})}
              placeholder="Mensaje"
              className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm
                       focus:outline-none focus:border-cyber-accent"
            />
          </div>
        )
      
      case 'sound_alert':
        return (
          <select
            value={options.sound_type}
            onChange={(e) => setOptions({...options, sound_type: e.target.value})}
            className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm
                     focus:outline-none focus:border-cyber-accent mt-2"
          >
            <option value="beep">🔔 Beep</option>
            <option value="alert">⚡ Alerta</option>
            <option value="error">❌ Error</option>
            <option value="police">🚨 Sirena Policía</option>
            <option value="ufo">👽 UFO</option>
            <option value="random">🎲 Random</option>
          </select>
        )
      
      case 'browser_bomb':
        return (
          <div className="flex items-center gap-2 mt-2">
            <span className="text-sm text-gray-400">Ventanas:</span>
            <input
              type="range"
              min="1"
              max="20"
              value={options.browser_count}
              onChange={(e) => setOptions({...options, browser_count: parseInt(e.target.value)})}
              className="flex-1"
            />
            <span className="text-sm text-cyber-accent font-mono w-8">{options.browser_count}</span>
          </div>
        )
      
      case 'message_bomb':
      case 'popup_loop':
        return (
          <div className="flex items-center gap-2 mt-2">
            <span className="text-sm text-gray-400">Cantidad:</span>
            <input
              type="range"
              min="1"
              max="10"
              value={options.message_count}
              onChange={(e) => setOptions({...options, message_count: parseInt(e.target.value)})}
              className="flex-1"
            />
            <span className="text-sm text-cyber-accent font-mono w-8">{options.message_count}</span>
          </div>
        )
      
      case 'crazy_mouse':
        return (
          <div className="flex items-center gap-2 mt-2">
            <span className="text-sm text-gray-400">Duración:</span>
            <input
              type="range"
              min="1"
              max="15"
              value={options.crazy_duration}
              onChange={(e) => setOptions({...options, crazy_duration: parseInt(e.target.value)})}
              className="flex-1"
            />
            <span className="text-sm text-cyber-accent font-mono w-8">{options.crazy_duration}s</span>
          </div>
        )
      
      case 'block_site':
        return (
          <input
            type="text"
            value={options.block_domain}
            onChange={(e) => setOptions({...options, block_domain: e.target.value})}
            placeholder="ej: facebook.com"
            className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm
                     focus:outline-none focus:border-cyber-accent mt-2"
          />
        )
      
      case 'prank_server':
        return (
          <select
            value={options.prank_server_mode}
            onChange={(e) => setOptions({...options, prank_server_mode: e.target.value})}
            className="w-full bg-gray-800/50 border border-gray-700 rounded-lg px-3 py-2 text-sm
                     focus:outline-none focus:border-cyber-accent mt-2"
          >
            <option value="rickroll">🎵 Rickroll</option>
            <option value="bsod">💀 Pantalla Azul</option>
            <option value="hacked">☠️ Hacked!</option>
            <option value="jumpscare">👻 Jumpscare</option>
          </select>
        )
      
      default:
        return null
    }
  }

  const renderPrankCard = (prank) => {
    const Icon = PRANK_ICONS[prank.id] || Ghost
    const isActive = activePranks.some(a => a.id === prank.id)
    const isExecuting = executing === prank.id
    const prankResult = result?.prankId === prank.id ? result : null
    const isExpanded = expandedPrank === prank.id
    const hasOptions = ['speak', 'fake_error', 'sound_alert', 'browser_bomb', 'message_bomb', 
                       'popup_loop', 'block_site', 'prank_server', 'crazy_mouse'].includes(prank.id)
    
    return (
      <div 
        key={prank.id} 
        className={`cyber-card p-3 transition-all duration-200 hover:scale-[1.02] ${
          isActive ? 'ring-2 ring-cyber-accent' : ''
        }`}
      >
        <div className="flex items-center gap-3">
          {/* Icon */}
          <div className={`p-2.5 rounded-xl flex-shrink-0 ${
            isActive 
              ? 'bg-cyber-accent text-black' 
              : 'bg-gray-800 text-gray-400 group-hover:text-white'
          }`}>
            <Icon className="w-5 h-5" />
          </div>
          
          {/* Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-white truncate">{prank.name}</h3>
              {prank.requires_admin && (
                <span className="px-1.5 py-0.5 rounded text-[10px] bg-cyber-warning/20 text-cyber-warning flex-shrink-0">
                  ADMIN
                </span>
              )}
              <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                prank.danger_level === 'safe' ? 'bg-green-500' :
                prank.danger_level === 'medium' ? 'bg-yellow-500' : 'bg-red-500'
              }`} title={prank.danger_level}></span>
            </div>
            <p className="text-xs text-gray-500 truncate">{prank.description}</p>
          </div>
          
          {/* Action Button */}
          <div className="flex-shrink-0">
            {isActive ? (
              <button
                onClick={() => stopPrank(prank.id)}
                className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
              >
                <Square className="w-4 h-4" />
              </button>
            ) : (
              <div className="flex gap-1">
                {hasOptions && (
                  <button
                    onClick={() => setExpandedPrank(isExpanded ? null : prank.id)}
                    className="p-2 rounded-lg bg-gray-800 text-gray-400 hover:text-white transition-colors"
                  >
                    <Sparkles className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => handleExecutePrank(prank)}
                  disabled={isExecuting}
                  className="p-2 rounded-lg bg-cyber-accent/20 text-cyber-accent hover:bg-cyber-accent/30 
                           transition-colors disabled:opacity-50"
                >
                  {isExecuting ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Play className="w-4 h-4" />
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Expanded Options */}
        {isExpanded && hasOptions && (
          <div className="mt-3 pt-3 border-t border-gray-800">
            {renderPrankOptions(prank)}
          </div>
        )}

        {/* Result */}
        {prankResult && (
          <div className={`mt-2 p-2 rounded-lg text-xs flex items-center gap-2 ${
            prankResult.success 
              ? 'bg-green-500/20 text-green-400' 
              : 'bg-red-500/20 text-red-400'
          }`}>
            {prankResult.success ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
            {prankResult.message}
          </div>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-cyber-accent" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <Ghost className="w-8 h-8 text-cyber-accent" />
            Zona de Pranks
          </h1>
          <p className="text-gray-400 mt-1">
            {pranks.length} pranks disponibles • {activePranks.length} activas
          </p>
        </div>
        
        <div className="flex gap-3">
          <button onClick={loadPranks} className="cyber-btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
          </button>
          {activePranks.length > 0 && (
            <button onClick={stopAll} className="cyber-btn-danger flex items-center gap-2">
              <Square className="w-4 h-4" />
              Parar Todo
            </button>
          )}
        </div>
      </div>

      {/* Active Pranks */}
      {activePranks.length > 0 && (
        <div className="cyber-card p-4 border-cyber-accent/30 bg-cyber-accent/5">
          <div className="flex items-center gap-2 mb-3">
            <Radio className="w-5 h-5 text-cyber-accent animate-pulse" />
            <span className="font-semibold">Pranks Activas</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {activePranks.map((prank, idx) => {
              const Icon = PRANK_ICONS[prank.id] || Ghost
              return (
                <div key={idx} className="px-3 py-2 rounded-lg bg-cyber-accent/20 text-cyber-accent 
                                         flex items-center gap-2 text-sm">
                  <Icon className="w-4 h-4" />
                  <span>{prank.id}</span>
                  {prank.port && <span className="text-xs opacity-60">:{prank.port}</span>}
                  <button onClick={() => stopPrank(prank.id)} className="hover:text-white ml-1">
                    <XCircle className="w-4 h-4" />
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setSelectedCategory('all')}
          className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
            selectedCategory === 'all'
              ? 'bg-cyber-accent text-black font-medium'
              : 'bg-gray-800/50 text-gray-400 hover:text-white'
          }`}
        >
          Todas ({pranks.length})
        </button>
        {Object.entries(CATEGORIES).map(([key, cat]) => {
          const count = groupedPranks[key]?.length || 0
          if (count === 0) return null
          const CatIcon = cat.icon
          return (
            <button
              key={key}
              onClick={() => setSelectedCategory(key)}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors flex items-center gap-2 ${
                selectedCategory === key
                  ? 'bg-cyber-accent text-black font-medium'
                  : 'bg-gray-800/50 text-gray-400 hover:text-white'
              }`}
            >
              <CatIcon className="w-4 h-4" />
              {cat.name.split(' ').slice(1).join(' ')} ({count})
            </button>
          )
        })}
      </div>

      {/* Pranks by Category */}
      {filteredCategories.map(category => {
        const catPranks = groupedPranks[category]
        if (!catPranks || catPranks.length === 0) return null
        
        const catInfo = CATEGORIES[category] || { 
          name: category, 
          color: 'from-gray-500/20 to-transparent border-gray-500/30',
          icon: Ghost,
          description: ''
        }
        const CatIcon = catInfo.icon
        
        return (
          <div key={category} className="space-y-3">
            {/* Category Header */}
            <div className={`p-4 rounded-xl bg-gradient-to-r ${catInfo.color} border`}>
              <div className="flex items-center gap-3">
                <CatIcon className="w-6 h-6" />
                <div>
                  <h2 className="font-semibold text-lg">{catInfo.name}</h2>
                  <p className="text-sm text-gray-400">{catInfo.description}</p>
                </div>
                <span className="ml-auto px-2 py-1 bg-black/30 rounded text-sm">
                  {catPranks.length}
                </span>
              </div>
            </div>
            
            {/* Pranks Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {catPranks.map(prank => renderPrankCard(prank))}
            </div>
          </div>
        )
      })}

      {/* Quick Actions */}
      <div className="cyber-card p-6">
        <h2 className="font-semibold mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5 text-cyber-warning" />
          Acciones Rápidas
        </h2>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {[
            { id: 'rickroll', icon: Music, label: 'Rickroll', color: 'text-orange-400' },
            { id: 'fake_bsod', icon: MonitorX, label: 'BSOD', color: 'text-blue-400' },
            { id: 'crazy_mouse', icon: MousePointer, label: 'Mouse', color: 'text-purple-400' },
            { id: 'fake_virus', icon: Bug, label: 'Virus', color: 'text-red-400' },
            { id: 'matrix_screen', icon: Binary, label: 'Matrix', color: 'text-green-400' },
            { id: 'speak', icon: MessageCircle, label: 'Hablar', color: 'text-cyan-400' },
          ].map(action => (
            <button
              key={action.id}
              onClick={() => executePrank(action.id, action.id === 'speak' ? { text: '¡Hola!' } : {})}
              className="p-3 rounded-xl bg-gray-800/50 hover:bg-gray-800 transition-all 
                       hover:scale-105 text-center group"
            >
              <action.icon className={`w-6 h-6 mx-auto mb-1 ${action.color} 
                                      group-hover:scale-110 transition-transform`} />
              <span className="text-xs text-gray-400 group-hover:text-white">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Prank Server Info */}
      {activePranks.some(p => p.id === 'prank_server') && (
        <div className="cyber-card p-6 border-pink-500/30 bg-pink-500/5">
          <h2 className="font-semibold mb-3 flex items-center gap-2">
            <Server className="w-5 h-5 text-pink-400" />
            Servidor de Pranks Activo
          </h2>
          <p className="text-gray-400 mb-3">
            Comparte este link con dispositivos en tu red:
          </p>
          <div className="flex items-center gap-3">
            <code className="flex-1 bg-gray-900 px-4 py-2 rounded-lg font-mono text-pink-400 text-sm">
              http://{window.location.hostname}:8888
            </code>
            <button
              onClick={() => navigator.clipboard.writeText(`http://${window.location.hostname}:8888`)}
              className="cyber-btn-secondary px-4 text-sm"
            >
              Copiar
            </button>
          </div>
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <div className="cyber-card p-6">
          <h2 className="font-semibold mb-4 flex items-center gap-2">
            <History className="w-5 h-5 text-gray-400" />
            Historial ({history.length})
          </h2>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {history.slice().reverse().slice(0, 15).map((item, idx) => {
              const Icon = PRANK_ICONS[item.prank_id] || Ghost
              return (
                <div key={idx} className="flex items-center gap-3 py-2 border-b border-gray-800/50 last:border-0">
                  <Icon className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-300 text-sm">{item.prank_id}</span>
                  {item.result?.success !== undefined && (
                    item.result.success ? (
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-400" />
                    )
                  )}
                  <span className="text-xs text-gray-600 ml-auto">
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default Pranks
