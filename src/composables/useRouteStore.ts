import { reactive, computed } from 'vue'
import { api } from '@/api'

export type RouteStatus = '筹备中' | '进行中' | '草稿' | '已完成'

export interface Route {
  id: string
  name: string
  origin: string
  destination: string
  startDate: string
  endDate: string
  status: RouteStatus
  progress: number
  daysLeft: number
  totalDistance?: number // 里程
  totalDuration?: number // 预计耗时(秒)
  schedule?: any[] // 后端返回的行程安排
  manualTodos?: ManualTodo[]
  routeReminders?: RouteReminder[]
}

export interface ManualTodo {
  id: string
  title: string
  done: boolean
}

export interface SuggestionTask {
  id: string
  title: string
  source: 'ai' | 'manual'
  done: boolean
}

export interface RouteReminder {
  id?: string
  type?: string
  severity?: 'high' | 'medium' | 'low'
  level?: 'high' | 'medium' | 'low'
  title: string
  description: string
  source?: string
}

const state = reactive({
  routes: [] as Route[],
  isLoading: false,
  currentAlerts: [] as any[],
  currentSuggestions: [] as any[],
  currentEquipment: [] as any[],
  currentManualTodos: [] as ManualTodo[],
  selectedHomeRouteId: null as string | null
})

const normalizeManualTodos = (raw: any): ManualTodo[] => {
  if (!Array.isArray(raw)) return []
  return raw
    .map((item, idx) => ({
      id: String(item?.id || `todo-${idx}`),
      title: String(item?.title || '').trim(),
      done: Boolean(item?.done),
    }))
    .filter(item => item.title)
}

const normalizeRouteReminders = (raw: any): RouteReminder[] => {
  if (!Array.isArray(raw)) return []
  return raw
    .map((item, idx) => {
      const severity = ['high', 'medium', 'low'].includes(item?.severity || item?.level)
        ? (item?.severity || item?.level)
        : 'medium'
      return {
        id: String(item?.id || `route-reminder-${idx}`),
        type: item?.type || 'route_ai',
        severity,
        level: severity,
        title: String(item?.title || '').trim(),
        description: String(item?.description || '').trim(),
        source: item?.source || 'AI出行提醒',
      } as RouteReminder
    })
    .filter(item => item.title && item.description)
}

const toRouteDateParam = (dateText?: string) => {
  if (!dateText || dateText === '—') return undefined
  const normalized = dateText.replace(/\./g, '-')
  return /^\d{4}-\d{2}-\d{2}$/.test(normalized) ? normalized : undefined
}

const routeWaypointNames = (route: Route) => {
  const genericTitle = /^(第\s*\d+\s*天骑行|Day\s*\d+)$/i
  const names = new Set<string>()
  ;(route.schedule || []).forEach((item: any) => {
    ;['city', 'location', 'start_location', 'end_location', 'from', 'to', 'destination', 'stop', 'stay'].forEach((key) => {
      const value = String(item?.[key] || '').trim()
      if (value && value !== route.origin && value !== route.destination) names.add(value)
    })
    const title = String(item?.title || '').trim()
    if (title && !genericTitle.test(title) && title.length <= 20) names.add(title)
  })
  return Array.from(names).slice(0, 6)
}

const buildWeatherReminders = (weatherRes: any, route: Route, dateParam?: string): RouteReminder[] => {
  const reminders: RouteReminder[] = []
  const weather = weatherRes?.weather

  if (weather?.type === 'forecast') {
    const temp = weather.tempMin && weather.tempMax ? `${weather.tempMin}-${weather.tempMax}℃` : ''
    const wind = [weather.windDir, weather.windScale ? `${weather.windScale}级` : ''].filter(Boolean).join('')
    const extras = [
      weather.precip ? `降水量 ${weather.precip}mm` : '',
      weather.vis ? `能见度 ${weather.vis}km` : '',
    ].filter(Boolean)
    reminders.push({
      id: `weather-${route.id}-${weather.date || dateParam || 'forecast'}`,
      type: 'weather',
      severity: 'low',
      level: 'low',
      title: `【天气】${route.destination}${weather.date ? ` ${weather.date}` : ''}`,
      description: [`预计${weather.text || '天气待确认'}`, temp, wind, ...extras].filter(Boolean).join('，'),
      source: '和风天气',
    })
  } else if (weather?.type === 'now') {
    const wind = [weather.windDir, weather.windScale ? `${weather.windScale}级` : ''].filter(Boolean).join('')
    reminders.push({
      id: `weather-${route.id}-now`,
      type: 'weather',
      severity: 'low',
      level: 'low',
      title: `【天气】${route.destination}当前天气`,
      description: [
        weather.text || '天气待确认',
        weather.temp ? `${weather.temp}℃` : '',
        weather.feelsLike ? `体感 ${weather.feelsLike}℃` : '',
        wind,
        weather.humidity ? `湿度 ${weather.humidity}%` : '',
      ].filter(Boolean).join('，'),
      source: '和风天气',
    })
  } else if (weatherRes?.message) {
    reminders.push({
      id: `weather-${route.id}-message`,
      type: 'weather',
      severity: 'low',
      level: 'low',
      title: `【天气】${route.destination}天气查询`,
      description: String(weatherRes.message),
      source: '和风天气',
    })
  }

  return reminders
}

const buildNewsReminders = (newsRes: any, route: Route): RouteReminder[] => {
  const newsAlerts = Array.isArray(newsRes?.alerts) ? newsRes.alerts : []
  if (newsAlerts.length > 0) return newsAlerts

  return [{
    id: `news-${route.id}-empty`,
    type: 'news',
    severity: 'low',
    level: 'low',
    title: '【新闻】沿途资讯',
    description: `暂未获取到与 ${route.origin} 到 ${route.destination} 相关的新闻提醒，出发前建议再次确认沿途交通、天气和临时管制信息。`,
    source: '新闻检索',
  }]
}

export function useRouteStore() {
  const routes = computed(() => state.routes)
  const isLoading = computed(() => state.isLoading)

  // 获取后端真实数据
  const fetchRoutes = async () => {
    try {
      state.isLoading = true
      const res = await api.getRoutes()
      if (res.status === 'success') {
        state.routes = res.data.map((r: any) => {
          const wp = r.waypoints && typeof r.waypoints === 'object' && !Array.isArray(r.waypoints) ? r.waypoints : null
          const startISO = wp?.start_date ? String(wp.start_date) : null
          const endISO = wp?.end_date ? String(wp.end_date) : null

          const parseISO = (s: string | null) => {
            if (!s) return null
            const d = new Date(s)
            return Number.isNaN(d.getTime()) ? null : d
          }

          const formatDate = (d: Date) => {
            const y = d.getFullYear()
            const m = String(d.getMonth() + 1).padStart(2, '0')
            const day = String(d.getDate()).padStart(2, '0')
            return `${y}.${m}.${day}`
          }

          const startD = parseISO(startISO)
          const endD = parseISO(endISO)
          const startDateText = startD ? formatDate(startD) : '—'
          const endDateText = endD ? formatDate(endD) : startDateText

          const today = new Date()
          today.setHours(0, 0, 0, 0)
          
          const startDTime = startD ? startD.getTime() : today.getTime()
          const endDTime = endD ? endD.getTime() : startDTime
          
          let status: RouteStatus = '筹备中'
          if (today.getTime() < startDTime) {
            status = '筹备中'
          } else if (today.getTime() > endDTime) {
            status = '已完成'
          } else {
            status = '进行中'
          }

          const daysLeft = startD ? Math.max(0, Math.ceil((startDTime - today.getTime()) / (1000 * 60 * 60 * 24))) : 0

          const todos = normalizeManualTodos(
            Array.isArray(wp?.manual_todos)
              ? wp.manual_todos
              : Array.isArray(r.manual_todos)
                ? r.manual_todos
                : []
          )
          const routeReminders = normalizeRouteReminders(wp?.route_reminders)
          const progress = todos.length > 0 ? Math.round((todos.filter((t: any) => t.done).length / todos.length) * 100) : 0

          return {
            id: r.id,
            name: r.route_name,
            origin: r.origin_name,
            destination: r.dest_name,
            startDate: startDateText,
            endDate: endDateText,
            status,
            progress,
            daysLeft,
            totalDistance: r.total_distance ? r.total_distance / 1000 : 0,
            totalDuration: r.total_duration || 0,
            schedule: wp?.schedule && Array.isArray(wp.schedule) ? wp.schedule : undefined,
            manualTodos: todos,
            routeReminders
          }
        })
        if (state.selectedHomeRouteId && !state.routes.some(r => r.id === state.selectedHomeRouteId)) {
          state.selectedHomeRouteId = null
        }

        const activeRoute = state.selectedHomeRouteId
          ? state.routes.find(r => r.id === state.selectedHomeRouteId)
          : state.routes.find(r => r.status === '进行中') || state.routes.find(r => r.status === '筹备中') || state.routes[0]
        state.currentManualTodos = activeRoute?.manualTodos || []
        state.currentAlerts = activeRoute?.routeReminders || []
      }
    } catch (e) {
      console.error('Failed to fetch routes:', e)
    } finally {
      state.isLoading = false
    }
  }

  // 获取当前主行程（第一个筹备中或进行中的行程）
  const defaultHomeRoute = computed(() => {
    return state.routes.find(r => r.status === '进行中') || state.routes.find(r => r.status === '筹备中') || state.routes[0] || null
  })

  const homeRouteCandidates = computed(() => state.routes)

  const mainRoute = computed(() => {
    if (state.selectedHomeRouteId) {
      const selected = state.routes.find(r => r.id === state.selectedHomeRouteId)
      if (selected) return selected
    }
    return defaultHomeRoute.value
  })

  const selectHomeRoute = (routeId: string) => {
    const route = state.routes.find(r => r.id === routeId)
    if (!route) return
    state.selectedHomeRouteId = route.id
    state.currentSuggestions = []
    state.currentEquipment = []
    state.currentAlerts = route.routeReminders || []
    state.currentManualTodos = route.manualTodos || []
  }

  // 获取其他行程
  const otherRoutes = computed(() => {
    if (!mainRoute.value) return []
    return state.routes.filter(r => r.id !== mainRoute.value?.id)
  })

  const fetchAlertsAndSuggestions = async (route: Route) => {
    if (!route) return

    // “建议完成”不依赖天气/禁摩/新闻接口，先同步展示后端已持久化的默认待办。
    const persistedReminders = route.routeReminders || []
    state.currentAlerts = persistedReminders
    state.currentManualTodos = route.manualTodos || []
    
    try {
      // 并行请求：天气预警、禁摩政策、智能建议
      // 安全解析月份，防止 startDate 为 '—' 时产生 NaN
      let month = new Date().getMonth() + 1
      if (route.startDate && route.startDate !== '—') {
        const parsed = new Date(route.startDate.replace(/\./g, '-'))
        if (!Number.isNaN(parsed.getTime())) {
          month = parsed.getMonth() + 1
        }
      }

      const dateParam = toRouteDateParam(route.startDate)
      const waypoints = routeWaypointNames(route)

      const [weatherRes, restrictionRes, newsRes, suggestionRes] = await Promise.all([
        api.getWeatherAlerts(route.destination, dateParam),
        api.getRestriction(route.destination),
        api.getNewsAlertsForRoute({ origin: route.origin, destination: route.destination, waypoints }, 6),
        api.getSuggestions(
          route.destination,
          route.daysLeft || 1,
          month,
          route.origin
        )
      ])

      const weatherReminders = buildWeatherReminders(weatherRes, route, dateParam)
      const newsReminders = buildNewsReminders(newsRes, route)

      state.currentAlerts = [
        ...weatherReminders,
        ...(weatherRes.alerts || []),
        ...(restrictionRes.data?.is_restricted ? [restrictionRes.data] : []),
        ...newsReminders,
        ...persistedReminders
      ]

      state.currentSuggestions = suggestionRes.data?.suggestions || []
      state.currentEquipment = suggestionRes.data?.equipment_list || []
      state.currentManualTodos = route.manualTodos || []
      
    } catch (e) {
      console.error('Failed to fetch alerts:', e)
    }
  }

  // 异步新增行程：先调用后端智能规划，再存入 Store
  const addRouteAsync = async (routeData: { name: string; origin: string; destination: string; startDate: string; waypoints?: string[]; ridingStyle?: string; schedule?: any[] }) => {
    state.isLoading = true
    try {
      // 1. 调用后端智能规划接口
      const wps = (routeData.waypoints || []).map(wp => ({
        name: wp,
        location: wp,
        stay_days: 1
      }))
      const res = await api.planRoute({
        name: routeData.name,
        origin: routeData.origin,
        destination: routeData.destination,
        start_date: routeData.startDate,
        waypoints: wps,
        riding_style: routeData.ridingStyle || 'leisure',
        schedule: routeData.schedule || []
      })
      
      const planData = res.data
      
      // 2. 计算日期间隔与结束日期
      const start = new Date(routeData.startDate)
      const end = new Date(start.getTime() + (planData.estimated_days - 1) * 24 * 60 * 60 * 1000)
      
      // 格式化日期 yyyy.mm.dd
      const formatDate = (d: Date) => {
        const y = d.getFullYear()
        const m = String(d.getMonth() + 1).padStart(2, '0')
        const day = String(d.getDate()).padStart(2, '0')
        return `${y}.${m}.${day}`
      }

      // 计算倒计时天数
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      const startDTime = start.getTime()
      const endDTime = end.getTime()
      
      let status: RouteStatus = '筹备中'
      if (today.getTime() < startDTime) {
        status = '筹备中'
      } else if (today.getTime() > endDTime) {
        status = '已完成'
      } else {
        status = '进行中'
      }
      
      const diffDays = Math.ceil((startDTime - today.getTime()) / (1000 * 60 * 60 * 24))

      const newRoute: Route = {
        id: planData.route_id,
        name: planData.name,
        origin: planData.origin,
        destination: planData.destination,
        startDate: formatDate(start),
        endDate: formatDate(end),
        status,
        progress: 0,
        daysLeft: diffDays > 0 ? diffDays : 0,
        totalDistance: planData.total_distance_km,
        schedule: planData.schedule, // 存入后端生成的每日日程
        manualTodos: normalizeManualTodos(planData.manual_todos),
        routeReminders: normalizeRouteReminders(planData.route_reminders)
      }
      
      // 插入到最前面
      state.routes.unshift(newRoute)
      state.selectedHomeRouteId = newRoute.id
      
      // 创建后，刷新预警与建议
      await fetchAlertsAndSuggestions(newRoute)
      
      return newRoute
      
    } catch (error: any) {
      console.error('Failed to plan route:', error)
      throw error
    } finally {
      state.isLoading = false
    }
  }

  return {
    routes,
    mainRoute,
    otherRoutes,
    homeRouteCandidates,
    isLoading,
    alerts: computed(() => state.currentAlerts),
    suggestions: computed(() => state.currentSuggestions),
    suggestionTasks: computed<SuggestionTask[]>(() => {
      // 现在的建议与提醒已经有专门的页面，这里的“建议完成”完全由持久化的 manualTodos 接管
      // 以便所有事项都可以被勾选、编辑、删除
      const sourceTodos = state.currentManualTodos.length > 0
        ? state.currentManualTodos
        : (mainRoute.value?.manualTodos || [])
      const manualTasks = sourceTodos.map((t) => ({
        ...t,
        source: 'manual' as const,
      }))
      return manualTasks
    }),
    equipment: computed(() => state.currentEquipment),
    fetchRoutes,
    addRouteAsync,
    fetchAlertsAndSuggestions,
    selectHomeRoute,
    async saveManualTodos(routeId: string, todos: ManualTodo[]) {
      await api.updateRouteManualTodos(routeId, todos)
      const target = state.routes.find(r => r.id === routeId)
      if (target) {
        target.manualTodos = todos
        target.progress = todos.length > 0 ? Math.round((todos.filter(t => t.done).length / todos.length) * 100) : 0
      }
      if (mainRoute.value?.id === routeId) {
        state.currentManualTodos = todos
      }
    },
    async deleteRoute(id: string) {
      await api.deleteRoute(id)
      state.routes = state.routes.filter(r => r.id !== id)
      if (state.selectedHomeRouteId === id) {
        state.selectedHomeRouteId = null
      }
    }
  }
}
