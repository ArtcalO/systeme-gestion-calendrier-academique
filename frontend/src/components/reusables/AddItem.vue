<template>
  <el-dialog
    v-model="dialogVisible"
    title="Ajouter un element"
    top="2vh"
    max-width="340"
    width="320"
    heigth="auto"
  >
    <el-form label-position="top" label-width="100px" :model="truck">
      <el-row :gutter="20">
        <el-col :span="24">
          <el-switch
            v-model="is_service"
            class="mb-2"
            active-text="Service"
            inactive-text="Location"
          />
          <el-form-item label="Entrer la plque du tracteur" v-if="!is_service">
            <el-input v-model="keyword" name="item_designation" placeholder="Entrer la plaque du tracteur"  >
              <template #append>
                  <el-button @click="searchTruck" type="primary" :icon="Search" />
                </template>
            </el-input>
            <p v-if="!!truck">{{ formatTruck(truck) }}</p>
          </el-form-item>
          <el-form-item label="Nature de l'article ou service">
            <el-input v-model="item_designation" name="item_designation" />
          </el-form-item>
          <el-form-item label="Quantite">
            <el-input v-model="item_quantity" name="item_quantity" />
          </el-form-item>
          <el-form-item label="PU">
            <el-input v-model="item_price" name="item_price" />
          </el-form-item>
          <el-form-item label="PV HTVA (Fbu)">
            <el-input v-model="totAmount" name="totAmount" />
          </el-form-item>
        </el-col>
      </el-row>
      <br>
      <el-button :loading="isLoading" @click="validateItem" type="primary"
        >Valider</el-button
      >
    </el-form>
  </el-dialog>
</template>

<script >
import { Search } from '@element-plus/icons-vue'
export default{
  props:["tvaProps"],
  data(){
    return {
      keyword:"",
      truck:null,
      is_service:false,
      item_designation:"",
      item_quantity:1,
      item_price:0,
      item_ct:0,
      item_tl:0,
      item_price_nvat:0,
      vat:0,
      item_price_wvat:0,
      item_total_amount:0,
      dialogVisible:true,
      Search,
      isLoading:false,
    }
  },
  watch:{
    "totAmount":{
      deep:true,
      handler(new_val){
        if(new_val){
          this.item_total_amount=new_val
        }
      }
    }
  },
  methods: {
    imprimer() {
      print()
    },
    calcPrixHTVA(){
      return (parseFloat(this.item_quantity)*this.item_price)+this.item_ct
    },
    calcPrixTVA(){
      if(this.tvaProps=="1")
        return this.calcPrixHTVA()*18/100
      else
        return this.calcPrixHTVA()*0/100
    },
    calcTVAC(){
      return this.calcPrixHTVA()+this.calcPrixTVA()
    },
    calcTTC(){
      return this.calcTVAC()+this.item_tl
    },
    validateItem(){
      let data ={
        "truck":this.truck?this.truck.id:null,
        "item_designation":this.item_designation,
        "item_quantity":this.item_quantity,
        "item_price":this.item_price,
        "item_ct":this.item_ct,
        "item_tl":this.item_tl,
        "item_price_vat":this.item_price_vat,
        //prix HTVA = (pu*q)+tc
        "item_price_nvat":this.calcPrixHTVA(),
        //prix TVA = (HTVA*18)/100
        "vat":this.calcPrixTVA(),
        "is_service":this.is_service,
        "item_price_wvat":this.calcTVAC(),
        "item_total_amount":this.calcTTC(),
      }
      this.$emit("itemEmitted",data)
      this.$emit("close")
    },
    formatTruck(truck){
      this.item_designation=`${truck.modele}-${truck.plaque}`
      this.item_price = truck.prix
      return `${truck.plaque}-${truck.modele}`
    },
    searchTruck(){
      this.isLoading=true
      axios.get(`trucks/?plaque=${this.keyword}`)
      .then((res)=>{
        this.isLoading=false
         if(res.data.results.length == 1){
          this.truck = res.data.results[0]
        }
        if(res.data.results.length == 0){
          this.useNotifyError(`Le tracteur ayant le numero de plaque ${this.keyword} n'existe pas !`)
        }
      })
      .catch((err)=>{
        this.isLoading=false
        this.errorOrRefresh(err, this.createTruck)
      })
    },
  },
  computed:{
    totAmount(){
      let item_total_amount=this.item_price*parseFloat(this.item_quantity)
      return item_total_amount
    }
  }
}

</script>
<style scoped>
p{
  margin-bottom:0px;
}
</style>
