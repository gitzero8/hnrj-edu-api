<template>
	<view class="page-container" :style="{ paddingTop: navBarHeight + 'px' }">
		<!-- 顶部导航栏 -->
		<view class="navbar" :style="{ paddingTop: navBarPaddingTop, height: navBarHeight + 'px' }">
			<text class="nav-title">成绩</text>
		</view>

		<!-- 未登录 -->
		<NotLoggedIn v-if="!authStore.isLoggedIn" />

		<template v-else>
			<!-- 学期筛选 -->
			<view class="filter-bar">
				<view class="filter-select" @click="showSemesterPicker = true">
					<text>{{ selectedSemesterName }}</text>
					<AppIcon name="chevron-down" :size="13" color="#999" />
				</view>
			</view>

			<!-- 加载中 -->
			<view v-if="loading" class="state-container">
				<view class="loading-spinner"></view>
				<text class="state-text">加载成绩中...</text>
			</view>

			<!-- 错误 -->
			<view v-else-if="error" class="state-container">
				<AppIcon name="alert-triangle" :size="48" color="#FAAD14" :stroke-width="1.5" class="state-icon" />
				<text class="error-text">{{ errorMsg }}</text>
				<button class="retry-btn" @click="loadData">重新加载</button>
			</view>

			<!-- 空状态 -->
			<view v-else-if="filteredGrades.length === 0" class="state-container">
				<AppIcon name="file-text" :size="48" color="#CCCCCC" :stroke-width="1.5" class="state-icon" />
				<text class="empty-text">
					{{ selectedSemester === 'all' ? '暂无成绩数据' : '该学期暂无成绩记录' }}
				</text>
			</view>

			<!-- 成绩列表 -->
			<scroll-view v-else class="grades-content" scroll-y :style="{ paddingBottom: pageBottomPadding + 'px' }">
				<view v-for="group in groupedGrades" :key="group.semester" class="semester-group">
					<view class="semester-header">
						<text class="semester-name">{{ group.semester }}</text>
						<text class="semester-count">{{ group.courses.length }}门</text>
					</view>
					<view class="grade-list">
						<view v-for="(course, idx) in group.courses" :key="idx" class="grade-card">
							<view class="grade-main">
								<view class="grade-info">
									<text class="grade-name">{{ course.courseName }}</text>
									<view class="grade-meta">
										<text class="meta-item">学分: {{ course.credit ?? '-' }}</text>
										<text class="meta-item">{{ course.examinationNature || course.examNature || course.khfs || '正常考试' }}</text>
									</view>
								</view>
								<view class="grade-score-wrap">
									<text class="grade-label">分数</text>
									<text class="grade-score" :class="getScoreClass(course.fraction)">{{ course.fraction ?? '-' }}</text>
								</view>
							</view>
						</view>
					</view>
				</view>
			</scroll-view>
		</template>

		<!-- 学期选择抽屉 -->
		<AppPicker
			v-model:show="showSemesterPicker"
			title="选择学期"
			mode="list"
			:options="semesterOptions"
			:model-value="selectedSemester"
			@select="onSemesterSelect"
		/>

		<!-- 凭证过期弹窗 -->
		<AppModal
			v-model:show="showExpiredModal"
			title="登录已过期"
			message="为了你的账号安全，请重新登录后继续查看"
			confirm-text="去登录"
			@confirm="handleExpired"
		/>

		<TabBar active-tab="grades" />
	</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAuthStore } from '@/store/auth'
import { getTermGPA, getSemesterList } from '@/api'
import TabBar from '@/components/TabBar.vue'
import AppModal from '@/components/AppModal.vue'
import AppPicker from '@/components/AppPicker.vue'
import AppIcon from '@/components/AppIcon.vue'
import NotLoggedIn from '@/components/NotLoggedIn.vue'
import { navBarHeight, navBarPaddingTop, pageBottomPadding } from '@/utils/layout'

const authStore = useAuthStore()

const loading = ref(true)
const error = ref(false)
const errorMsg = ref('')
const allGrades = ref([])
const semesterList = ref([])
const selectedSemester = ref('all')
const selectedSemesterName = ref('全部学期')
const showSemesterPicker = ref(false)
const showExpiredModal = ref(false)

// 兼容后端不同字段命名：semesterId/semesterName 为实际返回字段
function getSemesterId(sem) {
	return sem.semesterId || sem.id || sem.semester || ''
}

function getSemesterName(sem) {
	return sem.semesterName || sem.semester || sem.name || ''
}

// 成绩记录所属学期，兼容 curSemesterName / semester / xq
function getGradeSemester(grade) {
	return grade.curSemesterName || grade.semester || grade.xq || ''
}

const semesterOptions = computed(() => {
	const list = [{ label: '全部学期', value: 'all' }]
	semesterList.value.forEach(sem => {
		const id = getSemesterId(sem)
		if (!id) return
		list.push({ label: getSemesterName(sem), value: id })
	})
	return list
})

const filteredGrades = computed(() => {
	if (selectedSemester.value === 'all') return allGrades.value
	return allGrades.value.filter(g => getGradeSemester(g) === selectedSemester.value)
})

const groupedGrades = computed(() => {
	const map = {}
	filteredGrades.value.forEach(g => {
		const sem = getGradeSemester(g) || '未知学期'
		if (!map[sem]) map[sem] = []
		map[sem].push(g)
	})
	return Object.entries(map)
		.map(([semester, courses]) => ({ semester, courses }))
		.sort((a, b) => b.semester.localeCompare(a.semester))
})

function getScoreClass(score) {
	const s = Number(score)
	if (isNaN(s)) return ''
	if (s >= 90) return 'score-excellent'
	if (s >= 80) return 'score-good'
	if (s >= 60) return 'score-pass'
	return 'score-fail'
}

function onSemesterSelect(opt) {
	selectedSemester.value = opt.value
	selectedSemesterName.value = opt.label
}

async function loadData() {
	if (!authStore.isLoggedIn) return
	loading.value = true
	error.value = false
	try {
		const [gradeRes, semRes] = await Promise.all([
			getTermGPA(),
			getSemesterList()
		])

		if (String(gradeRes.code) === '1' && gradeRes.data && gradeRes.data.length > 0) {
			allGrades.value = gradeRes.data[0].achievement || []
		} else if (String(gradeRes.code) === '0') {
			throw new Error(gradeRes.Msg || '获取成绩失败')
		} else {
			if (authStore.isLoggedIn) {
				const valid = await authStore.checkTokenValid()
				if (!valid) {
					authStore.markTokenExpired()
					showExpiredModal.value = true
					return
				}
			}
			allGrades.value = []
		}

		if (String(semRes.code) === '1' && semRes.data) {
			semesterList.value = semRes.data
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
				errorMsg.value = e.message || '网络请求失败，请检查网络连接'
			}
		} else {
			error.value = true
			errorMsg.value = e.message || '网络请求失败，请检查网络连接'
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

// 使用页面级 onShow：从登录页返回时 onMounted 不会再次触发
let dataLoaded = false

onShow(() => {
	if (authStore.isLoggedIn) {
		if (dataLoaded) return
		dataLoaded = true
		loadData()
	} else {
		// 未登录 / 已退出：复位状态，保证下次登录后能重新加载
		dataLoaded = false
		loading.value = false
	}
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

.nav-title {
	font-size: 18px;
	font-weight: 600;
	color: #fff;
}

.filter-bar {
	background: #fff;
	padding: 12px 16px;
	border-bottom: 1px solid #eee;
}

.filter-select {
	display: flex;
	align-items: center;
	justify-content: space-between;
	background: #f5f5f5;
	padding: 10px 14px;
	border-radius: 8px;
	font-size: 14px;
	color: #333;
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

.empty-text {
	font-size: 15px;
	color: #999;
}

.retry-btn {
	background: #4A90D9;
	color: #fff;
	border: none;
	border-radius: 20px;
	padding: 10px 32px;
	font-size: 14px;
}

.grades-content {
	flex: 1;
	padding: 12px;
	overflow-x: hidden;
}

.semester-group {
	margin-bottom: 16px;
}

.semester-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 8px 4px;
}

.semester-name {
	flex: 1;
	min-width: 0;
	font-size: 15px;
	font-weight: 600;
	color: #333;
	word-break: break-all;
	overflow-wrap: break-word;
}

.semester-count {
	flex-shrink: 0;
	margin-left: 8px;
	font-size: 12px;
	color: #999;
}

.grade-list {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.grade-card {
	background: #fff;
	border-radius: 10px;
	padding: 14px;
}

.grade-main {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.grade-info {
	flex: 1;
	min-width: 0;
}

.grade-name {
	font-size: 15px;
	font-weight: 600;
	color: #333;
	margin-bottom: 6px;
	display: block;
	word-break: break-all;
	overflow-wrap: break-word;
}

.grade-meta {
	display: flex;
	flex-wrap: wrap;
	gap: 12px;
}

.meta-item {
	font-size: 12px;
	color: #999;
	word-break: break-all;
	overflow-wrap: break-word;
}

.grade-score-wrap {
	flex-shrink: 0;
	text-align: center;
	margin-left: 12px;
}

.grade-label {
	font-size: 11px;
	color: #999;
	display: block;
	margin-bottom: 2px;
}

.grade-score {
	font-size: 22px;
	font-weight: 700;
}

.score-excellent { color: #52C41A; }
.score-good { color: #4A90D9; }
.score-pass { color: #FAAD14; }
.score-fail { color: #F5222D; }
</style>
