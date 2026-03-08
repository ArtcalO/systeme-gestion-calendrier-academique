import { createStore } from 'vuex'

export default createStore({
  state: {
    user:null,
    url:"/api",
    rail:false,
    society:{},
    developped_by:{"name":"K SQUAD", "url":"https://ksquad.dev"},
    app_name:"K-SCHOOL",
    academicYears:[],
    faculties:[],
    departments:[],
    active:'0',
    levels:[],
    subjects:[],
    modules:[],

    profs:[],
    classes:[],
    books:[],
    cours_speciaux:[],
    chapitres:[],
    sections:[],
    domaines:[],
    disciplines:[],
    competences:[],
    themes:[],
    lecons:[],
    exercices:[],
    evaluations:[],
    epreuves_types:[],
    pointsEvaluations:[],
    palmares:[],
    anneesScolaires:[],
    bulletins:[],
    eleves:[],
    printing:false,
    TRIMESTRES:[
      {label:"1er Trimestre", value:1},
      {label:"2ème Trimestre", value:2},
      {label:"3ème Trimestre", value:3}
    ],
    TYPES_EVALUATIONS:[
      {label:"Interrogation", value:1},
      {label:"Examen", value:2}
    ]
  },
  computed: {
    accessToken() {
      return user.access
    },
  },
  getters: {
  },
  mutations: {
  },
  actions: {
  },
  modules: {
  }
})
