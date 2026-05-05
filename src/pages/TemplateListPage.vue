﻿<template>
  <div class="h-full app-page relative flex flex-col pb-6">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">全部场景模板</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8 space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <div
          v-for="tpl in exploreTemplates"
          :key="tpl.id"
          @click="viewDetail(tpl.id)"
          class="app-card p-3 rounded-2xl flex flex-col items-center text-center cursor-pointer active:scale-95 transition-transform"
        >
          <image :src="tpl.image" class="w-full h-24 rounded-md mb-2" mode="aspectFill" />
          <h4 class="text-xs font-bold text-slate-800">{{ tpl.title }}</h4>
          <p class="text-[10px] text-slate-400 mt-1 line-clamp-2 h-7">{{ tpl.desc }}</p>
          <button @click.stop="applyTemplate(tpl)" class="app-action-button mt-2 w-full py-1.5 text-xs text-[#064e3b] bg-[#064e3b]/5 rounded-md font-medium">套用</button>
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
import { exploreTemplates } from '@/data/templates'
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

