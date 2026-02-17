<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			prof:{
				first_name:"",
				last_name:"",
				password:"",
				email:""
			},
		}
	},
	beforeMount(){
		if(this.$route.params.id)
			this.fetchSingleProf()
	},
	components:{
		UploadFilled,
	},
	methods:{
		fetchSingleProf(){
			this.isLoading=true
			axios.get('profs/'+this.$route.params.id+"/")
			.then((res)=>{
				this.isLoading=false
				this.prof.first_name = res.data.user.first_name
				this.prof.last_name = res.data.user.last_name
				this.prof.email = res.data.user.email
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
		createProf(){
			if(this.prof.last_name.trim()==""){
				this.useNotifyError("Veuillez specifier le nom du prof !")
				return
			}
			if(this.prof.first_name.trim()==""){
				this.useNotifyError("Veuillez specifier le prenom du prof !")
				return
			}
			if(this.prof.email.trim()==""){
				this.useNotifyError("Veuillez specifier l'email du prof !")
				return
			}
			this.isLoading=true
			
			if(!this.$route.params.id)
				axios.post("profs/", this.prof)
				.then((res)=>{
					this.useNotifySuccess("Professeur Crée avec success !")
					this.$store.state.profs.push(res.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createProf)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`profs/${this.$route.params.id}/`, this.prof)
				.then((res)=>{
					this.useNotifySuccess("prof modifé avec success !")
					this.$store.state.profs.push(res.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createProf)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="prof">
			<h5 class="border-b pb-3 mb-3">Ajout Professeur</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom">
						<el-input v-model="prof.last_name" placeholder="nom du prof" :name="prof.last_name" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Prénom">
						<el-input v-model="prof.first_name" placeholder="prenom du prof" :name="prof.first_name" />
					</el-form-item>
				</el-col>
			</el-row>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Email">
						<el-input type="email" v-model="prof.email" placeholder="email du prof" :name="prof.email" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12" v-if="!$route.params.id">
					<el-form-item label="Mot de passe">
						<el-input type="password" v-model="prof.password" placeholder="mot de passe du prof" :name="prof.password" />
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createProf" type="primary" size="large"
				>Valider</el-button
			>
		</el-form>
	</el-card>
</template>

<style scoped>
.drop-area {
	text-align: center;
	padding: 20px;
	background-color: #f1f1f1;
	border: 2px dashed #ccc;
	cursor: pointer;
}

.drag-over {
	background-color: #c1c1c1;
}

.dropzone-text {
	padding: 10px;
}

img {
	max-width: 100%;
	max-height: 115px;
}
</style>
