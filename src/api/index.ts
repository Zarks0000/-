import { redirectToAuthPage } from '@/utils/authRedirect'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'
const WX_CLOUD_ENV_ID = import.meta.env.VITE_WX_CLOUD_ENV_ID || ''
const WX_CLOUD_CONTAINER_SERVICE = import.meta.env.VITE_WX_CLOUD_CONTAINER_SERVICE || ''

let wxCloudInitialized = false

function getWxCloud() {
  const wxRuntime = (globalThis as any).wx
  return wxRuntime?.cloud
}

export function initWxCloud() {
  if (wxCloudInitialized) return

  const wxCloud = getWxCloud()
  if (!WX_CLOUD_ENV_ID || !wxCloud?.init) return

  wxCloud.init({
    env: WX_CLOUD_ENV_ID,
    traceUser: true,
  })
  wxCloudInitialized = true
}

function shouldUseWxCloudContainer() {
  return Boolean(WX_CLOUD_ENV_ID && WX_CLOUD_CONTAINER_SERVICE && getWxCloud()?.callContainer)
}

function getCloudContainerPath(url: string) {
  const match = url.match(/^https?:\/\/[^/]+(\/.*)?$/)
  if (match) return match[1] || '/'
  return url.startsWith('/') ? url : `/${url}`
}

function normalizeRequestBody(body: any) {
  if (typeof body !== 'string') return body
  try {
    return JSON.parse(body)
  } catch {
    return body
  }
}

function redirectToAuthWhenUnauthorized(data: any) {
  const message = data?.message || data?.detail
  if (message !== '未登录') return

  uni.removeStorageSync('vibe_auth_token')
  uni.removeStorageSync('vibe_user_id')
  uni.removeStorageSync('vibe_user_profile')

  redirectToAuthPage()
}

function createFetchResponse(statusCode: number, data: any) {
  let safeData = data
  if (safeData && typeof safeData === 'object') {
    safeData = JSON.parse(JSON.stringify(safeData))
  }
  redirectToAuthWhenUnauthorized(safeData)

  return {
    ok: statusCode >= 200 && statusCode < 300,
    status: statusCode,
    statusText: String(statusCode),
    json: async () => safeData,
  }
}

async function cloudContainerFetch(url: string, options: any = {}): Promise<any> {
  initWxCloud()

  const wxCloud = getWxCloud()
  if (!wxCloud?.callContainer) {
    throw new Error('当前环境不支持微信云托管调用')
  }

  return new Promise((resolve, reject) => {
    wxCloud.callContainer({
      config: {
        env: WX_CLOUD_ENV_ID,
      },
      path: getCloudContainerPath(url),
      method: (options.method || 'GET').toUpperCase(),
      timeout: 15000,
      header: {
        ...(options.headers || {}),
        'X-WX-SERVICE': WX_CLOUD_CONTAINER_SERVICE,
      },
      data: normalizeRequestBody(options.body),
      success: (res: any) => {
        resolve(createFetchResponse(res.statusCode || 200, res.data))
      },
      fail: (err: any) => {
        const message = err?.errMsg || err?.message || '微信云托管请求失败'
        reject(new Error(message))
      },
    })
  })
}

async function httpFetch(url: string, options: any = {}): Promise<any> {
  return new Promise((resolve, reject) => {
    uni.request({
      url,
      method: (options.method || 'GET').toUpperCase() as any,
      header: options.headers || {},
      data: normalizeRequestBody(options.body),
      success: (res) => {
        resolve(createFetchResponse(res.statusCode, res.data))
      },
      fail: (err) => {
        const detail = err as any
        const message = detail?.errMsg || detail?.message || '网络请求失败，请确认后端服务已启动'
        reject(new Error(message))
      }
    })
  })
}

// Mock fetch API using uni.request locally and wx.cloud.callContainer in WeChat CloudBase.
async function fetch(url: string, options: any = {}): Promise<any> {
  if (shouldUseWxCloudContainer()) {
    return cloudContainerFetch(url, options)
  }
  return httpFetch(url, options)
}

async function readErrorMessage(response: any, fallback: string) {
  try {
    const data = await response.json()
    return data?.detail || data?.message || fallback
  } catch {
    return fallback
  }
}

function buildQuery(params: Record<string, unknown>) {
  return Object.keys(params)
    .filter((key) => {
      const value = params[key]
      return value !== undefined && value !== null && String(value) !== ''
    })
    .map((key) => `${encodeURIComponent(key)}=${encodeURIComponent(String(params[key]))}`)
    .join('&')
}

function getAuthToken(): string {
  return uni.getStorageSync('vibe_auth_token') || ''
}

function buildAuthHeaders(extra: Record<string, string> = {}) {
  const token = getAuthToken()
  return token
    ? { ...extra, Authorization: `Bearer ${token}` }
    : extra
}

export const api = {
  // 获取所有已保存的路线
  async getRoutes() {
    const ts = new Date().getTime()
    const response = await fetch(`${API_BASE_URL}/routes?_t=${ts}`, {
      headers: buildAuthHeaders({
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      })
    })
    return response.json()
  },

  async getRoute(routeId: string) {
    const ts = new Date().getTime()
    const response = await fetch(`${API_BASE_URL}/routes/${routeId}?_t=${ts}`, {
      headers: buildAuthHeaders({
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      })
    })
    return response.json()
  },

  async updateRouteSchedule(routeId: string, schedule: any[]) {
    const ts = new Date().getTime()
    const response = await fetch(`${API_BASE_URL}/routes/${routeId}/schedule?_t=${ts}`, {
      method: 'PUT',
      headers: buildAuthHeaders({
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }),
      body: JSON.stringify({ schedule }),
    })
    if (!response.ok) {
      throw new Error(`保存失败: ${response.status} ${response.statusText}`)
    }
    const data = await response.json()
    if (data.status === 'error') {
      throw new Error(data.message || '保存失败')
    }
    return data
  },

  async updateRouteManualTodos(routeId: string, todos: any[]) {
    const ts = new Date().getTime()
    const response = await fetch(`${API_BASE_URL}/routes/${routeId}/manual-todos?_t=${ts}`, {
      method: 'PUT',
      headers: buildAuthHeaders({
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }),
      body: JSON.stringify({ manual_todos: todos }),
    })
    return response.json()
  },

  // 删除路线
  async deleteRoute(routeId: string) {
    const ts = new Date().getTime()
    const response = await fetch(`${API_BASE_URL}/routes/${routeId}?_t=${ts}`, {
      method: 'DELETE',
      headers: buildAuthHeaders({
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      })
    })
    return response.json()
  },

  // 路线规划 API
  async planRoute(payload: { name: string; origin: string; destination: string; start_date: string; waypoints?: any[]; riding_style?: string; schedule?: any[] }) {
    const response = await fetch(`${API_BASE_URL}/routes/plan`, {
      method: 'POST',
      headers: buildAuthHeaders({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify(payload),
    })
    if (!response.ok) {
      const message = await readErrorMessage(response, `创建失败: ${response.status} ${response.statusText}`)
      throw new Error(message)
    }
    const result = await response.json()
    if (result?.status === 'error') {
      throw new Error(result.message || '创建失败')
    }
    return result
  },

  // 获取智能建议 API
  async getSuggestions(destination: string, days: number, month: number, origin?: string) {
    const params = buildQuery({
      destination,
      days,
      month,
      origin,
    })

    const response = await fetch(`${API_BASE_URL}/suggestions?${params}`)
    return response.json()
  },

  // 获取天气预警 API
  async getWeatherAlerts(location: string, date?: string) {
    const params = [`location=${encodeURIComponent(location)}`]
    if (date) params.push(`date=${encodeURIComponent(date)}`)
    const response = await fetch(`${API_BASE_URL}/weather/alerts?${params.join('&')}`)
    return response.json()
  },

  // 获取禁摩情况 API
  async getRestriction(city: string) {
    const response = await fetch(
      `${API_BASE_URL}/restriction/city?city=${encodeURIComponent(city)}`
    )
    return response.json()
  },

  async getNewsAlertsForRoute(data: { origin: string; destination: string; waypoints?: string[] }, count = 6) {
    const params = buildQuery({
      origin: data.origin,
      destination: data.destination,
      count,
      waypoints: data.waypoints && data.waypoints.length ? data.waypoints.join(',') : undefined,
    })
    const response = await fetch(`${API_BASE_URL}/news/route-alerts?${params}`)
    return response.json()
  },

  // --- 实用工具 API ---
  async calculateEquipment(items: string[]) {
    const response = await fetch(`${API_BASE_URL}/tools/equipment-calc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ items }),
    })
    if (!response.ok) throw new Error('计算失败')
    return response.json()
  },

  async estimateBudget(
    origin: string,
    destination: string,
    days: number,
    via_cities = '',
    notes = ''
  ) {
    const response = await fetch(`${API_BASE_URL}/tools/budget-estimate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ origin, destination, days, via_cities, notes }),
    })
    const data = await response.json()
    if (!response.ok || data.status === 'error') {
      throw new Error(data.message || '估算失败')
    }
    return data
  },

  async wxLogin(code: string, nickname?: string) {
    const response = await fetch(`${API_BASE_URL}/auth/wx-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, nickname }),
    })
    return response.json()
  },

  async submitFeedback(payload: { content: string; contact?: string; page?: string }) {
    const response = await fetch(`${API_BASE_URL}/feedback`, {
      method: 'POST',
      headers: buildAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(payload),
    })
    return response.json()
  },

  async getMyProfile() {
    const response = await fetch(`${API_BASE_URL}/me/profile`, {
      headers: buildAuthHeaders(),
    })
    return response.json()
  },

  async getMyVehicles() {
    const response = await fetch(`${API_BASE_URL}/me/vehicles`, {
      headers: buildAuthHeaders(),
    })
    return response.json()
  },

  async saveMyVehicles(items: any[]) {
    const response = await fetch(`${API_BASE_URL}/me/vehicles`, {
      method: 'PUT',
      headers: buildAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ items }),
    })
    return response.json()
  },

  async getMyEquipments() {
    const response = await fetch(`${API_BASE_URL}/me/equipments`, {
      headers: buildAuthHeaders(),
    })
    return response.json()
  },

  async saveMyEquipments(items: any[]) {
    const response = await fetch(`${API_BASE_URL}/me/equipments`, {
      method: 'PUT',
      headers: buildAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ items }),
    })
    return response.json()
  },

  async getMyTemplates() {
    const response = await fetch(`${API_BASE_URL}/me/templates`, {
      headers: buildAuthHeaders(),
    })
    return response.json()
  },

  async saveMyTemplates(items: any[]) {
    const response = await fetch(`${API_BASE_URL}/me/templates`, {
      method: 'PUT',
      headers: buildAuthHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ items }),
    })
    return response.json()
  },

  async getMyHistory() {
    const response = await fetch(`${API_BASE_URL}/me/history`, {
      headers: buildAuthHeaders(),
    })
    return response.json()
  }
}
