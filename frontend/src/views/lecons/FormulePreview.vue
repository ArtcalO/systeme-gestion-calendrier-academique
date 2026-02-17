<script >
import VuePdfEmbed from 'vue-pdf-embed'
export default {
  name: 'LivreDetails',
  components:{VuePdfEmbed},
  data() {
    return {
		cours:{},
		isLoading: true,
		page: null,
		pageCount: 1,
		showAllPages: true,
    };
  },
  watch: {
    showAllPages() {
      this.page = this.showAllPages ? null : 1
    },
  },
  beforeMount(){
  	this.getCours()
  },
  methods:{
  	getCours() {
		axios
			.get(`/formules/?lecon=${this.$route.params.id_lecon}`, this.headers)
			.then((res) => {
				this.cours = res.data.results[0]
			})
			.catch((err) => {
				this.displayErrorOrRefreshToken(err, this.getCours);
			})
	},
	handleDocumentRender() {
      this.isLoading = false
      this.pageCount = this.$refs.pdfRef.pageCount
    },
  }
};
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">PDF</h4>
			</v-col>
		</v-row>
		<el-card>
			<div class="app-header">
			    <template v-if="isLoading">
			      Loading...
			    </template>

			    <template v-else>
			      <span v-if="showAllPages">
			        {{ pageCount }} page(s)
			      </span>

			      <span v-else>
			        <button :disabled="page <= 1" @click="page--">❮</button>

			        {{ page }} / {{ pageCount }}

			        <button :disabled="page >= pageCount" @click="page++">❯</button>
			      </span>

			      <label class="right">
			        <input v-model="showAllPages" type="checkbox">

			        Show all pages
			      </label>
			    </template>
			  </div>

			  <div class="app-content">
			    <vue-pdf-embed
			      ref="pdfRef"
			      :source="cours.pdf"
			      :page="page"
			      @rendered="handleDocumentRender"
			    />
			</div>
		</el-card>
	</div>
</template>
<style lang="css" scoped>
body {
  margin: 0;
  padding: 0;
  background-color: #ccc;
}

.vue-pdf-embed > div {
  margin-bottom: 8px;
  box-shadow: 0 2px 8px 4px rgba(0, 0, 0, 0.1);
}

.app-header {
  padding: 16px;
  box-shadow: 0 2px 8px 4px rgba(0, 0, 0, 0.1);
  background-color: #555;
  color: #ddd;
}

.app-content {
  padding: 24px 16px;
  background-color: #ccc;
}

.right {
  float: right;
}
</style>
