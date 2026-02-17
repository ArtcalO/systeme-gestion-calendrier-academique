<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			themes:this.$store.state.themes,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.themes"(new_val){
	 	this.themes=new_val
	 },
	 "keyword"(new_val){
	 	this.themes = this.$store.state.themes.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchThemes()
	},
	methods:{
		fetchThemes(){
			this.isLoading=true
			let url=""
			if(this.$route.name=="themesDiscipline")
				url='themes/?discipline='+this.$route.params.id_discipline
			else
				url = 'themes/'
			axios.get(url)
			.then((res)=>{
				this.isLoading=false
				this.$store.state.themes=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				this.errorOrRefresh(err, this.fetchThemes)
			})
		}
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Themes</h4>
			</v-col>
			<v-col cols="auto" v-if="!active_user_is('eleve')">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createTheme' })"
					>Theme</el-button
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
			<el-table v-loading="isLoading" :data="themes" style="width: 100%">
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
				<el-table-column fixed label="Theme" min-width="90">
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
			          v-if="!active_user_is('eleve')"
			          size="small"
			          type="primary"
			          @click="$router.push({name:'modifyTheme', params:{id:scope.row.id}})"
			          >Modifier</el-button
			        >
			         <el-button
			           v-if="active_user_is('eleve')"
			          size="small"
			          type="primary"
			          @click="$router.push({name:'leconsTheme', params:{id_theme:scope.row.id}})"
			          >Lecons</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
