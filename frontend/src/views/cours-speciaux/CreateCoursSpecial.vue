<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			cours:{
				nom:"",
			},
		}
	},
	beforeMount(){
		this.fetchCoursSpeciaux()
		if(this.$route.params.id)
			this.fetchSingleCoursSpecial()
	},
	components:{
		UploadFilled,
	},
	methods:{
		fetchCoursSpeciaux(){
			this.isLoading=true
			axios.get('coursSpeciaux/')
			.then((response)=>{
				this.isLoading=false
				this.$store.state.classes=response.data.results
			})
			.catch((error)=>{
				this.isLoading=false
				this.errorOrRefresh(error, this.fetchCoursSpeciaux)
			})
		},
		fetchSingleCoursSpecial(){
			this.isLoading=true
			axios.get('coursSpeciaux/'+this.$route.params.id+"/")
			.then((response)=>{
				this.isLoading=false
				this.cours.classe = response.data.classe.id
				this.cours.nom = response.data.nom
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.fetchSingleCoursSpecial)
			})
		},
		createCours(){
			if(this.cours.nom.trim()==""){
				this.useNotifyError("Veuillez specifier le nom du cours !")
				return
			}
			this.isLoading=true
			
			if(!this.$route.params.id)
				axios.post("coursSpeciaux/", this.cours)
				.then((response)=>{
					this.useNotifySuccess("cours Crée avec success !")
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createCours)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`coursSpeciaux/${this.$route.params.id}/`, this.cours)
				.then((response)=>{
					this.useNotifySuccess("cours modifé avec success !")
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createCours)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="cours">
			<h5 class="border-b pb-3 mb-3">Ajout cours</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom">
						<el-input v-model="cours.nom" placeholder="nom de la cours" name="nom" />
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createCours" type="primary" size="large"
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
