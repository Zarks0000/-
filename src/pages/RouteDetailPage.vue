﻿<template>
  <div class="h-full bg-slate-50 relative flex flex-col">
    <header class="app-safe-header bg-gradient-to-br from-[#0f172a] to-[#064e3b] h-24 pt-10 px-4 flex items-center text-white sticky top-0 z-50 shrink-0">
      <button
        class="w-9 h-9 -ml-1 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 transition-colors"
        @click="goBack"
      >
        <Icon name="chevron-left" size="40rpx" class="brightness-0 invert" />
      </button>
      <div class="ml-2 flex-1 min-w-0">
        <div class="text-sm font-bold truncate">{{ title }}</div>
        <div class="text-[10px] text-white/70 truncate">{{ subtitle }}</div>
      </div>
      <button
        class="ml-2 w-9 h-9 rounded-full bg-white/10 hover:bg-white/20 transition-colors flex items-center justify-center"
        @click="deleteRoute"
      >
        <Icon name="trash-2" size="32rpx" class="brightness-0 invert" />
      </button>
      <button
        class="ml-2 px-3 h-9 rounded-full bg-white/10 hover:bg-white/20 transition-colors text-xs font-bold flex items-center justify-center shrink-0"
        @click="toggleEdit"
      >
        {{ isEditing ? '完成' : '编辑' }}
      </button>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8">
      <section class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100">
        <div class="flex items-center justify-between">
          <div class="min-w-0">
            <h2 class="text-lg font-bold text-slate-900 truncate">{{ title }}</h2>
            <div class="mt-1 text-xs text-slate-500">
              {{ dateRange }}
            </div>
          </div>
          <div class="text-right">
            <div class="text-xs text-slate-400">预计全程</div>
            <div class="text-sm font-bold text-emerald-700">{{ distanceText }}</div>
          </div>
        </div>
      </section>

      <section class="mt-4">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-bold text-slate-800">路线轨迹</h3>
          <div class="text-[10px] text-slate-400">{{ durationText }}</div>
        </div>

        <div v-if="mapError" class="bg-white rounded-2xl border border-slate-100 p-4 text-slate-400 text-xs flex items-center justify-center h-[240px]">
          暂无路线轨迹
        </div>
        <!-- #ifdef MP-WEIXIN -->
        <map
          v-else
          class="w-full h-[240px] rounded-2xl border border-slate-100 bg-slate-100 overflow-hidden relative z-10"
          :latitude="mpMapCenter.latitude"
          :longitude="mpMapCenter.longitude"
          :scale="mpMapScale"
          :polyline="mpMapPolylines"
          :include-points="mpIncludePoints"
          :show-location="false"
          :show-compass="false"
          :enable-zoom="true"
          :enable-scroll="true"
          :enable-rotate="false"
          :enable-overlooking="false"
        />
        <!-- #endif -->
        <!-- #ifndef MP-WEIXIN -->
        <div
          v-else
          id="route-map"
          class="w-full h-[240px] rounded-2xl border border-slate-100 bg-slate-100 overflow-hidden relative z-10"
        ></div>
        <!-- #endif -->
      </section>

      <section class="mt-6">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-bold text-slate-800">分日路书</h3>
          <div class="text-[10px] text-slate-400">共 {{ scheduleView.length }} 天</div>
        </div>

        <div class="space-y-3">
          <div
            v-for="item in scheduleView"
            :key="item.day"
            class="bg-white rounded-2xl shadow-sm border border-slate-100"
            :class="isEditing ? 'p-3' : 'p-4'"
          >
            <template v-if="isEditing">
              <div class="flex items-center gap-2">
                <div class="shrink-0 h-8 px-2 rounded-lg bg-emerald-50 text-[10px] font-bold text-emerald-700 flex items-center justify-center">
                  Day {{ item.day }}
                </div>
                <input
                  v-model="item.title"
                  type="text"
                  placeholder-class="app-input-placeholder-sm"
                  class="app-input-sm flex-1 min-w-0 text-xs font-bold text-slate-900 bg-slate-50 border border-slate-200 rounded-lg px-3 outline-none focus:border-emerald-600/60 focus:ring-2 focus:ring-emerald-500/10"
                  :placeholder="`第 ${item.day} 天标题`"
                />
                <button
                  class="app-icon-button w-8 h-8 rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200"
                  @click.prevent="removeDay(item.day)"
                >
                  <Icon name="trash-2" size="32rpx" />
                </button>
              </div>

              <div class="mt-2 grid grid-cols-3 gap-2">
                <div class="min-w-0">
                  <div class="text-[10px] text-slate-400 mb-1">开始</div>
                  <input
                    v-model="item.start_time"
                    type="text"
                    placeholder-class="app-input-placeholder-sm"
                    placeholder="09:00"
                    class="app-input-sm w-full bg-slate-50 border border-slate-200 rounded-lg px-2 text-xs outline-none focus:border-emerald-600/60 focus:ring-2 focus:ring-emerald-500/10"
                  />
                </div>
                <div class="min-w-0">
                  <div class="text-[10px] text-slate-400 mb-1">结束</div>
                  <input
                    v-model="item.end_time"
                    type="text"
                    placeholder-class="app-input-placeholder-sm"
                    placeholder="17:00"
                    class="app-input-sm w-full bg-slate-50 border border-slate-200 rounded-lg px-2 text-xs outline-none focus:border-emerald-600/60 focus:ring-2 focus:ring-emerald-500/10"
                  />
                </div>
                <div class="min-w-0">
                  <div class="text-[10px] text-slate-400 mb-1">里程</div>
                  <input
                    v-model.number="item.distance_km"
                    type="number"
                    min="0"
                    step="0.1"
                    placeholder-class="app-input-placeholder-sm"
                    placeholder="km"
                    class="app-input-sm w-full bg-orange-50 border border-orange-100 rounded-lg px-2 text-xs font-bold text-[#f97316] text-right outline-none focus:border-orange-400 focus:ring-2 focus:ring-orange-400/10"
                  />
                </div>
              </div>

              <textarea
                v-model="item.description"
                rows="2"
                placeholder-class="app-textarea-placeholder"
                class="route-edit-textarea mt-2 w-full text-xs text-slate-700 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 outline-none resize-none focus:border-emerald-600/60 focus:ring-2 focus:ring-emerald-500/10"
                placeholder="当天计划、补给点、注意事项…"
              ></textarea>
            </template>

            <template v-else>
              <div class="flex items-start justify-between">
                <div class="min-w-0 flex-1">
                  <div class="text-xs font-bold text-slate-900">
                  {{ item.title || `第 ${item.day} 天` }}
                  </div>

                  <div class="mt-2 flex items-center space-x-2 text-[11px] text-slate-500">
                    <span v-if="item.start_time || item.end_time" class="px-2 py-0.5 rounded-md bg-slate-50 border border-slate-100">
                      {{ (item.start_time || '—') + ' - ' + (item.end_time || '—') }}
                    </span>
                  </div>

                  <div class="mt-2 text-[11px] text-slate-500 leading-relaxed">
                    {{ item.description || '' }}
                  </div>
                </div>
                <div class="shrink-0 ml-3 text-right">
                  <div class="text-[10px] text-slate-400">预计</div>
                  <div class="text-xs font-bold text-[#f97316]">{{ distanceKmText(item.distance_km) }}</div>
                </div>
              </div>
            </template>
          </div>
        </div>

        <div v-if="isEditing" class="mt-4 flex items-center justify-between">
          <button
            class="app-action-button px-4 py-2 rounded-full bg-slate-100 text-slate-700 text-xs font-bold active:scale-95 transition-transform"
            @click="addDay"
          >
            添加一天
          </button>
          <button
            class="app-action-button px-4 py-2 rounded-full bg-[#064e3b] text-white text-xs font-bold shadow-md shadow-emerald-900/20 active:scale-95 transition-transform disabled:opacity-50"
            :disabled="isSaving"
            @click="saveSchedule"
          >
            {{ isSaving ? '保存中…' : '保存路书' }}
          </button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, nextTick, onUnmounted } from 'vue'
import { router } from '@/utils/router'
import { onLoad } from '@dcloudio/uni-app'
import Icon from '@/components/Icon.vue'
import { api } from '@/api'
import { confirmDialog, showError } from '@/utils/uni'

type ScheduleItem = {
  day: number
  title?: string
  start_time?: string
  end_time?: string
  distance_km?: number
  description?: string
}

type MapPoint = {
  latitude: number
  longitude: number
}


const route = { params: {} as any, query: {} as any };

onLoad((options) => {
  route.params = options || {};
  route.query = options || {};
})
const routeId = computed(() => String(route.params.id || ''))

const raw = ref<any>(null)
const mapError = ref(false)
const isEditing = ref(false)
const isSaving = ref(false)
const editable = ref<ScheduleItem[]>([])

const parseISO = (s: string | null | undefined) => {
  if (!s) return null
  const d = new Date(s)
  return Number.isNaN(d.getTime()) ? null : d
}

const formatDot = (d: Date) => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}.${m}.${day}`
}

const title = computed(() => raw.value?.route_name || '行程详情')
const subtitle = computed(() => {
  const o = raw.value?.origin_name || ''
  const dst = raw.value?.dest_name || ''
  if (!o && !dst) return ''
  return `${o} → ${dst}`
})

const meta = computed(() => {
  const wp = raw.value?.waypoints
  return typeof wp === 'object' && wp && !Array.isArray(wp) ? wp : null
})

const startDate = computed(() => parseISO(meta.value?.start_date))
const endDate = computed(() => parseISO(meta.value?.end_date))
const dateRange = computed(() => {
  if (!startDate.value) return ''
  const s = formatDot(startDate.value)
  if (!endDate.value || formatDot(endDate.value) === s) return s
  return `${s} - ${formatDot(endDate.value)}`
})

const totalDistanceKm = computed(() => {
  const m = raw.value?.total_distance
  if (!m || typeof m !== 'number') return 0
  return m / 1000
})

const distanceText = computed(() => {
  if (!totalDistanceKm.value) return '—'
  return `${totalDistanceKm.value.toFixed(1)} km`
})

const durationText = computed(() => {
  const s = raw.value?.total_duration
  if (!s || typeof s !== 'number') return ''
  const hours = s / 3600
  if (hours < 1) return `约 ${Math.max(1, Math.round(s / 60))} 分钟`
  return `约 ${hours.toFixed(1)} 小时`
})

const distanceKmText = (v: any) => {
  const n = typeof v === 'number' ? v : Number(v)
  if (!Number.isFinite(n) || n <= 0) return '—'
  return `${n.toFixed(1)} km`
}

const toEditableDistance = (v: any) => {
  const n = typeof v === 'number' ? v : Number(v)
  return Number.isFinite(n) && n >= 0 ? n : undefined
}

const schedule = computed<ScheduleItem[]>(() => {
  const s = meta.value?.schedule
  if (Array.isArray(s) && s.length) return s as ScheduleItem[]

  // 如果后端也没有 schedule 字段，才退化到下面这个默认的生成逻辑
  const d = totalDistanceKm.value
  if (!d) return []
  const daily = 300
  const days = Math.max(1, Math.round(d / daily))
  const out: ScheduleItem[] = []
  let remain = d
  for (let i = 1; i <= days; i++) {
    const dayDistance = Math.min(daily, remain)
    remain -= dayDistance
    out.push({
      day: i,
      title: `第 ${i} 天骑行`,
      start_time: '09:00',
      end_time: '17:00',
      distance_km: Number(dayDistance.toFixed(1)),
      description: `预计骑行 ${Number(dayDistance.toFixed(1))} 公里，建议每 1.5 小时休息一次。`,
    })
  }
  return out
})

const scheduleView = computed<ScheduleItem[]>(() => {
  return isEditing.value ? editable.value : schedule.value
})

const polylineStr = computed(() => {
  const candidate = meta.value?.polyline || raw.value?.polyline
  return typeof candidate === 'string' ? candidate.trim() : ''
})

const parseRoutePoints = (value: string): MapPoint[] => {
  if (!value) return []
  return value
    .split(';')
    .map((item) => {
      const [lng, lat] = item.split(',')
      return {
        latitude: Number(lat),
        longitude: Number(lng),
      }
    })
    .filter((item) => Number.isFinite(item.latitude) && Number.isFinite(item.longitude))
}

const routePoints = computed<MapPoint[]>(() => parseRoutePoints(polylineStr.value))

const mpIncludePoints = computed(() => routePoints.value)

const mpMapPolylines = computed(() => {
  if (routePoints.value.length < 2) return []
  return [
    {
      points: routePoints.value,
      color: '#059669',
      width: 6,
      borderColor: '#ffffff',
      borderWidth: 2,
    },
  ]
})

const mpMapCenter = computed<MapPoint>(() => {
  const first = routePoints.value[0]
  if (first) return first
  return {
    latitude: 39.9042,
    longitude: 116.4074,
  }
})

const mpMapScale = computed(() => {
  const count = routePoints.value.length
  if (count > 120) return 6
  if (count > 60) return 7
  if (count > 20) return 8
  if (count > 8) return 9
  return 11
})

const mapInstance = ref<any>(null)
const leafLetLib = ref<any>(null)

const initMap = async (polylineStr: string) => {
  if (!polylineStr) {
    mapError.value = true
    return
  }

  // 小程序端暂不直接挂载 Leaflet DOM 地图，避免运行时崩溃。
  // #ifndef H5
  mapError.value = true
  return
  // #endif

  const points = routePoints.value.map((point) => [point.latitude, point.longitude] as [number, number])

  if (points.length === 0) {
    mapError.value = true
    return
  }

  if (mapInstance.value) {
    mapInstance.value.remove()
  }

  const leafLetModule = leafLetLib.value || await import('leaflet')
  const L = leafLetModule.default || leafLetModule
  leafLetLib.value = L

  const map = L.map('route-map', {
    zoomControl: false,
    attributionControl: false
  })
  mapInstance.value = map

  L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
    maxZoom: 18,
    minZoom: 3,
    subdomains: ['1', '2', '3', '4'],
    attribution: '© AutoNavi'
  }).addTo(map)

  const polyline = L.polyline(points, { color: '#059669', weight: 4, opacity: 0.8 }).addTo(map)
  
  const startIcon = L.divIcon({
    html: `<div style="width:12px;height:12px;background:#10B981;border:2px solid white;border-radius:50%;box-shadow:0 0 4px rgba(0,0,0,0.3);"></div>`,
    className: '',
    iconSize: [12, 12],
    iconAnchor: [6, 6]
  })
  
  const endIcon = L.divIcon({
    html: `<div style="width:12px;height:12px;background:#EF4444;border:2px solid white;border-radius:50%;box-shadow:0 0 4px rgba(0,0,0,0.3);"></div>`,
    className: '',
    iconSize: [12, 12],
    iconAnchor: [6, 6]
  })

  L.marker(points[0], { icon: startIcon }).addTo(map)
  L.marker(points[points.length - 1], { icon: endIcon }).addTo(map)

  map.fitBounds(polyline.getBounds(), { padding: [20, 20] })
}

const goBack = () => {
  router.back()
}

const cloneSchedule = () => {
  const base = schedule.value
  editable.value = base.map(it => ({
    day: it.day,
    title: it.title || `第 ${it.day} 天骑行`,
    start_time: it.start_time || '09:00',
    end_time: it.end_time || '17:00',
    distance_km: toEditableDistance(it.distance_km),
    description: it.description || '',
  }))
}

const toggleEdit = () => {
  if (!isEditing.value) {
    cloneSchedule()
    isEditing.value = true
    return
  }
  isEditing.value = false
}

const addDay = () => {
  const next = (editable.value.length || 0) + 1
  editable.value.push({
    day: next,
    title: `第 ${next} 天骑行`,
    start_time: '09:00',
    end_time: '17:00',
    distance_km: undefined,
    description: '',
  })
}

const removeDay = (day: number) => {
  if (!isEditing.value) return
  const next = editable.value.filter(it => it.day !== day)
  if (next.length === 0) return
  editable.value = next.map((it, idx) => ({ ...it, day: idx + 1 }))
}

const saveSchedule = async () => {
  if (!routeId.value || isSaving.value) return
  isSaving.value = true
  try {
    const payload = editable.value.map((it, idx) => ({
      day: idx + 1,
      title: (it.title || '').trim() || `第 ${idx + 1} 天骑行`,
      start_time: it.start_time || null,
      end_time: it.end_time || null,
      distance_km: toEditableDistance(it.distance_km) ?? null,
      description: (it.description || '').trim() || null,
    }))
    await api.updateRouteSchedule(routeId.value, payload)
    const res = await api.getRoute(routeId.value)
    raw.value = res?.data || null
    isEditing.value = false
  } catch (error: any) {
    showError(error.message || '保存路书失败，请稍后重试')
    console.error('Failed to save schedule:', error)
  } finally {
    isSaving.value = false
  }
}

const deleteRoute = async () => {
  if (!routeId.value) return
  const ok = await confirmDialog('确定删除该行程吗？删除后不可恢复。')
  if (!ok) return
  await api.deleteRoute(routeId.value)
  router.replace('/route')
}

onMounted(async () => {
  if (!routeId.value) return
  const res = await api.getRoute(routeId.value)
  raw.value = res?.data || null

  mapError.value = routePoints.value.length < 2

  // #ifdef H5
  if (!mapError.value) {
    await nextTick()
    await initMap(polylineStr.value)
  }
  // #endif
})

onUnmounted(() => {
  if (mapInstance.value) {
    mapInstance.value.remove()
  }
})
</script>

<style scoped>
.route-edit-textarea {
  height: 112rpx;
  min-height: 112rpx;
  line-height: 36rpx;
  padding-top: 16rpx;
  padding-bottom: 16rpx;
  box-sizing: border-box;
}
</style>
