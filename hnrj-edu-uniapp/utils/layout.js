let sysInfo = {}

try {
	sysInfo = uni.getSystemInfoSync() || {}
} catch (e) {
	sysInfo = {}
}

export const statusBarHeight = sysInfo.statusBarHeight || 0

export const safeAreaBottom = (() => {
	const insets = sysInfo.safeAreaInsets
	if (insets && typeof insets.bottom === 'number') {
		return Math.max(insets.bottom, 0)
	}
	if (sysInfo.safeArea && typeof sysInfo.safeArea.bottom === 'number' && sysInfo.screenHeight) {
		return Math.max(sysInfo.screenHeight - sysInfo.safeArea.bottom, 0)
	}
	return 0
})()

export const navBarContentHeight = 44

export const navBarHeight = statusBarHeight + navBarContentHeight

export const tabBarContentHeight = 56

export const tabBarHeight = tabBarContentHeight + safeAreaBottom

export const pageBottomPadding = tabBarHeight + 16

export const navBarPaddingTop = statusBarHeight + 'px'
