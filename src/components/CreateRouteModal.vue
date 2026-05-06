<template>
  <div v-if="isOpen" class="fixed inset-0 z-[100] flex flex-col justify-end">
    <!-- 背景遮罩 -->
    <div class="absolute inset-0 bg-black/40 transition-opacity" @click="close"></div>
    
    <!-- 模态框主体 -->
    <div class="relative bg-white w-full rounded-t-3xl overflow-hidden transform transition-transform duration-300">
      <div class="p-6 max-h-[82vh] overflow-y-auto hide-scrollbar">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-slate-800">新建行程</h2>
          <button @click="close" class="route-close-button w-10 h-10 m-0 p-0 bg-slate-50 border border-slate-100 rounded-full shadow-none text-slate-500 flex items-center justify-center leading-none">
            <Icon name="x" size="32rpx" />
          </button>
        </div>

        <div class="app-form-stack">
          <!-- 行程名称 -->
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">行程名称</label>
            <input 
              v-model="form.name" 
              type="text" 
              required
              placeholder-class="route-input-placeholder"
              placeholder="给这次摩旅起个响亮的名字" 
              class="route-input w-full h-10 bg-slate-50 border border-slate-200 rounded-xl px-4 py-0 text-sm leading-10 text-slate-700 focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
            >
          </div>

          <!-- 起点与终点 -->
          <div class="flex items-center space-x-2">
            <div class="flex-1 min-w-0">
              <div class="flex justify-between items-center mb-1">
                <label class="block text-xs font-medium text-slate-500">起点</label>
              </div>
              <input 
                v-model="form.origin" 
                type="text" 
                required
                placeholder-class="route-input-placeholder"
                placeholder="出发城市" 
                class="route-input w-full h-10 bg-slate-50 border border-slate-200 rounded-xl px-4 py-0 text-sm leading-10 text-slate-700 focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
              >
            </div>
            <Icon name="arrow-right" size="32rpx" class="shrink-0 mt-5" />
            <div class="flex-1 min-w-0">
              <label class="block text-xs font-medium text-slate-500 mb-1">终点</label>
              <input 
                v-model="form.destination" 
                type="text" 
                required
                placeholder-class="route-input-placeholder"
                placeholder="目的城市" 
                class="route-input w-full h-10 bg-slate-50 border border-slate-200 rounded-xl px-4 py-0 text-sm leading-10 text-slate-700 focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
              >
            </div>
          </div>

          <!-- 出发日期 -->
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">出发日期</label>
            <picker
              mode="date"
              :value="form.startDate || todayDate"
              :start="todayDate"
              :end="maxRouteDate"
              @change="onStartDateChange"
            >
              <view
                class="route-input w-full h-10 bg-slate-50 border border-slate-200 rounded-xl px-4 py-0 text-sm leading-10 flex items-center justify-between"
                :class="form.startDate ? 'text-slate-700' : 'text-slate-400'"
              >
                <text>{{ form.startDate || '请选择出发日期' }}</text>
                <Icon name="calendar" size="28rpx" class="shrink-0 ml-2" />
              </view>
            </picker>
          </div>

          <!-- 途经点 -->
          <div>
            <label class="block text-xs font-medium text-slate-500 mb-1">途经城市（选填，用逗号隔开）</label>
            <input 
              v-model="form.waypointsStr" 
              type="text" 
              placeholder-class="route-input-placeholder"
              placeholder="例如: 郑州,洛阳" 
              class="route-input w-full h-10 bg-slate-50 border border-slate-200 rounded-xl px-4 py-0 text-sm leading-10 text-slate-700 focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
            >
          </div>

          <button 
            type="button"
            @click="submitForm"
            :disabled="store.isLoading.value"
            class="route-submit-button w-[80%] mx-auto mt-4 bg-[#064e3b] text-white text-sm font-bold h-11 rounded-xl active:scale-[0.98] transition-transform disabled:opacity-50 flex justify-center items-center"
          >
            <span v-if="store.isLoading.value" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
            {{ store.isLoading.value ? '正在智能规划中...' : '开始筹备' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import Icon from '@/components/Icon.vue'
import { useRouteStore } from '@/composables/useRouteStore'
import { showError } from '@/utils/uni'

defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits(['close'])
const store = useRouteStore()

type PresetScheduleItem = {
  day?: number
  title?: string
  start_time?: string
  end_time?: string
  distance_km?: number
  description?: string
}

type CreateRouteForm = {
  name: string
  origin: string
  destination: string
  startDate: string
  waypointsStr: string
  ridingStyle: string
  schedule: PresetScheduleItem[]
}

const close = () => {
  emit('close')
}

const formatPickerDate = (value: Date) => {
  const year = value.getFullYear()
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const todayDate = formatPickerDate(new Date())
const maxRouteDate = formatPickerDate(new Date(new Date().getFullYear() + 3, 11, 31))

const onStartDateChange = (event: any) => {
  form.startDate = event?.detail?.value || ''
}

const isValidDateInput = (value: string) => {
  const text = value.trim()
  if (!/^\d{4}-\d{2}-\d{2}$/.test(text)) return false
  const parsed = new Date(`${text}T00:00:00`)
  if (Number.isNaN(parsed.getTime())) return false
  const [year, month, day] = text.split('-').map(Number)
  return (
    parsed.getFullYear() === year &&
    parsed.getMonth() + 1 === month &&
    parsed.getDate() === day
  )
}

const cloneSchedule = (schedule?: PresetScheduleItem[]) => {
  return Array.isArray(schedule)
    ? schedule.map((item, idx) => ({
        day: idx + 1,
        title: item.title || '',
        start_time: item.start_time || '09:00',
        end_time: item.end_time || '17:00',
        distance_km: Number(item.distance_km || 0),
        description: item.description || '',
      }))
    : []
}

const form = reactive<CreateRouteForm>({
  name: '',
  origin: '',
  destination: '',
  startDate: '',
  waypointsStr: '',
  ridingStyle: 'normal',
  schedule: []
})

// 监听 isOpen，当打开时如果外部没有传入预设值，则保留当前或重置
// 更好的做法是暴露一个方法供外部调用
const openWithPreset = (preset: Partial<CreateRouteForm>) => {
  Object.assign(form, {
    name: '',
    origin: '',
    destination: '',
    startDate: '',
    waypointsStr: '',
    ridingStyle: 'normal',
    ...preset,
    schedule: cloneSchedule(preset.schedule)
  })
}

defineExpose({
  openWithPreset
})

const submitForm = async () => {
  if (store.isLoading.value) return

  if (!form.name.trim()) {
    showError('请输入行程名称')
    return
  }

  if (!form.origin.trim()) {
    showError('请输入起点')
    return
  }

  if (!form.destination.trim()) {
    showError('请输入终点')
    return
  }

  if (!form.startDate.trim()) {
    showError('请输入出发日期')
    return
  }

  if (!isValidDateInput(form.startDate)) {
    showError('出发日期格式应为 YYYY-MM-DD')
    return
  }

  try {
    const wps = form.waypointsStr ? form.waypointsStr.split(/[,，]/).map(s => s.trim()).filter(Boolean) : []
    await store.addRouteAsync({
      name: form.name,
      origin: form.origin,
      destination: form.destination,
      startDate: form.startDate,
      waypoints: wps,
      ridingStyle: form.ridingStyle,
      schedule: cloneSchedule(form.schedule)
    })
    
    // 重置表单
    form.name = ''
    form.origin = ''
    form.destination = ''
    form.startDate = ''
    form.waypointsStr = ''
    form.ridingStyle = 'normal'
    form.schedule = []
    
    close()
  } catch (error: any) {
    showError(error.message || '创建行程失败，请检查网络或后端日志')
  }
}
</script>

<style>
.route-input {
  height: 80rpx;
  min-height: 80rpx;
  line-height: 80rpx;
  box-sizing: border-box;
}

.route-input-placeholder {
  color: #94a3b8;
  font-size: 28rpx;
  line-height: 80rpx;
}

.route-close-button {
  width: 80rpx;
  min-width: 80rpx;
  height: 80rpx;
  min-height: 80rpx;
  box-sizing: border-box;
}

.route-submit-button {
  height: 88rpx;
  min-height: 88rpx;
  line-height: 88rpx;
}
</style>
