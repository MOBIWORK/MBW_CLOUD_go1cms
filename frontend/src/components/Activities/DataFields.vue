<template>
	<div class="my-3 flex items-center justify-between text-lg font-medium sm:mb-4 sm:mt-8">
		<div class="flex h-8 items-center text-xl font-semibold text-ink-gray-8">
			{{ __("Data") }}
			<Badge v-if="isDirty" class="ml-3" :label="'Not Saved'" theme="orange" />
		</div>
		<div class="flex gap-1">
			<Button v-if="!isMobileView" @click="showDataFieldsModal = true">
				<EditIcon class="h-4 w-4" />
			</Button>
			<Button
				label="Save"
				:disabled="!isDirty"
				variant="solid"
				:loading="data.save.loading"
				@click="saveChanges"
			/>
		</div>
	</div>
	<!-- <div
		v-if="data.get.loading"
		class="flex flex-1 flex-col items-center justify-center gap-3 text-xl font-medium text-gray-500"
	>
		<LoadingIndicator class="h-6 w-6" />
		<span>{{ __("Loading...") }}</span>
	</div> -->
	<div class="pb-8">
		<FieldLayout v-if="tabs.data" :tabs="tabs.data" :data="data.doc" :doctype="doctype" />
	</div>
	<DataFieldsModal
		v-if="showDataFieldsModal"
		v-model="showDataFieldsModal"
		:doctype="doctype"
		@reload="
			() => {
				tabs.reload();
				data.reload();
			}
		"
	/>
</template>

<script setup>
import EditIcon from "@/components/Icons/EditIcon.vue";
import DataFieldsModal from "@/components/Modals/DataFieldsModal.vue";
import FieldLayout from "@/components/FieldLayout/FieldLayout.vue";
import { Badge, createResource, createDocumentResource } from "frappe-ui";
import LoadingIndicator from "@/components/Icons/LoadingIndicator.vue";
import { createToast } from "@/utils";
import { usersStore } from "@/stores/users";
import { isMobileView } from "@/composables/settings";
import { onMounted, ref, watch, computed, toRaw } from "vue";


const props = defineProps({
	doctype: {
		type: String,
		required: true,
	},
	docname: {
		type: String,
		required: true,
	},
	data: {
		type: Object,
		default: () => ({}),
	},
	incomingData: {
		type: Object,
		default: () => ({}),
	},
});

// const manuallyEdited = ref(false);

console.log(props);

const { isManager } = usersStore();

const showDataFieldsModal = ref(false);

const isDirty = ref(false);

// Function để deep convert object/array thành plain object, loại bỏ hoàn toàn Vue reactivity
function toPlainObject(obj) {
	if (obj === null || obj === undefined || typeof obj !== 'object') {
		return obj;
	}
	
	if (Array.isArray(obj)) {
		return obj.map(item => toPlainObject(item));
	}
	
	// Convert object thành plain object
	const plain = {};
	const raw = toRaw(obj);
	
	for (const key in raw) {
		if (raw.hasOwnProperty(key)) {
			plain[key] = toPlainObject(raw[key]);
		}
	}
	
	return plain;
}

// Function để reset isDirty state sau khi save
function resetDirtyState() {
	isDirty.value = false;
}

const data = createDocumentResource({
	doctype: props.doctype,
	name: props.docname,
	auto: true,
	setValue: {
		onSuccess: () => {
			// Reset dirty state sau khi save thành công
			resetDirtyState();
			
			createToast({
				title: "Data Updated",
				icon: "check",
				iconClasses: "text-ink-green-3",
			});
			console.log(data);
		},
		onError: (err) => {
			createToast({
				title: "Error",
				text: err.messages[0],
				icon: "x",
				iconClasses: "text-red-600",
			});
		},
	},
});

const shouldReload = ref(false);



watch(
	() => props.data,
	async (newVal) => {
		if (!newVal) return;

		const localEdits = {};

		// Lưu lại field user đã sửa - sử dụng toPlainObject để loại bỏ hoàn toàn Vue reactivity
		if (data.originalDoc && data.doc) {
			const plainDoc = toPlainObject(data.doc);
			const plainOriginal = toPlainObject(data.originalDoc);
			
			for (const key in plainDoc) {
				if (JSON.stringify(plainDoc[key]) !== JSON.stringify(plainOriginal[key])) {
					localEdits[key] = plainDoc[key];
				}
			}
		}

		console.log("Saving user edits before reload:", localEdits);

		await data.reload(); // ✅ reload ngay lập tức
		console.log("Reloading...");

		// Gán lại những field user đã sửa
		for (const key in localEdits) {
			if (data.doc && data.doc.hasOwnProperty(key)) {
				data.doc[key] = localEdits[key];
			}
		}

		// Log changes for debugging
		if (Object.keys(localEdits).length > 0) {
			console.log("Restored user edits:", localEdits);
		}
	},
);

watch(
	() => props.incomingData,
	(newVal) => {
		if (!newVal) return;

		Object.assign(data.doc, newVal);
	},
);

// Tạo computed property để so sánh data.doc và data.originalDoc
// const isDirty = computed(() => {
// 	const rawDoc = toRaw(data.doc);
// 	const rawOriginal = toRaw(data.originalDoc);

// 	const cloneDoc = { ...rawDoc };
// 	const cloneOriginal = { ...rawOriginal };
// 	console.log(JSON.stringify(cloneDoc) !== JSON.stringify(cloneOriginal));

// 	return JSON.stringify(cloneDoc) !== JSON.stringify(cloneOriginal);
// });



// Watch để check isDirty - sử dụng toPlainObject để loại bỏ hoàn toàn Vue reactivity
watch(
	() => data.doc,
	(newVal) => {
		if (!newVal || !data.originalDoc) {
			isDirty.value = false;
			return;
		}

		// Convert thành plain object để loại bỏ hoàn toàn Vue reactivity
		const plainDoc = toPlainObject(newVal);
		const plainOriginal = toPlainObject(data.originalDoc);
		
		// So sánh bằng JSON.stringify cho nested objects/arrays
		let hasChanged = false;
		for (const key in plainDoc) {
			const currentStr = JSON.stringify(plainDoc[key]);
			const originalStr = JSON.stringify(plainOriginal[key]);
			
			if (currentStr !== originalStr) {
				hasChanged = true;
				break;
			}
		}
		
		// Debug log khi có thay đổi
		if (hasChanged !== isDirty.value) {
			console.log('isDirty changed from', isDirty.value, 'to', hasChanged);
			console.log('Plain doc sample:', {
				keys: Object.keys(plainDoc).slice(0, 5),
				plainDoc: plainDoc.can_full_name,
				plainOriginal: plainOriginal.can_full_name
			});
			
			// Log chi tiết field nào thay đổi
			const diff = {};
			for (const key in plainDoc) {
				const currentStr = JSON.stringify(plainDoc[key]);
				const originalStr = JSON.stringify(plainOriginal[key]);
				
				if (currentStr !== originalStr) {
					diff[key] = {
						old: plainOriginal[key],
						new: plainDoc[key],
					};
				}
			}
			
			if (Object.keys(diff).length > 0) {
				console.log("Fields changed:", diff);
			}
		}
		
		isDirty.value = hasChanged;
	},
	{ deep: true },
);

// watch(isDirty, (newVal) => {
//   console.log("isDirty changed:", newVal)
// })

// watch(() => data, (newVal) => {
//   console.log("newVal:", newVal)
// }, { deep: true })

const tabs = createResource({
	url: "go1_cms.go1_cms.doctype.mbw_ats_fields_layout.mbw_ats_fields_layout.get_fields_layout",
	cache: ["DataFields", props.doctype],
	params: { doctype: props.doctype, type: "Data Fields" },
	auto: true,
});

function saveChanges() {
	data.save.submit();
}

// Expose functions if needed
defineExpose({
	resetDirtyState,
	isDirty
});
</script>
