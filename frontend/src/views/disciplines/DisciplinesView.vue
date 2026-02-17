<script >
import { Plus,Search,More,View } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			disciplines:this.$store.state.disciplines,
			isLoading:false,keyword:"",Plus,Search,View
		}
	},
	watch: {
	 "$store.state.disciplines"(new_val){
	 	this.disciplines=new_val
	 },
	 "keyword"(new_val){
	 	this.disciplines = this.$store.state.disciplines.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	components:{
		More,
	},
	mounted(){
		this.fetchDiscipline()
	},
	methods:{
		fetchDiscipline(){
			this.isLoading=true
			let url=""
			if(this.$route.name=="disciplinesDomaine")
				url='disciplines/?domaine='+this.$route.params.id_domaine
			else
				url = 'disciplines/'
			axios.get(url)
			.then((res)=>{
				this.isLoading=false
				this.$store.state.disciplines=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				this.errorOrRefrsh(err, this.fetchDiscipline)
			})
		}
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Disciplines</h4>
			</v-col>
			<v-col cols="auto" v-if="active_user_is('admin')">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createDiscipline' })"
					>Disciplines</el-button
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
			<el-table v-loading="isLoading" :data="disciplines" style="width: 100%">
				<el-table-column fixed label="Classe" >
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.domaine.classe.nom+' '+
									scope.row.domaine.classe.section.nom+' '+
									scope.row.domaine.classe.section.niveau.nom

								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Discipline">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.nom
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Pond.">
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
				<el-table-column fixed label="Professeur" v-if="active_user_is('admin')">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.prof.user.last_name+' '+
									scope.row.prof.user.first_name
								}}
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
										v-if="!active_user_is('eleve','professeur')"
										:icon="View"
										color="primary"
										 @click="$router.push({name:'modifyDiscipline', params:{id:scope.row.id}})"
										>
										Modifier
									</el-dropdown-item>
									<el-dropdown-item
										:icon="View"
										color="secondary"
										 @click="$router.push({name:'themesDiscipline', params:{id_discipline:scope.row.id}})"
										>
										Themes
									</el-dropdown-item>
									<el-dropdown-item
										:icon="View" 
										@click="$router.push({name:'evaluationsView', params:{id_discipline:scope.row.id}})"
										>
										Evaluations
									</el-dropdown-item>
									<el-dropdown-item
										:icon="View" 
										@click="$router.push({name:'palmaresDiscipline', params:{id_discipline:scope.row.id}})"
										>
										Palmares
									</el-dropdown-item>
									<el-dropdown-item
										:icon="View" 
										color="warning"
										@click="$router.push({name:'evaluationsView', params:{id_discipline:scope.row.id}})"
										>
										Elèves
									</el-dropdown-item>
									<el-dropdown-item
										:icon="View" 
										color="warning"
										@click="$router.push({name:'competencesDiscipline', params:{id_discipline:scope.row.id}})"
										>
										Competences
									</el-dropdown-item>
								</el-dropdown-menu>
							</template>
						</el-dropdown>
			      </template>
			    </el-table-column>	
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
