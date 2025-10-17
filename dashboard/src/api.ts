import axios from 'axios'

const anomalyAPI = axios.create({
  baseURL: '/api/anomaly',
})

const policyAPI = axios.create({
  baseURL: '/api/policy',
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


