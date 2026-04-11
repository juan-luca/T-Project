import React, { useState, useEffect } from 'react'
import { 
  Wifi, Signal, Lock, Unlock, RefreshCw, Play, Square,
  Download, Key, AlertTriangle, Radio, Users, Zap, FileText
} from 'lucide-react'
import { 
  getWiFiNetworks, scanWiFiNetworks, getWiFiAuditRequirements,
  startHandshakeCapture, stopHandshakeCapture, getCaptureStatus,
  sendDeauthForCapture, getWordlists, downloadWordlist, startCrack,
  startDeauth, stopDeauth, getDeauthStatus
} from '../services/api'

function WiFiNetworkCard({ network, onCapture, onDeauth, onCrack }) {
  const getSecurityColor = (encryption) => {
    if (!encryption || encryption === 'Open') return 'text-cyber-danger'
    if (encryption.includes('WEP')) return 'text-cyber-warning'
    return 'text-cyber-accent'
  }

  const getSignalBars = (signal) => {
    if (signal >= 80) return 4
    if (signal >= 60) return 3
    if (signal >= 40) return 2
    return 1
  }

  return (
    <div className="cyber-card-hover p-4">
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          {/* Signal Strength */}
          <div className="flex flex-col items-center">
            <Signal className={`w-6 h-6 ${
              network.signal >= 60 ? 'text-cyber-accent' :
              network.signal >= 40 ? 'text-cyber-warning' :
              'text-cyber-danger'
            }`} />
            <span className="text-xs mt-1">{network.signal}%</span>
          </div>

          {/* Network Info */}
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-semibold">{network.ssid || '(Hidden)'}</h3>
              {network.encryption && network.encryption !== 'Open' ? (
                <Lock className={`w-4 h-4 ${getSecurityColor(network.encryption)}`} />
              ) : (
                <Unlock className="w-4 h-4 text-cyber-danger" />
              )}
            </div>
            <p className="text-sm text-gray-400 font-mono">{network.bssid}</p>
            <div className="flex gap-4 mt-2 text-xs text-gray-500">
              <span>Canal: {network.channel}</span>
              <span className={getSecurityColor(network.encryption)}>
                {network.encryption || 'Open'}
              </span>
            </div>

            {/* Status badges */}
            <div className="flex gap-2 mt-2">
              {network.handshake_captured && (
                <span className="px-2 py-0.5 rounded text-xs bg-cyber-accent/20 text-cyber-accent">
                  Handshake ✓
                </span>
              )}
              {network.is_cracked && (
                <span className="px-2 py-0.5 rounded text-xs bg-cyber-purple/20 text-cyber-purple">
                  Contraseña: {network.password}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2">
          {!network.is_cracked && (
            <>
              <button
                onClick={() => onCapture(network)}
                className="px-3 py-1.5 text-xs rounded bg-cyber-accent/20 text-cyber-accent hover:bg-cyber-accent/30 transition-colors"
              >
                Capturar
              </button>
              <button
                onClick={() => onDeauth(network)}
                className="px-3 py-1.5 text-xs rounded bg-cyber-warning/20 text-cyber-warning hover:bg-cyber-warning/30 transition-colors"
              >
                Deauth
              </button>
              {network.handshake_captured && (
                <button
                  onClick={() => onCrack(network)}
                  className="px-3 py-1.5 text-xs rounded bg-cyber-purple/20 text-cyber-purple hover:bg-cyber-purple/30 transition-colors"
                >
                  Crackear
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function WiFiAudit() {
  const [networks, setNetworks] = useState([])
  const [requirements, setRequirements] = useState(null)
  const [wordlists, setWordlists] = useState([])
  const [isScanning, setIsScanning] = useState(false)
  const [captureStatus, setCaptureStatus] = useState(null)
  const [activeTab, setActiveTab] = useState('networks')
  const [crackModal, setCrackModal] = useState(null)
  const [selectedWordlist, setSelectedWordlist] = useState('')

  useEffect(() => {
    loadData()
    const interval = setInterval(checkCaptureStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [networksRes, reqsRes, wordlistsRes] = await Promise.all([
        getWiFiNetworks(),
        getWiFiAuditRequirements(),
        getWordlists()
      ])
      setNetworks(networksRes.data.networks || [])
      setRequirements(reqsRes.data)
      setWordlists(wordlistsRes.data)
    } catch (err) {
      console.error('Error loading data:', err)
    }
  }

  const handleScan = async () => {
    setIsScanning(true)
    try {
      const res = await scanWiFiNetworks()
      setNetworks(res.data.networks || [])
    } catch (err) {
      console.error('Scan error:', err)
    }
    setIsScanning(false)
  }

  const checkCaptureStatus = async () => {
    try {
      const res = await getCaptureStatus()
      setCaptureStatus(res.data)
    } catch (err) {
      // Ignore errors
    }
  }

  const handleStartCapture = async (network) => {
    try {
      await startHandshakeCapture(network.bssid, network.channel)
      checkCaptureStatus()
    } catch (err) {
      console.error('Capture error:', err)
    }
  }

  const handleStopCapture = async () => {
    try {
      await stopHandshakeCapture()
      checkCaptureStatus()
      loadData()
    } catch (err) {
      console.error('Stop capture error:', err)
    }
  }

  const handleSendDeauth = async (network) => {
    try {
      await sendDeauthForCapture(network.bssid)
    } catch (err) {
      console.error('Deauth error:', err)
    }
  }

  const handleStartCrack = async () => {
    if (!crackModal || !selectedWordlist) return
    
    try {
      const res = await startCrack(
        crackModal.handshake_path,
        selectedWordlist,
        'aircrack',
        crackModal.bssid
      )
      
      if (res.data.cracked) {
        alert(`¡Contraseña encontrada! ${res.data.password}`)
        loadData()
      } else {
        alert('No se encontró la contraseña con este wordlist')
      }
      
      setCrackModal(null)
    } catch (err) {
      console.error('Crack error:', err)
    }
  }

  const handleDownloadWordlist = async (name) => {
    try {
      await downloadWordlist(name)
      const res = await getWordlists()
      setWordlists(res.data)
    } catch (err) {
      console.error('Download error:', err)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <Wifi className="w-8 h-8 text-cyber-accent2" />
            WiFi Auditoría
          </h1>
          <p className="text-gray-400 mt-1">Herramientas de análisis de seguridad WiFi</p>
        </div>
        <button
          onClick={handleScan}
          disabled={isScanning}
          className="cyber-btn-primary flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${isScanning ? 'animate-spin' : ''}`} />
          {isScanning ? 'Escaneando...' : 'Escanear WiFi'}
        </button>
      </div>

      {/* Warning */}
      <div className="cyber-card p-4 border-cyber-danger/30 bg-cyber-danger/5">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-cyber-danger flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-cyber-danger">⚠️ Solo para tu propia red</p>
            <p className="text-sm text-gray-400 mt-1">
              Auditar redes WiFi ajenas sin autorización es ILEGAL. 
              Estas herramientas son solo para probar la seguridad de TU red.
            </p>
          </div>
        </div>
      </div>

      {/* Requirements Check */}
      {requirements && (
        <div className="cyber-card p-4">
          <h3 className="font-semibold mb-3">Estado del Sistema</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${requirements.capture?.scapy_available ? 'bg-cyber-accent' : 'bg-cyber-danger'}`} />
              <span className="text-sm">Scapy</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${requirements.capture?.aircrack_available ? 'bg-cyber-accent' : 'bg-gray-500'}`} />
              <span className="text-sm">Aircrack-ng</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${requirements.capture?.hashcat_available ? 'bg-cyber-accent' : 'bg-gray-500'}`} />
              <span className="text-sm">Hashcat</span>
            </div>
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${requirements.deauth?.monitor_mode_supported ? 'bg-cyber-accent' : 'bg-gray-500'}`} />
              <span className="text-sm">Monitor Mode</span>
            </div>
          </div>
          {requirements.capture?.recommendations?.length > 0 && (
            <div className="mt-3 text-sm text-gray-400">
              {requirements.capture.recommendations.map((rec, i) => (
                <p key={i}>• {rec}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Capture Status — real-time 4-way handshake progress */}
      {captureStatus?.is_capturing && (
        <div className="cyber-card p-4 border-cyber-accent/30 bg-cyber-accent/5">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <Radio className="w-5 h-5 text-cyber-accent animate-pulse" />
              <div>
                <p className="font-medium">Capturando handshake WPA...</p>
                <p className="text-sm text-gray-400 font-mono">
                  {captureStatus.current?.target_bssid} | Canal {captureStatus.current?.channel}
                </p>
              </div>
            </div>
            <button
              onClick={handleStopCapture}
              className="cyber-btn-danger flex items-center gap-2"
            >
              <Square className="w-4 h-4" />
              Detener
            </button>
          </div>

          {/* 4-way handshake message tracker */}
          <div className="mt-2">
            <p className="text-xs text-gray-500 mb-2">
              Progreso del 4-way handshake (necesitas M1+M2 o M2+M3 para crackear):
            </p>
            <div className="flex gap-2 flex-wrap">
              {['M1', 'M2', 'M3', 'M4'].map((msg) => {
                const captured = (captureStatus.current?.eapol_messages || []).includes(msg)
                const isMinimum = msg === 'M1' || msg === 'M2' || msg === 'M3'
                return (
                  <div
                    key={msg}
                    className={`flex items-center gap-1 px-3 py-1 rounded-full text-sm font-mono border
                      ${captured
                        ? 'bg-cyber-accent/20 border-cyber-accent text-cyber-accent'
                        : 'bg-gray-800/50 border-gray-600 text-gray-500'
                      }`}
                  >
                    <span className={captured ? 'text-cyber-accent' : 'text-gray-600'}>
                      {captured ? '✓' : '○'}
                    </span>
                    {msg}
                    {isMinimum && (
                      <span className="text-xs opacity-60 ml-1">
                        {msg === 'M1' ? 'ANonce' : msg === 'M2' ? 'SNonce+MIC' : 'GTK+MIC'}
                      </span>
                    )}
                  </div>
                )
              })}
            </div>

            {captureStatus.current?.handshake_complete && (
              <p className="text-cyber-accent text-sm mt-2 font-semibold">
                ✓ Handshake válido capturado — listo para crackear offline
              </p>
            )}

            <p className="text-xs text-gray-600 mt-2">
              Paquetes EAPOL totales: {captureStatus.current?.eapol_count || 0} |
              Paquetes capturados: {captureStatus.current?.packets_captured || 0}
            </p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-800 pb-2">
        {[
          { id: 'networks', label: 'Redes WiFi', icon: Wifi },
          { id: 'wordlists', label: 'Wordlists', icon: FileText },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
              activeTab === tab.id
                ? 'bg-cyber-accent/20 text-cyber-accent'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Networks Tab */}
      {activeTab === 'networks' && (
        <div className="space-y-4">
          {networks.length > 0 ? (
            networks.map((network, i) => (
              <WiFiNetworkCard
                key={i}
                network={network}
                onCapture={handleStartCapture}
                onDeauth={handleSendDeauth}
                onCrack={setCrackModal}
              />
            ))
          ) : (
            <div className="text-center py-12">
              <Wifi className="w-16 h-16 mx-auto text-gray-600 mb-4" />
              <h3 className="text-xl font-semibold text-gray-400">No hay redes</h3>
              <p className="text-gray-500 mt-2">Haz click en "Escanear WiFi" para buscar redes</p>
            </div>
          )}
        </div>
      )}

      {/* Wordlists Tab */}
      {activeTab === 'wordlists' && (
        <div className="space-y-4">
          <div className="cyber-card p-4">
            <h3 className="font-semibold mb-3">Descargar Wordlists</h3>
            <div className="flex gap-2">
              <button
                onClick={() => handleDownloadWordlist('rockyou')}
                className="cyber-btn-secondary flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                RockYou (14M)
              </button>
              <button
                onClick={() => handleDownloadWordlist('common')}
                className="cyber-btn-secondary flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Common (100K)
              </button>
            </div>
          </div>

          <div className="cyber-card p-4">
            <h3 className="font-semibold mb-3">Wordlists Disponibles</h3>
            {wordlists.length > 0 ? (
              <div className="space-y-2">
                {wordlists.map((wl, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-gray-800/30">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-cyber-accent2" />
                      <div>
                        <p className="font-medium">{wl.name}</p>
                        <p className="text-sm text-gray-400">
                          {wl.words?.toLocaleString()} palabras • {(wl.size / 1024 / 1024).toFixed(1)} MB
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500">No hay wordlists descargadas</p>
            )}
          </div>
        </div>
      )}

      {/* Crack Modal */}
      {crackModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setCrackModal(null)}>
          <div className="bg-cyber-dark border border-gray-800 rounded-xl p-6 max-w-md w-full mx-4" onClick={e => e.stopPropagation()}>
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Key className="w-6 h-6 text-cyber-purple" />
              Crackear Handshake
            </h3>

            <div className="mb-4">
              <p className="text-gray-400">Red: <span className="text-white">{crackModal.ssid}</span></p>
              <p className="text-gray-400 text-sm font-mono">{crackModal.bssid}</p>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-400 mb-2">
                Seleccionar Wordlist
              </label>
              <select
                value={selectedWordlist}
                onChange={e => setSelectedWordlist(e.target.value)}
                className="cyber-input"
              >
                <option value="">Seleccionar...</option>
                {wordlists.map((wl, i) => (
                  <option key={i} value={wl.path}>{wl.name}</option>
                ))}
              </select>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setCrackModal(null)}
                className="flex-1 cyber-btn-secondary"
              >
                Cancelar
              </button>
              <button
                onClick={handleStartCrack}
                disabled={!selectedWordlist}
                className="flex-1 cyber-btn-primary disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Zap className="w-4 h-4" />
                Iniciar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default WiFiAudit
