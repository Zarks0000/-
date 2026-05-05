import { createSSRApp } from 'vue'
import './style.css'
import App from './App.vue'
import { useUserStore } from '@/composables/useUserStore'

export function createApp() {
  const app = createSSRApp(App)
  
  // 在应用启动前初始化用户信息
  useUserStore().init()

  return {
    app,
  }
}
