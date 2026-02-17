<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			epreuves_types:this.$store.state.epreuves_types,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.epreuves_types"(new_val){
	 	this.epreuves_types=new_val
	 },
	 "keyword"(new_val){
	 	this.epreuves_types = this.$store.state.epreuves_types.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchepreuves_types()
	},
	methods:{
		fetchepreuves_types(){
			this.isLoading=true
			axios.get('domaines/'+this.$route.params.id_domaine+'/ep-type-domaine/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.epreuves_types=res.data
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
				<h4 class="font-weight-medium">Epreuves Types</h4>
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
			<el-table v-loading="isLoading" :data="epreuves_types" style="width: 100%">
				<el-table-column fixed label="Session" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.edition.session
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Discipline" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.discipline.nom
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
			          @click="$router.push({name:'epreuvePreview', params:{id_epreuve:scope.row.id}})"
			          >Lire</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
