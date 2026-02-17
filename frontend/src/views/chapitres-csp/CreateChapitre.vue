<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			imageData1:null,
			chapitre:{
				nom:"",
				pdf:null,
			},
		}
	},
	components:{
		UploadFilled,
	},
	methods:{
		getLivre(e){
	      this.chapitre.pdf=e.target.files[0]
	    },
		createchapitre(){
			if(this.chapitre.nom.trim()==""){
				this.useNotifyError("Veuillez specifier le nom du chapitre !")
				return
			}
			this.isLoading=true
			let data = new FormData()
			data.append("cours_pecial",this.$route.params.id)
			data.append("nom",this.chapitre.nom)
			data.append("pdf",this.chapitre.pdf)
			axios.post("chapitres/", data)
			.then((response)=>{
				this.useNotifySuccess("Chapitre cours spécial Crée avec success !")
				this.$router.go(-1)
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.createchapitre)
			}).finally(()=>this.isLoading=false)
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="chapitre">
			<h5 class="border-b pb-3 mb-3">Ajout chapitre</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom">
						<el-input v-model="chapitre.nom" placeholder="nom de la chapitre" name="nom" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="PDF">
					 <v-file-input
			            variant="outlined"
			            density="compact"
			            clearable
			            label="Fichier PDF"
			            @change="e=>getLivre(e)"
			          ></v-file-input>
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createchapitre" type="primary" size="large"
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
