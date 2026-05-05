﻿<template>
  <div class="h-full app-page relative flex flex-col pb-6">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">摩旅知识</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8 space-y-4">
      <div class="space-y-3">
        <div 
          v-for="knowledge in exploreKnowledge" 
          :key="knowledge.id"
          @click="viewDetail(knowledge.id)"
          class="app-card p-3 rounded-2xl flex space-x-3 cursor-pointer active:scale-[0.98] transition-transform"
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
    </main>
  </div>
</template>

<script setup lang="ts">
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'
import { exploreKnowledge } from '@/data/templates'



const viewDetail = (id: string) => {
  router.push(`/knowledge/${id}`)
}
</script>

