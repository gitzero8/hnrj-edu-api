<template>
	<view
		v-if="rendered"
		class="app-modal-mask"
		:class="{ 'is-show': visible }"
		@click="onMaskClick"
	>
		<view class="app-modal" :class="{ 'is-show': visible }" @click.stop>
			<view class="app-modal__body">
				<text v-if="title" class="app-modal__title">{{ title }}</text>
				<slot>
					<text v-if="message" class="app-modal__message">{{ message }}</text>
				</slot>
			</view>
			<view class="app-modal__footer">
				<view
					v-if="showCancel"
					class="app-modal__btn"
					hover-class="app-modal__btn--hover"
					@click="onCancel"
				>
					<text>{{ cancelText }}</text>
				</view>
				<view
					class="app-modal__btn app-modal__btn--em"
					:class="['app-modal__btn--' + type, { 'is-divider': showCancel }]"
					hover-class="app-modal__btn--hover"
					@click="onConfirm"
				>
					<text>{{ confirmText }}</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script setup>
import { ref, watch, nextTick, onUnmounted } from 'vue'

const props = defineProps({
	show: { type: Boolean, default: false },
	title: { type: String, default: '' },
	message: { type: String, default: '' },
	// 仅用于主按钮语义色：primary | warning | danger | success
	type: { type: String, default: 'primary' },
	confirmText: { type: String, default: '确定' },
	cancelText: { type: String, default: '取消' },
	showCancel: { type: Boolean, default: false },
	maskClosable: { type: Boolean, default: false },
	duration: { type: Number, default: 220 }
})

const emit = defineEmits(['update:show', 'confirm', 'cancel'])

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
		// 先渲染节点、下一帧再切换为可见，确保过渡动画能正常触发
		nextTick(() => {
			openTimer = setTimeout(() => {
				visible.value = true
			}, 20)
		})
	} else if (rendered.value) {
		// 先播放退出动画，动画结束后再卸载节点
		visible.value = false
		closeTimer = setTimeout(() => {
			rendered.value = false
		}, props.duration)
	}
}, { immediate: true })

onUnmounted(clearTimers)

function close() {
	emit('update:show', false)
}

function onMaskClick() {
	if (props.maskClosable) close()
}

function onConfirm() {
	emit('confirm')
	close()
}

function onCancel() {
	emit('cancel')
	close()
}
</script>

<style scoped>
.app-modal-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	z-index: 9999;
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 0 32px;
	background: rgba(0, 0, 0, 0.45);
	opacity: 0;
	transition: opacity 0.22s ease;
}

.app-modal-mask.is-show {
	opacity: 1;
}

.app-modal {
	width: 100%;
	max-width: 320px;
	background: #fff;
	border-radius: 16px;
	box-shadow: 0 12px 40px rgba(0, 0, 0, 0.16);
	opacity: 0;
	transform: scale(0.86);
	transition: transform 0.24s cubic-bezier(0.32, 1.25, 0.5, 1), opacity 0.22s ease;
}

.app-modal.is-show {
	opacity: 1;
	transform: scale(1);
}

.app-modal__body {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 26px 22px 22px;
}

.app-modal__title {
	font-size: 17px;
	font-weight: 600;
	color: #333;
	line-height: 1.4;
	text-align: center;
}

.app-modal__message {
	margin-top: 8px;
	font-size: 14px;
	color: #666;
	line-height: 1.55;
	text-align: center;
}

.app-modal__footer {
	display: flex;
	border-top: 1px solid #f0f0f0;
}

.app-modal__btn {
	flex: 1;
	min-width: 0;
	height: 50px;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 16px;
	color: #666;
}

.app-modal__btn--hover {
	background: #f7f7f7;
}

.app-modal__btn--em {
	font-weight: 600;
}

.app-modal__btn--primary {
	color: #4A90D9;
}

.app-modal__btn--warning {
	color: #FAAD14;
}

.app-modal__btn--danger {
	color: #F5222D;
}

.app-modal__btn--success {
	color: #52C41A;
}

.app-modal__btn.is-divider {
	border-left: 1px solid #f0f0f0;
}
</style>
