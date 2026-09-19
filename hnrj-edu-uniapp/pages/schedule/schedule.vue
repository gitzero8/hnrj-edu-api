<template>
	<view class="page-container" :style="{ paddingTop: navBarHeight + 'px' }">
		<!-- 顶部导航栏 -->
		<view class="navbar" :style="{ paddingTop: navBarPaddingTop, height: navBarHeight + 'px' }">
			<text class="nav-title">课表</text>
			<view v-if="authStore.isLoggedIn" class="nav-right" @click="showWeekPicker = !showWeekPicker">
				<text>第{{ currentWeek }}周</text>
				<AppIcon name="chevron-down" :size="12" color="#fff" class="arrow" />
			</view>
		</view>

		<!-- 未登录 -->
		<NotLoggedIn v-if="!authStore.isLoggedIn" />

		<template v-else>
			<!-- 周次栏：与本周是否有课无关，始终保留，便于切换周次 -->
			<scroll-view v-if="!loading && !error" class="week-bar" scroll-x show-scrollbar="false">
				<view class="week-bar-inner">
					<view
						v-for="w in weeks"
						:key="w"
						class="week-item"
						:class="{
							active: currentWeek === Number(w),
							now: nowWeek === Number(w)
						}"
						@click="switchWeek(w)"
					>
						<text class="week-num">{{ w }}</text>
						<text class="week-label">周</text>
					</view>
				</view>
			</scroll-view>

			<!-- 加载中 -->
			<view v-if="loading" class="state-container">
				<view class="loading-spinner"></view>
				<text class="state-text">加载课表中...</text>
			</view>

			<!-- 错误 -->
			<view v-else-if="error" class="state-container">
				<AppIcon name="alert-triangle" :size="48" color="#FAAD14" :stroke-width="1.5" class="state-icon" />
				<text class="error-text">{{ errorMsg }}</text>
				<button class="retry-btn" @click="loadData">重新加载</button>
			</view>

			<!-- 空状态 -->
			<view v-else-if="weekCourses.length === 0" class="state-container">
				<AppIcon name="inbox" :size="48" color="#CCCCCC" :stroke-width="1.5" class="state-icon" />
				<text class="empty-text">本周暂无课程安排</text>
			</view>

			<!-- 课表内容 -->
			<scroll-view v-else class="schedule-content" scroll-y :style="{ paddingBottom: pageBottomPadding + 'px' }">
				<!-- 按天展示课程，每天再按上午 / 下午 / 晚上分段 -->
				<view class="days-container">
					<view v-for="day in weekDays" :key="day.id" class="day-section">
						<view class="day-header">
							<text class="day-name">{{ day.name }}</text>
							<text v-if="isCurrentWeek && day.id === todayWeekDay" class="today-badge">今天</text>
							<text v-if="daySlotMap[day.id].total > 0" class="day-count">{{ daySlotMap[day.id].total }}节课</text>
						</view>

						<view class="slot-list">
							<template v-for="slot in daySlotMap[day.id].slots" :key="slot.id">
								<!-- 有课程：完整时段卡片 -->
								<view v-if="slot.courses.length > 0" class="slot-block">
									<view class="slot-header">
										<AppIcon :name="slot.icon" :size="13" :color="slot.color" />
										<text class="slot-name">{{ slot.name }}</text>
										<text class="slot-count">{{ slot.courses.length }}节</text>
									</view>

									<view class="course-list">
										<view
											v-for="(course, idx) in slot.courses"
											:key="courseKey(course, idx)"
											class="course-card"
											:class="'card-' + slot.id"
											@click="toggleCourse(course, idx)"
										>
											<view class="course-main">
												<view class="course-info">
													<text class="course-name">{{ course.courseName }}</text>
													<view class="course-meta">
														<view class="meta-item">
															<AppIcon name="clock" :size="12" color="#8a8f99" />
															<text class="meta-text">{{ course.startTime }}-{{ course.endTIme }}</text>
														</view>
														<view class="meta-item">
															<AppIcon name="map-pin" :size="12" color="#8a8f99" />
															<text class="meta-text">{{ course.classroomName || course.location }}</text>
														</view>
													</view>
													<view class="course-teacher">
														<AppIcon name="teacher" :size="12" color="#999" />
														<text class="meta-text">{{ course.teacherName }}</text>
													</view>
												</view>
												<view class="course-side">
													<text v-if="getCourseStatus(course) === 'ongoing'" class="status-tag status-ongoing">正在上课...</text>
													<text v-else-if="getCourseStatus(course) === 'upcoming'" class="status-tag status-upcoming">即将开课...</text>
													<AppIcon
														name="chevron-down"
														:size="16"
														color="#B8BCC4"
														class="expand-arrow"
														:class="{ open: isExpanded(course, idx) }"
													/>
												</view>
											</view>
											<view v-if="isExpanded(course, idx)" class="course-detail">
												<view class="detail-row">
													<text class="detail-label">考核方式</text>
													<text class="detail-value">{{ course.khfs || '未知' }}</text>
												</view>
												<view class="detail-row">
													<text class="detail-label">上课周次</text>
													<text class="detail-value">{{ course.classWeek }}周</text>
												</view>
												<view v-if="course.xkrs" class="detail-row">
													<text class="detail-label">选课人数</text>
													<text class="detail-value">{{ course.xkrs }}人</text>
												</view>
												<view v-if="course.buildingName" class="detail-row">
													<text class="detail-label">教学楼</text>
													<text class="detail-value">{{ course.buildingName }}</text>
												</view>
												<view v-if="course.ktmc" class="detail-row">
													<text class="detail-label">上课班级</text>
													<text class="detail-value">{{ course.ktmc }}</text>
												</view>
											</view>
										</view>
									</view>
								</view>

								<!-- 无课程：压缩为单行细条，避免空时段占用整块卡片高度 -->
								<view v-else class="slot-empty-row">
									<AppIcon :name="slot.icon" :size="12" color="#C8CBD0" />
									<text class="slot-empty-name">{{ slot.name }}</text>
									<text class="slot-empty-text">无课程</text>
								</view>
							</template>
						</view>
					</view>
				</view>
			</scroll-view>
		</template>

		<!-- 周次选择抽屉 -->
		<AppPicker
			v-model:show="showWeekPicker"
			title="选择教学周"
			mode="grid"
			:options="weekOptions"
			:model-value="currentWeek"
			@select="onWeekSelect"
		/>

		<!-- 凭证过期弹窗 -->
		<AppModal
			v-model:show="showExpiredModal"
			title="登录已过期"
			message="为了你的账号安全，请重新登录后继续查看"
			confirm-text="去登录"
			@confirm="handleExpired"
		/>

		<TabBar active-tab="schedule" />
	</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow, onUnload } from '@dcloudio/uni-app'
import { useAuthStore } from '@/store/auth'
import { getTimeMode, getTeachingWeek, getCurriculum } from '@/api'
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
const allCourses = ref([])
const weeks = ref([])
const currentWeek = ref(1)
const kbjcmsid = ref('')
const expandedId = ref(null)
const showWeekPicker = ref(false)
const showExpiredModal = ref(false)
const isCurrentWeek = ref(true)
const nowTime = ref(Date.now())

let statusTimer = null
// 标记当前登录态下是否已完成首次加载，避免 onShow 重复触发请求
let dataLoaded = false

function startStatusTimer() {
	if (statusTimer) return
	statusTimer = setInterval(() => {
		nowTime.value = Date.now()
	}, 60000)
}

function stopStatusTimer() {
	if (statusTimer) {
		clearInterval(statusTimer)
		statusTimer = null
	}
}

const weekDays = [
	{ id: '1', name: '周一' },
	{ id: '2', name: '周二' },
	{ id: '3', name: '周三' },
	{ id: '4', name: '周四' },
	{ id: '5', name: '周五' },
	{ id: '6', name: '周六' },
	{ id: '7', name: '周日' }
]

// 作息分段：上午（12:00 前）/ 下午（12:00-18:00）/ 晚上（18:00 后）
const timeSlots = [
	{ id: 'morning', name: '上午', icon: 'sunrise', color: '#F59E0B' },
	{ id: 'afternoon', name: '下午', icon: 'sun', color: '#4A90D9' },
	{ id: 'evening', name: '晚上', icon: 'moon', color: '#7C6BD9' }
]

const todayWeekDay = computed(() => {
	const d = new Date().getDay()
	return d === 0 ? '7' : String(d)
})

const weekCourses = computed(() => {
	return allCourses.value.filter(c => {
		const weekDetails = (c.classWeekDetails || '').split(',').filter(Boolean)
		return weekDetails.includes(String(currentWeek.value))
	})
})

const weekOptions = computed(() => weeks.value.map(w => ({
	label: `第${w}周`,
	value: Number(w)
})))

/*
 * 按「天 × 时间段」预分组，模板中直接取用。
 * 模板里调用函数每次重渲染都会执行，课程较多时开销明显，故用 computed 缓存。
 * slots 用数组（而非以 id 为键的对象）以便模板直接 v-for。
 */
const daySlotMap = computed(() => {
	const map = {}
	weekDays.forEach(day => {
		const dayCourses = weekCourses.value.filter(c => c.weekDay === day.id)
		map[day.id] = {
			total: dayCourses.length,
			slots: timeSlots.map(slot => ({
				...slot,
				courses: dayCourses.filter(c => getTimeSlotId(c) === slot.id)
			}))
		}
	})
	return map
})

/*
 * 判断课程属于哪个时间段：
 * 以开始时间为准，12:00 前为上午、18:00 前为下午、之后为晚上。
 * startTime 缺失时退回按节次推断（1-4 节上午，5-8 节下午，9 节起晚上）。
 */
function getTimeSlotId(course) {
	const startMin = parseTime(course.startTime)
	if (!isNaN(startMin)) {
		const hour = Math.floor(startMin / 60)
		if (hour < 12) return 'morning'
		if (hour < 18) return 'afternoon'
		return 'evening'
	}

	const section = parseStartSection(course)
	if (section === null) return 'morning'
	if (section <= 4) return 'morning'
	if (section <= 8) return 'afternoon'
	return 'evening'
}

/*
 * 解析起始节次，兼容后端两种编码：
 * weekNoteDetail "103,104" → 首项 "103"（1 + 节次）→ 3
 * classTime "10304"       → "1" + 起始 "03" + 结束 "04" → 3
 */
function parseStartSection(course) {
	const note = String(course.weekNoteDetail || '').split(',')[0].trim()
	if (note) {
		const n = Number(note.replace(/\D/g, ''))
		if (!isNaN(n) && n > 0) {
			return n > 10 ? Number(String(n).slice(-2)) : n
		}
	}

	const code = String(course.classTime || '').replace(/\D/g, '')
	if (code.length >= 3) {
		const s = Number(code.slice(1, 3))
		if (!isNaN(s)) return s
	}
	return null
}

// 以 nowTime 为基准，使依赖它的 computed 能随定时器每分钟刷新（跨周时自动更新）
function calcCurrentWeek() {
	const now = new Date(nowTime.value)
	const year = now.getFullYear()
	let semesterStart = new Date(year, 8, 1)
	if (now < semesterStart) {
		semesterStart = new Date(year - 1, 8, 1)
	}
	const diff = Math.floor((now - semesterStart) / (7 * 24 * 60 * 60 * 1000))
	return Math.max(1, Math.min(diff + 1, 20))
}

// 真实当前教学周：始终用于周次栏标记，与用户手动选中的周次相互独立
const nowWeek = computed(() => calcCurrentWeek())

// 解析 "HH:MM" 为分钟数；无效输入返回 NaN，由调用方决定兜底策略
function parseTime(timeStr) {
	if (!timeStr) return NaN
	const [h, m] = String(timeStr).split(':').map(Number)
	if (isNaN(h)) return NaN
	return h * 60 + (isNaN(m) ? 0 : m)
}

function getCourseStatus(course) {
	if (!isCurrentWeek.value || course.weekDay !== todayWeekDay.value) return ''
	const now = new Date()
	const nowMin = now.getHours() * 60 + now.getMinutes()
	const startMin = parseTime(course.startTime)
	const endMin = parseTime(course.endTIme)

	if (nowMin >= startMin && nowMin < endMin) return 'ongoing'

	// 检查是否有正在上课的课程
	const hasOngoing = weekCourses.value.some(c => {
		if (c.weekDay !== todayWeekDay.value) return false
		const s = parseTime(c.startTime)
		const e = parseTime(c.endTIme)
		return nowMin >= s && nowMin < e
	})

	if (hasOngoing) return ''

	if (nowMin < startMin && (startMin - nowMin) <= 35) return 'upcoming'
	return ''
}

// 展开项的标识：课程 id 可能与同一时段内其他课程重名，拼接序号保证唯一
function courseKey(course, idx) {
	return course.jx0408id + '-' + idx
}

function isExpanded(course, idx) {
	return expandedId.value === courseKey(course, idx)
}

function toggleCourse(course, idx) {
	const key = courseKey(course, idx)
	expandedId.value = expandedId.value === key ? null : key
}

function switchWeek(w) {
	currentWeek.value = Number(w)
	isCurrentWeek.value = (currentWeek.value === calcCurrentWeek())
	expandedId.value = null
}

function onWeekSelect(opt) {
	switchWeek(opt.value)
}

async function loadData() {
	if (!authStore.isLoggedIn) return
	loading.value = true
	error.value = false
	try {
		if (!kbjcmsid.value) {
			const modeRes = await getTimeMode()
			if (String(modeRes.code) === '1' && modeRes.data && modeRes.data.length > 0) {
				kbjcmsid.value = modeRes.data[0].kbjcmsid
			} else {
				throw new Error('获取课表时间模式失败')
			}
		}

		if (weeks.value.length === 0) {
			const weekRes = await getTeachingWeek()
			if (String(weekRes.code) === '1' && weekRes.data) {
				weeks.value = weekRes.data.map(w => w.week)
			}
		}

		const res = await getCurriculum('all', kbjcmsid.value)
		if (String(res.code) === '1' && res.data && res.data.length > 0) {
			allCourses.value = res.data[0].courses || []
		} else if (String(res.code) === '0') {
			throw new Error(res.Msg || '获取课表失败')
		} else {
			if (authStore.isLoggedIn) {
				const valid = await authStore.checkTokenValid()
				if (!valid) {
					authStore.markTokenExpired()
					showExpiredModal.value = true
					return
				}
			}
			allCourses.value = []
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

// 使用页面级 onShow：从登录页返回时 onMounted 不会再次触发，
// 只有 onShow 能覆盖"未登录进入 → 去登录 → 返回"这一场景。
onShow(() => {
	if (authStore.isLoggedIn) {
		if (dataLoaded) return
		dataLoaded = true
		currentWeek.value = calcCurrentWeek()
		isCurrentWeek.value = true
		loadData()
		startStatusTimer()
	} else {
		// 未登录 / 已退出：复位状态，保证下次登录后能重新加载
		dataLoaded = false
		loading.value = false
		stopStatusTimer()
	}
})

onUnload(() => {
	stopStatusTimer()
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
	justify-content: space-between;
}

.nav-title {
	font-size: 18px;
	font-weight: 600;
	color: #fff;
}

.nav-right {
	display: flex;
	align-items: center;
	background: rgba(255,255,255,0.2);
	padding: 6px 12px;
	border-radius: 14px;
	font-size: 14px;
	color: #fff;
}

.arrow {
	margin-left: 4px;
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

.schedule-content {
	flex: 1;
	min-height: 0;
	overflow-x: hidden;
}

.week-bar {
	flex-shrink: 0;
	white-space: nowrap;
	background: #fff;
	padding: 10px 12px;
	border-bottom: 1px solid #eee;
}

.week-bar-inner {
	display: inline-flex;
}

.week-item {
	display: inline-flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 6px 14px;
	margin-right: 6px;
	border-radius: 10px;
	min-width: 44px;
	transition: background-color 0.2s ease;
}

.week-num {
	font-size: 16px;
	font-weight: 600;
	line-height: 1.25;
	color: #333;
}

.week-label {
	font-size: 11px;
	line-height: 1.25;
	color: #999;
}

/*
 * 当前周：淡蓝底 + 主色字，定位为「次级」标记，
 * 与选中周的实心蓝底拉开层次，二者不再争夺视觉焦点
 */
.week-item.now {
	background: #EAF3FC;
}

.week-item.now .week-num {
	color: #4A90D9;
}

.week-item.now .week-label {
	color: #8FBBE5;
}

/*
 * 选中周：实心蓝底白字，优先级高于「当前周」
 * 同特异性选择器后者覆盖前者，故 .active 必须排在 .now 之后
 */
.week-item.active {
	background: #4A90D9;
}

.week-item.active .week-num {
	color: #fff;
}

.week-item.active .week-label {
	color: rgba(255,255,255,0.8);
}

.days-container {
	padding: 12px;
}

.day-section {
	margin-bottom: 16px;
}

.day-header {
	display: flex;
	align-items: center;
	margin-bottom: 8px;
	padding-left: 4px;
}

.day-name {
	flex-shrink: 0;
	font-size: 15px;
	font-weight: 600;
	color: #333;
}

.today-badge {
	font-size: 11px;
	color: #fff;
	background: #4A90D9;
	padding: 2px 8px;
	border-radius: 10px;
	margin-left: 8px;
}

.day-count {
	font-size: 12px;
	color: #999;
	margin-left: auto;
}

/* 时段容器：上午 / 下午 / 晚上 */
.slot-list {
	display: flex;
	flex-direction: column;
	gap: 6px;
}

.slot-block {
	background: #fff;
	border-radius: 12px;
	padding: 10px 12px;
}

.slot-header {
	display: flex;
	align-items: center;
	margin-bottom: 8px;
}

.slot-name {
	flex-shrink: 0;
	margin-left: 5px;
	font-size: 13px;
	font-weight: 600;
	color: #333;
}

.slot-count {
	margin-left: auto;
	font-size: 11px;
	color: #999;
}

/*
 * 无课程的时段：不渲染整块卡片，压缩为一行细条（约 26px），
 * 既保留「上午 / 下午 / 晚上」三段结构，又不让空白占据屏幕
 */
.slot-empty-row {
	display: flex;
	align-items: center;
	padding: 5px 12px;
	background: #fff;
	border-radius: 8px;
}

.slot-empty-name {
	margin-left: 5px;
	font-size: 12px;
	color: #b8bcc4;
}

.slot-empty-text {
	margin-left: auto;
	font-size: 11px;
	color: #d9dce1;
}

.course-list {
	display: flex;
	flex-direction: column;
	gap: 8px;
}

.course-card {
	background: #F7F8FA;
	border-radius: 8px;
	padding: 10px 12px;
	border-left: 3px solid #4A90D9;
}

/* 左侧色条按时间段区分，与时段标题配色一致 */
.course-card.card-morning {
	border-left-color: #F59E0B;
}

.course-card.card-afternoon {
	border-left-color: #4A90D9;
}

.course-card.card-evening {
	border-left-color: #7C6BD9;
}

.course-main {
	display: flex;
	justify-content: space-between;
}

.course-info {
	flex: 1;
	min-width: 0;
}

.course-name {
	font-size: 14px;
	font-weight: 600;
	color: #333;
	margin-bottom: 6px;
	display: block;
	word-break: break-all;
	overflow-wrap: break-word;
}

.course-meta {
	display: flex;
	flex-wrap: wrap;
	gap: 8px;
	margin-bottom: 4px;
}

.meta-item {
	display: flex;
	align-items: center;
	font-size: 12px;
	color: #666;
}

.meta-text {
	flex: 1;
	min-width: 0;
	margin-left: 4px;
	word-break: break-all;
	overflow-wrap: break-word;
}

.course-teacher {
	display: flex;
	align-items: center;
	font-size: 12px;
	color: #999;
}

.course-side {
	display: flex;
	align-items: center;
	gap: 6px;
	flex-shrink: 0;
	margin-left: 8px;
}

/* 展开指示箭头：展开时翻转，提示「点击收起」 */
.expand-arrow {
	transition: transform 0.2s ease;
}

.expand-arrow.open {
	transform: rotate(180deg);
}

.status-tag {
	font-size: 11px;
	padding: 3px 8px;
	border-radius: 10px;
	white-space: nowrap;
}

.status-ongoing {
	background: rgba(74,144,217,0.1);
	color: #4A90D9;
}

.status-upcoming {
	background: rgba(250,173,20,0.1);
	color: #FAAD14;
}

.course-detail {
	margin-top: 10px;
	padding-top: 10px;
	border-top: 1px dashed #e2e5ea;
}

.detail-row {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	padding: 4px 0;
}

.detail-label {
	flex-shrink: 0;
	white-space: nowrap;
	font-size: 13px;
	color: #999;
}

.detail-value {
	flex: 1;
	min-width: 0;
	margin-left: 12px;
	text-align: right;
	font-size: 13px;
	color: #333;
	word-break: break-all;
	overflow-wrap: break-word;
}
</style>
