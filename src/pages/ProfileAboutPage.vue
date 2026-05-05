﻿<template>
  <div class="h-full app-page relative flex flex-col">
    <header class="app-safe-header app-topbar h-24 pt-10 px-4 flex justify-between items-center sticky top-0 z-40 shrink-0 border-b border-slate-100">
      <button @click="router.back()" class="app-back-button -ml-2 text-slate-400 hover:text-slate-600">
        <Icon name="chevron-left" size="40rpx" />
      </button>
      <h1 class="text-base font-bold text-slate-800">关于摩旅客</h1>
      <div class="w-9"></div>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar p-4 space-y-4 pb-8">
      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">产品定位</h2>
        <p class="text-xs text-slate-600 mt-2 leading-relaxed">
          摩旅客是一款面向摩托车旅行爱好者的小程序，围绕出发前准备、途中信息查询和行程回顾，帮助骑行者把复杂的摩旅筹备整理成可执行的计划。
        </p>
      </section>

      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">你可以用它做什么</h2>
        <ul class="mt-2 text-xs text-slate-600 space-y-1 leading-relaxed">
          <li>规划行程：按起终点、途经点和日期生成路线与分日路书。</li>
          <li>出发准备：整理待办事项、车辆档案、装备清单和预算估算。</li>
          <li>查询信息：快速查看天气、禁摩政策、路线参考和摩旅知识。</li>
          <li>沉淀记录：用微信账号保存个人模板、历史回顾和行程资料。</li>
        </ul>
      </section>

      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">适用场景</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          适合周末短途、跨城骑行、长线摩旅和高原路线等场景。你可以从模板开始，也可以按自己的目的地创建专属计划。
        </p>
      </section>

      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">信息说明</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          应用内路线、天气、政策、预算和建议内容仅供参考。实际骑行前请以官方交通规定、实时天气路况、车辆状态和自身身体情况为准。
        </p>
      </section>

      <section class="app-card rounded-2xl p-4">
        <h2 class="text-sm font-bold text-slate-800">反馈邮箱</h2>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">
          产品问题、数据删除申请和功能建议可通过“帮助与反馈”提交，反馈文本会发送至 madingyinan@outlook.com。
        </p>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { router } from '@/utils/router'
import Icon from '@/components/Icon.vue'


</script>
