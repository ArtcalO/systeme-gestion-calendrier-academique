<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			profs:this.$store.state.profs,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.profs"(new_val){
	 	this.profs=new_val
	 },
	 "keyword"(new_val){
	 	this.profs = this.$store.state.profs.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		console.log("mounted profs")
		this.fetchProfs()
	},
	methods:{
		fetchProfs(){
			this.isLoading=true
			axios.get('/users/professors/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.profs=res.data.results
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
				<h4 class="font-weight-medium">Professeurs</h4>
			</v-col>
			<v-col cols="auto">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createProf' })"
					>Professeur</el-button
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
			<el-table v-loading="isLoading" :data="profs" style="width: 100%">
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
				<el-table-column fixed label="Email" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.user.email
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
			          @click="$router.push({name:'modifyProf', params:{id:scope.row.id}})"
			          >Modifier</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
