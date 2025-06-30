<template>
	<ProcessRecruitRound
		v-if="rounds"
		:data="rounds"
		:round-types="roundTypes"
		@edit="editRound"
		@add="openAddModal"
		@delete="deleteRound"
		@reorder="updatePositions"
	/>
	<p v-else class="text-center text-gray-500">{{ __("No rounds available") }}</p>

	<AddTypeModal
		v-model="isModalOpen"
		v-model:edit="isEdit"
		@action="isEdit ? saveEditedRound() : addRound()"
	>
		<template #title>
			{{ isEdit ? __("Edit Round") : __("Add Round") }}
		</template>
		<template #content>
			<div class="flex flex-col gap-4">
				<FormControl
					type="text"
					size="sm"
					variant="subtle"
					placeholder="Round Name"
					label="Round Name"
					v-model="selectedRound.round_name"
					required
				/>
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
				<div class="flex flex-col">
					<span class="text-xs text-ink-gray-5 mb-2">{{ __("Select Test") }}</span>
					<Link
						v-if="props.jobOpeningId"
						class="text-sm text-ink-gray-8"
						v-model="selectedRound.test_link"
						:doctype="'LMS Quiz'"
						:filters="{ job_opening_id: props.jobOpeningId }"
					/>
				</div>
				<!-- Conditional rendering based on whether a quiz exists -->
				<!-- <Button v-if="!existingQuiz.data" variant="outline" class="ml-2" @click="navigateToQuizzes()">
					<div class="flex items-center gap-1">
						<FeatherIcon name="plus" class="h-4" />
						<span class="text-nowrap">{{ __("Create Test") }}</span>
					</div>
				</Button> -->
				<!-- <Button v-else variant="outline" class="ml-2" @click="navigateToExistingQuiz()">
					<div class="flex items-center gap-1">
						<FeatherIcon name="edit-2" class="h-4" />
						<span class="text-nowrap">{{ __("Edit Test") }}</span>
					</div>
				</Button> -->
				<div>
					<!-- <FormControl
						type="autocomplete"
						label="Select Test"
						:options="options_Test"
						size="sm"
						variant="subtle"
						v-model="selectedQuiz"
						@update:modelValue="handleQuizSelection"
					/> -->
					<!-- Replace the link display with a Send Mail button -->
					<!-- <div v-if="selectedQuiz" class="mt-2 flex space-x-2">
						<Button variant="outline" @click="copyLinkToClipboard" class="flex-1">
							<div class="flex items-center gap-1">
								<FeatherIcon name="copy" class="h-4" />
								<span>{{ __("Copy Link") }}</span>
							</div>
						</Button>
						<Button variant="outline" @click="sendQuizEmail" class="flex-1">
							<div class="flex items-center gap-1">
								<FeatherIcon name="mail" class="h-4" />
								<span>{{ __("Send Email") }}</span>
							</div>
						</Button>
					</div> -->
				</div>

				<div class="mt-4 border-t pt-4">
					<div class="text-sm font-semibold mb-2">{{ __("Automation Triggers") }}</div>
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
								label="Action Type"
								:options="[
									'Send Email',
									'Create Task',
									// 'Update Field',
									// 'Assign Permission',
									// 'Create Document',
									'Send Notification',
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
import ProcessRecruitRound from "@/components/ProcessRecruitRound.vue";
import AddTypeModal from "./Modals/AddTypeModal.vue";
import { createToast, validateTriggers } from "../utils";
import { FormControl, Checkbox, createResource } from "frappe-ui";
import { ref, computed, watch, toRaw, onMounted } from "vue";
import Autocomplete from "./frappe-ui-custom/Autocomplete.vue";
import { useRouter, useRoute } from "vue-router";
import Link from "@/components/Controls/Link.vue";
const props = defineProps({
	modelValue: Object,
	roundTypes: {
		type: Array,
		default: () => [],
	},
	jobOpeningId: {
		type: String,
		default: "",
	},
});
const emit = defineEmits(["update:modelValue"]);
const router = useRouter();
const rounds = ref(null);
watch(
	() => props.modelValue,
	(newVal) => {
		try {
			// Ưu tiên structuredClone nếu là object thường
			rounds.value = structuredClone(toRaw(newVal));
		} catch (e) {
			console.warn("structuredClone failed, using JSON fallback", e);
			rounds.value = JSON.parse(JSON.stringify(newVal));
		}
	},
	{ immediate: true, deep: true },
);

// Resource to check if a quiz exists for the current job opening
const existingQuiz = createResource({
	url: "frappe.client.get_list",
	params: {
		doctype: "LMS Quiz",
		filters: {
			job_opening_id: props.jobOpeningId,
		},
		fields: ["name", "title", "link_test"],
		limit: 100,
	},
	auto: false,
});

// Available quiz options for autocomplete
const options_Test = ref([]);
const selectedQuiz = ref(null);
const selectedQuizLink = ref("");

// Function to handle quiz selection
const handleQuizSelection = (quiz) => {
	if (quiz) {
		// Find the selected quiz in the existingQuiz data
		const selected = existingQuiz.data.find((q) => q.name === quiz.value);
		if (selected && selected.link_test) {
			selectedQuizLink.value = selected.link_test;
		} else {
			selectedQuizLink.value = "";
		}
	} else {
		selectedQuizLink.value = "";
	}
};

// Function to copy the quiz link to clipboard
const copyLinkToClipboard = () => {
	if (!selectedQuiz.value) {
		createToast({
			title: __("No Test Selected"),
			text: __("Please select a test first"),
			icon: "alert-circle",
			iconClasses: "text-yellow-600",
		});
		return;
	}

	// Generate and copy the quiz link
	const generateTokenResource = createResource({
		url: "mbw_ats.mbw_ats.doctype.lms_quiz.lms_quiz.generate_quiz_token",
		params: {
			quiz_id: selectedQuiz.value.value,
			job_opening_id: props.jobOpeningId,
			send_email_to_candidates: false,
		},
		onSuccess: (data) => {
			const autoLoginUrl = `${window.location.origin}/mbw_ats/auto-login/${data.quiz_id}?token=${data.token}`;

			navigator.clipboard
				.writeText(autoLoginUrl)
				.then(() => {
					createToast({
						title: __("Link Copied"),
						text: __("The test link has been copied to clipboard"),
						icon: "check",
						iconClasses: "text-green-600",
					});
				})
				.catch((err) => {
					console.error("Failed to copy link: ", err);
					createToast({
						title: __("Copy Failed"),
						text: __("Failed to copy the link to clipboard"),
						icon: "alert-circle",
						iconClasses: "text-red-600",
					});
				});
		},
	});

	generateTokenResource.fetch();
};

// Function to send quiz email to candidates
const sendQuizEmail = () => {
	if (!selectedQuiz.value) {
		createToast({
			title: __("No Test Selected"),
			text: __("Please select a test first"),
			icon: "alert-circle",
			iconClasses: "text-yellow-600",
		});
		return;
	}

	// Confirm before sending
	if (!confirm(__("Do you want to send test email to all candidates in this job opening?"))) {
		return;
	}

	const sendMailResource = createResource({
		url: "mbw_ats.mbw_ats.doctype.lms_quiz.lms_quiz.send_quiz_email_to_candidates",
		params: {
			quiz_id: selectedQuiz.value.value,
			job_opening_id: props.jobOpeningId,
		},
		onSuccess: (data) => {
			if (data.success) {
				createToast({
					title: __("Success"),
					text: data.message,
					icon: "check",
					iconClasses: "text-green-600",
				});
			} else {
				createToast({
					title: __("Error"),
					text: data.message,
					icon: "alert-circle",
					iconClasses: "text-red-600",
				});
			}
		},
		onError: (err) => {
			console.error("Error sending test emails:", err);
			createToast({
				title: __("Error"),
				text: err.message || __("Could not send test emails"),
				icon: "alert-circle",
				iconClasses: "text-red-600",
			});
		},
	});

	sendMailResource.fetch();
};

// Watch for changes in job opening ID and check for existing quiz
watch(
	() => props.jobOpeningId,
	() => {
		if (props.jobOpeningId) {
			checkExistingQuiz();
		}
	},
	{ immediate: true },
);

// Check for existing quiz on component mount
onMounted(() => {
	if (props.jobOpeningId) {
		checkExistingQuiz();
	}
});

// Function to check if a quiz exists for the current job opening
function checkExistingQuiz() {
	if (!props.jobOpeningId) return;

	existingQuiz.params = {
		doctype: "LMS Quiz",
		filters: {
			job_opening_id: props.jobOpeningId,
		},
		fields: ["name", "title", "link_test"],
		limit: 100,
	};
	existingQuiz.fetch().then(() => {
		// Once we have the quizzes, format them for the autocomplete dropdown
		if (existingQuiz.data && existingQuiz.data.length > 0) {
			options_Test.value = existingQuiz.data.map((quiz) => ({
				label: quiz.title,
				value: quiz.name,
				link: quiz.link_test,
			}));
		}
	});
}

const isEdit = ref(false);
const isModalOpen = ref(false);
const selectedRound = ref({ triggers: [] });
const roundTypes = ref(props.roundTypes || []);

const selectedRoundType = computed({
	get() {
		return (
			roundTypes.value.find((option) => option.value === selectedRound.value.round_type) ||
			null
		);
	},
	set(option) {
		selectedRound.value.round_type = option?.value || "";
	},
});

const triggerEventOptions = [
	{ label: __("When candidate enters this stage"), value: "on_enter" },
	{ label: __("When candidate exits this stage"), value: "on_exit" },
	{ label: __("Scheduled check (daily/weekly)"), value: "scheduled" },
	{ label: __("When data in this stage is updated"), value: "on_update" },
	{ label: __("Create test for candidate"), value: "on_create_test" },
];

const targetOptions = [
	{ label: "Applicant", value: "Applicant" },
	{ label: "Recruiter", value: "Recruiter" },
	{ label: "Interviewer", value: "Interviewer" },
	{ label: "HR Staff", value: "HR Staff" },
	{ label: "Hiring Manager", value: "Hiring Manager" },
];

function emitUpdate() {
	console.log(rounds.value);
	emit("update:modelValue", rounds.value);
}

function editRound(round) {
	console.log(round);

	// Deep clone tránh mutation object reactive gốc
	const clone = JSON.parse(JSON.stringify(round));

	if (Array.isArray(clone.triggers)) {
		for (const t of clone.triggers) {
			try {
				t.targets = JSON.parse(t.targets || "[]");
				console.log(t.targets);
			} catch (e) {
				console.error("Failed to parse targets:", e);
				t.targets = [];
			}
		}
	}

	selectedRound.value = clone;
	isEdit.value = true;
	isModalOpen.value = true;
}

function openAddModal() {
	selectedRound.value = {
		round_type_name: "",
		color: "gray",
		position: 0,
		triggers: [],

		__isLocal: true,
	};
	isEdit.value = false;
	isModalOpen.value = true;

	// Reset selected quiz when opening the modal
	selectedQuiz.value = null;
	selectedQuizLink.value = "";
}

function addEmptyTrigger() {
	selectedRound.value.triggers.push({
		trigger_event: "on_enter",
		action_type: "Send Email",
		targets: [],
		enabled: true,
		send_booking_email: false,
	});
}

function recalculateAllPositions() {
	const fixedStart = rounds.value.fixedStart || [];
	const draggable = rounds.value.draggableRounds || [];
	const fixedEnd = rounds.value.fixedEnd || [];

	let currentPosition = 1;

	for (const r of fixedStart) {
		r.position = currentPosition++;
	}

	for (const r of draggable) {
		r.position = currentPosition++;
	}

	for (const r of fixedEnd) {
		r.position = currentPosition++;
	}

	emitUpdate();
}

function addRound() {
	if (!selectedRound.value.round_name || !selectedRound.value.round_type) {
		createToast({
			title: "Missing Fields",
			icon: "alert-circle",
			iconClasses: "text-red-600",
		});
		return;
	}

	selectedRound.value.triggers = selectedRound.value.triggers.map((t) => ({
		...t,
		targets: JSON.stringify(t.targets || []),
	}));

	const fixedStart = rounds.value.fixedStart || [];
	const fixedEnd = rounds.value.fixedEnd || [];
	let draggable = rounds.value.draggableRounds || [];

	// Add new round vào giữa
	draggable.push({
		...selectedRound.value,
		__isLocal: true,
	});

	// Recalculate positions
	// fixedStart giữ nguyên vị trí
	let currentPosition = 1;

	for (const r of fixedStart) {
		r.position = currentPosition++;
	}

	for (const r of draggable) {
		r.position = currentPosition++;
	}

	for (const r of fixedEnd) {
		r.position = currentPosition++;
	}

	// Gán lại vào rounds
	rounds.value.draggableRounds = draggable;
	rounds.value.fixedStart = fixedStart;
	rounds.value.fixedEnd = fixedEnd;
	emitUpdate();
	isModalOpen.value = false;
}

function saveEditedRound() {
	const rawTriggers = selectedRound.value.triggers || [];

	const converted = rawTriggers.map((t) => ({
		...t,
		targets: JSON.stringify(Array.isArray(t.targets) ? t.targets : []),
	}));

	const updateRoundList = (list) =>
		list.map((r) =>
			r.name === selectedRound.value.name
				? { ...selectedRound.value, triggers: converted, __isLocal: true }
				: r,
		);

	// Cập nhật vào cả 3 list
	rounds.value.fixedStart = updateRoundList(rounds.value.fixedStart || []);
	rounds.value.draggableRounds = updateRoundList(rounds.value.draggableRounds || []);
	rounds.value.fixedEnd = updateRoundList(rounds.value.fixedEnd || []);

	emitUpdate();
	isModalOpen.value = false;
}

function updatePositions(event) {
	const { oldIndex, newIndex } = event;
	console.log("Reorder event:", oldIndex, newIndex);
	if (oldIndex === newIndex) return;

	// Sort list theo position để đồng bộ với index UI
	const list = [...rounds.value.draggableRounds].sort((a, b) => a.position - b.position);

	// Di chuyển phần tử trong list
	const moved = list.splice(oldIndex, 1)[0];
	list.splice(newIndex, 0, moved);

	// Cập nhật lại position tuần tự
	list.forEach((item, idx) => {
		item.position = idx + 1; // hoặc currentPos++ nếu tính theo offset khác
	});

	// Gán lại vào state
	rounds.value.draggableRounds = list;

	// Update lại fixedEnd để đảm bảo vị trí toàn cục đúng
	recalculateAllPositions();
}

function deleteRound(round) {
	rounds.value.draggableRounds = rounds.value.draggableRounds.filter(
		(r) => r.name !== round.name,
	);
	// Gọi update lại toàn bộ vị trí
	recalculateAllPositions();
}
</script>

<style scoped>
:deep(.form-control.prefix select) {
	padding-left: 2rem;
}

.form-control {
	margin-bottom: 12px;
}
</style>
