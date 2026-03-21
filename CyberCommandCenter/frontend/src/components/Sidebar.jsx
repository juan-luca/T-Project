import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Monitor, 
  Shield, 
  Wrench, 
  Ghost,
  Wifi,
  Activity,
  FileText,
  Settings,
  ChevronLeft,
  ChevronRight,
  Smartphone,
  BarChart3,
  Key
} from 'lucide-react'

const menuItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
  { icon: Monitor, label: 'Dispositivos', path: '/devices' },
  { icon: Smartphone, label: 'Control iOS/Android', path: '/device-control' },
  { icon: Shield, label: 'Seguridad', path: '/security' },
  { icon: Wrench, label: 'Herramientas', path: '/tools' },
  { icon: Ghost, label: 'Pranks', path: '/pranks' },
  { icon: Wifi, label: 'WiFi Audit', path: '/wifi-audit' },
  { icon: Key, label: 'WiFi Hacker', path: '/wifi-hacker' },
  { icon: Activity, label: 'Tráfico', path: '/traffic' },
  { icon: BarChart3, label: 'Monitor Tráfico', path: '/traffic-monitor' },
  { icon: FileText, label: 'Logs', path: '/logs' },
  { icon: Settings, label: 'Configuración', path: '/settings' },
]

function Sidebar({ isOpen, setIsOpen }) {
  return (
    <aside className={`${isOpen ? 'w-64' : 'w-20'} bg-cyber-dark border-r border-gray-800 transition-all duration-300 flex flex-col`}>
      {/* Logo */}
      <div className="h-16 flex items-center justify-center border-b border-gray-800 px-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyber-accent to-cyber-accent2 flex items-center justify-center">
            <Shield className="w-6 h-6 text-cyber-dark" />
          </div>
          {isOpen && (
            <div className="overflow-hidden">
              <h1 className="text-lg font-bold text-white whitespace-nowrap">Cyber Command</h1>
              <p className="text-xs text-gray-500 whitespace-nowrap">Security Center</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `
              flex items-center gap-3 px-3 py-3 rounded-lg transition-all duration-200
              ${isActive 
                ? 'bg-cyber-accent/10 text-cyber-accent border border-cyber-accent/30' 
                : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
              }
            `}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            {isOpen && <span className="font-medium">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="h-12 flex items-center justify-center border-t border-gray-800 text-gray-400 hover:text-white transition-colors"
      >
        {isOpen ? <ChevronLeft className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
      </button>
    </aside>
  )
}

export default Sidebar
