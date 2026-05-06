﻿<template>
  <div class="h-full bg-slate-50 relative flex flex-col">
    <header class="app-safe-header h-24 pt-10 px-4 bg-white flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">隐私设置</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 space-y-4 pb-8">
      <section class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <h2 class="text-sm font-bold text-slate-800">账号与数据</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          我们仅在你登录后保存账号、车辆、装备、模板与历史行程数据，用于跨设备同步和行程回顾。
        </p>
        <div class="mt-3 space-y-2">
          <label class="flex items-center justify-between text-sm text-slate-700">
            <span>仅登录后保存我的数据</span>
            <input type="checkbox" checked disabled class="accent-emerald-700" />
          </label>
          <label class="flex items-center justify-between text-sm text-slate-700">
            <span>登录后同步我的模板与装备</span>
            <input type="checkbox" checked disabled class="accent-emerald-700" />
          </label>
        </div>
      </section>

      <section class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <h2 class="text-sm font-bold text-slate-800">权限说明</h2>
        <ul class="mt-2 text-xs text-slate-500 space-y-1 leading-relaxed">
          <li>定位权限：用于路线规划与天气查询的城市匹配。</li>
          <li>网络权限：用于请求天气、路况、禁摩等在线信息。</li>
          <li>本地存储：用于缓存登录状态与页面数据。</li>
        </ul>
      </section>

      <section class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <h2 class="text-sm font-bold text-slate-800">数据管理</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          如需清理本地缓存，可在微信小程序设置或开发者工具中清理缓存。若要永久删除账号数据，请通过“帮助与反馈”提交“账号删除申请”。
        </p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'


</script>
