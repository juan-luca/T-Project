import axios from 'axios'

const API_BASE = '/api/v1'

// Axios instance shared across all pages
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor – stamp start time for latency logging
api.interceptors.request.use(
  (config) => {
    config.metadata = { startTime: Date.now() }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor – surface structured errors and log in dev
api.interceptors.response.use(
  (response) => {
    if (import.meta.env?.DEV) {
      const duration = Date.now() - response.config.metadata?.startTime
      console.debug(`[API] ${response.config.method.toUpperCase()} ${response.config.url} - ${duration}ms`)
    }
    return response
  },
  (error) => {
    const errorInfo = {
      code: error.response?.data?.error?.code || 'NETWORK_ERROR',
      message: error.response?.data?.error?.message || error.message,
      status: error.response?.status || 0,
      url: error.config?.url
    }
    console.error(`[API Error] ${errorInfo.code}: ${errorInfo.message}`, {
      status: errorInfo.status,
      url: errorInfo.url
    })
    error.apiError = errorInfo
    return Promise.reject(error)
  }
)

// ─── Dashboard ───────────────────────────────────────────────────────────────
export const getDashboardStats = () => api.get('/dashboard/stats')

// ─── Devices ─────────────────────────────────────────────────────────────────
export const getDevices  = ()                      => api.get('/devices')
export const updateDevice = (id, data)             => api.put(`/devices/${id}`, data)
export const scanNetwork  = (type = 'arp')         => api.post('/devices/scan', { type })
export const scanPorts    = (deviceId, ports=null) => api.post(`/devices/${deviceId}/ports`, { ports })

// ─── Alerts ──────────────────────────────────────────────────────────────────
export const getAlerts = (limit = 50, unread = false) =>
  api.get('/alerts', { params: { limit, unread } })

// ─── WiFi (header status) ────────────────────────────────────────────────────
export const getWiFiNetworks  = () => api.get('/wifi/networks')
export const getConnectedWiFi = () => api.get('/wifi/connected')

// ─── WiFi Audit ──────────────────────────────────────────────────────────────
export const getWiFiAuditRequirements = () => api.get('/wifi-audit/requirements')
export const scanWiFiNetworks         = () => api.get('/wifi-audit/scan')

export const startHandshakeCapture = (bssid, channel, timeout = 300) =>
  api.post('/wifi-audit/capture/start', { bssid, channel, timeout })
export const stopHandshakeCapture  = () => api.post('/wifi-audit/capture/stop')
export const getCaptureStatus      = () => api.get('/wifi-audit/capture/status')

export const sendDeauthForCapture = (bssid, clientMac = 'ff:ff:ff:ff:ff:ff', count = 5) =>
  api.post('/wifi-audit/capture/deauth', { bssid, client_mac: clientMac, count })

export const getWordlists      = ()                                                => api.get('/wifi-audit/crack/wordlists')
export const downloadWordlist  = (name)                                            => api.post('/wifi-audit/crack/wordlists/download', { name })
export const startCrack        = (captureFile, wordlist, method='aircrack', bssid=null) =>
  api.post('/wifi-audit/crack/start', { capture_file: captureFile, wordlist, method, bssid })

export const startDeauth   = (targetMac, apMac, interval = 0.1) =>
  api.post('/wifi-audit/deauth/start', { target_mac: targetMac, ap_mac: apMac, interval })
export const stopDeauth    = (targetMac = null) => api.post('/wifi-audit/deauth/stop', { target_mac: targetMac })
export const getDeauthStatus = ()               => api.get('/wifi-audit/deauth/status')

export default api
