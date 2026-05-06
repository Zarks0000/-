﻿<template>
  <div class="h-full bg-slate-50 relative flex flex-col pb-6">
    <header class="app-safe-header h-24 pt-10 px-4 bg-white flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">全部精选路线</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8 space-y-4">
      <div
        v-for="rt in exploreRoutes"
        :key="rt.id"
        @click="viewDetail(rt.id)"
        class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden relative cursor-pointer active:scale-[0.98] transition-transform"
      >
        <div class="h-28 relative">
          <image :src="rt.image" class="absolute inset-0 w-full h-full" mode="aspectFill" />
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
          <div class="absolute bottom-3 left-3 text-white z-10">
            <h4 class="font-bold text-lg drop-shadow-md">{{ rt.title }}</h4>
            <p class="text-xs opacity-90 mt-1 drop-shadow">{{ rt.desc }}</p>
          </div>
        </div>
        <div class="p-4 flex items-center">
          <div class="route-meta-row">
            <div class="route-meta-item">
              <view class="route-meta-icon route-meta-compass">
                <view class="route-meta-compass-needle"></view>
              </view>
              <text class="route-meta-text">{{ rt.days }} 天</text>
            </div>
            <div class="route-meta-item">
              <view class="route-meta-icon route-meta-mountain">
                <view class="route-meta-mountain-shape"></view>
              </view>
              <text class="route-meta-text">{{ rt.style === 'leisure' ? '休闲游' : (rt.style === 'aggressive' ? '挑战' : '标准') }}</text>
            </div>
          </div>
          <button @click.stop="applyTemplate(rt)" class="app-action-button ml-3 shrink-0 bg-[#064e3b] text-white px-4 py-1.5 rounded-full text-xs font-bold shadow-sm active:scale-95 transition-transform">
            参考路线
          </button>
        </div>
      </div>
    </main>

    <CreateRouteModal
      ref="createRouteModalRef"
      :is-open="isCreateModalOpen"
      @close="isCreateModalOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'
import { exploreRoutes } from '@/data/templates'
import CreateRouteModal from '@/components/CreateRouteModal.vue'


const createRouteModalRef = ref<InstanceType<typeof CreateRouteModal> | null>(null)
const isCreateModalOpen = ref(false)

const viewDetail = (id: string) => {
  router.push(`/template/${id}`)
}

const buildPreset = (item: any) => ({
  ...(item?.applyArgs || item || {}),
  schedule: Array.isArray(item?.schedule) ? item.schedule : []
})

const applyTemplate = (item: any) => {
  isCreateModalOpen.value = true
  setTimeout(() => {
    createRouteModalRef.value?.openWithPreset(buildPreset(item))
  }, 50)
}
</script>

<style scoped>
.route-meta-row {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  color: #64748b;
  font-size: 12px;
  line-height: 20px;
}

.route-meta-item {
  display: flex;
  align-items: center;
  height: 20px;
  margin-right: 16px;
  white-space: nowrap;
}

.route-meta-icon {
  width: 14px;
  height: 14px;
  margin-right: 4px;
  flex: 0 0 14px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.route-meta-text {
  display: block;
  height: 20px;
  line-height: 20px;
}

.route-meta-compass {
  border: 1.5px solid #64748b;
  border-radius: 999px;
}

.route-meta-compass-needle {
  width: 5px;
  height: 5px;
  background: #64748b;
  transform: rotate(45deg);
}

.route-meta-mountain {
  align-items: flex-end;
}

.route-meta-mountain-shape {
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 11px solid #64748b;
}
</style>
