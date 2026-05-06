﻿<template>
  <div class="h-full bg-slate-50 flex flex-col relative">
    <header class="app-safe-header h-24 pt-10 px-4 bg-white flex items-center justify-between sticky top-0 z-50 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">禁摩查询</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8 space-y-5">
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <label class="block text-sm font-medium text-slate-700 mb-2">输入查询城市</label>
        <div class="flex space-x-2">
          <input 
            v-model="city" 
            @keyup.enter="search"
            type="text" 
            placeholder-class="app-input-placeholder"
            placeholder="例如: 北京" 
            class="app-input flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 text-sm focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
          >
          <button 
            @click="search"
            :disabled="loading"
            class="app-action-button h-10 bg-[#064e3b] text-white px-5 rounded-xl text-sm font-bold shadow-sm active:scale-95 transition-transform disabled:opacity-50"
          >
            查询
          </button>
        </div>
      </div>

      <div v-if="result" class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <div class="flex items-center mb-3">
          <Icon name="shield-alert" size="40rpx" class="mr-2 shrink-0" />
          <h3 class="font-bold text-slate-800">{{ city }} 禁摩政策</h3>     
        </div>
        <p class="text-sm text-slate-600 leading-relaxed">{{ result.data?.description || '未查询到相关禁摩信息或该城市不禁摩。' }}</p>
      </div>

      <div v-else-if="searched && !loading" class="text-center text-slate-400 py-10">
        <p class="text-sm">未查询到该城市信息</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'
import { api } from '@/api'


const city = ref('')
const loading = ref(false)
const searched = ref(false)
const result = ref<any>(null)

const search = async () => {
  if (!city.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const res = await api.getRestriction(city.value.trim())
    result.value = res.status === 'ok' || res.status === 'success' ? res : null
  } catch (e) {
    result.value = null
  } finally {
    loading.value = false
  }
}
</script>
