<script>
import { User, Lock } from '@element-plus/icons-vue'
export default{
	data(){
		return {
			isLoading:false,
			username:"",
			password:"",
			confirm:"",
			User,Lock
		}
	},
	methods: {
		login(){
			if(this.username.trim()==""){
				this.useNotifyError("Veuillez remplir votre nom d'utilisateur ou telephone")
				return
			}
			if(this.password.trim()==""){
				this.useNotifyError("Veuillez remplir votre mot de passe")
				return
			}
			if(this.confirm.trim()==""){
				this.useNotifyError("Veuillez confirmer votre mot de passe ")
				return
			}
			if(this.confirm.trim()!=this.password.trim()){
				this.useNotifyError("Les deux mots de passe ne correspondnent pas")
				return
			}
			let data = {
				"username":this.username,
				"password":this.password
			}
			axios.post("users/register/", data)
			.then((res)=>{
				this.useNotifySuccess("Enregistrement avec success")
				this.$store.state.user = res.data
				this.$router.push('/login')
			})
			.catch((err)=>{
				console.log(err)
				this.useNotifyError("Enregistrement echoué, Veuillez réesayer!")
			}).finally(()=>this.isLoading=false)
		}
	},
}
</script>

<template>
	<main class="min-vh-100 d-flex is-background">
		<div class="flex-grow-1">
			<div class="h-100 py-5 d-flex align-items-center">
				<v-container>
					<v-row align="center" justify="center" class="h-100">
						<v-col cols="10" sm="8" md="6" lg="5">
							<v-card class="shadow border-primary rounded border-3 border-t border-b px-4 py-12">
								<v-card-title class="border-b">
									<h5 class="fw-700 opacity-75">Créer un compte</h5>
								</v-card-title>
								<v-card-text class="px-8">
									<v-form class="mt-4" @submit.prevent="login">
										<div class="mb-4">
											<v-label class="fs-13">Telephone ou email</v-label>
											<el-input
												v-model="username"
												size="large"
												placeholder="Telephone ou email"
												:prefix-icon="User"
												required
											/>
										</div>
										<div class="mb-4">
											<v-label class="fs-13">Mot de passe</v-label>
											<el-input
												v-model="password"
												type="password"
												size="large"
												placeholder="********"
												:prefix-icon="Lock"
												show-password
												required
											/>
										</div>
										<div class="mb-4">
											<v-label class="fs-13">Confirmer</v-label>
											<el-input
												v-model="confirm"
												type="password"
												size="large"
												placeholder="********"
												:prefix-icon="Lock"
												show-password
												required
											/>
										</div>
										<v-btn
											color="primary"
											type="submit"
											class="text-none"
											size="large"
											:loading="isLoading"
											>Créer</v-btn
										>
										<div class="buttons">
											<a href="/login">Se connecter</a>
										</div>
									</v-form>
								</v-card-text>
							</v-card>
						</v-col>
					</v-row>
				</v-container>
			</div>
		</div>
	</main>
</template>

<style scoped>
.is-background {
	background: #fafbf9;
}
.buttons{
	display: flex;
	margin-top:15px;
	justify-content: space-between;
}
</style>
