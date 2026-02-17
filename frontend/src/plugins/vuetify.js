import { createVuetify } from 'vuetify'

// Vuetify styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

const customTheme = {
	dark: false,
	colors: {
		background: '#FFFFFF',
		surface: '#FFFFFF',
		primary: '#4099ff',
		// primary: 'F5A100', old
		// 'primary-darken-1': '#3700B3', old
		// 'primary-lighten-5': '#ffffff', old
		secondary: '#03DAC6',
		'secondary-darken-1': '#018786',
		error: '#B00020',
		info: '#2196F3',
		success: '#4CAF50',
		warning: '#FB8C00'
	}
}

const vuetify = createVuetify({
	theme: {
		defaultTheme: 'customTheme',
		themes: {
			customTheme
		}
	}
})

export default vuetify