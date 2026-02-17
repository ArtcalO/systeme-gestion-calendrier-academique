<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			section:{
				niveau:null,
				nom:"",
			},
		}
	},
	beforeMount(){
		this.fetchNiveaux()
		if(this.$route.params.id)
			this.fetchSingleSection()
	},
	components:{
		UploadFilled,
	},
	methods:{
		fetchNiveaux(){
			this.isLoading=true
			axios.get('niveaux/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.niveaux=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
		fetchSingleSection(){
			this.isLoading=true
			axios.get('sections/'+this.$route.params.id+"/")
			.then((res)=>{
				this.isLoading=false
				this.section.niveau = res.data.niveau.id
				this.section.nom = res.data.nom
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
		createsection(){
			if(this.section.niveau==null){
				this.useNotifyError("Veuillez specifier le niveau de la section !")
				return
			}
			if(this.section.nom.trim()==""){
				this.useNotifyError("Veuillez specifier le nom de la section !")
				return
			}
			this.isLoading=true
			
			if(!this.$route.params.id)
				axios.post("sections/", this.section)
				.then((response)=>{
					this.useNotifySuccess("section Crée avec success !")
					this.$store.state.sections.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createsection)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`sections/${this.$route.params.id}/`, this.section)
				.then((response)=>{
					this.useNotifySuccess("section modifé avec success !")
					this.$store.state.sections.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createsection)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="section">
			<h5 class="border-b pb-3 mb-3">Ajout section</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Niveau">
						<el-select filterable v-model="section.niveau" placeholder="Select" class="w-100">
							<el-option
								v-for="item in $store.state.niveaux"
								:key="item.id"
								:label="item.nom"
								:value="item.id"
							/>
						</el-select>
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom">
						<el-input v-model="section.nom" placeholder="nom de la section" name="nom" />
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createsection" type="primary" size="large"
				>Valider</el-button
			>
		</el-form>
	</el-card>
</template>

<style scoped>
.drop-area {
	text-align: center;
	padding: 20px;
	background-color: #f1f1f1;
	border: 2px dashed #ccc;
	cursor: pointer;
}

.drag-over {
	background-color: #c1c1c1;
}

.dropzone-text {
	padding: 10px;
}

img {
	max-width: 100%;
	max-height: 115px;
}
</style>
