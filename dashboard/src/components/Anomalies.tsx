import { useState, useEffect } from 'react'
import { anomalyService, Anomaly } from '../api'

// Tooltip Component
function Tooltip({ children, text }: { children: React.ReactNode; text: string }) {
  return (
    <div className="group relative inline-block">
      {children}
      <div className="invisible group-hover:visible absolute z-10 w-64 px-3 py-2 text-sm text-white bg-gray-900 rounded-lg shadow-lg -top-14 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
        {text}
        <div className="absolute w-2 h-2 bg-gray-900 transform rotate-45 left-1/2 -translate-x-1/2 top-full -mt-1"></div>
      </div>
    </div>
  )
}

export default function Anomalies() {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [allPredictions, setAllPredictions] = useState<Anomaly[]>([])
  const [showAll, setShowAll] = useState(false)
  const [loading, setLoading] = useState(true)
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [detecting, setDetecting] = useState(false)

  const fetchData = async () => {
    try {
      const [anomalyData, allData] = await Promise.all([
        anomalyService.getAnomalies(),
        anomalyService.getAllPredictions(),
      ])
      setAnomalies(anomalyData)
      setAllPredictions(allData)
    } catch (error) {
      console.error('Error fetching anomalies:', error)
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

  const manualDetection = async () => {
    try {
      setDetecting(true)
      await anomalyService.manualDetection()
      await fetchData()
    } catch (error) {
      console.error('Error triggering manual detection:', error)
    } finally {
      setDetecting(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'warning':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return (
          <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )
      case 'warning':
        return (
          <svg className="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )
      default:
        return (
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
    }
  }

  const displayData = showAll ? allPredictions : anomalies
  const normalPredictions = allPredictions.filter((p) => !p.anomaly).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Anomaly Detection</h1>
          <p className="text-gray-600 mt-1">Real-time anomaly detection and predictions</p>
        </div>
        <div className="flex space-x-3">
          <Tooltip text={showAll ? "Show only detected anomalies" : "Show all predictions including normal behavior"}>
            <button
              onClick={() => setShowAll(!showAll)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium shadow-md transition-all ${
                showAll
                  ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                  : 'bg-white border-2 border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              <span>{showAll ? 'Show Anomalies Only' : 'Show All Predictions'}</span>
            </button>
          </Tooltip>
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
          <Tooltip text="Manually trigger anomaly detection analysis now">
            <button
              onClick={manualDetection}
              disabled={detecting || loading}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md transition-all"
            >
              <svg className={`w-4 h-4 ${detecting ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span>{detecting ? 'Detecting...' : 'Detect Now'}</span>
            </button>
          </Tooltip>
        </div>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Tooltip text="Number of anomalies currently detected">
          <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-red-500 hover:shadow-xl transition">
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <p className="text-sm font-medium text-gray-600">Active Anomalies</p>
            </div>
            <p className="text-4xl font-bold text-red-600">{anomalies.length}</p>
          </div>
        </Tooltip>
        <Tooltip text="Total predictions made across all services">
          <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-blue-500 hover:shadow-xl transition">
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-sm font-medium text-gray-600">Total Predictions</p>
            </div>
            <p className="text-4xl font-bold text-blue-600">{allPredictions.length}</p>
          </div>
        </Tooltip>
        <Tooltip text="Predictions showing normal behavior">
          <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-green-500 hover:shadow-xl transition">
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <p className="text-sm font-medium text-gray-600">Normal</p>
            </div>
            <p className="text-4xl font-bold text-green-600">{normalPredictions}</p>
          </div>
        </Tooltip>
        <Tooltip text="Percentage of predictions that detected anomalies">
          <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-purple-500 hover:shadow-xl transition">
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                </svg>
              </div>
              <p className="text-sm font-medium text-gray-600">Detection Rate</p>
            </div>
            <p className="text-4xl font-bold text-gray-900">
              {allPredictions.length > 0
                ? `${((anomalies.length / allPredictions.length) * 100).toFixed(1)}%`
                : '0%'}
            </p>
          </div>
        </Tooltip>
      </div>

      {/* Anomalies List */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="px-6 py-5 border-b bg-gradient-to-r from-gray-50 to-white">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-gray-900">
                {showAll ? 'All Predictions' : 'Active Anomalies'}
              </h2>
            </div>
            <span className="text-sm text-gray-500">
              Showing {displayData.length} {displayData.length === 1 ? 'result' : 'results'}
            </span>
          </div>
        </div>
        <div className="divide-y">
          {loading ? (
            <div className="flex justify-center items-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : displayData.length === 0 ? (
            <div className="p-12 text-center">
              <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-gray-500 text-lg">
                {showAll ? 'No predictions available' : 'No anomalies detected'}
              </p>
              <p className="text-gray-400 text-sm mt-2">
                {showAll ? 'Run detection to generate predictions' : 'All services operating normally'}
              </p>
            </div>
          ) : (
            displayData.map((anomaly, index) => (
              <div key={index} className="p-6 hover:bg-gray-50 transition">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center flex-shrink-0">
                        <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                        </svg>
                      </div>
                      <div className="flex items-center space-x-3 flex-wrap">
                        <h3 className="text-xl font-bold text-gray-900 capitalize">
                          {anomaly.service}
                        </h3>
                        <span className="text-sm text-gray-400">•</span>
                        <span className="px-3 py-1 text-sm font-semibold text-purple-700 bg-purple-50 rounded-md capitalize">
                          {anomaly.metric.replace('_', ' ')}
                        </span>
                        {anomaly.anomaly && (
                          <>
                            <span className="text-sm text-gray-400">•</span>
                            <Tooltip text={`Severity level: ${anomaly.severity}`}>
                              <span className={`flex items-center space-x-1 px-3 py-1 text-xs font-bold rounded-full border-2 ${getSeverityColor(anomaly.severity)}`}>
                                {getSeverityIcon(anomaly.severity)}
                                <span>{anomaly.severity.toUpperCase()}</span>
                              </span>
                            </Tooltip>
                          </>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                      <Tooltip text="Current measured value for this metric">
                        <div className="bg-blue-50 p-3 rounded-lg">
                          <div className="flex items-center space-x-2 mb-1">
                            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                            </svg>
                            <p className="text-xs font-semibold text-blue-700">Current Value</p>
                          </div>
                          <p className="text-sm font-bold text-blue-900">
                            {anomaly.current_value.toFixed(3)}
                          </p>
                        </div>
                      </Tooltip>
                      
                      <Tooltip text="Expected normal range based on historical data">
                        <div className="bg-green-50 p-3 rounded-lg">
                          <div className="flex items-center space-x-2 mb-1">
                            <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                            </svg>
                            <p className="text-xs font-semibold text-green-700">Expected Range</p>
                          </div>
                          <p className="text-sm font-bold text-green-900">
                            {anomaly.expected_range.min.toFixed(2)} - {anomaly.expected_range.max.toFixed(2)}
                          </p>
                        </div>
                      </Tooltip>
                      
                      <Tooltip text="Confidence level of the anomaly detection">
                        <div className="bg-orange-50 p-3 rounded-lg">
                          <div className="flex items-center space-x-2 mb-1">
                            <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                            </svg>
                            <p className="text-xs font-semibold text-orange-700">Confidence</p>
                          </div>
                          <p className="text-sm font-bold text-orange-900">
                            {(anomaly.confidence * 100).toFixed(1)}%
                          </p>
                        </div>
                      </Tooltip>
                      
                      <Tooltip text="When this prediction was generated">
                        <div className="bg-purple-50 p-3 rounded-lg">
                          <div className="flex items-center space-x-2 mb-1">
                            <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <p className="text-xs font-semibold text-purple-700">Timestamp</p>
                          </div>
                          <p className="text-sm font-bold text-purple-900">
                            {new Date(anomaly.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </Tooltip>
                    </div>
                  </div>
                  <div className="ml-6 flex-shrink-0">
                    {anomaly.anomaly ? (
                      <div className="flex flex-col items-center justify-center w-24 h-24 bg-gradient-to-br from-red-100 to-red-200 rounded-xl border-2 border-red-300">
                        <svg className="w-10 h-10 text-red-600 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <span className="text-xs font-bold text-red-700">ANOMALY</span>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center w-24 h-24 bg-gradient-to-br from-green-100 to-green-200 rounded-xl border-2 border-green-300">
                        <svg className="w-10 h-10 text-green-600 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="text-xs font-bold text-green-700">NORMAL</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
