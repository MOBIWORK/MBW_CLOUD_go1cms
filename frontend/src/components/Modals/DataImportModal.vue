<template>
	<Dialog v-model="show" :options="dialogOptions">
		 <!-- #body slot bắt buộc để hiển thị phần nội dung -->
		 <template #body>
      <div class="max-w-3xl mx-auto p-6 bg-white rounded shadow-md">
    <h2 class="text-xl font-bold mb-4">
      {{ dataImportName ? `${documentType} Import` : 'New Data Import' }}
    </h2>

    <!-- Data Import Form -->
    <form v-if="!dataImportName" @submit.prevent="createDataImport" class="space-y-4">
      <input v-model="documentType" placeholder="Document Type" required class="border p-2 w-full">
      <select v-model="importType" class="border p-2 w-full">
        <option>Insert New Records</option>
        <option>Update Existing Records</option>
        <option>Upsert Records</option>
      </select>
      <label><input type="checkbox" v-model="dontSendEmail"> Don't Send Emails</label>
      <button type="submit" class="bg-blue-600 text-white px-4 py-2">Save</button>
    </form>

    <!-- Upload & Import Actions -->
    <div v-else>
      <button @click="downloadTemplate" class="bg-green-600 text-white px-4 py-2">Download Template</button>

      <input type="file" @change="handleFileChange" class="mt-4">
      <button @click="uploadFile" class="bg-purple-600 text-white px-4 py-2 mt-2">Upload File</button>

      <div v-if="fileUrl" class="mt-4 p-2 bg-gray-100 rounded">
        <a :href="fileUrl" target="_blank">{{ fileUrl }}</a>
        <button @click="clearFile" class="text-red-500 ml-4">Clear</button>
      </div>

      <button @click="previewFile" class="bg-gray-600 text-white px-4 py-2 mt-2">Reload File</button>

      <button @click="startImport" class="bg-indigo-600 text-white px-4 py-2 mt-4">Start Import</button>

      <div v-if="importLog.length" class="mt-4">
        <h3 class="font-semibold">Import Log</h3>
        <table class="w-full border mt-2">
          <thead>
            <tr class="bg-gray-200">
              <th class="border">Row</th>
              <th class="border">Status</th>
              <th class="border">Message</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in importLog" :key="log.row">
              <td class="border text-center">{{ log.row }}</td>
              <td class="border text-center" :class="log.status === 'Success' ? 'text-green-600' : 'text-red-600'">
                {{ log.status }}
              </td>
              <td class="border">{{ log.message }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <button v-if="importCompleted" @click="startImport" class="bg-black text-white px-4 py-2 mt-4">Retry Import</button>

      <div v-if="message" class="mt-4 p-2 rounded" :class="success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
        {{ message }}
      </div>
    </div>
  </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-3 p-4">
        <Button variant="ghost" @click="isOpen = false">Cancel</Button>
        <Button variant="primary" :loading="isLoading" @click="importData">Import</Button>
      </div>
    </template>
	</Dialog>
</template>

<script setup>
import OrganizationsIcon from "@/components/Icons/OrganizationsIcon.vue";
import { usersStore } from "@/stores/users";
import { call, FeatherIcon, createResource } from "frappe-ui";
import { ref, nextTick, watch, computed, h, onMounted,provide } from "vue";
import { useRouter } from "vue-router";
import { createToast } from "@/utils";
import { useQuickEntry } from "../../stores/quickEntry";
import { useFieldStore } from "../../stores/activeRecord";
const useField = useFieldStore();

const quickEntryDoctype = useQuickEntry();

const props = defineProps({
	open: Boolean,
	options: {
		type: Object,
		default: {
			redirect: true,
			detailMode: false,
			afterInsert: () => { },
		},
	},
	list_field_value: {
		type: Object,
		default: {},
	},
	listPermission: {
		type: Object,
		default: {},
	},
	editMode: {
		type: Boolean,
		default: false,
	},
	doctype: {
		type: String,
		default: "Data Import",
	},
	data: Object,
	doctypes: {
    type: Array,
    default: () => [],
  },
});
provide(
  'data',
  computed(() => ref({})),
)
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

const emit = defineEmits(["updateList",'close', 'uploaded']);

const loading = ref(false);
const title = ref(null);
const detailMode = ref(false);
const editMode = ref(false);
let _address = ref({});
const context = __("unit"); // Ngữ cảnh hiện tại
let _data = ref({
	name: "",
});
const navigateToImportDetail = (importId) => {
  router.push({
    name: "Data Import Detail",
    params: { importId: importId },
  });
};

const validateData = () => {
	return true;
};

const showAddressModal = ref(false);

let doc = ref({});
let oldValue = ref();


const dialogOptions = computed(() => {
	let title =__("Add Data Import") ;
	let size = "6xl";
	let actions = [
			{
				label: __("Create"),
				variant: "solid",
				onClick: () => (callInsertDoc()),
			},
		]

	return { title, size, actions };
});

const fields = computed(() => {
	let details = [
		{
			icon: OrganizationsIcon,
			name: "name",
			value: _data.value.name,
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
			createToast({
				title: __("Success"),
				text: __(`Successfully added ${context}`),
				icon: "check",
				iconClasses: "text-green-600",
			});
			emit("updateList",doc.name);
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
		
		} else {
			_data.value = {
				name: "",
			};
		}
	});

	editMode.value = editModeVal;
});


const showQuickEntryModal = defineModel("quickEntry");

function openQuickEntryModal() {
	showQuickEntryModal.value = true;
	nextTick(() => {
		show.value = false;
	});
}
const documentType = ref('')
const importType = ref('Insert New Records')
const dontSendEmail = ref(false)
const dataImportName = ref('')
const selectedFile = ref(null)
const fileUrl = ref('')
const importLog = ref([])
const importCompleted = ref(false)
const message = ref('')
const success = ref(false)

async function createDataImport() {
  const res = await fetch('/api/resource/Data Import', { method: 'POST', credentials: 'include',
    body: JSON.stringify({ doctype: 'Data Import', reference_doctype: documentType.value, import_type: importType.value, send_email: dontSendEmail.value ? 0 : 1 }),
    headers: { 'Content-Type': 'application/json' }})
  const data = await res.json()
  dataImportName.value = data.data.name
}

async function downloadTemplate() {
  window.open(`/api/method/frappe.core.doctype.data_import.data_import.download_template?doctype=${documentType.value}`, '_blank')
}

function handleFileChange(e) { selectedFile.value = e.target.files[0] }

async function uploadFile() {
  const fd = new FormData(); fd.append('file', selectedFile.value)
  const res = await fetch('/api/method/upload_file', { method: 'POST', credentials: 'include', body: fd })
  const data = await res.json()
  fileUrl.value = data.message.file_url
}

async function clearFile() {
  fileUrl.value = ''
  await fetch(`/api/resource/Data Import/${dataImportName.value}`, { method: 'PUT', credentials: 'include',
    body: JSON.stringify({ file_url: null }), headers: { 'Content-Type': 'application/json' }})
}

async function previewFile() {
  message.value = 'Preview loading...'
  // Implement API to load preview
}

async function startImport() {
  const res = await fetch('/api/method/frappe.core.doctype.data_import.data_import.start_import', {
    method: 'POST', credentials: 'include', body: JSON.stringify({ data_import: dataImportName.value }),
    headers: { 'Content-Type': 'application/json' }})
  const data = await res.json()
  importLog.value = data.message.logs
  importCompleted.value = true
  success.value = !data.message.failed
  message.value = data.message.failed ? 'Import completed with errors.' : 'Import successful!'
}
</script>
