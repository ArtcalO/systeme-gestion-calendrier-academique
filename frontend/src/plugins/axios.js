import axios from 'axios'
import store from '../store'
function url(){
  let base_url = ""
  let base_host = window.location.host.split(":")[0]
  let locals = ["localhost", "127.0.0.1"]
  if(locals.includes(base_host)){
    base_url = window.location.protocol+"//"+base_host+":8000"
  }
  return base_url + '/api';

  return "https://api.school.ksquad.dev/api"
}
export const axiosService = axios.create({
	baseURL: url()
})


axiosService.interceptors.request.use((config) => {
	config.headers.Authorization = store.state.user?.access ? `Bearer ${store.state.user?.access}` : ''
	return config
})

export const obrAxios = axios.create()