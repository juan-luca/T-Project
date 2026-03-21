import axios from 'axios'

const API_BASE = '/api/v1'

// Create axios instance with defaults
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - add timestamp to requests
api.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: Date.now() }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle errors globally
api.interceptors.response.use(
  (response) => {
    // Log successful requests in development
    if (import.meta.env?.DEV) {
      const duration = Date.now() - response.config.metadata?.startTime
      console.debug(`[API] ${response.config.method.toUpperCase()} ${response.config.url} - ${duration}ms`)
    }
    return response
  },
  (error) => {
    // Extract error details
    const errorInfo = {
      code: error.response?.data?.error?.code || 'NETWORK_ERROR',
      message: error.response?.data?.error?.message || error.message,
      status: error.response?.status || 0,
      url: error.config?.url
    }

    // Log errors
    console.error(`[API Error] ${errorInfo.code}: ${errorInfo.message}`, {
      status: errorInfo.status,
      url: errorInfo.url
    })

    // Enhance error object
    error.apiError = errorInfo

    return Promise.reject(error)
  }
)

// Helper to extract error message
export const getErrorMessage = (error) => {
  return error.apiError?.message || error.message || 'Error desconocido'
}

// Health Check
export const getHealth = () => api.get('/health')
export const getHealthSimple = () => api.get('/health/simple')

// Dashboard
export const getDashboardStats = () => api.get('/dashboard/stats')
export const getNetworkInfo = () => api.get('/dashboard/network-info')

// Devices
export const getDevices = () => api.get('/devices')
export const getDevice = (id) => api.get(`/devices/${id}`)
export const updateDevice = (id, data) => api.put(`/devices/${id}`, data)
export const scanNetwork = (type = 'arp') => api.post('/devices/scan', { type })
export const scanPorts = (deviceId, ports = null) => api.post(`/devices/${deviceId}/ports`, { ports })

// Alerts
export const getAlerts = (limit = 50, unread = false) => 
  api.get('/alerts', { params: { limit, unread } })
export const markAlertRead = (id) => api.post(`/alerts/${id}/read`)
export const markAllAlertsRead = () => api.post('/alerts/read-all')

// WiFi
export const getWiFiNetworks = () => api.get('/wifi/networks')
export const getConnectedWiFi = () => api.get('/wifi/connected')

// WiFi Audit
export const getWiFiAuditRequirements = () => api.get('/wifi-audit/requirements')
export const scanWiFiNetworks = () => api.get('/wifi-audit/scan')
export const startHandshakeCapture = (bssid, channel, timeout = 300) => 
  api.post('/wifi-audit/capture/start', { bssid, channel, timeout })
export const stopHandshakeCapture = () => api.post('/wifi-audit/capture/stop')
export const getCaptureStatus = () => api.get('/wifi-audit/capture/status')
export const sendDeauthForCapture = (bssid, clientMac = 'ff:ff:ff:ff:ff:ff', count = 5) =>
  api.post('/wifi-audit/capture/deauth', { bssid, client_mac: clientMac, count })
export const getWordlists = () => api.get('/wifi-audit/crack/wordlists')
export const downloadWordlist = (name) => api.post('/wifi-audit/crack/wordlists/download', { name })
export const startCrack = (captureFile, wordlist, method = 'aircrack', bssid = null) =>
  api.post('/wifi-audit/crack/start', { capture_file: captureFile, wordlist, method, bssid })
export const startDeauth = (targetMac, apMac, interval = 0.1) =>
  api.post('/wifi-audit/deauth/start', { target_mac: targetMac, ap_mac: apMac, interval })
export const stopDeauth = (targetMac = null) => api.post('/wifi-audit/deauth/stop', { target_mac: targetMac })
export const getDeauthStatus = () => api.get('/wifi-audit/deauth/status')

// Pranks
export const getPranks = () => api.get('/pranks')
export const executePrank = (prankId, options = {}) =>
  api.post('/pranks/execute', { prank_id: prankId, options })
export const stopPrank = (prankId) =>
  api.post('/pranks/stop', { prank_id: prankId })
export const stopAllPranks = () => api.post('/pranks/stop-all')
export const getPranksHistory = () => api.get('/pranks/history')

// Tools
export const wakeOnLan = (mac) => api.post('/tools/wake-on-lan', { mac })
export const pingHost = (host) => api.post('/tools/ping', { host })
export const traceroute = (host) => api.post('/tools/traceroute', { host })
export const dnsLookup = (domain) => api.post('/tools/dns-lookup', { domain })

// System Tools
export const runSpeedTest = (includeUpload = true) => 
  api.post('/system/speed-test', { include_upload: includeUpload })
export const getWifiPasswords = () => api.get('/system/wifi-passwords')
export const getConnections = () => api.get('/system/connections')
export const getConnectionStats = () => api.get('/system/connections/stats')
export const getProcessNetwork = () => api.get('/system/processes')
export const systemPing = (host, count = 4) => api.post('/system/ping', { host, count })
export const pingMultiple = (hosts) => api.post('/system/ping-multiple', { hosts })
export const getArpTable = () => api.get('/system/arp-table')
export const flushArp = () => api.post('/system/arp-flush')
export const getDnsCache = () => api.get('/system/dns-cache')
export const flushDns = () => api.post('/system/dns-flush')
export const getInterfaces = () => api.get('/system/interfaces')
export const getNetworkStats = () => api.get('/system/network-stats')

export default api
