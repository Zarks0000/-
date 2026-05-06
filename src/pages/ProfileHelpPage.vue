﻿<template>
  <div class="h-full bg-slate-50 relative flex flex-col">
    <header class="app-safe-header h-24 pt-10 px-4 bg-white flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">帮助与反馈</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 space-y-4 pb-8">
      <section class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <h2 class="text-sm font-bold text-slate-800">常见问题</h2>
        <div class="mt-3 space-y-3 text-xs text-slate-600">
          <div>
            <p class="font-semibold text-slate-700">1. 为什么预算估算有时失败？</p>
            <p class="mt-1">通常由网络波动或大模型超时导致，可重试或减少一次输入内容长度。</p>
          </div>
          <div>
            <p class="font-semibold text-slate-700">2. 为什么我的数据和别人不一样？</p>
            <p class="mt-1">系统按微信用户隔离账号，不同登录 code 对应不同账号数据。</p>
          </div>
          <div>
            <p class="font-semibold text-slate-700">3. 如何恢复误删模板？</p>
            <p class="mt-1">当前暂不支持回收站，请在删除前确认，建议先复制一份后再编辑。</p>
          </div>
        </div>
      </section>

      <section class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <h2 class="text-sm font-bold text-slate-800">问题反馈</h2>
        <p class="text-xs text-slate-500 mt-2">请尽量提供页面路径、操作步骤、错误截图和时间，便于快速定位。</p>
        <textarea
          v-model="feedback"
          rows="5"
          placeholder-class="app-textarea-placeholder"
          placeholder="请输入你的问题或建议..."
          class="app-textarea mt-3 w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm outline-none focus:border-emerald-600/60 resize-none"
        />
        <button
          @click="submitFeedback"
          class="app-full-button mt-3 w-full bg-[#064e3b] text-white text-sm font-bold py-2.5 rounded-lg"
        >
          提交反馈
        </button>
      </section>

      <section class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <h2 class="text-sm font-bold text-slate-800">联系方式</h2>
        <p class="text-xs text-slate-500 mt-2">反馈邮箱：support@mototrip.local（示例）</p>
        <p class="text-xs text-slate-500 mt-1">紧急问题请在反馈中注明“紧急”，我们会优先处理。</p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'
import { showError, showSuccess } from '@/utils/uni'


const feedback = ref('')

const submitFeedback = () => {
  if (!feedback.value.trim()) {
    showError('请先填写反馈内容')
    return
  }
  showSuccess('反馈已提交')
  feedback.value = ''
}
</script>
