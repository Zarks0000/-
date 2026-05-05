﻿<template>
  <div class="h-full app-page relative flex flex-col pb-6">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">我的模板</h1>
      <button @click="openCreate" class="app-header-pill-button bg-emerald-50 text-xs text-emerald-700 font-bold">新增</button>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 pb-8 space-y-4">
      <div
        v-for="(item, idx) in items"
        :key="item.id"
        @click="openDetail(item.id)"
        class="app-card rounded-2xl p-4 cursor-pointer active:scale-[0.98] transition-transform"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center shrink-0">
                <Icon name="file-text" size="36rpx" />
              </div>
              <div class="min-w-0">
                <h3 class="text-sm font-bold text-slate-800 line-clamp-1">{{ item.title || `模板 ${idx + 1}` }}</h3>
                <p class="text-xs text-slate-400 mt-0.5">{{ item.days }} 天 · {{ item.schedule.length }} 段路书</p>
              </div>
            </div>
            <p class="text-xs text-slate-500 line-clamp-2 mt-3">{{ item.desc || '暂无模板说明，点击卡片查看模板详情' }}</p>
          </div>
          <div class="flex items-center gap-1 shrink-0">
            <button
              @click.stop="openEdit(idx)"
              class="app-action-button h-8 px-3 rounded-full bg-slate-50 text-xs text-slate-500 font-medium"
            >
              编辑
            </button>
            <button
              @click.stop="removeItem(idx)"
              class="app-icon-button w-8 h-8 text-slate-300 hover:text-red-400"
            >
              <Icon name="trash-2" size="32rpx" />
            </button>
          </div>
        </div>
      </div>

      <div v-if="items.length === 0" class="text-center text-slate-400 text-sm py-16">
        暂无模板，点击右上角“新增”
      </div>
    </main>

    <div
      v-if="showEditor"
      class="absolute inset-0 z-[70] bg-black/40 flex items-end"
      @click.self="showEditor = false"
    >
      <div class="w-full max-h-[84vh] overflow-y-auto hide-scrollbar bg-white rounded-t-2xl p-4 space-y-4" @click.stop>
        <div class="flex items-center justify-between mb-1">
          <h3 class="text-sm font-bold text-slate-800">{{ editingIndex >= 0 ? '编辑模板' : '新增模板' }}</h3>
          <button @click="showEditor = false" class="app-icon-button app-close-button">
            <Icon name="x" size="32rpx" />
          </button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="form-label">模板名称</label>
            <input v-model="draft.title" type="text" placeholder-class="app-input-placeholder" placeholder="如 周末环湖" class="w-full input app-input" />
          </div>
          <div>
            <label class="form-label">模板简介</label>
            <textarea v-model="draft.desc" rows="2" placeholder-class="app-textarea-placeholder" placeholder="可填写路线特点、适用场景等" class="w-full input app-textarea resize-none"></textarea>
          </div>
          <div>
            <label class="form-label">建议天数</label>
            <input v-model.number="draft.days" type="number" min="1" max="30" placeholder-class="app-input-placeholder" placeholder="请输入建议天数，如 3" class="w-full input app-input" />
          </div>
        </div>
        <div class="pt-1 border-t border-slate-100">
          <div class="text-xs text-slate-500 mb-2">分日路书</div>
          <div v-for="(day, dIdx) in draft.schedule" :key="`day-${dIdx}`" class="bg-slate-50 rounded-xl p-3 mb-3 border border-slate-200 space-y-3">
            <div class="flex justify-between items-center">
              <span class="text-xs text-slate-500">Day {{ dIdx + 1 }}</span>
              <button @click="removeSchedule(dIdx)" class="app-icon-button w-8 h-8 text-slate-300 hover:text-red-400">
                <Icon name="trash-2" size="32rpx" />
              </button>
            </div>
            <div>
              <label class="form-label">当天标题</label>
              <input v-model="day.title" type="text" placeholder-class="app-input-placeholder" placeholder="如 城市 A 到城市 B" class="w-full input app-input" />
            </div>
            <div>
              <label class="form-label">当天里程</label>
              <input v-model.number="day.distance_km" type="number" min="0" placeholder-class="app-input-placeholder" placeholder="请输入预计里程，如 120 km" class="w-full input app-input" />
            </div>
            <div>
              <label class="form-label">当天描述</label>
              <textarea v-model="day.description" rows="2" placeholder-class="app-textarea-placeholder" placeholder="可填写途经点、住宿点、注意事项等" class="w-full input app-textarea resize-none"></textarea>
            </div>
          </div>
          <button @click="addSchedule" class="app-action-button w-full py-2 text-xs text-[#064e3b] bg-[#064e3b]/5 rounded-lg font-medium">新增一天路书</button>
        </div>
        <button
          @click="saveEditor"
          :disabled="saving"
          class="app-full-button w-full mt-2 bg-[#064e3b] text-white font-bold py-3 rounded-xl disabled:opacity-50"
        >
          {{ saving ? '保存中...' : '保存' }}
        </button>
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

type ScheduleItem = {
  day: number
  title: string
  distance_km: number | ''
  description: string
}

type TemplateItem = {
  id: string
  title: string
  desc?: string
  days: number | ''
  schedule: ScheduleItem[]
}


const items = ref<TemplateItem[]>([])
const saving = ref(false)
const showEditor = ref(false)
const editingIndex = ref(-1)
const draft = ref<TemplateItem>({
  id: '',
  title: '',
  desc: '',
  days: '',
  schedule: [{ day: 1, title: '', distance_km: '', description: '' }]
})

const uid = () => `${Date.now()}_${Math.random().toString(16).slice(2, 8)}`
const normalizeSchedule = (schedule: any, days = 1): ScheduleItem[] => {
  if (Array.isArray(schedule) && schedule.length > 0) {
    return schedule.map((s, idx) => ({
      day: idx + 1,
      title: s?.title || '',
      distance_km: s?.distance_km === '' || s?.distance_km === null || typeof s?.distance_km === 'undefined'
        ? ''
        : Number(s.distance_km),
      description: s?.description || ''
    }))
  }
  return Array.from({ length: Math.max(1, days) }, (_, i) => ({
    day: i + 1, title: '', distance_km: '', description: ''
  }))
}
const normalizeTemplate = (raw: any): TemplateItem => {
  const days = raw?.days === '' || raw?.days === null || typeof raw?.days === 'undefined'
    ? ''
    : Math.max(1, Number(raw.days || 1))
  return {
    id: raw?.id || uid(),
    title: raw?.title || '',
    desc: raw?.desc || raw?.note || '',
    days,
    schedule: normalizeSchedule(raw?.schedule, days === '' ? 1 : days)
  }
}

const openCreate = () => {
  editingIndex.value = -1
  draft.value = normalizeTemplate({ id: uid(), days: '' })
  showEditor.value = true
}

const openEdit = (idx: number) => {
  editingIndex.value = idx
  draft.value = normalizeTemplate(items.value[idx])
  showEditor.value = true
}

const openDetail = (id: string) => {
  router.push(`/profile/templates/${id}`)
}

const removeItem = async (idx: number) => {
  const ok = await confirmDialog('确认删除该模板吗？')
  if (!ok) return
  items.value.splice(idx, 1)
  await persist()
}

const load = async () => {
  const res = await api.getMyTemplates()
  if (res.status === 'success') {
    items.value = Array.isArray(res.data) ? res.data.map(normalizeTemplate) : []
  }
}

const persist = async () => {
  saving.value = true
  try {
    const payload = items.value
      .map(i => normalizeTemplate({ ...i, title: i.title.trim() }))
      .filter(i => i.title)
    const res = await api.saveMyTemplates(payload)
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
  const title = draft.value.title.trim()
  if (!title) {
    showError('请填写模板名称')
    return
  }
  const next: TemplateItem = {
    ...normalizeTemplate(draft.value),
    title,
    days: Math.max(1, Number(draft.value.days || draft.value.schedule.length || 1)),
    schedule: draft.value.schedule.map((s, idx) => ({
      day: idx + 1,
      title: (s.title || '').trim() || `第${idx + 1}天行程`,
      distance_km: Number(s.distance_km || 0),
      description: (s.description || '').trim() || '沿途骑行，按计划前往下一站。'
    }))
  }
  if (editingIndex.value >= 0) {
    items.value[editingIndex.value] = next
  } else {
    items.value.unshift(next)
  }
  await persist()
  showEditor.value = false
}

const addSchedule = () => {
  draft.value.schedule.push({
    day: draft.value.schedule.length + 1,
    title: '',
    distance_km: '',
    description: ''
  })
  draft.value.days = draft.value.schedule.length
}

const removeSchedule = (idx: number) => {
  if (draft.value.schedule.length <= 1) return
  draft.value.schedule.splice(idx, 1)
  draft.value.schedule = draft.value.schedule.map((s, i) => ({ ...s, day: i + 1 }))
  draft.value.days = draft.value.schedule.length
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

textarea.input {
  height: auto;
  min-height: 144rpx;
  line-height: 40rpx;
  padding-top: 20rpx;
  padding-bottom: 20rpx;
}

.form-label {
  display: block;
  margin-bottom: 8rpx;
  color: #64748b;
  font-size: 24rpx;
  font-weight: 600;
  line-height: 32rpx;
}
</style>

