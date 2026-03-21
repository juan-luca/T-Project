import React from 'react'
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react'

/**
 * Error Boundary Component
 * Catches JavaScript errors in child components and displays a fallback UI
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null,
      eventId: null
    }
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    // Log error to console
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    // Store error info for display
    this.setState({
      errorInfo,
      eventId: Date.now().toString(36)
    })
    
    // Log to backend if available
    this.logErrorToBackend(error, errorInfo)
  }

  logErrorToBackend = async (error, errorInfo) => {
    try {
      // Attempt to log error to backend
      await fetch('/api/v1/logs/error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'frontend_error',
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo?.componentStack,
          url: window.location.href,
          timestamp: new Date().toISOString()
        })
      }).catch(() => {}) // Silent fail if backend unavailable
    } catch {
      // Ignore logging errors
    }
  }

  handleReset = () => {
    this.setState({ 
      hasError: false, 
      error: null, 
      errorInfo: null,
      eventId: null
    })
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  handleRefresh = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback prop
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleReset)
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-cyber-dark flex items-center justify-center p-4">
          <div className="max-w-lg w-full bg-cyber-card rounded-2xl border border-gray-700 overflow-hidden">
            {/* Header */}
            <div className="bg-red-500/10 border-b border-red-500/30 p-6">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-red-500/20 rounded-xl">
                  <AlertTriangle className="w-8 h-8 text-red-400" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white">
                    ¡Algo salió mal!
                  </h1>
                  <p className="text-gray-400 text-sm">
                    Se produjo un error inesperado
                  </p>
                </div>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 space-y-4">
              <p className="text-gray-300">
                Lo sentimos, ha ocurrido un error en la aplicación. 
                Puedes intentar las siguientes opciones:
              </p>

              {/* Error details (development only) */}
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700">
                  <div className="flex items-center gap-2 mb-2">
                    <Bug className="w-4 h-4 text-purple-400" />
                    <span className="text-sm font-medium text-purple-400">
                      Detalles del error (Dev Mode)
                    </span>
                  </div>
                  <pre className="text-xs text-red-400 overflow-x-auto whitespace-pre-wrap">
                    {this.state.error.message}
                  </pre>
                  {this.state.errorInfo?.componentStack && (
                    <pre className="text-xs text-gray-500 mt-2 overflow-x-auto whitespace-pre-wrap max-h-32">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  )}
                </div>
              )}

              {/* Event ID */}
              {this.state.eventId && (
                <p className="text-xs text-gray-500">
                  ID del error: <code className="text-purple-400">{this.state.eventId}</code>
                </p>
              )}
            </div>

            {/* Actions */}
            <div className="p-6 pt-0 flex flex-col sm:flex-row gap-3">
              <button
                onClick={this.handleRefresh}
                className="flex-1 px-4 py-3 bg-cyber-accent text-cyber-dark rounded-lg font-medium hover:bg-cyber-accent/80 transition flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-4 h-4" />
                Recargar página
              </button>
              <button
                onClick={this.handleGoHome}
                className="flex-1 px-4 py-3 bg-gray-700 text-white rounded-lg font-medium hover:bg-gray-600 transition flex items-center justify-center gap-2"
              >
                <Home className="w-4 h-4" />
                Ir al inicio
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * Wrapper component for sections that might fail independently
 */
export const SectionErrorBoundary = ({ children, fallbackMessage = "Este módulo no está disponible" }) => {
  return (
    <ErrorBoundary
      fallback={(error, reset) => (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-center">
          <AlertTriangle className="w-8 h-8 text-red-400 mx-auto mb-3" />
          <p className="text-red-400 font-medium mb-2">
            {fallbackMessage}
          </p>
          <p className="text-gray-500 text-sm mb-4">
            {error?.message || 'Error desconocido'}
          </p>
          <button
            onClick={reset}
            className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition text-sm"
          >
            Reintentar
          </button>
        </div>
      )}
    >
      {children}
    </ErrorBoundary>
  )
}

export default ErrorBoundary
