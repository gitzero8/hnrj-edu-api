import { useAuthStore } from '@/store/auth'

// const BASE_URL = 'http://10.201.84.39:5000' // 备选本地API接口服务（当官方API接口失效时应急使用）
const BASE_URL = 'http://222.243.161.213:81/hnrjzyxyhd'


/**
 * 判定是否为登录态失效
 * 后端在 token 失效时返回 HTTP 500，业务码藏在响应体中：
 *   { "code": "401", "Msg": "非法访问：/xxx", "data": "" }
 * 因此不能只看 HTTP 状态码，必须同时检查响应体 code。
 */
function isAuthFailure(statusCode, body) {
	if (statusCode === 401 || statusCode === 403) return true

	let code = ''
	if (body && typeof body === 'object') {
		if (body.code !== undefined && body.code !== null) {
			code = String(body.code)
		}
	} else if (typeof body === 'string' && body) {
		const matched = body.match(/"code"\s*:\s*"?(\d+)"?/)
		code = matched ? matched[1] : ''
	}
	return code === '401' || code === '403'
}

/**
 * 统一请求封装（uni-app版）
 * APP端 uni.request 不受CORS限制，可直接请求后端
 * @param {Object} config - 请求配置
 * @param {string} config.url - 接口路径
 * @param {Object} config.params - URL查询参数
 * @param {number} config.timeout - 超时时间（毫秒）
 */
function request(config) {
	return new Promise((resolve, reject) => {
		const authStore = useAuthStore()

		// 构建URL
		let url = BASE_URL + config.url
		if (config.params) {
			const params = []
			Object.entries(config.params).forEach(([key, value]) => {
				if (value !== undefined && value !== null && value !== '') {
					params.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
				}
			})
			if (params.length > 0) {
				url += (url.includes('?') ? '&' : '?') + params.join('&')
			}
		}

		// 请求头
		const header = {}
		if (authStore.token) {
			header['token'] = authStore.token
		}

		uni.request({
			url,
			method: 'POST',
			header,
			timeout: config.timeout || 15000,
			success: (res) => {
				// 登录态失效：清除凭证并统一以 code 401 抛出，页面据此弹窗提示
				if (isAuthFailure(res.statusCode, res.data)) {
					authStore.markTokenExpired()
					reject({ code: 401, message: '登录已过期，请重新登录' })
					return
				}
				if (res.statusCode >= 200 && res.statusCode < 300) {
					resolve(res.data)
				} else {
					// 非登录态异常：优先透传后端 Msg，便于定位问题
					const msg = (res.data && typeof res.data === 'object' && res.data.Msg)
						|| `请求失败(${res.statusCode})`
					reject({ code: res.statusCode, message: msg, data: res.data })
				}
			},
			fail: (err) => {
				if (err.errMsg && err.errMsg.includes('timeout')) {
					reject({ code: 'TIMEOUT', message: '请求超时，请检查网络' })
				} else {
					console.log(err)
					reject({ code: 'NETWORK_ERROR', message: '网络连接失败，请检查网络设置' })
				}
			}
		})
	})
}

export default request
