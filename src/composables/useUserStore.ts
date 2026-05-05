import { reactive, computed } from 'vue'
import { api } from '@/api'

const state = reactive({
  isLoggedIn: false,
  isLoggingIn: false,
  token: '',
  userId: '',
  userInfo: {
    nickname: '游客',
    avatar: '',
    age: 0,
    totalDistance: 0,
    trips: 0,
    cities: 0,
    vehicles: 0,
    equipments: 0,
    templates: 0
  }
})

let ensureLoginPromise: Promise<boolean> | null = null

function readSavedProfile(raw: unknown) {
  if (!raw || typeof raw !== 'string') return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function showRequiredLoginModal(): Promise<void> {
  return new Promise((resolve) => {
    uni.showModal({
      title: '微信授权登录',
      content: '登录后才能使用摩旅客的行程规划、工具查询和个人数据功能。',
      showCancel: false,
      confirmText: '微信登录',
      success: () => resolve(),
      fail: () => resolve(),
    })
  })
}

function getWechatLoginCode(): Promise<string> {
  return new Promise((resolve, reject) => {
    uni.login({
      provider: 'weixin',
      success: (res) => {
        if (res.code) {
          resolve(res.code)
          return
        }
        reject(new Error('未获取到微信临时登录凭证'))
      },
      fail: (err) => {
        const detail = err as any
        reject(new Error(detail?.errMsg || '微信登录失败'))
      },
    })
  })
}

export function useUserStore() {
  const init = () => {
    const token = uni.getStorageSync('vibe_auth_token')
    const userId = uni.getStorageSync('vibe_user_id')
    const saved = uni.getStorageSync('vibe_user_profile')
    const profile = readSavedProfile(saved)
    if (token && !String(token).startsWith('mt_')) {
      logout()
      return
    }
    if (token && userId && profile) {
      state.isLoggedIn = true
      state.token = token
      state.userId = userId
      state.userInfo = profile
    }
  }

  const refreshProfile = async () => {
    if (!state.isLoggedIn) return
    const res = await api.getMyProfile()
    if (res.status === 'success') {
      state.userInfo = res.data
      uni.setStorageSync('vibe_user_profile', JSON.stringify(res.data))
    }
  }

  const login = async (codeInput?: string, nicknameInput?: string) => {
    const code = (codeInput || '').trim()
    if (!code) {
      throw new Error('未获取到微信临时登录凭证')
    }
    const nickname = (nicknameInput || '').trim() || undefined
    const res = await api.wxLogin(code, nickname)
    if (res.status !== 'success') {
      throw new Error(res.message || '登录失败')
    }
    const { token, user_id, profile } = res.data
    state.isLoggedIn = true
    state.token = token
    state.userId = user_id
    state.userInfo = profile
    uni.setStorageSync('vibe_auth_token', token)
    uni.setStorageSync('vibe_user_id', user_id)
    uni.setStorageSync('vibe_user_profile', JSON.stringify(profile))
  }

  const loginWithWeChat = async () => {
    state.isLoggingIn = true
    try {
      const code = await getWechatLoginCode()
      await login(code, '微信用户')
      await refreshProfile()
    } finally {
      state.isLoggingIn = false
    }
  }

  const ensureLoggedIn = async (prompt = true) => {
    if (state.isLoggedIn) return true
    if (ensureLoginPromise) return ensureLoginPromise

    ensureLoginPromise = (async () => {
      if (prompt) {
        await showRequiredLoginModal()
      }
      await loginWithWeChat()
      return true
    })()

    try {
      return await ensureLoginPromise
    } finally {
      ensureLoginPromise = null
    }
  }

  const logout = () => {
    state.isLoggedIn = false
    state.isLoggingIn = false
    state.token = ''
    state.userId = ''
    state.userInfo = {
      nickname: '游客',
      avatar: '',
      age: 0,
      totalDistance: 0,
      trips: 0,
      cities: 0,
      vehicles: 0,
      equipments: 0,
      templates: 0
    }
    uni.removeStorageSync('vibe_auth_token')
    uni.removeStorageSync('vibe_user_id')
    uni.removeStorageSync('vibe_user_profile')
  }

  return {
    isLoggedIn: computed(() => state.isLoggedIn),
    isLoggingIn: computed(() => state.isLoggingIn),
    token: computed(() => state.token),
    userId: computed(() => state.userId),
    userInfo: computed(() => state.userInfo),
    init,
    refreshProfile,
    login,
    loginWithWeChat,
    ensureLoggedIn,
    logout
  }
}
