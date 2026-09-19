# -*- coding: utf-8 -*-
"""
移动教务系统 API 模拟服务器
基于 Flask + SQLite + JWT
仿湖南软件职业技术大学移动教务系统接口
"""
import os
import json
import base64
import time
import uuid
from datetime import datetime, timedelta, timezone

from flask import Flask, request, jsonify, g, session, send_from_directory
import jwt
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from database import init_db, seed_data, get_conn

# ==================== 配置 ====================
app = Flask(__name__)
app.secret_key = 'edu_admin_secret_key_2026'
app.config['SESSION_COOKIE_NAME'] = 'admin_session'

# JWT 配置
JWT_SECRET = 'edu_system_jwt_secret_key_2026'
JWT_ALGORITHM = 'HS512'
JWT_EXPIRE_HOURS = 4

# AES 配置（与文档一致）
AES_KEY = b'qzkj1kjghd=876&*'

# 学校代码
SCHOOL_CODE = '4711'

# ==================== 工具函数 ====================

def decrypt_password(encrypted_pwd: str) -> str:
    """
    解密登录密码
    加密流程: 原始密码 -> JSON.stringify -> AES-ECB加密 -> Base64 -> 再次Base64
    解密流程: Base64解码 -> Base64解码 -> AES-ECB解密 -> JSON解析
    """
    try:
        # 步骤1: 第一次Base64解码，得到AES密文的Base64字符串
        first_decode = base64.b64decode(encrypted_pwd).decode('utf-8')
        # 步骤2: 第二次Base64解码，得到AES加密字节
        encrypted_bytes = base64.b64decode(first_decode)
        # 步骤3: AES-ECB解密
        cipher = AES.new(AES_KEY, AES.MODE_ECB)
        decrypted_padded = cipher.decrypt(encrypted_bytes)
        # 步骤4: 去除PKCS7填充
        decrypted_bytes = unpad(decrypted_padded, AES.block_size)
        json_str = decrypted_bytes.decode('utf-8')
        # 步骤5: JSON解析，得到原始密码（JSON.stringify会给字符串加双引号）
        original_password = json.loads(json_str)
        return original_password
    except Exception as e:
        # 解密失败，尝试直接作为明文密码处理（兼容测试）
        return encrypted_pwd


def generate_token(user_no: str) -> str:
    """生成JWT Token"""
    now = datetime.now(timezone.utc)
    payload = {
        'aud': user_no,
        'exp': int((now + timedelta(hours=JWT_EXPIRE_HOURS)).timestamp() * 1000),
        'iat': int(now.timestamp() * 1000)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> dict:
    """
    验证JWT Token，返回payload或None
    兼容毫秒级时间戳（与原系统token格式一致）
    """
    try:
        # 禁用 exp/iat/aud 自动验证，因为原系统使用毫秒级时间戳且aud为学号
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM],
                             options={'verify_exp': False, 'verify_iat': False,
                                      'verify_aud': False})
        # 手动检查过期时间（兼容毫秒级和秒级）
        exp = payload.get('exp', 0)
        if exp > 1e12:
            # 毫秒级时间戳
            now = int(time.time() * 1000)
        else:
            # 秒级时间戳
            now = int(time.time())
        if exp > now:
            return payload
        return None
    except Exception:
        return None


def get_user_from_token() -> dict:
    """从请求头的token中获取用户信息，失败返回None"""
    token = request.headers.get('token', '')
    if not token:
        return None
    payload = verify_token(token)
    if not payload:
        return None
    user_no = payload.get('aud', '')
    if not user_no:
        return None
    # 从数据库查询用户
    conn = get_conn()
    user = conn.execute('SELECT * FROM users WHERE user_no = ?', (user_no,)).fetchone()
    conn.close()
    if not user:
        return None
    return dict(user)


def success_response(data, msg='success', code='1'):
    """通用成功响应"""
    return jsonify({'code': code, 'Msg': msg, 'data': data})


def error_response(msg='操作失败', code='0'):
    """通用错误响应"""
    return jsonify({'code': code, 'Msg': msg, 'data': {}})


# ==================== 认证中间件 ====================

@app.before_request
def auth_middleware():
    """认证中间件：学生API需要验证token，管理后台使用自己的session认证"""
    # 学生登录接口不需要认证
    if request.path == '/login':
        return None
    # 管理后台所有路径跳过学生token验证（使用自己的session认证）
    if request.path.startswith('/admin'):
        return None
    # OPTIONS 请求不需要认证
    if request.method == 'OPTIONS':
        return None
    # 验证token
    token = request.headers.get('token', '')
    if not token:
        return jsonify({'code': '0', 'Msg': f'非法访问：{request.path}', 'data': {}}), 200
    payload = verify_token(token)
    if not payload:
        return jsonify({'code': '0', 'Msg': f'未授权访问：{request.path}', 'data': {}}), 200
    # 将用户信息存入g
    user_no = payload.get('aud', '')
    conn = get_conn()
    user = conn.execute('SELECT * FROM users WHERE user_no = ?', (user_no,)).fetchone()
    conn.close()
    if not user:
        return jsonify({'code': '0', 'Msg': f'未授权访问：{request.path}', 'data': {}}), 200
    g.current_user = dict(user)
    return None


# ==================== 接口实现 ====================

@app.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    user_no = request.args.get('userNo', '')
    pwd = request.args.get('pwd', '')
    encode = request.args.get('encode', '')

    if not user_no or not pwd:
        return error_response('该帐号不存在或密码错误！')

    # 查询用户
    conn = get_conn()
    user = conn.execute('SELECT * FROM users WHERE user_no = ?', (user_no,)).fetchone()
    conn.close()

    if not user:
        return error_response('该帐号不存在或密码错误！')

    # 解密密码
    if encode == '1':
        input_password = decrypt_password(pwd)
    else:
        input_password = pwd

    # 验证密码
    if input_password != user['password']:
        return error_response('该帐号不存在或密码错误！')

    # 生成token
    token = generate_token(user['user_no'])

    data = {
        'birthday': user['birthday'],
        'academyName': user['academy_name'],
        'userNo': user['user_no'],
        'entranceYear': user['entrance_year'],
        'clsName': user['cls_name'],
        'name': user['name'],
        'userType': user['user_type'],
        'token': token
    }
    return jsonify({'code': '1', 'Msg': '登录成功！', 'data': data})


@app.route('/initUserInfo2', methods=['POST'])
def init_user_info2():
    """
    校验Token有效性 / 获取用户基本信息
    注意：此接口直接返回数据对象，不包含 code/Msg 包装
    """
    user = g.current_user
    token = request.headers.get('token', '')
    data = {
        'birthday': user['birthday'],
        'academyName': user['academy_name'],
        'userNo': user['user_no'],
        'entranceYear': user['entrance_year'],
        'clsName': user['cls_name'],
        'name': user['name'],
        'userType': user['user_type'],
        'token': token
    }
    return jsonify(data)


@app.route('/student/my', methods=['POST'])
def student_my():
    """获取学生详细个人信息"""
    user = g.current_user
    data = [{
        'ksh': '',
        'sfzjh': '',
        'gender': user['gender'],
        'dh': user['phone'],
        'className': user['cls_name'],
        'idno': user['idno'],
        'studentID': user['user_no'],
        'inGrade': user['in_grade'],
        'school': user['school'],
        'name': user['name'],
        'majorName': user['major_name'],
        'dateBirth': user['birthday'],
        'sfzczxkt': user['sfzczxkt'],
        'academy': user['academy_name'],
        'trainingLevel': user['training_level']
    }]
    return jsonify({'Msg': 'success', 'code': '1', 'data': data})


@app.route('/Get_sjkbms', methods=['POST'])
def get_sjkbms():
    """获取时间模式列表"""
    conn = get_conn()
    modes = conn.execute('SELECT * FROM time_modes').fetchall()
    conn.close()
    data = []
    for m in modes:
        data.append({
            'mrms': m['mrms'],
            'kbjcmsid': m['kbjcmsid'],
            'kbjcmsmc': m['kbjcmsmc']
        })
    # 注意：此接口 code 为数字 1，msg 为小写
    return jsonify({'msg': 'success', 'code': 1, 'data': data})


@app.route('/teachingWeek', methods=['POST'])
def teaching_week():
    """获取教学周次列表（从数据库读取，支持按学期查询）"""
    semester = request.args.get('semester', '')

    # 如果未指定学期，使用当前学期
    if not semester:
        conn = get_conn()
        current = conn.execute("SELECT semester_id FROM semesters WHERE is_current = '1'").fetchone()
        conn.close()
        semester = current['semester_id'] if current else '2026-2027-1'

    # 从数据库读取该学期的周次
    conn = get_conn()
    weeks = conn.execute(
        'SELECT week_number FROM teaching_weeks WHERE semester_id = ? ORDER BY week_number',
        (semester,)
    ).fetchall()
    conn.close()

    if weeks:
        data = [{'week': str(w['week_number'])} for w in weeks]
    else:
        # 数据库中没有配置时，回退到固定20周
        data = [{'week': str(i)} for i in range(1, 21)]

    return jsonify({'code': '1', 'Msg': 'success', 'data': data})


@app.route('/student/curriculum', methods=['POST'])
def student_curriculum():
    """获取学生课表"""
    user = g.current_user
    week = request.args.get('week', 'all')
    kbjcmsid = request.args.get('kbjcmsid', '')

    if not week or not kbjcmsid:
        return error_response('参数不完整')

    # 查询课程
    conn = get_conn()
    # 获取当前学期
    current_sem = conn.execute("SELECT * FROM semesters WHERE is_current = '1'").fetchone()
    semester_id = current_sem['semester_id'] if current_sem else '2026-2027-1'

    courses = conn.execute(
        'SELECT * FROM courses WHERE user_no = ? AND semester_id = ?',
        (user['user_no'], semester_id)
    ).fetchall()
    conn.close()

    # 按周次过滤
    filtered_courses = []
    for c in courses:
        if week == 'all':
            filtered_courses.append(c)
        else:
            # 检查该周是否在上课周次中
            week_details = c['class_week_details'] or ''
            if f',{week},' in week_details:
                filtered_courses.append(c)

    # 构建课程列表
    course_list = []
    for c in filtered_courses:
        course_list.append({
            'classWeek': c['class_week'],
            'teacherName': c['teacher_name'] or '',
            'weekNoteDetail': c['week_note_detail'] or '',
            'buttonCode': c['button_code'] or '0',
            'xkrs': c['xkrs'] or 0,
            'ktmc': c['ktmc'] or '',
            'classTime': c['class_time'] or '',
            'classroomNub': c['classroom_nub'] or '',
            'jx0408id': c['jx0408id'] or '',
            'buildingName': c['building_name'] or '',
            'courseName': c['course_name'] or '',
            'isRepeatCode': c['is_repeat_code'] or '0',
            'jx0404id': c['jx0404id'] or '',
            'weekDay': c['week_day'] or '',
            'classroomName': c['classroom_name'] or '',
            'khfs': c['khfs'] or '',
            'startTime': c['start_time'] or '',
            'endTIme': c['end_time'] or '',
            'location': c['location'] or '',
            'fzmc': c['fzmc'] or '',
            'classWeekDetails': c['class_week_details'] or '',
            'coursesNote': c['courses_note'] or 0
        })

    # 构建日期数组（周一到周日）
    date_list = [
        {'xqmc': '一', 'mxrq': '', 'zc': week, 'xqid': '1', 'rq': ''},
        {'xqmc': '二', 'mxrq': '', 'zc': week, 'xqid': '2', 'rq': ''},
        {'xqmc': '三', 'mxrq': '', 'zc': week, 'xqid': '3', 'rq': ''},
        {'xqmc': '四', 'mxrq': '', 'zc': week, 'xqid': '4', 'rq': ''},
        {'xqmc': '五', 'mxrq': '', 'zc': week, 'xqid': '5', 'rq': ''},
        {'xqmc': '六', 'mxrq': '', 'zc': week, 'xqid': '6', 'rq': ''},
        {'xqmc': '日', 'mxrq': '', 'zc': week, 'xqid': '0', 'rq': ''}
    ]

    data = [{
        'date': date_list,
        'courses': course_list,
        'nodesLst': [],
        'item': {},
        'week': week,
        'nodes': [],
        'weekday': [],
        'bz': '',
        'topInfo': {}
    }]
    return jsonify({'Msg': 'success~', 'code': '1', 'data': data})


@app.route('/student/termGPA', methods=['POST'])
def student_term_gpa():
    """获取学生学期成绩"""
    user = g.current_user
    semester = request.args.get('semester', '')

    conn = get_conn()
    if semester:
        grades = conn.execute(
            'SELECT * FROM grades WHERE user_no = ? AND cur_semester_name = ? ORDER BY cur_semester_name, id',
            (user['user_no'], semester)
        ).fetchall()
    else:
        grades = conn.execute(
            'SELECT * FROM grades WHERE user_no = ? ORDER BY cur_semester_name, id',
            (user['user_no'],)
        ).fetchall()
    conn.close()

    achievement = []
    for row in grades:
        achievement.append({
            'curriculumAttributes': row['curriculum_attributes'] or '',
            'courseName': row['course_name'] or '',
            'curSemesterName': row['cur_semester_name'] or '',
            'courseNature': row['course_nature'] or '',
            'examinationNature': row['examination_nature'] or '',
            'kcbh': row['kcbh'] or '',
            'credit': row['credit'] or 0,
            'cj0708id': row['cj0708id'] or '',
            'fraction': row['fraction'] or ''
        })

    data = [{
        'studentID': user['user_no'],
        'xqgpa': [],
        'pjcj': '',
        'achievement': achievement
    }]
    return jsonify({'Msg': 'success', 'code': '1', 'data': data})


@app.route('/currentTerm', methods=['POST'])
def current_term():
    """获取当前学期"""
    conn = get_conn()
    sem = conn.execute("SELECT * FROM semesters WHERE is_current = '1'").fetchone()
    conn.close()
    if sem:
        data = [{'semesterId': sem['semester_id'], 'semesterName': sem['semester_name']}]
    else:
        data = [{'semesterId': '2026-2027-1', 'semesterName': '2026-2027-1'}]
    return jsonify({'code': '1', 'Msg': 'success', 'data': data})


@app.route('/semesterList', methods=['POST'])
def semester_list():
    """获取学期列表（根据学生入学年份过滤，只返回入学年份及之后的学期）"""
    user = g.current_user
    entrance_year = user.get('entrance_year', '') or user.get('in_grade', '')

    conn = get_conn()
    semesters = conn.execute('SELECT * FROM semesters ORDER BY semester_id DESC').fetchall()
    conn.close()

    data = []
    for s in semesters:
        # 学期ID格式 "YYYY-YYYY-N"，提取起始年份
        sem_id = s['semester_id']
        try:
            sem_start_year = int(sem_id.split('-')[0])
        except (ValueError, IndexError):
            sem_start_year = 0

        # 如果有入学年份，过滤：只返回起始年份 >= 入学年份的学期
        if entrance_year:
            try:
                ent_year = int(entrance_year)
                if sem_start_year < ent_year:
                    continue
            except ValueError:
                pass

        data.append({
            'isdqxq': s['is_current'],
            'semesterId': s['semester_id'],
            'semesterName': s['semester_name']
        })
    return jsonify({'code': '1', 'Msg': 'success', 'data': data})


# ==================== 后台管理系统 ====================

def admin_required(f):
    """管理员登录认证装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_user'):
            return jsonify({'code': 0, 'msg': '未登录或登录已过期', 'data': {}}), 401
        return f(*args, **kwargs)
    return decorated


@app.route('/admin')
def admin_page():
    """管理后台页面"""
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
                               'admin.html')


@app.route('/admin/api/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    data = request.get_json(silent=True) or request.form
    username = data.get('username', '')
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'code': 0, 'msg': '用户名和密码不能为空', 'data': {}})

    conn = get_conn()
    admin = conn.execute('SELECT * FROM admins WHERE username = ?', (username,)).fetchone()
    conn.close()

    if not admin or admin['password'] != password:
        return jsonify({'code': 0, 'msg': '用户名或密码错误', 'data': {}})

    session['admin_user'] = admin['username']
    session['admin_name'] = admin['name']
    return jsonify({'code': 1, 'msg': '登录成功', 'data': {
        'username': admin['username'],
        'name': admin['name']
    }})


@app.route('/admin/api/logout', methods=['POST'])
def admin_logout():
    """管理员登出"""
    session.clear()
    return jsonify({'code': 1, 'msg': '已退出登录', 'data': {}})


@app.route('/admin/api/stats', methods=['GET'])
@admin_required
def admin_stats():
    """数据统计"""
    conn = get_conn()
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    course_count = conn.execute('SELECT COUNT(*) FROM courses').fetchone()[0]
    grade_count = conn.execute('SELECT COUNT(*) FROM grades').fetchone()[0]
    semester_count = conn.execute('SELECT COUNT(*) FROM semesters').fetchone()[0]

    # 按学院统计用户数
    academy_stats = conn.execute(
        'SELECT academy_name, COUNT(*) as cnt FROM users GROUP BY academy_name ORDER BY cnt DESC'
    ).fetchall()

    # 按学期统计成绩数
    grade_by_sem = conn.execute(
        'SELECT cur_semester_name, COUNT(*) as cnt FROM grades GROUP BY cur_semester_name ORDER BY cur_semester_name'
    ).fetchall()
    conn.close()

    return jsonify({'code': 1, 'msg': 'success', 'data': {
        'user_count': user_count,
        'course_count': course_count,
        'grade_count': grade_count,
        'semester_count': semester_count,
        'academy_stats': [{'name': r['academy_name'], 'count': r['cnt']} for r in academy_stats],
        'grade_by_semester': [{'semester': r['cur_semester_name'], 'count': r['cnt']} for r in grade_by_sem]
    }})


# ---------- 用户管理 ----------

@app.route('/admin/api/users', methods=['GET'])
@admin_required
def admin_users_list():
    """用户列表"""
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    offset = (page - 1) * page_size

    conn = get_conn()
    if keyword:
        like = f'%{keyword}%'
        total = conn.execute(
            'SELECT COUNT(*) FROM users WHERE user_no LIKE ? OR name LIKE ? OR cls_name LIKE ?',
            (like, like, like)
        ).fetchone()[0]
        users = conn.execute(
            'SELECT * FROM users WHERE user_no LIKE ? OR name LIKE ? OR cls_name LIKE ? ORDER BY user_no LIMIT ? OFFSET ?',
            (like, like, like, page_size, offset)
        ).fetchall()
    else:
        total = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        users = conn.execute('SELECT * FROM users ORDER BY user_no LIMIT ? OFFSET ?',
                             (page_size, offset)).fetchall()
    conn.close()

    return jsonify({'code': 1, 'msg': 'success', 'data': {
        'total': total,
        'page': page,
        'page_size': page_size,
        'list': [dict(u) for u in users]
    }})


@app.route('/admin/api/users', methods=['POST'])
@admin_required
def admin_user_create():
    """新增用户"""
    data = request.get_json(silent=True) or request.form
    required = ['user_no', 'password', 'name']
    for f in required:
        if not data.get(f):
            return jsonify({'code': 0, 'msg': f'{f} 不能为空', 'data': {}})

    conn = get_conn()
    exists = conn.execute('SELECT COUNT(*) FROM users WHERE user_no = ?', (data['user_no'],)).fetchone()[0]
    if exists:
        conn.close()
        return jsonify({'code': 0, 'msg': '学号已存在', 'data': {}})

    conn.execute('''INSERT INTO users (user_no, password, name, birthday, gender, idno, phone,
        user_type, academy_name, cls_name, major_name, entrance_year, training_level, school, in_grade, sfzczxkt)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        data['user_no'], data['password'], data.get('name', ''),
        data.get('birthday', ''), data.get('gender', ''), data.get('idno', ''),
        data.get('phone', ''), data.get('user_type', '2'), data.get('academy_name', ''),
        data.get('cls_name', ''), data.get('major_name', ''), data.get('entrance_year', ''),
        data.get('training_level', ''), data.get('school', '湖南软件职业技术大学'),
        data.get('in_grade', ''), data.get('sfzczxkt', '1')
    ))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '添加成功', 'data': {}})


@app.route('/admin/api/users/<user_no>', methods=['PUT'])
@admin_required
def admin_user_update(user_no):
    """更新用户"""
    data = request.get_json(silent=True) or request.form
    conn = get_conn()
    exists = conn.execute('SELECT COUNT(*) FROM users WHERE user_no = ?', (user_no,)).fetchone()[0]
    if not exists:
        conn.close()
        return jsonify({'code': 0, 'msg': '用户不存在', 'data': {}})

    fields = ['password', 'name', 'birthday', 'gender', 'idno', 'phone', 'user_type',
              'academy_name', 'cls_name', 'major_name', 'entrance_year', 'training_level',
              'school', 'in_grade', 'sfzczxkt']
    updates = []
    values = []
    for f in fields:
        if f in data:
            updates.append(f'{f} = ?')
            values.append(data[f])
    if updates:
        values.append(user_no)
        conn.execute(f'UPDATE users SET {", ".join(updates)} WHERE user_no = ?', values)
        conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '更新成功', 'data': {}})


@app.route('/admin/api/users/<user_no>', methods=['DELETE'])
@admin_required
def admin_user_delete(user_no):
    """删除用户"""
    conn = get_conn()
    conn.execute('DELETE FROM users WHERE user_no = ?', (user_no,))
    conn.execute('DELETE FROM courses WHERE user_no = ?', (user_no,))
    conn.execute('DELETE FROM grades WHERE user_no = ?', (user_no,))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '删除成功', 'data': {}})


# ---------- 课程管理 ----------

@app.route('/admin/api/courses', methods=['GET'])
@admin_required
def admin_courses_list():
    """课程列表"""
    keyword = request.args.get('keyword', '')
    user_no = request.args.get('user_no', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    offset = (page - 1) * page_size

    conn = get_conn()
    where = []
    params = []
    if keyword:
        where.append('(course_name LIKE ? OR teacher_name LIKE ?)')
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if user_no:
        where.append('user_no = ?')
        params.append(user_no)
    where_sql = f'WHERE {" AND ".join(where)}' if where else ''

    total = conn.execute(f'SELECT COUNT(*) FROM courses {where_sql}', params).fetchone()[0]
    courses = conn.execute(
        f'SELECT * FROM courses {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?',
        params + [page_size, offset]
    ).fetchall()
    conn.close()

    return jsonify({'code': 1, 'msg': 'success', 'data': {
        'total': total, 'page': page, 'page_size': page_size,
        'list': [dict(c) for c in courses]
    }})


@app.route('/admin/api/courses', methods=['POST'])
@admin_required
def admin_course_create():
    """新增课程"""
    d = request.get_json(silent=True) or request.form
    required = ['user_no', 'semester_id', 'course_name']
    for f in required:
        if not d.get(f):
            return jsonify({'code': 0, 'msg': f'{f} 不能为空', 'data': {}})

    conn = get_conn()
    conn.execute('''INSERT INTO courses (user_no, semester_id, course_name, teacher_name,
        class_week, class_week_details, week_day, start_time, end_time, class_time,
        week_note_detail, classroom_name, classroom_nub, building_name, location,
        ktmc, khfs, xkrs, jx0404id, jx0408id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (
        d['user_no'], d['semester_id'], d['course_name'], d.get('teacher_name', ''),
        d.get('class_week', ''), d.get('class_week_details', ''), d.get('week_day', ''),
        d.get('start_time', ''), d.get('end_time', ''), d.get('class_time', ''),
        d.get('week_note_detail', ''), d.get('classroom_name', ''), d.get('classroom_nub', ''),
        d.get('building_name', ''), d.get('location', ''), d.get('ktmc', ''),
        d.get('khfs', ''), d.get('xkrs', 0), d.get('jx0404id', ''), d.get('jx0408id', '')
    ))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '添加成功', 'data': {}})


@app.route('/admin/api/courses/<int:cid>', methods=['PUT'])
@admin_required
def admin_course_update(cid):
    """更新课程"""
    d = request.get_json(silent=True) or request.form
    conn = get_conn()
    exists = conn.execute('SELECT COUNT(*) FROM courses WHERE id = ?', (cid,)).fetchone()[0]
    if not exists:
        conn.close()
        return jsonify({'code': 0, 'msg': '课程不存在', 'data': {}})

    fields = ['user_no', 'semester_id', 'course_name', 'teacher_name', 'class_week',
              'class_week_details', 'week_day', 'start_time', 'end_time', 'class_time',
              'week_note_detail', 'classroom_name', 'classroom_nub', 'building_name',
              'location', 'ktmc', 'khfs', 'xkrs', 'jx0404id', 'jx0408id']
    updates = []
    values = []
    for f in fields:
        if f in d:
            updates.append(f'{f} = ?')
            values.append(d[f])
    if updates:
        values.append(cid)
        conn.execute(f'UPDATE courses SET {", ".join(updates)} WHERE id = ?', values)
        conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '更新成功', 'data': {}})


@app.route('/admin/api/courses/<int:cid>', methods=['DELETE'])
@admin_required
def admin_course_delete(cid):
    """删除课程"""
    conn = get_conn()
    conn.execute('DELETE FROM courses WHERE id = ?', (cid,))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '删除成功', 'data': {}})


# ---------- 成绩管理 ----------

@app.route('/admin/api/grades', methods=['GET'])
@admin_required
def admin_grades_list():
    """成绩列表"""
    keyword = request.args.get('keyword', '')
    user_no = request.args.get('user_no', '')
    semester = request.args.get('semester', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    offset = (page - 1) * page_size

    conn = get_conn()
    where = []
    params = []
    if keyword:
        where.append('(course_name LIKE ? OR user_no LIKE ?)')
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if user_no:
        where.append('user_no = ?')
        params.append(user_no)
    if semester:
        where.append('cur_semester_name = ?')
        params.append(semester)
    where_sql = f'WHERE {" AND ".join(where)}' if where else ''

    total = conn.execute(f'SELECT COUNT(*) FROM grades {where_sql}', params).fetchone()[0]
    grades = conn.execute(
        f'SELECT * FROM grades {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?',
        params + [page_size, offset]
    ).fetchall()
    conn.close()

    return jsonify({'code': 1, 'msg': 'success', 'data': {
        'total': total, 'page': page, 'page_size': page_size,
        'list': [dict(g) for g in grades]
    }})


@app.route('/admin/api/grades', methods=['POST'])
@admin_required
def admin_grade_create():
    """新增成绩"""
    d = request.get_json(silent=True) or request.form
    required = ['user_no', 'course_name', 'cur_semester_name']
    for f in required:
        if not d.get(f):
            return jsonify({'code': 0, 'msg': f'{f} 不能为空', 'data': {}})

    conn = get_conn()
    cj_id = uuid.uuid4().hex.upper()
    conn.execute('''INSERT INTO grades (user_no, curriculum_attributes, course_name,
        cur_semester_name, course_nature, examination_nature, kcbh, credit, cj0708id, fraction)
        VALUES (?,?,?,?,?,?,?,?,?,?)''', (
        d['user_no'], d.get('curriculum_attributes', '必修'), d['course_name'],
        d['cur_semester_name'], d.get('course_nature', ''), d.get('examination_nature', '正常考试'),
        d.get('kcbh', ''), d.get('credit', 0), cj_id, d.get('fraction', '')
    ))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '添加成功', 'data': {}})


@app.route('/admin/api/grades/<int:gid>', methods=['PUT'])
@admin_required
def admin_grade_update(gid):
    """更新成绩"""
    d = request.get_json(silent=True) or request.form
    conn = get_conn()
    exists = conn.execute('SELECT COUNT(*) FROM grades WHERE id = ?', (gid,)).fetchone()[0]
    if not exists:
        conn.close()
        return jsonify({'code': 0, 'msg': '成绩记录不存在', 'data': {}})

    fields = ['user_no', 'curriculum_attributes', 'course_name', 'cur_semester_name',
              'course_nature', 'examination_nature', 'kcbh', 'credit', 'fraction']
    updates = []
    values = []
    for f in fields:
        if f in d:
            updates.append(f'{f} = ?')
            values.append(d[f])
    if updates:
        values.append(gid)
        conn.execute(f'UPDATE grades SET {", ".join(updates)} WHERE id = ?', values)
        conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '更新成功', 'data': {}})


@app.route('/admin/api/grades/<int:gid>', methods=['DELETE'])
@admin_required
def admin_grade_delete(gid):
    """删除成绩"""
    conn = get_conn()
    conn.execute('DELETE FROM grades WHERE id = ?', (gid,))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '删除成功', 'data': {}})


# ---------- 学期管理 ----------

@app.route('/admin/api/semesters', methods=['GET'])
@admin_required
def admin_semesters_list():
    """学期列表"""
    conn = get_conn()
    semesters = conn.execute('SELECT * FROM semesters ORDER BY semester_id DESC').fetchall()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': [dict(s) for s in semesters]})


@app.route('/admin/api/semesters', methods=['POST'])
@admin_required
def admin_semester_create():
    """新增学期"""
    d = request.get_json(silent=True) or request.form
    if not d.get('semester_id'):
        return jsonify({'code': 0, 'msg': 'semester_id 不能为空', 'data': {}})

    conn = get_conn()
    exists = conn.execute('SELECT COUNT(*) FROM semesters WHERE semester_id = ?', (d['semester_id'],)).fetchone()[0]
    if exists:
        conn.close()
        return jsonify({'code': 0, 'msg': '学期已存在', 'data': {}})

    conn.execute('INSERT INTO semesters (semester_id, semester_name, is_current) VALUES (?,?,?)',
                 (d['semester_id'], d.get('semester_name', d['semester_id']), d.get('is_current', '0')))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '添加成功', 'data': {}})


@app.route('/admin/api/semesters/<semester_id>', methods=['PUT'])
@admin_required
def admin_semester_update(semester_id):
    """更新学期"""
    d = request.get_json(silent=True) or request.form
    conn = get_conn()
    exists = conn.execute('SELECT COUNT(*) FROM semesters WHERE semester_id = ?', (semester_id,)).fetchone()[0]
    if not exists:
        conn.close()
        return jsonify({'code': 0, 'msg': '学期不存在', 'data': {}})

    # 如果设置为当前学期，先取消其他学期的当前标记
    if d.get('is_current') == '1':
        conn.execute("UPDATE semesters SET is_current = '0'")

    updates = []
    values = []
    if 'semester_name' in d:
        updates.append('semester_name = ?')
        values.append(d['semester_name'])
    if 'is_current' in d:
        updates.append('is_current = ?')
        values.append(d['is_current'])
    if updates:
        values.append(semester_id)
        conn.execute(f'UPDATE semesters SET {", ".join(updates)} WHERE semester_id = ?', values)
        conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '更新成功', 'data': {}})


@app.route('/admin/api/semesters/<semester_id>', methods=['DELETE'])
@admin_required
def admin_semester_delete(semester_id):
    """删除学期"""
    conn = get_conn()
    conn.execute('DELETE FROM semesters WHERE semester_id = ?', (semester_id,))
    conn.execute('DELETE FROM teaching_weeks WHERE semester_id = ?', (semester_id,))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '删除成功', 'data': {}})


# ---------- 周次管理 ----------

@app.route('/admin/api/weeks', methods=['GET'])
@admin_required
def admin_weeks_list():
    """获取某学期的周次列表"""
    semester_id = request.args.get('semester_id', '')
    if not semester_id:
        return jsonify({'code': 0, 'msg': 'semester_id 参数不能为空', 'data': {}})
    conn = get_conn()
    weeks = conn.execute(
        'SELECT * FROM teaching_weeks WHERE semester_id = ? ORDER BY week_number',
        (semester_id,)
    ).fetchall()
    conn.close()
    return jsonify({'code': 1, 'msg': 'success', 'data': [dict(w) for w in weeks]})


@app.route('/admin/api/weeks', methods=['POST'])
@admin_required
def admin_week_create():
    """新增周次"""
    d = request.get_json(silent=True) or request.form
    required = ['semester_id', 'week_number']
    for f in required:
        if not d.get(f):
            return jsonify({'code': 0, 'msg': f'{f} 不能为空', 'data': {}})

    conn = get_conn()
    conn.execute('''INSERT INTO teaching_weeks (semester_id, week_number, start_date, end_date, is_holiday, note)
        VALUES (?,?,?,?,?,?)''', (
        d['semester_id'], d['week_number'], d.get('start_date', ''),
        d.get('end_date', ''), d.get('is_holiday', '0'), d.get('note', '')
    ))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '添加成功', 'data': {}})


@app.route('/admin/api/weeks/<int:wid>', methods=['PUT'])
@admin_required
def admin_week_update(wid):
    """更新周次"""
    d = request.get_json(silent=True) or request.form
    conn = get_conn()
    exists = conn.execute('SELECT COUNT(*) FROM teaching_weeks WHERE id = ?', (wid,)).fetchone()[0]
    if not exists:
        conn.close()
        return jsonify({'code': 0, 'msg': '周次记录不存在', 'data': {}})

    fields = ['semester_id', 'week_number', 'start_date', 'end_date', 'is_holiday', 'note']
    updates = []
    values = []
    for f in fields:
        if f in d:
            updates.append(f'{f} = ?')
            values.append(d[f])
    if updates:
        values.append(wid)
        conn.execute(f'UPDATE teaching_weeks SET {", ".join(updates)} WHERE id = ?', values)
        conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '更新成功', 'data': {}})


@app.route('/admin/api/weeks/<int:wid>', methods=['DELETE'])
@admin_required
def admin_week_delete(wid):
    """删除周次"""
    conn = get_conn()
    conn.execute('DELETE FROM teaching_weeks WHERE id = ?', (wid,))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': '删除成功', 'data': {}})


@app.route('/admin/api/weeks/generate', methods=['POST'])
@admin_required
def admin_weeks_generate():
    """自动生成某学期的周次（根据开始日期和总周数）"""
    from datetime import datetime, timedelta
    d = request.get_json(silent=True) or request.form
    semester_id = d.get('semester_id', '')
    start_date_str = d.get('start_date', '')
    total_weeks = int(d.get('total_weeks', 20))

    if not semester_id or not start_date_str:
        return jsonify({'code': 0, 'msg': 'semester_id 和 start_date 不能为空', 'data': {}})

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'code': 0, 'msg': 'start_date 格式错误，应为 YYYY-MM-DD', 'data': {}})

    conn = get_conn()
    # 先删除该学期已有的周次
    conn.execute('DELETE FROM teaching_weeks WHERE semester_id = ?', (semester_id,))
    # 生成新的周次
    for week_num in range(1, total_weeks + 1):
        week_start = start_date + timedelta(weeks=week_num - 1)
        week_end = week_start + timedelta(days=6)
        conn.execute('''INSERT INTO teaching_weeks (semester_id, week_number, start_date, end_date, is_holiday, note)
            VALUES (?,?,?,?,?,?)''', (
            semester_id, week_num, week_start.strftime('%Y-%m-%d'),
            week_end.strftime('%Y-%m-%d'), '0', ''
        ))
    conn.commit()
    conn.close()
    return jsonify({'code': 1, 'msg': f'成功生成 {total_weeks} 周', 'data': {}})


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'code': '0', 'Msg': '接口不存在', 'data': {}}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'code': '0', 'Msg': '请求方法不允许', 'data': {}}), 405


# ==================== CORS 支持 ====================

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, token, Authorization'
    return response


# ==================== 启动 ====================

def main():
    # 初始化数据库
    init_db()
    seed_data()
    # 启动服务器
    port = int(os.environ.get('PORT', 5000))
    print('=' * 60)
    print('  移动教务系统 API 模拟服务器已启动')
    print('  学校代码: 4711')
    print(f'  API 地址: http://127.0.0.1:{port}')
    print(f'  管理后台: http://127.0.0.1:{port}/admin')
    print('  管理员账号: admin / Admin@2026')
    print('  学生测试账号:')
    print('    新生: 202609011001 / Demo@2026edu')
    print('    老生: 202309011002 / Demo@2026edu')
    print('=' * 60)
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
