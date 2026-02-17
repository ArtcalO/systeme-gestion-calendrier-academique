<script >
import { Plus,Search,More,View } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			lecons:this.$store.state.lecons,
			isLoading:false,keyword:"",Plus,Search,View
		}
	},
	watch: {
	 "$store.state.lecons"(new_val){
	 	this.lecons=new_val
	 },
	 "keyword"(new_val){
	 	this.lecons = this.$store.state.lecons.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	components:{More},
	mounted(){
		this.fetchLecons()
	},
	methods:{
		fetchLecons(){
			this.isLoading=true
			let url=""
			if(this.$route.name=="themesDiscipline")
				url='lecons/?theme='+this.$route.params.id_theme
			else
				url = 'lecons/'
			axios.get(url)
			.then((res)=>{
				this.isLoading=false
				this.$store.state.lecons=res.data.results
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
				<h4 class="font-weight-medium">Leçons</h4>
			</v-col>
			<v-col cols="auto" v-if="!active_user_is('eleve')">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createLecon' })"
					>Leçon</el-button
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
			<el-table v-loading="isLoading" :data="lecons" style="width: 100%">
				<el-table-column fixed label="Thème" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.theme.nom
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Nom" min-width="90">
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
				<el-table-column fixed="right" label="Actions">
					<template #default="scope">
					      <el-dropdown placement="bottom-end">
							<span class="el-dropdown-link border rounded-1 pa-2 d-flex align-center">
								<el-icon rotate><More /></el-icon>
							</span>
							<template #dropdown>
								<el-dropdown-menu type="primary">
									<el-dropdown-item
										:icon="View"
										color="primary"
										@click="$router.push({name:'leconPreview', params:{id:scope.row.id}})"
										>
										Lire
									</el-dropdown-item>
									<el-dropdown-item
										v-if="active_user_is('admin')"
										:icon="Plus" 
										@click="$router.push({name:'exercicesView', params:{id:scope.row.id}})"
									>
										Ajouter Excercices
									</el-dropdown-item>
									<el-dropdown-item
										v-if="active_user_is('admin')"
										:icon="View" 
										@click="$router.push({name:'exercicesPreview', params:{id:scope.row.id}})"
										>
										Voir Exercices
									</el-dropdown-item>
									<el-dropdown-item
										v-if="active_user_is('admin')"
										:icon="View" 
										@click="$router.push({name:'formulePreview', params:{id_lecon:scope.row.id}})"
									>
										Voir Formules
									</el-dropdown-item>
									<el-dropdown-item
										v-if="active_user_is('admin')"
										:icon="Plus" 
										 @click="$router.push({name:'createFormule', params:{id_lecon:scope.row.id}})"

									>
										Ajouter Formules / Astuces
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
