<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs" />
		</template>
		<template #right-header>
			<Button v-if="canCreate" variant="solid" :label="__('Create')" @click="handleCreateClick">
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
		doctype="ATS_Unit"
		:enableGroupSearch="true"
	/>
	<ListView
		class="h-full px-5"
		v-if="treeData?.length"
		:columns="treeColumns"
		:rows="treeData"
		:options="{
			selectable: false,
			showTooltip: true,
			resizeColumn: true,
		}"
		row-key="id"
	>
		<template #group-header="{ group }">
			<span class="text-base font-medium leading-6 text-ink-gray-9">
				{{ group.group }} ({{ group.rows.length }})
			</span>
		</template>
	</ListView>
	
	<div v-else class="flex h-full items-center justify-center">
		<div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500">
			<EmailIcon class="h-10 w-10" />
			<span>{{ __("No Data Found") }}</span>
			<Button :label="__('Create')" @click="handleCreateClick">
				<template #prefix><FeatherIcon name="plus" class="h-4" /></template>
			</Button>
		</div>
	</div>

	<Modal
		v-model="showModal"
		:list_field_value="list_field_value"
		:editMode="editMode"
		:listPermission="listPermission"
		v-model:quickEntry="showQuickEntryModal"
		@updateList="listData.reload()"
	></Modal>

	<QuickEntryModal v-model="showQuickEntryModal" doctype="ATS_Unit" />
	<ConfirmModal
		v-model="showConfirmModal"
		@confirm="() => deleteRecord(fieldStore.childTableField)"
	>
		<template #title>
			<div class="text-lg font-semibold flex justify-center">
				{{ __("Xác nhận xóa") }}
			</div>
		</template>
		<template #content>
			<span class="flex justify-center">
				{{ __("Bạn có chắc chắn muốn xóa bản ghi này không?") }}
			</span>
		</template>
	</ConfirmModal>
</template>

<script setup>
import EmailIcon from "@/components/Icons/EmailIcon.vue";
import LayoutHeader from "@/components/LayoutHeader.vue";
import ViewControls from "@/components/ViewControls.vue";
import QuickEntryModal from "@/components/Modals/QuickEntryModal.vue";
import Modal from "@/components/Modals/ATS_Unit_Modal.vue";
import { Breadcrumbs, Button, createResource } from "frappe-ui";
import ListView from "@/components/frappe-ui-custom/ListView/ListView.vue";
import { ref, computed, onMounted, reactive, watch } from "vue";
import { useFieldStore } from "../../stores/activeRecord";
import ConfirmModal from "@/components/Modals/ConfirmModal.vue";
import { createToast } from "@/utils";
import { usePermissionStore } from "@/stores/permission";

const { can } = usePermissionStore();

const canCreate = can("ATS_Unit", "create");

const breadcrumbs = [{ label: __("Unit"), route: { name: "Unit" } }];

const fieldStore = useFieldStore();
const showConfirmModal = ref(false);

watch(
	() => fieldStore.timestamp,
	() => {
		console.log("Fields updated");
		if (fieldStore.actionType === "edit") {
			showModal.value = true;
			showyyy(fieldStore.childTableField);
		} else if (fieldStore.actionType === "delete") {
			showConfirmModal.value = true;
		}
	},
);

const listData = ref({});
const loadMore = ref(1);
const triggerResize = ref(1);
const updatedPageCount = ref(20);
const viewControls = ref(null);
const listPermission = ref({});

const rows = computed(() => {
	if (!listData.value?.data?.data) return [];
	return listData.value?.data.data;
});

const defaultValue = { label: "Modal View", value: "1" };

const showModal = ref(false);
const editMode = ref(false);
const showQuickEntryModal = ref(false);
const list_field_value = ref({
	name: "",
	parent_ats_unit: "",
	unit_id: "",
	unit_name: "",
	company_id: "",
	unit_address: "",
	unit_head: "",
	unit_level: "",
	is_group: 1,
	cat_order: 0,
	cat_status: "Active",
	cat_color: "",
	cat_icon: "",
});

async function showyyy(name) {
	let t = rows.value?.find((row) => row.name === name);
	list_field_value.value = {
		name: t.name,
		parent_ats_unit: t.parent_ats_unit,
		unit_id: t.unit_id,
		unit_name: t.unit_name,
		company_id: t.company_id,
		unit_address: t.unit_address,
		unit_head: t.unit_head,
		unit_level: t.unit_level,
		is_group: 1,
		cat_order: t.cat_order,
		cat_status: t.cat_status,
		cat_color: t.cat_color,
		cat_icon: t.cat_icon,
	};
	editMode.value = true;
	showModal.value = true;
}

const handleCreateClick = () => {
	showModal.value = true;
	editMode.value = false;
};

const treeData = ref([]);
const treeColumns = ref([]);
const isFirstRun = ref(true);

function convertToTree(data, collapsed = true) {
	const lookup = {};
	const tree = [];

	// Tạo một bảng tra cứu để tham chiếu nhanh
	data.forEach((item) => {
		lookup[item.name] = {
			...item,
			children: [],
			collapsed: collapsed, // Sử dụng trạng thái để quyết định collapsed
		};
	});

	// Xây dựng cây
	data.forEach((item) => {
		if (item.parent_ats_unit) {
			if (lookup[item.parent_ats_unit]) {
				// Nếu tìm thấy node cha, thêm vào children của node cha
				lookup[item.parent_ats_unit].children.push(lookup[item.name]);
			} else {
				// Nếu không tìm thấy node cha, thêm node này vào cây như một node gốc
				tree.push(lookup[item.name]);
			}
		} else {
			// Nếu không có parent_ats_unit, thêm vào cây như một node gốc
			tree.push(lookup[item.name]);
		}
	});

	return tree;
}

watch(
	() => listData.value.data,
	(newValue, oldValue) => {
	console.log(newValue)
		if (newValue && newValue.data && newValue.data.length > 0) {
			// Kiểm tra nếu dữ liệu đã đầy đủ
			treeData.value = convertToTree(newValue.data, isFirstRun.value);
			treeColumns.value = newValue.columns;

			// Cập nhật trạng thái chỉ lần đầu chạy
			if (isFirstRun.value) {
				isFirstRun.value = false;
			}

			console.log("Tree Data Updated:", treeData.value);
		} else {
			treeData.value = [];
		}
	},
	{ immediate: true },
);

function deleteRecord(name) {
	createResource({
		url: "frappe.client.delete",
		params: {
			doctype: "ATS_Unit",
			name: name,
		},
		auto: true,
		onSuccess: () => {
			listData.value.reload();
			createToast({
				title: __("Xóa thành công"),
				icon: "check",
				iconClasses: "text-green-600",
			});
		},
		onError: (err) => {
			createToast({
				title: __("Có lỗi xảy ra "),
				text: __(err.messages?.[0]),
				icon: "x",
				iconClasses: "text-red-600",
			});
		},
	});
}
</script>
