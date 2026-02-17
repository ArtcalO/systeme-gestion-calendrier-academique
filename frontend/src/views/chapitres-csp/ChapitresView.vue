<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			chapitres:this.$store.state.chapitres,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.chapitres"(new_val){
	 	this.chapitres=new_val
	 },
	 "keyword"(new_val){
	 	this.chapitres = this.$store.state.chapitres.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchchapitres()
	},
	methods:{
		fetchchapitres(){
			this.isLoading=true
			axios.get('chapitres/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.chapitres=res.data.results
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
				<h4 class="font-weight-medium">Chapitres</h4>
			</v-col>
			<v-col cols="auto" v-if="active_user_is('eleve')">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createChapitre', params:{id:$route.params.id} })"
					>Chapitre</el-button
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
			<el-table v-loading="isLoading" :data="chapitres" style="width: 100%">
				<el-table-column fixed label="Nom du chapitre" min-width="90">
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
				<el-table-column fixed="right" label="Actions" min-width="80">
			      <template #default="scope">
			        <el-button
			          size="small"
			          type="primary"
			          @click="$router.push({name:'chapitrePreview', params:{id:scope.row.id}})"
			          >Lire</el-button
			        >
			        <el-button
			          v-if="!active_user_is('eleve')"
			          size="small"
			          type="warning"
			          @click="$router.push({name:'exercicesCSPView', params:{id:scope.row.id}})"
			          >Exercices</el-button
			        >
			        <el-button
			          v-if="active_user_is('eleve')"
			          size="small"
			          type="warning"
			          @click="$router.push({name:'createExerciceCSP', params:{id:scope.row.id}})"
			          >Ajouter Exercices</el-button
			        >
			        <el-button
			          size="small"
			          type="primary"
			          @click="$router.push({name:'exerciceCSP', params:{id:scope.row.id}})"
			          >Voir Exercices</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
