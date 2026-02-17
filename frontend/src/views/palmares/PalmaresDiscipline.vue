<script >
import { Plus,Search,EditPen,Check,Delete,More } from '@element-plus/icons-vue'
import { ElButton } from 'element-plus'
export default {
	data(){
		return {
			palamres:this.$store.state.palamres,
			isLoading:false,keyword:"",Plus,Search,Check,Delete,EditPen,
			nullVisible:false,
			isNullLoading:false,
			nullData:[],
			discipline:{},
			disciplines:[],
			addSuggestionsVisible:false,
			studentObj:null,
			editAppreciation:false,
			addConseilVisible:false,
			moyenne:0,
			somme:0,
			filters:{
				annee_scolaire:this.$store.state.user.annee_encours,
				trimestre:this.$store.state.user.trimestre_encours,
				discipline:null
			},
			appreciations:{
				user:"",
				eleve:"",
				discipline:"",
				annee_scolaire:"",
				trimestre:"",
				appreciations:"",
			},
			conseils:{
				user:"",
				eleve:"",
				annee_scolaire:"",
				trimestre:"",
				conseil:"",
			},
			compilation:{
				remplissage:false,
				annee_scolaire:this.$store.state.user.annee_encours,
				trimestre:null,
				tj:0,
				ex:0,
			},
		}
	},
	components:{
		More
	},
	watch: {
	 "$store.state.palamres"(new_val){
	 	this.palamres=new_val
	 },
	 "filters.discipline"(new_val){
	 	this.fetchDicipline()
	 },
	 
	 "keyword"(new_val){
	 	this.palamres = this.$store.state.palamres.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchAnneesScolaires()
		if(this.active_user_is('titulaire'))
			this.fetchCourseClasse()
		else{
			this.fetchPalmares()
			this.fetchDicipline()
		}
		
	},
	methods:{
		generateBuletins(){
			if(this.active_user_is("titulaire"))
				this.filters.classe = this.$store.state.user.id_classe_titulaire
			axios.post('bulletins/generer/', this.filters)
			.then(()=>{
				this.useNotifySuccess("Opération effectué avec succes !")
				this.$router.push("/bulletins")
			})
			.catch((error)=>{
				console.log(error)
				this.errorOrRefresh(error, this.generateBuletins)
			})
		},
		fetchDicipline(){
			let discipline = null
			if(this.$route.params.id_discipline)
				discipline=this.$route.params.id_discipline
			else
				discipline=this.filters.discipline
			axios.get(`disciplines/${discipline}`)
			.then((res)=>{
				this.discipline=res.data
			})
			.catch((err)=>{
				this.errorOrRefresh(err, this.fetchDicipline)
			})
		},
		isTitulaireCourse(){
			if(this.discipline.prof.user.id==this.$store.state.user.id)
				return true
			else
				return false
		},
		fetchCourseClasse(){
			axios.get(`classes/${this.$store.state.user.id_classe_titulaire}/disciplines/`, this.classe)
				.then((res)=>{
					this.disciplines = res.data
					if(this.disciplines.length>0){
						this.filters.discipline=this.disciplines[0].id
						this.fetchPalmares()
						this.fetchDicipline()
					}

				})
				.catch((err)=>{
					this.errorOrRefresh(error, this.fetchCourseClasse)
				}).finally(()=>this.isLoading=false)
		},
		openNullDetails(id_eleve){
				this.nullVisible=true
				let data = {
					discipline:this.$route.params.id_discipline?this.$route.params.id_discipline:this.filters.discipline,
					annee_scolaire:this.filters.annee_scolaire,
					trimestre:this.filters.trimestre
				}
				this.isNullLoading=true
				axios.post(`eleves/${id_eleve}/check-null-student/`, data)
				.then((res)=>{
					this.isNullLoading=false
					this.nullData=res.data
				})
				.catch((err)=>{
					this.isNullLoading=false
					this.nullVisible=false
					this.errorOrRefresh(err, this.fetchPalmares)
				})				
		},
		openAddSuggestionsModal(studentPoint){
			this.studentObj = studentPoint
			this.addSuggestionsVisible=true
			if(this.studentObj.appreciations.length>0){
				this.appreciations.appreciations = this.studentObj.appreciations[0].appreciations
				this.editAppreciation = true
			}
		},
		openAddConseilsModal(studentPoint){
			this.studentObj = studentPoint
			this.addConseilVisible=true
			if(this.studentObj.conseils.length>0){
				this.conseils.conseil = this.studentObj.conseils[0].conseil
				this.editAppreciation = true
			}
		},
		validateSugesstions(){
			if(this.studentObj==null){
				this.useNotifyError("Veuillez selectionner l'élève")
				return 0
			}
			this.appreciations.eleve = this.studentObj.eleve_id
			this.appreciations.discipline = this.$route.params.id_discipline?this.$route.params.id_discipline:this.filters.discipline
			this.appreciations.annee_scolaire = this.filters.annee_scolaire
			this.appreciations.trimestre = this.filters.trimestre
			this.appreciations.user = this.$store.state.user.id
			if(this.editAppreciation){
				this.appreciations.id = this.studentObj.appreciations[0].id
				axios.put('appreciations/'+this.appreciations.id+"/", this.appreciations)
				.then(()=>{
					this.useNotifySuccess("Suggestions modifiés avec success !")
					this.fetchPalmares()
					this.addSuggestionsVisible=false
					this.editAppreciation=false
				})
				.catch((error)=>{
					this.errorOrRefresh(error, this.validateSugesstions)
				})
				return 0
			}else
				axios.post('appreciations/', this.appreciations)
				.then(()=>{
					this.useNotifySuccess("Suggestions ajoutés avec success !")
					this.fetchPalmares()
					this.addSuggestionsVisible=false
					this.editAppreciation=false
				})
				.catch((error)=>{
					this.errorOrRefresh(error, this.validateSugesstions)
				})
		},
		validateConseils(){
			if(this.studentObj==null){
				this.useNotifyError("Veuillez selectionner l'élève")
				return 0
			}
			this.conseils.eleve = this.studentObj.eleve_id
			this.conseils.annee_scolaire = this.filters.annee_scolaire
			this.conseils.trimestre = this.filters.trimestre
			this.conseils.user = this.$store.state.user.id
			if(this.editAppreciation){
				this.conseils.id = this.studentObj.conseils[0].id
				axios.put('conseilClasses/'+this.conseils.id+"/", this.conseils)
				.then(()=>{
					this.useNotifySuccess("Suggestions modifiés avec success !")
					this.fetchPalmares()
					this.addConseilVisible=false
					this.editAppreciation=false
				})
				.catch((error)=>{
					this.errorOrRefresh(error, this.validateSugesstions)
				})
				return 0
			}else
				axios.post('conseilClasses/', this.conseils)
				.then(()=>{
					this.useNotifySuccess("Suggestions ajoutés avec success !")
					this.fetchPalmares()
					this.addConseilVisible=false
					this.editAppreciation=false
				})
				.catch((error)=>{
					this.errorOrRefresh(error, this.validateSugesstions)
				})
		},
		reCompile(){
			let data={
				remplissage:false,
				annee_scolaire:this.filters.annee_scolaire,
				trimestre:this.filters.trimestre,
				tj:0,
				ex:0
			}
			axios.post('disciplines/'+this.$route.params.id_discipline+'/compiler/', data)
			.then(()=>{
				this.fetchPalmares()
			})
			.catch((error)=>{
				this.errorOrRefresh(error, this.reCompile)
			})
		},
		checkEcheck(row){
			return (row.points_tj+row.points_ex)>this.discipline.maxima?false:true
		},
		validateSingleStudentPoints(studentPoints){
			this.isLoading=true
			studentPoints.eleve = studentPoints.eleve.id
			studentPoints.evaluation = studentPoints.evaluation.id
			axios.put('pointsEvaluations/'+studentPoints.id+"/", studentPoints)
			.then(()=>{
				this.useNotifySuccess("Opération effectué avec succes !")
				this.reCompile()
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.validateSingleStudentPoints)
			})
		},
		exportPalmares(){
			let items = this.palamres
			let data = "sep=;\n"
			let titles = []
			if(items.length > 0){
				for(let name of Object.keys(items[0])){
					if(
						name != "appareil" &&
						name != 'appreciations' &&
						name !="conseils" &&
						name !="suggestions" &&
						name !="palmares"
					){
						data += (name + ";")
						titles.push(name)
					}
				}
				data += "\n"
				for(let item of items){
					for(let title of titles){
						data += (JSON.stringify(item[title]) + ";")
					}
					data += "\n"
				}
				window.location = "data:text/csv;base64,77u/" + btoa(data);
			}
		},
		moyenneClasse(){
			for(let i=0;i<this.$store.state.palamres.length;i++){
				if(
					this.$store.state.palamres[i].points_ex != null && 
					this.$store.state.palamres[i].points_tj != null
				)
					this.somme+=(this.$store.state.palamres[i].points_ex+this.$store.state.palamres[i].points_tj)
			}

			this.moyenne = (this.somme/this.$store.state.palamres?.length)*100/100
		},
		fetchPalmares(){
			let discipline = null
			if(this.$route.params.id_discipline)
				discipline=this.$route.params.id_discipline
			else
				discipline=this.filters.discipline
			this.isLoading=true
			axios.get(`detailsPalmares/?discipline=${discipline}&annee_scolaire=${this.filters.annee_scolaire}&trimestre=${this.filters.trimestre}`)
			.then((res)=>{
				this.isLoading=false
				this.$store.state.palamres=res.data.results
				this.nullVisible=false
				this.moyenneClasse()
			})
			.catch((err)=>{
				this.isLoading=false
				this.errorOrRefresh(err, this.fetchPalmares)
			})
		}
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Palmares pour <strong>{{discipline?.nom}}</strong></h4>
			</v-col>
			<v-col>
				<el-input v-model="keyword" placeholder="Chercher" class="input-with-select w-100">
					<template #append>
						<el-button type="primary" :icon="Search" />
					</template>
				</el-input>
			</v-col>
		</v-row>
		<el-card>
			<template #header>
				<div class="card-header d-xl-flex align-center justify-space-between">
					<div class="d-md-flex ">
						<div class="mr-sm-2 my-2 my-sm-0">
							<el-form-item >
								<el-col :span="6" v-if="active_user_is('titulaire')" >
					        		<el-form-item label="Discipline">
										<el-select filterable v-model="filters.discipline" placeholder="Année scolaire" class="w-100">
											<el-option
												v-for="item in disciplines"
												:key="item.id"
												:label="item.nom"
												:value="item.id"
											/>
										</el-select>
									</el-form-item>
								</el-col>
								<el-col :span="6">
					        		<el-form-item label="Année Scolaire">
										<el-select filterable v-model="filters.annee_scolaire" placeholder="Année scolaire" class="w-100">
											<el-option
												v-for="item in $store.state.anneesScolaires"
												:key="item.id"
												:label="item.debut.split('-')[0]+'-'+item.fin.split('-')[0]"
												:value="item.id"
											/>
										</el-select>
									</el-form-item>
								</el-col>
								<el-col :span="6" >
									<el-form-item label="Trimestre">
										<el-select filterable v-model="filters.trimestre" placeholder="Trimestre" class="w-100">
											<el-option
												v-for="item in $store.state.TRIMESTRES"
												:key="item.value"
												:label="item.label"
												:value="item.value"
											/>
										</el-select>
									</el-form-item>
								</el-col>
					      
						      <el-col :span="2">
						        <el-button type="primary" @click="fetchPalmares">Filtrer</el-button>
						      </el-col>

							  <el-col :span="2">
						        <el-button type="primary" @click="exportPalmares">Exporter</el-button>
						      </el-col>

						       <el-col :span="2">
						        <el-button
						        	type="success"
						        	@click="generateBuletins"
						        	v-if="active_user_is('titulaire')"
						        >Gnerer Bultetins</el-button>
						      </el-col>

							</el-form-item>
						</div>
					</div>
				</div>
			</template>
			<el-table v-loading="isLoading" :data="palamres" style="width: 100%">
				<el-table-column fixed label="Nom" width="250">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.eleve.last_name+' '+scope.row.eleve.username
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="TJ" width="60">
					<template #default="scope">
						<div>
							<span v-if="scope.row.points_tj!=null">
								{{ 
									(scope.row.points_tj)*50/50
								}}%
							</span>
							<span v-else>
								<u class="null" @click="openNullDetails(scope.row.eleve_id)" >null</u>
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="EX" width="60">
					<template #default="scope">
						<div>
							<span v-if="scope.row.points_ex!=null">
								{{ 
									(scope.row.points_ex)*50/50
								}}%
							</span>
							<span v-else>
								<u class="null" @click="openNullDetails(scope.row.eleve_id)" >null</u>
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Tot" width="60">
					<template #default="scope">
						<div>
							<span :class="{echeckCheck:checkEcheck(scope.row)}" v-if="scope.row.points_tj!=null && scope.row.points_ex!=null">
								{{ 
									(scope.row.points_tj+scope.row.points_ex)*100/100
								}} %
							</span>
							<span v-else>
								<u class="null" @click="openNullDetails(scope.row.eleve_id)">null</u>
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Moy. Classe" width="100">
					<template #default="scope">
						<div>
							<span :class="{echeckCheck:checkEcheck(scope.row)}" v-if="scope.row.points_tj!=null && scope.row.points_ex!=null">
								{{ 
									parseInt(moyenne.toFixed(2))
								}} %
							</span>
							<span v-else>
								<u class="null" @click="openNullDetails(scope.row.eleve_id)">null</u>
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column label="Appreciations" >
					<template #default="scope">
						<div>
							<strong  v-if="scope.row.appreciations.length>0">
								{{ 
									scope.row.appreciations[0].appreciations
								}}
							</strong>
							<span v-else>
								---
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column label="Conseil de classe" >
					<template #default="scope">
						<div>
							<strong  v-if="scope.row.conseils.length>0">
								{{ 
									scope.row.conseils[0].conseil
								}}
							</strong>
							<span v-else>
								---
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
								<el-dropdown-menu type="primary">
									<el-dropdown-item
										v-if="active_user_is('professeur','titulaire') && scope.row.appreciations.length<=0"
										:icon="Plus"
										 @click="openAddSuggestionsModal(scope.row)"
										>
										Appréciations
									</el-dropdown-item>
									<el-dropdown-item
										v-if="active_user_is('professeur','titulaire') && scope.row.appreciations.length>0"
										:icon="EditPen"
										 @click="openAddSuggestionsModal(scope.row)"
										>
										Appréciations
									</el-dropdown-item>
									<el-dropdown-item
										v-if="active_user_is('titulaire') && scope.row.conseils.length<=0"
										:icon="Plus"
										@click="openAddConseilsModal(scope.row)"
										>
										Conseils de classe
									</el-dropdown-item>
									<el-dropdown-item
										v-if="active_user_is('titulaire') && scope.row.conseils.length>0"
										:icon="EditPen"
										@click="openAddConseilsModal(scope.row)"
										>
										Conseils de classe
									</el-dropdown-item>
								</el-dropdown-menu>
							</template>
						</el-dropdown>
			      </template>
			    </el-table-column>	
			</el-table>
		</el-card>
		<el-dialog  v-model="nullVisible" title="Details des interrogations où il a eu Null" width="800" >
		    <el-card v-if="isNullLoading">
		      <el-skeleton animated />
		    </el-card>
		    <el-card v-else>
		      	<el-table  :data="nullData">
				<el-table-column fixed label="Date">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.evaluation.date
								}}
							</span>
						</div>
					</template>
				</el-table-column>

				<el-table-column fixed label="Type">
					<template #default="scope">
						<div>
							<span>
								{{ 
									getEvaluationType(scope.row.evaluation.type_evaluation)
								}}
								N*
								{{
									scope.row.evaluation.numero
								}}/
								{{
									scope.row.evaluation.maxima
								}}
							</span>
							
						</div>
					</template>
				</el-table-column>
				<el-table-column label="Points" width="170">
					<template #default="scope">
						<div>
							<el-input-number v-model="scope.row.points" :min="1" :max="scope.row.evaluation.maxima" />
						</div>
					</template>
				</el-table-column>
				<el-table-column label="Op.">
			      <template #default="scope" v-if="isTitulaireCourse()">
			        <el-button type="success" :icon="Check" circle @click="validateSingleStudentPoints(scope.row)" />
			      </template>
			    </el-table-column>
			</el-table>
		    </el-card>
		    <template #footer>
		      <div class="dialog-footer">
		        <el-button type="primary" @click="nullVisible = false">
		          Fermer
		        </el-button>
		      </div>
		    </template>
		</el-dialog>

		<el-dialog  v-model="addSuggestionsVisible" :title="'Appréciations pour '+studentObj?.eleve.last_name+' '+studentObj?.eleve.username+' pour '+filters.trimestre+' Trim.'" width="550" >
			<el-form-item label="Appéciations">
				<el-input type="textarea" v-model="appreciations.appreciations" :placeholder="'Appréciations pour'+studentObj?.eleve.last_name+' '+studentObj?.eleve.username" name="nom" />
			</el-form-item>
		    <template #footer>
		      <div class="dialog-footer">
		        <el-button type="danger" @click="addSuggestionsVisible = false">
		          Annuler
		        </el-button>
				<el-button type="primary" @click="validateSugesstions">
		          Valider
		        </el-button>
		      </div>
		    </template>
		</el-dialog>

		<el-dialog  v-model="addConseilVisible" :title="'Conseil de classe pour '+studentObj?.eleve.last_name+' '+studentObj?.eleve.username+' pour '+filters.trimestre+' Trim.'" width="550" >
			<el-form-item label="Conseil de classe">
				<el-input type="textarea" v-model="conseils.conseil" :placeholder="'Conseil de classe  pour'+studentObj?.eleve.last_name+' '+studentObj?.eleve.username" name="nom" />
			</el-form-item>
		    <template #footer>
		      <div class="dialog-footer">
		        <el-button type="danger" @click="addConseilVisible = false">
		          Annuler
		        </el-button>
				<el-button type="primary" @click="validateConseils">
		          Valider
		        </el-button>
		      </div>
		    </template>
		</el-dialog>
	</div>
</template>

<style lang="css" scoped>
.null{
	color:dodgerblue;
	cursor:pointer;
}
.echeckCheck{
	color:red;
}
</style>
