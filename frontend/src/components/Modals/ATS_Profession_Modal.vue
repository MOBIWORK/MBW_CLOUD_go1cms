<template>
	<Dialog v-model="show" :options="dialogOptions">
		<template #body>
			<div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
				<div class="mb-5 flex items-center justify-between">
					<div>
						<h3 class="text-2xl font-semibold leading-6 text-gray-900">
							{{ __(dialogOptions.title) || __("Untitled") }}
						</h3>
					</div>
					<div class="flex items-center gap-1">
						<Button
							v-if="isManager() || detailMode"
							variant="ghost"
							class="w-7 !px-0"
							@click="detailMode ? (detailMode = false) : openQuickEntryModal()"
						>
							<EditIcon class="h-4 w-4" />
						</Button>
						<Button variant="ghost" class="w-7" @click="show = false">
							<FeatherIcon name="x" class="h-4 w-4" />
						</Button>
					</div>
				</div>
				<div>
					<div v-if="detailMode" class="flex flex-col gap-3.5">
						<div
							class="flex h-7 items-center gap-2 text-base text-gray-800"
							v-for="field in fields"
							:key="field.name"
						>
							<div class="grid w-7 place-content-center">
								<component :is="field.icon" />
							</div>
							<div>{{ field.value }}</div>
						</div>
					</div>
					<FieldLayout
						v-if="tabs.data"
						:tabs="tabs.data"
						:data="_data"
						:doctype="props.doctype"
					/>
				</div>
			</div>
			<div v-if="showActionButtons" class="px-4 pb-7 pt-4 sm:px-6">
				<div class="space-y-2 flex justify-end">
					<Button
						class="w-fit"
						v-for="action in dialogOptions.actions"
						:key="action.label"
						v-bind="action"
						:label="__(action.label)"
						:loading="loading"
					/>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import EditIcon from "@/components/Icons/EditIcon.vue";
import FieldLayout from "@/components/FieldLayout/FieldLayout.vue";
import OrganizationsIcon from "@/components/Icons/OrganizationsIcon.vue";
import { usersStore } from "@/stores/users";
import { call, FeatherIcon, createResource } from "frappe-ui";
import { ref, nextTick, watch, computed, h } from "vue";
import { useRouter } from "vue-router";
import { createToast } from "@/utils";
import { useQuickEntry } from "../../stores/quickEntry";
import { useFieldStore } from "../../stores/activeRecord";
import { usePermissionStore } from "@/stores/permission";

const useField = useFieldStore();

const quickEntryDoctype = useQuickEntry();

const props = defineProps({
	options: {
		type: Object,
		default: {
			redirect: true,
			detailMode: false,
			afterInsert: () => {},
		},
	},
	list_field_value: {
		type: Object,
		default: {},
	},
	editMode: {
		type: Boolean,
		default: false,
	},
	doctype: {
		type: String,
		default: "ATS_Profession",
	},
});

watch(
	() => quickEntryDoctype.timestamp,
	(newVal) => {
		if (quickEntryDoctype.doctype === props.doctype) {
			tabs.reload();
		}
	},
);

const { isManager } = usersStore();

const router = useRouter();
const show = defineModel();

const emit = defineEmits(["updateList"]);

const loading = ref(false);
const title = ref(null);
const detailMode = ref(false);
const editMode = ref(false);
let _address = ref({});
const context = __("profession"); // Ngữ cảnh hiện tại
let _data = ref({
    profession_id: "",
    profession_name: "",
    profession_description: "",
    unit_id: "",
    cat_status: "Active",
    cat_order: "",
    cat_color: "",
    cat_icon: "",
    name: "",
});

// xu ly perrmission
const { can } = usePermissionStore();

const canEdit = can(props.doctype, "write");
const showActionButtons = ref(false);
watch(
	() => props.editMode,
	(newVal) => {
		if ((newVal && canEdit) || !newVal) {
			showActionButtons.value = true;
		} else {
			showActionButtons.value = false;
		}
	}, 
	{ immediate: true },
);


let doc = ref({});
let oldValue = ref();

const validateData = () => {
	if (!_data.value.profession_name) {
		createToast({
			title: __("Error occurred"),
			text: __("Profession Name is required."),
			icon: "x",
			iconClasses: "text-red-600",
		});
		loading.value = false;
		return false;
	}
	if (!_data.value.profession_id) {
		createToast({
			title: __("Error occurred"),
			text: __("Profession ID is required."),
			icon: "x",
			iconClasses: "text-red-600",
		});
		loading.value = false;
		return false;
	}
	if (!_data.value.cat_status) {
		createToast({
			title: __("Error occurred"),
			text: __("Cat Status is required."),
			icon: "x",
			iconClasses: "text-red-600",
		});
		loading.value = false;
		return false;
	}
	return true;
};

async function updateData() {
	const old = oldValue.value;
	const newOrg = _data.value;

	const nameChanged = old.name !== newOrg.profession_name;
	delete old.name;
	delete newOrg.name;

	const otherFieldChanged = JSON.stringify(old) !== JSON.stringify(newOrg);
	const values = newOrg;

	if (!nameChanged && !otherFieldChanged) {
		show.value = false;
		return;
	}

	let name;
	loading.value = true;
	if (!validateData()) {
		return; // Dừng ngay tại đây nếu validate thất bại
	}
	if (nameChanged) {
		name = await callRenameDoc();
	}
	if (otherFieldChanged) {
		name = await callSetValue(values);
	}
	emit("updateList");
	handleDataUpdate({ name }, nameChanged);
}

async function callRenameDoc() {
	console.log(doc.value);
	try {
		const d = await call("frappe.client.rename_doc", {
			doctype: props.doctype,
			old_name: useField.childTableField,
			new_name: _data.value.profession_name,
		});
		loading.value = false;
		return d;
	} catch (error) {
		createToast({
			title: __("Error occurred"),
			text: __(error.messages?.[0]),
			icon: "x",
			iconClasses: "text-red-600",
		});
		loading.value = false;
		console.error("Error in callRenameDoc:", error);
		throw new Error("Failed to rename document. Please try again later.");
	}
}

async function callSetValue(values) {
	try {
		if (!validateData()) {
			return; // Dừng ngay tại đây nếu validate thất bại
		}
		// Hiển thị trạng thái loading
		loading.value = true;

		// Gọi API và chờ phản hồi
		const d = await call("frappe.client.set_value", {
			doctype: props.doctype,
			name: _data.value.profession_name,
			fieldname: values,
		});

		createToast({
			title: __("Success"),
			text: __(`Successfully updated ${context}`),
			icon: "check",
			iconClasses: "text-green-600",
		});

		// Trả về giá trị name từ phản hồi
		return d.name;
	} catch (error) {
		// Xử lý lỗi nếu có
		createToast({
			title: __("Error occurred"),
			text: __(error.messages?.[0] || __(`An error occurred while updating {context}`)),
			icon: "x",
			iconClasses: "text-red-600",
		});
		console.error("Error in callSetValue:", error);
		throw new Error("Failed to set value. Please try again later.");
	} finally {
		// Đảm bảo trạng thái loading được tắt dù có lỗi hay không
		loading.value = false;
	}
}

async function callInsertDoc() {
	try {
		if (!validateData()) {
			return; // Dừng ngay tại đây nếu validate thất bại
		}
		// Bắt đầu trạng thái loading
		loading.value = true;

		// Gọi API để chèn tài liệu mới
		const doc = await call("frappe.client.insert", {
			doc: {
				doctype: props.doctype,
				..._data.value,
			},
		});

		// Kiểm tra nếu tài liệu được tạo thành công
		if (doc.name) {
			handleDataUpdate(doc);
			createToast({
				title: __("Success"),
				text: __(`Successfully added ${context}`),
				icon: "check",
				iconClasses: "text-green-600",
			});
			emit("updateList");
		}
	} catch (error) {
		// Xử lý lỗi
		createToast({
			title: __(`Failed to create {context}`),
			text: __(error.messages?.[0]),
			icon: "x",
			iconClasses: "text-red-600",
		});
		console.error("Error in callInsertDoc:", error);
		throw new Error("Failed to insert document. Please try again later.");
	} finally {
		// Đảm bảo trạng thái loading được tắt
		loading.value = false;
	}
}

function handleDataUpdate(doc, renamed = false) {
	show.value = false;
	props.options.afterInsert && props.options.afterInsert(doc);
}

const dialogOptions = computed(() => {
	let title = !editMode.value ? "Add Profession" : "Edit Data";
	let size = "6xl";
	let actions = detailMode.value
		? []
		: [
				{
					label: editMode.value ? __("Save") : __("Create"),
					variant: "solid",
					onClick: () => (editMode.value ? updateData() : callInsertDoc()),
				},
			];

	return { title, size, actions };
});

const fields = computed(() => {
	let details = [
		{
			icon: OrganizationsIcon,
			name: "profession_id",
			value: _data.value.profession_id,
		},
	];

	return details.filter((field) => field.value);
});

const tabs = createResource({
	url: "go1_cms.go1_cms.doctype.mbw_ats_fields_layout.mbw_ats_fields_layout.get_fields_layout",
	cache: ["QuickEntry", props.doctype],
	params: { doctype: props.doctype, type: "Quick Entry" },
	auto: true,
});

const filteredSections = computed(() => {
	let allSections = sections.data || [];
	if (!allSections.length) return [];

	return allSections;
});

watch([() => show.value, () => props.editMode], ([showVal, editModeVal]) => {
	if (!showVal) return;

	nextTick(() => {
		oldValue.value = { ...props.list_field_value };
		if (editModeVal) {
			_data.value = { ...props.list_field_value };
		} else {
			//_data.value = doc.value;
			_data.value = {
				profession_id: "",
				profession_name: "",
				profession_description: "",
				unit_id: "",
				cat_status: "Active",
				cat_order: "",
				cat_color: "",
				cat_icon: "",
				name: "",
			};
		}
	});

	if (!show.value) {
		doc.value = {};
	}

	editMode.value = editModeVal;
});

const showQuickEntryModal = defineModel("quickEntry");

function openQuickEntryModal() {
	showQuickEntryModal.value = true;
	nextTick(() => {
		show.value = false;
	});
}
</script>