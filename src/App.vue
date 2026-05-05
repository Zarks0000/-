<script setup lang="ts">
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'
import { useUserStore } from '@/composables/useUserStore'
import { initWxCloud } from '@/api'
import { getAuthPageRoute, getCurrentPageRoute, redirectToAuthPage } from '@/utils/authRedirect'

const userStore = useUserStore()

const AUTH_PAGE = getAuthPageRoute()

const redirectToAuthIfNeeded = () => {
  userStore.init()
  if (userStore.isLoggedIn.value) return

  const currentRoute = getCurrentPageRoute()
  if (!currentRoute) {
    setTimeout(redirectToAuthIfNeeded, 80)
    return
  }
  if (currentRoute === AUTH_PAGE) return

  redirectToAuthPage()
}

onLaunch(() => {
  console.log('App Launch')
  initWxCloud()
  redirectToAuthIfNeeded()
})

onShow(() => {
  console.log('App Show')
  redirectToAuthIfNeeded()
})

onHide(() => {
  console.log('App Hide')
})
</script>

<style>
/* TailwindCSS 已在 style.css 中引入，此处无需重复引入 */

/* 微信小程序兼容的全局样式：只隐藏滚动条，不禁用滚动 */
.hide-scrollbar::-webkit-scrollbar {
  width: 0;
  height: 0;
  color: transparent;
  display: none;
}
</style>
