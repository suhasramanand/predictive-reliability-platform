import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Home from './components/Home'
import Dashboard from './components/Dashboard'
import Anomalies from './components/Anomalies'
import Actions from './components/Actions'
import Policies from './components/Policies'
import AI from './components/AI'

// Custom Cursor Component
function CustomCursor() {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [dotPosition, setDotPosition] = useState({ x: 0, y: 0 })
  const [clicking, setClicking] = useState(false)
  const [clickEffect, setClickEffect] = useState<{ x: number; y: number; id: number }[]>([])
  const [scanWaves, setScanWaves] = useState<{ x: number; y: number; id: number }[]>([])

  useEffect(() => {
    const updatePosition = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY })
      // Dot follows with slight delay
      setTimeout(() => {
        setDotPosition({ x: e.clientX, y: e.clientY })
      }, 50)
    }

    const handleMouseDown = (e: MouseEvent) => {
      setClicking(true)
      const id = Date.now()
      // Add radar scan effect
      setClickEffect(prev => [...prev, { x: e.clientX, y: e.clientY, id }])
      setTimeout(() => {
        setClickEffect(prev => prev.filter(effect => effect.id !== id))
      }, 800)
      
      // Add scan wave effect
      const waveId = Date.now() + 1
      setScanWaves(prev => [...prev, { x: e.clientX, y: e.clientY, id: waveId }])
      setTimeout(() => {
        setScanWaves(prev => prev.filter(wave => wave.id !== waveId))
      }, 1000)
    }

    const handleMouseUp = () => {
      setClicking(false)
    }

    window.addEventListener('mousemove', updatePosition)
    window.addEventListener('mousedown', handleMouseDown)
    window.addEventListener('mouseup', handleMouseUp)

    return () => {
      window.removeEventListener('mousemove', updatePosition)
      window.removeEventListener('mousedown', handleMouseDown)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [])

  return (
    <>
      {/* Crosshair reticle */}
      <div
        className="custom-cursor"
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
          transform: `translate(-50%, -50%) scale(${clicking ? 0.8 : 1})`,
        }}
      />
      {/* Scanning ring */}
      <div
        className="custom-cursor-ring"
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
          transform: `translate(-50%, -50%) scale(${clicking ? 0.7 : 1})`,
        }}
      />
      {/* Center monitoring dot with heartbeat */}
      <div
        className="custom-cursor-dot"
        style={{
          left: `${dotPosition.x}px`,
          top: `${dotPosition.y}px`,
        }}
      />
      {/* Radar scan effects on click */}
      {clickEffect.map(effect => (
        <div
          key={effect.id}
          className="cursor-click-effect"
          style={{
            left: `${effect.x}px`,
            top: `${effect.y}px`,
          }}
        />
      ))}
      {/* Scan wave effects */}
      {scanWaves.map(wave => (
        <div
          key={wave.id}
          className="cursor-scan-wave"
          style={{
            left: `${wave.x}px`,
            top: `${wave.y}px`,
          }}
        />
      ))}
    </>
  )
}

function Navigation() {
  const location = useLocation()
  
  const isActive = (path: string) => {
    return location.pathname === path
  }
  
  const navLinkClass = (path: string) => {
    return `px-4 py-2 rounded-lg text-sm font-medium transition-all ${
      isActive(path)
        ? 'bg-blue-600 text-white shadow-lg'
        : 'text-gray-700 hover:bg-gray-100'
    }`
  }

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-3 px-3 py-2 text-gray-800 hover:text-blue-600 transition">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <span className="font-bold text-xl bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Predictive Reliability Platform
              </span>
            </Link>
          </div>
          <div className="flex space-x-2 items-center">
            <Link to="/" className={navLinkClass('/')}>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                <span>Home</span>
              </div>
            </Link>
            <Link to="/dashboard" className={navLinkClass('/dashboard')}>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span>Dashboard</span>
              </div>
            </Link>
            <Link to="/anomalies" className={navLinkClass('/anomalies')}>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>Anomalies</span>
              </div>
            </Link>
            <Link to="/actions" className={navLinkClass('/actions')}>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>Actions</span>
              </div>
            </Link>
            <Link to="/policies" className={navLinkClass('/policies')}>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
                <span>Policies</span>
              </div>
            </Link>
            <Link to="/ai" className={navLinkClass('/ai')}>
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                <span>AI</span>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
        <CustomCursor />
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/anomalies" element={<Anomalies />} />
            <Route path="/actions" element={<Actions />} />
            <Route path="/policies" element={<Policies />} />
            <Route path="/ai" element={<AI />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

