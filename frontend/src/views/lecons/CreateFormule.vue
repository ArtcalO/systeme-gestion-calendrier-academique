<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			imageData1:null,
			formule:{
				lecon:this.$route.params.id_lecon,
				pdf:null,
			},
		}
	},
	beforeMount(){
		if(this.$route.params.id_formule)
			this.fetchSingleFormule()
	},
	components:{
		UploadFilled,
	},
	methods:{
		getLivre(e){
	      this.formule.pdf=e.target.files[0]
	    },
		fetchSingleFormule(){
			this.isLoading=true
			axios.get('formules/'+this.$route.params.id_formule+"/")
			.then((res)=>{
				this.isLoading=false
				this.formule.lecon = res.data.lecon.id
				this.formule.pdf = res.data.pdf
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
				this.errorOrRefresh(err, this.fetchSingleFormule)
			})
		},
		createformule(){
			if(this.formule.pdf==null){
				this.useNotifyError("Veuillez specifier le pdf !")
				return
			}
			this.isLoading=true
			let data = new FormData()
			data.append("lecon",this.formule.lecon)
			data.append("pdf",this.formule.pdf)
			if(this.$route.name=="createFormule")
				axios.post("formules/", data)
				.then((response)=>{
					this.useNotifySuccess("formule Crée avec success !")
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createformule)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`formules/${this.$route.params.id}/`, data)
				.then((response)=>{
					this.useNotifySuccess("formule modifé avec success !")
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createformule)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="formule">
			<h5 class="border-b pb-3 mb-3">Ajout formule</h5>
			<el-row :gutter="20">
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
			<el-button :loading="isLoading" @click="createformule" type="primary" size="large"
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
