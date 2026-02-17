<script >
	export default {
		watch: {
			"$store.state.user":{
				deep:true,
				handler(new_val){
				if(!!new_val){
					localStorage.setItem('user', JSON.stringify(new_val));

				} else {
					localStorage.removeItem('user')
				}
				}
			},
		},
		mounted(){
			console.log("mounted app")
			var user = JSON.parse(localStorage.getItem('user'));
			if(user) {
				this.$store.state.user = user;
				if(this.active_user_is('eleve') && !user.complete)
					this.$router.push('profile/complete/'+this.getEleveId('eleve'))
			}
		}
	} 
</script>

<template>
	<div class="app">
		<router-view :key="$route.fullPath" />
	</div>
</template>

<style>
@media print {
	.nonprintable, button, input{
		display: none!important;
		margin: 0!important;
		padding: 0!important;
	}
	nav{
		display: none !important;
	}
	.v-navigation-drawer__content {
    	display: none;
	}
	.main-container{
	--v-layout-left: 0px;
	--v-layout-right: 0px;
	--v-layout-top: 0px;
	--v-layout-bottom: 0px;
	}
	.page{
		margin: 0!important;
		padding: 0!important;
	}
	body {
		background: white;
	}
	body::after {
		background: white;
	}
	.content,
	.inner-content,
	.page-wrapper {
		margin: 0!important;
		padding: 0!important;
	}
}

</style>
