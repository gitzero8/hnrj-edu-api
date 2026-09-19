import request from '@/utils/request'
import { encryptPassword } from '@/utils/crypto'

// 学校代码
const SCHOOL_CODE = '4711'

/**
 * 用户登录
 * @param {string} userNo - 学号
 * @param {string} password - 原始密码
 */
export function login(userNo, password) {
	const encryptedPwd = encryptPassword(password)
	return request({
		url: '/login',
		params: {
			userNo,
			pwd: encryptedPwd,
			encode: 1
		}
	})
}

/**
 * 校验Token/获取用户基本信息
 */
export function validateToken() {
	return request({
		url: '/initUserInfo2'
	})
}

/**
 * 获取学生详细信息
 */
export function getUserDetail() {
	return request({
		url: '/student/my',
		params: {
			xxdm: SCHOOL_CODE
		}
	})
}

/**
 * 获取课表时间模式
 */
export function getTimeMode() {
	return request({
		url: '/Get_sjkbms',
		params: {
			xxdm: SCHOOL_CODE
		}
	})
}

/**
 * 获取教学周次列表
 */
export function getTeachingWeek() {
	return request({
		url: '/teachingWeek',
		params: {
			xxdm: SCHOOL_CODE
		}
	})
}

/**
 * 获取学生课表
 * @param {string} week - 周次（'all'表示全部）
 * @param {string} kbjcmsid - 课表时间模式ID
 */
export function getCurriculum(week = 'all', kbjcmsid = '') {
	return request({
		url: '/student/curriculum',
		params: {
			xxdm: SCHOOL_CODE,
			week,
			kbjcmsid
		}
	})
}

/**
 * 获取学生成绩
 */
export function getTermGPA() {
	return request({
		url: '/student/termGPA',
		params: {
			xxdm: SCHOOL_CODE
		}
	})
}

/**
 * 获取当前学期
 */
export function getCurrentTerm() {
	return request({
		url: '/currentTerm',
		params: {
			xxdm: SCHOOL_CODE
		}
	})
}

/**
 * 获取学期列表
 */
export function getSemesterList() {
	return request({
		url: '/semesterList',
		params: {
			xxdm: SCHOOL_CODE
		}
	})
}
