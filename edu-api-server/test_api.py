# -*- coding: utf-8 -*-
"""
接口测试脚本
输出每个API接口的完整原始JSON数据
"""
import json
import base64
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

BASE_URL = 'http://127.0.0.1:5000'
AES_KEY = b'qzkj1kjghd=876&*'


def encrypt_password(password: str) -> str:
    """加密登录密码（与文档一致）"""
    json_str = json.dumps(password)
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    padded_data = pad(json_str.encode('utf-8'), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
    final_pwd = base64.b64encode(encrypted_b64.encode('utf-8')).decode('utf-8')
    return final_pwd


def print_response(title, resp):
    """打印完整的响应数据"""
    print('\n' + '=' * 70)
    print(title)
    print('=' * 70)
    print(f'请求地址: {resp.url}')
    print(f'状态码: {resp.status_code}')
    print('响应数据:')
    try:
        print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
    except Exception:
        print(resp.text)


def main():
    print('移动教务系统 API 模拟服务器 - 接口测试（完整原始数据）')
    print(f'服务器地址: {BASE_URL}')

    # ========== 1. 用户登录 ==========
    encrypted_pwd = encrypt_password('Demo@2026edu')
    resp = requests.post(f'{BASE_URL}/login', params={
        'userNo': '202309011002',
        'pwd': encrypted_pwd,
        'encode': '1'
    })
    print_response('【1】用户登录 POST /login', resp)
    try:
        token = resp.json()['data']['token']
    except Exception:
        print('登录失败，终止测试')
        return

    headers = {'token': token}

    # ========== 2. 校验Token /initUserInfo2 ==========
    resp = requests.post(f'{BASE_URL}/initUserInfo2', headers=headers)
    print_response('【2】校验Token POST /initUserInfo2', resp)

    # ========== 3. 学生详细信息 /student/my ==========
    resp = requests.post(f'{BASE_URL}/student/my', headers=headers)
    print_response('【3】学生详细信息 POST /student/my', resp)

    # ========== 4. 时间模式 /Get_sjkbms ==========
    resp = requests.post(f'{BASE_URL}/Get_sjkbms', headers=headers)
    print_response('【4】时间模式 POST /Get_sjkbms', resp)

    # ========== 5. 教学周次 /teachingWeek ==========
    resp = requests.post(f'{BASE_URL}/teachingWeek', headers=headers)
    print_response('【5】教学周次 POST /teachingWeek', resp)

    # ========== 6. 学生课表（全部周次）==========
    resp = requests.post(f'{BASE_URL}/student/curriculum',
                         params={'week': 'all', 'kbjcmsid': '63D5F875CCE34BF482A67EC5424EE1D1'},
                         headers=headers)
    print_response('【6】学生课表（全部周次）POST /student/curriculum?week=all', resp)

    # ========== 7. 学生课表（指定周次）==========
    resp = requests.post(f'{BASE_URL}/student/curriculum',
                         params={'week': '1', 'kbjcmsid': '63D5F875CCE34BF482A67EC5424EE1D1'},
                         headers=headers)
    print_response('【7】学生课表（第1周）POST /student/curriculum?week=1', resp)

    # ========== 8. 学生成绩（所有学期）==========
    resp = requests.post(f'{BASE_URL}/student/termGPA', headers=headers)
    print_response('【8】学生成绩（所有学期）POST /student/termGPA', resp)

    # ========== 9. 学生成绩（指定学期）==========
    resp = requests.post(f'{BASE_URL}/student/termGPA',
                         params={'semester': '2023-2024-1'},
                         headers=headers)
    print_response('【9】学生成绩（2023-2024-1学期）POST /student/termGPA?semester=2023-2024-1', resp)

    # ========== 10. 当前学期 ==========
    resp = requests.post(f'{BASE_URL}/currentTerm', headers=headers)
    print_response('【10】当前学期 POST /currentTerm', resp)

    # ========== 11. 学期列表 ==========
    resp = requests.post(f'{BASE_URL}/semesterList', headers=headers)
    print_response('【11】学期列表 POST /semesterList', resp)

    # ========== 12. 无Token访问测试 ==========
    resp = requests.post(f'{BASE_URL}/student/my')
    print_response('【12】无Token访问 POST /student/my（应返回非法访问）', resp)

    # ========== 13. 错误密码登录测试 ==========
    encrypted_wrong = encrypt_password('wrongpassword')
    resp = requests.post(f'{BASE_URL}/login', params={
        'userNo': '202609011001',
        'pwd': encrypted_wrong,
        'encode': '1'
    })
    print_response('【13】错误密码登录 POST /login（应返回账号不存在或密码错误）', resp)

    print('\n' + '=' * 70)
    print('全部接口测试完成!')
    print('=' * 70)


if __name__ == '__main__':
    main()
