<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			classes:this.$store.state.classes,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.classes"(new_val){
	 	this.classes=new_val
	 	console.log(this.classes)
	 },
	 "keyword"(new_val){
	 	this.classes = this.$store.state.classes.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchClasses()
	},
	methods:{
		fetchClasses(){
			this.isLoading=true
			axios.get('epreuvesTypes/classes-test/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.classes=res.data
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
			<el-table v-loading="isLoading" :data="classes" style="width: 100%">
				<el-table-column fixed label="Section" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.section.nom
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
				<el-table-column fixed="right" label="Actions" min-width="80">
			      <template #default="scope">
			        <el-button
			          size="small"
			          type="primary"
			          @click="$router.push({name:'epTypDomaines', params:{id_classe:scope.row.id}})"
			          >Domaines</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
