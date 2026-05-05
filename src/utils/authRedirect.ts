const AUTH_PAGE = 'pages/AuthPage'
const AUTH_PAGE_URL = `/${AUTH_PAGE}`

let redirectingToAuth = false

export function getAuthPageRoute() {
  return AUTH_PAGE
}

export function getCurrentPageRoute() {
  const pages = getCurrentPages()
  return pages[pages.length - 1]?.route || ''
}

export function redirectToAuthPage() {
  const currentRoute = getCurrentPageRoute()
  if (currentRoute === AUTH_PAGE) return false

  if (!currentRoute) {
    setTimeout(redirectToAuthPage, 80)
    return true
  }

  if (redirectingToAuth) return true

  redirectingToAuth = true
  uni.reLaunch({
    url: AUTH_PAGE_URL,
    complete: () => {
      setTimeout(() => {
        redirectingToAuth = false
      }, 80)
    },
  })
  return true
}
