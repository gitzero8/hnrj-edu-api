# 湖南软件职业技术大学移动教务系统 API 接口文档

## 1. 概述

### 1.1 系统信息

| 项目 | 内容 |
|------|------|
| 系统名称 | 移动教务系统 |
| 前端地址 | http://222.243.161.213:81/hnrjzyxysjd/ |
| API 基础地址 | http://222.243.161.213:81/hnrjzyxyhd |
| 学校代码 | 4711 |
| 技术栈 | Vue.js + Spring Boot (JWT认证) |

### 1.2 认证方式

系统采用 **JWT (JSON Web Token)** 认证机制。

- 登录成功后，响应中返回 `token` 字段
- 后续所有需要认证的接口，需在 HTTP 请求头中携带 `token`
- Token 有效期约为 4 小时（具体以服务端为准）

**请求头示例：**
```
token: eyJhbGciOiJIUzUxMiJ9...
```

### 1.3 请求格式

- **请求方法**：主要使用 `POST`
- **参数传递**：通过 URL Query String 传递参数（`params` 方式）
- **Content-Type**：`application/x-www-form-urlencoded` 或不指定
- **字符编码**：UTF-8

### 1.4 响应格式

所有接口返回 JSON 格式数据，通用结构如下：

```json
{
  "code": "1",
  "Msg": "success",
  "data": {}
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 状态码，"1"表示成功，"0"表示失败 |
| Msg | string | 提示信息 |
| data | object/array | 响应数据，具体结构见各接口说明 |

> **注意**：部分接口（如 `/initUserInfo2`）直接返回数据对象，不包含 `code`/`Msg` 包装。

### 1.5 接口汇总

| 分类 | 接口名称 | 请求方法 | 接口地址 | 说明 |
|------|----------|----------|----------|------|
| 认证 | 用户登录 | POST | `/login` | 用户登录，获取Token |
| 个人信息 | 获取用户信息 | POST | `/initUserInfo2` | 获取当前登录用户的基本信息 |
| 课表 | 获取时间模式 | POST | `/Get_sjkbms` | 获取课表时间模式（节次模式）列表 |
| 课表 | 获取教学周次 | POST | `/teachingWeek` | 获取当前学期的教学周次列表 |
| 课表 | 获取学生课表 | POST | `/student/curriculum` | 获取学生的课程表信息 |
| 成绩 | 获取学生成绩 | POST | `/student/termGPA` | 获取学生的所有学期成绩 |
| 辅助 | 获取当前学期 | POST | `/currentTerm` | 获取当前生效的学期 |
| 辅助 | 获取学期列表 | POST | `/semesterList` | 获取所有可查询的学期列表 |

---

## 2. 登录接口

### 2.1 用户登录

**接口地址**：`POST /login`

**接口说明**：用户登录，获取访问令牌（Token）

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| userNo | string | 是 | 学号/工号 |
| pwd | string | 是 | 加密后的密码（加密算法见第7章） |
| encode | string | 是 | 固定值 `"1"`，表示密码已加密 |
| captchaData | string | 否 | 验证码（学校代码4711不需要） |
| codeVal | string | 否 | 验证码标识（学校代码4711不需要） |

**请求示例**：

```bash
curl -X POST "http://222.243.161.213:81/hnrjzyxyhd/login?userNo=2026****0000&pwd=<加密后的密码>&encode=1"
```

**响应示例**：

```json
{
  "code": "1",
  "Msg": "登录成功！",
  "data": {
    "birthday": "2000****",
    "academyName": "人工智能学院",
    "userNo": "2026****0000",
    "entranceYear": "2026",
    "clsName": "人工智能(专升本)****班",
    "name": "张某某",
    "userType": "2",
    "token": "eyJhbGciOiJIUzUxMiJ9..."
  }
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| birthday | string | 出生日期（YYYYMMDD） |
| academyName | string | 学院名称 |
| userNo | string | 学号/工号 |
| entranceYear | string | 入学年份 |
| clsName | string | 班级名称 |
| name | string | 姓名 |
| userType | string | 用户类型，"1"=教师，"2"=学生 |
| token | string | JWT访问令牌 |

**错误响应**：

```json
{
  "code": "0",
  "Msg": "该帐号不存在或密码错误！",
  "data": {}
}
```

---

## 3. 个人信息接口

### 3.1 获取学生详细信息（用于获取用户个人信息）

**接口地址**：`POST /student/my`

**接口说明**：获取当前登录学生的详细个人信息

**请求头**：

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| token | string | 是 | 登录获取的访问令牌 |
| **请求参数**：无 |  |  |  |
| **请求示例**： |  |  |  |

```
curl -X POST "[http://222.243.161.213:81/hnrjzyxyhd/student/my](http://222.243.161.213:81/hnrjzyxyhd/student/my)" \
  -H "token: <your_token>"
```

**响应示例**：

```
{
  "Msg": "success",
  "code": "1",
  "data": [
    {
      "ksh": "",
      "sfzjh": "",
      "gender": "男",
      "dh": "",
      "className": "人工智能(专升本)****班",
      "idno": "431***********0000",
      "studentID": "2026****0000",
      "inGrade": "2026",
      "school": "湖南软件职业技术大学",
      "name": "张某某",
      "majorName": "人工智能工程技术(专升本)",
      "dateBirth": "2000****",
      "sfzczxkt": "1",
      "academy": "人工智能学院",
      "trainingLevel": "专升本"
    }
  ]
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| Msg | string | 返回提示信息，success代表成功 |
| code | string | 业务状态码，"1"代表成功 |
| data | array | 学生信息数组 |
| ksh | string | 考生号 |
| sfzjh | string | 证件号 |
| gender | string | 性别 |
| dh | string | 联系电话 |
| className | string | 班级名称 |
| idno | string | 身份证号 |
| studentID | string | 学号 |
| inGrade | string | 入学年份 |
| school | string | 学校名称 |
| name | string | 学生姓名 |
| majorName | string | 专业名称 |
| dateBirth | string | 出生日期（YYYYMMDD格式） |
| sfzczxkt | string | 是否在校状态标识 |
| academy | string | 所属学院 |
| trainingLevel | string | 培养层次 |
 
---

## 4. 课程表接口

### 4.1 获取时间模式列表

**接口地址**：`POST /Get_sjkbms`

**接口说明**：获取课表时间模式（节次模式）列表，用于课表查询

**请求头**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| token | string | 是 | 访问令牌 |

**请求参数**：无

**响应示例**：

```json
{
  "msg": "success",
  "code": 1,
  "data": [
    {
      "mrms": "1",
      "kbjcmsid": "63D5F875CCE34BF482A67EC5424EE1D1",
      "kbjcmsmc": "默认节次模式"
    }
  ]
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| mrms | string | 是否默认模式（"1"=默认） |
| kbjcmsid | string | 时间模式ID（课表查询时使用） |
| kbjcmsmc | string | 时间模式名称 |

### 4.2 获取教学周次列表

**接口地址**：`POST /teachingWeek`

**接口说明**：获取当前学期的教学周次列表，用于课表查询时选择具体周次

**请求头**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| token | string | 是 | 访问令牌 |

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| semester | string | 否 | 学年学期ID，如"2026-2027-1"；为空时默认查询当前学期 |

**请求示例**：

```bash
# 无参数（默认当前学期）
curl -X POST "http://222.243.161.213:81/hnrjzyxyhd/teachingWeek" \
  -H "token: <your_token>"

# 指定学期
curl -X POST "http://222.243.161.213:81/hnrjzyxyhd/teachingWeek?semester=2026-2027-1" \
  -H "token: <your_token>"
```

**响应示例**：

```json
{
  "code": "1",
  "Msg": "success",
  "data": [
    {"week": "1"},
    {"week": "2"},
    {"week": "3"},
    {"week": "4"},
    {"week": "5"},
    {"week": "6"},
    {"week": "7"},
    {"week": "8"},
    {"week": "9"},
    {"week": "10"},
    {"week": "11"},
    {"week": "12"},
    {"week": "13"},
    {"week": "14"},
    {"week": "15"},
    {"week": "16"},
    {"week": "17"},
    {"week": "18"},
    {"week": "19"},
    {"week": "20"}
  ]
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| data | array | 教学周次列表 |
| data[].week | string | 周次编号（1-20） |

> **说明**：该接口返回当前学期的所有教学周次，通常为20周。在查询课表时，可将 `week` 参数设置为具体的周次编号，或设置为 `"all"` 查询全部周次的课程。

### 4.3 获取学生课表

**接口地址**：`POST /student/curriculum`

**接口说明**：获取学生的课程表信息

**请求头**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| token | string | 是 | 访问令牌 |

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| week | string | 是 | 查询周次，`"all"` 表示查询全部周次，或指定具体周次如 `"1"` |
| kbjcmsid | string | 是 | 时间模式ID，通过 `/Get_sjkbms` 接口获取 |

**请求示例**：

```bash
curl -X POST "http://222.243.161.213:81/hnrjzyxyhd/student/curriculum?week=all&kbjcmsid=63D5F875CCE34BF482A67EC5424EE1D1" \
  -H "token: <your_token>"
```

**响应示例**：

```json
{
  "Msg": "success~",
  "code": "1",
  "data": [
    {
      "date": [
        {"xqmc": "一", "mxrq": "", "zc": "all", "xqid": "1", "rq": ""},
        {"xqmc": "二", "mxrq": "", "zc": "all", "xqid": "2", "rq": ""},
        {"xqmc": "三", "mxrq": "", "zc": "all", "xqid": "3", "rq": ""},
        {"xqmc": "四", "mxrq": "", "zc": "all", "xqid": "4", "rq": ""},
        {"xqmc": "五", "mxrq": "", "zc": "all", "xqid": "5", "rq": ""},
        {"xqmc": "六", "mxrq": "", "zc": "all", "xqid": "6", "rq": ""},
        {"xqmc": "日", "mxrq": "", "zc": "all", "xqid": "0", "rq": ""}
      ],
      "courses": [
        {
          "classWeek": "17-18",
          "teacherName": "",
          "weekNoteDetail": "103,104",
          "buttonCode": "0",
          "xkrs": 21,
          "ktmc": "人工智能(专升本)****班",
          "classTime": "10304",
          "classroomNub": "H02实-305",
          "jx0408id": "BA63F7A80C6745E499220C7162C2DD3B",
          "buildingName": "第二实训楼（老校区）",
          "courseName": "大模型应用实践",
          "isRepeatCode": "0",
          "jx0404id": "2026202713332",
          "weekDay": "1",
          "classroomName": "S2-305",
          "khfs": "考查",
          "startTime": "10:00",
          "endTIme": "11:40",
          "location": "S2-305",
          "fzmc": "",
          "classWeekDetails": ",17,18,",
          "coursesNote": 2
        }
      ],
      "nodesLst": [],
      "item": {},
      "week": "all",
      "nodes": [],
      "weekday": [],
      "bz": "",
      "topInfo": {}
    }
  ]
}
```

**响应字段说明 - 课程信息（courses数组元素）**：

| 字段 | 类型 | 说明 |
|------|------|------|
| courseName | string | 课程名称 |
| teacherName | string | 授课教师姓名 |
| classWeek | string | 上课周次范围，如"17-18" |
| classWeekDetails | string | 详细上课周次，逗号分隔，如",17,18," |
| weekDay | string | 星期几（"1"=周一，"2"=周二，...，"7"=周日） | 注意："7"=周日，与 {"xqmc": "日", "mxrq": "", "zc": "all", "xqid": "0", "rq": ""} 不同
| startTime | string | 上课开始时间，如"10:00" |
| endTIme | string | 上课结束时间，如"11:40" |
| classTime | string | 节次编码，如"10304"表示第3-4节 |
| weekNoteDetail | string | 节次详情，如"103,104" |
| classroomName | string | 教室名称，如"S2-305" |
| classroomNub | string | 教室编号，如"H02实-305" |
| buildingName | string | 教学楼名称，如"第二实训楼（老校区）" |
| location | string | 上课地点（简化） |
| ktmc | string | 上课班级名称 |
| khfs | string | 考核方式（"考查"/"考试"） |
| xkrs | number | 选课人数 |
| jx0404id | string | 教学任务ID |
| jx0408id | string | 课表安排ID |
| isRepeatCode | string | 是否重复课程标记 |
| buttonCode | string | 按钮操作码 |
| fzmc | string | 分组名称 |
| coursesNote | number | 课程备注数量 |

---

## 5. 考试成绩接口

### 5.1 获取学生学期成绩

**接口地址**：`POST /student/termGPA`

**接口说明**：获取当前登录学生的所有学期成绩信息，包括课程成绩、学分、考试性质等。该接口会根据Token自动识别学生身份，返回该学生的全部成绩数据。

**请求头**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| token | string | 是 | 访问令牌 |

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| semester | string | 否 | 学年学期ID，如"2023-2024-1"；为空时返回所有学期成绩 |

**请求示例**：

```bash
# 查询所有学期成绩
curl -X POST "http://222.243.161.213:81/hnrjzyxyhd/student/termGPA" \
  -H "token: <your_token>"

# 查询指定学期成绩
curl -X POST "http://222.243.161.213:81/hnrjzyxyhd/student/termGPA?semester=2023-2024-1" \
  -H "token: <your_token>"
```

**响应示例**：

```json
{
  "Msg": "success",
  "code": "1",
  "data": [
    {
      "studentID": "2023****0000",
      "xqgpa": [],
      "pjcj": "",
      "achievement": [
        {
          "curriculumAttributes": "必修",
          "courseName": "体育与健康（1）",
          "curSemesterName": "2023-2024-1",
          "courseNature": "公共必修课",
          "examinationNature": "正常考试",
          "kcbh": "01002101",
          "credit": 2,
          "cj0708id": "0E8DF101B636EBDAE0630103FE0A32EE",
          "fraction": "68"
        },
        {
          "curriculumAttributes": "必修",
          "courseName": "高职应用数学",
          "curSemesterName": "2023-2024-1",
          "courseNature": "公共必修课",
          "examinationNature": "正常考试",
          "kcbh": "01002105",
          "credit": 4,
          "cj0708id": "0F0C59A339C690D7E0630103FE0AE4ED",
          "fraction": "78"
        },
        {
          "curriculumAttributes": "必修",
          "courseName": "公共英语（1）",
          "curSemesterName": "2023-2024-1",
          "courseNature": "公共课",
          "examinationNature": "正常考试",
          "kcbh": "01002113",
          "credit": 4,
          "cj0708id": "0F0C562BF9AC0802E0630103FE0A02D8",
          "fraction": "53"
        },
        {
          "curriculumAttributes": "必修",
          "courseName": "公共英语（1）",
          "curSemesterName": "2023-2024-1",
          "courseNature": "公共课",
          "examinationNature": "重修一",
          "kcbh": "01002113",
          "credit": 4,
          "cj0708id": "52EA7D6E80E35F46E0630103FE0AC25A",
          "fraction": "87"
        },
        {
          "curriculumAttributes": "必修",
          "courseName": "公共英语（1）",
          "curSemesterName": "2023-2024-1",
          "courseNature": "公共课",
          "examinationNature": "补考一",
          "kcbh": "01002113",
          "credit": 4,
          "cj0708id": "13E7F0974724C234E0630103FE0A289F",
          "fraction": "0"
        }
      ]
    }
  ]
}
```

**响应字段说明 - 顶层数据（data数组元素）**：

| 字段 | 类型 | 说明 |
|------|------|------|
| studentID | string | 学号 |
| xqgpa | array | 学期GPA列表（可能为空） |
| pjcj | string | 平均成绩（可能为空） |
| achievement | array | 成绩列表 |

**响应字段说明 - 成绩信息（achievement数组元素）**：

| 字段 | 类型 | 说明 |
|------|------|------|
| curriculumAttributes | string | 课程属性（必修/选修等） |
| courseName | string | 课程名称 |
| curSemesterName | string | 学期名称，如"2023-2024-1" |
| courseNature | string | 课程性质（公共必修课/公共课/专业基础课等） |
| examinationNature | string | 考试性质（正常考试/补考一/重修一等） |
| kcbh | string | 课程编号 |
| credit | number | 学分 |
| cj0708id | string | 成绩记录唯一ID |
| fraction | string | 成绩分数 |

> **说明**：
> - 该接口返回当前登录学生的所有学期成绩，无需传入学生ID，系统根据Token自动识别。
> - 同一门课程可能有多条成绩记录（正常考试、补考、重修等），通过 `examinationNature` 字段区分。
> - 新生入学初期可能暂无成绩数据，此时 `achievement` 数组为空。
> - 实际测试数据：2023级学生返回61条成绩记录，涵盖6个学期（2023-2024-1至2025-2026-2）。

---

## 6. 辅助接口


### 6.1 校验Token有效性

**接口地址**：`POST /initUserInfo2`

**接口说明**：获取当前登录用户的基本信息，根据返回的内容判断Token有效性

**请求头**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| token | string | 是 | 登录获取的访问令牌 |

**请求参数**：无

**请求示例**：

```bash
curl -X POST "http://222.243.161.213:81/hnrjzyxyhd/initUserInfo2" \
  -H "token: <your_token>"
```

**响应示例**：

```json
{
  "birthday": "2000****",
  "academyName": "人工智能学院",
  "userNo": "2026****0000",
  "entranceYear": "2026",
  "clsName": "人工智能(专升本)****班",
  "name": "张某某",
  "userType": "2",
  "token": "eyJhbGciOiJIUzUxMiJ9..."
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| birthday | string | 出生日期（YYYYMMDD格式） |
| academyName | string | 所属学院名称 |
| userNo | string | 学号 |
| entranceYear | string | 入学年份 |
| clsName | string | 班级名称 |
| name | string | 学生姓名 |
| userType | string | 用户类型（"2"表示学生） |
| token | string | 当前有效的访问令牌 |

> **注意**：此接口在状态码为 200 时响应直接返回数据对象，不包含 `code`/`Msg` 包装层。

### 6.2 获取当前学期

**接口地址**：`POST /currentTerm`

**接口说明**：获取当前生效的学期信息

**请求头**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| token | string | 是 | 访问令牌 |

**请求参数**：无

**响应示例**：

```json
{
  "code": "1",
  "Msg": "success",
  "data": [
    {
      "semesterId": "2026-2027-1",
      "semesterName": "2026-2027-1"
    }
  ]
}
```

### 6.3 获取学期列表

**接口地址**：`POST /semesterList`

**接口说明**：获取所有可查询的学期列表，用于课表查询、成绩查询等场景下选择学期。系统会根据当前时间返回所有已开设的学期。

**请求头**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| token | string | 是 | 访问令牌 |

**请求参数**：无

**请求示例**：

```bash
curl -X POST "http://222.243.161.213:81/hnrjzyxyhd/semesterList" \
  -H "token: <your_token>"
```

**响应示例**：

```json
{
  "code": "1",
  "Msg": "success",
  "data": [
    {
      "isdqxq": "1",
      "semesterId": "2026-2027-1",
      "semesterName": "2026-2027-1"
    },
    {
      "isdqxq": "0",
      "semesterId": "2025-2026-2",
      "semesterName": "2025-2026-2"
    },
    {
      "isdqxq": "0",
      "semesterId": "2025-2026-1",
      "semesterName": "2025-2026-1"
    },
    {
      "isdqxq": "0",
      "semesterId": "2024-2025-2",
      "semesterName": "2024-2025-2"
    },
    {
      "isdqxq": "0",
      "semesterId": "2024-2025-1",
      "semesterName": "2024-2025-1"
    },
    {
      "isdqxq": "0",
      "semesterId": "2023-2024-2",
      "semesterName": "2023-2024-2"
    },
    {
      "isdqxq": "0",
      "semesterId": "2023-2024-1",
      "semesterName": "2023-2024-1"
    }
  ]
}
```

**响应字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| isdqxq | string | 是否当前学期（"1"=是，"0"=否） |
| semesterId | string | 学期ID，格式为"YYYY-YYYY-N"（如"2026-2027-1"表示2026-2027学年第一学期） |
| semesterName | string | 学期名称 |

> **说明**：该接口返回系统中所有已开设的学期，按时间倒序排列，当前学期排在第一位。实际测试返回7个学期（2023-2024-1至2026-2027-1）。`semesterId` 可用于成绩查询（`/student/termGPA?semester=xxx`）等接口的学期筛选参数。

---

## 7. 密码加密算法

登录接口的密码字段 `pwd` 需要经过特定的加密处理，以下是完整的加密算法说明。

### 7.1 加密流程

```
原始密码 → JSON.stringify() → AES-ECB加密 → Base64编码 → 最终pwd
```

### 7.2 加密参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 加密算法 | AES | 对称加密算法 |
| 加密模式 | ECB | 电子密码本模式 |
| 填充方式 | Pkcs7 | PKCS7填充 |
| 加密密钥 | `qzkj1kjghd=876&*` | 固定密钥，UTF-8编码 |

### 7.3 加密步骤

1. **JSON序列化**：将原始密码字符串进行 `JSON.stringify()` 处理（即给字符串加上双引号）
   - 输入：`password****`
   - 输出：`"password****"`

2. **AES-ECB加密**：使用密钥 `qzkj1kjghd=876&*` 对上一步结果进行AES-ECB加密（Pkcs7填充），输出Base64格式的密文

3. **Base64编码**：将上一步的Base64密文字符串再次进行Base64编码，得到最终的 `pwd` 参数值

### 7.4 JavaScript 实现示例

```javascript
const CryptoJS = require('crypto-js');

// 加密密钥
const SECRET_KEY = "qzkj1kjghd=876&*";

/**
 * 加密登录密码
 * @param {string} password - 原始密码
 * @returns {string} 加密后的密码（用于登录接口的pwd参数）
 */
function encryptPassword(password) {
    // 步骤1: JSON序列化
    const jsonStr = JSON.stringify(password);
    
    // 步骤2: AES-ECB加密
    const key = CryptoJS.enc.Utf8.parse(SECRET_KEY);
    const encrypted = CryptoJS.AES.encrypt(jsonStr, key, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    }).toString();
    
    // 步骤3: Base64编码
    const finalPwd = btoa(encrypted);
    
    return finalPwd;
}

// 使用示例
const password = "password****";
const encryptedPwd = encryptPassword(password);
console.log("加密后的密码:", encryptedPwd);
```

### 7.5 Python 实现示例

```python
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# 加密密钥
SECRET_KEY = b"qzkj1kjghd=876&*"

def encrypt_password(password: str) -> str:
    """
    加密登录密码
    :param password: 原始密码
    :return: 加密后的密码
    """
    # 步骤1: JSON序列化
    json_str = json.dumps(password)
    
    # 步骤2: AES-ECB加密
    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    padded_data = pad(json_str.encode('utf-8'), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
    
    # 步骤3: Base64编码
    final_pwd = base64.b64encode(encrypted_b64.encode('utf-8')).decode('utf-8')
    
    return final_pwd

# 使用示例
password = "password****"
encrypted_pwd = encrypt_password(password)
print("加密后的密码:", encrypted_pwd)
```

---

## 8. 完整调用流程示例

### 8.1 使用 curl 完整调用流程

以下示例使用老生账号（2023****0000）演示，该账号有完整的课表和成绩数据。

```bash
# ============================================
# 1. 加密密码（使用Node.js + crypto-js）
# ============================================
ENCRYPTED_PWD=$(node -e "
const CryptoJS = require('crypto-js');
const key = CryptoJS.enc.Utf8.parse('qzkj1kjghd=876&*');
const jsonStr = JSON.stringify('password****');
const encrypted = CryptoJS.AES.encrypt(jsonStr, key, {
    mode: CryptoJS.mode.ECB,
    padding: CryptoJS.pad.Pkcs7
}).toString();
console.log(Buffer.from(encrypted).toString('base64'));
")

# ============================================
# 2. 登录获取Token
# ============================================
LOGIN_RESPONSE=$(curl -s -X POST \
  "http://222.243.161.213:81/hnrjzyxyhd/login?userNo=2023****0000&pwd=${ENCRYPTED_PWD}&encode=1")

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['token'])")

echo "登录成功，获取到Token: ${TOKEN:0:50}..."

# ============================================
# 3. 校验Token有效性
# ============================================
echo ""
echo "=== 个人信息（Token有效性校验） ==="
curl -s -X POST "http://222.243.161.213:81/hnrjzyxyhd/initUserInfo2" \
  -H "token: $TOKEN" | python3 -m json.tool

# ============================================
# 4. 获取个人信息
# ============================================
echo ""
echo "=== 个人信息（查询个人信息） ==="
curl -s -X POST "http://222.243.161.213:81/hnrjzyxyhd/student/my" \
  -H "token: $TOKEN" | python3 -m json.tool

# ============================================
# 5. 获取当前学期
# ============================================
echo ""
echo "=== 当前学期 ==="
CURRENT_SEMESTER=$(curl -s -X POST "http://222.243.161.213:81/hnrjzyxyhd/currentTerm" \
  -H "token: $TOKEN" | python3 -c "import json,sys; print(json.load(sys.stdin)['data'][0]['semesterId'])")
echo "当前学期: $CURRENT_SEMESTER"

# ============================================
# 6. 获取所有可查询学期列表
# ============================================
echo ""
echo "=== 学期列表 ==="
curl -s -X POST "http://222.243.161.213:81/hnrjzyxyhd/semesterList" \
  -H "token: $TOKEN" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for sem in data['data']:
    current = ' [当前]' if sem['isdqxq'] == '1' else ''
    print(f\"  {sem['semesterId']}{current}\")
"

# ============================================
# 7. 获取时间模式（课表查询前置）
# ============================================
KBJCMSID=$(curl -s -X POST "http://222.243.161.213:81/hnrjzyxyhd/Get_sjkbms" \
  -H "token: $TOKEN" | python3 -c "import json,sys; print(json.load(sys.stdin)['data'][0]['kbjcmsid'])")
echo ""
echo "时间模式ID: $KBJCMSID"

# ============================================
# 8. 获取教学周次列表（课表查询前置）
# ============================================
echo ""
echo "=== 教学周次 ==="
curl -s -X POST "http://222.243.161.213:81/hnrjzyxyhd/teachingWeek" \
  -H "token: $TOKEN" | python3 -c "
import json, sys
data = json.load(sys.stdin)
weeks = [d['week'] for d in data['data']]
print(f'共 {len(weeks)} 周: {weeks}')
"

# ============================================
# 9. 获取课程表（全部周次）
# ============================================
echo ""
echo "=== 课程表（全部周次）==="
curl -s -X POST "http://222.243.161.213:81/hnrjzyxyhd/student/curriculum?week=all&kbjcmsid=${KBJCMSID}" \
  -H "token: $TOKEN" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data.get('data') and len(data['data']) > 0:
    courses = data['data'][0].get('courses', [])
    print(f'共 {len(courses)} 门课程:')
    for c in courses[:5]:
        print(f\"  {c['courseName']} | 周{c['classWeek']} | 星期{c['weekDay']} | {c['startTime']}-{c['endTIme']} | {c.get('location','')}\")
    if len(courses) > 5:
        print(f'  ... 还有 {len(courses)-5} 门课程')
else:
    print('暂无课表数据')
"

# ============================================
# 10. 获取课程表（指定周次，如第1周）
# ============================================
echo ""
echo "=== 课程表（第1周）==="
curl -s -X POST "http://222.243.161.213:81/hnrjzyxyhd/student/curriculum?week=1&kbjcmsid=${KBJCMSID}" \
  -H "token: $TOKEN" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data.get('data') and len(data['data']) > 0:
    courses = data['data'][0].get('courses', [])
    print(f'第1周共 {len(courses)} 门课程')
else:
    print('第1周暂无课程')
"

# ============================================
# 11. 获取学生成绩（所有学期）
# ============================================
echo ""
echo "=== 学生成绩（所有学期）==="
curl -s -X POST "http://222.243.161.213:81/hnrjzyxyhd/student/termGPA" \
  -H "token: $TOKEN" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data.get('data') and len(data['data']) > 0:
    achievements = data['data'][0].get('achievement', [])
    # 按学期统计
    semesters = {}
    for cj in achievements:
        sem = cj.get('curSemesterName', '')
        if sem not in semesters:
            semesters[sem] = []
        semesters[sem].append(cj)
    print(f'共 {len(achievements)} 条成绩记录，涵盖 {len(semesters)} 个学期:')
    for sem, courses in sorted(semesters.items()):
        print(f'  {sem}: {len(courses)}门课')
    # 显示前3条成绩
    print(f'\n前3条成绩:')
    for cj in achievements[:3]:
        print(f\"  {cj['courseName']} | {cj['curSemesterName']} | {cj['fraction']}分 | {cj['credit']}学分 | {cj['examinationNature']}\")
else:
    print('暂无成绩数据')
"

# ============================================
# 12. 获取学生成绩（指定学期，如2023-2024-1）
# ============================================
echo ""
echo "=== 学生成绩（2023-2024-1学期）==="
curl -s -X POST "http://222.243.161.213:81/hnrjzyxyhd/student/termGPA?semester=2023-2024-1" \
  -H "token: $TOKEN" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data.get('data') and len(data['data']) > 0:
    achievements = data['data'][0].get('achievement', [])
    print(f'2023-2024-1学期共 {len(achievements)} 门课:')
    for cj in achievements[:5]:
        print(f\"  {cj['courseName']} | {cj['fraction']}分 | {cj['credit']}学分 | {cj['examinationNature']}\")
    if len(achievements) > 5:
        print(f'  ... 还有 {len(achievements)-5} 门课')
else:
    print('该学期暂无成绩')
"
```

### 8.2 接口调用顺序总结

| 步骤 | 接口 | 用途 | 是否必须 |
|------|------|------|----------|
| 1 | `POST /login` | 登录获取Token | 必须 |
| 2 | `POST /initUserInfo2` | 校验Token有效性 | 可选 |
| 2 | `POST /student/my` | 获取个人信息 | 可选 |
| 3 | `POST /currentTerm` | 获取当前学期 | 可选 |
| 4 | `POST /semesterList` | 获取所有学期列表 | 可选（成绩筛选时有用） |
| 5 | `POST /Get_sjkbms` | 获取时间模式ID | 课表查询必须 |
| 6 | `POST /teachingWeek` | 获取教学周次列表 | 可选（课表周次选择时有用） |
| 7 | `POST /student/curriculum` | 获取学生课表 | 课表查询必须 |
| 8 | `POST /student/termGPA` | 获取学生成绩 | 成绩查询必须 |

---

## 9. 错误码说明

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 1 | 成功 | - |
| 0 | 失败 | 查看Msg字段的具体错误信息 |
| 401 | 未授权/非法访问 | 检查Token是否正确、是否过期，重新登录 |
| 404 | 接口不存在 | 检查接口地址是否正确 |

### 常见错误信息

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| 该帐号不存在或密码错误！ | 学号或密码错误 | 检查学号和密码是否正确，确认密码加密算法是否正确 |
| 登录失败！ | 密码加密格式错误 | 检查pwd参数是否经过正确的加密和Base64编码 |
| 未授权访问：/xxx | Token无效或过期 | 重新登录获取新的Token |
| 非法访问：/xxx | 请求头格式错误 | 检查token请求头是否正确设置 |

---

## 10. 注意事项

1. **网络访问**：该系统部署在内网/校园网环境，需确保网络可达，不要使用代理访问。

2. **Token管理**：Token具有时效性，建议在每次调用前检查Token有效性，失效时重新登录。

3. **密码安全**：加密密钥为固定值，请勿泄露；传输过程中建议使用HTTPS（当前系统为HTTP）。

4. **请求频率**：请勿频繁调用接口，避免对服务器造成压力。

5. **数据时效性**：课表、成绩等数据可能随时间更新，建议按需查询。

6. **新生数据**：新入学学生在开学初期可能暂无课表、成绩等数据，属正常现象。

7. **接口权限**：学生端核心接口（课表、成绩等）均以 `/student/` 开头，系统根据Token自动识别学生身份，无需传入学号等参数。部分以 `/teacher/` 开头的接口为教师端管理接口，学生用户可能无法访问或只能查看本人数据。

8. **数据差异**：新生（如2026级）在开学初期可能暂无课表、成绩等数据；老生（如2023级）通常有完整的历史数据。接口返回空数组属正常现象，不代表接口异常。

---

**文档版本**：v1.1  
**更新日期**：2026-09-13  
**测试账号**：
- 新生账号：2026****0000（张某某，人工智能(专升本)****班，2026级）
- 老生账号：2023****0000（张某某，计算机应用技术****班，2023级，有完整历史成绩数据）