<script>
export default {
	onLaunch: function() {
		console.log('App Launch')
	},
	onShow: function() {
		console.log('App Show')
	},
	onHide: function() {
		console.log('App Hide')
	}
}
</script>

<style>
/* 全局样式 */
page {
	background-color: #F5F6FA;
	font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
	font-size: 14px;
	color: #333;
}

:root {
	--primary-color: #4A90D9;
	--primary-light: #6BA8E8;
	--danger-color: #F5222D;
	--success-color: #52C41A;
	--warning-color: #FAAD14;
	--text-primary: #333333;
	--text-secondary: #666666;
	--text-tertiary: #999999;
	--text-placeholder: #CCCCCC;
	--border-color: #E8E8E8;
	--bg-color: #F5F6FA;
	--card-bg: #FFFFFF;
}

/*
 * uni-app 内置组件（view、scroll-view 等）默认 box-sizing 为 content-box，
 * 会导致带 padding 的容器实际宽度 = 100% + padding，在 App 端产生横向溢出。
 * 注意：不包含 input / textarea，避免影响 H5 输入框聚焦与输入。
 */
view,
scroll-view,
swiper,
swiper-item,
cover-view,
cover-image,
movable-area,
movable-view,
picker,
picker-view,
picker-view-column,
button,
label,
navigator,
form,
progress,
slider,
switch,
checkbox,
radio {
	box-sizing: border-box;
}

/* 横向溢出兜底 */
.page-container,
uni-page-body,
uni-page-wrapper {
	overflow-x: hidden;
}

/* 通用按钮 */
.btn-primary {
	background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
	color: #fff;
	border: none;
	border-radius: 22px;
	font-size: 16px;
	font-weight: 600;
}
</style>
