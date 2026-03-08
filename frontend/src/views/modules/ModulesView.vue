<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			modules:this.$store.state.modules,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.modules"(new_val){
		this.modules=new_val
	 },
	 "keyword"(new_val){
		this.modules = this.$store.state.modules.filter(x =>{
		return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
	  })
	 }
	},
	mounted(){
		this.fetchModules()
	},
	methods:{
		fetchModules(){
			this.isLoading=true
			axios.get('/academic/modules/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.modules=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		}
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Modules</h4>
			</v-col>
			<v-col cols="auto">
				<el-button type="primary" :icon="Plus"
					>Module</el-button
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
			<el-table v-loading="isLoading" :data="modules" style="width: 100%">
				<el-table-column fixed label="Nom" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.name
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Categorie" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.subject_name
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Niveau" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.level_name
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Programme" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.program_name
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Credits" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.credits
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Heures/Semaine" min-width="90">
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
				<el-table-column fixed label="Prerequis ?" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.has_prerequisites ? "Oui" : "Non"
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Nb Pre-requis" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.prerequisites_list.length
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed="right" label="Actions" min-width="80">
				  <template #default="scope">
					<el-button
					  size="small"
					  type="primary"
					 
					  >Modifier</el-button
					>
				  </template>
				</el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>