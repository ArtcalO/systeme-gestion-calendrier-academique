<script >
import ExercicesResponses from "../../components/reusables/ExercicesResponse.vue"
import { Plus,Search } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			exercices:[],responsesExercicesObj:{},response_shown:false,
			isLoading:false,keyword:"",Plus,Search,lecon:{},responses:[]
		}
	},
	components:{ExercicesResponses},
	beforeMount(){
		this.fetchLecon()
	},
	mounted(){
		this.fetchExcercices()
	},
	methods:{
		fetchLecon(){
			this.isLoading=true
			axios.get('lecons/'+this.$route.params.id+'/')
			.then((res)=>{
				this.isLoading=false
				this.lecon=res.data
			})
			.catch((err)=>{
				this.isLoading=false
				this.errorOrRefresh(err, this.fetchLecon)
			})
		},
		fetchExercices() {
			this.fetching=true
			axios
				.get(`${this.url}/exercices/?lecon=${this.$route.params.id}`, this.headers)
				.then((res) => {
					this.exercices = res.data.results;
					this.fetching = false;
				})
				.catch((err) => {
					this.errorOrRefresh(err, this.fetchExercices);
				});
		},
		getCheckBoxValue(el,value){
			let obj = {"q_id":el,"resp":value}
			this.upsert(this.responses,obj)
		},
		upsert(array, element) {
			const i = array.findIndex(_element => _element.q_id === element.q_id);
			if (i > -1) array[i] = element;
			else array.push(element);
		},
		modifier(x) {
			this.edit = true;
			this.$store.state.current_exercice = x;
			this.openModal();
		},
		close(){
			this.fetchExcercices()
			this.response_shown=false
		},
		requestSupprimer(x) {
			this.request = x;
			let modal = document.getElementById("confirm");
			modal.showModal();
		},
		shuffleArray(array) {
			for (let i = array.length - 1; i > 0; i--) {
				const j = Math.floor(Math.random() * (i + 1));
				[array[i], array[j]] = [array[j], array[i]];
			}
			return array
		},
		validateResponses(){
			if(this.responses.length==0){
				this.useNotifyError("Pas de reponses soumises... Veuillez repondre au moins une question !")
			}else
				axios
					.post(`reponsesEleves/`, {"reponses":this.responses,"eleve":this.getEleveId('eleve')}, this.headers)
					.then((res) => {
						this.responsesExercicesObj=res.data
						this.response_shown=true
					})
					.catch((err) => {
						this.errorOrRefresh(err, this.validateResponses);
					});
		},
		fetchExcercices(){
			this.isLoading=true
			axios.get('exercices/?lecon='+this.$route.params.id)
			.then((res)=>{
				this.isLoading=false
				this.exercices=res.data.results
			})
			.catch((err)=>{
				this.isLoading=false
				console.log(err)
				this.errorOrRefresh(err, this.fetchExcercices())
			})
		}
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Exercices pour la lecon <strong>{{lecon?.nom}}</strong></h4>
			</v-col>
			<v-col cols="auto" v-if="active_user_is('admin')">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createExercice', params:{id:$route.params.id} })"
					>Exercice</el-button
				>
			</v-col>
		</v-row>
		<el-card>
			<form v-if="exercices.length>0" class="quiz-body" @submit.prevent="validateUserResponse">
				<ol class="quiz-question-list">
					<li
						class="quiz-question"
						v-for="(item,i) in getRandomElements(exercices,10)"
						:data-index="i"
						data-type="multiple_choice_single_answer"
						:key="item.id"
					>
						<span class="quiz-question-header">{{item.question}}</span>

						<section class="quiz-answers">
							<div v-for="(el,i) in shuffleArray([item.reponse,item.mauvaise_reponse1,item.mauvaise_reponse2,item.mauvaise_reponse3])" :key="i" class="quiz-answer" :data-index="i">
								<input
									type="radio"
									class="form-check-input"
									:value="el"
									:id="item.id"
									:name="item.id"
									@change="getCheckBoxValue(item.id,el)"
								/>
								<label for="question-0-0">{{el}}</label>
								<div class="quiz-feedback"></div>
							</div>
						</section>
					</li>
					<el-button
						:loading="isLoading" v-if="active_user_is('eleve')" @click="validateResponses" type="primary"
						>Valider</el-button>
				</ol>
			</form>
		</el-card>
		<ExercicesResponses v-if="response_shown" :correctionExerciceProps="responsesExercicesObj" @close="close" />
	</div>
</template>

<style lang="css" scoped>
	/* Exerises */
	.quiz-question-list {
	list-style-position: inside;
	}
	.quiz-question {
	margin: 0 0 30px;
	}
	.quiz-answer {
	-webkit-box-align: start;
	-webkit-align-items: flex-start;
	-moz-box-align: start;
	-ms-flex-align: start;
	align-items: flex-start;
	display: -webkit-box;
	display: -webkit-flex;
	display: -moz-box;
	display: -ms-flexbox;
	display: flex;
	margin: 16px 0;
	position: relative;
	}
	input[type="checkbox"],
	input[type="radio"] {
	margin-top: 0;
	position: relative;
	height: 18px;
	width: 18px;
	margin-right: 10px;
	}
	.buttons-groups{
	min-width:400px;
	display:flex;
	justify-content:space-between;
}
</style>
