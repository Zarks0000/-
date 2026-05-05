import { ref, watchEffect, onMounted, computed } from 'vue'

type Theme = 'light' | 'dark'

export function useTheme() {
  const theme = ref<Theme>('light')

  const getPreferredTheme = (): Theme => {
    const saved = uni.getStorageSync('theme') as Theme | null
    if (saved === 'light' || saved === 'dark') return saved
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light'
    }
    return 'light'
  }

  const applyTheme = (t: Theme) => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.remove('light', 'dark')
      document.documentElement.classList.add(t)
    }
    uni.setStorageSync('theme', t)
  }

  const toggleTheme = () => {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  onMounted(() => {
    theme.value = getPreferredTheme()
    applyTheme(theme.value)
  })

  watchEffect(() => {
    applyTheme(theme.value)
  })

  return {
    theme,
    toggleTheme,
    isDark: computed(() => theme.value === 'dark'),
  }
}
