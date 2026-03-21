import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import ErrorBoundary, { SectionErrorBoundary } from './components/ErrorBoundary'
import Dashboard from './pages/Dashboard'
import Devices from './pages/Devices'
import DeviceControl from './pages/DeviceControl'
import Security from './pages/Security'
import Tools from './pages/Tools'
import Pranks from './pages/Pranks'
import WiFiAudit from './pages/WiFiAudit'
import Traffic from './pages/Traffic'
import TrafficMonitor from './pages/TrafficMonitor'
import WiFiHackerPage from './pages/WiFiHackerPage'
import Logs from './pages/Logs'
import Settings from './pages/Settings'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
          
          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            <Header toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
            
            <main className="flex-1 overflow-y-auto p-6">
              <SectionErrorBoundary fallbackMessage="Error al cargar la página">
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/devices" element={<Devices />} />
                  <Route path="/device-control" element={<DeviceControl />} />
                  <Route path="/security" element={<Security />} />
                  <Route path="/tools" element={<Tools />} />
                  <Route path="/pranks" element={<Pranks />} />
                  <Route path="/wifi-audit" element={<WiFiAudit />} />
                  <Route path="/wifi-hacker" element={<WiFiHackerPage />} />
                  <Route path="/traffic" element={<Traffic />} />
                  <Route path="/traffic-monitor" element={<TrafficMonitor />} />
                  <Route path="/logs" element={<Logs />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </SectionErrorBoundary>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
