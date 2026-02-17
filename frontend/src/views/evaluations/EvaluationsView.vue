<script >
import { EditPen,Search,More,View,Check,Close } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			discipline:{},evaluations:this.$store.state.evaluations,
			isLoading:false,keyword:"",EditPen,Search,View,Check,Close,
			validation_modal:false,compiler_modal:false, type:"",evaluationObj:null,
			compilation:{
				remplissage:false,
				annee_scolaire:this.$store.state.user.annee_encours,
				trimestre:null,
				tj:0,
				ex:0,
			},
			anneesScolaires:[],
		}
	},
	watch: {
	 "$store.state.discipline"(new_val){
	 	this.discipline=new_val
	 },
	 "keyword"(new_val){
	 	this.evaluations = this.$store.state.evaluations.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	components:{
		More
	},
	mounted(){
		this.fetchSingleDiscipline()
		this.fetchEvaluations()
		this.fetchAnneesScolaires()
	},
	methods:{
		handleRowDblclick(row, event) {
			this.$router.push({name:'pointsEvaluations', params:{id_evaluation:row.id}})
	    },
	    fetchAnneesScolaires(){
			this.isLoading=true
			axios.get('anneesScolaires/')
			.then((res)=>{
				this.isLoading=false
				this.anneesScolaires=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				this.errorOrRefresh(err, this.fetchAnneesScolaires)
			})
		},
		fetchSingleDiscipline(){
			this.isLoading=true
			axios.get('disciplines/'+this.$route.params.id_discipline+"/")
			.then((response)=>{
				this.isLoading=false
				this.discipline = response.data
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.fetchSingleDiscipline)
			})
		},
		fetchEvaluations(){
			this.isLoading=true
			axios.get('evaluations/?discipline='+this.$route.params.id_discipline)
			.then((response)=>{
				this.isLoading=false
				this.evaluations = response.data.results
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.fetchEvaluations)
			})
		},
		openModal(type,evaluation){
			this.validation_modal=true
			this.type=type
			this.evaluationObj=evaluation
		},
		performValidation(){
			if(this.type=="valider")
				this.validateEvaluation(this.evaluationObj)
			if(this.type=="abandonner")
				this.unValidateEvaluation(this.evaluationObj)
		},
		validateEvaluation(evaluation){
			axios.get('evaluations/'+evaluation.id+'/validate/')
			.then((response)=>{
				this.isLoading=false
				evaluation.est_valide = true
				this.validation_modal=false
				this.useNotifySuccess("Evaluation validée avec success !")
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.validateEvaluation)
			})
		},
		performCompilation(){
			axios.post('disciplines/'+this.discipline.id+'/compiler/', this.compilation)
			.then(()=>{
				this.useNotifySuccess("Compilation terminée avec success !")
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.unValidateEvaluation)
			})
		},
		unValidateEvaluation(evaluation){
			axios.get('evaluations/'+evaluation.id+'/un-validate/')
			.then((response)=>{
				this.isLoading=false
				evaluation.est_valide = false
				this.validation_modal=false
				this.useNotifySuccess("Evaluation abandonnée avec success !")
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.unValidateEvaluation)
			})
		}
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Evaluations pour <strong>{{ discipline?discipline.nom:'...' }}</strong></h4>
			</v-col>
			<v-col cols="auto" v-if="active_user_is('professeur')">
				<el-button type="primary" :icon="Plus"	@click="$router.push({ name: 'createEvaluation',params:{id_discipline:$route.params.id_discipline}})"

				>
					Evaluation
				</el-button>
			</v-col>
		</v-row>
		<el-card>
			<template #header>
				<div class="card-header d-xl-flex align-center justify-space-between">
					<div></div>
					<div class="d-md-flex align-center">
						<div class="mr-sm-2 my-2 my-sm-0">
							<el-input v-model="keyword" placeholder="Chercher" class="input-with-select w-100">
								<template #append>
									<el-button type="primary" :icon="Search" />
								</template>
							</el-input>

						</div>
						<el-button
							type="success"
							:icon="Plus"
							@click="compiler_modal=true"
						>Compiler</el-button>
					</div>
				</div>
			</template>
			<el-table
				v-loading="isLoading"
				:data="evaluations"
				style="width: 100%"
				@row-dblclick="handleRowDblclick"
			>
				<el-table-column fixed label="Date" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.date
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Trimestre" min-width="50">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.trimestre
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Type" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									getEvaluationType(scope.row.type_evaluation)
								}}
								N*
								{{
									scope.row.numero
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Max" min-width="50">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.maxima
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Valide ?" min-width="50">
					<template #default="scope">
						<div>
							<span>
								<el-button v-if="scope.row.est_valide" type="success" size="small" :icon="Check" circle />
								<el-button v-else type="danger" size="small" :icon="Close" circle />
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Nb Vides" min-width="50">
					<template #default="scope">
						<div>
							<span>
								{{scope.row.vides}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed="right" label="Actions">
					<template #default="scope">
					      <el-dropdown placement="bottom-end">
							<span class="el-dropdown-link border rounded-1 pa-2 d-flex align-center">
								<el-icon rotate ><More color="primary" /></el-icon>
							</span>
							<template #dropdown>
								<el-dropdown-menu type="secondary">
									<el-dropdown-item
										:icon="View"
										color="secondary"
										@click="$router.push({name:'pointsEvaluations', params:{id_evaluation:scope.row.id}})"
										>
										Points
									</el-dropdown-item>
									<el-dropdown-item
										:icon="EditPen"
										color="primary"
										@click="$router.push({name:'modifyEvaluation', params:{id_evaluation:scope.row.id}})"
										>
										Modifier
									</el-dropdown-item>

			        		
									<el-dropdown-item
										v-if="!scope.row.est_valide"
										color="success"
										:icon="Check"
										@click="openModal('valider',scope.row)"
										>
										Valider
									</el-dropdown-item>

									<el-dropdown-item
										v-else
										color="danger"
										:icon="Close" 
										@click="openModal('abandonner',scope.row)"
										>
										Abandoner
									</el-dropdown-item>

								</el-dropdown-menu>
							</template>
						</el-dropdown>
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
		<el-dialog
			v-model="validation_modal"
			title="Confirmation !"
			width="30%">
	        <span>Voulez vous {{type}} cette évaluation ?</span>
	          <template #footer>
	            <span class="dialog-footer">
	              <el-button @click="validation_modal = false">Annuler</el-button>
	              <el-button :loading="isLoading" type="primary" @click="performValidation">
	                Confirmer
	              </el-button>
	            </span>
	          </template>
	    </el-dialog>

	    <el-dialog
			v-model="compiler_modal"
			title="Compilation !"
			width="40%">
	        <el-form label-position="top" label-width="100px" :model="personnel">
	            <el-row :gutter="20">
	          		<el-col :span="20" :sm="12">
						<el-form-item label="Année Scolaire">
							<el-select filterable v-model="compilation.annee_scolaire" placeholder="Année scolaire" class="w-100">
								<el-option
									v-for="item in anneesScolaires"
									:key="item.id"
									:label="item.debut.split('-')[0]+'-'+item.fin.split('-')[0]"
									:value="item.id"
								/>
							</el-select>
						</el-form-item>
					</el-col>
					<el-col :span="20" :sm="12">
						<el-form-item label="Trimestre">
							<el-select filterable v-model="compilation.trimestre" placeholder="Trimestre" class="w-100">
								<el-option
									v-for="item in $store.state.TRIMESTRES"
									:key="item.value"
									:label="item.label"
									:value="item.value"
								/>
							</el-select>
						</el-form-item>
					</el-col>
	            </el-row>
	            <br>
	            <el-row :gutter="20">
	            	<el-col :span="20" :sm="20" >
		                <el-form-item>
		                    <el-radio-group v-model="compilation.remplissage">
		                      <el-radio :label="false" border>Sans Remplissage</el-radio>
		                      <el-radio :label="true" border>Avec remplissage</el-radio>
		                    </el-radio-group>
		                </el-form-item>
	                </el-col>
	            </el-row>
	            <br>
	            <el-row :gutter="20" v-if="compilation.remplissage">
					<el-col :span="20" :sm="12">
						<el-form-item label="Remplir les interrogations vides par : ">
							<el-input v-model="compilation.tj" placeholder="nom du niveau" name="nom" />
						</el-form-item>
					</el-col >
					<el-col :span="20" :sm="12">
						<el-form-item label="Remplir les examens vides par : ">
							<el-input v-model="compilation.ex" placeholder="Remplir les examens vides par" name="nom" />
						</el-form-item>
					</el-col>
				</el-row>
	        </el-form>
	          <template #footer>
	            <span class="dialog-footer">
	              <el-button @click="compiler_modal = false">Annuler</el-button>
	              <el-button :loading="isLoading" type="primary" @click="performCompilation">
	                Confirmer
	              </el-button>
	            </span>
	          </template>
	    </el-dialog>
	    </div>
</template>

<style lang="scss" scoped></style>
