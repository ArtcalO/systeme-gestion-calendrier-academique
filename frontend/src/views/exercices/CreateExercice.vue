<script >
import { UploadFilled } from '@element-plus/icons-vue'
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			exercice:{
				lecon:this.$route.params.id,
				question: "",
				detail: "",
				reponse: "",
				mauvaise_reponse1: "",
				mauvaise_reponse2: "",
				mauvaise_reponse3: "",
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
			axios.get('exercices/'+this.$route.params.id+"/")
			.then((res)=>{
				this.isLoading=false
				this.exercice.question = response.data.question
				this.exercice.detail = response.data.detail
				this.exercice.reponse = response.data.reponse
				this.exercice.mauvaise_reponse1 = response.data.mauvaise_reponse1
				this.exercice.mauvaise_reponse2 = response.data.mauvaise_reponse2
				this.exercice.mauvaise_reponse3 = response.data.mauvaise_reponse3
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
			})
		},
		createExercice(){
			if(
				this.exercice.mauvaise_reponse1.trim()=="" ||
				this.exercice.mauvaise_reponse2.trim()=="" ||
				this.exercice.mauvaise_reponse3.trim()=="" ||
				this.exercice.reponse.trim()=="" ||
				this.exercice.question.trim()==""
			){
				this.useNotifyError("Veuillez remplir toutes les cases !")
				return
			}

			this.isLoading=true 
			console.log(this.exercice)
			axios.post("exercices/", this.exercice)
			.then((response)=>{
				this.useNotifySuccess("Exercice Crée avec success !")
				this.$store.state.exercices.push(response.data)
				this.$router.go(-1)
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.createExercice)
			}).finally(()=>this.isLoading=false)			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" :model="exercice">
			<h5 class="border-b pb-3 mb-3">Ajout de l'exercice</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">	
					<el-form-item label="Question">
						<el-input v-model="exercice.question" placeholder="question de l'exercice" name="question" />
					</el-form-item>
					<el-form-item label="Details">
						<el-input v-model="exercice.detail" placeholder="detail de l'exercice" name="detail" />
					</el-form-item>
					<el-form-item label="Reponse">
						<el-input v-model="exercice.reponse" placeholder="reponse de l'exercice" name="reponse" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Mauvaise reponse 1 ">
						<el-input v-model="exercice.mauvaise_reponse1" placeholder="mauvaise_reponse1" name="mauvaise_reponse1" />
					</el-form-item>
					<el-form-item label="Mauvaise reponse 2">
						<el-input v-model="exercice.mauvaise_reponse2" placeholder="mauvaise_reponse2" name="mauvaise_reponse2" />
					</el-form-item>
					<el-form-item label="Mauvaise reponse 3">
						<el-input v-model="exercice.mauvaise_reponse3" placeholder="mauvaise_reponse3" name="mauvaise_reponse3" />
					</el-form-item>
				</el-col>
			</el-row>
			<br/>
			<el-button :loading="isLoading" @click="createExercice" type="primary" size="large"
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
