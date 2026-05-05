<template>
  <div class="h-full app-page relative flex flex-col">
    <!-- 1. 顶部导航 -->
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex justify-between items-center sticky top-0 z-40 shrink-0">
      <div class="flex items-center">
        <button v-if="canGoBack" @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600 mr-1">
          <Icon name="chevron-left" size="40rpx" />
        </button>
        <div>
          <h1 class="text-xl font-black text-slate-900 tracking-wide">我的行程</h1>
        </div>
      </div>
    </header>

    <!-- 2. 状态分组切换 -->
    <div class="app-topbar px-4 sticky app-safe-sticky-under-header top-24 z-40 shrink-0">
      <div class="flex justify-between max-w-[360px] mx-auto">
        <button 
          v-for="tab in tabs" 
          :key="tab"
          @click="activeTab = tab"
          class="app-action-button relative m-0 min-w-24 px-0 py-3 bg-transparent border-0 rounded-none shadow-none text-[15px] font-black leading-normal transition-colors duration-200"
          :class="activeTab === tab ? 'text-[#064e3b]' : 'text-slate-400'"
        >
          {{ tab }}
          <!-- 选中下划线 -->
          <div 
            v-if="activeTab === tab"
            class="absolute bottom-0 left-1/2 -translate-x-1/2 w-8 h-1 bg-[#064e3b] rounded-t-full shadow-[0_0_0_2rpx_rgba(6,78,59,0.12)]"
          ></div>
        </button>
      </div>
    </div>

    <!-- 3. 行程列表区 -->
    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-24 relative">
      <!-- 行程列表 -->
      <div v-if="filteredRoutes.length > 0" class="space-y-4">
        <div
          v-for="route in filteredRoutes" 
          :key="route.id"
          @click="router.push(`/route/${route.id}`)"
          class="app-card-strong rounded-[28rpx] p-4 active:bg-[#fbfaf7] transition-colors relative overflow-hidden"
        >
          <div class="absolute right-[-18rpx] top-[-18rpx] w-16 h-16 rounded-full bg-[#064e3b]/8"></div>
          <div class="flex justify-between items-start mb-2">
            <div class="relative z-10 min-w-0">
              <h3 class="font-bold text-slate-800 text-lg">{{ route.name }}</h3>
              <div class="flex items-center text-xs text-slate-400 mt-1">
                <span class="flex items-center">
                  <Icon name="calendar" size="24rpx" class="mr-1 shrink-0" />
                  <span>{{ route.startDate === route.endDate ? route.startDate : `${route.startDate} - ${route.endDate}` }}</span>
                </span>
                <span v-if="route.startDate !== route.endDate" style="margin-left: 20rpx;">{{ 
                  Math.ceil((new Date(route.endDate.replace(/\./g, '-')).getTime() - new Date(route.startDate.replace(/\./g, '-')).getTime()) / (1000*60*60*24)) + 1 
                }}天</span>
                <span v-else style="margin-left: 20rpx;">单日</span>
              </div>
              <!-- 新增：显示高德 API 估算的真实距离 -->
              <div v-if="route.totalDistance" class="flex items-center text-xs text-slate-500 mt-1">
                <span class="flex items-center font-semibold text-emerald-600">全程约 {{ route.totalDistance.toFixed(1) }} km</span>
              </div>
            </div>
            <button class="app-icon-button relative z-10 w-8 h-8 text-slate-400 -mr-1 hover:bg-slate-100 rounded-full" @click.stop.prevent="confirmDeleteRoute(route.id)">
              <Icon name="trash-2" size="32rpx" />
            </button>
          </div>
          
          <div class="flex items-center space-x-2 text-sm text-slate-600 mb-4 mt-3">
            <span class="bg-[#fbfaf7] border border-[#ebe4d7] px-2 py-0.5 rounded-full text-xs">{{ route.origin }}</span>
            <Icon name="arrow-right" size="24rpx" />
            <span class="bg-[#064e3b]/10 text-[#064e3b] px-2 py-0.5 rounded-full text-xs font-bold">{{ route.destination }}</span>
          </div>

          <div class="flex items-center justify-between mt-4">
            <div class="flex-1 mr-4">
              <div class="flex justify-between text-[10px] text-slate-400 mb-1">
                <span>备整进度 {{ route.progress }}%</span>
              </div>
              <div class="w-full bg-[#eee7db] h-2 rounded-full overflow-hidden">
                <div class="bg-[#064e3b] h-full transition-all duration-500" :style="{ width: `${route.progress}%` }"></div>
              </div>
            </div>
            <div class="text-[#064e3b] text-xs font-black bg-[#eef7f2] border border-[#cfe5da] px-2 py-1 rounded-full">
              {{ route.daysLeft > 0 ? `距出发 ${route.daysLeft} 天` : '今天出发' }}
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="h-full flex flex-col items-center justify-center text-slate-400 pb-20">
        <Icon name="map" size="96rpx" />
        <p class="text-sm mb-4">
          {{ activeTab === '已完成' ? '开始你的第一次摩旅吧' : `还没有${activeTab}的摩旅` }}
        </p>
        <button v-if="activeTab !== '已完成'" @click="isCreateModalOpen = true" class="app-action-button app-primary-button px-4 py-2 text-sm rounded-full font-bold">创建新行程</button>
      </div>
    </main>

    <!-- 4. 浮动创建按钮 (FAB) -->
    <button 
      @click="isCreateModalOpen = true"
      class="absolute right-4 bottom-24 w-14 h-14 app-accent-button rounded-full flex items-center justify-center active:scale-90 transition-transform z-50"
    >
      <Icon name="plus" size="48rpx" class="brightness-0 invert" />
    </button>

    <!-- 5. 新建行程模态框 -->
    <CreateRouteModal 
      :is-open="isCreateModalOpen" 
      @close="isCreateModalOpen = false" 
    />
  </div>
 </template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { onPullDownRefresh, onShareAppMessage } from '@dcloudio/uni-app'
import Icon from '@/components/Icon.vue'
import { useRouteStore } from '@/composables/useRouteStore'
import CreateRouteModal from '@/components/CreateRouteModal.vue'
import { router } from '@/utils/router'
import { confirmDialog } from '@/utils/uni'

const tabs = ['筹备中', '进行中', '已完成']
const activeTab = ref('筹备中')
const store = useRouteStore()
const isCreateModalOpen = ref(false)
const canGoBack = ref(false)

onMounted(async () => {
  const pages = getCurrentPages()
  canGoBack.value = pages.length > 1
  await store.fetchRoutes()
})

onPullDownRefresh(async () => {
  await store.fetchRoutes()
  uni.stopPullDownRefresh()
})

onShareAppMessage(() => {
  return {
    title: '我的摩旅路线',
    path: '/pages/RoutePage'
  }
})

const confirmDeleteRoute = async (routeId: string) => {
  const ok = await confirmDialog('确定删除该行程吗？删除后不可恢复。')
  if (!ok) return
  await store.deleteRoute(routeId)
}

// 根据当前选中 Tab 过滤行程列表
const filteredRoutes = computed(() => {
  return store.routes.value.filter(route => route.status === activeTab.value)
})
</script>

