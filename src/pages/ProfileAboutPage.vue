﻿<template>
  <div class="h-full bg-slate-50 relative flex flex-col">
    <header class="app-safe-header h-24 pt-10 px-4 bg-white flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">关于摩旅工具</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 space-y-4 pb-8">
      <section class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <h2 class="text-sm font-bold text-slate-800">产品定位</h2>
        <p class="text-xs text-slate-600 mt-2 leading-relaxed">
          摩旅工具是一款面向摩托车旅行爱好者的行程规划与知识辅助工具，帮助你在出发前完成路线规划、预算估算、装备准备与风险排查。
        </p>
      </section>

      <section class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <h2 class="text-sm font-bold text-slate-800">核心功能</h2>
        <ul class="mt-2 text-xs text-slate-600 space-y-1 leading-relaxed">
          <li>路线规划：按起终点生成行程，并支持分日路书编辑。</li>
          <li>发现页面：提供场景模板、精选路线与摩旅知识。</li>
          <li>实用工具：天气查询、禁摩查询、预算估算、装备建议。</li>
          <li>个人中心：账号隔离保存车辆、装备、模板与历史回顾。</li>
        </ul>
      </section>

      <section class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <h2 class="text-sm font-bold text-slate-800">版本信息</h2>
        <p class="text-xs text-slate-500 mt-2">当前版本：v0.1.0（开发版）</p>
        <p class="text-xs text-slate-500 mt-1">适用环境：微信小程序与移动端 H5 场景</p>
      </section>

      <section class="bg-white rounded-2xl shadow-sm border border-slate-100 p-4">
        <h2 class="text-sm font-bold text-slate-800">免责声明</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          应用内路线、天气、政策与预算信息仅供出行参考，实际骑行请遵守当地交通法规，并结合实时路况、天气与身体状态谨慎决策。
        </p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'


</script>
