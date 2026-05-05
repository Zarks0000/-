﻿<template>
  <div class="h-full app-page relative flex flex-col">
    <!-- 1. 顶部状态栏 & 导航 -->
    <header class="app-safe-header app-hero-header h-24 pt-10 px-4 flex items-center text-white sticky top-0 z-50 shrink-0">
      <div class="flex items-center">
        <button v-if="canGoBack" @click="router.back()" class="w-8 h-8 flex items-center justify-center bg-white/10 rounded-full hover:bg-white/20 transition-colors mr-2">
          <Icon name="chevron-left" size="40rpx" class="brightness-0 invert" />
        </button>
        <div class="w-11 h-11 mr-3 bg-white text-[#064e3b] rounded-2xl flex items-center justify-center shadow-[4rpx_4rpx_0_rgba(0,0,0,0.18)]">
          <Icon name="bike" size="44rpx" />
        </div>
        <div>
          <span class="text-lg font-black tracking-wider">摩旅客</span>
          <div class="mt-0.5 flex items-center gap-1">
            <span class="w-2 h-2 rounded-full bg-white/80"></span>
            <span class="w-2 h-2 bg-white/45"></span>
            <span class="w-0 h-0 border-l-[4px] border-r-[4px] border-b-[8px] border-l-transparent border-r-transparent border-b-white"></span>
          </div>
        </div>
      </div>
    </header>

    <!-- 可滚动内容区 -->
    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar pb-24">
      <!-- 2. 当前主行程卡 (视觉焦点) -->
      <section class="px-4 mt-4">
        <div v-if="store.homeRouteCandidates.value.length > 1" class="relative mb-3">
          <button
            class="m-0 w-full app-card rounded-2xl px-4 py-3 flex items-center justify-between active:bg-[#fbfaf7] transition-colors"
            @click="isRouteSwitcherOpen = !isRouteSwitcherOpen"
          >
            <div class="flex items-center min-w-0">
              <Icon name="repeat" size="32rpx" class="mr-2 shrink-0" />
              <div class="text-left min-w-0">
                <div class="text-[10px] text-slate-400 leading-none">首页展示行程</div>
                <div class="text-sm font-bold text-slate-800 truncate mt-1">{{ homeRoute?.name || '请选择行程' }}</div>
              </div>
            </div>
            <div class="flex items-center text-xs text-[#064e3b] font-medium shrink-0 ml-3">
              <span>切换</span>
              <Icon name="chevron-down" size="28rpx" class="ml-1" />
            </div>
          </button>

          <div v-if="isRouteSwitcherOpen" class="mt-2 app-card rounded-2xl overflow-hidden">
            <button
              v-for="route in store.homeRouteCandidates.value"
              :key="route.id"
              class="m-0 w-full px-4 py-3 flex items-center justify-between text-left border-b border-slate-50 last:border-b-0 active:bg-slate-50"
              :class="homeRoute?.id === route.id ? 'bg-emerald-50' : 'bg-white'"
              @click="selectHomeRoute(route.id)"
            >
              <div class="min-w-0">
                <div class="text-sm font-bold text-slate-800 truncate">{{ route.name }}</div>
                <div class="text-[10px] text-slate-400 mt-1 truncate">
                  {{ route.origin }} - {{ route.destination }} · {{ route.startDate === route.endDate ? route.startDate : `${route.startDate} - ${route.endDate}` }}
                </div>
              </div>
              <Icon v-if="homeRoute?.id === route.id" name="check" size="32rpx" class="shrink-0 ml-3" />
            </button>
          </div>
        </div>

        <template v-if="homeRoute">
          <div 
            @click="router.push(`/route/${homeRoute.id}`)"
            class="block bg-[#064e3b] h-[284px] rounded-[28rpx] relative overflow-hidden p-5 flex flex-col justify-between text-white shadow-[10rpx_10rpx_0_rgba(18,24,21,0.14)] active:opacity-90"
          >
            <!-- 背景装饰：山脉线条 -->
            <div class="absolute inset-0 opacity-10 pointer-events-none">
              <svg class="w-full h-full" viewBox="0 0 400 300">
                <path d="M0 250 L100 150 L200 220 L300 100 L400 200 L400 300 L0 300 Z" fill="currentColor"></path>
              </svg>
            </div>
            <div class="absolute right-[-36rpx] top-[-32rpx] w-32 h-32 rounded-full bg-white/10 pointer-events-none"></div>
            <div class="absolute right-16 bottom-20 w-16 h-16 bg-white/10 rotate-45 pointer-events-none"></div>
            
            <div class="relative z-10">
              <div class="flex justify-between items-start">
                <div>
                  <h2 class="text-xl font-bold">{{ homeRoute.name }}</h2>
                  <p class="text-sm text-slate-300 mt-1">
                    {{ homeRoute.startDate === homeRoute.endDate ? homeRoute.startDate : `${homeRoute.startDate} - ${homeRoute.endDate}` }}
                  </p>
                </div>
                <div class="bg-white/90 text-[#064e3b] px-3 py-1 rounded-full text-xs font-black shadow-[3rpx_3rpx_0_rgba(0,0,0,0.12)]">
                  {{ homeRoute.status === '已完成' ? '已完成' : homeRoute.status === '进行中' ? '进行中' : homeRoute.daysLeft > 0 ? `倒计时 ${homeRoute.daysLeft} 天` : '今天出发' }}
                </div>
              </div>
              
              <div class="mt-8">
                <div class="flex items-center space-x-2 mb-2">
                  <Icon name="map-pin" size="32rpx" class="brightness-0 invert" />
                  <span class="text-sm font-medium">目的地：{{ homeRoute.destination }}</span>
                </div>
                
                <div class="w-full bg-white/20 h-2 rounded-full overflow-hidden border border-white/20">
                  <div class="bg-white h-full transition-all duration-500" :style="{ width: `${homeRoute.progress}%` }"></div>
                </div>
                
                <div class="flex justify-between text-[10px] mt-2 text-slate-300">
                  <span>备整进度 {{ homeRoute.progress }}%</span>
                  <span v-if="homeRoute.progress < 100">还有未完成项</span>
                  <span v-else>准备就绪</span>
                </div>
              </div>
            </div>
            
            <div class="relative z-10 w-full bg-white text-slate-900 py-3 rounded-2xl font-black flex items-center justify-center space-x-2 shadow-[4rpx_4rpx_0_rgba(0,0,0,0.18)]">
              <span>{{ homeRoute.status === '已完成' || homeRoute.progress >= 100 ? '查看行程详情' : '继续完善准备' }}</span>
              <Icon name="chevron-right" size="24rpx" />
            </div>
          </div>
        </template>
        
        <!-- 无主行程时的引导卡片 -->
        <div v-else class="app-card-strong border-2 border-dashed border-[#d8cdbd] h-[284px] rounded-[28rpx] p-5 flex flex-col items-center justify-center text-slate-400">
          <Icon name="bike" size="96rpx" />
          <h2 class="text-lg font-bold text-slate-700 mb-2">开启新的旅程</h2>
          <p class="text-xs mb-6">创建一个新行程，系统将为你提供智能准备建议</p>
          <button 
            @click="isCreateModalOpen = true"
            class="app-action-button app-primary-button px-6 py-2.5 rounded-full text-sm font-bold"
          >
            创建第一个行程
          </button>
        </div>
      </section>

      <!-- 3. 关键提醒区 (仅有主行程时显示) -->
      <section v-if="homeRoute" class="mt-6 px-4">
        <div class="flex justify-between items-center mb-3">
          <h3 class="app-section-heading">给你的出行提醒</h3>
          <div @click="router.push('/suggestions')" class="app-link text-xs flex items-center shrink-0 ml-3 whitespace-nowrap">
            全部出行提醒 <Icon name="chevron-right" size="24rpx" />
          </div>
        </div>
        <div class="space-y-3">
          <template v-if="store.alerts.value.length > 0">
            <div 
              v-for="(alert, index) in homeAlerts" 
              :key="index"
              class="p-3 rounded-2xl flex items-start gap-3 border-l-4 app-card"
              :class="{
                'bg-red-50 border-red-500': alert.severity === 'high' || alert.level === 'high',
                'bg-emerald-50 border-emerald-500': alert.severity === 'medium' || alert.level === 'medium',
                'bg-blue-50 border-blue-500': alert.severity === 'low' || alert.level === 'low',
                'bg-slate-50 border-slate-400': !alert.severity && !alert.level
              }"
            >
              <Icon v-if="alert.severity === 'high' || alert.level === 'high'" name="alert-triangle" size="40rpx" class="shrink-0 mt-0.5" />
              <Icon v-else-if="alert.type === 'weather'" name="cloud-snow" size="40rpx" class="shrink-0 mt-0.5" />
              <Icon v-else-if="alert.type === 'news'" name="book-open" size="40rpx" class="shrink-0 mt-0.5" />
              <Icon v-else name="wrench" size="40rpx" class="shrink-0 mt-0.5" />
              
              <div class="min-w-0 flex-1 text-xs leading-relaxed" :class="{
                'text-red-900': alert.severity === 'high' || alert.level === 'high',
                'text-emerald-900': alert.severity === 'medium' || alert.level === 'medium',
                'text-blue-900': alert.severity === 'low' || alert.level === 'low',
                'text-slate-900': !alert.severity && !alert.level
              }">
                <div class="font-bold truncate">{{ alert.title || '出行提醒' }}</div>
                <div class="mt-1">{{ alert.description || '暂无详细说明' }}</div>
              </div>
            </div>
          </template>
          <div v-else class="text-center text-xs text-slate-400 py-4 app-card rounded-2xl">
            暂无特殊出行预警
          </div>
        </div>
      </section>

      <!-- 4. 建议完成区 (仅有主行程时显示) -->
      <section v-if="homeRoute" class="mt-6 px-4">
        <div class="flex justify-between items-center mb-3">
          <h3 class="app-section-heading">建议完成</h3>
          <button class="app-action-button ml-auto m-0 p-0 bg-transparent border-0 rounded-none shadow-none text-xs text-[#064e3b] flex items-center justify-end font-bold" @click="toggleManualTodoInput">
            <Icon name="plus" size="24rpx" class="mr-1 shrink-0" /> 添加事项
          </button>
        </div>
        <div v-if="isAddingManualTodo" class="mb-3 app-card rounded-2xl p-3">
          <div class="flex items-center space-x-2">
            <input
              v-model="newManualTodoTitle"
              type="text"
              maxlength="40"
              placeholder-class="app-input-placeholder"
              placeholder="输入要手动添加的事项"
              class="app-input flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3 text-sm outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
              @keyup.enter="addManualTodo"
            />
            <button
              class="app-action-button px-3 py-2 rounded-xl bg-[#064e3b] text-white text-xs font-medium disabled:opacity-50"
              :disabled="!newManualTodoTitle.trim()"
              @click="addManualTodo"
            >
              保存
            </button>
            <button
              class="app-action-button px-3 py-2 rounded-xl bg-slate-100 text-slate-500 text-xs font-medium"
              @click="cancelManualTodoInput"
            >
              取消
            </button>
          </div>
        </div>
        <div class="app-card rounded-2xl divide-y divide-[#f0ebe0] overflow-hidden">
          <template v-if="store.suggestionTasks.value.length > 0">
            <div 
              v-for="task in store.suggestionTasks.value" 
              :key="task.id"
              class="p-4 flex items-center justify-between"
            >
              <div class="flex items-center space-x-3 flex-1 min-w-0 mr-3">
                <button
                  class="app-icon-button shrink-0 w-5 h-5 border-2 rounded-md transition-colors"
                  :class="task.done ? 'bg-emerald-500 border-emerald-500 text-white' : 'border-slate-200 text-transparent'"
                  @click="toggleManualTodo(task.id)"
                >
                  <Icon name="check" size="24rpx" />
                </button>
                
                <input
                    v-if="editingTodoId === task.id"
                    ref="editingInputRef"
                    v-model="editingTodoTitle"
                    type="text"
                    class="app-input-sm flex-1 text-sm bg-slate-50 border border-slate-200 rounded px-2 outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
                    @blur="saveEditedTodo(task.id)"
                    @keyup.enter="saveEditedTodo(task.id)"
                  />
                <span 
                  v-else
                  class="text-sm truncate cursor-text flex-1" 
                  :class="task.done ? 'text-slate-400 line-through' : 'text-slate-700'"
                  @click="startEditingTodo(task)"
                >
                  {{ task.title }}
                </span>
              </div>
              <div class="flex items-center space-x-2 shrink-0">
                <button
                  class="app-icon-button w-8 h-8 text-slate-300 hover:text-red-400 transition-colors"
                  @click="removeManualTodo(task.id)"
                >
                  <Icon name="trash-2" size="32rpx" />
                </button>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="p-4 text-center text-xs text-slate-400">
              暂无待办事项，点击上方添加
            </div>
          </template>
        </div>
      </section>

      <!-- 5. 其他内容区 (仅当有其他行程时显示) -->
      <section v-if="store.otherRoutes.value.length > 0" class="mt-6">
        <div class="px-4 flex justify-between items-center mb-3">
          <h3 class="app-section-heading">我的其他行程</h3>
        </div>
        <div class="flex space-x-4 overflow-x-auto hide-scrollbar px-4 pb-4">
          <div
            v-for="route in store.otherRoutes.value"
            :key="route.id"
            @click="router.push(`/route/${route.id}`)"
            class="shrink-0 w-64 h-32 app-card rounded-2xl p-4 flex flex-col justify-between cursor-pointer active:scale-[0.98] transition-transform"
          >
            <div>
              <span class="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full">{{ route.origin }} - {{ route.destination }}</span>
              <h4 class="mt-1 font-bold text-slate-800 truncate">{{ route.name }}</h4>
            </div>
            <div class="flex justify-between items-end">
              <span class="text-[10px] text-slate-400">
                {{ route.startDate === route.endDate ? route.startDate : `${route.startDate} 起` }}
              </span>
              <span class="text-[#064e3b] text-xs font-medium">查看详情</span>
            </div>
          </div>
        </div>
      </section>

      <!-- 新建行程模态框组件引入 -->
      <CreateRouteModal 
        :is-open="isCreateModalOpen" 
        @close="isCreateModalOpen = false" 
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, watch, nextTick } from 'vue'
import { onPullDownRefresh, onShareAppMessage, onShow } from '@dcloudio/uni-app'
import Icon from '@/components/Icon.vue'
import { useRouteStore } from '@/composables/useRouteStore'
import CreateRouteModal from '@/components/CreateRouteModal.vue'
import { router } from '@/utils/router'

const store = useRouteStore()
const homeRoute = computed(() => store.mainRoute.value)
const homeAlerts = computed(() => store.alerts.value.slice(0, 2))
const canGoBack = ref(false)
const isCreateModalOpen = ref(false)
const isRouteSwitcherOpen = ref(false)
const isAddingManualTodo = ref(false)
const newManualTodoTitle = ref('')

const editingTodoId = ref<string | null>(null)
const editingTodoTitle = ref('')
const editingInputRef = ref<any>(null)
const mountedOnce = ref(false)

const startEditingTodo = async (task: any) => {
  editingTodoId.value = task.id
  editingTodoTitle.value = task.title
  await nextTick()
  // v-for 中 ref 会收集为数组，取第一个元素
  const el = Array.isArray(editingInputRef.value) ? editingInputRef.value[0] : editingInputRef.value
  el?.focus?.()
}

const saveEditedTodo = async (todoId: string) => {
  if (editingTodoId.value !== todoId) return
  
  const route = homeRoute.value
  if (!route) return
  
  const newTitle = editingTodoTitle.value.trim()
  editingTodoId.value = null
  
  if (!newTitle) return

  const nextTodos = (route.manualTodos || []).map(item =>
    item.id === todoId ? { ...item, title: newTitle } : item
  )
  await store.saveManualTodos(route.id, nextTodos)
}

const refreshHomeData = async () => {
  await store.fetchRoutes()
  if (homeRoute.value) {
    await store.fetchAlertsAndSuggestions(homeRoute.value)
  }
}

onMounted(async () => {
  const pages = getCurrentPages()
  canGoBack.value = pages.length > 1
  await refreshHomeData()
  mountedOnce.value = true
})

onShow(async () => {
  if (!mountedOnce.value) return
  await refreshHomeData()
})

onPullDownRefresh(async () => {
  await refreshHomeData()
  uni.stopPullDownRefresh()
})

onShareAppMessage(() => {
  return {
    title: '摩旅客 - 智能摩旅出行规划',
    path: '/pages/HomePage'
  }
})

// 监听主行程变化，重新获取预警和建议
watch(() => homeRoute.value, (newRoute) => {
  if (newRoute) {
    store.fetchAlertsAndSuggestions(newRoute)
  }
})

const toggleManualTodoInput = () => {
  isAddingManualTodo.value = true
}

const cancelManualTodoInput = () => {
  isAddingManualTodo.value = false
  newManualTodoTitle.value = ''
}

const selectHomeRoute = (routeId: string) => {
  store.selectHomeRoute(routeId)
  isRouteSwitcherOpen.value = false
  editingTodoId.value = null
  cancelManualTodoInput()
}

const addManualTodo = async () => {
  const route = homeRoute.value
  if (!route) return
  const title = newManualTodoTitle.value.trim()
  if (!title) return

  const nextTodos = [...(route.manualTodos || []), {
    id: `manual-${Date.now()}`,
    title,
    done: false,
  }]
  await store.saveManualTodos(route.id, nextTodos)
  cancelManualTodoInput()
}

const toggleManualTodo = async (todoId: string) => {
  const route = homeRoute.value
  if (!route) return
  const nextTodos = (route.manualTodos || []).map(item =>
    item.id === todoId ? { ...item, done: !item.done } : item
  )
  await store.saveManualTodos(route.id, nextTodos)
}

const removeManualTodo = async (todoId: string) => {
  const route = homeRoute.value
  if (!route) return
  const nextTodos = (route.manualTodos || []).filter(item => item.id !== todoId)
  await store.saveManualTodos(route.id, nextTodos)
}
</script>

