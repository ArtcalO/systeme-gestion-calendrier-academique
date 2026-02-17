<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			discipline:{},
			competence:{
				annee_scolaire:this.$store.state.user.annee_encours,
				trimestre:this.$store.state.user.trimestre_encours,
				discipline:null,
                competences:""
			},
		}
	},
	beforeMount(){
		if(this.$route.params.id_competence)
			this.fetchSingleCompetence()
		this.fetchSingleDicipline()
		this.fetchAnneesScolaires()
	},
	components:{
		UploadFilled,
	},
	methods:{
		fetchSingleDicipline(){
			this.isLoading=true
			axios.get('disciplines/'+this.$route.params.id_discipline+"/")
			.then((res)=>{
				this.isLoading=false
				this.discipline = res.data
			})
			.catch((err)=>{
				this.isLoading=false
				this.errorOrRefresh(err, this.fetchSingleDicipline)
			})
		},
		fetchSingleCompetence(){
			axios.get(`competences/${this.$route.params.id_evaluation}/`,)
				.then((response)=>{
					this.competence.annee_scolaire=response.data.annee_scolaire
					this.competence.trimestre=response.data.trimestre
					this.competence.competences=response.data.competences
					this.competence.discipline=response.data.discipline
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.fetchSingleEvaluation)
				}).finally(()=>this.isLoading=false)
		},
		modifyCompetence(){
			axios.put(`competences/${this.$route.params.id_evaluation}/`, this.evaluation)
				.then((response)=>{
					this.useNotifySuccess("Competence modifé avec success !")
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					this.errorOrRefresh(error, this.modifyCompetence)
				}).finally(()=>this.isLoading=false)
		},
		createCompetence(){
			this.competence.discipline = this.$route.params.id_discipline
			if(this.competence.annee_scolaire==null){
				this.useNotifyError("Veuillez specifier l'année scolaire !")
				return
			}
			if(this.competence.trimestre==null){
				this.useNotifyError("Veuillez specifier le trimestre !")
				return
			}
            if(this.competence.competences.trim()==''){
				this.useNotifyError("Veuillez specifier la competence !")
				return
			}
			if(this.competence.discipline==null){
				this.useNotifyError("Pas de dicipline trouvé !")
				this.$router.push({name:"competencesDiscipline", params:{id_discipline:this.$route.params.id_discipline}})
				return
			}
			this.isLoading=true

			if(!this.$route.params.id_competence)
				axios.post("competences/", this.competence)
				.then((response)=>{
					this.useNotifySuccess("Compétence crée avec success !")
					this.$store.state.competences.push(response.data)
					this.$router.push({name:"competencesDiscipline", params:{id_discipline:this.$route.params.id_discipline}})
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createCompetence)
				}).finally(()=>this.isLoading=false)
			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="evaluation">
			<h5 class="border-b pb-3 mb-3">Création compétences  pour <strong>{{ discipline?discipline?.nom:'...' }}</strong></h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Année Scolaire">
						<el-select filterable v-model="competence.annee_scolaire" placeholder="Année scolaire" class="w-100">
							<el-option
								v-for="item in $store.state.anneesScolaires"
								:key="item.id"
								:label="item.debut.split('-')[0]+'-'+item.fin.split('-')[0]"
								:value="item.id"
							/>
						</el-select>
					</el-form-item>
					<el-form-item label="Trimestre">
						<el-select filterable v-model="competence.trimestre" placeholder="Trimestre" class="w-100">
							<el-option
								v-for="item in $store.state.TRIMESTRES"
								:key="item.value"
								:label="item.label"
								:value="item.value"
							/>
						</el-select>
					</el-form-item>
                    <el-form-item label="Numéro">
						<el-input type="text" v-model="competence.competences" placeholder="Competences" name="competence" />
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button v-if="$route.params.id_competence" :loading="isLoading" @click="modifyCompetence" type="primary" size="large"
				>Valider</el-button
			>
			<el-button v-else :loading="isLoading" @click="createCompetence" type="primary" size="large"
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
