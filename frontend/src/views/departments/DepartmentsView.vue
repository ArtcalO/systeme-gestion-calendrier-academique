<script >
import { Plus,Search } from '@element-plus/icons-vue'
export default {
    data(){
        return {
            departments:this.$store.state.departments,
            isLoading:false,keyword:"",Plus,Search
        }
    },
    watch: {
     "$store.state.departments"(new_val){
        this.departments=new_val
     },
     "keyword"(new_val){
        this.departments = this.$store.state.departments.filter(x =>{
        return JSON.stringify(x).toLowerCase().includes(new_val.toLowerCase())
      })
     }
    },
    mounted(){
        this.fetchDepartments()
    },
    methods:{
        fetchDepartments(){
            this.isLoading=true
            axios.get('/academic/departments/')
            .then((res)=>{
                this.isLoading=false
                this.$store.state.departments=res.data.results
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
                <h4 class="font-weight-medium">Departements</h4>
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
            <el-table v-loading="isLoading" :data="departments" style="width: 100%">
                <el-table-column fixed label="Departement">
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
                <el-table-column fixed label="CODE" min-width="90">
                    <template #default="scope">
                        <div>
                            <span>
                                {{ 
                                    scope.row.code
                                }}
                            </span>
                        </div>
                    </template>
                </el-table-column>

                <el-table-column fixed label="Faculté" min-width="90">
                    <template #default="scope">
                        <div>
                            <span>
                                {{ 
                                    scope.row.faculty_name
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
