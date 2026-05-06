﻿<template>
  <div class="h-full bg-slate-50 flex flex-col relative">
    <header class="app-safe-header h-24 pt-10 px-4 bg-white flex items-center justify-between sticky top-0 z-50 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">装备计算</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8 space-y-5">
      <div class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <div class="flex items-center justify-between mb-2">
          <label class="block text-sm font-medium text-slate-700">添加你要携带的装备</label>
          <button
            @click="importMyEquipments"
            :disabled="importingMyEquipments"
            class="app-action-button m-0 px-3 py-1.5 rounded-full bg-orange-50 text-orange-700 text-xs font-medium disabled:opacity-50"
          >
            <Icon name="briefcase" size="24rpx" class="mr-1 shrink-0" />
            {{ importingMyEquipments ? '导入中' : '导入我的装备' }}
          </button>
        </div>
        <div class="app-form-stack mb-4">
          <div v-for="(item, idx) in items" :key="idx" class="app-form-row">
            <input 
              v-model="items[idx]" 
              type="text" 
              placeholder-class="app-input-placeholder"
              placeholder="例如: 帐篷、睡袋、补胎工具" 
              class="app-input flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 text-sm focus:outline-none focus:border-[#064e3b] focus:ring-1 focus:ring-[#064e3b]/20"
            >
            <button @click="removeItem(idx)" class="app-icon-button w-8 h-8 text-slate-300 hover:text-red-400 transition-colors">
              <Icon name="trash-2" size="32rpx" />
            </button>
          </div>
        </div>
        <div class="flex space-x-3">
          <button @click="addItem" class="app-action-button flex-1 text-sm text-[#064e3b] font-medium py-2 bg-emerald-50 rounded-xl transition-colors">
            + 继续添加
          </button>
          <button 
            @click="calculate"
            :disabled="loading || items.filter(Boolean).length === 0"
            class="app-action-button flex-1 bg-[#064e3b] text-white px-5 py-2 rounded-xl text-sm font-bold shadow-sm active:scale-95 transition-transform disabled:opacity-50"
          >
            {{ loading ? '计算中...' : '开始估算' }}
          </button>
        </div>
      </div>

      <div v-if="result" class="space-y-4">
        <div class="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl p-5 text-white shadow-lg shadow-emerald-500/20">
          <div class="flex justify-between items-center mb-4">
            <div>
              <p class="text-xs opacity-80">预估总重量</p>
              <h3 class="text-3xl font-bold font-mono mt-1">{{ result.data.total_weight_kg }} <span class="text-base font-medium">kg</span></h3>
            </div>
            <div class="text-right">
              <p class="text-xs opacity-80">预估总体积</p>
              <h3 class="text-3xl font-bold font-mono mt-1">{{ result.data.total_volume_L }} <span class="text-base font-medium">L</span></h3>
            </div>
          </div>
          <div class="bg-black/10 rounded-lg p-3 text-xs leading-relaxed">
            <span class="font-bold mr-1">专家建议：</span>{{ result.data.advice }}
          </div>
        </div>

        <h3 class="font-bold text-slate-800 flex items-center">
          <Icon name="package" size="32rpx" class="mr-1 shrink-0" />
          <span>装备明细评估</span>
        </h3>
        <div class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden divide-y divide-slate-50">
          <div v-for="(item, idx) in result.data.items" :key="idx" class="p-3 flex justify-between items-center">
            <span class="text-sm font-medium text-slate-700 flex-1">{{ item.name }}</span>
            <div class="flex space-x-4 text-xs text-slate-500 font-mono">
              <span class="w-12 text-right">{{ item.weight_kg }} kg</span>
              <span class="w-12 text-right">{{ item.volume_L }} L</span>
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'
import { api } from '@/api'
import { showError, showSuccess } from '@/utils/uni'

type MyEquipment = {
  id?: string
  name?: string
  category?: string
  weight_kg?: number | null
  note?: string
}

const items = ref(['', ''])
const loading = ref(false)
const importingMyEquipments = ref(false)
const result = ref<any>(null)

const addItem = () => items.value.push('')
const removeItem = (idx: number) => items.value.splice(idx, 1)

const formatMyEquipment = (item: MyEquipment) => {
  const name = (item.name || '').trim()
  if (!name) return ''
  const extra = [
    item.category ? item.category.trim() : '',
    item.weight_kg !== null && typeof item.weight_kg !== 'undefined' ? `${item.weight_kg}kg` : ''
  ].filter(Boolean)
  return extra.length > 0 ? `${name}（${extra.join('，')}）` : name
}

const importMyEquipments = async () => {
  if (importingMyEquipments.value) return

  importingMyEquipments.value = true
  try {
    const res = await api.getMyEquipments()
    if (res.status !== 'success') {
      throw new Error(res.message || '读取我的装备失败')
    }

    const imported = Array.isArray(res.data)
      ? res.data.map(formatMyEquipment).filter(Boolean)
      : []
    if (imported.length === 0) {
      showError('我的装备中暂无可导入内容')
      return
    }

    const existing = new Set(items.value.map(i => i.trim()).filter(Boolean))
    const nextImported = imported.filter(name => !existing.has(name))
    if (nextImported.length === 0) {
      showSuccess('我的装备已全部导入')
      return
    }

    items.value = [
      ...items.value.map(i => i.trim()).filter(Boolean),
      ...nextImported
    ]
    result.value = null
    showSuccess(`已导入${nextImported.length}件装备`)
  } catch (e: any) {
    showError(e.message || '导入我的装备失败')
  } finally {
    importingMyEquipments.value = false
  }
}

const calculate = async () => {
  const validItems = items.value.map(i => i.trim()).filter(Boolean)
  if (validItems.length === 0) return
  
  loading.value = true
  try {
    const res = await api.calculateEquipment(validItems)
    result.value = res.status === 'ok' ? res : null
  } catch (e: any) {
    showError(e.message || '大模型评估失败')
  } finally {
    loading.value = false
  }
}
</script>
