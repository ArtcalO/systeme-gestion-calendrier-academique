import { ElMessage } from 'element-plus'

export const useNotifySuccess = (message) => {
	ElMessage({
		message: message,
		type: 'success',
		duration: 4000,
	})
}

export const useNotifyError = (message) => {
	ElMessage({
		message: message,
		type: 'error',
		duration: 4000
	})
}

export const useNotifyWarning = (message) => {
	ElMessage({
		message: message,
		type: 'warning',
		duration: 4000
	})
}