<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs" />
		</template>
		<template #right-header>
			<Button variant="solid" :label="__('Create')" @click="handleCreateClick">
				<template #prefix><FeatherIcon name="plus" class="h-4" /></template>
			</Button>
		</template>
	</LayoutHeader>
	<ViewControls
		ref="viewControls"
		v-model="listData"
		v-model:loadMore="loadMore"
		v-model:resizeColumn="triggerResize"
		v-model:updatedPageCount="updatedPageCount"
		doctype="ATS_Company"
		:enableGroupSearch="true"
	/>
	<DataListView
		ref="dataListView"
		v-if="listData.data && rows.length"
		v-model="listData.data.page_length_count"
		v-model:list="listData"
		:doctype="'ATS_Company'"
		:rows="rows"
		:columns="listData.data?.columns || []"
		:options="{
			showTooltip: false,
			resizeColumn: true,
			rowCount: listData.data?.row_count || 0,
			totalCount: listData.data?.total_count || 0,
		}"
		@showModal="showModal"
		@loadMore="() => loadMore++"
		@columnWidthUpdated="() => triggerResize++"
		@updatePageCount="(count) => (updatedPageCount = count)"
		@showTask="showTask"
		@applyFilter="(data) => viewControls.applyFilter(data)"
		@deleteRecord="listData.reload()"
	/>

	<div v-else-if="listData.data" class="flex h-full items-center justify-center">
		<div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500">
			<EmailIcon class="h-10 w-10" />
			<span>{{ __("No Data Found") }}</span>
			<Button :label="__('Create')" @click="handleCreateClick">
				<template #prefix><FeatherIcon name="plus" class="h-4" /></template>
			</Button>
		</div>
	</div>
	<Modal
		v-model="showInfoModalData"
		:list_field_value="list_field_value"
		:editMode="editMode"
		:doctype="'ATS_Company'"
		v-model:quickEntry="showQuickEntryModal"
		@updateList="listData.reload()"
	></Modal>

	<QuickEntryModal v-model="showQuickEntryModal" doctype="ATS_Company" />
</template>

<script setup>
import EmailIcon from "@/components/Icons/EmailIcon.vue";
import LayoutHeader from "@/components/LayoutHeader.vue";
import ViewControls from "@/components/ViewControls.vue";
import QuickEntryModal from "@/components/Modals/QuickEntryModal.vue";
import Modal from "@/components/Modals/ATS_Company_Modal.vue";
import DataListView from "@/components/ListViews/ATS_Company_ListView.vue";

import { Breadcrumbs, Button, createResource } from "frappe-ui";
import { ref, computed, onMounted, reactive } from "vue";
import { usePermissionStore } from "@/stores/permission";

const { can } = usePermissionStore();

// const canCreate = can("ATS_Company", "create");

// console.log(">>>>", canCreate);

const breadcrumbs = [{ label: __("Company"), route: { name: "Company" } }];

const dataListView = ref(null);
const listData = ref({});
const loadMore = ref(1);
const triggerResize = ref(1);
const updatedPageCount = ref(20);
const viewControls = ref(null);

const pageLengthCount = computed(() => listData.value?.data?.page_length_count || 20);

const rows = computed(() => {
	if (!listData.value?.data?.data) return [];
	return listData.value?.data.data;
});

const showInfoModalData = ref(false);
const editMode = ref(false);
const showQuickEntryModal = ref(false);

const list_field_value = ref({});

// Hàm khởi tạo `list_field_value` từ bản ghi mẫu
function initializeListFieldValue() {
	const sampleRow = rows.value?.[0] || {}; // Lấy bản ghi mẫu từ rows
	list_field_value.value = Object.keys(sampleRow).reduce((acc, key) => {
		acc[key] = ""; // Mặc định giá trị rỗng
		return acc;
	}, {});
}

async function showModal(name) {
	let t = rows.value?.find((row) => row.name === name);
	if (t) {
		list_field_value.value = { ...t };
	}
	editMode.value = true;
	showInfoModalData.value = true;
}

const handleCreateClick = () => {
	initializeListFieldValue();
	showInfoModalData.value = true;
	editMode.value = false;
};
</script>
