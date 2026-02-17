<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			sections:this.$store.state.sections,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.sections"(new_val){
	 	this.sections=new_val
	 },
	 "keyword"(new_val){
	 	this.sections = this.$store.state.sections.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchSections()
	},
	methods:{
		fetchSections(){
			this.isLoading=true
			axios.get('sections/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.sections=res.data.results
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
				<h4 class="font-weight-medium">Sections</h4>
			</v-col>
			<v-col cols="auto">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createSection' })"
					>Section</el-button
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
			<el-table v-loading="isLoading" :data="sections" style="width: 100%">
				<el-table-column fixed label="Niveau" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.niveau.nom
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
			          @click="$router.push({name:'modifySection', params:{id:scope.row.id}})"
			          >Modifier</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
