<script >
import { useGetGenerativeModelGP } from '../../composables/useGetGenerativeModelGP.js'

export default {
	data(){
		return {
			question:"",
			answer:"",
			isLoading:false,
		}
	},
	methods: {
		async fetchAnswer () {
		  this.answer = ''
		  this.isLoading = true
		  try {
		    this.answer = await useGetGenerativeModelGP(this.question)
		    console.log(this.answer)
		  } catch (error) {
		    console.log({ error })
		  } finally {
		    this.isLoading = false
		    this.question = ''
		  }
		}
	},	
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Bakame</h4>
			</v-col>
		</v-row>
		<el-card>
			<el-form label-position="top" label-width="100px" :model="question">
				<h5 class="border-b pb-3 mb-3">Bonjour {{active_user?.first_name}}, je suis <strong>Bakame (Lapinou intelligent)</strong>, demandez-moi quelque chose !</h5>
				<el-row :gutter="20">
					<el-col :span="24" :sm="24">
						<el-form-item >
							<el-input type="textarea" id="question" v-model="question" placeholder="Ecrive votre demande ici" name="nom"
							/>
						</el-form-item>
						<el-button
							class="mt-3"
							:disabled="!question"
							@click="fetchAnswer"
							size="default"
				          	type="primary"
						>
						{{ `${isLoading ? 'bakame en cours ...' : 'Demander à Bakame'}` }}
						</el-button>
					</el-col>
					
				</el-row>
			</el-form>
			<br>
			<div>
				<p v-if="answer">{{ answer }}</p>
			</div>
		</el-card>
	</div>
</template>

