<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			courses:this.$store.state.courses,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.courses"(new_val){
	 	this.courses=new_val
	 },
	 "keyword"(new_val){
	 	this.courses = this.$store.state.courses.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchcoursCourses()
	},
	methods:{
		fetchcoursCourses(){
			this.isLoading=true
			axios.get('/academic/courses/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.courses=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
		generateAttribution(){
			this.isLoading=true
			axios.post('/assignments/run_algorithm/', {academic_year_id:1})
			.then((res)=>{
				this.isLoading=false
				this.fetchcoursCourses()
				this.$message.success("Attributions générées avec succès")
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
				this.$message.error("Erreur lors de la génération des attributions")
			})
		}
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Cours spéciaux</h4>
			</v-col>
			<v-col cols="auto" >
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createCoursSpecial' })"
					>Cours Spécial</el-button
				>
				<el-button type="primary" @click="generateAttribution()"
					>Generer Attribution Cours</el-button
				>
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
					</div>
				</div>
			</template>
			<el-table v-loading="isLoading" :data="courses" style="width: 100%">
				<el-table-column fixed label="Nom" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.module_name
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Code" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.module_code
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Année Academique" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.academic_year_name
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Semestre" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.semester
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Heures/S." min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.weekly_hours
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Professeur" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.assigned_professor
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Status" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.status
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				
				<el-table-column fixed="right" label="Actions" min-width="80">
			      <template #default="scope">
			        <el-button
			          size="small"
			          type="warning"
			          
			          >Chapitres</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
