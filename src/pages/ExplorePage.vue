﻿<template>
  <div class="h-full bg-[#faf9f6] flex flex-col relative">
    <header class="app-safe-header h-24 pt-10 px-4 bg-[#faf9f6] flex items-center sticky top-0 z-40 shrink-0">
      <div class="flex items-center w-full">
        <button v-if="canGoBack" @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600 mr-1">
          <Icon name="chevron-left" size="40rpx" />
        </button>
        <h1 class="text-xl font-bold text-slate-900">发现</h1>
      </div>
    </header>
    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-24 space-y-6">
      <!-- 2. 场景模板库 -->
      <section>
        <div class="relative w-full flex items-center mb-3 pr-20">
          <h3 class="font-bold text-slate-800">场景模板</h3>
          <button @click="router.push('/templates')" class="absolute right-0 top-1/2 -translate-y-1/2 m-0 p-0 bg-transparent border-0 rounded-none shadow-none text-xs text-slate-400 flex items-center justify-end leading-none">
            <span>全部</span><Icon name="chevron-right" size="24rpx" class="ml-1" />
          </button>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div
            v-for="tpl in displayedTemplates"
            :key="tpl.id"
            @click="viewDetail(tpl.id)"
            class="bg-white p-3 rounded-xl shadow-sm border border-slate-100 cursor-pointer active:scale-95 transition-transform"
          >
            <div class="w-8 h-8 rounded-lg flex items-center justify-center mb-2" :class="iconBgClass(tpl.iconBg)">
              <Icon :name="iconName(tpl.icon)" size="32rpx" />
            </div>
            <h4 class="text-sm font-bold text-slate-800">{{ tpl.title }}</h4>
            <p class="text-[10px] text-slate-400 mt-1 line-clamp-1">{{ tpl.desc }}</p>
            <button @click.stop="applyTemplate(tpl)" class="app-action-button mt-3 w-full py-1.5 text-xs text-[#064e3b] bg-[#064e3b]/5 rounded-md font-medium">套用模板</button>
          </div>
        </div>
      </section>

      <!-- 3. 独立工具区 -->
      <section>
        <div class="w-full flex items-center mb-3">
          <h3 class="font-bold text-slate-800">实用工具</h3>
        </div>
        <div class="grid grid-cols-4 gap-2">
          <div @click="router.push('/tool/restriction')" class="bg-white py-3 flex flex-col items-center rounded-xl shadow-sm border border-slate-100 cursor-pointer active:scale-95 transition-transform">
            <div class="w-10 h-10 bg-red-50 rounded-full flex items-center justify-center mb-1">
              <Icon name="shield-alert" size="40rpx" />
            </div>
            <span class="text-[10px] font-medium text-slate-700">禁摩查询</span>
          </div>
          <div @click="router.push('/tool/weather')" class="bg-white py-3 flex flex-col items-center rounded-xl shadow-sm border border-slate-100 cursor-pointer active:scale-95 transition-transform">
            <div class="w-10 h-10 bg-sky-50 rounded-full flex items-center justify-center mb-1">
              <Icon name="cloud-sun" size="40rpx" />
            </div>
            <span class="text-[10px] font-medium text-slate-700">天气查询</span>
          </div>
          <div @click="router.push('/tool/equipment')" class="bg-white py-3 flex flex-col items-center rounded-xl shadow-sm border border-slate-100 cursor-pointer active:scale-95 transition-transform">
            <div class="w-10 h-10 bg-emerald-50 rounded-full flex items-center justify-center mb-1">
              <Icon name="package" size="40rpx" />
            </div>
            <span class="text-[10px] font-medium text-slate-700">装备计算</span>
          </div>
          <div @click="router.push('/tool/budget')" class="bg-white py-3 flex flex-col items-center rounded-xl shadow-sm border border-slate-100 cursor-pointer active:scale-95 transition-transform">
            <div class="w-10 h-10 bg-amber-50 rounded-full flex items-center justify-center mb-1">
              <Icon name="calculator" size="40rpx" />
            </div>
            <span class="text-[10px] font-medium text-slate-700">预算估算</span>
          </div>
        </div>
      </section>

      <!-- 精选路线参考 -->
      <section>
        <div class="relative w-full flex items-center mb-3 pr-20">
          <h3 class="font-bold text-slate-800">精选路线参考</h3>
          <button @click="router.push('/routes')" class="absolute right-0 top-1/2 -translate-y-1/2 m-0 p-0 bg-transparent border-0 rounded-none shadow-none text-xs text-slate-400 flex items-center justify-end leading-none">
            <span>全部</span><Icon name="chevron-right" size="24rpx" class="ml-1" />
          </button>
        </div>
        <div class="space-y-4">
          <div
            v-for="rt in displayedRoutes"
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
        </div>
      </section>

      <!-- 4. 摩旅知识卡片 -->
      <section>
        <div class="relative w-full flex items-center mb-3 pr-24">
          <h3 class="font-bold text-slate-800">摩旅知识</h3>
          <button @click="router.push('/knowledge')" class="absolute right-0 top-1/2 -translate-y-1/2 m-0 p-0 bg-transparent border-0 rounded-none shadow-none text-xs text-slate-400 flex items-center justify-end leading-none">
            <span>查看全部</span><Icon name="chevron-right" size="24rpx" class="ml-1" />
          </button>
        </div>
        <div class="space-y-3">
          <div 
            v-for="knowledge in displayedKnowledge" 
            :key="knowledge.id"
            @click="router.push(`/knowledge/${knowledge.id}`)"
            class="bg-white p-3 rounded-xl shadow-sm border border-slate-100 flex space-x-3 cursor-pointer active:scale-[0.98] transition-transform"
          >
            <div class="w-20 h-20 bg-slate-100 rounded-md shrink-0 flex items-center justify-center overflow-hidden">
              <image v-if="knowledge.image" :src="knowledge.image" class="w-full h-full" mode="aspectFill" />
              <div v-else class="text-[11px] font-bold tracking-wide text-slate-400">摩旅</div>
            </div>
            <div class="flex flex-col justify-between flex-1 py-0.5">
              <div>
                <h4 class="text-sm font-bold text-slate-800 line-clamp-1">{{ knowledge.title }}</h4>
                <p class="text-xs text-slate-500 mt-1 line-clamp-2">{{ knowledge.desc }}</p>
              </div>
              <div class="text-[10px] text-slate-400 flex items-center mt-2">
                <Icon name="book-open" size="24rpx" class="mr-1 shrink-0" />
                <span>{{ knowledge.readTime }} 分钟阅读</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

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
import Icon from '@/components/Icon.vue'
import CreateRouteModal from '@/components/CreateRouteModal.vue'
import { exploreTemplates, exploreRoutes, exploreKnowledge } from '@/data/templates'


const createRouteModalRef = ref<InstanceType<typeof CreateRouteModal> | null>(null)
const isCreateModalOpen = ref(false)
const canGoBack = ref(false)

onMounted(() => {
  const pages = getCurrentPages()
  canGoBack.value = pages.length > 1
})

const iconName = (raw?: string) => {
  if (!raw) return 'compass'
  return raw.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase()
}

const iconBgClass = (raw?: string) => {
  switch (raw) {
    case 'bg-orange-50':
      return 'bg-orange-50'
    case 'bg-emerald-50':
      return 'bg-emerald-50'
    case 'bg-blue-50':
    default:
      return 'bg-blue-50'
  }
}

const displayedTemplates = computed(() => {
  return exploreTemplates.slice(0, 2)
})

const displayedRoutes = computed(() => {
  return exploreRoutes.slice(0, 1)
})

const displayedKnowledge = computed(() => {
  return exploreKnowledge.slice(0, 1)
})

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
