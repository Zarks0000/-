﻿<template>
  <div class="h-full bg-slate-50 relative flex flex-col pb-20">
    <header class="app-safe-header h-24 pt-10 px-4 bg-white flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">模板详情</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar relative" v-if="data">
      <!-- 封面图/渐变区 -->
      <div class="w-full h-[240px] relative flex flex-col justify-end p-6 text-white overflow-hidden">
        <image v-if="data.image" :src="data.image" class="absolute inset-0 w-full h-full" mode="aspectFill" />
        <div v-else :class="`absolute inset-0 bg-gradient-to-r ${data.coverGradient || 'from-slate-700 to-slate-800'}`"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
        <div class="relative z-10">
          <h2 class="text-2xl font-bold drop-shadow-lg">{{ data.title }}</h2>
          <p class="text-sm opacity-90 mt-1 drop-shadow-md">{{ data.desc }}</p>
        </div>
      </div>

      <div class="p-4 relative z-10">
        <!-- 信息卡片 -->
        <div class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100 mb-4 flex justify-between">
           <div class="text-center flex-1 border-r border-slate-100">
             <div class="text-xs text-slate-400 mb-1">建议天数</div>
             <div class="font-bold text-slate-800">{{ data.days }} 天</div>
           </div>
           <div class="text-center flex-1">
             <div class="text-xs text-slate-400 mb-1">骑行风格</div>
             <div class="font-bold text-slate-800">{{ styleText }}</div>
           </div>
        </div>

        <!-- 分日路书 -->
        <h3 class="font-bold text-slate-800 mb-3 flex items-center">
          <Icon name="map" size="32rpx" class="mr-1 shrink-0" />
          <span>分日路书参考</span>
        </h3>
        <div class="space-y-3">
          <div v-for="day in data.schedule" :key="day.day" class="bg-white rounded-2xl p-4 shadow-sm border border-slate-100">
            <div class="flex justify-between items-center mb-2">
              <span class="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded text-xs font-bold">
                Day {{ day.day }}
              </span>
              <span class="text-xs text-slate-400 font-medium">约 {{ day.distance_km }} km</span>
            </div>
            <h4 class="font-bold text-slate-800 text-sm mb-1">{{ day.title }}</h4>
            <p class="text-xs text-slate-500 leading-relaxed">{{ day.description }}</p>
          </div>
        </div>
      </div>
    </main>

    <div v-else class="flex-1 flex items-center justify-center text-slate-400">
      加载中...
    </div>

    <!-- 底部悬浮操作栏 -->
    <div class="fixed bottom-0 w-full md:w-[375px] bg-white border-t border-slate-100 p-4 pb-8 z-40">
      <button @click="applyTemplate" class="app-full-button w-full bg-[#064e3b] text-white font-bold py-3.5 rounded-xl shadow-lg shadow-[#064e3b]/30 active:scale-[0.98] transition-transform">
        套用此{{ data?.type === 'route' ? '路线' : '模板' }}
      </button>
    </div>

    <CreateRouteModal 
      ref="createRouteModalRef"
      :is-open="isCreateModalOpen" 
      @close="isCreateModalOpen = false" 
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { router } from '@/utils/router'
import { onLoad } from '@dcloudio/uni-app'
import Icon from '@/components/Icon.vue'
import { exploreTemplates, exploreRoutes } from '@/data/templates'
import CreateRouteModal from '@/components/CreateRouteModal.vue'
import { showError } from '@/utils/uni'

const route = { params: {} as any, query: {} as any };

onLoad((options) => {
  route.params = options || {};
  route.query = options || {};
})


const data = ref<any>(null)
const isCreateModalOpen = ref(false)
const createRouteModalRef = ref<any>(null)

onMounted(() => {
  const id = route.params.id as string
  const found = exploreTemplates.find(t => t.id === id) || exploreRoutes.find(r => r.id === id)
  if (found) {
    data.value = found
  } else {
    showError('未找到该模板')
    router.back()
  }
})

const styleText = computed(() => {
  if (data.value?.style === 'leisure') return '休闲游'
  if (data.value?.style === 'aggressive') return '挑战'
  return '标准'
})

const applyTemplate = () => {
  isCreateModalOpen.value = true
  setTimeout(() => {
    createRouteModalRef.value?.openWithPreset({
      ...(data.value?.applyArgs || {}),
      schedule: Array.isArray(data.value?.schedule) ? data.value.schedule : []
    })
  }, 50)
}
</script>
