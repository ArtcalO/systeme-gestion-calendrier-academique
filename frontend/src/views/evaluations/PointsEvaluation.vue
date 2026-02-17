<script >
import { EditPen,Search,More,View,Edit,Check,Delete } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			evaluation:{},pointsEvaluations:this.$store.state.pointsEvaluations,
			isLoading:false,keyword:"",EditPen,Search,View,
			Edit,Check,Delete
		}
	},
	mounted(){
		this.fetchSingleEvaluation()
		this.fetchpointsEvaluations()
	},
	components:{
		More,
	},
	watch: {
	 "$store.state.pointsEvaluations"(new_val){
	 	this.pointsEvaluations=new_val
	 },
	 "keyword"(new_val){
	 	this.pointsEvaluations = this.$store.state.pointsEvaluations.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	methods:{
		validateAll(){
			this.isLoading=false
			axios.post('pointsEvaluations/validateAll/', this.pointsEvaluations)
			.then(()=>{
				this.useNotifySuccess("Validés avec success !")
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.validateAll)
			})
		},
		validateSingleStudentPoints(studentPoints){
			this.isLoading=true
			studentPoints.eleve = studentPoints.eleve.id
			studentPoints.evaluation = studentPoints.evaluation.id
			axios.put('pointsEvaluations/'+studentPoints.id+"/", studentPoints)
			.then((response)=>{
				this.isLoading=false
				this.discipline = response.data
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.validateSingleStudentPoints)
			})
		},
		fetchSingleEvaluation(){
			this.isLoading=true
			axios.get('evaluations/'+this.$route.params.id_evaluation+"/")
			.then((response)=>{
				this.isLoading=false
				this.discipline = response.data
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.fetchSingleEvaluation)
			})
		},
		fetchpointsEvaluations(){
			this.isLoading=true
			axios.get('pointsEvaluations/?evaluation='+this.$route.params.id_evaluation)
			.then((response)=>{
				this.isLoading=false
				this.$store.state.pointsEvaluations = response.data.results
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.fetchpointsEvaluations)
			})
		},
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Points pour <strong>{{ discipline?discipline.nom:'...' }}</strong></h4>
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
						<div class="mr-sm-2 my-2 my-sm-0">
							<el-button type="success"	@click="validateAll">
								Valider Tout
							</el-button>

						</div>
					</div>
				</div>
			</template>
			<el-table v-loading="isLoading" :data="pointsEvaluations" style="width: 100%">
				<el-table-column  label="Eleve" width="200">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.eleve.full_name
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column label="Points" width="200">
					<template #default="scope">
						<div>
							<el-input-number v-model="scope.row.points" :min="1" :max="scope.row.evaluation.maxima" />
						</div>
					</template>
				</el-table-column>	
				<el-table-column label="Operations"  width="120">
			      <template #default="scope">
			        <el-button type="success" :icon="Check" circle @click="validateSingleStudentPoints(scope.row)" />
			        <el-button type="danger" :icon="Delete" circle @click="scope.row.points=null" />
			      </template>
			    </el-table-column>
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
