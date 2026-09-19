<template>
	<view class="login-page">
		<view class="login-header" :style="{ paddingTop: headerPaddingTop + 'px' }">
			<view class="nav-back" :style="{ top: (statusBarHeight + 6) + 'px' }" @click="goBack">
				<AppIcon name="chevron-left" :size="24" color="#fff" />
			</view>
			<view class="logo-circle">
				<image class="logo-img" src="/static/icons/icon-1024.png" mode="aspectFit" />
			</view>
			<text class="app-title">软大查查</text>
			<text class="app-subtitle">由湖南软件职业技术大学提供技术支持</text>
		</view>

		<view class="login-form">
			<view class="form-item">
				<AppIcon name="user" :size="18" color="#9aa0a6" class="input-icon" />
				<input
					v-model="userNo"
					class="form-input"
					type="text"
					placeholder="请输入学号"
					maxlength="20"
					@confirm="handleLogin"
				/>
			</view>

			<view class="form-item">
				<AppIcon name="lock" :size="18" color="#9aa0a6" class="input-icon" />
				<input
					v-model="password"
					class="form-input"
					:password="!showPassword"
					placeholder="请输入密码"
					@confirm="handleLogin"
				/>
				<view class="input-suffix" @click="showPassword = !showPassword">
					<AppIcon :name="showPassword ? 'eye-off' : 'eye'" :size="18" color="#9aa0a6" />
				</view>
			</view>

			<view class="remember-row">
				<view class="remember-label" @click="rememberMe = !rememberMe">
					<view class="checkbox" :class="{ checked: rememberMe }">
						<AppIcon v-if="rememberMe" name="check" :size="11" color="#fff" :stroke-width="3" />
					</view>
					<text class="remember-text">记住密码</text>
				</view>
			</view>

			<button
				class="login-btn"
				:class="{ loading: loading }"
				:disabled="loading || !canSubmit"
				@click="handleLogin"
			>
				<text>{{ loading ? '登录中...' : '登 录' }}</text>
			</button>
		</view>

		<view class="login-footer" :style="{ paddingBottom: (safeAreaBottom + 20) + 'px' }">
			<text>本系统面向湖南软件职业技术大学在校学生使用</text>
			<text class="version">v1.0.0</text>
		</view>

		<!-- Toast -->
		<view v-if="toastVisible" class="toast">{{ toastMessage }}</view>
	</view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import AppIcon from '@/components/AppIcon.vue'
import { statusBarHeight, safeAreaBottom } from '@/utils/layout'

const headerPaddingTop = statusBarHeight + 36

const authStore = useAuthStore()

const userNo = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const loading = ref(false)
const toastVisible = ref(false)
const toastMessage = ref('')

const REMEMBER_KEY = 'hnrj_remember'

const canSubmit = computed(() => userNo.value.trim() && password.value.trim())

function goBack() {
	const pages = getCurrentPages()
	if (pages.length > 1) {
		uni.navigateBack()
	} else {
		uni.redirectTo({ url: '/pages/schedule/schedule' })
	}
}

onMounted(async () => {
	// 已有有效登录态时无需重复登录，直接返回
	if (authStore.isLoggedIn) {
		const valid = await authStore.checkTokenValid()
		if (valid) {
			goBack()
			return
		}
		authStore.clearAuth()
	}

	// 读取记住的密码
	try {
		const saved = uni.getStorageSync(REMEMBER_KEY)
		if (saved) {
			const data = JSON.parse(saved)
			userNo.value = data.userNo || ''
			password.value = data.password || ''
			rememberMe.value = true
		}
	} catch (e) {}
})

function showToast(msg) {
	toastMessage.value = msg
	toastVisible.value = true
	setTimeout(() => { toastVisible.value = false }, 2000)
}

function saveCredentials() {
	if (rememberMe.value) {
		uni.setStorageSync(REMEMBER_KEY, JSON.stringify({
			userNo: userNo.value,
			password: password.value
		}))
	} else {
		uni.removeStorageSync(REMEMBER_KEY)
	}
}

async function handleLogin() {
	if (!userNo.value.trim()) {
		showToast('请输入学号')
		return
	}
	if (!password.value.trim()) {
		showToast('请输入密码')
		return
	}

	loading.value = true
	try {
		const result = await authStore.login(userNo.value.trim(), password.value)
		if (result.success) {
			saveCredentials()
			showToast('登录成功')
			setTimeout(() => {
				goBack()
			}, 500)
		} else {
			showToast(result.message || '登录失败')
		}
	} catch (e) {
		showToast(e.message || '网络异常，请稍后重试')
	} finally {
		loading.value = false
	}
}
</script>

<style scoped>
.login-page {
	min-height: 100vh;
	background: #F5F6FA;
	display: flex;
	flex-direction: column;
	padding: 0 24px;
}

.login-header {
	position: relative;
	margin: 0 -24px;
	padding-left: 24px;
	padding-right: 24px;
	padding-bottom: 52px;
	display: flex;
	flex-direction: column;
	align-items: center;
	background: linear-gradient(180deg, #4A90D9 0%, #6BA8E8 100%);
}

.login-header::after {
	content: '';
	position: absolute;
	left: 0;
	right: 0;
	bottom: 0;
	height: 44px;
	background: linear-gradient(180deg, rgba(245,246,250,0) 0%, #F5F6FA 100%);
}

.nav-back {
	position: absolute;
	left: 8px;
	width: 36px;
	height: 36px;
	display: flex;
	align-items: center;
	justify-content: center;
	line-height: 1;
	color: #fff;
	z-index: 2;
}

.logo-circle {
	width: 72px;
	height: 72px;
	border-radius: 50%;
	background: rgba(255,255,255,0.25);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 16px;
}

.logo-img {
	width: 72px;
	height: 72px;
	border-radius: 50%;
}

.app-title {
	font-size: 24px;
	font-weight: 700;
	color: #fff;
	margin-bottom: 6px;
}

.app-subtitle {
	font-size: 13px;
	color: rgba(255,255,255,0.85);
}

.login-form {
	background: #fff;
	border-radius: 16px;
	padding: 28px 20px;
	box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.form-item {
	display: flex;
	align-items: center;
	border-bottom: 1px solid #f0f0f0;
	padding: 12px 0;
}

.input-icon {
	flex-shrink: 0;
	margin-right: 10px;
}

.form-input {
	flex: 1;
	min-width: 0;
	font-size: 15px;
	color: #333;
	height: 40px;
}

.input-suffix {
	flex-shrink: 0;
	display: flex;
	align-items: center;
	padding: 0 8px;
}

.remember-row {
	padding: 16px 0 20px;
}

.remember-label {
	display: flex;
	align-items: center;
}

.checkbox {
	width: 18px;
	height: 18px;
	border: 1.5px solid #ccc;
	border-radius: 4px;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 8px;
}

.checkbox.checked {
	background: #4A90D9;
	border-color: #4A90D9;
}

.remember-text {
	font-size: 14px;
	color: #666;
}

.login-btn {
	width: 100%;
	height: 46px;
	background: linear-gradient(135deg, #4A90D9, #6BA8E8);
	color: #fff;
	border: none;
	border-radius: 23px;
	font-size: 16px;
	font-weight: 600;
	display: flex;
	align-items: center;
	justify-content: center;
}

.login-btn[disabled] {
	opacity: 0.6;
}

.login-footer {
	margin-top: auto;
	padding-top: 30px;
	text-align: center;
}

.login-footer text {
	display: block;
	font-size: 12px;
	color: #999;
	margin-bottom: 4px;
}

.version {
	font-size: 11px !important;
	color: #ccc !important;
}

.toast {
	position: fixed;
	top: 50%;
	left: 50%;
	transform: translate(-50%, -50%);
	background: rgba(0,0,0,0.75);
	color: #fff;
	padding: 12px 24px;
	border-radius: 8px;
	font-size: 14px;
	z-index: 9999;
}
</style>
