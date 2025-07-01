<template>
	<LayoutHeader>
		<template #left-header>
			<Breadcrumbs :items="breadcrumbs"> </Breadcrumbs>
		</template>
		<template #right-header>
			<div class="relative">
				<Dropdown :options="defaultActions" @click.stop>
					<template v-slot="{ open }">
						<Button variant="solid" class="flex items-center gap-1">
							<template #prefix>
								<FeatherIcon name="plus" class="h-4 w-4" />
							</template>
							<span>{{ __("Create") }}</span>
							<template #suffix>
								<FeatherIcon :name="open ? 'chevron-up' : 'chevron-down'" class="h-4 w-4" />
							</template>
						</Button>
					</template>
				</Dropdown>
			</div>
			<div class="relative">
				<Dropdown :options="statusOptions('ATS_JobOpening', updateField, customStatuses)">
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
			</div>
		</template>
	</LayoutHeader>
	<div class="flex flex-1 flex-col overflow-hidden">
		<FileUploader @success="">
			<template #default="{ openFileSelector, error }">
				<div class="flex items-start justify-start gap-6 p-5 sm:items-center">
					<div class="group relative flex items-center justify-center h-6 w-6">
						<Button theme="gray" :variant="'ghost'" :ref_for="true" size="sm" @click="navigateToJobOpening">
							<template #prefix>
								<FeatherIcon name="arrow-left" class="h-8 w-8" />
							</template>
						</Button>
					</div>
					<div class="flex flex-col justify-center gap-2 sm:gap-0.5">
						<div class="text-3xl font-semibold text-gray-900 flex gap-2 items-center">
							{{ getDataRecord.data?.jo_public_title }}
							<Button theme="gray" :variant="'outline'" :ref_for="true" size="sm"
								@click="navigateToJobOpeningDetail">
								<template #prefix>
									<EditIcon />
									{{ __("Edit Job") }}
								</template>
							</Button>
							<!-- Nút chia sẻ Facebook và LinkedIn dùng FeatherIcon -->
							<Tooltip text="Share on Facebook" v-if="getDataRecord.data?.job_url_cms">
								<Button variant="outline" size="sm" class="p-1"
									:disabled="!getDataRecord.data?.job_url_cms" @click="shareOnFacebook">
									<FeatherIcon name="facebook" class="h-5 w-5 text-blue-600" />
								</Button>
							</Tooltip>
							<Tooltip text="Share on LinkedIn" v-if="getDataRecord.data?.job_url_cms">
								<Button variant="outline" size="sm" class="p-1"
									:disabled="!getDataRecord.data?.job_url_cms" @click="shareOnLinkedIn">
									<FeatherIcon name="linkedin" class="h-5 w-5 text-blue-700" />
								</Button>
							</Tooltip>

							<!-- Badge hiển thị trạng thái -->
							<Button variant="solid" :theme="isUpdating
									? 'gray'
									: getDataRecord.data?.publish_to_career_page
										? 'green'
										: 'red'
								" :loading="isUpdating" :disabled="isUpdating" @click="togglePublishStatus" class="flex items-center gap-1">
								<div class="flex items-center gap-1">
									<FeatherIcon v-if="!isUpdating" :name="getDataRecord.data?.publish_to_career_page
											? 'check-circle'
											: 'x-circle'
										" class="w-4 h-4" />
									<span>
										{{
											isUpdating
												? __("Updating...")
												: getDataRecord.data?.publish_to_career_page
													? __("Published")
													: __("Unpublished")
										}}
									</span>
								</div>
							</Button>
						</div>
						<div class="mt-2 flex gap-4 text-sm text-gray-600">
							<span class="">
								{{ getDataRecord.data?.jo_position }}
							</span>
							<div class="border-l border"></div>
							<span class="">
								Open Positions:
								{{ getDataRecord.data?.jo_display_quantity }}
							</span>
							<div class="border-l border"></div>
							<span class="">
								Applicants Applied:
								{{ getDataRecord.data?.applicants_applied }}
							</span>
							<div class="border-l border"></div>
							<span class="">
								Application Deadline:
								{{
									getFormat(
										getDataRecord.data?.jo_application_deadline,
										"",
										true,
									)
								}}
							</span>
							<div class="border-l border"></div>
							<!-- Popover cho "View More" -->
							<Popover placement="bottom">
								<template #target="{ togglePopover }">
									<span class="cursor-pointer text-gray-700" @click="togglePopover">
										View More
									</span>
								</template>

								<template #body-main>
									<div class="p-4">
										<div class="text-md font-normal">
											<p>
												<strong>{{ __("Contact Email") }}:</strong>
												{{ getDataRecord.data?.jo_contact_email }}
											</p>
											<p>
												<strong>{{ __("Contact Person") }}:</strong>
												{{ getDataRecord.data?.jo_contact_person }}
											</p>
											<p>
												<strong>{{ __("Contact Phone") }}:</strong>
												{{ getDataRecord.data?.jo_contact_phone }}
											</p>
										</div>
									</div>
								</template>
							</Popover>
						</div>
						<ErrorMessage class="mt-2" :message="__(error)" />
					</div>
				</div>
			</template>
		</FileUploader>
		<Tabs as="div" class="border rounded" v-model="tabIndex" :tabs="tabs">
			<template #tab-panel>
				<div v-show="tabs[tabIndex].name === 'Candidates'" class="flex flex-col h-full">
					<CMS_Candidate v-if="getDataRecord.data?.name"
						:filters="{ job_opening_id: getDataRecord.data.name, rejected: 0 }"
						:jobOpeningId="props.jobOpeningId" hideHeader candidateView displayCount
						@updateJobOpening="getDataRecord.reload()" ref="candidateRef" />
				</div>
				<!-- <div v-show="tabs[tabIndex].name === 'Interview_Schedule'">
					
					<ATS_Schedule
						:filters="{ jo_id: getDataRecord.data?.name }"
						hideHeader
						hideListView
						embedded
						ref="scheduleRef"
					/>
				</div> -->
			</template>
		</Tabs>
	</div>
	<ConfirmModal v-model="showConfirmModal" @confirm="() => deleteRecord(fieldStore.childTableField)">
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

	<Dialog v-model="showCandidateSelector">
		<template #body-title>
			<h3 class="text-lg font-medium">{{ __("Chọn ứng viên để gán vào tin") }}</h3>
		</template>

		<template #body-content>
			<Autocomplete v-model="selectedCandidates" :options="unassignedCandidates" placeholder="Chọn ứng viên"
				:multiple="true">
				<template #item-prefix="{ option }">
					<Avatar :image="getCandidateAvatar(option)" :label="option.can_full_name" class="w-6 h-6" />
				</template>

				<template #item-suffix="{ option }">
					<!-- Checkmark nếu đang được chọn -->
					<div v-if="selectedCandidates.find((c) => c.value === option.value)">
						<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-green-500" fill="none"
							viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
							<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
						</svg>
					</div>
				</template>
			</Autocomplete>
		</template>

		<template #actions>
			<div class="flex justify-end">
				<Button variant="solid" @click="assignCandidatesToJob" :disabled="!selectedCandidates.length">
					{{ __("Gán vào tin") }}
				</Button>
				<Button variant="subtle" class="ml-2" @click="showCandidateDialog = false">
					{{ __("Huỷ") }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import LayoutHeader from "@/components/LayoutHeader.vue";
import {
	Breadcrumbs,
	Avatar,
	FileUploader,
	Dropdown,
	Tabs,
	call,
	createResource,
	FeatherIcon,
	Popover,
	Dialog,
	Autocomplete,
	Tooltip,
} from "frappe-ui";

import {
	createToast,
	getFormat,
} from "@/utils";

import EditIcon from "@/components/Icons/EditIcon.vue";
import CalendarIcon from "@/components/Icons/CalendarIcon.vue";
import UserPlus from "@/components/Icons/UserPlus.vue";
import IndicatorIcon from "@/components/Icons/IndicatorIcon.vue";
import User from "@/components/Icons/User.vue";
import ConfirmModal from "../../components/Modals/ConfirmModal.vue";


import { useFieldStore } from "@/stores/activeRecord";
import { useActiveTabManager } from "@/composables/useActiveTabManager";

import { h, computed, ref, watch, provide } from "vue";
import { useRoute, useRouter } from "vue-router";

import CMS_Candidate from "../cms_candidate/Candidates.vue";
import { statusesStore } from "@/stores/statuses";
import { useCountCandidateStore } from "@/stores/CountCandidate";
import { updateDocumentTitle } from '@/utils';
import { getColoredAvatar } from "@/utils/avatar";


const { statusOptions, getJOStatus } = statusesStore();

const fieldStore = useFieldStore();
const countCandidateStore = useCountCandidateStore();

const scheduleRef = ref(null);
const candidateRef = ref(null);
const isUpdating = ref(false);
const breadcrumbs = computed(() => {
	let items = [{ label: __("Job Opening"), route: { name: "job_opening" } }];

	items.push({
		label: getDataRecord.data?.name || __("Untitled"),
		route: {},
	});
	return items;
});

const props = defineProps({
	jobOpeningId: {
		type: String,
		required: true,
	},
});

const router = useRouter();
const route = useRoute();
const customStatuses = ref([]);
const showConfirmModal = ref(false);

const hiddenFilters = ref(["job_opening_id", "jo_id"]);
const showCandidateSelector = ref(false);
const selectedCandidates = ref([]);
const unassignedCandidates = ref([]);
const loadingCandidates = ref(false);

// Helper function to get candidate avatar with fallback
const getCandidateAvatar = (option) => {
	return getColoredAvatar(option.label, option.can_avatar);
};

async function fetchUnassignedCandidates() {
	loadingCandidates.value = true;
	try {
		const res = await call("frappe.client.get_list", {
			doctype: "ATS_Candidate",
			fields: ["name", "can_full_name", "can_email", "can_avatar", "job_opening_id"],
			limit_page_length: 100,
		});
		unassignedCandidates.value = res
			.filter((item) => {
				const alreadyInJob = item.job_opening_id === getDataRecord.data.name;
				const emailDuplicated = res.some(
					(c) =>
						c.can_email === item.can_email &&
						c.job_opening_id === getDataRecord.data.name,
				);
				return !alreadyInJob && !emailDuplicated;
			})
			.map((item) => ({
				label: item.can_full_name,
				value: item.name,
				can_email: item.can_email,
				can_avatar: item.can_avatar,
			}));
	} catch (err) {
		console.log(object)(err);
	} finally {
		loadingCandidates.value = false;
	}
}

function openCandidateSelector() {
	fetchUnassignedCandidates();
	showCandidateSelector.value = true;
}

async function assignCandidatesToJob() {
	try {
		await call("go1_cms.api.candidate.assign_candidates_to_job", {
			job_id: getDataRecord.data.name,
			candidate_ids: selectedCandidates.value.map((c) => c.value),
		});
		showCandidateSelector.value = false;
		selectedCandidates.value = [];
		createToast({
			title: __("Candidates assigned successfully"),
			icon: "check",
			iconClasses: "text-green-600",
		});

		candidateRef.value.viewControls.reloadData();
	} catch (err) {
		console.log(err);
	}
}


provide("hiddenFilters", hiddenFilters);
provide("jobOpeningId", props.jobOpeningId);

const createSchedule = (job_opening) => {
	if (!scheduleRef.value) return;

	scheduleRef.value?.handleCreateClick(job_opening);
};

const createCandidate = (job_opening, recruitment_process) => {
	if (!candidateRef.value) return;
	candidateRef.value?.openChoiceModal();
	candidateRef.value.createParams = {
		job_opening: getDataRecord.data.name,
		recruitment_process: getDataRecord.data.recruitment_process[0].round_name,
	};
	// candidateRef.value?.handleCreateClick(job_opening, recruitment_process);
};

const getDataRecord = createResource({
	url: "go1_cms.go1_cms.doctype.cms_jobopening.api.get_detail",
	params: { name: props.jobOpeningId },
	auto: true,
	cache: ["getDataRecored", props.jobOpeningId],
	onSuccess: (data) => {

	},
});

watch(
	() => getDataRecord.data?.recruitment_process,
	(val) => {
		if (val && val.length && candidateRef.value) {
			candidateRef.value.createParams = {
				job_opening: getDataRecord.data.name,
				recruitment_process: val[0].round_name,
			};
		}
	},
	{ immediate: true },
);

const getDataCountCandidateRecruitProcess = createResource({
	url: "go1_cms.go1_cms.doctype.cms_jobopening.api.get_candidate_counts",	
	params: { job_opening: props.jobOpeningId },
	auto: true,
	onSuccess: (data) => {
		countCandidateStore.setCountCandidate(data);
	},
});

// const getProcessByJob = createResource({
// 	url: "mbw_ats.mbw_ats.doctype.ats_jobopening.api.get_recruitment_stages",
// 	params: { job_opening: props.jobOpeningId },
// 	auto: true,
// 	onSuccess: (data) => {
// 		countCandidateStore.setRecruitmentProcess(data);
// 	},
// });

// onMounted(() => {
// 	if (getDataRecord.data) return;
// 	getDataRecord.fetch();
// });

// watch(
// 	() => route.fullPath,
// 	() => {
// 		console.log("Route changed, refetching data...");
// 		getDataRecord.fetch();
// 	}
// );

const navigateToJobOpening = () => {
	router.push({
		name: "job_opening",
	});
};

const navigateToJobOpeningDetail = () => {
	router.push({
		name: "ats_job_opening_detail",
		params: { id: props.jobOpeningId },
		query: { from: "view" }
	});
};

const defaultActions = ref([
	{
		icon: h(User, { class: "h-4 w-4" }),
		label: __("New Candidate"),
		onClick: () =>
			createCandidate(getDataRecord.data.name, getDataRecord.data.recruitment_process),
	},
	{
		icon: h(CalendarIcon, { class: "h-4 w-4" }),
		label: __("New Schedule"),
		onClick: () => createSchedule(getDataRecord.data.name),
	},
	{
		icon: h(UserPlus, { class: "h-4 w-4" }),
		label: __("Select Existing Candidates"),
		onClick: () => {
			openCandidateSelector();
		},
	},
]);

// KHoi taoj cac tab
const activitiesTabs = computed(() => {
	let tabOptions = [
		{
			name: "Candidates",
			label: __("Candidates"),
			icon: User,
		},

	];
	return tabOptions.filter((tab) => (tab.condition ? tab.condition() : true));
});

const tabs = computed(() => {
	return [...activitiesTabs.value].filter((tab) => (tab.condition ? tab.condition() : true));
});

let { tabIndex } = useActiveTabManager(tabs, "Candidates");

// watch(tabIndex, (newVal) => {
// 	console.log(newVal);
// });

function validateRequired(fieldname, value) {
	let meta = getDataRecord.data.fields_meta || {};
	if (meta[fieldname]?.reqd && !value) {
		createToast({
			title: __("Error Updating"),
			text: __(`${meta[fieldname].label} is a required field`),
			icon: "x",
			iconClasses: "text-red-600",
		});
		return true;
	}
	return false;
}

// Lấy dữ liệu lịch trình từ API
// const schedulesResource = createResource({
// 	url: "mbw_ats.mbw_ats.doctype.ats_jobopening.api.get_schedules_by_job",
// 	params: { name: props.jobOpeningId },
// 	auto: true, // Gọi API ngay khi component được mounted
// 	onSuccess: (data) => {
// 		// Gán dữ liệu lịch trình vào biến `schedules`
// 	},
// });

// Chuyển dữ liệu về dạng phù hợp với lịch
// const dataCalendar = computed(() => {
// 	return (
// 		schedulesResource.data?.data?.map((item) => {
// 			const startHour = parseInt(item.sch_start_time.split(":")[0]);
// 			const startMinute = parseInt(item.sch_start_time.split(":")[1]);

// 			// Tính toán thời gian kết thúc
// 			let endMinute = startMinute + item.sch_duration;
// 			let endHour = startHour;
// 			if (endMinute >= 60) {
// 				endHour += Math.floor(endMinute / 60);
// 				endMinute %= 60;
// 			}

// 			const fromTime = `${String(startHour).padStart(2, "0")}:${String(startMinute).padStart(2, "0")}`;
// 			const toTime = `${String(endHour).padStart(2, "0")}:${String(endMinute).padStart(2, "0")}`;

// 			return {
// 				title: item.sch_interview_type,
// 				date: item.sch_interview_date,
// 				jo: item.jo_id,
// 				from_time: fromTime,
// 				to_time: toTime,
// 				color: getStatusColor(item.sch_interview_date, fromTime, toTime),
// 				with: item.can_id,
// 				room: item.sch_room,
// 				name: item.name,
// 			};
// 		}) || []
// 	);
// });

// Hàm xác định màu trạng thái
const getStatusColor = (date, startTime, endTime) => {
	const now = new Date();
	const eventStart = new Date(`${date}T${startTime}`);
	const eventEnd = new Date(`${date}T${endTime}`);

	const diffInDays = (eventStart - now) / (1000 * 60 * 60 * 24);

	if (eventEnd < now) return "gray"; // Đã diễn ra (Quá khứ)
	if (eventStart <= now && eventEnd >= now) return "green"; // Đang diễn ra
	if (eventStart.toDateString() === now.toDateString()) return "red"; // Hôm nay, chưa bắt đầu
	if (diffInDays <= 1) return "yellow"; // Sắp diễn ra trong 1 ngày
	if (diffInDays <= 2) return "orange"; // Sắp diễn ra trong 2 ngày
	if (diffInDays <= 7) return "purple"; // Trong vòng 1 tuần
	return "blue"; // Tương lai xa
};

//convert class dropdown
const generateClassObject = (colorClass) => {
	// Tạo một đối tượng từ mảng lớp CSS
	return colorClass?.reduce((acc, className) => {
		acc[className] = true;
		return acc;
	}, {});
};

function updateField(name, value, callback) {
	updateFieldData(name, value, () => {
		getDataRecord.data[name] = value;
		callback?.();
	});
	getDataRecord.fetch();
}

function updateFieldData(fieldname, value, callback) {
	value = Array.isArray(fieldname) ? "" : value;

	if (!Array.isArray(fieldname) && validateRequired(fieldname, value)) return;

	createResource({
		url: "frappe.client.set_value",
		params: {
			doctype: "ATS_JobOpening",
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

const togglePublishStatus = async () => {
	const newStatus = getDataRecord.data?.publish_to_career_page ? 0 : 1;

	isUpdating.value = true;

	try {
		await call("frappe.client.set_value", {
			doctype: "ATS_JobOpening",
			name: getDataRecord.data?.name,
			fieldname: {
				publish_to_career_page: newStatus,
			},
		});
		getDataRecord.reload(); // refetch lại dữ liệu
		createToast({
			title: __("Record updated"),
			icon: "check",
			iconClasses: "text-green-600",
		});
		isUpdating.value = false;
	} catch (err) {
		isUpdating.value = false;
		createToast({
			title: __("Error updating Record"),
			text: __(err.messages?.[0]),
			icon: "x",
			iconClasses: "text-red-600",
		});
	}
};

const shareOnFacebook = () => {
	const url = getDataRecord.data?.job_url_cms;
	if (!url) return;
	const shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
	window.open(shareUrl, "_blank", "width=600,height=400");
};

const shareOnLinkedIn = () => {
	const url = getDataRecord.data?.job_url_cms;
	if (!url) return;
	const shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`;
	window.open(shareUrl, "_blank", "width=600,height=400");
};
const pageMeta = computed(() => {
	return {
		title: getDataRecord.data?.jo_public_title || __('Job Opening'),
		description: __('Job Opening'),
	}
})

updateDocumentTitle(pageMeta)
</script>
