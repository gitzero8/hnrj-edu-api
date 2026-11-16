<template>
	<view class="page-container" :style="{ paddingTop: navBarHeight + 'px' }">
		<!-- 顶部导航栏 -->
		<view class="navbar" :style="{ paddingTop: navBarPaddingTop, height: navBarHeight + 'px' }">
			<view class="nav-back" @click="goBack">
				<AppIcon name="chevron-left" :size="24" color="#fff" />
			</view>
			<text class="nav-title">赞赏支持</text>
			<view class="nav-placeholder"></view>
		</view>

		<scroll-view class="donate-content" scroll-y :style="{ paddingBottom: contentBottomPadding + 'px' }">
			<!-- 感谢文案 -->
			<view class="thank-card">
				<view class="thank-icon">
					<AppIcon name="heart" :size="28" color="#FF6B81" :stroke-width="1.6" />
				</view>
				<text class="thank-title">如果这款软件帮到了你</text>
				<text class="thank-desc">欢迎请我喝杯奶茶，你的每一份支持都是我持续更新的动力</text>
			</view>

			<!-- 支付方式切换 -->
			<view class="pay-tabs">
				<view
					class="pay-tab pay-tab-wechat"
					:class="{ active: activePay === 'wechat' }"
					@click="switchPay('wechat')"
				>
					<text>微信</text>
				</view>
				<view
					class="pay-tab pay-tab-alipay"
					:class="{ active: activePay === 'alipay' }"
					@click="switchPay('alipay')"
				>
					<text>支付宝</text>
				</view>
			</view>

			<!-- 收款码卡片 -->
			<view class="qrcode-card">
				<image
					class="qrcode-img"
					:src="currentQrUrl"
					mode="aspectFit"
					@click="previewQrCode"
				/>
				<view class="qrcode-tips">
					<text class="qrcode-tip">点击二维码放大，长按可保存到相册</text>
					<text class="qrcode-tip-sub">打开{{ currentPayName }}「扫一扫」，从相册选择二维码即可打赏</text>
				</view>
			</view>

			<text class="footer-note">感谢你的支持，我会继续把这个小工具做得更好</text>
		</scroll-view>
	</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppIcon from '@/components/AppIcon.vue'
import { navBarHeight, navBarPaddingTop, safeAreaBottom } from '@/utils/layout'

// ============================================================
// 收款码图片链接配置
// 发布后换码只需替换下面两个 URL。
// 建议在 GitHub 仓库里新建一个英文目录存放收款码（目录名用英文更稳，
// 中文目录生成 raw 链接时会被 URL 编码，容易出错），例如：
//   仓库/qrcode/wechat.png
//   仓库/qrcode/alipay.png
// 然后使用 raw 直链地址：
//   https://raw.githubusercontent.com/<用户名>/<仓库>/<分支>/qrcode/wechat.png
// 若国内加载慢，可改用 jsDelivr CDN 加速：
//   https://cdn.jsdelivr.net/gh/<用户名>/<仓库>@<分支>/qrcode/wechat.png
// ============================================================
const WECHAT_QR_URL = 'https://raw.githubusercontent.com/你的用户名/你的仓库/main/qrcode/wechat.png'
const ALIPAY_QR_URL = 'https://raw.githubusercontent.com/你的用户名/你的仓库/main/qrcode/alipay.png'

const activePay = ref('wechat')

const currentQrUrl = computed(() => activePay.value === 'wechat' ? WECHAT_QR_URL : ALIPAY_QR_URL)
const currentPayName = computed(() => activePay.value === 'wechat' ? '微信' : '支付宝')

const contentBottomPadding = safeAreaBottom + 32

function switchPay(type) {
	activePay.value = type
}

function goBack() {
	uni.navigateBack()
}

function previewQrCode() {
	uni.previewImage({
		urls: [currentQrUrl.value],
		current: currentQrUrl.value
	})
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

.donate-content {
	flex: 1;
	padding: 16px;
	overflow-x: hidden;
	box-sizing: border-box;
}

.thank-card {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 28px 20px 24px;
}

.thank-icon {
	width: 56px;
	height: 56px;
	border-radius: 50%;
	background: rgba(255,107,129,0.1);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 14px;
}

.thank-title {
	font-size: 18px;
	font-weight: 600;
	color: #333;
	margin-bottom: 8px;
}

.thank-desc {
	font-size: 13px;
	color: #999;
	text-align: center;
	line-height: 20px;
}

.pay-tabs {
	display: flex;
	justify-content: center;
	margin-bottom: 12px;
}

.pay-tab {
	min-width: 104px;
	text-align: center;
	padding: 8px 22px;
	border-radius: 20px;
	font-size: 14px;
	font-weight: 500;
	color: #666;
	background: #fff;
	margin: 0 6px;
}

.pay-tab-wechat.active {
	color: #07C160;
	background: rgba(7,193,96,0.1);
}

.pay-tab-alipay.active {
	color: #1677FF;
	background: rgba(22,119,255,0.1);
}

.qrcode-card {
	background: #fff;
	border-radius: 16px;
	padding: 20px 16px;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.qrcode-img {
	width: 480rpx;
	height: 480rpx;
	border-radius: 8px;
	background: #f5f5f5;
}

.qrcode-tips {
	margin-top: 16px;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.qrcode-tip {
	font-size: 14px;
	color: #333;
	font-weight: 500;
	margin-bottom: 6px;
}

.qrcode-tip-sub {
	font-size: 12px;
	color: #999;
	text-align: center;
	line-height: 18px;
}

.footer-note {
	display: block;
	text-align: center;
	font-size: 12px;
	color: #ccc;
	margin-top: 24px;
}
</style>
