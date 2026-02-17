<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			domaines:this.$store.state.domaines,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.domaines"(new_val){
	 	this.domaines=new_val
	 },
	 "keyword"(new_val){
	 	this.domaines = this.$store.state.domaines.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchDomaines()
	},
	methods:{
		fetchDomaines(){
			this.isLoading=true
			axios.get('domaines/?classe='+this.$route.params.id_classe)
			.then((res)=>{
				this.isLoading=false
				this.$store.state.domaines=res.data.results
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
				<h4 class="font-weight-medium">Domaines</h4>
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
			<el-table v-loading="isLoading" :data="domaines" style="width: 100%">
				<el-table-column fixed label="Classe" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.classe.nom
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Domaine" min-width="90">
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
			          @click="$router.push({name:'epreuvesTypes', params:{id_domaine:scope.row.id}})"
			          >Epreuves Types</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
