<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
    data(){
        return {
            academicYears:this.$store.state.academicYears,
            isLoading:false,keyword:"",Plus,Search
        }
    },
    watch: {
     "$store.state.academicYears"(new_val){
        this.academicYears=new_val
     },
     "keyword"(new_val){
        this.academicYears = this.$store.state.academicYears.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
     }
    },
    mounted(){
        this.fetchAcademicYears()
    },
    methods:{
        fetchAcademicYears(){
            this.isLoading=true
            axios.get('/academic/academic-years/')
            .then((res)=>{
                this.isLoading=false
                this.$store.state.academicYears=res.data.results
            })
            .catch((err)=>{
                this.isLoading=false
                console.log(err)
            })
        }
    }
}
</script>

<template>
    <div>
        <v-row align="center" class="my-2">
            <v-col>
                <h4 class="font-weight-medium">Annee Academique </h4>
            </v-col>
        </v-row>
        <el-card>
            <template #header>
                <div class="card-header d-xl-flex align-center justify-space-between">
                    <div></div>
                    <div class="d-md-flex align-center">
                        <div class="mr-sm-2 my-2 my-sm-0">
                            <el-input v-model="keyword" placeholder="Chercher" class="input-with-select w-100">
                                <template #append>
                                    <el-button type="primary" :icon="Search" />
                                </template>
                            </el-input>
                        </div>
                    </div>
                </div>
            </template>
            <el-table v-loading="isLoading" :data="academicYears" style="width: 100%">
                <el-table-column fixed label="Annee Academique" min-width="90">
                    <template #default="scope" >
                        <div>
                            <span>
                                {{ 
                                    scope.row.name
                                }}
                            </span>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column fixed label="Debut" min-width="90">
                    <template #default="scope">
                        <div>
                            <span>
                                {{ 
                                    scope.row.start_date
                                }}
                            </span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column fixed label="Fn" min-width="90">
                    <template #default="scope">
                        <div>
                            <span>
                                {{ 
                                    scope.row.end_date
                                }}
                            </span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column fixed label="Inscriptions" min-width="90">
                    <template #default="scope">
                        <div>
                            <span>
                                {{ 
                                    scope.row.is_enrollment_open?'En cours':'Terminé'
                                }}
                            </span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column fixed label="Nb Cours" min-width="90">
                    <template #default="scope">
                        <div>
                            <span>
                                {{ 
                                    scope.row.courses_count
                                }}
                            </span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column fixed label="Statut" min-width="90">
                    <template #default="scope">
                        <div>
                            <span>
                                {{ 
                                    scope.row.is_current?'Année en cours':'Terminée'
                                }}
                            </span>
                        </div>
                    </template>
                </el-table-column>
                
                		
            </el-table>
        </el-card>
    </div>
</template>

<style lang="scss" scoped></style>
