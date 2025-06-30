<template>
	<!-- Loading hoặc dữ liệu rỗng -->
	<ProcessRecruitRound
		v-if="rounds.data"
		:data="rounds.data"
		:round-types="roundTypes"
		@edit="editRound"
		@add="openAddModal"
		@delete="deleteRound"
		@reorder="updatePositions"
	/>
	<p v-else class="text-center text-gray-500">{{ __("Loading data") }}</p>

	<!-- Modal thêm vòng -->
	<AddTypeModal
		v-model="isModalOpen"
		v-model:edit="isEdit"
		@action="isEdit ? saveEditedRound() : addRoundToFrappe()"
	>
		<template #title>
			{{ isEdit ? __("Edit Round") : __("Add Round") }}
		</template>
		<template #content>
			<div class="flex flex-col gap-4">
				<!-- Tên vòng -->
				<FormControl
					type="text"
					size="sm"
					variant="subtle"
					placeholder="Round Name"
					:label="__('Round Name')"
					v-model="selectedRound.round_name"
					required
				/>

				<!-- Chọn kiểu vòng -->
				<Autocomplete
					v-model="selectedRoundType"
					:options="roundTypes"
					placeholder="Select Round Type"
					:filterable="true"
				>
					<template #prefix>
						<div
							v-if="selectedRoundType?.color"
							class="w-3 h-3 rounded-full mr-2"
							:style="{ backgroundColor: selectedRoundType.color }"
						></div>
					</template>
					<template #item-prefix="{ option }">
						<div class="flex items-center">
							<div
								class="w-3 h-3 rounded-full mr-2"
								:style="{ backgroundColor: option.color }"
							></div>
						</div>
					</template>
				</Autocomplete>

				<!-- Cấu hình Trigger -->
				<div class="mt-4 border-t pt-4 hidden">
					<div class="text-sm font-semibold mb-2">{{__('Automation Triggers')}}</div>

					<div v-if="selectedRound.triggers?.length">
						<div
							v-for="(trigger, index) in selectedRound.triggers"
							:key="index"
							class="bg-white p-3 rounded-md mb-2 border"
						>
							<FormControl
								type="select"
								:label="__('Trigger Event')"
								:options="triggerEventOptions"
								v-model="trigger.trigger_event"
								size="sm"
								class="form-control"
							/>

							<FormControl
								type="select"
								:label="__('Action Type')"
								:options="[
									'Send Email',
									'Create Task',
									// 'Update Field',
									// 'Assign Permission',
									// 'Create Document',
									'Send Notification',
									// 'Webhook',
								]"
								v-model="trigger.action_type"
								size="sm"
								class="form-control"
							/>

							<Autocomplete
								v-model="trigger.targets"
								:options="targetOptions"
								placeholder="Apply to Roles"
								:label="__('Apply to Roles')"
								size="sm"
								:hideSearch="true"
								:multiple="true"
								class="form-control"
							/>

							<div class="flex justify-between mt-2 text-sm">
								<label class="flex items-center gap-2">
									<Checkbox size="sm" v-model="trigger.enabled" />
									<span>{{ __("Enabled") }}</span>
								</label>
								<label class="flex items-center gap-2">
									<Checkbox size="sm" v-model="trigger.send_booking_email" />
									<span>{{ __("Send Booking Email") }}</span>
								</label>
								<button
									class="text-red-500 text-xs"
									@click="selectedRound.triggers.splice(index, 1)"
								>
									{{ __("Delete Trigger") }}
								</button>
							</div>
						</div>
					</div>

					<button
						class="mt-2 text-sm text-blue-600 hover:underline"
						@click="addEmptyTrigger()"
					>
						+ {{ __("Add Trigger") }}
					</button>
				</div>
			</div>
		</template>
	</AddTypeModal>
</template>

<script setup>
import { createResource, FormControl, call, Autocomplete, Checkbox } from "frappe-ui";
import { computed, ref, watchEffect, watch } from "vue";
import AddTypeModal from "./Modals/AddTypeModal.vue";
import { createToast, validateTriggers } from "../utils";
import ProcessRecruitRound from "./ProcessRecruitRound.vue";

const isModalOpen = ref(false);
const isEdit = ref(false);
const selectedRound = ref({});
const roundTypes = ref([]);

watch(
	() => isModalOpen.value,
	(newType) => {
		console.log(isModalOpen.value);
	},
);

const addEmptyTrigger = () => {
	selectedRound.value.triggers.push({
		trigger_event: "on_enter",
		action_type: "Send Email",
		targets: [], // dạng chuỗi, bạn có thể tách ra mảng ở backend
		// params: "{}",
		enabled: true,
		send_booking_email: false,
	});
};

const targetOptions = [
	{ label: "Applicant", value: "Applicant" },
	{ label: "Recruiter", value: "Recruiter" },
	{ label: "Interviewer", value: "Interviewer" },
	{ label: "HR Staff", value: "HR Staff" },
	{ label: "Hiring Manager", value: "Hiring Manager" },
];

const triggerEventOptions = [
	{ label: __("When candidate enters this stage"), value: "on_enter" },
	{ label: __("When candidate exits this stage"), value: "on_exit" },
	{ label: __("Scheduled check (daily/weekly)"), value: "scheduled" },
	{ label: __("When data in this stage is updated"), value: "on_update" },
	{ label: __("Create test for candidate"), value: "on_create_test" },
];

// Fetch dữ liệu từ API Frappe
const rounds = createResource({
	url: "go1_cms.go1_cms.doctype.ats_recruitment_process.ats_recruitment_process.get_recruitment_process",
	auto: true,
	transform: (data) => ({
		fixedStart: data.fixedStart,
		draggableRounds: data.draggableRounds,
		fixedEnd: data.fixedEnd,
	}),
});

const roundTypesWithColor = createResource({
	url: "go1_cms.go1_cms.doctype.ats_recruitment_process.ats_recruitment_process.get_round_types_with_color",
	auto: true,
	onSuccess: (data) => {
		console.log(data.message);
		if (data) {
			roundTypes.value = data.message;
		} else {
			roundTypes.value = [];
		}
	},
});

const selectedRoundType = computed({
	get() {
		return (
			roundTypes.value.find((option) => option.value === selectedRound.value.round_type) ||
			null
		);
	},
	set(option) {
		selectedRound.value.round_type = option?.value || ""; // Chỉ lưu value
		console.log(selectedRound.value);
	},
});

const getRoundColor = (roundType) => {
	const found = roundTypes.value.find((r) => r.value === roundType);
	return found ? found.color : "#ccc"; // Nếu không tìm thấy, trả về màu xám mặc định
};

// Gán dữ liệu trực tiếp vào biến
const fixedStart = ref([]);
const draggableRounds = ref([]);
const fixedEnd = ref([]);

// Cập nhật dữ liệu khi API trả về
watch(
	() => rounds.data,
	(newData) => {
		if (newData) {
			fixedStart.value = newData.fixedStart || [];
			draggableRounds.value = newData.draggableRounds || [];
			fixedEnd.value = newData.fixedEnd || [];
		}
		console.log("Dữ liệu API:", rounds.data); // Kiểm tra dữ liệu API
	},
	{ immediate: true },
);

// Hàm mở modal sửa vòng
const editRound = (round) => {
	const clone = { ...round };

	if (Array.isArray(clone.triggers)) {
		for (const t of clone.triggers) {
			try {
				t.targets = JSON.parse(t.targets || "[]");
			} catch {
				t.targets = [];
			}
		}
	}
	selectedRound.value = clone;
	console.log(selectedRound.value);
	isEdit.value = true;
	isModalOpen.value = true;
};

// Hàm mở modal để thêm vòng mới
const openAddModal = () => {
	const newPosition = rounds.data.length - 1; // Thêm vào trước phần tử cuối cùng
	selectedRound.value = {
		round_type_name: "",
		color: "gray",
		position: newPosition,
		triggers: [],
	};
	isEdit.value = false;
	isModalOpen.value = true;
};

// 🏆 **Hàm cập nhật vị trí khi kéo thả**
const updatePositions = async (event) => {
	console.log(event);
	const { oldIndex, newIndex } = event;

	if (oldIndex === newIndex) return;

	const roundsList = draggableRounds.value;

	// Cập nhật vị trí mới trong `draggableRounds`
	// draggableRounds.value.forEach((round, index) => {
	// 	round.position = index + 1;
	// });
	// ⚠️ Thay đổi thứ tự thủ công vì Vue không reactivity được array mutate sâu
	roundsList.splice(newIndex, 0, roundsList.splice(oldIndex, 1)[0]);
	// Cập nhật lại vị trí
	roundsList.forEach((round, index) => {
		round.position = index + 1;
	});
	try {
		// Gửi danh sách vòng giữa lên API
		await call(
			"go1_cms.go1_cms.doctype.ats_recruitment_process.ats_recruitment_process.update_round_positions",
			{
				rounds_json: JSON.stringify(roundsList),
			},
		);

		createToast({
			title: __("Updated Positions"),
			icon: "check",
			iconClasses: "text-green-600",
		});

		// Reload danh sách sau khi cập nhật
		rounds.reload();
	} catch (error) {
		createToast({
			title: error || __("Error updating positions"),
			icon: "alert-circle",
			iconClasses: "text-red-600",
		});
	}
};

// Hàm thêm vòng mới vào Frappe
const addRoundToFrappe = async () => {
	try {
		// Bước 1: Cập nhật vị trí của 2 vòng cuối trước khi thêm mới
		await call(
			"go1_cms.go1_cms.doctype.ats_recruitment_process.ats_recruitment_process.update_end_round_positions_before_insert",
		);

		// Bước 2: Tính toán vị trí mới (trước 2 vòng cuối)
		const newPosition = draggableRounds.value.length + 1;

		// 🔥 Bước 3: Convert triggers nếu có
		const rawTriggers = selectedRound.value.triggers || [];
		const triggers = rawTriggers.map((t) => ({
			...t,
			targets: JSON.stringify(t.targets || []),
			__isLocal: true,
		}));

		// 🔒 Optional: validate luôn trước khi gửi (re-use validateTriggers)
		const validation = validateTriggers(rawTriggers);
		if (!validation.valid) {
			createToast({
				title: validation.error,
				icon: "alert-circle",
				iconClasses: "text-red-600",
			});
			return;
		}

		// Bước 4: Gửi API thêm vòng mới
		const newRound = await call("frappe.client.insert", {
			doc: {
				doctype: "ATS_Recruitment_Process",
				round_name: selectedRound.value.round_name,
				round_type: selectedRound.value.round_type,
				position: newPosition,
				default: false,
				automation_rules: triggers, // ✅ Thêm trigger vào đây
			},
		});

		// Hiển thị thông báo
		createToast({
			title: __("Added Successfully"),
			icon: "check",
			iconClasses: "text-green-600",
		});

		// Refresh danh sách để cập nhật UI
		rounds.reload();
		isModalOpen.value = false;
	} catch (error) {
		createToast({
			title: error || __("Error adding round"),
			icon: "alert-circle",
			iconClasses: "text-red-600",
		});
	}
};

const saveEditedRound = async () => {
	try {
		const checkTrigger = validateTriggers(selectedRound.value.triggers);

		console.log(checkTrigger);
		if (!checkTrigger.valid) {
			createToast({
				title: checkTrigger.error,
				icon: "alert-circle",
				iconClasses: "text-red-600",
			});
			return;
		}
		console.log("d,mm");
		const oldName = selectedRound.value.name; // Tên cũ
		const newName = selectedRound.value.round_name; // Tên mới
		const newType = selectedRound.value.round_type; // Kiểu vòng mới

		// Nếu tên mới khác tên cũ thì cần rename trước
		if (oldName !== newName) {
			await call("frappe.client.rename_doc", {
				doctype: "ATS_Recruitment_Process",
				old_name: oldName,
				new_name: newName,
			});
		}

		// Chuyển đổi trigger.targets → JSON string trước khi gửi
		const triggers = selectedRound.value.triggers.map((t) => ({
			...t,
			targets: JSON.stringify(t.targets || []),
			__isLocal: true,
		}));

		console.log(triggers);

		// Cập nhật dữ liệu sau khi đổi tên
		await call("frappe.client.set_value", {
			doctype: "ATS_Recruitment_Process",
			name: newName,
			fieldname: {
				round_name: newName,
				round_type: newType, // Cập nhật luôn kiểu vòng nếu có
				automation_rules: triggers,
			},
		});

		// Hiển thị thông báo
		createToast({
			title: __("Updated Successfully"),
			icon: "check",
			iconClasses: "text-green-600",
		});

		// Refresh danh sách
		rounds.reload();
		isModalOpen.value = false;
	} catch (error) {
		// Hiển thị lỗi nếu có
		createToast({
			title: error || __("Error updating round"),
			icon: "alert-circle",
			iconClasses: "text-red-600",
		});
	}
};

const deleteRound = async (round) => {
	if (round.default) {
		createToast({
			title: __("This round cannot be deleted"),
			icon: "alert-circle",
			iconClasses: "text-yellow-600",
		});
		return;
	}

	try {
		// Gọi API xóa vòng và cập nhật vị trí
		const response = await call(
			"go1_cms.go1_cms.doctype.ats_recruitment_process.ats_recruitment_process.delete_round",
			{
				name: round.name,
			},
		);

		if (response.success) {
			createToast({
				title: __("Deleted Successfully"),
				icon: "check",
				iconClasses: "text-green-600",
			});
			rounds.reload();
		} else {
			createToast({
				title: response.message || __("Error deleting round"),
				icon: "alert-circle",
				iconClasses: "text-red-600",
			});
		}
	} catch (error) {
		createToast({
			title: error || __("Error deleting round"),
			icon: "alert-circle",
			iconClasses: "text-red-600",
		});
	}
};
</script>

<style scoped>
:deep(.form-control.prefix select) {
	padding-left: 2rem;
}

.form-control {
	margin-bottom: 12px;
}
</style>
