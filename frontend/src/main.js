import { createApp } from 'vue'

import App from './App.vue'

import router from './router'
import store from './store'

import {axiosService, obrAxios} from './plugins/axios'
import mixins from './composables/mixins.js'

import vuetify from './plugins/vuetify'
import ElementPlus from './plugins/element-plus'

import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.min.css'

window.axios = axiosService;
window.obrAxios = obrAxios;

const app = createApp(App)

app
	.use(router)
	.mixin(mixins)
	.use(store)
	.use(vuetify)
	.use(ElementPlus)

app.mount('#app')
