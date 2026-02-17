<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			eleve:{
				user:{
					first_name:"",
					last_name:"",
					username:"",
				},
				genre:"",
				date_naissance:"",
				classe:null
			},
		}
	},
	beforeMount(){
		if(this.$store.state.classes.length<=0)
			this.fetchClasses()
		if(this.$route.params.id_eleve)
			this.fetchSingleStudent()
	},
	components:{
		UploadFilled,
	},
	methods:{
		fetchClasses(){
			this.isLoading=true
			axios.get('classes/')
			.then((response)=>{
				this.isLoading=false
				this.$store.state.classes=response.data.results
			})
			.catch((error)=>{
				this.isLoading=false
				this.errorOrRefresh(error, this.createDomaine)
			})
		},
		fetchSingleStudent(){
			this.isLoading=true
			axios.get('eleves/'+this.$route.params.id_eleve+"/")
			.then((res)=>{
				this.isLoading=false
				this.eleve = res.data
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
		createEleve(){
			if(this.eleve.user.last_name.trim()==""){
				this.useNotifyError("Veuillez specifier le nom de l'eleve !")
				return
			}
			if(this.eleve.user.first_name.trim()==""){
				this.useNotifyError("Veuillez specifier le prenom de l'eleve !")
				return
			}
			if(this.eleve.genre.trim()==""){
				this.useNotifyError("Veuillez specifier le genre de l'eleve !")
				return
			}
			if(this.eleve.date_naissance.trim()==""){
				this.useNotifyError("Veuillez specifier la date de naissance de l'eleve !")
				return
			}
			if(this.eleve.classe==null){
				this.useNotifyError("Veuillez specifier la classe de l'eleve !")
				return
			}
			this.isLoading=true
			
			if(!this.$route.params.id_eleve){
				this.eleve.user.username = this.eleve.user.first_name.split(' ').join('')
				axios.post("eleves/", this.eleve)
				.then((res)=>{
					this.useNotifySuccess("Eleve crée avec success !")
					this.$store.state.eleves.push(res.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createEleve)
				}).finally(()=>this.isLoading=false)
			}
			else
				axios.put(`eleves/${this.$route.params.id_eleve}/`, this.eleve)
				.then((res)=>{
					this.useNotifySuccess("Eleve modifé avec success !")
					this.$store.state.eleves.push(res.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createEleve)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="prof">
			<h5 class="border-b pb-3 mb-3">Ajout Elève</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom">
						<el-input v-model="eleve.user.last_name" placeholder="nom élève" :name="eleve.user.last_name" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Prénom">
						<el-input v-model="eleve.user.first_name" placeholder="prenom élève" :name="eleve.user.first_name" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom d'utilisateur">
						<el-input disabled="true" v-model="eleve.user.username" placeholder="Nom d'utilisateur élève" :name="eleve.user.username" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Genre">
						<el-select filterable v-model="eleve.genre" placeholder="Select" class="w-100">
							<el-option
								key="M"
								label="Maculin"
								value="M"
							/>
							<el-option
								key="F"
								label="Féminin"
								value="F"
							/>
						</el-select>
					</el-form-item>
				</el-col>
			</el-row>
			<el-row :gutter="20">
				
				<el-col :span="24" :sm="12">
					<el-form-item label="Date de naissance">
						<el-input type="date" v-model="eleve.date_naissance" placeholder="email du élève" :name="eleve.email" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12" >
					<el-form-item label="Classe">
						<el-select filterable v-model="eleve.classe" placeholder="Select" class="w-100">
							<el-option
								v-for="item in $store.state.classes"
								:key="item.id"
								:label="item.nom"
								:value="item.id"
							/>
						</el-select>
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createEleve" type="primary" size="large"
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
