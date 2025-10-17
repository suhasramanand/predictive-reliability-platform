import { useState, useEffect } from 'react'
import { anomalyService, policyService, ServiceHealth, PolicyStatus } from '../api'

// Tooltip Component
function Tooltip({ children, text }: { children: React.ReactNode; text: string }) {
  return (
    <div className="group relative inline-block">
      {children}
      <div className="invisible group-hover:visible absolute z-10 w-48 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg -top-12 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
        {text}
        <div className="absolute w-2 h-2 bg-gray-900 transform rotate-45 left-1/2 -translate-x-1/2 top-full -mt-1"></div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const [servicesHealth, setServicesHealth] = useState<ServiceHealth[]>([])
  const [policyStatus, setPolicyStatus] = useState<PolicyStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const fetchData = async () => {
    try {
      const [health, status] = await Promise.all([
        anomalyService.getServicesHealth(),
        policyService.getStatus(),
      ])
      setServicesHealth(health)
      setPolicyStatus(status)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()

    if (autoRefresh) {
      const interval = setInterval(fetchData, 10000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const toggleAutoRemediation = async () => {
    try {
      const enabled = await policyService.toggleAutoRemediation()
      setPolicyStatus(prev => prev ? { ...prev, auto_remediation_enabled: enabled } : null)
    } catch (error) {
      console.error('Error toggling auto-remediation:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'degraded':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Overview</h1>
          <p className="text-gray-600 mt-1">Real-time monitoring of all microservices</p>
        </div>
        <div className="flex space-x-3">
          <Tooltip text={autoRefresh ? "Disable automatic refresh every 10 seconds" : "Enable automatic refresh every 10 seconds"}>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium shadow-md transition-all ${
                autoRefresh
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {autoRefresh ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                )}
              </svg>
              <span>Auto-refresh: {autoRefresh ? 'ON' : 'OFF'}</span>
            </button>
          </Tooltip>
          <Tooltip text="Manually refresh all data now">
            <button
              onClick={fetchData}
              className="flex items-center space-x-2 px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 shadow-md transition-all"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Refresh</span>
            </button>
          </Tooltip>
        </div>
      </div>

      {/* Policy Status Card */}
      {policyStatus && (
        <div className="bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-lg p-6 border border-gray-200">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Auto-Remediation Status</h2>
                <p className="text-sm text-gray-600">Policy engine monitoring and enforcement</p>
              </div>
            </div>
            <Tooltip text={policyStatus.auto_remediation_enabled ? "Click to disable automatic remediation actions" : "Click to enable automatic remediation actions"}>
              <button
                onClick={toggleAutoRemediation}
                className={`flex items-center space-x-2 px-5 py-2.5 rounded-lg text-sm font-semibold shadow-lg transition-all ${
                  policyStatus.auto_remediation_enabled
                    ? 'bg-green-600 text-white hover:bg-green-700'
                    : 'bg-red-600 text-white hover:bg-red-700'
                }`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {policyStatus.auto_remediation_enabled ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  )}
                </svg>
                <span>{policyStatus.auto_remediation_enabled ? 'ENABLED' : 'DISABLED'}</span>
              </button>
            </Tooltip>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <Tooltip text="Total number of policy rules currently loaded">
              <div className="bg-white border-2 border-blue-200 rounded-lg p-4 hover:shadow-md transition">
                <div className="flex items-center space-x-2 mb-2">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="text-sm font-medium text-gray-600">Policies Loaded</p>
                </div>
                <p className="text-3xl font-bold text-gray-900">{policyStatus.policies_loaded}</p>
              </div>
            </Tooltip>
            <Tooltip text="Number of remediation actions executed by the policy engine">
              <div className="bg-white border-2 border-purple-200 rounded-lg p-4 hover:shadow-md transition">
                <div className="flex items-center space-x-2 mb-2">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <p className="text-sm font-medium text-gray-600">Actions Executed</p>
                </div>
                <p className="text-3xl font-bold text-gray-900">{policyStatus.actions_executed}</p>
              </div>
            </Tooltip>
            <Tooltip text="Timestamp of the last policy evaluation check">
              <div className="bg-white border-2 border-green-200 rounded-lg p-4 hover:shadow-md transition">
                <div className="flex items-center space-x-2 mb-2">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-sm font-medium text-gray-600">Last Check</p>
                </div>
                <p className="text-lg font-bold text-gray-900">
                  {policyStatus.last_check ? new Date(policyStatus.last_check).toLocaleTimeString() : 'N/A'}
                </p>
              </div>
            </Tooltip>
          </div>
        </div>
      )}

      {/* Services Health Grid */}
      <div>
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
            </svg>
          </div>
          <h2 className="text-2xl font-semibold text-gray-900">Services Health</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {servicesHealth.map((service) => (
            <div key={service.service} className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200 hover:shadow-xl transition-shadow">
              <div className={`px-5 py-4 border-b-4 ${getStatusColor(service.status)}`}>
                <div className="flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                    </svg>
                    <h3 className="text-lg font-bold capitalize">{service.service}</h3>
                  </div>
                  <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide">
                    {service.status}
                  </span>
                </div>
              </div>
              <div className="p-5">
                <div className="space-y-3">
                  {Object.entries(service.metrics).map(([metric, value]) => (
                    <div key={metric} className="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        <span className="text-sm font-medium text-gray-700 capitalize">
                          {metric.replace('_', ' ')}
                        </span>
                      </div>
                      <span className="text-sm font-bold text-gray-900">
                        {typeof value === 'number' ? value.toFixed(2) : value}
                        {metric.includes('cpu') ? '%' : metric.includes('rate') ? '%' : ''}
                      </span>
                    </div>
                  ))}
                  <div className="pt-3 border-t-2 border-gray-200">
                    <div className="flex justify-between items-center p-2 bg-gradient-to-r from-gray-50 to-white rounded-lg">
                      <div className="flex items-center space-x-2">
                        <svg className={`w-5 h-5 ${service.anomalies_detected > 0 ? 'text-red-600' : 'text-green-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          {service.anomalies_detected > 0 ? (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                          ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          )}
                        </svg>
                        <span className="text-sm font-semibold text-gray-700">Anomalies Detected</span>
                      </div>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-bold ${
                          service.anomalies_detected > 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                        }`}
                      >
                        {service.anomalies_detected}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Links */}
      <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl shadow-lg p-6 border border-indigo-200">
        <div className="flex items-center space-x-3 mb-5">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900">Observability Tools</h2>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Tooltip text="Open Grafana dashboards for metrics visualization">
            <a
              href="http://localhost:3001"
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center justify-center p-5 bg-white border-2 border-orange-300 rounded-xl hover:shadow-lg transition-all hover:scale-105"
            >
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-3">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <span className="text-sm font-bold text-gray-900">Grafana</span>
              <span className="text-xs text-gray-500 mt-1">Dashboards</span>
            </a>
          </Tooltip>
          <Tooltip text="Open Prometheus metrics explorer">
            <a
              href="http://localhost:9090"
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center justify-center p-5 bg-white border-2 border-red-300 rounded-xl hover:shadow-lg transition-all hover:scale-105"
            >
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-3">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
              </div>
              <span className="text-sm font-bold text-gray-900">Prometheus</span>
              <span className="text-xs text-gray-500 mt-1">Metrics</span>
            </a>
          </Tooltip>
          <Tooltip text="Open Jaeger distributed tracing UI">
            <a
              href="http://localhost:16686"
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center justify-center p-5 bg-white border-2 border-blue-300 rounded-xl hover:shadow-lg transition-all hover:scale-105"
            >
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <span className="text-sm font-bold text-gray-900">Jaeger</span>
              <span className="text-xs text-gray-500 mt-1">Tracing</span>
            </a>
          </Tooltip>
          <Tooltip text="Open Anomaly Detection API documentation">
            <a
              href="http://localhost:8080/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-col items-center justify-center p-5 bg-white border-2 border-purple-300 rounded-xl hover:shadow-lg transition-all hover:scale-105"
            >
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-3">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </div>
              <span className="text-sm font-bold text-gray-900">API Docs</span>
              <span className="text-xs text-gray-500 mt-1">Swagger</span>
            </a>
          </Tooltip>
        </div>
      </div>
    </div>
  )
}


