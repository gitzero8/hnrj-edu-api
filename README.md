# 软大查查（hnrj-edu-api）

湖南软件职业技术大学移动教务查询工具，包含 **API 模拟服务器（后端）** 与 **uni-app 客户端（前端）** 两部分，采用单仓库（Monorepo）结构统一管理。

> 本项目为私人项目，仓库为 **Private**，请勿将仓库内容外传。

## 仓库结构

```
hnrj-edu-api/
├── edu-api-server/                 # 后端：Flask 模拟服务器
│   ├── app.py                      # 主服务器（路由、认证、9 个接口）
│   ├── database.py                 # 数据库初始化与模拟数据
│   ├── static/admin.html           # 管理页面
│   ├── test_api.py                 # 接口自测脚本
│   ├── requirements.txt            # Python 依赖
│   └── README.md                   # 后端使用说明
├── hnrj-edu-uniapp/                # 前端：uni-app 客户端（软大查查）
│   ├── pages/                      # 登录 / 课表 / 成绩 / 我的 / 个人信息详情
│   ├── components/                 # TabBar、弹窗、选择器等公共组件
│   ├── store/                      # Pinia 状态管理（认证）
│   ├── utils/                      # 请求封装、密码加密
│   ├── api/                        # 接口封装
│   └── README.md                   # 前端使用说明
├── 教务系统原生API接口文档.md        # API 接口文档（脱敏副本）
├── 维护指南.md                      # 仓库维护指南
└── README.md                       # 本文件
```

## 快速开始

### 1. 启动后端模拟服务器

```bash
cd edu-api-server
pip install -r requirements.txt
python app.py
```

服务器默认监听 `http://127.0.0.1:5000`，首次启动自动创建 SQLite 数据库并填充模拟数据。

### 2. 运行前端客户端

推荐使用 **HBuilderX** 导入 `hnrj-edu-uniapp` 目录后直接运行到手机/模拟器，或使用 CLI 模式：

```bash
cd hnrj-edu-uniapp
npm install
npm run dev:h5      # H5 开发
npm run dev:app     # 安卓 APP 开发（需连接手机或模拟器）
```

> 前端默认请求线上官方 API，切换本地模拟服务器的方法见 `hnrj-edu-uniapp/utils/request.js` 中的 `BASE_URL` 注释。

### 3. 模拟测试账号

模拟服务器内置以下账号（均为虚构数据）：

| 账号类型 | 学号 | 密码 | 说明 |
|----------|------|------|------|
| 新生 | `202609011001` | `Demo@2026edu` | 人工智能(专升本)9901班，有课表，暂无成绩 |
| 老生 | `202309011002` | `Demo@2026edu` | 计算机应用技术9902班，6个学期共57条成绩记录 |
| 管理员 | `admin` | `Admin@2026` | 管理页面（`edu-api-server/static/admin.html`） |

登录密码需先按 AES-ECB（Pkcs7）算法加密，具体流程见后端 README 与接口文档。

## 功能概览

### 后端（edu-api-server）

基于 **Flask + SQLite + JWT**，完全仿原教务系统接口规范，实现 9 个核心接口：

| 接口 | 说明 |
|------|------|
| `/login` | 用户登录，获取 Token |
| `/initUserInfo2` | 校验 Token 有效性，获取用户基本信息 |
| `/student/my` | 获取学生详细个人信息 |
| `/Get_sjkbms` | 获取课表时间模式列表 |
| `/teachingWeek` | 获取教学周次列表 |
| `/student/curriculum` | 获取学生课表 |
| `/student/termGPA` | 获取学生学期成绩 |
| `/currentTerm` | 获取当前学期 |
| `/semesterList` | 获取学期列表 |

认证采用 JWT（HS512，4 小时有效期），除 `/login` 外均需在请求头携带 `token`。

### 前端（hnrj-edu-uniapp）

基于 **Vue 3 + uni-app + Pinia**，支持安卓 APK、iOS、H5、小程序多端，核心功能：

- **登录认证**：学号 + 密码登录，密码前端 AES 加密，登录态持久化，Token 过期自动跳转
- **课表查询**：周课表展示、教学周次切换、课程详情、实时上课状态标签
- **成绩查询**：按学期分组展示、学期筛选、成绩等级颜色标识
- **个人中心**：个人信息展示与详情（身份证号前端脱敏显示）

## 文档索引

| 文档 | 说明 |
|------|------|
| [教务系统原生API接口文档.md](教务系统原生API接口文档.md) | 全部接口的完整规范（脱敏副本），前后端开发的依据 |
| [edu-api-server/README.md](edu-api-server/README.md) | 后端启动方式、接口列表、密码加密与响应格式说明 |
| [hnrj-edu-uniapp/README.md](hnrj-edu-uniapp/README.md) | 前端技术栈、功能清单、打包与运行方式 |
| [维护指南.md](维护指南.md) | Git 提交推送、敏感文件纪律、常见问题处理 |

## 敏感信息纪律（重要）

- 仓库为 **Private**，已通过 `.gitignore` 排除数据库文件（`*.db`）、依赖目录、构建产物、安卓签名证书（`unpackage/`）以及**原始接口文档**（含真实个人信息，仅保留本地）
- 仓库内所有账号、身份证号、手机号、班级等均为**虚构模拟数据**
- 提交前请自查：`git status` 确认文件清单，避免将本地真实数据（数据库、原始文档、签名证书）提交入库，详见 [维护指南.md](维护指南.md)

## 技术栈

| 端 | 技术 |
|----|------|
| 后端 | Python / Flask / SQLite / PyJWT / pycryptodome |
| 前端 | Vue 3 / uni-app / Pinia / CryptoJS / Vite |
| 版本管理 | Git + GitHub（Private 仓库，main 分支） |
