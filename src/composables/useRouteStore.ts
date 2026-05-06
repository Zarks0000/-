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

      const [weatherRes, restrictionRes, newsRes, suggestionRes] = await Promise.all([
        api.getWeatherAlerts(route.destination),
        api.getRestriction(route.destination),
        api.getNewsAlertsForRoute({ origin: route.origin, destination: route.destination }, 6),
        api.getSuggestions(
          route.destination,
          route.daysLeft || 1,
          month,
          route.origin
        )
      ])

      state.currentAlerts = [
        ...persistedReminders,
        ...(weatherRes.alerts || []),
        ...(restrictionRes.data?.is_restricted ? [restrictionRes.data] : []),
        ...((newsRes && newsRes.alerts) || [])
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
      
      // 创建完成后立即返回，让创建弹窗先关闭；天气、禁摩、新闻和建议在后台加载。
      fetchAlertsAndSuggestions(newRoute).catch((error) => {
        console.error('Failed to fetch alerts after route creation:', error)
      })
      
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
