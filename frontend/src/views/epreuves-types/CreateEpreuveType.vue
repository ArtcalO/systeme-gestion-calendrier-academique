<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			editions:[],
			epreuve:{
				discipline:this.$route.params.id_discipline,
				pdf:null,
				edition:null,
			},
		}
	},
	beforeMount(){
		this.fetchEditions()
		if(this.$route.name == "")
			this.fetchSinglEpreuve()
	},
	components:{
		UploadFilled,
	},
	methods:{
		getLivre(e){
	      this.epreuve.pdf=e.target.files[0]
	    },
		fetchEditions(){
			this.isLoading=true
			axios.get('editions/')
			.then((res)=>{
				this.isLoading=false
				this.editions=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
				this.errorOrRefresh(err, this.fetchEditions)
			})
		},
		fetchSinglEpreuve(){
			this.isLoading=true
			axios.get('epreuves/'+this.$route.params.id_discipline+"/")
			.then((res)=>{
				this.isLoading=false
				this.epreuve.discipline = res.data.discipline
				this.epreuve.pdf = res.data.pdf
				this.epreuve.edition = res.data.edition
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
				this.errorOrRefresh(err,this.fetchSinglEpreuve)
			})
		},
		createEpreuveType(){
			if(this.epreuve.pdf==null){
				this.useNotifyError("Veuillez specifier le pdf de l'epreuve type !")
				return
			}
			if(this.epreuve.edition == null){
				this.useNotifyError("Veuillez specifier l'edition de l'epreuve type !")
				return
			}
			this.isLoading=true
			let data = new FormData()
			data.append("discipline",this.epreuve.discipline)
			data.append("edition",this.epreuve.edition)
			data.append("pdf",this.epreuve.pdf)
			if(this.$route.name=="editEpreuveType")
				axios.put(`epreuvesTypes/${this.$route.params.id_epreuve}/`, data)
				.then((response)=>{
					this.useNotifySuccess("epreuve modifé avec success !")
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createEpreuveType)
				}).finally(()=>this.isLoading=false)
			else
				axios.post("epreuvesTypes/", data)
				.then((response)=>{
					this.useNotifySuccess("epreuve Crée avec success !")
					this.$router.go(-1)
				})
				.catch((error)=>{
					this.isLoading=false
					console.log(error)
					this.errorOrRefresh(error, this.createEpreuveType)
				}).finally(()=>this.isLoading=false)

		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="epreuve">
			<h5 class="border-b pb-3 mb-3">Ajout epreuve</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Theme">
						<el-select filterable v-model="epreuve.edition" placeholder="Editions" class="w-100">
							<el-option
								v-for="item in editions"
								:key="item.id"
								:label="item.session"
								:value="item.id"
							/>
						</el-select>
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
			<el-button :loading="isLoading" @click="createEpreuveType" type="primary" size="large"
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
