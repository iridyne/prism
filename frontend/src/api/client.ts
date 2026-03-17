import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export type RiskLevel = 'low' | 'medium' | 'high'

export interface PositionInput {
  code: string
  allocation: number
}

export interface PreferencesInput {
  risk_level: RiskLevel
  horizon_months: number
  target_return?: number
}

export interface Portfolio {
  id: string
  name: string
  positions: PositionInput[]
  preferences: PreferencesInput
  status: string
  created_at: string
}

export interface AnalysisResult {
  portfolio_id: string
  overall_score: number | null
  summary: string | null
  recommendations: string[]
  correlation_warnings: string[]
  backtest_metrics: Record<string, unknown>
  agent_insights: Array<Record<string, unknown>>
  created_at: string
}

export interface TaskStatus {
  task_id: string
  portfolio_id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  progress: number
  message: string
  timestamp: string
  error?: string | null
}

export const portfolioApi = {
  create: async (payload: {
    name: string
    positions: PositionInput[]
    preferences: PreferencesInput
  }): Promise<Portfolio> => {
    const { data } = await apiClient.post('/api/portfolios', payload)
    return data
  },

  list: async (): Promise<Portfolio[]> => {
    const { data } = await apiClient.get('/api/portfolios')
    return data
  },

  get: async (id: string): Promise<Portfolio> => {
    const { data } = await apiClient.get(`/api/portfolios/${id}`)
    return data
  },

  analyze: async (id: string): Promise<{ task_id: string; status: string }> => {
    const { data } = await apiClient.post(`/api/portfolios/${id}/analyze`)
    return data
  },

  getAnalysis: async (id: string): Promise<AnalysisResult> => {
    const { data } = await apiClient.get(`/api/portfolios/${id}/analysis`)
    return data
  },
}

export const taskApi = {
  get: async (taskId: string): Promise<TaskStatus> => {
    const { data } = await apiClient.get(`/api/tasks/${taskId}`)
    return data
  },
}

export const wsUrlForTask = (taskId: string): string => {
  const httpBase = API_BASE_URL.replace(/\/$/, '')
  const wsBase = httpBase.startsWith('https://')
    ? httpBase.replace('https://', 'wss://')
    : httpBase.replace('http://', 'ws://')
  return `${wsBase}/ws/tasks/${taskId}`
}
