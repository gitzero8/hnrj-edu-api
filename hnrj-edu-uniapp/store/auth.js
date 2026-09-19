import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, validateToken, getUserDetail } from '@/api'

const TOKEN_KEY = 'hnrj_token'
const USER_KEY = 'hnrj_user'

// 统一读取本地缓存：兼容以对象或 JSON 字符串两种形式存入的数据
function readStorage(key) {
	try {
		const raw = uni.getStorageSync(key)
		if (!raw) return null
		return typeof raw === 'string' ? JSON.parse(raw) : raw
	} catch (e) {
		return null
	}
}

export const useAuthStore = defineStore('auth', () => {
	const token = ref(readStorage(TOKEN_KEY) || '')
	const userInfo = ref(readStorage(USER_KEY) || null)
	const userDetail = ref(null)
	const lastTokenCheck = ref(0)
	const tokenExpired = ref(false)

	const isLoggedIn = computed(() => !!token.value)

	// 节流验证：距离上次验证不足2分钟则跳过
	async function validateTokenThrottled() {
		if (!token.value) return false
		const now = Date.now()
		if (now - lastTokenCheck.value < 2 * 60 * 1000) {
			return true
		}
		const valid = await checkTokenValid()
		lastTokenCheck.value = now
		if (!valid) {
			tokenExpired.value = true
		}
		return valid
	}

	function setAuth(data) {
		token.value = data.token
		userInfo.value = {
			name: data.name,
			userNo: data.userNo,
			academyName: data.academyName,
			clsName: data.clsName,
			entranceYear: data.entranceYear,
			userType: data.userType,
			birthday: data.birthday
		}
		// 重新登录后清除上一次的过期标记
		tokenExpired.value = false
		lastTokenCheck.value = Date.now()
		uni.setStorageSync(TOKEN_KEY, JSON.stringify(data.token))
		uni.setStorageSync(USER_KEY, JSON.stringify(userInfo.value))
	}

	function clearAuth() {
		token.value = ''
		userInfo.value = null
		userDetail.value = null
		tokenExpired.value = false
		lastTokenCheck.value = 0
		uni.removeStorageSync(TOKEN_KEY)
		uni.removeStorageSync(USER_KEY)
	}

	/**
	 * 标记登录态已失效（区别于主动退出登录）
	 * 清除凭证的同时保留 tokenExpired 标记，供页面弹出"登录已过期"提示
	 */
	function markTokenExpired() {
		token.value = ''
		userInfo.value = null
		userDetail.value = null
		lastTokenCheck.value = 0
		tokenExpired.value = true
		uni.removeStorageSync(TOKEN_KEY)
		uni.removeStorageSync(USER_KEY)
	}

	async function login(userNo, password) {
		const res = await apiLogin(userNo, password)
		if (String(res.code) === '1' && res.data) {
			setAuth(res.data)
			return { success: true }
		}
		return { success: false, message: res.Msg || '登录失败' }
	}

	/**
	 * 校验登录态
	 * 返回 true  => 登录有效（含"无法判定"的网络异常，避免误登出）
	 * 返回 false => 明确失效（后端以 code 401 标识），调用方应提示并跳转登录
	 */
	async function checkTokenValid() {
		if (!token.value) return false
		try {
			const res = await validateToken()
			if (res && res.userNo) {
				if (res.token && res.token !== token.value) {
					token.value = res.token
					uni.setStorageSync(TOKEN_KEY, JSON.stringify(res.token))
				}
				return true
			}
			return false
		} catch (e) {
			// request 层已统一把登录态失效归一为 code 401
			if (e && String(e.code) === '401') {
				return false
			}
			// 网络超时、连接失败等无法判定登录态，保持当前登录状态
			return true
		}
	}

	async function fetchUserDetail() {
		try {
			const res = await getUserDetail()
			if (String(res.code) === '1' && res.data && res.data.length > 0) {
				userDetail.value = res.data[0]
				return userDetail.value
			}
			return null
		} catch (e) {
			// 登录态失效需向上抛出，交由页面统一弹窗提示
			if (e && String(e.code) === '401') throw e
			return null
		}
	}

	function logout() {
		clearAuth()
	}

	return {
		token,
		userInfo,
		userDetail,
		isLoggedIn,
		tokenExpired,
		lastTokenCheck,
		login,
		logout,
		checkTokenValid,
		validateTokenThrottled,
		fetchUserDetail,
		clearAuth,
		markTokenExpired
	}
})
