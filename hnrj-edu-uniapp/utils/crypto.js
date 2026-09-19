import CryptoJS from 'crypto-js'

// 加密密钥
const SECRET_KEY = 'qzkj1kjghd=876&*'

/**
 * 密码加密（与教务系统一致）
 * 流程: JSON.stringify → AES-ECB(Pkcs7) → Base64 → 再次Base64
 * @param {string} password - 原始密码
 * @returns {string} 加密后的密码
 */
export function encryptPassword(password) {
	// 第一步: JSON.stringify
	const jsonStr = JSON.stringify(password)

	// 第二步: AES-ECB 加密 (Pkcs7填充)
	const key = CryptoJS.enc.Utf8.parse(SECRET_KEY)
	const encrypted = CryptoJS.AES.encrypt(jsonStr, key, {
		mode: CryptoJS.mode.ECB,
		padding: CryptoJS.pad.Pkcs7
	})

	// 第三步: Base64 (ciphertext本身就是Base64)
	const base64Str = encrypted.toString()

	// 第四步: 再次Base64
	const doubleBase64 = CryptoJS.enc.Base64.stringify(CryptoJS.enc.Utf8.parse(base64Str))

	return doubleBase64
}

export default {
	encryptPassword
}
