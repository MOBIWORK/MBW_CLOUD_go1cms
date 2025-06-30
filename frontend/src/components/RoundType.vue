<script setup>
import { createResource, FormControl, call } from "frappe-ui";
import { computed, ref, watchEffect, watch } from "vue";
import Draggable from "vuedraggable";
import ColorPicker from "@/components/ColorPicker.vue";
import AddTypeModal from "./Modals/AddTypeModal.vue";
import { createToast } from "../utils";

const isModalOpen = ref(false);
const isEdit = ref(false);
const selectedRound = ref({});

// Fetch dữ liệu từ API Frappe
const rounds = createResource({
	url: "go1_cms.go1_cms.doctype.ats_round_type.ats_round_type.get_round_types",
	auto: true,
	transform: (data) => ({
		fixedStart: data.fixedStart,
		draggableRounds: data.draggableRounds,
		fixedEnd: data.fixedEnd,
	}),
});

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
	selectedRound.value = { ...round }; // Clone dữ liệu để tránh thay đổi trực tiếp
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
	};
	isEdit.value = false;
	isModalOpen.value = true;
};

// 🏆 **Hàm cập nhật vị trí khi kéo thả**
const updatePositions = async (event) => {
	const { oldIndex, newIndex } = event;

	if (oldIndex === newIndex) return;

	// Cập nhật vị trí mới trong `draggableRounds`
	draggableRounds.value.forEach((round, index) => {
		round.position = index + 1;
	});

	try {
		// Gửi danh sách vòng giữa lên API
		await call(
			"go1_cms.go1_cms.doctype.ats_round_type.ats_round_type.update_round_positions",
			{
				rounds_json: JSON.stringify(draggableRounds.value),
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
		// Tính toán vị trí mới (trước vòng cuối cùng)
		const newPosition = draggableRounds.value.length + 1;
		const lastRound = fixedEnd.value[0]; // Lấy vòng cuối cùng

		// Gửi API thêm vòng mới vào `draggableRounds`
		const newRound = await call("frappe.client.insert", {
			doc: {
				doctype: "ATS_Round_Type",
				round_type_name: selectedRound.value.round_type_name,
				color: selectedRound.value.color,
				position: newPosition,
			},
		});

		// Nếu thêm thành công, cập nhật vị trí của vòng cuối
		if (newRound.name && lastRound) {
			await call("frappe.client.set_value", {
				doctype: "ATS_Round_Type",
				name: lastRound.name,
				fieldname: "position",
				value: newPosition + 1, // Đẩy vòng cuối xuống sau vòng mới
			});
		}

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
		// Hiển thị lỗi nếu có
		createToast({
			title: error || __("Error adding round"),
			icon: "alert-circle",
			iconClasses: "text-red-600",
		});
	}
};

const saveEditedRound = async () => {
	try {
		const oldName = selectedRound.value.name; // Tên cũ
		const newName = selectedRound.value.round_type_name; // Tên mới
		const newColor = selectedRound.value.color; // Màu sắc mới

		// Nếu tên mới khác tên cũ thì cần rename trước
		if (oldName !== newName) {
			await call("frappe.client.rename_doc", {
				doctype: "ATS_Round_Type",
				old_name: oldName,
				new_name: newName,
			});
		}

		// Cập nhật dữ liệu sau khi đổi tên
		await call("frappe.client.set_value", {
			doctype: "ATS_Round_Type",
			name: newName,
			fieldname: {
				round_type_name: newName,
				color: newColor, // Cập nhật luôn màu sắc
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
			"go1_cms.go1_cms.doctype.ats_round_type.ats_round_type.delete_round",
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

<template>
	<div v-if="rounds.data" class="bg-white p-4 rounded-lg w-full shadow">
		<!-- Hiển thị vòng đầu tiên (KHÔNG KÉO THẢ) -->
		<div
			v-for="round in fixedStart"
			:key="round.name"
			class="flex items-center justify-between bg-gray-100 p-3 mb-2 border-l-4 shadow-md"
		>
			<div class="flex gap-2 items-center flex-1 ml-6 font-medium text-gray-700">
				<div class="h-3 w-3 rounded-full" :style="{ backgroundColor: round.color }"></div>
				<span>
					{{ round.round_type_name }}
				</span>
			</div>

			<button @click="editRound(round)" class="text-black hover:text-blue-700">
				<FeatherIcon class="h-4" name="edit" />
			</button>
		</div>

		<!-- Kéo thả các vòng giữa -->
		<Draggable
			v-model="draggableRounds"
			item-key="name"
			handle=".drag-handle"
			@end="updatePositions"
		>
			<template #item="{ element }">
				<div
					class="flex items-center justify-between bg-white p-3 mb-2 border-l-4 shadow-md"
				>
					<FeatherIcon class="h-4 drag-handle cursor-grab" name="list" />
					<div class="flex gap-2 items-center flex-1 ml-2 font-medium text-gray-700">
						<div class="h-3 w-3 rounded-full" :style="{ backgroundColor: element.color }"></div>
						<span>
							{{ element.round_type_name }}
						</span>
					</div>
					<div class="flex gap-2">
						<button @click="editRound(element)" class="text-black hover:text-blue-700">
							<FeatherIcon class="h-4" name="edit" />
						</button>
						<button
							v-if="!element.default"
							@click="deleteRound(element)"
							class="text-red-500 hover:text-red-700"
						>
							<FeatherIcon class="h-4" name="trash-2" />
						</button>
					</div>
				</div>
			</template>
		</Draggable>

		<!-- Nút thêm vòng mới -->
		<div
			@click="openAddModal"
			class="flex items-center justify-center bg-blue-100 p-3 mb-2 border-l-4 border-blue-500 shadow-md cursor-pointer hover:bg-blue-200"
		>
			<FeatherIcon class="h-4 text-blue-600" name="plus" />
			<span class="ml-2 text-blue-600 font-medium">Thêm vòng mới</span>
		</div>

		<!-- Hiển thị vòng cuối (KHÔNG KÉO THẢ) -->
		<div
			v-for="round in fixedEnd"
			:key="round.name"
			class="flex items-center justify-between bg-gray-100 p-3 mt-2 border-l-4 shadow-md"
		>
			<div class="flex gap-2 items-center flex-1 ml-6 font-medium text-gray-700">
				<div class="h-3 w-3 rounded-full" :style="{ backgroundColor: round.color }"></div>
				<span>
					{{ round.round_type_name }}
				</span>
			</div>
			<!-- Chỉ hiển thị nút XÓA nếu vòng không phải default -->

			<button @click="editRound(round)" class="text-black hover:text-blue-700">
				<FeatherIcon class="h-4" name="edit" />
			</button>
		</div>
	</div>

	<!-- Loading hoặc dữ liệu rỗng -->
	<p v-else class="text-center text-gray-500">Đang tải dữ liệu...</p>

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
			<FormControl
				:type="'text'"
				size="sm"
				variant="subtle"
				placeholder="Round Name"
				:label="__('Round Name')"
				v-model="selectedRound.round_type_name"
				required="true"
			/>
			<div class="flex flex-col gap-1 mt-2">
				<span class="block text-xs text-ink-gray-5">Color</span>
				<ColorPicker placeholder="Select Color" v-model="selectedRound.color" />
			</div>
		</template>
	</AddTypeModal>
</template>
