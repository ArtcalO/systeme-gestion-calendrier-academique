<script >
import { useDateFormat } from '@vueuse/core'

export default{
	data(){
		return {
			confirm:"",
			isLoading:false,
			classes:[],
			profile:{
				first_name:"",
				last_name:"",
				telephone:"",
				genre:"M",
				date_naissance:"",
				classe:null,
			},
		}
	},
	mounted(){
		this.fetchClasses()
	},
	methods:{
		fetchClasses(){
			this.isLoading=true
			axios.get('classes/')
			.then((response)=>{
				this.isLoading=false
				this.classes = response.data.results
				this.fetchEleve()
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.fetchClasses)
			})
		},
		fetchEleve(){
			this.isLoading=true
			axios.get(`eleves/${this.getEleveId('eleve')}/`)
			.then((response)=>{
				this.isLoading=false
				this.profile.first_name = response.data.user.first_name
				this.profile.last_name = response.data.user.last_name
				this.profile.telephone = response.data.telephone
				this.profile.genre = response.data.genre
				this.profile.date_naissance = response.data.date_naissance
				this.profile.classe = response.data.classe
			})
			.catch((error)=>{
				this.isLoading=false
				console.log(error)
				this.errorOrRefresh(error, this.fetchClasses)
			})
		},
		completeProfile(){
			if(this.profile.first_name.trim()==""){
				this.useNotifyError("Veuillez specifier votre prenom !")
				return
			}
			if(this.profile.last_name.trim()==""){
				this.useNotifyError("Veuillez specifier votre nom !")
				return
			}
			if(this.profile.genre.trim()==""){
				this.useNotifyError("Veuillez specifier votre genre !")
				return
			}
			if(this.profile.date_naissance.trim()==""){
				this.useNotifyError("Veuillez specifier votre date de naissance !")
				return
			}
			if(this.profile.classe==null){
				this.useNotifyError("Veuillez specifier votre classe !")
				return
			}
			this.isLoading=true

			axios.post(`eleves/${this.getEleveId('eleve')}/complete-profile/`, this.profile)

			.then((res)=>{
				this.useNotifySuccess("Profile completé avec succes, vouz allez être deconnecté !")
				this.$store.state.user = null
				localStorage.removeItem('user')
        		window.location="/"
			})
			.catch((err)=>{
				this.isLoading=false
				this.useNotifyError("Une erreur s'est produite !")
			}).finally(()=>this.isLoading=false)

			
		},
	}
}
</script>

<template>
	<el-card>
		<el-form label-position="top" label-width="100px" >
			<h5 class="border-b pb-3 mb-3">Completer profile</h5>
			<el-row :gutter="20">
				<el-col :span="24" :sm="12">
					<el-form-item label="Nom">
						<el-input type="text" v-model="profile.last_name" name="Nom" />
					</el-form-item>
					<el-form-item label="Prénom">
						<el-input type="text" v-model="profile.first_name" name="prenom" />
					</el-form-item>
					<el-form-item label="Téléphone">
						<el-input type="text" v-model="profile.telephone" name="telephone" />
					</el-form-item>
				</el-col>
				<el-col :span="24" :sm="12">
					<el-form-item label="Genre">
						<el-select filterable v-model="profile.genre" placeholder="Select" class="w-100">
							<el-option
								label="Masculin"
								value="M"
							/>
							<el-option
								label="Féminin"
								value="F"
							/>
						</el-select>
					</el-form-item>
					<el-form-item label="Date de naissance">
						<el-input type="date" v-model="profile.date_naissance" name="date_naissance" />
					</el-form-item>
					<el-form-item label="Classe">
						<el-select filterable v-model="profile.classe" placeholder="Select" class="w-100">
							<el-option
								v-for="classe in classes"
								:label="classe.nom+'  '+classe?.section?.nom+'  '+classe?.section?.niveau?.nom"
								:value="classe.id"
							/>
						</el-select>
					</el-form-item>
				</el-col>
			</el-row>
			<el-button class="mt-3" :loading="isLoading" @click="completeProfile" type="primary" size="large"
				>Completer</el-button
			>
		</el-form>
	</el-card>
</template>

<style scoped>
</style>
