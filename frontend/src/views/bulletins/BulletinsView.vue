<script >
import { Plus,Search,Check,Delete } from '@element-plus/icons-vue'
export default {
	data(){
		return {
			bulletins:[],
			classes:[],
			eleves:[],
			active_classe:null,
			annee_scolaire:null,
			filters:{
				annee_scolaire:this.$store.state.user.annee_encours,
				classe:null,
			},
			recto:true,
			
		}
	},
	watch: {
	 "$store.state.bulletins"(new_val){
	 	this.bulletins=new_val
	 	this.eleves = this.bulletins.bulletins
	 },
	 "filters.classe"(new_val){
	 	if(new_val)
	 		this.filters.classe=new_val
	 },	 
	 "keyword"(new_val){
	 	this.bulletins = this.$store.state.bulletins.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
	 }
	},
	beforeMount(){
		this.fetchClasses()
	},
	mounted(){
		this.fetchAnneesScolaires()

		
	},
	methods:{
		checkClasse(){
			if(this.active_user_is('titulaire')){
				console.log(this.$store.state.user.id_classe_titulaire)
				this.filters.classe=this.$store.state.user.id_classe_titulaire
			}
			if(this.active_user_is('admin')){
				this.filters.classe=this.classes[0]
			}
			this.fetchBulletins()
		},
		fetchClasses(){
			axios.get('classes/')
			.then((res)=>{
				this.classes=res.data.results
				this.checkClasse()
			})
			.catch((err)=>{
				this.isLoading=false
				this.errorOrRefresh(error, this.fetchClasses)
			})
		},
		generateBuletins(){
			if(this.active_user_is("titulaire"))
				this.filters.classe = this.$store.state.user.id_classe_titulaire
			axios.post('bulletins/generer/', this.filters)
			.then(()=>{
				this.useNotifySuccess("Opération effectué avec succes !")
				this.$router.push("/bulletins")
			})
			.catch((error)=>{
				console.log(error)
				this.errorOrRefresh(error, this.generateBuletins)
			})
		},
		imprimer(){
			this.$store.state.printing=true
			setTimeout(()=>{
				print()
				this.$store.state.printing=false
			},1000)
			
		},
		fetchBulletins(){
			if(this.filters.classe)
				axios.get(`bulletins/?annee_scolaire=${this.filters.annee_scolaire}&classe=${this.filters.classe}`)
				.then((res)=>{
					this.$store.state.bulletins=res.data.results[0]
					this.active_classe = res.data.results[0].classe
					this.annee_scolaire = res.data.results[0].annee_scolaire
					this.eleves=this.$store.state.bulletins.bulletins
				})
				.catch((err)=>{
					this.errorOrRefresh(err, this.fetchBulletins)
				})
			else
				this.checkClasse()

		},
		half(x){
			return x/2;
		},
		add(x,y){
			return parseFloat(x+y).toFixed(2);
		},
		year_total(w_1,e_1,w_2,e_2,w_3,e_3){
			if(w_1!=null && e_1!=null && w_2!=null && e_2!=null && w_3!=null && e_3 !=null){
				return parseFloat(w_1+e_1+w_2+e_2+w_3+e_3).toFixed(2)
			}else{
				return ""
			}
		},
		checkNullablility(x){
			if(x!=null){
				return x
			}else{
				return ""
			}
		},
		checkBeforeAdd(x,y){
			if(x!=null && y!=null)
				return this.add(x,y)
			return ""
		},
	}
}
</script>

<template>
	<div>
		<v-row class="my-2 non-printable">
			<v-col>
				<h4>Bulettins</h4>
			</v-col>
			<v-col>
				<el-button type="primary" @click="imprimer" >Imprimer</el-button>
			</v-col>
			<v-col>
				<el-input v-model="keyword" placeholder="Chercher" class="input-with-select w-100">
					<template #append>
						<el-button type="primary" :icon="Search" />
					</template>
				</el-input>
			</v-col>
		</v-row>
		<el-card class="non-printble">
			<template #header class="non-printable" >
				<div class="card-header d-xl-flex align-center justify-space-between non-printable">
					<div class="d-md-flex non-printable ">
						<div class="mr-sm-2 my-2 my-sm-0 non-printable">
							<el-form-item class="non-printable">
								<el-col :span="5" v-if="active_user_is('titulaire')" >
					        		<el-form-item label="Classes">
										<el-select filterable v-model="filters.classe" placeholder="Classes" class="w-100">
											<el-option
												v-for="item in classes"
												:key="item.id"
												:label="item.nom"
												:value="item.id"
											/>
										</el-select>
									</el-form-item>
								</el-col>
								<el-col :span="1">
								</el-col>
								<el-col :span="7">
					        		<el-form-item label="Année Scolaire">
										<el-select filterable v-model="filters.annee_scolaire" placeholder="Année scolaire" class="w-100">
											<el-option
												v-for="item in $store.state.anneesScolaires"
												:key="item.id"
												:label="item.debut.split('-')[0]+'-'+item.fin.split('-')[0]"
												:value="item.id"
											/>
										</el-select>
									</el-form-item>
								</el-col>
								<el-col :span="1">
								</el-col>				      
						      <el-col :span="2">
						        <el-button type="primary" @click="fetchBulletins">Filtrer</el-button>
						      </el-col>
						      <el-col :span="1">
								</el-col>
						       <el-col :span="4">
						        <el-button
						        	type="success"
						        	@click="generateBuletins"
						        	v-if="active_user_is('titulaire')"
						        >Générer Bultetins</el-button>
						      </el-col>
							  <el-col :span="2">
						        <el-switch
									v-model="recto"
									size="large"
									active-text="Recto"
									inactive-text="Verso"
								/>
						      </el-col>
							</el-form-item>
						</div>
					</div>
				</div>
			</template>
		</el-card>
		<div v-if="recto" class="bulletins">
			<table class="single-bulletin" v-for="eleve in eleves"  :key="eleve.id" >
				<div class="m-title">
					<p >{{eleve?.eleve.full_name}}</p>
				</div>
				<tbody>
					<tr style="border:0px">
						<td colspan="3" style="border:0px">
							<table style="text-align:center;border-collapse: collapse;">
								<tbody>
									<tr class="header-title">
										<td colspan="5">MAXIMA</td>
										<td colspan="4" >1èr TRIM</td>
										<td colspan="4" >2ème TRIM</td>
										<td colspan="4" >3ème TRIM</td>
										<td colspan="3" >TOT. ANNUELS</td>
									</tr>
									<tr>
										<td class="b-m-color">Cours</td>
										<td class="b-m-color">TJ</td>
										<td class="b-m-color">EX</td>
										<td class="b-m-color">TOT</td>
										<td class="b-m-color">Competences</td>
										<td class="b-s-color">TJ</td>
										<td class="b-s-color">EX</td>
										<td class="b-s-color">TOT</td>
										<td class="b-s-color">Appreciations</td>
										<td class="b-s-color">TJ</td>
										<td class="b-s-color">EX</td>
										<td class="b-s-color">TOT</td>
										<td class="b-s-color">Appreciations</td>
										<td class="b-s-color">TJ</td>
										<td class="b-s-color">EX</td>
										<td class="b-s-color">TOT</td>
										<td class="b-s-color">Appreciations</td>
										<td class="b-m-color">MAX</td>
										<td class="b-m-color">TOTAL</td>
										<td class="b-m-color">%</td>
									</tr>					
									<tr v-for="points in eleve.points"  :key="points.id"  >
										<td class="b-m-color" style="width:250px">{{points.discipline.nom}}</td>
										<td class="b-m-color"><strong>{{points.discipline.maxima}}</strong></td>
										<td class="b-m-color"><strong>{{points.discipline.maxima}}</strong></td>
										<td class="b-m-color"><strong>{{add(points.discipline.maxima,points.discipline.maxima)}}</strong></td>
										<td  style="margin: 0;padding: 0;min-width:200px" class="b-m-color competences">
												<table style="border: none; width: 100%;margin: 0;padding: 0" >
													<tr v-for="competence in points.discipline.competences">
														<td style="border: none;">{{competence.competences}}</td>
													</tr>
												</table>
										</td>
										<td
											class="b-s-color"
										>{{checkNullablility(points.test_1_trim)}}
										</td>
										<td
											class="b-s-color"
										>{{checkNullablility(points.exam_1_trim)}}
										</td>
										<td
											class="b-s-color"
										>{{checkBeforeAdd(points.test_1_trim,points.exam_1_trim)}}
											<span class="null-title"@click="" >Voir litiges</span>
										</td>
										<td class="b-s-color" style="min-width: 150px;">
											{{ points.appreciations_1_trim }}
										</td>
										<td
											class="b-s-color"
										>{{checkNullablility(points.test_2_trim)}}
										</td>
										<td
											class="b-s-color"
										>{{checkNullablility(points.exam_2_trim)}}
										</td>
										<td
											class="b-s-color"
										>{{checkBeforeAdd(points.test_2_trim,points.exam_2_trim)}}
										</td>
										<td class="b-s-color" style="min-width: 150px;">
											{{ points.appreciations_2_trim }}
										</td>
										<td
											class="b-s-color"
										>{{checkNullablility(points.test_3_trim)}}
											<span class="null-title" @click="">Voir litiges</span>
										</td>
										<td
											class="b-s-color"
										>{{checkNullablility(points.exam_3_trim)}}
										</td>
										<td
											class="b-s-color"
										>{{checkBeforeAdd(points.test_3_trim,points.exam_3_trim)}}
										</td>
										<td class="b-s-color" style="min-width: 150px;">
											{{ points.appreciations_3_trim }}
										</td>
										<td class="b-m-color" >{{points.discipline.maxima*3}}</td>
										<td class="b-m-color">
											{{year_total(
													points.test_1_term,
													points.exam_1_term,
													points.test_2_term,
													points.exam_2_term,
													points.test_3_term,
													points.exam_3_term
											)}}
										</td>
										<td class="b-m-color"></td>
									</tr>
									<tr>
										<td class="b-m-color"><strong>RELIGION</strong></td>
										<td class="b-m-color" v-for="i in 4"></td>
										<td class="b-s-color" v-for="i in 13"></td>
										<td class="b-m-color" v-for="i in 2"></td>
									</tr>
									<tr style="border-top:1px solid black; margin-top:2px;">
										<td><strong>TOTAUX</strong></td>
										<td class="b-m-color" v-for="i in 4"></td>
										<td class="b-s-color" v-for="i in 13"></td>
										<td class="b-m-color" v-for="i in 2"></td>
									</tr>
									<tr>
										<td><strong>POURCENTAGE</strong></td>
										<td class="b-m-color" v-for="i in 4"></td>
										<td class="b-s-color" v-for="i in 13"></td>
										<td class="b-m-color" v-for="i in 2"></td>
									</tr>
									
									<tr>
										<td rowspan="2"><strong>SIGNATURES</strong></td>
										<td colspan="3">Parents</td>
										<td colspan="5"></td>
										<td colspan="5"></td>
										<td colspan="6"></td>
									</tr>
									<tr>
										<td colspan="3">Titulaire</td>
										<td colspan="5"></td>
										<td colspan="5"></td>
										<td colspan="6"></td>
									</tr>
								</tbody>
							</table>
						</td>
					</tr>
				</tbody>
			</table>
		</div>
		<div v-else style="overflow-x: scroll;" >
			<div class="verso-bulletin" v-for="eleve in eleves"  :key="eleve.id" >
				<div class="verso-2-outline-border" >
					<div class="verso-2-container">
						<div class="verso-2-header">
							<div class="verso-2-title">
								<div>THE GROWING TREE ACADEMY</div>
								<div>NOM & PRENOM : {{eleve.eleve.full_name}}</div>
							</div>
							<img class="verso-2-logo" src="../../assets/gta.webp">
							<div class="verso-2-title">
								<div>Bulettins {{ active_classe?.nom}} </div>
								<div>A/S
									{{annee_scolaire?annee_scolaire.debut.split("-")[0]:'-'}} /
									{{annee_scolaire?annee_scolaire.fin.split("-")[0]:'-'}}
								</div>
							</div>
						</div>
						<div class="verso-2-conseil-classe" >
							<table>
								<thead>
									<th colspan="2">CONSEIL DE CLASSE</th>
								</thead>
								<tbody>
									<tr>
										<td>1èr TRIMESTRE</td>
										<td>{{ eleve.points[0].conseil_1_trim }}</td>
									</tr>
									<tr>
										<td>2ème TRIMESTRE</td>
										<td>{{ eleve.points[0].conseil_2_trim }}</td>
									</tr>
									<tr>
										<td>3ème TRIMESTRE</td>
										<td>{{ eleve.points[0].conseil_3_trim }}</td>
									</tr>
								</tbody>
							</table>
						</div>
						<div class="verso-2-annual-decision" >
							<table>
								<thead>
									<th colspan="2">DECISION ANNUELLE</th>
								</thead>
								<tbody>
									<tr>
										<td></td>
									</tr>
								</tbody>
							</table>
						</div>
						<div class="verso-2-signatures">
							<div class="verso-2-signature">Signature Professeur</div>
							<div class="verso-2-signature">Signature Direction</div>
						</div>
					</div>
				</div>
				<div class="verso-outline-border" >
					<div class="verso-container">
						<div class="verso-header">
							<div class="verso-title">THE GROWING TREE ACADEMY</div>
							<img class="verso-logo" src="../../assets/gta.webp">
						</div>
						<div class="verso-bulletin-title">
							BULLETIN SCOLAIRE
						</div>
						<div class="verso-student-info">
							<div class="verso-info-row">
								<div class="verso-info-label">Nom et Prénom:</div>
								<div class="verso-info-value">{{eleve.eleve.full_name}}</div>
							</div>
							<div class="verso-info-row">
								<div class="verso-info-label">Année Scolaire:</div>
								<div class="verso-info-value">
									{{annee_scolaire?annee_scolaire.debut.split("-")[0]:'-'}} /
									{{annee_scolaire?annee_scolaire.fin.split("-")[0]:'-'}}
								</div>
							</div>
							<div class="verso-info-row">
								<div class="verso-info-label">Classe:</div>
								<div class="verso-info-value">{{ active_classe?.nom}}</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style lang="css" scoped>
	.b-m-color{
		background-color: #c4dfb1
	}
	.b-s-color{
		background-color: #E1EED9
	}
	.bulletins{
		overflow-x: scroll;
		width: 100%;
	}
	.header-bultettins{
		display:flex;
		justify-content:center;
		margin-bottom:30px;
	}
	.header-title>td{
		font-weight:bold;
		background-color: #FFE499;
	}
	.m-title{
		font-size:14px;
		margin-bottom: 2px;
		padding: 15px;
		text-align: center;
	}
	.single-bulletin table{
		display:flex;
		flex-direction:column;
		justify-content:center;
	}

	.single-bulletin th,td{
		padding:5px;
		min-width:37px;
		width:auto;
		font-size:14px;
	}
	.competences{
		width: 200px
	}

	.null {
		position: relative;
	}
	.null-title {
		position: absolute;
		bottom: 90%;
		left: -70%;
		/*transform: translateX(-50%);*/
		padding: 5px;
		width: 100px;
		border: 1px solid grey;
		color: white;
		border-radius: 5px;
		display: none;
		background: rebeccapurple;
		cursor: pointer;
	}
	.null:hover .null-title {
		display: block;
	}
	.deliberation{
		display: flex;
		justify-content: center;
		flex-direction: row;
	}
	select{
		margin-right: 10px;
	}
	.verso-bulletin{
             display: flex;
             justify-content: space-between;
			 width: 100%;
        }
        .verso-outline-border{
            border: 2px solid #538134;
            width: 19cm;
            height: 27.5cm;
            padding: 10px;
        }
        .verso-container {
            width: 18.3cm;
            height: 26.8cm;
            padding: 20px;
            box-sizing: border-box;
            border: 2px solid #C2D734;
        }
        .verso-header {
            margin-top:16rem;
            text-align: center;
            margin-bottom: 30px;
        }
        .verso-title {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 20px;
            color: #538134 ;
        }
        .verso-logo {
            margin: 20px auto;
            width: 300px;
            height: 300px;
            background-color: #f0f0f0; /* Couleur de fond temporaire pour le logo */
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #C2D734;
        }
        .verso-bulletin-title{
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-top:5rem;
            font-weight: bold;
            text-decoration: underline;
        }
        .verso-student-info {
            margin: 30px 0;
            padding: 15px;
            border: 1px solid #C2D734;
            background-color: #538134;
        }
        .verso-info-row {
            display: flex;
            margin-bottom: 10px;
        }
        .verso-info-label {
            font-weight: bold;
            width: 150px;
        }
        .verso-info-value {
            flex-grow: 1;
        }

        /*Verso*/

        .verso-2-outline-border{
            border: 2px solid #538134;
			width: 19cm;
            height: 27.5cm;
            padding: 10px;
        }
        .verso-2-container {
			width: 18.3cm;
            height: 26.8cm;
            padding: 20px;
            box-sizing: border-box;
            border: 2px solid #C2D734;
        }

        .verso-2-header{
            display: flex;
            margin-top: 2rem;
        }
        .verso-2-logo {
            margin: 20px auto;
            width: 80px;
            height: 80px;
            background-color: #f0f0f0; /* Couleur de fond temporaire pour le logo */
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid #C2D734;
        }
        .verso-2-title{
            display: flex;
			font-weight: bold;
            flex-direction: column;
            justify-content: space-around;
        }
        .verso-2-conseil-classe table{
            margin-top: 6rem;
            width: 100%;
        }
        .verso-2-conseil-classe table, th, td{
            border: 1px solid black;border-collapse: collapse;
        }
        .verso-2-conseil-classe th{
           background-color: #538134;
		   text-align: center;
        }
        .verso-2-conseil-classe td, th{
           height: 60px;
        }
        .verso-2-conseil-classe td:first-child{
           width: 150px;
        }

        .verso-2-annual-decision table{
            margin-top: 6rem;
            width: 100%;
        }
        .verso-2-annual-decision table, th, td{
            border: 1px solid black;border-collapse: collapse;
        }
        .verso-2-annual-decision th{
           background-color: #C2D734;
        }
        .verso-2-annual-decision th{
           height: 60px;
		   text-align: center;
        }
        .verso-2-annual-decision td{
           height: 100px;
        }

        .verso-2-signatures {
            display: flex;
            justify-content: space-between;
            margin-top: 5rem;
        }
        
        .verso-2-signature {
            text-align: center;
            width: 45%;
            padding-top: 50px;
            border-top: 1px solid #333;
        }
	@media print {
		
		@page {
			size: A3 landscape;
			margin: 1cm; /* Optional: adjust margins as needed */
			
		}
		.el-card{
			display: none !important;
		}
		body {
			transform: scale(1); /* Ensures proper scaling */
			width: 100%;
		}
		table {
			page-break-inside: avoid;
		}
		
		.single-bulletin{
			background-color: white;
			display: block !important;
			visibility: visible !important;
			position: static !important;
		}
		.bulletins table.single-bulletin:first-child {
			padding-top: 0 !important;
		}
		.header-bultettins,.non-printable, .el-card__header,.m-title{
			display:none !important;
		
		/* Optional: Hide elements you don't want to print */
		}
		*{
			-webkit-print-color-adjust: exact !important;
			color-adjust : exact !important;
		}
		
	}

</style>
