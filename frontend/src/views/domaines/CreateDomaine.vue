<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			domaine:{
				classe:null,
				nom:"",
			},
		}
	},
	beforeMount(){
		this.fetchClasses()
		if(this.$route.params.id)
			this.fetchSingleDomaine()
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
		fetchSingleDomaine(){
			this.isLoading=true
			axios.get('domaines/'+this.$route.params.id+"/")
			.then((response)=>{
				this.isLoading=false
				this.domaine.classe = response.data.classe.id
				this.domaine.nom = response.data.nom
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.createDomaine)
			})
		},
		createDomaine(){
			if(this.domaine.classe==null){
				this.useNotifyError("Veuillez specifier la classe !")
				return
			}
			if(this.domaine.nom.trim()==""){
				this.useNotifyError("Veuillez specifier le nom du domaine !")
				return
			}
			this.isLoading=true
			
			if(!this.$route.params.id)
				axios.post("domaines/", this.domaine)
				.then((response)=>{
					this.useNotifySuccess("Domaine Crée avec success !")
					this.$store.state.domaines.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createDomaine)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`domaines/${this.$route.params.id}/`, this.domaine)
				.then((response)=>{
					this.useNotifySuccess("domaine modifé avec success !")
					this.$store.state.domaines.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createDomaine)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="domaine">
			<h5 class="border-b pb-3 mb-3">Ajout domaine</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Classe">
						<el-select filterable v-model="domaine.classe" placeholder="Select" class="w-100">
							<el-option
								v-for="item in $store.state.classes"
								:key="item.id"
								:label="item.nom"
								:value="item.id"
							/>
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom">
						<el-input v-model="domaine.nom" placeholder="nom de la domaine" name="nom" />
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createDomaine" type="primary" size="large"
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
