import React, { useState } from 'react'
import { 
  Shield, AlertTriangle, Eye, Lock, Users, 
  Search, RefreshCw, CheckCircle, XCircle
} from 'lucide-react'

function Security() {
  const [scanning, setScanning] = useState(false)
  const [results, setResults] = useState(null)

  const runSecurityScan = () => {
    setScanning(true)
    // Simulated security scan
    setTimeout(() => {
      setResults({
        score: 78,
        checks: [
          { name: 'Firewall activo', status: 'pass', description: 'Windows Firewall está habilitado' },
          { name: 'Encriptación WiFi', status: 'pass', description: 'WPA2/WPA3 detectado' },
          { name: 'Puertos expuestos', status: 'warning', description: '3 puertos abiertos detectados' },
          { name: 'Dispositivos desconocidos', status: 'warning', description: '2 dispositivos sin identificar' },
          { name: 'Actualización del router', status: 'fail', description: 'Firmware desactualizado' },
          { name: 'Contraseña WiFi', status: 'pass', description: 'Contraseña fuerte detectada' },
        ]
      })
      setScanning(false)
    }, 3000)
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pass': return <CheckCircle className="w-5 h-5 text-cyber-accent" />
      case 'warning': return <AlertTriangle className="w-5 h-5 text-cyber-warning" />
      case 'fail': return <XCircle className="w-5 h-5 text-cyber-danger" />
      default: return null
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-cyber-accent'
    if (score >= 60) return 'text-cyber-warning'
    return 'text-cyber-danger'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <Shield className="w-8 h-8 text-cyber-accent" />
            Centro de Seguridad
          </h1>
          <p className="text-gray-400 mt-1">Análisis y protección de tu red</p>
        </div>
        <button
          onClick={runSecurityScan}
          disabled={scanning}
          className="cyber-btn-primary flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
          {scanning ? 'Escaneando...' : 'Escanear Seguridad'}
        </button>
      </div>

      {/* Security Score */}
      {results && (
        <div className="cyber-card p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">Puntuación de Seguridad</h2>
              <p className="text-gray-400 text-sm mt-1">Basado en el último escaneo</p>
            </div>
            <div className="text-center">
              <div className={`text-5xl font-bold ${getScoreColor(results.score)}`}>
                {results.score}
              </div>
              <p className="text-gray-400 text-sm">/100</p>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            {results.checks.map((check, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-gray-800/30">
                <div className="flex items-center gap-3">
                  {getStatusIcon(check.status)}
                  <div>
                    <p className="font-medium">{check.name}</p>
                    <p className="text-sm text-gray-400">{check.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Security Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="cyber-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 rounded-xl bg-cyber-accent/10">
              <Eye className="w-6 h-6 text-cyber-accent" />
            </div>
            <h3 className="font-semibold">Detección de Intrusos</h3>
          </div>
          <p className="text-gray-400 text-sm">
            Monitoreo automático de nuevos dispositivos que se conectan a tu red.
          </p>
          <div className="mt-4 flex items-center justify-between">
            <span className="text-sm text-gray-500">Estado</span>
            <span className="text-cyber-accent">Activo</span>
          </div>
        </div>

        <div className="cyber-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 rounded-xl bg-cyber-accent2/10">
              <Lock className="w-6 h-6 text-cyber-accent2" />
            </div>
            <h3 className="font-semibold">Bloqueo de Dispositivos</h3>
          </div>
          <p className="text-gray-400 text-sm">
            Bloquea el acceso a internet de dispositivos no autorizados.
          </p>
          <div className="mt-4 flex items-center justify-between">
            <span className="text-sm text-gray-500">Bloqueados</span>
            <span className="text-white">0</span>
          </div>
        </div>

        <div className="cyber-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 rounded-xl bg-cyber-warning/10">
              <AlertTriangle className="w-6 h-6 text-cyber-warning" />
            </div>
            <h3 className="font-semibold">Alertas en Tiempo Real</h3>
          </div>
          <p className="text-gray-400 text-sm">
            Recibe notificaciones instantáneas de actividad sospechosa.
          </p>
          <div className="mt-4 flex items-center justify-between">
            <span className="text-sm text-gray-500">Hoy</span>
            <span className="text-cyber-warning">3 alertas</span>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="cyber-card p-6">
        <h2 className="text-lg font-semibold mb-4">Recomendaciones de Seguridad</h2>
        <div className="space-y-3">
          <div className="p-4 rounded-lg bg-cyber-warning/10 border border-cyber-warning/30">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-cyber-warning flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-cyber-warning">Actualiza el firmware del router</p>
                <p className="text-sm text-gray-400 mt-1">
                  Tu router puede tener vulnerabilidades conocidas. Verifica si hay actualizaciones disponibles.
                </p>
              </div>
            </div>
          </div>
          
          <div className="p-4 rounded-lg bg-gray-800/30">
            <div className="flex items-start gap-3">
              <Lock className="w-5 h-5 text-cyber-accent flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Cambia las credenciales por defecto</p>
                <p className="text-sm text-gray-400 mt-1">
                  Asegúrate de que tu router no use usuario/contraseña por defecto (admin/admin).
                </p>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-gray-800/30">
            <div className="flex items-start gap-3">
              <Users className="w-5 h-5 text-cyber-accent2 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium">Revisa los dispositivos conectados</p>
                <p className="text-sm text-gray-400 mt-1">
                  Regularmente verifica qué dispositivos están en tu red y elimina los desconocidos.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Security
