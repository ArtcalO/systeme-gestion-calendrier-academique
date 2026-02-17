<script>
import { Plus, Search } from '@element-plus/icons-vue'
export default{
	data(){
		return {
			keyword:""
		}
	}
}
</script>

<template>
	<div>
		<v-row align="center" class="my-2">
			<v-col>
				<h4 class="font-weight-medium">Dasboard</h4>
			</v-col>
			<v-col cols="auto">
				<el-button type="primary" :icon="Plus" @click="$router.push({ name: 'createClient' })"
					>Ajouter</el-button
				>
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
		</el-card>
	</div>
</template>

<style lang="scss" scoped></style>
