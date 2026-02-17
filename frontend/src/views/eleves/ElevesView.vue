<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			eleves:this.$store.state.eleves,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.eleves"(new_val){
	 	this.eleves=new_val
	 },
	 "keyword"(new_val){
	 	this.eleves = this.$store.state.eleves.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchEleves()
	},
	methods:{
		fetchEleves(){
			this.isLoading=true
			if(!this.$route.params.id_classe)
				axios.get('eleves/')
				.then((res)=>{
					this.isLoading=false
					this.$store.state.eleves=res.data.results
				})
				.catch((err)=>{
					this.isLoading=false
					console.log(err)
				})
			else
				axios.get('eleves/?classe='+this.$route.params.id_classe)
				.then((res)=>{
					this.isLoading=false
					this.$store.state.eleves=res.data.results
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
				<h4 class="font-weight-medium">Elèves</h4>
			</v-col>
			<v-col cols="auto">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createEleve' })"
					>Elève</el-button
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
			<el-table v-loading="isLoading" :data="eleves" style="width: 100%">
				<el-table-column fixed label="Nom" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.user.last_name
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Prenom" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.user.first_name
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Genre" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.genre
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Date de naissance" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.date_naissance
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
			          @click="$router.push({name:'modifyEleve', params:{id_eleve:scope.row.id}})"
			          >Modifier</el-button
			        >
			      </template>
			    </el-table-column>	
			</el-table>
		</el-card>
		
	</div>
</template>

<style lang="scss" scoped></style>
