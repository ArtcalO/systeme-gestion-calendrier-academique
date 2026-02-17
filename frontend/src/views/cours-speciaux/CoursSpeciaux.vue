<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			cours_speciaux:this.$store.state.cours_speciaux,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.cours_speciaux"(new_val){
	 	this.cours_speciaux=new_val
	 },
	 "keyword"(new_val){
	 	this.cours_speciaux = this.$store.state.cours_speciaux.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchcoursSpeciaux()
	},
	methods:{
		fetchcoursSpeciaux(){
			this.isLoading=true
			axios.get('coursSpeciaux/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.cours_speciaux=res.data.results
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
				<h4 class="font-weight-medium">Cours spéciaux</h4>
			</v-col>
			<v-col cols="auto" v-if="active_user_is('admin')">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createCoursSpecial' })"
					>Cours Spécial</el-button
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
			<el-table v-loading="isLoading" :data="cours_speciaux" style="width: 100%">
				<el-table-column fixed label="Thème" min-width="90">
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
			          type="warning"
			          @click="$router.push({name:'chapitres', params:{id:scope.row.id}})"
			          >Chapitres</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
