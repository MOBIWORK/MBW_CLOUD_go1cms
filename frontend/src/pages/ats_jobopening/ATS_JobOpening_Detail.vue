<template>
	<LayoutHeader>
		<template #left-header>
			<div class="flex items-center gap-2">

				<Button v-if="route.query.from === 'view'" :variant="'outline'" theme="gray" @click="backToView"
					class="mr-2">
					<template #icon>
						<FeatherIcon name="arrow-left" class="h-4 w-4" />
					</template>
					{{ __('Back to View') }}
				</Button>
				<Breadcrumbs :items="breadcrumbs">
					<template #prefix="{ item }">
						<Icon :icon="item.icon" class="mr-2 h-4" />
					</template>
				</Breadcrumbs>
			</div>

			<!-- <StatusDoctype
          :configDoc="configDoc"
          :doc="infoListData"
          :isDirty="isDirty"
        ></StatusDoctype> -->
		</template>
		<template #right-header>
			<!-- <Button
				:variant="'solid'"
				:ref_for="true"
				theme="gray"
				size="sm"
				:label="__('Update')"
				:loading="false"
				:loadingText="null"
				:disabled="false"
				:link="null"
				@click="() => updateInfo()"
			>
			</Button> -->
			<!-- <ActionDoctype
          doctype="xxx_yyy"
          :doc="infoListData"
          deleteRedirect="/yyys"
          createRedirect="/yyyNew"
          :onSave="updateInfo"
          :reloadDoc="() => getDataRecord.fetch()"
          v-model:configDoc="configDoc"
          v-model:isDirty="isDirty"
        ></ActionDoctype> -->
			<!-- <div class="flex items-center gap-2">
				<Button :variant="'outline'" theme="gray" @click="checkAndShowRevisions" :loading="checkingRevisions">
					<template #prefix>
						<FeatherIcon name="clock" class="h-4 w-4" />
					</template>
{{ __('View History') }}
</Button>

</div> -->
			<!-- <AssignTo v-model="assignedTo" :data="getDataRecord.data" doctype="ATS_JobOpening" /> -->
			<Dropdown :options="statusOptions('CMS_JobOpening', updateField, customStatuses)">
				<template #default="{ open }">
					<Button :label="getDataRecord.data?.status"
						:theme="getJOStatus(getDataRecord.data?.status)?.colorClass[2]" :class="generateClassObject(
							getJOStatus(getDataRecord.data?.status)?.colorClass,
						)
							">
						<template #prefix>
							<IndicatorIcon />
						</template>
						<template #suffix>
							<FeatherIcon :name="open ? 'chevron-up' : 'chevron-down'" class="h-4" />
						</template>
					</Button>
				</template>
			</Dropdown>
		</template>
	</LayoutHeader>
	<div class="flex h-full overflow-hidden">
		<Tabs as="div" v-model="tabIndex" :tabs="tabs">
			<template #tab-panel>
				<div v-if="tabs[tabIndex].name === 'Summary'" class="h-full flex flex-col px-3 sm:px-10">
					<div class="my-3 flex items-center justify-between text-lg font-medium sm:mt-2 ml-auto">
						<div class="flex gap-1">
							<Button :variant="'solid'" @click="showAIModal = true" class="">
								<template #prefix>
									<FeatherIcon name="cpu" class="h-3 w-3" />
								</template>
								{{ __('Generate By AI') }}
							</Button>
						</div>
					</div>
					<DataFields v-if="getDataRecord.data && getDataRecord.data.name" :doctype="'CMS_JobOpening'"
						:docname="getDataRecord.data.name" :data="getDataRecord.data" :incomingData="incomingData" />
				</div>

				<div v-else-if="tabs[tabIndex].name === 'Process_Recruit'" class="flex flex-col p-5 gap-4">
					<div class="flex justify-between">
						<span>
							{{ __("Process Recruit") }}
						</span>
						<!-- <Button
							:variant="'solid'"
							:ref_for="true"
							theme="gray"
							size="sm"
							@click="handleSaveRecruitmentRound"
						>
							{{ __("Save") }}
						</Button> -->
					</div>
					<ProcessRecruitTable v-if="roundTypes.length && recruitmentRounds" :modelValue="recruitmentRounds"
						:jobOpeningId="props.jobOpeningId" :roundTypes="roundTypes" :data="getDataRecord.data"
						@update:modelValue="handleProcessUpdate" />
				</div>
				<!-- Hiển thị component Activities khi tab là Activity, Comments hoặc Attachments -->
				<Activities v-else ref="activities" doctype="CMS_JobOpening" :tabs="tabs" v-model:reload="reload"
					v-model:tabIndex="tabIndex" v-model="getDataRecord" />
			</template>
		</Tabs>

		<Resizer class="flex flex-col justify-between border-l" side="right">
			<div class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
				v-if="getDataRecord.data && getDataRecord.data?.jo_public_title"
				@click="copyToClipboard(getDataRecord.data?.jo_public_title)">
				{{ __(getDataRecord.data?.jo_public_title) }}
			</div>

			<div v-if="sections.data" class="flex flex-1 flex-col justify-between overflow-hidden">
				<SidePanelLayout v-if="getDataRecord.data && getDataRecord.data.name" v-model="getDataRecord.data"
					:sections="sections.data" doctype="CMS_JobOpening" @update="updateField"
					@reload="sections.reload" />
			</div>
		</Resizer>
	</div>
	<AIModal v-if="showAIModal" v-model="showAIModal" :note="getDataRecord?.data"
		:jo_job_description=getDataRecord.data?.jo_job_description
		:jo_job_requirement=getDataRecord.data?.jo_job_requirement :jo_job_benefits=getDataRecord.data?.jo_job_benefits
		@after="(data) => useDataAI(data)" />

	<SidePanelModal v-if="showSidePanelModal" v-model="showSidePanelModal" doctype="CMS_JobOpening"
		@reload="() => fieldsLayout.reload()" />
</template>

<script setup>
import SidePanelModal from "@/components/Settings/SidePanelModal.vue";

import LayoutHeader from "@/components/LayoutHeader.vue";
import Resizer from "@/components/Resizer.vue";
import IndicatorIcon from "@/components/Icons/IndicatorIcon.vue";
import ActivityIcon from "@/components/Icons/ActivityIcon.vue";
import CommentIcon from "@/components/Icons/CommentIcon.vue";
import AttachmentIcon from "@/components/Icons/AttachmentIcon.vue";
import DocumentIcon from "@/components/Icons/DocumentIcon.vue";
import DetailsIcon from "@/components/Icons/DetailsIcon.vue";
import {
	call,
	FeatherIcon,
	createResource,
	Breadcrumbs,
	Button,
	Tabs,
	Dropdown,
	usePageMeta,
} from "frappe-ui";
import { ref, nextTick, watch, computed, reactive, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useActiveTabManager } from "@/composables/useActiveTabManager";
import Activities from "@/components/Activities/Activities.vue";
import {
	createToast,
	setupAssignees,
	setupCustomizations,
	copyToClipboard,
} from "@/utils";
import SidePanelLayout from "@/components/SidePanelLayout.vue";
import { statusesStore } from "@/stores/statuses";
import DataFields from "@/components/Activities/DataFields.vue";
import ProcessRecruitTable from "../../components/ProcessRecruitTable.vue";
import { getRandom } from "../../utils";
import { updateDocumentTitle } from '@/utils'
import AIModal from "@/components/Modals/AIModal.vue";


usePageMeta(() => {
	return {
		title: "Job Opening - Detail",
		emoji: "📋",
	};
});



const { statusOptions, getJOStatus } = statusesStore();
const customStatuses = ref([]);
const roundTypes = ref([]);
const recruitmentRounds = ref({
	fixedStart: [],
	draggableRounds: [],
	fixedEnd: [],
});

const isSyncingFromSidebar = ref(false);

const _data = ref({
	recruitment_process: [],
});

const props = defineProps({
	options: {
		type: Object,
		default: {
			redirect: true,
			detailMode: false,
			afterInsert: () => { },
		},
	},
	jobOpeningId: {
		type: String,
		required: true,
	},
});

const roundTypesWithColor = createResource({
	url: "go1_cms.go1_cms.doctype.ats_recruitment_process.ats_recruitment_process.get_round_types_with_color",
	auto: true,
	onSuccess: (data) => {
		console.log('🔍 Raw API response for roundTypes:', data);
		if (data && data.message) {
			// API trả về { message: { message: [...] } } nên cần parse đúng
			if (data.message.message && Array.isArray(data.message.message)) {
				roundTypes.value = data.message.message;
			} else if (Array.isArray(data.message)) {
				roundTypes.value = data.message;
			} else {
				roundTypes.value = [];
			}
		} else {
			roundTypes.value = [];
		}
		console.log('🎨 Processed roundTypes:', roundTypes.value);
	},
});

const convertRounds = (rounds = []) =>
	rounds.map((r) => ({
		name: r.name || getRandom(10),
		idx: r.position + 1,
		round_name: r.round_name,
		round_type: r.round_type,
		position: r.position,
		test_link: r.test_link,
		default: r.default,
		automation_rules: Array.isArray(r.triggers)
			? r.triggers.map((t) => ({
				...t,
				targets:
					typeof t.targets === "string"
						? t.targets
						: JSON.stringify(t.targets || []),
				name: t.name || getRandom(10),
				__isLocal: 1,
				owner: "Administrator",
			}))
			: [],
		__isLocal: 1,
	}));

// Hàm gọi API lấy danh sách vòng tuyển dụng của `ATS_Position`
const fetchJobOpeningRounds = async (name) => {
	try {
		const response = await call("go1_cms.api.get_job_opening_rounds", {
			job_opening: name,
		});

		if (response.success) {
			recruitmentRounds.value = {
				fixedStart: response.fixedStart,
				draggableRounds: response.draggableRounds,
				fixedEnd: response.fixedEnd,
			};
			_data.value.recruitment_process = [
				...convertRounds(response.fixedStart),
				...convertRounds(response.draggableRounds),
				...convertRounds(response.fixedEnd),
			];
			console.log("Job position rounds:", _data.value.recruitment_process);
		} else {
			console.error(response);
		}
	} catch (error) {
		console.error("Error fetching job position rounds:", error);
	}
};

const handleProcessUpdate = (data) => {
	console.log(data);

	_data.value.recruitment_process = [
		...convertRounds(data.fixedStart),
		...convertRounds(data.draggableRounds),
		...convertRounds(data.fixedEnd),
	];

	handleSaveRecruitmentRound();

	console.log("🔥 recruitment_process", _data.value.recruitment_process);
};

const handleSaveRecruitmentRound = async () => {
	try {
		console.log(_data.value.recruitment_process);
		const response = await call("go1_cms.api.save_job_opening_rounds", {
			job_opening: props.jobOpeningId,
			recruitment_process: _data.value.recruitment_process,
		});

		if (response.success) {
			createToast({
				title: __("Cập nhật thành công."),
				icon: "check",
				iconClasses: "text-green-800",
			});
			fetchJobOpeningRounds(props.jobOpeningId);
		} else {
			console.error(response);
		}
	} catch (error) {
		console.error("Error saving job position rounds:", error);
	}
};

const router = useRouter();
const route = useRoute();

const breadcrumbs = computed(() => {
	let items = [{ label: __("Job Opening"), route: { name: "job_opening" } }];

	//   if (route.query.view || route.query.viewType) {
	//     let view = getView(route.query.view, route.query.viewType, 'Sales Order')
	//     if (view) {
	//       items.push({
	//         label: __(view.label),
	//         icon: view.icon,
	//         route: {
	//           name: 'saleorders',
	//           params: { viewType: route.query.viewType },
	//           query: { view: route.query.view },
	//         },
	//       })
	//     }
	//   }

	items.push({
		label: getDataRecord.data?.jo_public_title || __(""),
		route: {
			name: "ats_job_opening_detail",
			params: { jobOpeningId: getDataRecord.data?.name },
		},
	});
	return items;
});

const showSidePanelModal = ref(false);
const showRevisionModal = ref(false);
const checkingRevisions = ref(false);
const listDataField = ref([]);
const detailMode = ref(false);
const listPermission = ref({});
const infoListData = reactive({});
const dataDetail = reactive({});
const oldValue = reactive({});
const loading = ref(false);
const showAIModal = ref(false);

// actions and status of doctype
const isDirty = ref(false);
const configDoc = ref();
const incomingData = ref({});

const assignedTo = ref([]);

const getDataRecord = createResource({
	url: "go1_cms.go1_cms.doctype.cms_jobopening.api.get_detail",
	params: { name: props.jobOpeningId },
	cache: ["getDataRecored", props.jobOpeningId],
	onSuccess: (data) => {
		isDirty.value = false;

		// for (const key in data) {
		// 	if (data.hasOwnProperty(key)) {
		// 		infoListData[key] = data[key];
		// 		dataDetail[key] = data[key];
		// 		oldValue[key] = data[key];
		// 	}
		// }
		setupAssignees(getDataRecord.data);
		setupCustomizations(getDataRecord, {
			doc: data,
			router,
			updateField,
			createToast,
			// deleteDoc: deleteSaleOrders,
			resource: { getDataRecord, sections },
			call,
		});
		assignedTo.value = data?._assignedTo || [];
	},
});

onMounted(() => {
	fetchJobOpeningRounds(props.jobOpeningId);
	if (getDataRecord.data) return;
	getDataRecord.fetch();
});

// Watch để theo dõi khi roundTypes thay đổi
watch(roundTypes, (newValue, oldValue) => {
	console.log('🔄 roundTypes changed from:', oldValue, 'to:', newValue);
}, { deep: true });

// const getcolumnsData = createResource({
// 	url: "mbw_ats.api.doc.get_column_doctype",
// 	params: {
// 		doctype: "ATS_JobOpening",
// 	},
// 	auto: true,
// 	onSuccess: async (data) => {
// 		listDataField.value = data;
// 	},
// });

async function callRenameDoc(oldName, newName) {
	try {
		const result = await call("frappe.client.rename_doc", {
			doctype: "CMS_JobOpening", // Doctype cần đổi tên
			old_name: oldName, // Tên cũ
			new_name: newName, // Tên mới
		});
		return result;
	} catch (error) {
		console.error("Error in callRenameDoc:", error);
		throw new Error("Failed to rename document. Please try again later.");
	}
}

const updateInfo = async () => {
	// Dữ liệu cũ và mới
	const nameChanged = props.jobOpeningId != String(infoListData.jo_id); // Kiểm tra nếu name thay đổi
	delete oldValue.name;
	delete infoListData.name;
	console.log(oldValue, infoListData);
	const otherFieldChanged = JSON.stringify(oldValue) !== JSON.stringify(infoListData); // Kiểm tra các trường khác có thay đổi không

	// Lấy các trường cần thiết từ `infoListData`
	const fieldsToUpdate = Object.keys(infoListData).reduce((acc, key) => {
		// Loại bỏ các trường hệ thống không cần thiết
		const excludedFields = [
			"creation",
			"modified",
			"owner",
			"docstatus",
			"_user_tags",
			"_comments",
			"_assign",
			"_liked_by",
			"name",
			"fields_meta",
			"idx",
			"modified_by",
		];
		if (!excludedFields.includes(key)) {
			acc[key] = infoListData[key]; // Thêm trường vào danh sách cần cập nhật
		}
		return acc;
	}, {});

	// Nếu không có thay đổi nào, thoát sớm
	if (!nameChanged && !otherFieldChanged) {
		createToast({
			title: __("Không có thay đổi nào."),
			icon: "info",
			iconClasses: "text-blue-600",
		});
		return;
	}

	// Đặt trạng thái loading
	loading.value = true;

	try {
		// Đổi tên nếu `nameChanged`
		let updatedName = props.jobOpeningId;
		if (nameChanged) {
			updatedName = await callRenameDoc(props.jobOpeningId, infoListData.jo_id); // Đổi tên document
		}

		// Cập nhật các trường khác nếu cần
		if (otherFieldChanged) {
			const updateJobOpening = createResource({
				url: "go1_cms.go1_cms.doctype.cms_job_opening.api.update_record",
				debounce: 500,
				params: {
					jobOpeningId: updatedName, // ID của bản ghi
					data: fieldsToUpdate, // Dữ liệu cần cập nhật
				},
				onSuccess: (response) => {
					createToast({
						title: __("Cập nhật thành công."),
						icon: "check",
						iconClasses: "text-green-800",
					});

					router.push({
						name: "ats_job_opening_detail",
						params: { jobOpeningId: updatedName },
					}); // Chuyển hướng về trang danh sách
					getDataRecord.update({ params: { name: updatedName } });
					getDataRecord.fetch(); // Reload lại dữ liệu sau khi cập nhật
				},
				onError: (err) => {
					createToast({
						title: __("Đã xảy ra lỗi."),
						text: err.message || __("Không thể cập nhật dữ liệu. Vui lòng thử lại."),
						icon: "x",
						iconClasses: "text-red-600",
					});
				},
			});

			// Gọi API cập nhật
			await updateJobOpening.fetch();
		}
	} catch (error) {
		// Xử lý lỗi
		createToast({
			title: __("Đã xảy ra lỗi."),
			text: error.message || __("Không thể cập nhật dữ liệu. Vui lòng thử lại."),
			icon: "x",
			iconClasses: "text-red-600",
		});
	} finally {
		// Tắt trạng thái loading
		loading.value = false;
	}
};

const dataTab = [
	{
		name: "Summary",
		label: __("Summary"),
		icon: DetailsIcon,
		// condition: () => listPermission.value?.data,
	},
];

const resumeTab = [

	{
		name: "Process_Recruit",
		label: __("Process Recruit"),
		icon: DocumentIcon,
		// condition: () => listPermission.value?.process_recruit,
	},
];

// KHoi taoj cac tab
const activitiesTabs = computed(() => {
	let tabOptions = [
		// {
		// 	name: "Data",
		// 	label: __("Data"),
		// 	icon: DetailsIcon,
		// },
		{
			name: "Activity",
			label: __("Activity"),
			icon: ActivityIcon,
		},
		{
			name: "Comments",
			label: __("Comments"),
			icon: CommentIcon,
		},
		{
			name: "Attachments",
			label: __("Attachments"),
			icon: AttachmentIcon,
		},
	];
	return tabOptions.filter((tab) => (tab.condition ? tab.condition() : true));
});

// Kết hợp activitiesTabs và additionalTabs thành một mảng duy nhất
const tabs = computed(() => {
	// Kết hợp cả các tab chính và bổ sung
	console.log(
		[...dataTab, ...resumeTab, ...activitiesTabs.value].filter((tab) =>
			tab.condition ? tab.condition() : true,
		),
	);
	return [...dataTab, ...resumeTab, ...activitiesTabs.value].filter((tab) =>
		tab.condition ? tab.condition() : true,
	);
});

const { tabIndex } = useActiveTabManager(tabs, "Summary");

watch(tabs, (value) => {
	if (value && route.params.tabName) {
		let index = value.findIndex(
			(tab) => tab.name.toLowerCase() === route.params.tabName.toLowerCase(),
		);
		if (index !== -1) {
			tabIndex.value = index;
		}
	}
});

const sections = createResource({
	url: "go1_cms.go1_cms.doctype.mbw_ats_fields_layout.mbw_ats_fields_layout.get_sidepanel_sections",
	cache: ["fieldsLayout", props.jobOpeningId],
	params: { doctype: "CMS_JobOpening" },
	auto: true,
});

function validateRequired(fieldname, value) {
	let meta = getDataRecord.data.fields_meta || {};
	if (meta[fieldname]?.reqd && !value) {
		createToast({
			title: __("Error Updating"),
			text: __("{0} is a required field", [meta[fieldname].label]),
			icon: "x",
			iconClasses: "text-red-600",
		});
		return true;
	}
	return false;
}

function updateFieldData(fieldname, value, callback) {
	value = Array.isArray(fieldname) ? "" : value;

	if (!Array.isArray(fieldname) && validateRequired(fieldname, value)) return;

	createResource({
		url: "frappe.client.set_value",
		params: {
			doctype: "CMS_JobOpening",
			name: props.jobOpeningId,
			fieldname,
			value,
		},
		auto: true,
		onSuccess: () => {
			getDataRecord.reload();

			createToast({
				title: __("Record updated"),
				icon: "check",
				iconClasses: "text-green-600",
			});
			callback?.();
		},
		onError: (err) => {
			createToast({
				title: __("Error updating Record"),
				text: __(err.messages?.[0]),
				icon: "x",
				iconClasses: "text-red-600",
			});
		},
	});
}

async function updateField(name, value, callback) {
	// Nếu là field jo_public_title → xử lý rename_doc
	isSyncingFromSidebar.value = true;
	if (name === "jo_public_title") {
		const oldName = getDataRecord.data.name;
		const newName = value;

		if (oldName === newName) return;

		try {
			await call("frappe.client.rename_doc", {
				doctype: "CMS_JobOpening",
				old_name: oldName,
				new_name: newName,
			});

			router.push({
				name: "ats_job_opening_detail",
				params: { jobOpeningId: newName },
			});
			getDataRecord.update({ params: { name: newName } });
			getDataRecord.reload(); // reload lại dữ liệu sau khi rename

			createToast({
				title: __("Document Renamed"),
				icon: "check",
				iconClasses: "text-green-600",
			});

			callback?.();
		} catch (error) {
			createToast({
				title: __("Error renaming document"),
				text: __(error.messages?.[0]),
				icon: "x",
				iconClasses: "text-red-600",
			});
		}
	} else {
		// Các field khác → dùng set_value
		updateFieldData(name, value, () => {
			getDataRecord.data[name] = value;
			callback?.();
		});
		// getDataRecord.fetch();
	}
	nextTick(() => {
		isSyncingFromSidebar.value = false;
	});
}
// onMounted(async () => {
// 	// await getListPermission("xxx_yyy")
// 	await fetchPermissions("ATS_JobOpening");
// });
// const fetchPermissions = async (doctype) => {
// 	const resource = await createResource({
// 		url: "go1_cms.api.permission.check_user_permissions", // Thay "your_app" bằng tên ứng dụng của bạn
// 		params: { doctype },
// 		auto: true,
// 		onSuccess(data) {
// 			listPermission.value = data?.permissions;
// 		},
// 	});
// 	resource.fetch();
// };
watch(
	() => route.params.id, // Theo dõi sự thay đổi của route params
	(newId, oldId) => {
		if (newId !== oldId) {
			fieldsLayout.fetch();
		}
	},
	{ immediate: true }, // Gọi ngay khi component được khởi tạo
);

//convert class dropdown
const generateClassObject = (colorClass) => {
	// Tạo một đối tượng từ mảng lớp CSS
	return colorClass?.reduce((acc, className) => {
		acc[className] = true;
		return acc;
	}, {});
};

function useDataAI(data) {
	// Gọi API fakeAIResource.fetch() để lấy dữ liệu từ API

	// getDataRecord.data.jo_job_description = data.jo_job_description;
	// getDataRecord.data.jo_job_requirement = data.jo_job_requirement;
	// getDataRecord.data.jo_job_benefits = data.jo_job_benefits;

	incomingData.value = {
		jo_job_description: data.jo_job_description,
		jo_job_requirement: data.jo_job_requirement,
		jo_job_benefits: data.jo_job_benefits,
	};

}

const checkAndShowRevisions = async () => {
	if (!getDataRecord.data?.name) {
		createToast({
			title: "Lỗi",
			text: "Dữ liệu chưa được tải.",
			icon: "x",
			iconClasses: "text-red-500",
		});
		return;
	}

	checkingRevisions.value = true;
	try {
		const response = await call("frappe.client.get_list", {
			doctype: "ATS_JobOpeningRevision",
			filters: { job_opening: getDataRecord.data.name },
			fields: ["name"],
			limit: 1,
		});

		if (!response || !response.length) {
			createToast({
				title: "Thông báo",
				text: "Không có lịch sử chỉnh sửa nào.",
				icon: "info",
				iconClasses: "text-blue-500",
			});
			return;
		}

		// Có revisions thì mở modal
		showRevisionModal.value = true;
	} catch (error) {
		createToast({
			title: "Lỗi",
			text: "Không thể kiểm tra lịch sử chỉnh sửa.",
			icon: "x",
			iconClasses: "text-red-500",
		});
	} finally {
		checkingRevisions.value = false;
	}
};

// const updateHiringCommittee = (data) => {
// 	// console.log(data);
// 	getDataRecord.reload();
// };
const pageMeta = computed(() => {
	return {
		title: getDataRecord.data?.jo_public_title || __('Job Opening'),
		description: __('Job Opening'),
	}
})

updateDocumentTitle(pageMeta)

const backToView = () => {
	router.push({
		name: "ats_job_opening_view",
		params: { jobOpeningId: props.jobOpeningId }
	});
};
</script>
