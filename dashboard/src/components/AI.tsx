import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { aiService, anomalyService, ServiceHealth } from '../api'

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

export default function AI() {
  const [chatQuery, setChatQuery] = useState('')
  const [chatResponse, setChatResponse] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  
  const [incidentSummary, setIncidentSummary] = useState('')
  const [summaryLoading, setSummaryLoading] = useState(false)
  
  const [rca, setRCA] = useState('')
  const [rcaLoading, setRCALoading] = useState(false)
  
  const [servicesHealth, setServicesHealth] = useState<ServiceHealth[]>([])
  const [aiHealth, setAIHealth] = useState<{ status: string } | null>(null)

  useEffect(() => {
    fetchAIHealth()
    fetchServicesHealth()
  }, [])

  const fetchAIHealth = async () => {
    try {
      const health = await aiService.getHealth()
      setAIHealth(health)
    } catch (error) {
      console.error('AI service unavailable:', error)
      setAIHealth({ status: 'unavailable' })
    }
  }

  const fetchServicesHealth = async () => {
    try {
      const health = await anomalyService.getServicesHealth()
      setServicesHealth(health)
    } catch (error) {
      console.error('Error fetching services:', error)
    }
  }

  const handleChat = async () => {
    if (!chatQuery.trim()) return
    setChatLoading(true)
    setChatResponse('')
    try {
      const answer = await aiService.chat(chatQuery, {
        services: servicesHealth.map(s => s.service),
      })
      setChatResponse(answer)
    } catch (error) {
      setChatResponse('Error: AI service unavailable. Please ensure GROQ_API_KEY is set.')
      console.error('Chat error:', error)
    } finally {
      setChatLoading(false)
    }
  }

  const handleSummarize = async () => {
    setSummaryLoading(true)
    setIncidentSummary('')
    try {
      const summary = await aiService.summarizeIncident('1h')
      setIncidentSummary(summary)
    } catch (error) {
      setIncidentSummary('Error: AI service unavailable. Please ensure GROQ_API_KEY is set.')
      console.error('Summary error:', error)
    } finally {
      setSummaryLoading(false)
    }
  }

  const handleRCA = async () => {
    setRCALoading(true)
    setRCA('')
    try {
      const result = await aiService.getRCA('1h')
      setRCA(result)
    } catch (error) {
      setRCA('Error: AI service unavailable. Please ensure GROQ_API_KEY is set.')
      console.error('RCA error:', error)
    } finally {
      setRCALoading(false)
    }
  }

  const isAIAvailable = aiHealth?.status === 'healthy'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI-Powered Insights</h1>
          <p className="text-gray-600 mt-1">Intelligent analysis using LLM-driven observability</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className={`px-4 py-2 rounded-lg font-semibold ${
            isAIAvailable 
              ? 'bg-green-100 text-green-700 border-2 border-green-300'
              : 'bg-red-100 text-red-700 border-2 border-red-300'
          }`}>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isAIAvailable ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
              <span>{isAIAvailable ? 'AI Active' : 'AI Unavailable'}</span>
            </div>
          </div>
        </div>
      </div>

      {!isAIAvailable && (
        <div className="bg-yellow-50 border-2 border-yellow-300 rounded-xl p-6">
          <div className="flex items-start space-x-3">
            <svg className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <h3 className="font-semibold text-yellow-900 mb-2">AI Service Configuration Required</h3>
              <p className="text-sm text-yellow-800">
                Set the <code className="bg-yellow-100 px-2 py-1 rounded font-mono">GROQ_API_KEY</code> environment variable 
                to enable AI-powered features. See README for configuration instructions.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* AI Chat Assistant */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
        <div className="px-6 py-5 border-b bg-gradient-to-r from-purple-50 to-indigo-50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Reliability Assistant</h2>
              <p className="text-sm text-gray-600">Ask questions about your system in plain English</p>
            </div>
          </div>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Ask your SRE question:</label>
              <textarea
                value={chatQuery}
                onChange={(e) => setChatQuery(e.target.value)}
                placeholder="e.g., What's causing high latency in the orders service?"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-purple-500 focus:outline-none"
                rows={3}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.metaKey) handleChat()
                }}
              />
            </div>
            <Tooltip text="Query the AI assistant about your system health, metrics, or troubleshooting">
              <button
                onClick={handleChat}
                disabled={chatLoading || !isAIAvailable || !chatQuery.trim()}
                className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-semibold hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg transition-all"
              >
                <svg className={`w-5 h-5 ${chatLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>{chatLoading ? 'Asking AI...' : 'Ask AI Assistant'}</span>
              </button>
            </Tooltip>
            {chatResponse && (
              <div className="mt-4 p-4 bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg border-2 border-purple-200">
                <div className="flex items-start space-x-3">
                  <svg className="w-6 h-6 text-purple-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div className="flex-1">
                    <h4 className="font-semibold text-purple-900 mb-2">AI Response:</h4>
                    <div className="prose prose-sm max-w-none text-gray-800">
                      <ReactMarkdown>{chatResponse}</ReactMarkdown>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Analysis Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Incident Summary */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
          <div className="px-6 py-4 border-b bg-gradient-to-r from-blue-50 to-cyan-50">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Incident Summary</h3>
            </div>
          </div>
          <div className="p-6">
            <Tooltip text="Generate AI-powered incident summary from metrics, logs, and traces">
              <button
                onClick={handleSummarize}
                disabled={summaryLoading || !isAIAvailable}
                className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md transition-all"
              >
                <svg className={`w-5 h-5 ${summaryLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>{summaryLoading ? 'Analyzing...' : 'Generate Summary'}</span>
              </button>
            </Tooltip>
            {incidentSummary && (
              <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                <div className="prose prose-sm max-w-none text-gray-800">
                  <ReactMarkdown>{incidentSummary}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Root Cause Analysis */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
          <div className="px-6 py-4 border-b bg-gradient-to-r from-orange-50 to-red-50">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-orange-500 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900">Root Cause Analysis</h3>
            </div>
          </div>
          <div className="p-6">
            <Tooltip text="AI-powered root cause analysis from logs and metrics correlation">
              <button
                onClick={handleRCA}
                disabled={rcaLoading || !isAIAvailable}
                className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-md transition-all"
              >
                <svg className={`w-5 h-5 ${rcaLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                <span>{rcaLoading ? 'Analyzing...' : 'Run RCA'}</span>
              </button>
            </Tooltip>
            {rca && (
              <div className="mt-4 p-4 bg-orange-50 rounded-lg border border-orange-200">
                <div className="prose prose-sm max-w-none text-gray-800">
                  <ReactMarkdown>{rca}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Features Info */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-6 border-2 border-indigo-200">
        <div className="flex items-start space-x-4">
          <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-indigo-900 mb-3">AI-Powered Features</h3>
            <div className="grid md:grid-cols-2 gap-3 text-sm text-indigo-800">
              <div className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p><strong>Natural Language Queries:</strong> Ask questions about your system in plain English</p>
              </div>
              <div className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p><strong>Incident Summarization:</strong> Auto-generate incident reports from observability data</p>
              </div>
              <div className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p><strong>Root Cause Analysis:</strong> AI identifies likely failure subsystems from logs and metrics</p>
              </div>
              <div className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-indigo-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p><strong>Remediation Advice:</strong> LLM recommends best corrective actions with rationale</p>
              </div>
            </div>
            <div className="mt-4 p-3 bg-indigo-100 rounded-lg">
              <p className="text-xs text-indigo-900">
                <strong>Powered by:</strong> Groq API with <code className="bg-indigo-200 px-1 rounded">openai/gpt-oss-120b</code> model
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Example Queries */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Example Queries</h3>
        <div className="grid md:grid-cols-2 gap-3">
          {[
            "What's the current health of all services?",
            "Why is the orders service experiencing high latency?",
            "What anomalies were detected in the last hour?",
            "Should I restart the payments service?",
            "Explain the error rate spike in users service",
            "What's the predicted capacity for the next 24 hours?",
          ].map((example, idx) => (
            <button
              key={idx}
              onClick={() => setChatQuery(example)}
              className="text-left px-4 py-3 bg-gray-50 hover:bg-purple-50 rounded-lg border border-gray-200 hover:border-purple-300 text-sm text-gray-700 hover:text-purple-700 transition-all"
            >
              "{example}"
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

