# 移动教务系统 API 模拟服务器

基于 **Flask + SQLite + JWT** 实现的移动教务系统 API 模拟后端，完全仿湖南软件职业技术大学移动教务系统接口规范。

## 功能特性

- 9 个核心接口完整实现（登录、个人信息、课表、成绩、学期等）
- JWT Token 认证机制（HS512 算法，4小时有效期）
- AES-ECB 密码解密（与原系统加密算法完全一致）
- SQLite 轻量级数据库，零配置
- 内置两个测试账号（新生 + 老生，含完整历史成绩数据）
- CORS 跨域支持，前端可直接调用

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | Flask 3.x |
| 数据库 | SQLite 3 |
| 认证 | JWT (PyJWT, HS512) |
| 加密 | AES-ECB (pycryptodome) |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python app.py
```

服务器默认监听 `http://127.0.0.1:5000`，可通过环境变量 `PORT` 修改端口。

### 3. 测试账号

| 账号类型 | 学号 | 密码 | 说明 |
|----------|------|------|------|
| 新生 | `202609011001` | `Demo@2026edu` | 人工智能(专升本)9901班，有课表，暂无成绩 |
| 老生 | `202309011002` | `Demo@2026edu` | 计算机应用技术9902班，6个学期共57条成绩记录 |

## 接口列表

| 序号 | 接口 | 方法 | 说明 | 认证 |
|------|------|------|------|------|
| 1 | `/login` | POST | 用户登录，获取Token | 否 |
| 2 | `/initUserInfo2` | POST | 校验Token有效性，获取用户基本信息 | 是 |
| 3 | `/student/my` | POST | 获取学生详细个人信息 | 是 |
| 4 | `/Get_sjkbms` | POST | 获取课表时间模式列表 | 是 |
| 5 | `/teachingWeek` | POST | 获取教学周次列表 | 是 |
| 6 | `/student/curriculum` | POST | 获取学生课表 | 是 |
| 7 | `/student/termGPA` | POST | 获取学生学期成绩 | 是 |
| 8 | `/currentTerm` | POST | 获取当前学期 | 是 |
| 9 | `/semesterList` | POST | 获取学期列表 | 是 |

## 调用示例

### 1. 登录获取 Token

```bash
# 密码需要先按文档中的 AES-ECB 算法加密
curl -X POST "http://127.0.0.1:5000/login?userNo=202609011001&pwd=<加密后的密码>&encode=1"
```

### 2. 获取用户信息

```bash
curl -X POST "http://127.0.0.1:5000/initUserInfo2" \
  -H "token: <your_token>"
```

### 3. 获取课表

```bash
curl -X POST "http://127.0.0.1:5000/student/curriculum?week=all&kbjcmsid=63D5F875CCE34BF482A67EC5424EE1D1" \
  -H "token: <your_token>"
```

### 4. 获取成绩

```bash
# 所有学期
curl -X POST "http://127.0.0.1:5000/student/termGPA" \
  -H "token: <your_token>"

# 指定学期
curl -X POST "http://127.0.0.1:5000/student/termGPA?semester=2023-2024-1" \
  -H "token: <your_token>"
```

## 密码加密说明

登录接口的 `pwd` 参数需要经过以下加密流程：

```
原始密码 → JSON.stringify() → AES-ECB加密(Pkcs7填充) → Base64编码 → 再次Base64编码 → 最终pwd
```

- 加密密钥：`qzkj1kjghd=876&*`
- 加密模式：AES / ECB / Pkcs7

服务器端会自动解密验证，与原系统行为完全一致。

## 响应格式

### 通用响应结构

```json
{
  "code": "1",
  "Msg": "success",
  "data": {}
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 状态码，"1"成功，"0"失败 |
| Msg | string | 提示信息 |
| data | object/array | 响应数据 |

> 注意：`/initUserInfo2` 接口直接返回数据对象，不包含 `code`/`Msg` 包装层。

## 数据库结构

| 表名 | 说明 |
|------|------|
| `users` | 用户信息表 |
| `semesters` | 学期表 |
| `time_modes` | 课表时间模式表 |
| `courses` | 课程表 |
| `grades` | 成绩表 |

数据库文件 `edu_system.db` 在首次启动时自动创建并填充测试数据。

## 项目结构

```
edu-api-server/
├── app.py              # 主服务器（路由、认证、接口实现）
├── database.py         # 数据库初始化与测试数据
├── requirements.txt    # Python 依赖
├── README.md           # 使用说明
└── edu_system.db       # SQLite 数据库（自动生成）
```

## 注意事项

1. 所有接口均使用 `POST` 方法，参数通过 URL Query String 传递
2. 需要认证的接口必须在请求头中携带 `token` 字段
3. Token 有效期为 4 小时，过期后需重新登录
4. 新生账号暂无成绩数据，属正常现象
5. 本服务器仅用于开发测试，不可用于生产环境
