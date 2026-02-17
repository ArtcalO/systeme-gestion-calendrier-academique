<template>
  <el-dialog
    v-model="dialogVisible"
    :title="'Reponses Exercices : '+found_answer.length+' / '+correctionExerciceProps.length+' | Score : '+ score+' /100'"
    top="2vh"
    width="21cm"
    heigth="1000"
  >
    <el-card
      v-for="(item,i) in correctionExerciceProps"
      :key="item.id"
      :class="{body_success:item.trouve,body_danger:!item.trouve}"
      >
      <template #header>
        <div class="card-header">
          {{correctionExerciceProps}}
          <span>{{item.exercice.question}}</span>
        </div>
      </template>
      <div v-for="(el,i) in shuffleArray([item.exercice.reponse,item.exercice.mauvaise_reponse1,item.exercice.mauvaise_reponse2,item.exercice.mauvaise_reponse3])" :key="i" class="quiz-answer" :data-index="i">
          <input
              type="radio"
              class="form-check-input"
              :value="el"
              :id="item.id"
              :name="item.id"
              v-model="item.reponse"
              disabled
          />
          <label for="question-0-0">{{el}}</label>
          <div class="quiz-feedback"></div>
      </div>
      <template #footer>Footer content</template>
    </el-card>
    <br>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="$emit('close')">Refaire</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script >
export default{
    data(){
      return {
        dialogVisible:true,
      }
    },
    props: ["correctionExerciceProps"],
    methods: {
        upsert(array, element) { // (1)
            const i = array.findIndex(_element => _element.q_id === element.q_id);
            if (i > -1) array[i] = element; // (2)
            else array.push(element);
        },
        shuffleArray(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
            return array
        },
    },
    mounted(){
      console.log(this.correctionExerciceProps)
    },
    computed: {
      found_answer() {
        return this.correctionExerciceProps.filter(x=>x.trouve==true);
      },
      score(){
        return parseInt(this.found_answer.length*100/this.correctionExerciceProps.length)
      },
      quit(){
        console.log("response")
      }
    },
}

</script>
<style scoped>


    /* Exerises */
    .quiz-question-list {
    list-style-position: inside;
    }
    .quiz-question {
    margin: 0 0 30px;
    padding:10px;
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
dialog-overlay{
    width:500px;
}
.body_danger{
  background-color:#f5424273; 
}
.header_danger{
  background-color:#f54242bd;
}

.body_success{
  background-color:#6eff619c;
}
.header_success{
  background-color:#6eff61;
}
.space{
  margin-right:20px;
}

</style>
