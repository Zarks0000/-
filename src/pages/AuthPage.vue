<template>
  <div class="h-full app-page relative flex flex-col items-center justify-center px-8 text-center">
    <div class="w-20 h-20 rounded-[28rpx] bg-[#064e3b] text-white flex items-center justify-center shadow-[8rpx_8rpx_0_rgba(18,24,21,0.12)]">
      <Icon name="bike" size="72rpx" class="brightness-0 invert" />
    </div>
    <h1 class="mt-6 text-2xl font-black text-slate-900">摩旅客</h1>
    <p class="mt-2 text-sm leading-relaxed text-slate-500">
      登录后使用行程规划、路线工具和个人数据同步。
    </p>

    <button
      class="app-action-button app-primary-button mt-8 w-full max-w-[320px] py-3 rounded-2xl text-base font-bold"
      :disabled="userStore.isLoggingIn.value"
      @click="startLogin(false)"
    >
      {{ userStore.isLoggingIn.value ? '登录中...' : '微信授权登录' }}
    </button>

    <p v-if="errorMessage" class="mt-4 text-xs leading-relaxed text-red-500">
      {{ errorMessage }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import Icon from '@/components/Icon.vue'
import { useUserStore } from '@/composables/useUserStore'

const userStore = useUserStore()
const errorMessage = ref('')
const promptedOnce = ref(false)

const goHome = () => {
  uni.reLaunch({ url: '/pages/HomePage' })
}

const startLogin = async (prompt = true) => {
  if (userStore.isLoggedIn.value) {
    goHome()
    return
  }

  errorMessage.value = ''
  try {
    await userStore.ensureLoggedIn(prompt)
    goHome()
  } catch (e: any) {
    errorMessage.value = e?.message || '微信登录失败，请稍后重试'
    uni.showToast({ title: errorMessage.value, icon: 'none' })
  }
}

const ensureEntry = () => {
  if (userStore.isLoggedIn.value) {
    goHome()
    return
  }
  if (promptedOnce.value) return
  promptedOnce.value = true
  setTimeout(() => {
    startLogin(true)
  }, 120)
}

onMounted(ensureEntry)
onShow(ensureEntry)
</script>
