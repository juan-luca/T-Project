import React, { useState, useEffect } from 'react'
import { 
  Settings as SettingsIcon, Save, RefreshCw, Wifi, 
  Shield, Bell, Database, Palette, Terminal
} from 'lucide-react'
import api from '../services/api'

function Settings() {
  const [settings, setSettings] = useState({
    network: {
      interface: 'wlan0',
      scanInterval: 60,
      autoScan: true,
      gateway: '192.168.1.1',
      subnet: '192.168.1.0/24'
    },
    security: {
      alertOnNewDevice: true,
      autoBlockUnknown: false,
      logRetentionDays: 30
    },
    notifications: {
      enabled: true,
      sound: true,
      desktop: true
    },
    appearance: {
      theme: 'dark',
      accentColor: '#00f0ff',
      compactMode: false
    }
  })
  const [saved, setSaved] = useState(false)
  const [interfaces, setInterfaces] = useState(['wlan0', 'eth0', 'wlan1'])

  useEffect(() => {
    fetchSettings()
    fetchInterfaces()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await api.get('/settings')
      if (response.data) {
        setSettings(prev => ({ ...prev, ...response.data }))
      }
    } catch (error) {
      console.error('Error fetching settings:', error)
    }
  }

  const fetchInterfaces = async () => {
    try {
      const response = await api.get('/network/interfaces')
      if (response.data.interfaces) {
        setInterfaces(response.data.interfaces)
      }
    } catch (error) {
      console.error('Error fetching interfaces:', error)
    }
  }

  const handleSave = async () => {
    try {
      await api.post('/settings', settings)
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (error) {
      console.error('Error saving settings:', error)
    }
  }

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <SettingsIcon className="w-8 h-8 text-cyber-accent" />
            Configuración
          </h1>
          <p className="text-gray-400 mt-1">Personaliza el comportamiento del sistema</p>
        </div>
        <button
          onClick={handleSave}
          className={`cyber-btn-primary flex items-center gap-2 ${saved ? 'bg-cyber-accent' : ''}`}
        >
          {saved ? (
            <>
              <RefreshCw className="w-4 h-4" />
              Guardado!
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Guardar Cambios
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Network Settings */}
        <div className="cyber-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-lg bg-cyber-accent/10">
              <Wifi className="w-5 h-5 text-cyber-accent" />
            </div>
            <h2 className="text-lg font-semibold">Red</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Interfaz de Red
              </label>
              <select
                value={settings.network.interface}
                onChange={(e) => updateSetting('network', 'interface', e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 
                         focus:outline-none focus:border-cyber-accent"
              >
                {interfaces.map(iface => (
                  <option key={iface} value={iface}>{iface}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Gateway
              </label>
              <input
                type="text"
                value={settings.network.gateway}
                onChange={(e) => updateSetting('network', 'gateway', e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 
                         focus:outline-none focus:border-cyber-accent"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Subred
              </label>
              <input
                type="text"
                value={settings.network.subnet}
                onChange={(e) => updateSetting('network', 'subnet', e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 
                         focus:outline-none focus:border-cyber-accent"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Intervalo de Escaneo (segundos)
              </label>
              <input
                type="number"
                value={settings.network.scanInterval}
                onChange={(e) => updateSetting('network', 'scanInterval', parseInt(e.target.value))}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 
                         focus:outline-none focus:border-cyber-accent"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50">
              <div>
                <p className="font-medium">Auto-escaneo</p>
                <p className="text-sm text-gray-500">Escanear red automáticamente</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.network.autoScan}
                  onChange={(e) => updateSetting('network', 'autoScan', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer 
                              peer-checked:after:translate-x-full peer-checked:after:border-white 
                              after:content-[''] after:absolute after:top-[2px] after:left-[2px] 
                              after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all 
                              peer-checked:bg-cyber-accent"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Security Settings */}
        <div className="cyber-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-lg bg-cyber-accent2/10">
              <Shield className="w-5 h-5 text-cyber-accent2" />
            </div>
            <h2 className="text-lg font-semibold">Seguridad</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50">
              <div>
                <p className="font-medium">Alertar nuevos dispositivos</p>
                <p className="text-sm text-gray-500">Notificar cuando se conecte un dispositivo nuevo</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.security.alertOnNewDevice}
                  onChange={(e) => updateSetting('security', 'alertOnNewDevice', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer 
                              peer-checked:after:translate-x-full peer-checked:after:border-white 
                              after:content-[''] after:absolute after:top-[2px] after:left-[2px] 
                              after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all 
                              peer-checked:bg-cyber-accent"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50">
              <div>
                <p className="font-medium">Auto-bloqueo</p>
                <p className="text-sm text-gray-500">Bloquear automáticamente dispositivos desconocidos</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.security.autoBlockUnknown}
                  onChange={(e) => updateSetting('security', 'autoBlockUnknown', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer 
                              peer-checked:after:translate-x-full peer-checked:after:border-white 
                              after:content-[''] after:absolute after:top-[2px] after:left-[2px] 
                              after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all 
                              peer-checked:bg-cyber-accent"></div>
              </label>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Retención de Logs (días)
              </label>
              <input
                type="number"
                value={settings.security.logRetentionDays}
                onChange={(e) => updateSetting('security', 'logRetentionDays', parseInt(e.target.value))}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 
                         focus:outline-none focus:border-cyber-accent"
              />
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="cyber-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-lg bg-cyber-warning/10">
              <Bell className="w-5 h-5 text-cyber-warning" />
            </div>
            <h2 className="text-lg font-semibold">Notificaciones</h2>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50">
              <div>
                <p className="font-medium">Notificaciones</p>
                <p className="text-sm text-gray-500">Habilitar todas las notificaciones</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifications.enabled}
                  onChange={(e) => updateSetting('notifications', 'enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer 
                              peer-checked:after:translate-x-full peer-checked:after:border-white 
                              after:content-[''] after:absolute after:top-[2px] after:left-[2px] 
                              after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all 
                              peer-checked:bg-cyber-accent"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50">
              <div>
                <p className="font-medium">Sonido</p>
                <p className="text-sm text-gray-500">Reproducir sonido en alertas</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifications.sound}
                  onChange={(e) => updateSetting('notifications', 'sound', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer 
                              peer-checked:after:translate-x-full peer-checked:after:border-white 
                              after:content-[''] after:absolute after:top-[2px] after:left-[2px] 
                              after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all 
                              peer-checked:bg-cyber-accent"></div>
              </label>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50">
              <div>
                <p className="font-medium">Notificaciones de Escritorio</p>
                <p className="text-sm text-gray-500">Mostrar notificaciones del sistema</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.notifications.desktop}
                  onChange={(e) => updateSetting('notifications', 'desktop', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer 
                              peer-checked:after:translate-x-full peer-checked:after:border-white 
                              after:content-[''] after:absolute after:top-[2px] after:left-[2px] 
                              after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all 
                              peer-checked:bg-cyber-accent"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Appearance Settings */}
        <div className="cyber-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-lg bg-cyber-accent/10">
              <Palette className="w-5 h-5 text-cyber-accent" />
            </div>
            <h2 className="text-lg font-semibold">Apariencia</h2>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Tema
              </label>
              <select
                value={settings.appearance.theme}
                onChange={(e) => updateSetting('appearance', 'theme', e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 
                         focus:outline-none focus:border-cyber-accent"
              >
                <option value="dark">Oscuro (Cyber)</option>
                <option value="light">Claro</option>
                <option value="hacker">Hacker (Verde)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                Color de Acento
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="color"
                  value={settings.appearance.accentColor}
                  onChange={(e) => updateSetting('appearance', 'accentColor', e.target.value)}
                  className="w-12 h-12 rounded-lg border-0 cursor-pointer"
                />
                <input
                  type="text"
                  value={settings.appearance.accentColor}
                  onChange={(e) => updateSetting('appearance', 'accentColor', e.target.value)}
                  className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 
                           focus:outline-none focus:border-cyber-accent font-mono"
                />
              </div>
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50">
              <div>
                <p className="font-medium">Modo Compacto</p>
                <p className="text-sm text-gray-500">Reducir espaciado para más contenido</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.appearance.compactMode}
                  onChange={(e) => updateSetting('appearance', 'compactMode', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer 
                              peer-checked:after:translate-x-full peer-checked:after:border-white 
                              after:content-[''] after:absolute after:top-[2px] after:left-[2px] 
                              after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all 
                              peer-checked:bg-cyber-accent"></div>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* System Info */}
      <div className="cyber-card p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 rounded-lg bg-gray-700/50">
            <Terminal className="w-5 h-5 text-gray-400" />
          </div>
          <h2 className="text-lg font-semibold">Información del Sistema</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-3 rounded-lg bg-gray-800/50">
            <p className="text-sm text-gray-400">Versión</p>
            <p className="font-mono">1.0.0</p>
          </div>
          <div className="p-3 rounded-lg bg-gray-800/50">
            <p className="text-sm text-gray-400">Python</p>
            <p className="font-mono">3.11.0</p>
          </div>
          <div className="p-3 rounded-lg bg-gray-800/50">
            <p className="text-sm text-gray-400">Base de Datos</p>
            <p className="font-mono">SQLite 3.40</p>
          </div>
          <div className="p-3 rounded-lg bg-gray-800/50">
            <p className="text-sm text-gray-400">Plataforma</p>
            <p className="font-mono">Windows</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Settings
