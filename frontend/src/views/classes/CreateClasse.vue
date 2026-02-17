<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			classe:{
				section:null,
				nom:"",
				epreuves_types:false,
			},
		}
	},
	beforeMount(){
		this.fetchSections()
		if(this.$route.params.id)
			this.fetchSingleClasse()
	},
	components:{
		UploadFilled,
	},
	methods:{
		fetchSections(){
			this.isLoading=true
			axios.get('sections/')
			.then((response)=>{
				this.isLoading=false
				this.$store.state.sections=response.data.results
			})
			.catch((error)=>{
				this.isLoading=false
				this.errorOrRefresh(error, this.createClasse)
			})
		},
		fetchSingleClasse(){
			this.isLoading=true
			axios.get('classes/'+this.$route.params.id+"/")
			.then((response)=>{
				this.isLoading=false
				this.classe.section = response.data.section.id
				this.classe.nom = response.data.nom
				this.classe.epreuves_types = response.data.epreuves_types
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.createClasse)
			})
		},
		createClasse(){
			if(this.classe.section==null){
				this.useNotifyError("Veuillez specifier la section de la classe !")
				return
			}
			if(this.classe.nom.trim()==""){
				this.useNotifyError("Veuillez specifier le nom de la classe !")
				return
			}
			this.isLoading=true
			
			if(!this.$route.params.id)
				axios.post("classes/", this.classe)
				.then((response)=>{
					this.useNotifySuccess("classe Crée avec success !")
					this.$store.state.classes.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createClasse)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`classes/${this.$route.params.id}/`, this.classe)
				.then((response)=>{
					this.useNotifySuccess("classe modifé avec success !")
					this.$store.state.classes.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createClasse)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="classe">
			<h5 class="border-b pb-3 mb-3">Ajout classe</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="section">
						<el-select filterable v-model="classe.section" placeholder="Select" class="w-100">
							<el-option
								v-for="item in $store.state.sections"
								:key="item.id"
								:label="item.nom"
								:value="item.id"
							/>
						</el-select>
					</el-form-item>
					<el-form-item label="Nom">
						<el-input v-model="classe.nom" placeholder="nom de la classe" name="nom" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Classe à test ?">
						<el-checkbox
						    v-model="classe.epreuves_types"
						  >
						    Contient des epreuves types
						  </el-checkbox>
					</el-form-item>

				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createClasse" type="primary" size="large"
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
