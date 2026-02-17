<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			books:this.$store.state.books,
			isLoading:false,keyword:"",Plus,Search
		}
	},
	watch: {
	 "$store.state.books"(new_val){
	 	this.books=new_val
	 },
	 "keyword"(new_val){
	 	this.books = this.$store.state.books.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	mounted(){
		this.fetchbooks()
	},
	methods:{
		fetchbooks(){
			this.isLoading=true
			axios.get('livres/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.books=res.data.results
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
				<h4 class="font-weight-medium">Bibliothèque</h4>
			</v-col>
			<v-col cols="auto" v-if="!active_user_is('eleve')">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createBook' })"
					>Livre</el-button
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
			<el-table v-loading="isLoading" :data="books" style="width: 100%">
				<el-table-column fixed label="Titre" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.titre
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Auteur" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.auteur
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed label="Année de sortie" min-width="90">
					<template #default="scope">
						<div>
							<span>
								{{ 
									scope.row.annee
								}}
							</span>
						</div>
					</template>
				</el-table-column>
				<el-table-column fixed="right" label="Actions" min-width="80">
			      <template #default="scope">
			        <el-button
			          v-if="active_user_is('admin')"
			          size="small"
			          type="primary"
			          @click="$router.push({name:'modifyBook', params:{id:scope.row.id}})"
			          >Modifier</el-button
			        >
			        <el-button
			          size="small"
			          type="primary"
			          @click="$router.push({name:'bookPreview', params:{id:scope.row.id}})"
			          >Lire</el-button
			        >
			      </template>
			    </el-table-column>		
			</el-table>
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
