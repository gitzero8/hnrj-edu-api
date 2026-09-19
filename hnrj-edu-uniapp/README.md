# 软大查查（uni-app版）

湖南软件职业技术大学移动教务查询工具的 uni-app 版本，支持打包安卓APK、iOS、H5、小程序等多端。

## 与原Vue3+Vite+Capacitor版本的主要差异

| 对比项 | 原版本（Capacitor） | uni-app版本 |
|--------|---------------------|-------------|
| 网络请求 | Axios + 原生HTTP桥接（MainActivity.java） | `uni.request`（APP端不受CORS限制） |
| 本地存储 | localStorage | `uni.setStorageSync` / `uni.getStorageSync` |
| 路由 | Vue Router | `uni.navigateTo` / `uni.redirectTo` + pages.json |
| 页面标签 | `<div>` `<span>` | `<view>` `<text>` |
| 安卓打包 | Capacitor + gradlew | HBuilderX云打包 / 离线SDK |
| 原生桥接 | 需手动改MainActivity.java | 无需，uni.request原生支持 |
| 跨端能力 | 仅H5+安卓 | H5+安卓+iOS+小程序 |

## 技术栈

- **框架**: Vue 3 (Composition API) + uni-app
- **状态管理**: Pinia
- **网络请求**: uni.request（封装）
- **加密**: CryptoJS (AES-ECB)
- **构建**: Vite（CLI模式）或 HBuilderX

## 项目结构

```
hnrj-edu-uniapp/
├── App.vue                  # 应用入口（全局样式）
├── main.js                  # 入口文件（Pinia注册）
├── manifest.json            # 应用配置（appid、权限、SDK）
├── pages.json               # 页面路由配置
├── package.json
├── pages/
│   ├── login/login.vue      # 登录页
│   ├── schedule/schedule.vue # 课表页
│   ├── grades/grades.vue    # 成绩页
│   ├── profile/profile.vue  # 我的页
│   └── profile-detail/profile-detail.vue # 个人信息详情
├── components/
│   ├── TabBar.vue           # 底部Tab栏
│   └── NotLoggedIn.vue      # 未登录引导
├── store/
│   └── auth.js              # 认证状态管理（Pinia）
├── utils/
│   ├── request.js           # uni.request封装
│   └── crypto.js            # 密码AES加密
└── api/
    └── index.js             # API接口封装
```

## 功能清单

### 账号与认证
- 学号+密码登录，密码前端AES加密
- 登录状态持久化（uni storage）
- 记住密码功能
- 五层Token验证机制（全局定时+路由节流+请求拦截+页面验证+核心方法）
- Token过期弹窗提示并跳转登录
- 退出登录清除缓存

### 课表查询
- 周课表展示（周一至周日，含周六周日）
- 教学周次切换（横向滑动+弹窗选择）
- 课程卡片展开详情
- 实时状态标签：正在上课（蓝）、即将开课（黄，35分钟内）
- 有课程正在上课时隐藏即将开课标签

### 成绩查询
- 按学期分组展示，倒序排列
- 学期筛选
- 成绩颜色标识（优秀/良好/及格/不及格）

### 个人中心
- 用户信息展示
- 个人信息详情（身份证脱敏）
- 退出登录二次确认

## 使用方法

### 方式一：HBuilderX（推荐，最简单）

1. 下载安装 [HBuilderX](https://www.dcloud.io/hbuilderx.html)（App开发版）
2. 文件 → 导入 → 从本地目录导入，选择本项目文件夹
3. 运行 → 运行到手机或模拟器 → 制作自定义调试基座（首次）
4. 发行 → 原生App-云打包 → 选择安卓 → 使用DCloud公用证书 → 打包

### 方式二：CLI模式

```bash
# 安装依赖
npm install

# H5开发
npm run dev:h5

# 安卓APP开发（需连接手机或模拟器）
npm run dev:app

# 构建H5
npm run build:h5

# 构建APP资源（需配合HBuilderX或离线SDK打包）
npm run build:app
```

## 注意事项

1. **CORS问题**：uni-app的`uni.request`在APP端不受浏览器CORS限制，可直接请求后端HTTP接口，无需代理或原生桥接
2. **HTTP明文**：manifest.json中已配置`allowHttp: true`，允许安卓APP使用HTTP请求
3. **校园网限制**：教务系统API有IP白名单，需在校园网环境下使用
4. **appid**：manifest.json中的`appid`为占位符`__UNI__HNRJEDU`，使用HBuilderX打开后会自动分配真实appid
5. **图标**：当前使用默认图标，可在HBuilderX中右键manifest.json → 图标配置 → 自动生成各尺寸图标

## API接口

| 接口 | 说明 |
|------|------|
| `/login` | 用户登录 |
| `/initUserInfo2` | 校验Token/获取用户信息 |
| `/student/my` | 获取学生详细信息 |
| `/Get_sjkbms` | 获取课表时间模式 |
| `/teachingWeek` | 获取教学周次 |
| `/student/curriculum` | 获取课表 |
| `/student/termGPA` | 获取成绩 |
| `/semesterList` | 获取学期列表 |

密码加密流程：`原始密码 → JSON.stringify → AES-ECB(Pkcs7) → Base64 → 再次Base64`

## 版本

v1.0.0
