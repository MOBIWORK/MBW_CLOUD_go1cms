<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs" />
		</template>
		<template #right-header> </template>
	</LayoutHeader>

	<!-- Tabs -->
	<div class="p-5">
		<Tabs
			as="div"
			class="border rounded"
			v-model="activeTab"
			:tabs="tabs"
		>
			<template #tab-panel="{ tab }">
				<div class="p-5">
					<!-- Hiển thị component tương ứng với từng tab -->
					<ProcessRecruit v-if="tab.name === 'recruitment_process'" />
					<RoundType v-if="tab.name === 'round_type'" />
				</div>
			</template>
		</Tabs>
	</div>
</template>


<script setup>
import ProcessRecruit from "@/components/ProcessRecruit.vue";
import RoundType from "@/components/RoundType.vue";
import LayoutHeader from "@/components/LayoutHeader.vue";
import { createResource, FormControl, call, Breadcrumbs, Tabs } from "frappe-ui";
import { ref } from "vue";

const breadcrumbs = [{ label: __("Recruitment"), route: { name: "Process" } }];

// Danh sách Tabs
const tabs = [
	{
		label: __("Recruitment Process"),
		name: "recruitment_process",
	},
	{
		label: __("Round Type"),
		name: "round_type",
	},
];

// Tab hiện tại
const activeTab = ref("recruitment_process");
</script>
