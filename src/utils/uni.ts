export function showError(title: string) {
  uni.showToast({
    title,
    icon: 'none',
    duration: 2200,
  })
}

export function showSuccess(title: string) {
  uni.showToast({
    title,
    icon: 'success',
    duration: 1800,
  })
}

export function confirmDialog(content: string, title = '提示') {
  return new Promise<boolean>((resolve) => {
    uni.showModal({
      title,
      content,
      success: (res) => resolve(!!res.confirm),
      fail: () => resolve(false),
    })
  })
}
