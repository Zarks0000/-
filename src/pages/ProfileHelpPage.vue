﻿<template>
  <div class="h-full app-page relative flex flex-col">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">帮助与反馈</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 space-y-4 pb-8">
      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">常见问题</h2>
        <div class="mt-3 space-y-3 text-xs text-slate-600">
          <div>
            <p class="font-semibold text-slate-700">1. 为什么必须先微信登录？</p>
            <p class="mt-1">摩旅客会保存行程、车辆、装备和模板数据，登录后才能确保这些内容只归属于你的账号。</p>
          </div>
          <div>
            <p class="font-semibold text-slate-700">2. 路线、天气和禁摩信息是否一定准确？</p>
            <p class="mt-1">这些信息来自在线接口和系统估算，仅供出行参考。出发前仍需结合实时路况、天气和当地交通规定确认。</p>
          </div>
          <div>
            <p class="font-semibold text-slate-700">3. 创建行程后还能调整路书吗？</p>
            <p class="mt-1">可以在行程详情中编辑分日安排、准备事项和路线信息。重要行程建议修改后再次检查每日里程。</p>
          </div>
          <div>
            <p class="font-semibold text-slate-700">4. 如何申请删除账号数据？</p>
            <p class="mt-1">请在下方反馈中写明“账号删除申请”，系统会将内容发送到指定邮箱处理。</p>
          </div>
        </div>
      </section>

      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">问题反馈</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          请尽量写清页面、操作步骤、错误提示和发生时间。提交后，文本会发送到邮箱 madingyinan@outlook.com。
        </p>
        <input
          v-model.trim="contact"
          type="text"
          placeholder-class="app-input-placeholder"
          placeholder="联系方式（选填，如微信号或邮箱）"
          class="app-input mt-3 w-full bg-slate-50 border border-slate-200 rounded-lg px-3 text-sm outline-none focus:border-emerald-600/60"
        />
        <textarea
          v-model="feedback"
          rows="5"
          placeholder-class="app-textarea-placeholder"
          placeholder="请输入你的问题或建议..."
          class="app-textarea mt-3 w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-emerald-600/60 resize-none"
        />
        <button
          @click="submitFeedback"
          :disabled="submitting"
          class="app-full-button mt-3 w-full bg-[#064e3b] text-white text-sm font-bold py-2.5 rounded-lg"
        >
          {{ submitting ? '发送中...' : '发送反馈' }}
        </button>
      </section>

      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">反馈处理说明</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          反馈内容仅用于定位问题、处理账号数据申请和改进产品体验。紧急问题请在开头注明“紧急”，并留下可联系到你的方式。
        </p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'
import { showError, showSuccess } from '@/utils/uni'
import { api } from '@/api'


const feedback = ref('')
const contact = ref('')
const submitting = ref(false)

const submitFeedback = async () => {
  const content = feedback.value.trim()
  if (!content) {
    showError('请先填写反馈内容')
    return
  }
  if (submitting.value) return

  submitting.value = true
  try {
    const res = await api.submitFeedback({
      content,
      contact: contact.value,
      page: 'ProfileHelpPage',
    })
    if (res.status !== 'success') {
      throw new Error(res.message || '发送失败')
    }
    showSuccess('反馈已发送')
    feedback.value = ''
    contact.value = ''
  } catch (e: any) {
    showError(e.message || '发送失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>
