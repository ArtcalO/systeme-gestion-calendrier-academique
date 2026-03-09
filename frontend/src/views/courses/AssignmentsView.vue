<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			courses:this.$store.state.assignments,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.assignments"(new_val){
	 	this.assignments=new_val
	 },
	 "keyword"(new_val){
	 	this.assignments = this.$store.state.assignments.filter(x =>{
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
			axios.get('/assignments/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.assignments=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Attributions des cours</h4>
			</v-col>
			<v-col cols="auto" >

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
			<el-table v-loading="isLoading" :data="assignments" style="width: 100%">
				<el-table-column fixed label="Cours" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.course_name
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
									scope.row.professor_name
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
				<el-table-column fixed label="Score" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.score
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Note" min-width="250">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.notes
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				
				<el-table-column fixed="right" label="Actions" min-width="80">
			      <template #default="scope">
			        <el-button
						v-if="!scope.row.confirmed_date"
			          size="small"
			          type="warning"
			          
			          >Confirmer</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
