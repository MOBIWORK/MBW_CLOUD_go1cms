<template>
	<ListView
		:class="$attrs.class"
		:columns="columns"
		:rows="rows"
		:options="{
			// ...(props.valueType === '1'
			// 	? { onRowClick: (row) => emit('showyyy', row.name) }
			// 	: {
			// 			getRowRoute: (row) => ({
			// 				name: 'ats_institution',
			// 				params: { yyyId: row.name },
			// 			}),
			// 		}),
			selectable: options.selectable,
			showTooltip: options.showTooltip,
			resizeColumn: options.resizeColumn,
		}"
		row-key="name"
	>
		<ListHeader class="sm:mx-5 mx-3" @columnWidthUpdated="emit('columnWidthUpdated')">
			<ListHeaderItem
				v-for="column in columns"
				:key="column.key"
				:item="column"
				@columnWidthUpdated="emit('columnWidthUpdated', column)"
			>
				<Button
					v-if="column.key == '_liked_by'"
					variant="ghosted"
					class="!h-4"
					@click="() => emit('applyLikeFilter')"
				>
					<HeartIcon class="h-4 w-4" />
				</Button>
			</ListHeaderItem>
		</ListHeader>

		<ListRows :rows="rows" v-slot="{ idx, column, item, row }" class="relative">
			<div v-if="column.key === 'company_id'">
				<Tooltip :text="item">
					<div
						class="flex items-center gap-2 truncate text-base cursor-pointer"
						@click="
							(event) => {
								fieldStore.childTableField = row.name;
								fieldStore.actionType = 'edit';
								emit('showModal', row.name);
							}
						"
					>
						<div v-if="item" class="truncate">
							{{ item }}
						</div>
					</div>
				</Tooltip>
			</div>
			<div v-else-if="column.key === 'company_name'">
				<Tooltip :text="item">
					<div
						class="flex items-center gap-2 truncate text-base cursor-pointer"
						@click="
							(event) => {
								fieldStore.childTableField = row.name;
								fieldStore.actionType = 'edit';
								emit('showModal', row.name);
							}
						"
					>
						<div v-if="item" class="truncate">
							{{ item }}
						</div>
					</div>
				</Tooltip>
			</div>
			<div v-else-if="column.key === 'cat_status'">
				<Tooltip :text="item">
					<div v-if="item == 'Active'" class="cursor-pointer">
						<Badge
							:variant="'subtle'"
							:theme="catStatusColor[item]"
							size="md"
							:label="__('Active')"
							@click="
								(event) =>
									emit('applyFilter', {
										event,
										idx,
										column,
										item,
										firstColumn: columns[0],
									})
							"
						/>
					</div>
					<div v-if="item == 'Inactive'" class="cursor-pointer">
						<Badge
							:variant="'subtle'"
							:theme="catStatusColor[item]"
							size="md"
							:label="__('Inactive')"
							@click="
								(event) =>
									emit('applyFilter', {
										event,
										idx,
										column,
										item,
										firstColumn: columns[0],
									})
							"
						/>
					</div>
				</Tooltip>
			</div>
			<ListRowItem v-else :item="item" class="">
				<template #prefix> </template>
				<template #default="{ label }">
					<Tooltip :text="label">
						<div class="truncate text-base">
							{{ label }}
						</div>
					</Tooltip>
				</template>
			</ListRowItem>
		</ListRows>
		<ListSelectBanner>
			<template #actions="{ selections, unselectAll }">
				<Dropdown :options="listBulkActionsRef.bulkActions(selections, unselectAll)">
					<Button icon="more-horizontal" variant="ghost" />
				</Dropdown>
			</template>
		</ListSelectBanner>
	</ListView>

	<ListFooter
		v-if="pageLengthCount"
		class="border-t sm:px-5 px-3 py-2"
		v-model="pageLengthCount"
		:options="{
			rowCount: options.rowCount,
			totalCount: options.totalCount,
		}"
		@loadMore="emit('loadMore')"
	/>
	<ListBulkActions
		ref="listBulkActionsRef"
		v-model="list"
		:doctype="props.doctype"
		:options="{
			hideAssign: true,
		}"
	/>
	<ConfirmModal
		v-model="showConfirmModal"
		@confirm="() => deleteRecord(fieldStore.childTableField)"
	>
		<template #title>
			<div class="text-lg font-semibold flex justify-center">
				{{ __("Confirm Deletion") }}
			</div>
		</template>
		<template #content>
			<span class="flex justify-center">
				{{ __("Are you sure you want to delete this record?") }}
			</span>
		</template>
	</ConfirmModal>
</template>

<script setup>
import HeartIcon from "@/components/Icons/HeartIcon.vue";
import ListBulkActions from "@/components/ListBulkActions.vue";
import ListRows from "@/components/ListViews/ListRows.vue";
import {
	Avatar,
	ListView,
	ListHeader,
	ListHeaderItem,
	ListRowItem,
	ListFooter,
	Dropdown,
	Tooltip,
	Badge,
	createResource,
} from "frappe-ui";
import { catStatusColor } from "../../utils";
import { ref, computed, watch, onMounted, reactive } from "vue";
import { useRoute } from "vue-router";
import { useFieldStore } from "../../stores/activeRecord";
import { createToast } from "@/utils";
import ConfirmModal from "../Modals/ConfirmModal.vue";
import ListSelectBanner from "../frappe-ui-custom/ListViewCustom/ListSelectBanner.vue";

const fieldStore = useFieldStore();
const showConfirmModal = ref(false);

watch(
	() => fieldStore.timestamp,
	() => {
		console.log("Fields updated");
		if (fieldStore.actionType === "edit") {
			emit("showModal", fieldStore.childTableField);
		} else if (fieldStore.actionType === "delete") {
			showConfirmModal.value = true;
		}
	},
);

const props = defineProps({
	rows: {
		type: Array,
		required: true,
	},
	columns: {
		type: Array,
		required: true,
	},
	options: {
		type: Object,
		default: () => ({
			selectable: true,
			showTooltip: true,
			resizeColumn: false,
			totalCount: 0,
			rowCount: 0,
		}),
	},
	doctype: {
		type: String,
		default: "ATS_Company",
	},
});

const emit = defineEmits([
	"loadMore",
	"updatePageCount",
	"columnWidthUpdated",
	"showModal",
	"applyFilter",
	"applyLikeFilter",
	"likeDoc",
	"deleteRecord",
]);

const route = useRoute();

const pageLengthCount = defineModel();
const list = defineModel("list");

watch(pageLengthCount, (val, old_value) => {
	if (val === old_value) return;
	emit("updatePageCount", val);
});

const listBulkActionsRef = ref(null);

defineExpose({
	customListActions: computed(() => listBulkActionsRef.value?.customListActions),
});
let errorShown = ref(false);

const deleteDoc = createResource({
	url: "frappe.client.delete",
	params: {},
	auto: false,
	onSuccess: () => {
		emit("deleteRecord");
		errorShown.value = false;
		createToast({
			title: __("Deleted Successfully"),
			icon: "check",
			iconClasses: "text-green-600",
		});
	},
	onError: (err) => {
		if (!errorShown.value) {
			errorShown.value = true; // Đánh dấu lỗi đã hiển thị
			console.log("Error occurred in deleteDoc:", err);
			createToast({
				title: __("Error occurred"),
				text: __(err.messages?.[0]) || __("An unexpected error occurred."),
				icon: "x",
				iconClasses: "text-red-600",
			});
			// Reset trạng thái sau 20ms
			setTimeout(() => {
				errorShown.value = false;
			}, 20);
		}
	},
});

function deleteRecord(name) {
	console.log("delete");
	deleteDoc.update({
		params: {
			doctype: props.doctype,
			name: name,
		},
	});
	deleteDoc.fetch();
}
</script>
