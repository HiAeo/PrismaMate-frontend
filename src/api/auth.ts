import api from './axios'

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserInfo {
  user_id: string
  email: string
  username: string
  created_at: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
}

export interface LoginRequest {
  email?: string
  username?: string
  password: string
}

/**
 * 用户注册
 */
export function register(email: string, username: string, password: string): Promise<LoginResponse> {
  return api.post('/auth/register', {
    email,
    username,
    password,
  })
}

/**
 * 用户登录
 */
export function login(email: string, password: string): Promise<LoginResponse>
export function login(username: string, password: string, isUsername: true): Promise<LoginResponse>
export function login(emailOrUsername: string, password: string, isUsername?: boolean): Promise<LoginResponse> {
  if (isUsername) {
    return api.post('/auth/login', {
      username: emailOrUsername,
      password,
    })
  }
  return api.post('/auth/login', {
    email: emailOrUsername,
    password,
  })
}

/**
 * 获取当前用户信息
 */
export function getMe(): Promise<UserInfo> {
  return api.get('/auth/me')
}

/**
 * 获取用户用量统计
 */
export function getUsage(): Promise<{
  total_tasks: number
  completed_tasks: number
  total_reports: number
  total_mentions: number
  total_detections: number
}> {
  return api.get('/user/usage')
}

/**
 * 退出登录
 */
export function logout() {
  localStorage.removeItem('token')
}
