<template>
	<view class="page-container" :style="{ paddingTop: navBarHeight + 'px' }">
		<!-- 顶部导航栏 -->
		<view class="navbar" :style="{ paddingTop: navBarPaddingTop, height: navBarHeight + 'px' }">
			<view class="nav-back" @click="goBack">
				<AppIcon name="chevron-left" :size="24" color="#fff" />
			</view>
			<text class="nav-title">个人信息详情</text>
			<view class="nav-placeholder"></view>
		</view>

		<!-- 加载中 -->
		<view v-if="loading" class="state-container">
			<view class="loading-spinner"></view>
			<text class="state-text">加载中...</text>
		</view>

		<!-- 错误 -->
		<view v-else-if="error" class="state-container">
			<AppIcon name="alert-triangle" :size="48" color="#FAAD14" :stroke-width="1.5" class="state-icon" />
			<text class="error-text">{{ errorMsg }}</text>
			<button class="retry-btn" @click="loadData">重新加载</button>
		</view>

		<!-- 详情内容 -->
		<scroll-view v-else class="detail-content" scroll-y :style="{ paddingBottom: detailBottomPadding + 'px' }">
			<!-- 基本信息 -->
			<view class="info-section">
				<text class="section-title">基本信息</text>
				<view class="info-card">
					<view class="info-row">
						<text class="info-label">姓名</text>
						<text class="info-value">{{ detail?.xm || detail?.name || authStore.userInfo?.name || '-' }}</text>
					</view>
					<view class="info-row">
						<text class="info-label">学号</text>
						<text class="info-value">{{ detail?.xh || detail?.userNo || authStore.userInfo?.userNo || '-' }}</text>
					</view>
					<view class="info-row">
						<text class="info-label">性别</text>
						<text class="info-value">{{ detail?.xbm || detail?.gender || '-' }}</text>
					</view>
					<view class="info-row">
						<text class="info-label">出生日期</text>
						<text class="info-value">{{ formatBirthday(detail?.csrq || detail?.birthday || authStore.userInfo?.birthday) }}</text>
					</view>
					<view class="info-row">
						<text class="info-label">身份证号</text>
						<text class="info-value">{{ maskIdCard(detail?.sfzh || detail?.idno) }}</text>
					</view>
				</view>
			</view>

			<!-- 学籍信息 -->
			<view class="info-section">
				<text class="section-title">学籍信息</text>
				<view class="info-card">
					<view class="info-row">
						<text class="info-label">学校</text>
						<text class="info-value">{{ detail?.xxmc || '湖南软件职业技术大学' }}</text>
					</view>
					<view class="info-row">
						<text class="info-label">学院</text>
						<text class="info-value">{{ detail?.xymc || detail?.academyName || authStore.userInfo?.academyName || '-' }}</text>
					</view>
					<view class="info-row">
						<text class="info-label">专业</text>
						<text class="info-value">{{ detail?.zymc || detail?.majorName || '-' }}</text>
					</view>
					<view class="info-row">
						<text class="info-label">班级</text>
						<text class="info-value">{{ detail?.bj || detail?.clsName || authStore.userInfo?.clsName || '-' }}</text>
					</view>
					<view class="info-row">
						<text class="info-label">入学年份</text>
						<text class="info-value">{{ detail?.rxnf || detail?.entranceYear || authStore.userInfo?.entranceYear || '-' }}</text>
					</view>
				</view>
			</view>
		</scroll-view>

		<!-- 凭证过期弹窗 -->
		<AppModal
			v-model:show="showExpiredModal"
			title="登录已过期"
			message="为了你的账号安全，请重新登录后继续查看"
			confirm-text="去登录"
			@confirm="handleExpired"
		/>
	</view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import AppModal from '@/components/AppModal.vue'
import AppIcon from '@/components/AppIcon.vue'
import { navBarHeight, navBarPaddingTop, safeAreaBottom } from '@/utils/layout'

const detailBottomPadding = safeAreaBottom + 16

const authStore = useAuthStore()

const loading = ref(true)
const error = ref(false)
const errorMsg = ref('')
const detail = ref(null)
const showExpiredModal = ref(false)

function formatBirthday(val) {
	if (!val) return '-'
	if (val.length === 8) {
		return `${val.slice(0,4)}-${val.slice(4,6)}-${val.slice(6,8)}`
	}
	return val
}

function maskIdCard(id) {
	if (!id) return '-'
	if (id.length < 8) return id
	return id.slice(0, 4) + '********' + id.slice(-4)
}

function goBack() {
	uni.navigateBack()
}

async function loadData() {
	loading.value = true
	error.value = false
	try {
		const data = await authStore.fetchUserDetail()
		if (data) {
			detail.value = data
		} else if (authStore.isLoggedIn) {
			const valid = await authStore.checkTokenValid()
			if (!valid) {
				authStore.markTokenExpired()
				showExpiredModal.value = true
			} else {
				error.value = true
				errorMsg.value = '暂无个人信息数据'
			}
		} else {
			error.value = true
			errorMsg.value = '暂无个人信息数据'
		}
	} catch (e) {
		if (e.code === 401 || authStore.tokenExpired) {
			showExpiredModal.value = true
		} else if (authStore.isLoggedIn) {
			const valid = await authStore.checkTokenValid()
			if (!valid) {
				authStore.markTokenExpired()
				showExpiredModal.value = true
			} else {
				error.value = true
				errorMsg.value = e.message || '网络请求失败'
			}
		} else {
			error.value = true
			errorMsg.value = e.message || '网络请求失败'
		}
	} finally {
		loading.value = false
	}
}

function handleExpired() {
	showExpiredModal.value = false
	authStore.clearAuth()
	// 延迟跳转，让弹窗收起动画完整播放
	setTimeout(() => {
		uni.redirectTo({ url: '/pages/login/login' })
	}, 180)
}

onMounted(() => {
	loadData()
})
</script>

<style scoped>
.page-container {
	min-height: 100vh;
	background: #F5F6FA;
	display: flex;
	flex-direction: column;
}

.navbar {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	z-index: 100;
	box-sizing: border-box;
	background: linear-gradient(135deg, #4A90D9, #6BA8E8);
	padding-left: 16px;
	padding-right: 16px;
	display: flex;
	align-items: center;
}

.nav-back {
	width: 32px;
	height: 32px;
	display: flex;
	align-items: center;
	justify-content: center;
	color: #fff;
}

.nav-title {
	flex: 1;
	text-align: center;
	font-size: 17px;
	font-weight: 600;
	color: #fff;
}

.nav-placeholder {
	width: 32px;
}

.state-container {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 60px 20px;
}

.loading-spinner {
	width: 36px;
	height: 36px;
	border: 3px solid #e0e0e0;
	border-top-color: #4A90D9;
	border-radius: 50%;
	animation: spin 0.8s linear infinite;
	margin-bottom: 16px;
}

@keyframes spin {
	to { transform: rotate(360deg); }
}

.state-text {
	font-size: 14px;
	color: #999;
}

.state-icon {
	margin-bottom: 16px;
}

.error-text {
	font-size: 16px;
	color: #666;
	margin-bottom: 24px;
}

.retry-btn {
	background: #4A90D9;
	color: #fff;
	border: none;
	border-radius: 20px;
	padding: 10px 32px;
	font-size: 14px;
}

.detail-content {
	flex: 1;
	padding: 12px;
	overflow-x: hidden;
}

.info-section {
	margin-bottom: 16px;
}

.section-title {
	font-size: 14px;
	font-weight: 600;
	color: #666;
	margin-bottom: 8px;
	padding-left: 4px;
	display: block;
}

.info-card {
	background: #fff;
	border-radius: 12px;
	overflow: hidden;
}

.info-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 14px 16px;
	border-bottom: 1px solid #f5f5f5;
}

.info-row:last-child {
	border-bottom: none;
}

.info-label {
	flex-shrink: 0;
	white-space: nowrap;
	font-size: 14px;
	color: #999;
}

.info-value {
	flex: 1;
	min-width: 0;
	font-size: 14px;
	color: #333;
	text-align: right;
	margin-left: 16px;
	word-break: break-all;
	overflow-wrap: break-word;
}
</style>
