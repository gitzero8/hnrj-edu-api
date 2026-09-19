<template>
	<view class="tab-bar" :style="{ paddingBottom: safeAreaBottom + 'px' }">
		<view class="tab-item" :class="{ active: activeTab === 'schedule' }" @click="switchTab('schedule')">
			<AppIcon
				name="calendar"
				:size="23"
				:color="activeTab === 'schedule' ? '#4A90D9' : '#999999'"
				:stroke-width="activeTab === 'schedule' ? 2.2 : 1.8"
			/>
			<text class="tab-label">课表</text>
		</view>
		<view class="tab-item" :class="{ active: activeTab === 'grades' }" @click="switchTab('grades')">
			<AppIcon
				name="file-text"
				:size="23"
				:color="activeTab === 'grades' ? '#4A90D9' : '#999999'"
				:stroke-width="activeTab === 'grades' ? 2.2 : 1.8"
			/>
			<text class="tab-label">成绩</text>
		</view>
		<view class="tab-item" :class="{ active: activeTab === 'profile' }" @click="switchTab('profile')">
			<AppIcon
				name="user"
				:size="23"
				:color="activeTab === 'profile' ? '#4A90D9' : '#999999'"
				:stroke-width="activeTab === 'profile' ? 2.2 : 1.8"
			/>
			<text class="tab-label">我的</text>
		</view>
	</view>
</template>

<script setup>
import { useAuthStore } from '@/store/auth'
import { safeAreaBottom } from '@/utils/layout'
import AppIcon from '@/components/AppIcon.vue'

const props = defineProps({
	activeTab: {
		type: String,
		default: 'schedule'
	}
})

const authStore = useAuthStore()

function switchTab(tab) {
	const urlMap = {
		schedule: '/pages/schedule/schedule',
		grades: '/pages/grades/grades',
		profile: '/pages/profile/profile'
	}
	if (tab === props.activeTab) return
	uni.redirectTo({ url: urlMap[tab] })
}
</script>

<style scoped>
.tab-bar {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	height: 56px;
	background: #fff;
	display: flex;
	border-top: 1px solid #eee;
	z-index: 100;
}

.tab-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	color: #999;
}

.tab-item.active {
	color: #4A90D9;
}

.tab-label {
	margin-top: 3px;
	font-size: 11px;
}
</style>
