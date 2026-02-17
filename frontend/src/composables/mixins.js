import { ElMessage } from 'element-plus'
import { breakpointsTailwind, useBreakpoints } from '@vueuse/core'
import { useDateFormat } from '@vueuse/core'

export default {
  methods: {
    toRound(amount){
      return Math.ceil(amount)
    },
    isNumeric(x) {
      let str = x.toString();
      if (str.match(/^[0-9]+$/)) return true;
      return false;
    },
    logOut() {
      if(confirm("Voulez-vous vraiment deconnecter?")){
        this.$store.state.user = null
        localStorage.removeItem('user')
        window.location="/"
        
      }
    },
    getEvaluationType(id){
      let evaluation = this.$store.state.TYPES_EVALUATIONS.filter(x=>x.value==id)
      return evaluation.length>0?evaluation[0].label:'Innconue' 
    },
    active_user_is(...groups){
      let user_groups = this.active_user?.groups
      if(!!this.active_user){
        for (let group of groups) {
          if(user_groups.map(g=>Object.keys(g)[0]).includes(group)){
            return true
          }
        }
      }
      return false
    },
    fetchAnneesScolaires(){
      this.isLoading=true
      axios.get('anneesScolaires/')
      .then((res)=>{
        this.isLoading=false
        this.$store.state.anneesScolaires=res.data.results
      })
      .catch((err)=>{
        this.isLoading=false
        this.errorOrRefresh(err, this.fetchAnneesScolaires)
      })
    },
    getEleveId(group_name){
      let user_groups = this.$store.state.user.groups
      let id = user_groups.find(x=>Object.keys(x)==group_name)?.eleve
      return id || ""
    },
    money(x, decimals=2) {
      let cash = parseFloat(x).toFixed(decimals)
      if(isNaN(x) || x == null) return "-";
      return cash.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    },
    getFullName(user){
      if(!user.first_name && !user.last_name)
        return `${user.username}`
      else return `${user.first_name} ${user.last_name}`
    },
    cleanString(str){
      if (!str) return "";
      if(typeof(str)=='object'){
        let string = ""
        for( let [clef, valeur] of Object.entries(str)){
          if(typeof(valeur)=='object'){
            let child = ""
            for( let [key, value] of Object.entries(valeur)){
              child += `${value}. `
            }
            valeur = child;
          }
          string+=`"${clef}": ${valeur}. `
        }
        return string;
      };
      str = str.toString();
      return str.replace( /(<([^>]+)>)/ig, '');
    },
    datetime(x) {
      if(!x) return "-"
      let date = new Date(x);
      return new Intl.DateTimeFormat(
        'en-GB',
        { dateStyle: 'short', timeStyle: 'short' }
      ).format(date)
    },
    getDate(date){
      return useDateFormat(date,"YYYY-MM-DD").value
    },
    getTime(date){
      return useDateFormat(date,"HH:mm").value
    },
    getToday(){
      return new Date().toISOString().split("T")[0]
    },
    getRandomElements(arr, n) {
        var result,
            len = arr?.length,
            taken = new Array(len);
        if (n > len){
            result = new Array(len);
            n=len
        }
        else
            result = new Array(n);
        while (n--) {
            var x = Math.floor(Math.random() * len);
            result[n] = arr[x in taken ? taken[x] : x];
            taken[x] = --len in taken ? taken[len] : len;
        }
        return result;
    },
    currentDateTime(){
        var m = new Date()
        var dateString =
         m.getUTCFullYear() +"-"+
         ("0"+(m.getUTCMonth()+1)).slice(-2)  +"-"+
         ("0"+m.getUTCDate()).slice(-2)  + "T" +
         ("0"+(m.getUTCHours()+2)).slice(-2)  +":"+
         ("0"+m.getUTCMinutes()).slice(-2)  + ":" +
         ("0"+m.getUTCSeconds()).slice(-2) 
        return dateString;
    },
    errorOrRefresh(error, callback, substitution_error_msg){
      if(error.response?.data?.code == "token_not_valid"){ 
        let refresh = this.$store.state.user.refresh
        if(!refresh){
          this.$store.state.user = null;
          return
        }
        axios.post(this.url+"/refresh/", {"refresh":refresh})
        .then((response) => {
          this.$store.state.user.access = response.data.access
          if(typeof callback == "function") callback()
        }).catch((error) => {
          this.$store.state.user = null;
          console.error(error)
          this.$store.state.alert = {
            type:"danger", message:this.cleanString("La session a expirée")
          }
        })
      } else {
        console.error(error)
        let error_msg = error.response?.data?.message || error.response?.data || "Erreur inconnue"
        this.$store.state.alert = {
          type:"danger", message:this.cleanString(error_msg)
        }
      }
    },

	useNotifySuccess(message){
		ElMessage({
			message: message,
			type: 'success',
			duration: 4000,
		})
	},
	useNotifyError(message){
		ElMessage({
			message: message,
			type: 'error',
			duration: 4000
		})
	},
	useNotifyWarning(message){
		ElMessage({
			message: message,
			type: 'warning',
			duration: 4000
		})
	},
  toggleNav() {
      this.$store.state.rail = !this.$store.state.rail
    },
  },
  computed:{
    active_user(){
      return this.$store.state.user;
    },
    society(){
      return this.$store.state.society;
    },
    app_name(){
      return this.$store.state.app_name
    },
    active_fullname(){
      return this.active_user?.first_name?`${this.active_user?.first_name} ${this.active_user?.last_name}`:"-------";
    },
    headers(){
      return {
        headers:{
          "Authorization":"Bearer "+this.$store.state.user.access,
        }
      }
    }
  }
}
