<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			discipline:{},
			evaluation:{
				annee_scolaire:null,
				trimestre:null,
				type_evaluation:null,
				maxima:null,
				discipline:null,
				numero:null,
			},
		}
	},
	beforeMount(){
		if(this.$route.params.id_evaluation)
			this.fetchSingleEvaluation()
		this.fetchSingleDicipline()
		this.fetchAnneesScolaires()
	},
	watch: {
	  'evaluation.type_evaluation':{
	  	deep:true,
	  	handler(new_val){
	  		if(new_val==2)
	    		this.evaluation.maxima=this.discipline.maxima
	  	}
	  },
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
		fetchSingleEvaluation(){
			axios.get(`evaluations/${this.$route.params.id_evaluation}/`,)
				.then((response)=>{
					this.evaluation.annee_scolaire=response.data.annee_scolaire
					this.evaluation.trimestre=response.data.trimestre
					this.evaluation.type_evaluation=response.data.type_evaluation
					this.evaluation.maxima=response.data.maxima
					this.evaluation.discipline=response.data.discipline
					this.evaluation.numero=response.data.numero
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createEvaluation)
				}).finally(()=>this.isLoading=false)
		},
		modifyEvaluation(){
			axios.put(`evaluations/${this.$route.params.id_evaluation}/`, this.evaluation)
				.then((response)=>{
					this.useNotifySuccess("Evaluation modifé avec success !")
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					this.errorOrRefresh(error, this.createEvaluation)
				}).finally(()=>this.isLoading=false)
		},
		createEvaluation(){
			this.evaluation.discipline = this.$route.params.id_discipline
			if(this.evaluation.annee_scolaire==null){
				this.useNotifyError("Veuillez specifier l'année scolaire !")
				return
			}
			if(this.evaluation.trimestre==null){
				this.useNotifyError("Veuillez specifier le trimestre !")
				return
			}
			if(this.evaluation.type_evaluation==null){
				this.useNotifyError("Veuillez specifier le type d'évaluation !")
				return
			}
			if(this.evaluation.discipline==null){
				this.useNotifyError("Pas de dicipline trouvé !")
				this.$router.push({name:"evaluationsView", params:{id_discipline:this.$route.params.id_discipline}})
				return
			}
			this.isLoading=true

			if(!this.$route.params.id_evaluation)
				delete this.evaluation.numero
				axios.post("evaluations/", this.evaluation)
				.then((response)=>{
					this.useNotifySuccess("Evaluation crée avec success !")
					this.$store.state.evaluations.push(response.data)
					this.$router.push({name:"evaluationsView", params:{id_discipline:this.$route.params.id_discipline}})
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createEvaluation)
				}).finally(()=>this.isLoading=false)
			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="evaluation">
			<h5 class="border-b pb-3 mb-3">Evaluation pour <strong>{{ discipline?discipline?.nom:'...' }}</strong></h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Année Scolaire">
						<el-select filterable v-model="evaluation.annee_scolaire" placeholder="Année scolaire" class="w-100">
							<el-option
								v-for="item in $store.state.anneesScolaires"
								:key="item.id"
								:label="item.debut.split('-')[0]+'-'+item.fin.split('-')[0]"
								:value="item.id"
							/>
						</el-select>
					</el-form-item>
					<el-form-item label="Trimestre">
						<el-select filterable v-model="evaluation.trimestre" placeholder="Trimestre" class="w-100">
							<el-option
								v-for="item in $store.state.TRIMESTRES"
								:key="item.value"
								:label="item.label"
								:value="item.value"
							/>
						</el-select>
					</el-form-item>
					<el-form-item label="Numéro" v-if="$route.params.id_evaluation">
						<el-input type="number" v-model="evaluation.numero" placeholder="numero" name="numero" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Type d'evaluation">
						<el-select filterable v-model="evaluation.type_evaluation" placeholder="Type d'evaluation" class="w-100">
							<el-option
								v-for="item in $store.state.TYPES_EVALUATIONS"
								:key="item.value"
								:label="item.label"
								:value="item.value"
							/>
						</el-select>
					</el-form-item>
					<el-form-item label="Maxima">
						<el-input type="number" v-model="evaluation.maxima" placeholder="maxima de l'evaluation" :name="evaluation.maxima" />
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button v-if="$route.params.id_evaluation" :loading="isLoading" @click="modifyEvaluation" type="primary" size="large"
				>Valider</el-button
			>
			<el-button v-else :loading="isLoading" @click="createEvaluation" type="primary" size="large"
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
