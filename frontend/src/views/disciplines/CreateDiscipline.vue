<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			discipline:{
				domaine:null,
				nom:"",
				prof:null,
				maxima:0,
			},
		}
	},
	beforeMount(){
		this.fetchDomaines()
		this.fetchProfs()
		if(this.$route.params.id)
			this.fetchSingleDiscipline()
	},
	components:{
		UploadFilled,
	},
	methods:{
		fetchDomaines(){
			this.isLoading=true
			axios.get('domaines/')
			.then((response)=>{
				this.isLoading=false
				this.$store.state.domaines=response.data.results
			})
			.catch((error)=>{
				this.isLoading=false
				this.errorOrRefresh(error, this.fetchDomaines)
			})
		},
		fetchProfs(){
			this.isLoading=true
			axios.get('profs/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.profs=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
		fetchSingleDiscipline(){
			this.isLoading=true
			axios.get('disciplines/'+this.$route.params.id+"/")
			.then((response)=>{
				this.isLoading=false
				this.discipline.domaine = response.data.domaine.id
				this.discipline.nom = response.data.nom
				this.discipline.prof = response.data.prof.id
				this.discipline.maxima = response.data.maxima

			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.fetchSingleDiscipline)
			})
		},
		createDsicipline(){
			if(this.discipline.domaine==null){
				this.useNotifyError("Veuillez specifier le domaine !")
				return
			}
			if(this.discipline.nom.trim()==""){
				this.useNotifyError("Veuillez specifier le nom de la discipline !")
				return
			}
			if(this.discipline.prof==null){
				this.useNotifyError("Veuillez specifier le professeur de la discipline !")
				return
			}
			this.isLoading=true
			
			if(!this.$route.params.id)
				axios.post("disciplines/", this.discipline)
				.then((response)=>{
					this.useNotifySuccess("Discipline Crée avec success !")
					this.$store.state.disciplines.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createDsicipline)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`disciplines/${this.$route.params.id}/`, this.discipline)
				.then((response)=>{
					this.useNotifySuccess("discipline modifé avec success !")
					this.$store.state.disciplines.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createDsicipline)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="discipline">
			<h5 class="border-b pb-3 mb-3">Ajout discipline</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Domaine">
						<el-select filterable v-model="discipline.domaine" placeholder="Select" class="w-100">
							<el-option
								v-for="item in $store.state.domaines"
								:key="item.id"
								:label="item.nom"
								:value="item.id"
							/>
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom">
						<el-input v-model="discipline.nom" placeholder="nom de la discipline" name="nom" />
					</el-form-item>
				</el-col>
			</el-row>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Ponderation">
						<el-input v-model="discipline.maxima" placeholder="Ponderation deu cours" name="ponderation" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Professeur">
						<el-select filterable v-model="discipline.prof" placeholder="Choisir un prof" class="w-100">
							<el-option
								v-for="item in $store.state.profs"
								:key="item.id"
								:label="item.user.last_name+' '+item.user.first_name"
								:value="item.id"
							/>
						</el-select>
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createDsicipline" type="primary" size="large"
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
