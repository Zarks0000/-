﻿<template>
  <div class="h-full app-page relative flex flex-col pb-6">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">文章详情</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8" v-if="data">
      <div class="app-card rounded-2xl overflow-hidden">
        <!-- 顶部配图区 -->
        <div v-if="data.image" class="w-full h-48 relative">
          <image :src="data.image" class="w-full h-full" mode="aspectFill" />
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"></div>
        </div>
        <div v-else :class="`w-full h-32 ${data.iconBg || 'bg-slate-100'} flex items-center justify-center`">
          <div class="text-sm font-bold tracking-[0.2em] text-slate-400">MOTO</div>
        </div>

        <div class="p-5">
          <h2 class="text-xl font-bold text-slate-800 mb-3">{{ data.title }}</h2>
          <div class="text-xs text-slate-400 flex items-center mb-6 pb-4 border-b border-slate-100">
            <Icon name="book-open" size="24rpx" class="mr-1 shrink-0" />
            <span>预计阅读时间：{{ data.readTime }} 分钟</span>
          </div>
          
          <div class="text-sm text-slate-600 leading-relaxed whitespace-pre-wrap">
            {{ data.content }}
          </div>
        </div>
      </div>
    </main>
    <div v-else class="flex-1 flex items-center justify-center text-slate-400">
      加载中...
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { router } from '@/utils/router'
import { onLoad } from '@dcloudio/uni-app'
import Icon from '@/components/Icon.vue'
import { exploreKnowledge } from '@/data/templates'
import { showError } from '@/utils/uni'

const route = { params: {} as any, query: {} as any };

onLoad((options) => {
  route.params = options || {};
  route.query = options || {};
})

const data = ref<any>(null)

onMounted(() => {
  const id = route.params.id as string
  const found = exploreKnowledge.find(k => k.id === id)
  if (found) {
    data.value = found
  } else {
    showError('未找到该文章')
    router.back()
  }
})
</script>

