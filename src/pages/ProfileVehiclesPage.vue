﻿<template>
  <div class="h-full bg-slate-50 relative flex flex-col pb-6">
    <header class="app-safe-header h-24 pt-10 px-4 bg-white flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">我的车辆</h1>
      <button @click="openCreate" class="app-header-pill-button bg-emerald-50 text-xs text-emerald-700 font-bold">新增</button>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8 space-y-3">
      <div
        v-for="(item, idx) in items"
        :key="item.id"
        @click="openEdit(idx)"
        class="bg-white rounded-2xl border border-slate-100 shadow-sm p-4 cursor-pointer active:scale-[0.98] transition-transform"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3 min-w-0">
            <div class="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center">
              <Icon name="bike" size="40rpx" />
            </div>
            <div class="min-w-0">
              <div class="text-sm font-bold text-slate-800 line-clamp-1">{{ item.brand }} {{ item.model }}</div>
              <div class="text-xs text-slate-400 mt-0.5">
                {{ item.displacement || '排量未填写' }} · {{ item.plate_no || '车牌未填写' }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-1 shrink-0 ml-3">
            <button @click.stop="openEdit(idx)" class="app-action-button h-8 px-3 rounded-full bg-slate-50 text-xs text-slate-500 font-medium">
              编辑
            </button>
            <button @click.stop="removeItem(idx)" class="app-icon-button w-8 h-8 text-slate-300 hover:text-red-400">
              <Icon name="trash-2" size="32rpx" />
            </button>
          </div>
        </div>
      </div>

      <div v-if="items.length === 0" class="text-center text-slate-400 text-sm py-16">
        暂无车辆，点击右上角“新增”
      </div>
    </main>

    <div
      v-if="showEditor"
      class="absolute inset-0 z-[70] bg-black/40 flex items-end"
      @click.self="showEditor = false"
    >
      <div class="w-full max-h-[84vh] overflow-y-auto hide-scrollbar bg-white rounded-t-2xl p-4" @click.stop>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-sm font-bold text-slate-800">{{ editingIndex >= 0 ? '编辑车辆' : '新增车辆' }}</h3>
          <button @click="showEditor = false" class="app-icon-button app-close-button">
            <Icon name="x" size="32rpx" />
          </button>
        </div>
        <div class="app-form-stack">
          <input v-model="draft.brand" type="text" placeholder-class="app-input-placeholder" placeholder="品牌（如 Honda）" class="w-full input app-input" />
          <input v-model="draft.model" type="text" placeholder-class="app-input-placeholder" placeholder="车型（如 CB500X）" class="w-full input app-input" />
          <div class="app-form-grid">
            <input v-model="draft.displacement" type="text" placeholder-class="app-input-placeholder" placeholder="排量（如 500cc）" class="w-full input app-input" />
            <input v-model="draft.plate_no" type="text" placeholder-class="app-input-placeholder" placeholder="车牌（可选）" class="w-full input app-input" />
          </div>
          <button
            @click="saveEditor"
            :disabled="saving"
            class="app-full-button w-full mt-1 bg-[#064e3b] text-white font-bold py-3 rounded-xl disabled:opacity-50"
          >
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'
import { api } from '@/api'
import { confirmDialog, showError, showSuccess } from '@/utils/uni'

type VehicleItem = {
  id: string
  brand: string
  model: string
  displacement?: string
  plate_no?: string
}


const items = ref<VehicleItem[]>([])
const saving = ref(false)
const showEditor = ref(false)
const editingIndex = ref(-1)
const draft = ref<VehicleItem>({ id: '', brand: '', model: '', displacement: '', plate_no: '' })

const uid = () => `${Date.now()}_${Math.random().toString(16).slice(2, 8)}`

const openCreate = () => {
  editingIndex.value = -1
  draft.value = { id: uid(), brand: '', model: '', displacement: '', plate_no: '' }
  showEditor.value = true
}

const openEdit = (idx: number) => {
  editingIndex.value = idx
  draft.value = { ...items.value[idx] }
  showEditor.value = true
}

const removeItem = async (idx: number) => {
  const ok = await confirmDialog('确认删除该车辆吗？')
  if (!ok) return
  items.value.splice(idx, 1)
  await persist()
}

const load = async () => {
  const res = await api.getMyVehicles()
  if (res.status === 'success') {
    items.value = Array.isArray(res.data) ? res.data : []
  }
}

const persist = async () => {
  saving.value = true
  try {
    const payload = items.value
      .map(i => ({ ...i, brand: i.brand.trim(), model: i.model.trim() }))
      .filter(i => i.brand && i.model)
    const res = await api.saveMyVehicles(payload)
    if (res.status !== 'success') throw new Error(res.message || '保存失败')
    showSuccess('保存成功')
    await load()
  } catch (e: any) {
    showError(e.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const saveEditor = async () => {
  const brand = draft.value.brand.trim()
  const model = draft.value.model.trim()
  if (!brand || !model) {
    showError('请至少填写品牌和车型')
    return
  }
  const next = { ...draft.value, brand, model }
  if (editingIndex.value >= 0) {
    items.value[editingIndex.value] = next
  } else {
    items.value.unshift(next)
  }
  await persist()
  showEditor.value = false
}

onMounted(load)
</script>

<style scoped>
.input {
  @apply bg-slate-50 border border-slate-200 rounded-lg px-3 text-sm outline-none focus:border-emerald-600/60;
  height: 80rpx;
  min-height: 80rpx;
  line-height: 80rpx;
  padding-top: 0;
  padding-bottom: 0;
}
</style>
