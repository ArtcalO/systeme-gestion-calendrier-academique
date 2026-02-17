<script >
export default{
	data(){
		return{
			drawer:true,
			modify_password:false,
			old_password:"",
			new_password:"",
			isLoading:false,
			confirm:"",
			visible:false,
		}
	},
	mounted(){
		console.log("mounted side bar")
	},
	methods: {
		modfiyPassCode(){
			if(this.confirm.trim() != this.new_password.trim()){
				this.useNotifyError("Mot de passe non identique !")
				return
			}
			this.isLoading=true
			let data = {
				"old_password":this.old_password,
				"new_password":this.new_password
			}
			axios.post("users/change_password/", data)
			.then(()=>{
				this.isLoading=false
				this.modify_password=false
				this.useNotifySuccess("Mot de passe modifée avec success !")
			}).catch((err)=>{
				this.isLoading=false
				this.errorOrRefresh(err,this.modfiyPassCode)
			})
		},
	},
}

</script>

<template>
	<v-navigation-drawer class="nonprintable" v-model="drawer" :rail="$store.state.rail" permanent>
		<v-list-item
			prepend-icon="mdi-account"
			class="py-2 my-2 border-b"
			:title="app_name"
			:subtitle="active_fullname"
		>
			<template v-slot:append>
				<v-btn
		          variant="text"
		          icon="mdi-pencil"
		          size="small"
		          @click.stop="modify_password=true"
		        ></v-btn>
				<v-btn
					variant="text"
					icon="mdi-logout"
					size="small"
					@click.stop="logOut()"
				></v-btn>
			</template>
		</v-list-item>

		<v-dialog
          transition="dialog-top-transition"
          width="390"
          v-model="modify_password"
        >
          <v-card
            prepend-icon="mdi-lock"
            title="Modifier Mot de passe"
          >
             <v-card-text>
                <v-text-field
                :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
                :type="visible ? 'text' : 'password'"
                density="compact"
                v-model="old_password"
                placeholder="Ancien Mot de passe"
                prepend-inner-icon="mdi-lock-outline"
                variant="outlined"
                @click:append-inner="visible = !visible"
            ></v-text-field>

            <v-text-field
                :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
                :type="visible ? 'text' : 'password'"
                density="compact"
                v-model="new_password"
                placeholder="Nouveau Mot de passe"
                prepend-inner-icon="mdi-lock-outline"
                variant="outlined"
                @click:append-inner="visible = !visible"
            ></v-text-field>

            <v-text-field
                :append-inner-icon="visible ? 'mdi-eye-off' : 'mdi-eye'"
                :type="visible ? 'text' : 'password'"
                density="compact"
                placeholder="Confirmer mot de passe"
                prepend-inner-icon="mdi-lock-outline"
                variant="outlined"
                v-model="confirm"
                @click:append-inner="visible = !visible"
            ></v-text-field>
            
            </v-card-text>

            <v-divider></v-divider>

            <v-card-actions>
              <v-spacer></v-spacer>

              <v-btn
                variant="plain"
                @click="modify_password = false"
              >Annuler</v-btn>

              <v-btn
                color="primary"
                :loading="isLoading"
                @click="modfiyPassCode"
              >Modifier Mot de passe</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

		<!-- <v-divider></v-divider> -->

		<v-list density="compact" color="primary" nav>
			<v-list-subheader>{{ app_name }}</v-list-subheader>
			<v-list-item
				v-if="!active_user_is('eleve','professeur') "
				prepend-icon="mdi-monitor-dashboard"
				title="Niveau"
				:to="{ name: 'niveaux' }"
				link
				exact=""
			>
			</v-list-item>
			<v-list-item
				v-if="!active_user_is('eleve', 'professeur')"
				prepend-icon="mdi-monitor-dashboard"
				title="Sections"
				:to="{ name: 'sections' }"
				link
				exact=""
			>
			</v-list-item>
			<v-list-item
				v-if="!active_user_is('eleve','professeur')"
				prepend-icon="mdi-monitor-dashboard"
				title="Classes"
				:to="{ name: 'classes' }"
				link
				exact=""
			>
			</v-list-item>
			<v-list-item
				v-if="active_user_is('admin')"
				prepend-icon="mdi-monitor-dashboard"
				title="Professeurs"
				:to="{ name: 'profs' }"
				link
				exact=""
			>
			</v-list-item>
			<v-list-item
				v-if="active_user_is('eleve') && active_user.complete"
				prepend-icon="mdi-monitor-dashboard"
				title="Classes"
				:to="{ name: 'classes' }"
				link
				exact=""
			>
			</v-list-item>

			<v-list-item
				v-if="!active_user_is('eleve','professeur')"
				prepend-icon="mdi-monitor-dashboard"
				title="Domaines"
				:to="{ name: 'domaines' }"
				link
				exact=""
			>
			</v-list-item>
			<v-list-item
			    v-if="!active_user_is('eleve')"
				prepend-icon="mdi-monitor-dashboard"
				title="Disciplines"
				:to="{ name: 'disciplines' }"
				link
				exact=""
			>
			</v-list-item>
			<v-list-item
			  v-if="active_user_is('titulaire')"
				prepend-icon="mdi-monitor-dashboard"
				title="Palmares"
				:to="{ name: 'palmares' }"
				link
				exact=""
			>
			</v-list-item>
			<v-list-item
			  v-if="active_user_is('titulaire','admin')"
				prepend-icon="mdi-monitor-dashboard"
				title="Bulletins"
				:to="{ name: 'bulletins' }"
				link
				exact=""
			>
			</v-list-item>
			<v-list-item
				v-if="!active_user_is('eleve')"
				prepend-icon="mdi-monitor-dashboard"
				title="Thèmes"
				:to="{ name: 'themes' }"
				link
				exact=""
			>
			</v-list-item>
			<v-list-item
				v-if="!active_user_is('eleve')"
				prepend-icon="mdi-monitor-dashboard"
				title="Leçons"
				:to="{ name: 'lecons' }"
				link
				exact=""
			>
			</v-list-item>
			<v-list-item
				prepend-icon="mdi-monitor-dashboard"
				title="Bakame"
				:to="{ name: 'chatAi' }"
				link
				exact=""
			>
			</v-list-item>
		</v-list>

	</v-navigation-drawer>
</template>

<style scoped>

</style>
