import api from './axios'

export interface BrandInfo {
  full_name: string
  short_names: string[]
}

export interface TaskCreateParams {
  brands: BrandInfo[]
  keywords: string[]
  platforms: string[]
  competitors?: BrandInfo[]
  task_type?: string
}

export interface Task {
  id: number
  task_type: string
  status: string
  brands: BrandInfo[]
  keywords: string[]
  platforms: string[]
  created_at: string
  started_at?: string
  completed_at?: string
}

export interface TaskStatus {
  task_id: number
  status: string
  progress: number
  message?: string
}

export function createTask(data: TaskCreateParams) {
  return api.post('/tasks', data)
}

export function getTask(taskId: number) {
  return api.get(`/tasks/${taskId}`)
}

export function getTaskStatus(taskId: number) {
  return api.get(`/tasks/${taskId}/status`)
}

export function getTaskResults(taskId: number) {
  return api.get(`/tasks/${taskId}/results`)
}

export function listTasks(skip = 0, limit = 20) {
  return api.get('/tasks', { params: { skip, limit } })
}
