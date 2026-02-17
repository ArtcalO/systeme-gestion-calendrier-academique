<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			imageData1:null,
			lecon:{
				niveau:null,
				nom:"",
				pdf:null,
			},
		}
	},
	beforeMount(){
		this.fetchThemes()
		if(this.$route.params.id)
			this.fetchSingleLecon()
	},
	components:{
		UploadFilled,
	},
	methods:{
		getLivre(e){
	      this.lecon.pdf=e.target.files[0]
	    },
		fetchThemes(){
			this.isLoading=true
			axios.get('themes/')
			.then((res)=>{
				this.isLoading=false
				this.$store.state.themes=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
		fetchSingleLecon(){
			this.isLoading=true
			axios.get('lecons/'+this.$route.params.id+"/")
			.then((res)=>{
				this.isLoading=false
				this.lecon.theme = res.data.theme.id
				this.lecon.nom = res.data.nom
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
		createLecon(){
			if(this.lecon.theme==null){
				this.useNotifyError("Veuillez specifier le theme !")
				return
			}
			if(this.lecon.nom.trim()==""){
				this.useNotifyError("Veuillez specifier le nom de la leçon !")
				return
			}
			this.isLoading=true
			let data = new FormData()
			data.append("theme",this.lecon.theme)
			data.append("nom",this.lecon.nom)
			data.append("pdf",this.lecon.pdf)
			if(!this.$route.params.id)
				axios.post("lecons/", data)
				.then((response)=>{
					this.useNotifySuccess("lecon Crée avec success !")
					this.$store.state.lecons.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createLecon)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`lecons/${this.$route.params.id}/`, data)
				.then((response)=>{
					this.useNotifySuccess("lecon modifé avec success !")
					this.$store.state.lecons.push(response.data)
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createLecon)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="lecon">
			<h5 class="border-b pb-3 mb-3">Ajout lecon</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Theme">
						<el-select filterable v-model="lecon.theme" placeholder="Select" class="w-100">
							<el-option
								v-for="item in $store.state.themes"
								:key="item.id"
								:label="item.nom"
								:value="item.id"
							/>
						</el-select>
					</el-form-item>
					<el-form-item label="Nom">
						<el-input v-model="lecon.nom" placeholder="nom de la lecon" name="nom" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="PDF">
					 <v-file-input
			            variant="outlined"
			            density="compact"
			            clearable
			            label="Fichier PDF"
			            @change="e=>getLivre(e)"
			          ></v-file-input>
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createLecon" type="primary" size="large"
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
