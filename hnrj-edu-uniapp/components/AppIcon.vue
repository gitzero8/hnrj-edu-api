<template>
	<view class="app-icon" :style="iconStyle"></view>
</template>

<script setup>
import { computed } from 'vue'

/*
 * 统一图标组件
 *
 * 实现方式：SVG data URI 作为 background-image。
 * 为什么不用模板里的 <svg>/<path> 内联标签：
 * App 端 Vue 运行时用 document.createElement('svg') 创建节点，
 * 而非 createElementNS，SVG 不在 SVG 命名空间下，浏览器会直接忽略不渲染。
 * 用 background-image 则交由 CSS 引擎解析，App / H5 / 小程序 均可用。
 *
 * color 需显式传入（data URI 是独立文档，无法继承 currentColor）。
 */
const ICON_PATHS = {
	// 用户 / 学生
	user: [
		'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2',
		'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0z'
	],
	// 教师
	teacher: [
		'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2',
		'M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0z',
		'M19 3l1 2 2 1-2 1-1 2-1-2-2-1 2-1 1-2z'
	],
	// 密码锁
	lock: [
		'M5 11h14a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2z',
		'M7 11V7a5 5 0 0 1 10 0v4'
	],
	// 显示密码
	eye: [
		'M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z',
		'M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0z'
	],
	// 隐藏密码
	'eye-off': [
		'M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24',
		'M1 1l22 22'
	],
	// 上课时间
	clock: [
		'M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0z',
		'M12 6v6l4 2'
	],
	// 上课地点
	'map-pin': [
		'M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z',
		'M15 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0z'
	],
	// 错误 / 警告
	'alert-triangle': [
		'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z',
		'M12 9v4',
		'M12 17h.01'
	],
	// 空状态 - 无课程
	inbox: [
		'M22 12h-6l-2 3h-4l-2-3H2',
		'M5.45 5.11L2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z'
	],
	// 空状态 - 无成绩
	'file-text': [
		'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z',
		'M14 2v6h6',
		'M16 13H8',
		'M16 17H8'
	],
	// 退出登录
	'log-out': [
		'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4',
		'M16 17l5-5-5-5',
		'M21 12H9'
	],
	// 向下箭头
	'chevron-down': [
		'M6 9l6 6 6-6'
	],
	// 向左箭头
	'chevron-left': [
		'M15 18l-6-6 6-6'
	],
	// 向右箭头
	'chevron-right': [
		'M9 18l6-6-6-6'
	],
	// 勾选
	check: [
		'M20 6L9 17l-5-5'
	],
	// 关闭
	close: [
		'M18 6L6 18',
		'M6 6l12 12'
	],
	// 刷新 / 重试
	refresh: [
		'M23 4v6h-6',
		'M1 20v-6h6',
		'M3.51 9a9 9 0 0 1 14.85-3.36L23 10',
		'M1 14l4.64 4.36A9 9 0 0 0 20.49 15'
	],
	// 课表
	calendar: [
		'M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z',
		'M16 2v4',
		'M8 2v4',
		'M3 10h18'
	],
	// 成绩
	file: [
		'M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z',
		'M13 2v7h7'
	],
	// 作息分段 - 上午（日出）
	sunrise: [
		'M17 18a5 5 0 0 0-10 0',
		'M12 2v7',
		'M8.5 5.5L12 2l3.5 3.5',
		'M1 18h2',
		'M21 18h2',
		'M4.22 10.22l1.42 1.42',
		'M18.36 11.64l1.42-1.42',
		'M23 22H1'
	],
	// 作息分段 - 下午（太阳）
	sun: [
		'M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0z',
		'M12 1v2',
		'M12 21v2',
		'M4.22 4.22l1.42 1.42',
		'M18.36 18.36l1.42 1.42',
		'M1 12h2',
		'M21 12h2',
		'M4.22 19.78l1.42-1.42',
		'M18.36 5.64l1.42-1.42'
	],
	// 作息分段 - 晚上（月亮）
	moon: [
		'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z'
	]
}

const props = defineProps({
	name: { type: String, required: true },
	size: { type: [Number, String], default: 16 },
	color: { type: String, default: '#666666' },
	strokeWidth: { type: [Number, String], default: 2 }
})

const iconStyle = computed(() => {
	const paths = ICON_PATHS[props.name] || []
	const body = paths.map(d => `<path d="${d}"/>`).join('')
	const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="${props.color}" stroke-width="${props.strokeWidth}" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`

	const s = typeof props.size === 'number' ? `${props.size}px` : props.size
	return {
		width: s,
		height: s,
		backgroundImage: `url("data:image/svg+xml,${encodeURIComponent(svg)}")`
	}
})
</script>

<style scoped>
.app-icon {
	display: block;
	flex-shrink: 0;
	background-repeat: no-repeat;
	background-position: center;
	background-size: 100% 100%;
	vertical-align: middle;
}
</style>
