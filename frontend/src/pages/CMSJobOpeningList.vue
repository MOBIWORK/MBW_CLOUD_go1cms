<template>
	<LayoutHeader>
		<template #left-header>
			<ViewBreadcrumbs
				v-model="viewControls"
				routeName="cms_job_opening"
				titleBredcrumbs="CMS Job Opening"
			/>
		</template>
		<template #right-header>
			<Button
				v-if="canCreate"
				variant="solid"
				:label="__('Create')"
				@click="handleCreateClick"
			>
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
		doctype="CMS_JobOpening"
		:enableGroupSearch="true"
		:options="{
			allowedViews: ['list', 'group_by'],
		}"
		@View="(view) => {
			console.log('🚨 CMS_JobOpening received View event:', view, 'from ViewControls');
			activeView = view;
		}"
	/>
	<DataListView
		ref="dataListView"
		v-if="listData.data && rows.length"
		v-model="listData.data.page_length_count"
		v-model:list="listData"
		:doctype="'CMS_JobOpening'"
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
		@hideDelete =""
		@selectionsChanged="(selections) => viewControls.updateSelections(selections)"
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
		v-if="showInfoModalData"
		v-model="showInfoModalData"
		:editMode="editMode"
		:initialData="list_field_value"
		@success="handleJobOpeningCreated"
		@draft-deleted="handleDraftDeleted"
	></Modal>

	<QuickEntryModal v-model="showQuickEntryModal" doctype="CMS_JobOpening" />
</template>

<script setup>
import EmailIcon from "@/components/Icons/EmailIcon.vue";
import ViewBreadcrumbs from "@/components/ViewBreadcrumbs.vue";
import LayoutHeader from "@/components/LayoutHeader.vue";
import ViewControls from "@/components/ViewControls.vue";
import QuickEntryModal from "@/components/Modals/QuickEntryModal.vue";
import Modal from "@/components/Modals/JobOpeningSteps/JobOpeningMultiStepForm.vue";
import DataListView from "@/components/ListViews/CMS_JobOpening_ListView.vue";

import { Button } from "frappe-ui";
import { ref, computed, inject, watch } from "vue";
import { useRoute } from "vue-router";
import { usePermissionStore } from "@/stores/permission";
import { updateDocumentTitle } from '@/utils'
const { can } = usePermissionStore();

const canCreate = can("CMS_JobOpening", "create");

const breadcrumbs = [{ label: __("CMS Job Opening"), route: { name: "cms_job_opening" } }];

const dataListView = ref(null);
const listData = ref({});
const loadMore = ref(1);
const triggerResize = ref(1);
const updatedPageCount = ref(20);
const viewControls = ref(null);

// Khôi phục activeView từ route hoặc localStorage
const route = useRoute();
const getStorageKey = () => `viewState_CMS_JobOpening_cms_job_opening`;
const savedActiveView = localStorage.getItem(getStorageKey());

// Ưu tiên route trước, sau đó localStorage
const initialActiveView = route.params.viewType || savedActiveView || "list";
const activeView = ref(initialActiveView);

const user = inject("$user");
const showTask = ()=>{

}

// Watch activeView để lưu vào localStorage khi thay đổi
watch(activeView, (newValue) => {
	localStorage.setItem(getStorageKey(), newValue);
	console.log("🔄 CMS_JobOpening activeView changed:", newValue);
});

// Watch route để sync activeView với route params
watch(() => route.params.viewType, (newViewType) => {
	console.log("🔄 CMS_JobOpening route watcher triggered:", {
		newViewType,
		currentActiveView: activeView.value,
		routeParams: route.params
	});
	
	if (newViewType && newViewType !== activeView.value) {
		console.log("🔄 Route forcing activeView change:", activeView.value, "→", newViewType);
		activeView.value = newViewType;
	}
}, { immediate: true });

const pageLengthCount = computed(() => listData.value?.data?.page_length_count || 20);

const rows = computed(() => {
	if (!listData.value?.data?.data) return [];
	if (listData.value.data.view_type === "group_by") {
		if (!listData.value?.data.group_by_field?.name) return [];
		return getGroupedByRows(
			listData.value?.data.data,
			listData.value?.data.group_by_field,
			listData.value.data.columns,
		);
	}
	return listData.value?.data.data;
});

function getGroupedByRows(listRows, groupByField, columns) {
	let groupedRows = [];

	groupByField.options?.forEach((option) => {
		let filteredRows = [];

		if (!option) {
			filteredRows = listRows.filter((row) => !row[groupByField.name]);
		} else {
			filteredRows = listRows.filter((row) => row[groupByField.name] == option);
		}

		console.log(filteredRows);

		let groupDetail = {
			label: groupByField.label,
			group: option || __(" "),
			collapsed: false,
			rows: parseRows(filteredRows, columns),
		};

		console.log(groupDetail);
		groupedRows.push(groupDetail);
	});

	return groupedRows || listRows;
}

function parseRows(rows, columns = []) {
	return rows.map((jo) => {
		let _rows = {};
		listData.value?.data.rows.forEach((row) => {
			_rows[row] = jo[row];
		});
		return _rows;
	});
}

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
	// Check if there's existing draft (using CMS storage key)
	const existingDraft = sessionStorage.getItem('cms_job_opening_draft');
	
	console.log('🔍 handleCreateClick - existingDraft:', existingDraft);
	
	if (existingDraft) {
		// Show confirmation dialog
		const confirmed = window.confirm('Phát hiện bản nháp đã lưu. Bạn có muốn tiếp tục bản nháp không?\n\n- Chọn OK để tiếp tục với bản nháp.\n- Chọn Cancel để xóa bản nháp và tạo mới.');
		
		if (confirmed) {
			// Continue with existing draft
			console.log('✨ Continuing with existing draft');
			showInfoModalData.value = true;
			return;
		} else {
			// Delete draft if user chooses to start fresh
			console.log('🗑️ User choose to delete draft and start fresh');
			sessionStorage.removeItem('cms_job_opening_draft');
		}
	}
	
	// Show form directly - no choice modal needed
	console.log('✨ Showing job opening form');
	initializeListFieldValue();
	editMode.value = false;
	showInfoModalData.value = true;
};

const handleJobOpeningCreated = (data) => {
	console.log("✅ CMS Job Opening created successfully:", data);
	
	// Force reload list data
	if (listData.value && typeof listData.value.reload === 'function') {
		listData.value.reload();
		console.log("🔄 List data reloaded");
	} else {
		console.warn("❌ listData.reload() not available");
	}
	
	// Close modal
	showInfoModalData.value = false;
	
	// Clear any remaining session storage (double check)
	const beforeClear = sessionStorage.getItem('cms_job_opening_draft');
	console.log("📝 SessionStorage before clear:", beforeClear);
	sessionStorage.removeItem('cms_job_opening_draft');
	const afterClear = sessionStorage.getItem('cms_job_opening_draft');
	console.log("🗑️ SessionStorage after clear:", afterClear);
};

const handleDraftDeleted = () => {
	// When draft is deleted, just close modal (no choice modal needed)
	showInfoModalData.value = false;
};

const pageMeta = computed(() => {
	return {
		title: __("CMS Job Opening"),
		description: __('CMS Job Opening Management'),
	}
})

updateDocumentTitle(pageMeta)
</script> 