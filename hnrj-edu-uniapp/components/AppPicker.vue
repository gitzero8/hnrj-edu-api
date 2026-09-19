<template>
	<view
		v-if="rendered"
		class="app-picker-mask"
		:class="{ 'is-show': visible }"
		@click="onMaskClick"
	>
		<view
			class="app-picker"
			:class="{ 'is-show': visible }"
			:style="{ paddingBottom: safeAreaBottom + 'px' }"
			@click.stop
		>
			<view class="app-picker__bar">
				<text class="app-picker__title">{{ title }}</text>
				<view class="app-picker__close" hover-class="app-picker__close--hover" @click="close">
					<AppIcon name="close" :size="15" color="#999" />
				</view>
			</view>

			<scroll-view class="app-picker__body" scroll-y>
				<view v-if="mode === 'grid'" class="app-picker__grid">
					<view
						v-for="(opt, idx) in options"
						:key="opt.value ?? idx"
						class="app-picker__cell"
						:class="{ 'is-active': isActive(opt) }"
						hover-class="app-picker__cell--hover"
						@click="onSelect(opt)"
					>
						<text class="app-picker__cell-text">{{ opt.label }}</text>
					</view>
				</view>

				<view v-else class="app-picker__list">
					<view
						v-for="(opt, idx) in options"
						:key="opt.value ?? idx"
						class="app-picker__row"
						:class="{ 'is-active': isActive(opt) }"
						hover-class="app-picker__row--hover"
						@click="onSelect(opt)"
					>
						<text class="app-picker__row-label">{{ opt.label }}</text>
						<AppIcon v-if="isActive(opt)" name="check" :size="16" color="#4A90D9" :stroke-width="2.5" class="app-picker__tick" />
					</view>
				</view>
			</scroll-view>
		</view>
	</view>
</template>

<script setup>
import { ref, watch, nextTick, onUnmounted } from 'vue'
import { safeAreaBottom } from '@/utils/layout'
import AppIcon from '@/components/AppIcon.vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	title: { type: String, default: '' },
	// list 竖向列表 | grid 网格
	mode: { type: String, default: 'list' },
	// [{ label, value, ...自定义字段 }]
	options: { type: Array, default: () => [] },
	modelValue: { type: [String, Number], default: '' },
	maskClosable: { type: Boolean, default: true },
	duration: { type: Number, default: 300 }
})

const emit = defineEmits(['update:show', 'select'])

const rendered = ref(false)
const visible = ref(false)
let openTimer = null
let closeTimer = null

function clearTimers() {
	if (openTimer) {
		clearTimeout(openTimer)
		openTimer = null
	}
	if (closeTimer) {
		clearTimeout(closeTimer)
		closeTimer = null
	}
}

watch(() => props.show, (val) => {
	clearTimers()
	if (val) {
		rendered.value = true
		nextTick(() => {
			openTimer = setTimeout(() => {
				visible.value = true
			}, 20)
		})
	} else if (rendered.value) {
		visible.value = false
		closeTimer = setTimeout(() => {
			rendered.value = false
		}, props.duration)
	}
}, { immediate: true })

onUnmounted(clearTimers)

function isActive(opt) {
	return String(opt.value) === String(props.modelValue)
}

function close() {
	emit('update:show', false)
}

function onMaskClick() {
	if (props.maskClosable) close()
}

function onSelect(opt) {
	emit('select', opt)
	close()
}
</script>

<style scoped>
.app-picker-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	z-index: 999;
	display: flex;
	align-items: flex-end;
	background: rgba(0, 0, 0, 0.45);
	opacity: 0;
	transition: opacity 0.28s ease;
}

.app-picker-mask.is-show {
	opacity: 1;
}

.app-picker {
	width: 100%;
	max-height: 78vh;
	display: flex;
	flex-direction: column;
	background: #fff;
	border-radius: 18px 18px 0 0;
	transform: translateY(100%);
	transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.app-picker.is-show {
	transform: translateY(0);
}

/* 顶部拖拽提示条 */
.app-picker::before {
	content: '';
	width: 36px;
	height: 4px;
	border-radius: 2px;
	background: #e0e0e0;
	margin: 10px auto 0;
	flex-shrink: 0;
}

.app-picker__bar {
	position: relative;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 12px 16px;
	flex-shrink: 0;
}

.app-picker__title {
	font-size: 16px;
	font-weight: 600;
	color: #333;
}

.app-picker__close {
	position: absolute;
	right: 8px;
	top: 50%;
	margin-top: -18px;
	width: 36px;
	height: 36px;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
}

.app-picker__close--hover {
	background: #f2f3f5;
}

.app-picker__body {
	flex: 1;
	min-height: 0;
	max-height: 60vh;
	padding: 0 16px 8px;
}

/* 网格模式 */
.app-picker__grid {
	display: flex;
	flex-wrap: wrap;
	margin: 0 -5px;
}

.app-picker__cell {
	width: 25%;
	padding: 5px;
}

.app-picker__cell-text {
	display: flex;
	align-items: center;
	justify-content: center;
	height: 42px;
	border-radius: 10px;
	background: #f5f6f8;
	font-size: 14px;
	color: #333;
	transition: background-color 0.15s ease, color 0.15s ease;
}

.app-picker__cell--hover .app-picker__cell-text {
	background: #ebedf0;
}

.app-picker__cell.is-active .app-picker__cell-text {
	background: linear-gradient(135deg, #4A90D9, #6BA8E8);
	color: #fff;
	font-weight: 600;
}

/* 列表模式 */
.app-picker__list {
	padding-bottom: 4px;
}

.app-picker__row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: 14px 12px;
	border-radius: 10px;
}

.app-picker__row--hover {
	background: #f7f8fa;
}

.app-picker__row-label {
	flex: 1;
	min-width: 0;
	font-size: 15px;
	color: #333;
	word-break: break-all;
	overflow-wrap: break-word;
}

.app-picker__row.is-active .app-picker__row-label {
	color: #4A90D9;
	font-weight: 600;
}

.app-picker__tick {
	flex-shrink: 0;
	margin-left: 12px;
}
</style>
