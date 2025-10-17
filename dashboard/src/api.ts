import axios from 'axios'

const anomalyAPI = axios.create({
  baseURL: '/api/anomaly',
})

const policyAPI = axios.create({
  baseURL: '/api/policy',
})

const aiAPI = axios.create({
  baseURL: '/api/ai',
})

export interface Anomaly {
  service: string
  metric: string
  current_value: number
  expected_range: {
    min: number
    max: number
    mean: number
  }
  anomaly: boolean
  confidence: number
  timestamp: string
  severity: string
}

export interface ServiceHealth {
  service: string
  status: string
  metrics: Record<string, number>
  anomalies_detected: number
}

export interface RemediationAction {
  action_id: string
  policy_name: string
  service: string
  action: string
  reason: string
  status: string
  timestamp: string
  details?: string
}

export interface Policy {
  name: string
  condition: string
  action: string
  service: string
  cooldown: number
  enabled: boolean
}

export interface PolicyStatus {
  auto_remediation_enabled: boolean
  policies_loaded: number
  actions_executed: number
  last_check?: string
}

export const anomalyService = {
  getAnomalies: async (): Promise<Anomaly[]> => {
    const response = await anomalyAPI.get('/predict')
    return response.data.anomalies || []
  },

  getAllPredictions: async (): Promise<Anomaly[]> => {
    const response = await anomalyAPI.get('/predictions/all')
    return response.data.predictions || []
  },

  getServicesHealth: async (): Promise<ServiceHealth[]> => {
    const response = await anomalyAPI.get('/services/health')
    return response.data.services || []
  },

  manualDetection: async (): Promise<Anomaly[]> => {
    const response = await anomalyAPI.post('/detect/manual')
    return response.data.anomalies || []
  },
}

export const policyService = {
  getStatus: async (): Promise<PolicyStatus> => {
    const response = await policyAPI.get('/status')
    return response.data
  },

  getPolicies: async (): Promise<Policy[]> => {
    const response = await policyAPI.get('/policies')
    return response.data.policies || []
  },

  getActions: async (): Promise<RemediationAction[]> => {
    const response = await policyAPI.get('/actions')
    return response.data.actions || []
  },

  getRecentActions: async (limit: number = 10): Promise<RemediationAction[]> => {
    const response = await policyAPI.get(`/actions/recent?limit=${limit}`)
    return response.data.actions || []
  },

  manualEvaluation: async (): Promise<RemediationAction[]> => {
    const response = await policyAPI.post('/evaluate')
    return response.data.actions || []
  },

  toggleAutoRemediation: async (): Promise<boolean> => {
    const response = await policyAPI.post('/toggle')
    return response.data.auto_remediation_enabled
  },
}

export interface ChatRequest {
  query: string
  context?: Record<string, any>
}

export interface ChatResponse {
  answer: string
}

export interface IncidentSummary {
  summary: string
}

export interface RCAResponse {
  rca: string
}

export interface AdviceRequest {
  service: string
  anomaly: string
  context?: Record<string, any>
}

export interface AdviceResponse {
  advice: string
}

export const aiService = {
  chat: async (query: string, context?: Record<string, any>): Promise<string> => {
    const response = await aiAPI.post('/chat', { query, context })
    return response.data.answer
  },

  summarizeIncident: async (timeRange: string = '1h', services?: string[]): Promise<string> => {
    const response = await aiAPI.post('/summarize', { time_range: timeRange, services })
    return response.data.summary
  },

  getRCA: async (timeRange: string = '1h', services?: string[]): Promise<string> => {
    const response = await aiAPI.post('/rca', { time_range: timeRange, services })
    return response.data.rca
  },

  getAdvice: async (service: string, anomaly: string, context?: Record<string, any>): Promise<string> => {
    const response = await aiAPI.post('/advice', { service, anomaly, context })
    return response.data.advice
  },

  getHealth: async (): Promise<{ status: string; service: string }> => {
    const response = await aiAPI.get('/health')
    return response.data
  },
}


