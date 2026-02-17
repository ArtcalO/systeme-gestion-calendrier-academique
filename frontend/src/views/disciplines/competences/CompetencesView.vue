<script >
import { Plus,Search,Check,Delete } from '@element-plus/icons-vue'
import { ElButton } from 'element-plus'
export default {
	data(){
		return {
			competences:this.$store.state.competences,
			isLoading:false,keyword:"",Plus,Search,Check,Delete,
            discipline:null,
			filters:{
				annee_scolaire:this.$store.state.user.annee_encours,
				trimestre:this.$store.state.user.trimestre_encours,
			},
		}
	},
	watch: {
	 "$store.state.competences"(new_val){
	 	this.competences=new_val
	 },	 
	 "keyword"(new_val){
	 	this.competences = this.$store.state.competences.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
        this.fetchDicipline()
		this.fetchAnneesScolaires()	
        this.fetchCompetences()	
	},
	methods:{
        fetchDicipline(){
			let discipline =this.$route.params.id_discipline
			axios.get(`disciplines/${discipline}`)
			.then((res)=>{
				this.discipline=res.data
			})
			.catch((err)=>{
				this.errorOrRefresh(err, this.fetchDicipline)
			})
		},
		fetchCompetences(){
            let discipline = this.$route.params.id_discipline
			axios.get(`competences/?discipline=${discipline}&annee_scolaire=${this.filters.annee_scolaire}&trimestre=${this.filters.trimestre}`)
				.then((res)=>{
					this.$store.state.competences=res.data.results
				})
				.catch((err)=>{
					this.errorOrRefresh(error, this.fetchCompetences)
				}).finally(()=>this.isLoading=false)
		},
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Competences : <strong>{{discipline?.nom}}</strong></h4>
			</v-col>
            <v-col cols="auto" >
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createCompetenceDiscipline', params:{id_competence:discipline?.id}})"
					>Competences</el-button
				>
			</v-col>
		</v-row>
		<el-card>
			<template #header>
				<div class="card-header d-xl-flex align-center justify-space-between">
					<div class="d-md-flex ">
						<div class="mr-sm-2 my-2 my-sm-0">
							<el-form-item >
								<el-col :span="8">
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
								<el-col :span="7" >
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
					      
						      <el-col :span="7">
						        <el-button type="primary" @click="fetchPalmares">Filtrer</el-button>
						      </el-col>

							</el-form-item>
						</div>
					</div>
				</div>
			</template>
			<el-table v-loading="isLoading" :data="competences" style="width: 100%">
				<el-table-column fixed label="Competences" width="250">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.competences
								}}
							</span>
						</div>
					</template>
				</el-table-column>
			</el-table>
		</el-card>
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
