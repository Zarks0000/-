/**
 * UniApp 路由跳转适配器
 * 兼容旧 H5 路径，统一映射到 `pages.json` 中声明的页面。
 */

const tabBarPages = [
  '/pages/HomePage',
  '/pages/RoutePage',
  '/pages/ExplorePage',
  '/pages/ProfilePage',
]

const authPage = '/pages/AuthPage'

type RouteMatcher = {
  pattern: RegExp
  toUrl: (...matches: string[]) => string
}

const legacyRoutes: RouteMatcher[] = [
  { pattern: /^\/$/, toUrl: () => '/pages/HomePage' },
  { pattern: /^\/auth$/, toUrl: () => '/pages/AuthPage' },
  { pattern: /^\/home$/, toUrl: () => '/pages/HomePage' },
  { pattern: /^\/route$/, toUrl: () => '/pages/RoutePage' },
  { pattern: /^\/route\/([^/?#]+)$/, toUrl: (id) => `/pages/RouteDetailPage?id=${encodeURIComponent(id)}` },
  { pattern: /^\/suggestions$/, toUrl: () => '/pages/SuggestionPage' },
  { pattern: /^\/templates$/, toUrl: () => '/pages/TemplateListPage' },
  { pattern: /^\/template\/([^/?#]+)$/, toUrl: (id) => `/pages/TemplateDetailPage?id=${encodeURIComponent(id)}` },
  { pattern: /^\/routes$/, toUrl: () => '/pages/RouteListPage' },
  { pattern: /^\/knowledge$/, toUrl: () => '/pages/KnowledgeListPage' },
  { pattern: /^\/knowledge\/([^/?#]+)$/, toUrl: (id) => `/pages/KnowledgeDetailPage?id=${encodeURIComponent(id)}` },
  { pattern: /^\/tool\/restriction$/, toUrl: () => '/pages/ToolRestrictionPage' },
  { pattern: /^\/tool\/weather$/, toUrl: () => '/pages/ToolWeatherPage' },
  { pattern: /^\/tool\/equipment$/, toUrl: () => '/pages/ToolEquipmentPage' },
  { pattern: /^\/tool\/budget$/, toUrl: () => '/pages/ToolBudgetPage' },
  { pattern: /^\/profile$/, toUrl: () => '/pages/ProfilePage' },
  { pattern: /^\/profile\/vehicles$/, toUrl: () => '/pages/ProfileVehiclesPage' },
  { pattern: /^\/profile\/equipments$/, toUrl: () => '/pages/ProfileEquipmentsPage' },
  { pattern: /^\/profile\/templates$/, toUrl: () => '/pages/ProfileTemplatesPage' },
  {
    pattern: /^\/profile\/templates\/([^/?#]+)$/,
    toUrl: (id) => `/pages/ProfileTemplateDetailPage?id=${encodeURIComponent(id)}`,
  },
  { pattern: /^\/profile\/history$/, toUrl: () => '/pages/ProfileHistoryPage' },
  { pattern: /^\/profile\/privacy$/, toUrl: () => '/pages/ProfilePrivacyPage' },
  { pattern: /^\/profile\/help$/, toUrl: () => '/pages/ProfileHelpPage' },
  { pattern: /^\/profile\/about$/, toUrl: () => '/pages/ProfileAboutPage' },
]

function normalizePath(path: string): string {
  const raw = path.startsWith('/') ? path : `/${path}`
  if (raw.startsWith('/pages/')) {
    return raw
  }

  const [pathname, search = ''] = raw.split('?')
  for (const route of legacyRoutes) {
    const matched = pathname.match(route.pattern)
    if (!matched) continue
    const nextUrl = route.toUrl(...matched.slice(1))
    if (!search) return nextUrl
    return nextUrl.includes('?') ? `${nextUrl}&${search}` : `${nextUrl}?${search}`
  }

  return raw
}

function isTabBarUrl(url: string) {
  return tabBarPages.some(page => url === page || url.startsWith(`${page}?`))
}

function hasAuthToken() {
  return Boolean(uni.getStorageSync('vibe_auth_token'))
}

function shouldRequireAuth(url: string) {
  return !(url === authPage || url.startsWith(`${authPage}?`))
}

function redirectToAuthIfNeeded(url: string) {
  if (!shouldRequireAuth(url) || hasAuthToken()) return false
  uni.reLaunch({ url: authPage })
  return true
}

export const router = {
  push(path: string) {
    const url = normalizePath(path)
    if (redirectToAuthIfNeeded(url)) return
    // H5 预览阶段先关闭 tabBar 依赖，统一走普通页面导航。
    // #ifdef H5
    uni.navigateTo({ url })
    return
    // #endif
    if (isTabBarUrl(url)) {
      uni.switchTab({ url: url.split('?')[0] })
      return
    }
    uni.navigateTo({ url })
  },
  replace(path: string) {
    const url = normalizePath(path)
    if (redirectToAuthIfNeeded(url)) return
    // #ifdef H5
    uni.redirectTo({ url })
    return
    // #endif
    if (isTabBarUrl(url)) {
      uni.switchTab({ url: url.split('?')[0] })
      return
    }
    uni.redirectTo({ url })
  },
  back(delta = 1) {
    uni.navigateBack({ delta })
  },
}
