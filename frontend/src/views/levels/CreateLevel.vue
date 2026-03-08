<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			niveau:{
				nom:"",
			},
		}
	},
	beforeMount(){
		if(this.$route.params.id)
			this.fetchSingleNiveau()
	},
	components:{
		UploadFilled,
	},
	methods:{
		fetchSingleNiveau(){
			this.isLoading=true
			axios.get('niveaux/'+this.$route.params.id+"/")
			.then((res)=>{
				this.isLoading=false
				this.niveau = res.data
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
		createNiveau(){
			if(this.niveau.nom.trim()==""){
				this.useNotifyError("Veuillez specifier le nom du niveau !")
				return
			}
			this.isLoading=true
			
			if(!this.$route.params.id)
				axios.post("niveaux/", this.niveau)
				.then((res)=>{
					this.useNotifySuccess("Niveau Crée avec success !")
					this.$store.state.niveaux.push(res.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createNiveau)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`niveaux/${this.$route.params.id}/`, this.niveau)
				.then((res)=>{
					this.useNotifySuccess("Niveau modifé avec success !")
					this.$store.state.niveaux.push(res.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createNiveau)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="niveau">
			<h5 class="border-b pb-3 mb-3">Ajout niveau</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom">
						<el-input v-model="niveau.nom" placeholder="nom du niveau" name="nom" />
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createNiveau" type="primary" size="large"
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
