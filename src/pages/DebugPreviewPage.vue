﻿<template>
  <div class="h-full bg-slate-50 flex flex-col">
    <header class="app-safe-header h-24 pt-10 px-4 bg-white flex items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="ml-1 text-base font-bold text-slate-800">调试页</h1>
    </header>
    <div class="flex-1 p-6">
      <div class="max-w-lg mx-auto bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
        <h1 class="text-xl font-bold text-slate-900">H5 调试页</h1>
        <p class="mt-3 text-sm text-slate-600">如果你能看到这个页面，说明 UniApp H5 基础链路是可用的，问题出在业务页面而不是开发服务器。</p>
        <div class="mt-4 text-xs text-slate-400">当前时间：{{ now }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Icon from '@/components/Icon.vue'
import { router } from '@/utils/router'

const now = new Date().toLocaleString()
</script>
