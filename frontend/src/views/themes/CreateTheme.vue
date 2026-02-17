<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			theme:{
				discipline:null,
				nom:"",
			},
		}
	},
	beforeMount(){
		this.fetchDisciplines()
		if(this.$route.params.id)
			this.fetchSingletTheme()
	},
	components:{
		UploadFilled,
	},
	methods:{
		fetchDisciplines(){
			this.isLoading=true
			axios.get('disciplines/')
			.then((response)=>{
				this.isLoading=false
				this.$store.state.disciplines=response.data.results
			})
			.catch((error)=>{
				this.isLoading=false
				this.errorOrRefresh(error, this.fetchDisciplines)
			})
		},
		fetchSingletTheme(){
			this.isLoading=true
			axios.get('themes/'+this.$route.params.id+"/")
			.then((response)=>{
				this.isLoading=false
				this.theme.discipline = response.data.discipline.id
				this.theme.nom = response.data.nom
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.fetchSingleTheme)
			})
		},
		createDiscipline(){
			if(this.theme.discipline==null){
				this.useNotifyError("Veuillez specifier la discipline !")
				return
			}
			if(this.theme.nom.trim()==""){
				this.useNotifyError("Veuillez specifier le nom du theme !")
				return
			}
			this.isLoading=true
			
			if(!this.$route.params.id)
				axios.post("themes/", this.theme)
				.then((response)=>{
					this.useNotifySuccess("Theme Crée avec success !")
					this.$store.state.themes.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createDiscipline)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`themes/${this.$route.params.id}/`, this.theme)
				.then((response)=>{
					this.useNotifySuccess("Theme modifé avec success !")
					this.$store.state.themes.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createDiscipline)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="theme">
			<h5 class="border-b pb-3 mb-3">Ajout thème</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Disciplines">
						<el-select filterable v-model="theme.discipline" placeholder="Select" class="w-100">
							<el-option
								v-for="item in $store.state.disciplines"
								:key="item.id"
								:label="item.nom"
								:value="item.id"
							/>
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom du thème">
						<el-input v-model="theme.nom" placeholder="nom du theme" name="nom" />
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createDiscipline" type="primary" size="large"
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
