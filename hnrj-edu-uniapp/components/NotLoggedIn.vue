<template>
	<view class="not-logged-in" :style="{ paddingBottom: (60 + tabBarHeight) + 'px' }">
		<view class="icon-wrapper">
			<AppIcon name="user" :size="38" color="#4A90D9" :stroke-width="1.5" />
		</view>
		<text class="title">请先登录查看完整内容</text>
		<button class="login-btn" @click="goLogin">去登录</button>
	</view>
</template>

<script setup>
import { tabBarHeight } from '@/utils/layout'
import AppIcon from '@/components/AppIcon.vue'

function goLogin() {
	const pages = getCurrentPages()
	const currentPage = pages[pages.length - 1]
	const redirect = '/' + currentPage.route
	uni.navigateTo({
		url: `/pages/login/login?redirect=${encodeURIComponent(redirect)}`
	})
}
</script>

<style scoped>
.not-logged-in {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 60px 40px;
}

.icon-wrapper {
	width: 80px;
	height: 80px;
	border-radius: 50%;
	background: rgba(74, 144, 217, 0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 20px;
}

.title {
	font-size: 15px;
	color: #666;
	margin-bottom: 24px;
}

.login-btn {
	background: linear-gradient(135deg, #4A90D9, #6BA8E8);
	color: #fff;
	border: none;
	border-radius: 22px;
	font-size: 15px;
	font-weight: 600;
	padding: 10px 40px;
	min-height: 44px;
	display: flex;
	align-items: center;
	justify-content: center;
}
</style>
