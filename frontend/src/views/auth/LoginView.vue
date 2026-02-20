<script>
import { User, Lock } from '@element-plus/icons-vue'
export default{
	data(){
		return {
			isLoading:false,
			username:"",
			password:"",
		}
	},
	methods: {
		login(){
			let data = {
				"username":this.username,
				"password":this.password
			}
			axios.post("/auth/login/", data)
			.then((res)=>{
				this.useNotifySuccess("Kaze kandi !")
				this.$store.state.user = res.data
				this.$router.push('/profs')
			})
			.catch((err)=>{
				console.log(err)
				this.errorOrRefresh(err,this.login)
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
							<v-card class="shadow border-primary rounded border-3 border-t border-b px-4 py-5">
								<div class="text-center mb-6">
									<img
										src="@/assets/logo.png"
										alt="Login"
										class="login-image"
									/>
								</div>
								<v-card-title class="border-b">
									<h5 class="fw-700 opacity-75">Se Connecter</h5>
								</v-card-title>
								<v-card-text class="px-8">
									<v-form class="mt-4" @submit.prevent="login">
										<div class="mb-4">
											<v-label class="fs-13">Nom d'utilisateur</v-label>
											<el-input
												v-model="username"
												size="large"
												placeholder="Votre nom d'utilisateur"
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
										<v-btn
											color="primary"
											type="submit"
											class="text-none"
											size="large"
											:loading="isLoading"
											>Connexion</v-btn
										>
									</v-form>
								</v-card-text>
							</v-card>
						</v-col>
					</v-row>
					<br>
					<center>
					  {{ new Date().getFullYear() }} — Yakozwe na <strong><a href="https://www.ksquad.dev" target="_blank" style="text-decoration:none;color:#E91E63;margin-top:15px;">K SQUAD</a></strong>
					</center>
				</v-container>
			</div>
		</div>
	</main>
</template>

<style scoped>
.is-background {
	background: #fafbf9;
}
.login-image {
	width: 120px;
}
</style>
