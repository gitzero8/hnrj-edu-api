<template>
	<view class="page-container" :style="{ paddingTop: navBarHeight + 'px' }">
		<!-- 顶部导航栏 -->
		<view class="navbar" :style="{ paddingTop: navBarPaddingTop, height: navBarHeight + 'px' }">
			<text class="nav-title">我的</text>
		</view>

		<!-- 未登录状态 -->
		<template v-if="!authStore.isLoggedIn">
			<view class="profile-guest">
				<view class="guest-avatar">
					<AppIcon name="user" :size="34" color="#fff" :stroke-width="1.6" />
				</view>
				<text class="guest-name">未登录</text>
				<text class="guest-desc">登录后查看个人信息</text>
				<button class="guest-btn" @click="goLogin">立即登录</button>
			</view>

			<view class="function-list">
				<view class="function-item" @click="goLogin">
					<view class="func-icon func-icon-blue">
						<AppIcon name="user" :size="19" color="#4A90D9" />
					</view>
					<text class="func-name">个人信息详情</text>
					<AppIcon name="chevron-right" :size="18" color="#CCCCCC" />
				</view>
			</view>
		</template>

		<!-- 已登录状态 -->
		<template v-else>
			<view class="profile-header">
				<view class="user-avatar">
					<text>{{ authStore.userInfo?.name?.charAt(0) || '学' }}</text>
				</view>
				<view class="user-info">
					<text class="user-name">{{ authStore.userInfo?.name || '加载中...' }}</text>
					<text class="user-no">学号：{{ authStore.userInfo?.userNo || '-' }}</text>
					<text class="user-class">{{ authStore.userInfo?.academyName || '' }} · {{ authStore.userInfo?.clsName || '' }}</text>
				</view>
			</view>

			<view class="function-list">
				<view class="function-item" @click="goProfileDetail">
					<view class="func-icon func-icon-blue">
						<AppIcon name="user" :size="19" color="#4A90D9" />
					</view>
					<text class="func-name">个人信息详情</text>
					<AppIcon name="chevron-right" :size="18" color="#CCCCCC" />
				</view>
				<view class="function-item" @click="showLogoutConfirm = true">
					<view class="func-icon func-icon-red">
						<AppIcon name="log-out" :size="19" color="#F5222D" />
					</view>
					<text class="func-name" style="color:#F5222D;">退出登录</text>
					<AppIcon name="chevron-right" :size="18" color="#CCCCCC" />
				</view>
			</view>
		</template>

		<!-- 底部版权 -->
		<view class="profile-footer" :style="{ paddingBottom: pageBottomPadding + 'px' }">
			<text>湖南软件职业技术大学提供技术支持</text>
			<text>软大查查 v1.0.0</text>
		</view>

		<!-- 退出登录确认弹窗 -->
		<AppModal
			v-model:show="showLogoutConfirm"
			type="danger"
			title="确认退出"
			message="退出后需重新登录才能查看课表和成绩"
			show-cancel
			cancel-text="取消"
			confirm-text="退出"
			@confirm="handleLogout"
		/>

		<!-- 凭证过期弹窗 -->
		<AppModal
			v-model:show="showExpiredModal"
			title="登录已过期"
			message="为了你的账号安全，请重新登录后继续查看"
			confirm-text="去登录"
			@confirm="handleExpired"
		/>

		<TabBar active-tab="profile" />
	</view>
</template>

<script setup>
import { ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/store/auth'
import TabBar from '@/components/TabBar.vue'
import AppModal from '@/components/AppModal.vue'
import AppIcon from '@/components/AppIcon.vue'
import { navBarHeight, navBarPaddingTop, pageBottomPadding } from '@/utils/layout'

const authStore = useAuthStore()

const showLogoutConfirm = ref(false)
const showExpiredModal = ref(false)

// 进入页面时主动验证token（我的页不发起业务API请求，需手动验证）
// 使用页面级 onShow，保证从登录页返回后也能重新校验
let tokenChecked = false

onShow(async () => {
	if (!authStore.isLoggedIn) {
		tokenChecked = false
		return
	}
	if (tokenChecked) return
	tokenChecked = true
	if (authStore.tokenExpired) return
	const valid = await authStore.checkTokenValid()
	if (!valid) {
		authStore.markTokenExpired()
		showExpiredModal.value = true
	}
})

function goLogin() {
	uni.navigateTo({ url: '/pages/login/login' })
}

function goProfileDetail() {
	uni.navigateTo({ url: '/pages/profile-detail/profile-detail' })
}

function handleLogout() {
	authStore.logout()
	// 延迟跳转，让弹窗收起动画完整播放
	setTimeout(() => {
		uni.redirectTo({ url: '/pages/schedule/schedule' })
	}, 180)
}

function handleExpired() {
	showExpiredModal.value = false
	authStore.clearAuth()
	// 延迟跳转，让弹窗收起动画完整播放
	setTimeout(() => {
		uni.redirectTo({ url: '/pages/login/login' })
	}, 180)
}
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

.nav-title {
	font-size: 18px;
	font-weight: 600;
	color: #fff;
}

.profile-guest {
	background: linear-gradient(135deg, #4A90D9, #6BA8E8);
	padding: 40px 20px 32px;
	display: flex;
	flex-direction: column;
	align-items: center;
	color: #fff;
}

.guest-avatar {
	width: 72px;
	height: 72px;
	border-radius: 50%;
	background: rgba(255,255,255,0.2);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 12px;
}

.guest-name {
	font-size: 20px;
	font-weight: 600;
	margin-bottom: 4px;
}

.guest-desc {
	font-size: 13px;
	opacity: 0.8;
	margin-bottom: 20px;
}

.guest-btn {
	background: #fff;
	color: #4A90D9;
	border: none;
	border-radius: 22px;
	font-size: 15px;
	font-weight: 600;
	padding: 10px 36px;
	min-height: 44px;
	display: flex;
	align-items: center;
	justify-content: center;
}

.profile-header {
	background: linear-gradient(135deg, #4A90D9, #6BA8E8);
	padding: 32px 20px 28px;
	display: flex;
	align-items: center;
}

.user-avatar {
	flex-shrink: 0;
	width: 60px;
	height: 60px;
	border-radius: 50%;
	background: rgba(255,255,255,0.25);
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 24px;
	color: #fff;
	font-weight: 600;
	margin-right: 16px;
}

.user-info {
	flex: 1;
	min-width: 0;
}

.user-name {
	font-size: 18px;
	font-weight: 600;
	color: #fff;
	display: block;
	margin-bottom: 4px;
	word-break: break-all;
	overflow-wrap: break-word;
}

.user-no {
	font-size: 13px;
	color: rgba(255,255,255,0.85);
	display: block;
	margin-bottom: 2px;
	word-break: break-all;
	overflow-wrap: break-word;
}

.user-class {
	font-size: 12px;
	color: rgba(255,255,255,0.7);
	word-break: break-all;
	overflow-wrap: break-word;
}

.function-list {
	background: #fff;
	margin: 12px;
	border-radius: 12px;
	overflow: hidden;
}

.function-item {
	display: flex;
	align-items: center;
	padding: 14px 16px;
	border-bottom: 1px solid #f5f5f5;
}

.function-item:last-child {
	border-bottom: none;
}

.func-icon {
	flex-shrink: 0;
	width: 36px;
	height: 36px;
	border-radius: 8px;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 12px;
}

.func-icon-blue {
	background: rgba(74,144,217,0.1);
}

.func-icon-red {
	background: rgba(245,34,45,0.1);
}

.func-name {
	flex: 1;
	min-width: 0;
	font-size: 15px;
	color: #333;
	word-break: break-all;
	overflow-wrap: break-word;
}

.profile-footer {
	margin-top: auto;
	padding: 20px;
	text-align: center;
}

.profile-footer text {
	display: block;
	font-size: 12px;
	color: #ccc;
	margin-bottom: 4px;
}
</style>
