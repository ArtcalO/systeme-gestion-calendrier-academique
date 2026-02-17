<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			imageData1:null,
			livre:{
				auteur:"",
				maison:"",
				titre:"",
				categorie:"",
				cover:null,
				description:"",
				annee:"",
				pdf:null,
			},
		}
	},
	beforeMount(){
		if(this.$route.params.id)
			this.fetchSingleBook()
	},
	components:{
		UploadFilled,
	},
	methods:{
		getLivre(e){
	      this.livre.pdf=e.target.files[0]
	    },
	    getCover(e){
	      this.livre.cover=e.target.files[0]
	    },
		fetchSingleBook(){
			this.isLoading=true
			axios.get('livres/'+this.$route.params.id+"/")
			.then((res)=>{
				this.isLoading=false
				this.livre.auteur = res.data.auteur
				this.livre.maison = res.data.maison
				this.livre.titre = res.data.titre
				this.livre.categorie = res.data.categorie
				this.livre.cover = res.data.cover
				this.livre.description = res.data.description
				this.livre.annee = res.data.annee
				this.livre.pdf = res.data.pdf
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
				this.errorOrRefresh(err, this.fetchSingleBook)
			})
		},
		createBook(){
			if(this.livre.auteur.trim()=="" ){
				this.useNotifyError("Veuillez specifier l'auteur !")
				return
			}
			if(this.livre.maison.trim()==""){
				this.useNotifyError("Veuillez specifier le maison du livre !")
				return
			}if(this.livre.titre.trim()==""){
				this.useNotifyError("Veuillez specifier le titre du livre !")
				return
			}if(this.livre.categorie.trim()==""){
				this.useNotifyError("Veuillez specifier le categorie du livre !")
				return
			}if(this.livre.cover==null){
				this.useNotifyError("Veuillez specifier le cover du livre !")
				return
			}if(this.livre.description.trim()==""){
				this.useNotifyError("Veuillez specifier le description du livre !")
				return
			}if(this.livre.annee.trim()==""){
				this.useNotifyError("Veuillez specifier le annee du livre !")
				return
			}if(this.livre.pdf==null){
				this.useNotifyError("Veuillez specifier le pdf du livre !")
				return
			}
			this.isLoading=true
			let data = new FormData()
			data.append("auteur", this.livre.auteur)
			data.append("maison", this.livre.maison)
			data.append("titre", this.livre.titre)
			data.append("categorie", this.livre.categorie)
			data.append("cover", this.livre.cover)
			data.append("description", this.livre.description)
			data.append("annee", this.livre.annee)
			data.append("pdf", this.livre.pdf)
			if(!this.$route.params.id)
				axios.post("livres/", data)
				.then((response)=>{
					this.useNotifySuccess("livre Crée avec success !")
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createBook)
				}).finally(()=>this.isLoading=false)
			else
				axios.put(`livres/${this.$route.params.id}/`, data)
				.then((response)=>{
					this.useNotifySuccess("livre modifé avec success !")
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createBook)
				}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="livre">
			<h5 class="border-b pb-3 mb-3">Ajout livre</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Auteur">
						<el-input v-model="livre.auteur" placeholder="auteur du livre" name="nom" />
					</el-form-item>
					<el-form-item label="Maison">
						<el-input v-model="livre.maison" placeholder="maison du livre" name="nom" />
					</el-form-item>
					<el-form-item label="Titre">
						<el-input v-model="livre.titre" placeholder="titre du livre" name="nom" />
					</el-form-item>
					<el-form-item label="Categorie">
						<el-input v-model="livre.categorie" placeholder="categorie du livre" name="nom" />
					</el-form-item>			
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Couverture">
					 <v-file-input
			            variant="outlined"
			            density="compact"
			            clearable
			            label="Couverture"
			            @change="e=>getCover(e)"
			          ></v-file-input>
					</el-form-item>
					<el-form-item label="Description">
						<el-input v-model="livre.description" placeholder="description du livre" name="nom" />
					</el-form-item>
					<el-form-item label="Annee">
						<el-input v-model="livre.annee" placeholder="annee du livre" name="nom" />
					</el-form-item>
					
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
			<el-button :loading="isLoading" @click="createBook" type="primary" size="large"
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
