﻿<template>
  <div class="h-full app-page relative flex flex-col">
    <!-- 1. 顶部个人信息卡 -->
    <header class="h-[236px] app-hero-header text-white pt-16 px-6 relative overflow-hidden shrink-0">
      <!-- 返回按钮 -->
      <button v-if="canGoBack" @click="router.back()" class="absolute left-4 app-safe-top-button top-12 z-20 w-8 h-8 flex items-center justify-center bg-white/10 rounded-full hover:bg-white/20 transition-colors">
        <Icon name="chevron-left" size="40rpx" class="brightness-0 invert" />
      </button>
      <!-- 背景装饰 -->
      <div class="absolute right-0 top-0 opacity-10 pointer-events-none">
        <svg class="w-64 h-64 -mr-10 -mt-10" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="100" fill="currentColor" />
        </svg>
      </div>
      <div class="absolute right-8 top-14 w-14 h-14 bg-white/10 rotate-45"></div>
      <div class="absolute right-24 bottom-8 w-16 h-16 rounded-full bg-white/10"></div>

      <div class="relative z-10 flex justify-between items-start">
        <div class="flex items-center">
          <div class="w-16 h-16 mr-5 bg-white rounded-2xl border-2 border-white/40 overflow-hidden shadow-[6rpx_6rpx_0_rgba(0,0,0,0.18)] flex items-center justify-center shrink-0">
            <Icon name="user" size="64rpx" class="opacity-80" />
          </div>
          <div v-if="userStore.isLoggedIn.value">
            <h2 class="text-xl font-bold">{{ userStore.userInfo.value.nickname }}</h2>
            <div class="flex space-x-2 mt-1.5">
              <span class="text-[10px] bg-white/20 px-2 py-0.5 rounded-full border border-white/10">摩龄 {{ userStore.userInfo.value.age }} 年</span>
              <span class="text-[10px] bg-white/20 px-2 py-0.5 rounded-full border border-white/10">{{ userStore.userInfo.value.trips }}次摩旅</span>
            </div>
          </div>
          <button v-else @click="handleLoginClick" class="m-0 p-0 bg-transparent border-0 rounded-none shadow-none cursor-pointer text-left flex flex-col items-start justify-start leading-normal">
            <h2 class="text-xl font-bold">点击登录/注册</h2>
            <p class="text-xs mt-1 text-emerald-100">登录后可保存和同步行程</p>
          </button>
        </div>
      </div>

      <!-- 2. 数据概览条 -->
      <div class="relative z-10 mt-8 flex justify-between px-2 bg-white/10 rounded-2xl border border-white/10 py-3">
        <div class="flex flex-col items-center">
          <span class="text-xl font-bold font-mono">{{ userStore.isLoggedIn.value ? userStore.userInfo.value.totalDistance : '-' }}</span>
          <span class="text-[10px] text-emerald-200 mt-0.5">累计里程(km)</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-xl font-bold font-mono">{{ userStore.isLoggedIn.value ? userStore.userInfo.value.trips : '-' }}</span>
          <span class="text-[10px] text-emerald-200 mt-0.5">完成摩旅</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-xl font-bold font-mono">{{ userStore.isLoggedIn.value ? userStore.userInfo.value.cities : '-' }}</span>
          <span class="text-[10px] text-emerald-200 mt-0.5">去过城市</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-xl font-bold font-mono">{{ userStore.isLoggedIn.value ? userStore.userInfo.value.vehicles : '-' }}</span>
          <span class="text-[10px] text-emerald-200 mt-0.5">登记车辆</span>
        </div>
      </div>
    </header>
    
    <main class="flex-1 min-h-0 overflow-y-auto hide-scrollbar pb-24 relative mt-4 z-20">
      <!-- 3. 核心模块入口 -->
      <section class="px-4">
        <div class="grid grid-cols-2 gap-3">
          <div @click="go('/profile/vehicles')" class="app-card p-4 rounded-2xl flex items-center space-x-3 cursor-pointer active:scale-[0.98] transition-transform">
            <div class="w-10 h-10 bg-indigo-50 rounded-2xl flex items-center justify-center shrink-0">
              <Icon name="bike" size="40rpx" />
            </div>
            <div>
              <h4 class="text-sm font-bold text-slate-800">我的车辆</h4>
              <p class="text-[10px] text-slate-400 mt-0.5">{{ userStore.isLoggedIn.value ? userStore.userInfo.value.vehicles + '辆车已登记' : '未登记车辆' }}</p>
            </div>
          </div>
          <div @click="go('/profile/equipments')" class="app-card p-4 rounded-2xl flex items-center space-x-3 cursor-pointer active:scale-[0.98] transition-transform">
            <div class="w-10 h-10 bg-slate-50 rounded-2xl flex items-center justify-center shrink-0">
              <Icon name="briefcase" size="40rpx" />
            </div>
            <div>
              <h4 class="text-sm font-bold text-slate-800">我的装备</h4>
              <p class="text-[10px] text-slate-400 mt-0.5">{{ userStore.isLoggedIn.value ? userStore.userInfo.value.equipments + '件装备档案' : '无装备档案' }}</p>
            </div>
          </div>
          <div @click="go('/profile/templates')" class="app-card p-4 rounded-2xl flex items-center space-x-3 cursor-pointer active:scale-[0.98] transition-transform">
            <div class="w-10 h-10 bg-emerald-50 rounded-2xl flex items-center justify-center shrink-0">
              <Icon name="file-text" size="40rpx" />
            </div>
            <div>
              <h4 class="text-sm font-bold text-slate-800">我的模板</h4>
              <p class="text-[10px] text-slate-400 mt-0.5">{{ userStore.isLoggedIn.value ? userStore.userInfo.value.templates + '个模板' : '无模板数据' }}</p>
            </div>
          </div>
          <div @click="go('/profile/history')" class="app-card p-4 rounded-2xl flex items-center space-x-3 cursor-pointer active:scale-[0.98] transition-transform">
            <div class="w-10 h-10 bg-purple-50 rounded-2xl flex items-center justify-center shrink-0">
              <Icon name="history" size="40rpx" />
            </div>
            <div>
              <h4 class="text-sm font-bold text-slate-800">历史回顾</h4>
              <p class="text-[10px] text-slate-400 mt-0.5">足迹与里程记录</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 4. 设置与辅助入口 -->
      <section class="mt-6 px-4">
        <div class="app-card rounded-2xl overflow-hidden">
          <button @click="router.push('/profile/privacy')" class="w-full px-4 py-4 flex items-center justify-between border-b border-slate-50 active:bg-slate-50 transition-colors">
            <div class="flex items-center space-x-3">
              <Icon name="shield" size="40rpx" />
              <span class="text-sm text-slate-700">隐私设置</span>
            </div>
            <Icon name="chevron-right" size="32rpx" />
          </button>
          <button @click="router.push('/profile/help')" class="w-full px-4 py-4 flex items-center justify-between border-b border-slate-50 active:bg-slate-50 transition-colors">
            <div class="flex items-center space-x-3">
              <Icon name="help-circle" size="40rpx" />
              <span class="text-sm text-slate-700">帮助与反馈</span>
            </div>
            <Icon name="chevron-right" size="32rpx" />
          </button>
          <button @click="router.push('/profile/about')" class="w-full px-4 py-4 flex items-center justify-between border-b border-slate-50 active:bg-slate-50 transition-colors">
            <div class="flex items-center space-x-3">
              <Icon name="info" size="40rpx" />
              <span class="text-sm text-slate-700">关于摩旅客</span>
            </div>
            <Icon name="chevron-right" size="32rpx" />
          </button>
        </div>
        
        <button v-if="userStore.isLoggedIn.value" @click="handleLogout" class="app-full-button w-full mt-4 bg-white py-3 rounded-xl text-red-500 text-sm font-bold shadow-sm border border-[#eadfd3] active:bg-slate-50 transition-colors">
          退出登录
        </button>
      </section>
    </main>

    <div
      v-if="showLogin"
      class="absolute inset-0 z-[70] bg-black/40 flex items-center justify-center p-4"
      @click.self="showLogin = false"
    >
      <div class="w-full max-w-[320px] app-card-strong rounded-2xl p-4">
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-bold text-slate-800">微信登录（开发态）</h3>
          <button @click="showLogin = false" class="app-icon-button app-close-button">
            <Icon name="x" size="32rpx" />
          </button>
        </div>
        <input
          v-model.trim="loginCode"
          type="text"
          placeholder-class="app-input-placeholder"
          placeholder="请输入 code（如 u1 / u2）"
          class="app-input w-full bg-slate-50 border border-slate-200 rounded-lg px-3 text-sm outline-none focus:border-emerald-600/60"
        />
        <input
          v-model.trim="loginNickname"
          type="text"
          placeholder-class="app-input-placeholder"
          placeholder="昵称（可选）"
          class="app-input w-full mt-2 bg-slate-50 border border-slate-200 rounded-lg px-3 text-sm outline-none focus:border-emerald-600/60"
        />
        <div class="mt-4 flex gap-2">
          <button @click="showLogin = false" class="flex-1 py-2 rounded-lg bg-slate-100 text-slate-600 text-sm flex items-center justify-center">取消</button>
          <button @click="onLogin" class="app-primary-button flex-1 py-2 rounded-lg text-sm font-bold flex items-center justify-center">登录</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Icon from '@/components/Icon.vue'
import { useUserStore } from '@/composables/useUserStore'
import { router } from '@/utils/router'
import { showError } from '@/utils/uni'
import { onMounted, ref } from 'vue'

const userStore = useUserStore()
const canGoBack = ref(false)
const showLogin = ref(false)
const loginCode = ref('')
const loginNickname = ref('')

const handleLoginClick = () => {
  onLogin()
}

const go = (path: string) => {
  if (!userStore.isLoggedIn.value) {
    showError('请先登录')
    return
  }
  router.push(path)
}

const onLogin = async () => {
  try {
    // #ifndef MP-WEIXIN
    if (!loginCode.value.trim()) {
      await userStore.ensureLoggedIn(true)
    } else {
      await userStore.login(loginCode.value, loginNickname.value)
      await userStore.refreshProfile()
    }
    showLogin.value = false
    loginCode.value = ''
    loginNickname.value = ''
    // #endif
    // #ifdef MP-WEIXIN
    await userStore.ensureLoggedIn(true)
    // #endif
  } catch (e: any) {
    uni.showToast({ title: e.message || '登录失败', icon: 'none' })
  }
}

const handleLogout = () => {
  userStore.logout()
  uni.reLaunch({ url: '/pages/AuthPage' })
}

onMounted(async () => {
  const pages = getCurrentPages()
  canGoBack.value = pages.length > 1
  if (userStore.isLoggedIn.value) {
    await userStore.refreshProfile()
  }
})
</script>

