﻿<template>
  <div class="h-full app-page relative flex flex-col">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">隐私设置</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 space-y-4 pb-8">
      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">登录与数据使用</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          摩旅客需要微信授权登录后使用。我们使用微信返回的 OpenID 识别账号，用于保存你的行程、车辆、装备、模板和历史回顾数据。
        </p>
        <div class="mt-3 space-y-2">
          <label class="flex items-center justify-between text-sm text-slate-700">
            <span>使用微信登录态保护个人数据</span>
            <input type="checkbox" checked disabled class="accent-emerald-700" />
          </label>
          <label class="flex items-center justify-between text-sm text-slate-700">
            <span>行程与个人档案按账号隔离</span>
            <input type="checkbox" checked disabled class="accent-emerald-700" />
          </label>
        </div>
      </section>

      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">我们会使用哪些信息</h2>
        <ul class="mt-2 text-xs text-slate-500 space-y-1 leading-relaxed">
          <li>微信登录信息：用于换取 OpenID 并生成应用内登录状态。</li>
          <li>行程数据：用于路线规划、分日路书、待办提醒与历史回顾。</li>
          <li>车辆和装备：用于出发准备、装备计算和个人档案管理。</li>
          <li>城市与路线关键词：用于天气、禁摩、路线参考等在线查询。</li>
        </ul>
      </section>

      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">本地缓存与删除</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          小程序会在本地保存登录状态，便于下次快速进入。你可以在“我的”页面退出登录清除本地登录缓存。若需删除服务端账号及行程数据，请在“帮助与反馈”中提交“账号删除申请”。
        </p>
      </section>

      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">安全承诺</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          我们不会主动公开你的个人行程和车辆装备信息，也不会将你的反馈内容用于与产品支持无关的用途。第三方服务仅用于完成你主动发起的查询或规划请求。
        </p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'


</script>
