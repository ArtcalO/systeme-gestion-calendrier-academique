<script setup>
import TheHeader from './TheHeader.vue'
import TheSidebar from './TheSidebar.vue'
</script>

<template>
	<v-layout>
		<the-sidebar v-if="!$store.state.printing"/>
		<the-header v-if="!$store.state.printing"/>
		<v-main >
			<v-container fluid="" >
				<router-view />
			</v-container>
		</v-main>
		
	</v-layout>
</template>

<style scoped>
.main-container {
	position: relative;
	margin: 0 auto;
	clear: both;
}
.content {
	margin-left: 250px;
	float: unset;
	right: 0;
}
.inner-content {
	padding: 10px;
}
.page-wrapper {
	padding: 0.6rem 1.5rem;
	-webkit-transition: all ease-in 0.3s;
	transition: all ease-in 0.3s;
}
@media print {
	.nonprintable, button, input{
		display: none!important;
	}
	.main-container {
		position: relative;
		margin: 0 !important;
		padding:0 !important;
		--v-layout-left: 0px !important;
	    --v-layout-right: 0px !important;
	    --v-layout-top: 0px !important;
	    --v-layout-bottom: 0px !important;
	}
	.v-container{
		padding:0 !important;
		--v-layout-left: 0px !important;
	    --v-layout-right: 0px !important;
	    --v-layout-top: 0px !important;
	    --v-layout-bottom: 0px !important;
	}
	.printable{
		display: inherit;
	}
	div.v-container.v-container--fluid{
	    --v-layout-left: 0px;
	    --v-layout-right: 0px;
	    --v-layout-top: 0px;
	    --v-layout-bottom: 0px;
	}
	.content,
	.inner-content,
	.page-wrappe {
		margin: 0!important;
		padding: 0!important;
	}
}
</style>
