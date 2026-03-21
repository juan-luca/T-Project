import React, { useState, useEffect } from 'react'
import { Bell, Menu, Search, RefreshCw, Wifi, WifiOff } from 'lucide-react'
import { getAlerts, getConnectedWiFi } from '../services/api'

function Header({ toggleSidebar }) {
  const [alerts, setAlerts] = useState([])
  const [showAlerts, setShowAlerts] = useState(false)
  const [wifiStatus, setWifiStatus] = useState(null)
  const [isScanning, setIsScanning] = useState(false)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [alertsRes, wifiRes] = await Promise.all([
        getAlerts(5, true),
        getConnectedWiFi()
      ])
      setAlerts(alertsRes.data)
      setWifiStatus(wifiRes.data)
    } catch (err) {
      console.error('Error loading header data:', err)
    }
  }

  const unreadCount = alerts.filter(a => !a.is_read).length

  return (
    <header className="h-16 bg-cyber-dark/80 backdrop-blur-sm border-b border-gray-800 flex items-center justify-between px-6">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Search */}
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            placeholder="Buscar..."
            className="w-64 pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-sm focus:outline-none focus:border-cyber-accent transition-colors"
          />
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* WiFi Status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800/50 border border-gray-700">
          {wifiStatus?.ssid ? (
            <>
              <Wifi className="w-4 h-4 text-cyber-accent" />
              <span className="text-sm font-medium">{wifiStatus.ssid}</span>
              {wifiStatus.signal && (
                <span className="text-xs text-gray-400">{wifiStatus.signal}%</span>
              )}
            </>
          ) : (
            <>
              <WifiOff className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-500">Sin conexión</span>
            </>
          )}
        </div>

        {/* Refresh Button */}
        <button
          onClick={loadData}
          disabled={isScanning}
          className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-5 h-5 ${isScanning ? 'animate-spin' : ''}`} />
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowAlerts(!showAlerts)}
            className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800 transition-colors relative"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 bg-cyber-danger rounded-full text-xs flex items-center justify-center text-white font-bold">
                {unreadCount}
              </span>
            )}
          </button>

          {/* Alerts Dropdown */}
          {showAlerts && (
            <div className="absolute right-0 top-full mt-2 w-80 bg-cyber-dark border border-gray-800 rounded-xl shadow-2xl z-50 overflow-hidden">
              <div className="p-3 border-b border-gray-800">
                <h3 className="font-semibold">Alertas</h3>
              </div>
              <div className="max-h-80 overflow-y-auto">
                {alerts.length > 0 ? (
                  alerts.map((alert, i) => (
                    <div key={i} className="p-3 border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                      <div className="flex items-start gap-3">
                        <div className={`w-2 h-2 rounded-full mt-2 ${
                          alert.severity === 'high' ? 'bg-cyber-danger' :
                          alert.severity === 'medium' ? 'bg-cyber-warning' :
                          'bg-cyber-accent'
                        }`} />
                        <div>
                          <p className="font-medium text-sm">{alert.title}</p>
                          <p className="text-xs text-gray-400 mt-1">{alert.description}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(alert.timestamp).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-4 text-center text-gray-500">
                    No hay alertas nuevas
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* User */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyber-purple to-cyber-accent2 flex items-center justify-center text-sm font-bold">
            A
          </div>
          <span className="text-sm font-medium hidden md:block">Admin</span>
        </div>
      </div>
    </header>
  )
}

export default Header
