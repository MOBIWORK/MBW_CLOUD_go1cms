<template>
	<div class="space-y-6">
		<div class="text-center">
			<h3 class="text-lg font-medium mb-2">{{ __("Process & Approval") }}</h3>
			<p class="text-gray-600 mb-6">
				{{ __("Set up recruitment workflow and approval process") }}
			</p>
		</div>

		<div class="space-y-6">
			<!-- Recruitment Process -->
			<div class="bg-white border border-gray-200 rounded-lg p-4">
				<h4 class="text-lg font-medium text-gray-900 mb-4">
					{{ __("Recruitment Process") }}
				</h4>

				<div
					v-if="
						recruitmentRounds &&
						(recruitmentRounds.fixedStart?.length ||
							recruitmentRounds.draggableRounds?.length ||
							recruitmentRounds.fixedEnd?.length)
					"
				>
					<ProcessRecruitTable
						:modelValue="recruitmentRounds"
						:roundTypes="roundTypes"
						:data="formData"
						@update:modelValue="handleProcessUpdate"
					/>
				</div>

				<div v-else class="text-center py-8">
					<FeatherIcon name="settings" class="h-12 w-12 text-gray-400 mx-auto mb-4" />
					<p class="text-gray-500 mb-4">{{ __("No recruitment process configured") }}</p>
					<Button
						variant="outline"
						@click="loadDefaultProcess"
						:loading="loadingProcess"
					>
						<template #prefix>
							<FeatherIcon name="plus" class="h-4 w-4" />
						</template>
						{{ __("Load Default Process") }}
					</Button>
				</div>
			</div>

			<!-- Hiring Committee -->
			<div class="bg-white border border-gray-200 rounded-lg p-4">
				<h4 class="text-lg font-medium text-gray-900 mb-4">
					{{ __("Hiring Committee") }}
				</h4>

				<div
					v-if="formData.hiring_committee && formData.hiring_committee.length > 0"
					class="space-y-3"
				>
					<div
						v-for="(member, index) in formData.hiring_committee"
						:key="index"
						class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
					>
						<div class="flex items-center space-x-3">
							<div
								class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center"
							>
								<FeatherIcon name="user" class="h-4 w-4 text-blue-600" />
							</div>
							<div>
								<p class="font-medium text-gray-900">
									{{ getUser(member.user).full_name || member.user }}
								</p>
								<p class="text-sm text-gray-600">{{ getUser(member.user).email }}</p>
							</div>
						</div>
						<Button size="sm" variant="ghost" theme="red" @click="removeMember(index)">
							<FeatherIcon name="x" class="h-4 w-4" />
						</Button>
					</div>
				</div>

				<div v-else class="text-center py-6 bg-gray-50 rounded-lg">
					<FeatherIcon name="users" class="h-8 w-8 text-gray-400 mx-auto mb-2" />
					<p class="text-gray-500 text-sm">
						{{ __("No hiring committee members added") }}
					</p>
				</div>

				<div class="mt-4">
					<Button variant="outline" @click="showAddMember = true">
						<template #prefix>
							<FeatherIcon name="user-plus" class="h-4 w-4" />
						</template>
						{{ __("Add Committee Member") }}
					</Button>
				</div>
			</div>

			<!-- Job Status -->
			<div class="bg-white border border-gray-200 rounded-lg p-4">
				<h4 class="text-lg font-medium text-gray-900 mb-4">{{ __("Initial Status") }}</h4>
				<Field
					:field="{
						fieldname: 'status',
						fieldtype: 'Select',
						label: 'Job Opening Status',
						options: statusOptions,
						placeholder: 'Select initial status',
						visible: true,
					}"
				/>
				<div class="mt-2 text-xs text-gray-500">
					{{ __("You can change the status after creating the job opening") }}
				</div>
			</div>
		</div>

		<!-- Process Summary -->
		<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
			<h4 class="text-sm font-medium text-blue-900 mb-3">{{ __("Process Summary") }}</h4>
			<div class="space-y-2 text-sm text-blue-800">
				<div class="flex items-center justify-between">
					<span>{{ __("Recruitment Rounds:") }}</span>
					<span class="font-medium">{{ totalRounds }}</span>
				</div>
				<div class="flex items-center justify-between">
					<span>{{ __("Committee Members:") }}</span>
					<span class="font-medium">{{ formData.hiring_committee?.length || 0 }}</span>
				</div>
				<div class="flex items-center justify-between">
					<span>{{ __("Initial Status:") }}</span>
					<span class="font-medium">{{ formData.status || "Draft" }}</span>
				</div>
			</div>
		</div>

		<!-- Final Review -->
		<div
			class="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6"
		>
			<div class="text-center">
				<div
					class="w-12 h-12 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center mx-auto mb-4"
				>
					<FeatherIcon name="check-circle" class="h-6 w-6 text-white" />
				</div>
				<h4 class="text-lg font-medium text-gray-900 mb-2">{{ __("Ready to Create") }}</h4>
				<p class="text-sm text-gray-600 mb-4">
					{{
						__(
							'Your job opening is configured and ready to be created. Review all steps and click "Create Job Opening" to proceed.',
						)
					}}
				</p>
				<div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-600">
					<div class="text-center">
						<div class="font-semibold text-gray-800">
							{{ formData.jo_public_title || "-" }}
						</div>
						<div>{{ __("Job Title") }}</div>
					</div>
					<div class="text-center">
						<div class="font-semibold text-gray-800">
							{{ formData.jo_position || "-" }}
						</div>
						<div>{{ __("Position") }}</div>
					</div>
					<div class="text-center">
						<div class="font-semibold text-gray-800">
							{{ formData.jo_location || "-" }}
						</div>
						<div>{{ __("Location") }}</div>
					</div>
					<div class="text-center">
						<div class="font-semibold text-gray-800">{{ publishingChannels }}</div>
						<div>{{ __("Channels") }}</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Add Member Modal -->
		<div
			v-if="showAddMember"
			class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
		>
			<div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
				<h3 class="text-lg font-medium text-gray-900 mb-4">
					{{ __("Add Committee Member") }}
				</h3>

				<div class="space-y-4">
                    <Link
					class="form-control flex-1 truncate cursor-text"
					:value="newMember.member_name"
					:filters="{}"
					:doctype="'User'"
					@change="(v) => addValue(v)"
					:hideMe="true"
				>
					<template #prefix>
						<UserAvatar class="mr-2 !h-4 !w-4" :user="selectedUser" />
					</template>
					<template #item-prefix="{ option }">
						<UserAvatar class="mr-2" :user="option.value" size="xl" />
					</template>
					<template #item-label="{ option }">
						<Tooltip :text="option.value">
							<div class="cursor-pointer text-ink-gray-9 flex flex-col">
								<div class="items-center">
									{{ getUser(option.value).full_name }}
									<div class="text-sm text-gray-500">
										{{ getUser(option.value).email }}
									</div>
								</div>
							</div>
						</Tooltip>
					</template>
				</Link>
				</div>

				<div class="flex justify-end space-x-3 mt-6">
					<Button variant="outline" @click="showAddMember = false">
						{{ __("Cancel") }}
					</Button>
					<Button variant="solid" @click="addMember" :disabled="!newMember.member_name">
						{{ __("Add Member") }}
					</Button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import Field from "@/components/FieldLayout/Field.vue";
import ProcessRecruitTable from "@/components/ProcessRecruitTable.vue";
import { computed, provide, watch, ref, onMounted } from "vue";
import { FeatherIcon, Button, call, Tooltip } from "frappe-ui";
import { createToast, getRandom } from "@/utils";
import { usersStore } from "@/stores/users";
import UserAvatar from "@/components/UserAvatar.vue";
import Link from "@/components/Controls/Link.vue";

const { getUser } = usersStore();

const props = defineProps({
	formData: {
		type: Object,
		required: true,
	},
});

const emit = defineEmits(["update:formData"]);

const showAddMember = ref(false);
const loadingProcess = ref(false);
const recruitmentRounds = ref({});
const roundTypes = ref([]);
const newMember = ref({
	member_name: "",
});
const selectedUser = ref(null);

const addValue = (value) => {
	selectedUser.value = value;
	newMember.value.member_name = value;
};

// Alias for clarity
const formData = computed(() => props.formData || {});

// Initialize recruitment rounds from formData if available
const initializeRecruitmentRounds = () => {
	console.log(
		"🔍 JobOpeningStepProcessApproval - formData.recruitment_process:",
		formData.value.recruitment_process,
	);

	if (formData.value.recruitment_process && formData.value.recruitment_process.length > 0) {
		// Convert formData.recruitment_process back to the expected format for ProcessRecruitTable
		const fixedStart = [];
		const draggableRounds = [];
		const fixedEnd = [];

		formData.value.recruitment_process.forEach((round) => {
			// Create proper format for ProcessRecruitTable
			const roundData = {
				name: round.name,
				round_name: round.round_name,
				round_type: round.round_type,
				position: round.position,
				test_link: round.test_link || "",
				default: round.default || 0,
				// triggers: round.automation_rules || [],
			};

			// ✅ Improved categorization logic based on round type and position
			if (round.default === 1) {
				// ✅ Fixed start rounds: Application, Application Review, Ứng tuyển
				if (
					round.position === 0 || 
					round.round_type === "Application Review" || 
					round.round_type === "Application" ||
					round.round_type === "Ứng tuyển" ||
					round.round_name === "Ứng tuyển" ||
					round.round_name === "Application" ||
					round.round_name === "Application Review"
				) {
					fixedStart.push(roundData);
				}
				// ✅ Fixed end rounds: Final Decision, Offer, Đã tuyển, high position numbers
				else if (
					round.round_type === "Final Decision" || 
					round.round_type === "Offer" ||
					round.round_type === "Đã tuyển" ||
					round.round_name === "Final Decision" ||
					round.round_name === "Offer" ||
					round.round_name === "Đã tuyển" ||
					round.position >= 999
				) {
					fixedEnd.push(roundData);
				} 
				// ✅ Middle default rounds go to draggable (can be reordered)
				else {
					draggableRounds.push(roundData);
				}
			} else {
				// ✅ Non-default rounds are draggable
				draggableRounds.push(roundData);
			}
		});

		// Sort by position
		fixedStart.sort((a, b) => a.position - b.position);
		draggableRounds.sort((a, b) => a.position - b.position);
		fixedEnd.sort((a, b) => a.position - b.position);

		recruitmentRounds.value = {
			fixedStart,
			draggableRounds,
			fixedEnd,
		};

		console.log(
			"✅ JobOpeningStepProcessApproval - recruitmentRounds loaded:",
			recruitmentRounds.value,
		);
	} else {
		// Reset if no data
		recruitmentRounds.value = {
			fixedStart: [],
			draggableRounds: [],
			fixedEnd: [],
		};
		console.log(
			"📝 JobOpeningStepProcessApproval - No recruitment process data, showing empty state",
		);
	}
};

// Provide data for Field components
provide("data", formData);
provide("doctype", "ATS_JobOpening");
provide("preview", false);

// Options
const statusOptions = [
	{ label: "Draft", value: "Draft" },
	{ label: "Open", value: "Open" },
	{ label: "Paused", value: "Paused" },
	{ label: "Closed", value: "Closed" },
];

// Removed memberRoleOptions - role will be determined from candidate data, not manual input

// Computed properties
const totalRounds = computed(() => {
	const rounds = recruitmentRounds.value;
	const fixedStart = rounds.fixedStart?.length || 0;
	const draggable = rounds.draggableRounds?.length || 0;
	const fixedEnd = rounds.fixedEnd?.length || 0;
	return fixedStart + draggable + fixedEnd;
});

const publishingChannels = computed(() => {
	let count = 0;
	if (formData.value.publish_to_career_page) count++;
	if (formData.value.publish_to_facebook) count++;
	if (formData.value.publish_to_topcv) count++;
	if (formData.value.publish_to_linkedin) count++;
	return count + " selected";
});

// Methods
const handleProcessUpdate = (data) => {
	console.log('🔄 JobOpeningStepProcessApproval - handleProcessUpdate called with:', data);
	
	recruitmentRounds.value = data;

	const processData = [
		...convertRounds(data.fixedStart),
		...convertRounds(data.draggableRounds),
		...convertRounds(data.fixedEnd),
	];
	
	console.log('🔄 JobOpeningStepProcessApproval - emitting recruitment_process:', {
		fixedStart: data.fixedStart?.length || 0,
		draggableRounds: data.draggableRounds?.length || 0,
		fixedEnd: data.fixedEnd?.length || 0,
		totalProcessData: processData.length
	});

	emit("update:formData", { recruitment_process: processData });
};

const convertRounds = (rounds = []) =>
	rounds.map((r) => ({
		name: r.name || getRandom(10),
		idx: r.position + 1,
		round_name: r.round_name,
		round_type: r.round_type,
		position: r.position,
		test_link: r.test_link,
		default: r.default,
		// automation_rules: Array.isArray(r.triggers)
		// 	? r.triggers.map((t) => ({
		// 			...t,
		// 			targets:
		// 				typeof t.targets === "string"
		// 					? t.targets
		// 					: JSON.stringify(t.targets || []),
		// 			name: t.name || getRandom(10),
		// 			__isLocal: 1,
		// 			owner: "Administrator",
		// 		}))
		// 	: [],
		__isLocal: 1,
	}));

const loadDefaultProcess = async () => {
	loadingProcess.value = true;
	try {
		// Load round types với màu sắc trước
		await loadRoundTypes();

		// Load default recruitment process based on position
		if (formData.value.jo_position) {
			const response = await call("go1_cms.api.get_job_position_rounds", {
				job_position: formData.value.jo_position,
			});

			if (response.success) {
				recruitmentRounds.value = {
					fixedStart: response.fixedStart,
					draggableRounds: response.draggableRounds,
					fixedEnd: response.fixedEnd,
				};
				handleProcessUpdate(recruitmentRounds.value);
			}
		} else {
			// Default generic process
			recruitmentRounds.value = {
				fixedStart: [
					{
						name: getRandom(10),
						round_name: "Application Review",
						round_type: "Application Review",
						position: 0,
						default: 1,
					},
				],
				draggableRounds: [
					{
						name: getRandom(10),
						round_name: "Phone Interview",
						round_type: "Phone Interview",
						position: 1,
						default: 0,
					},
					{
						name: getRandom(10),
						round_name: "Technical Interview",
						round_type: "Technical Interview",
						position: 2,
						default: 0,
					},
				],
				fixedEnd: [
					{
						name: getRandom(10),
						round_name: "Final Decision",
						round_type: "Final Decision",
						position: 3,
						default: 1,
					},
				],
			};
			handleProcessUpdate(recruitmentRounds.value);
		}

		createToast({
			title: __("Success"),
			text: __("Default recruitment process loaded"),
			icon: "check",
			iconClasses: "text-green-600",
		});
	} catch (error) {
		console.error("Error loading process:", error);
	} finally {
		loadingProcess.value = false;
	}
};

const addMember = () => {
	if (!newMember.value.member_name) return;

	const members = formData.value.hiring_committee || [];
	members.push({
		user: newMember.value.member_name,  // Chỉ có field user thôi trong child table
		name: getRandom(10),
		__isLocal: 1,
	});

	emit("update:formData", { hiring_committee: members });

	// Reset form
	newMember.value = { member_name: "" };
	selectedUser.value = null;
	showAddMember.value = false;
};

const removeMember = (index) => {
	const members = [...(formData.value.hiring_committee || [])];
	members.splice(index, 1);
	emit("update:formData", { hiring_committee: members });
};

// Load round types
const loadRoundTypes = async () => {
	try {
		const response = await call(
			"go1_cms.go1_cms.doctype.ats_recruitment_process.ats_recruitment_process.get_round_types_with_color",
		);
		if (response) {
			// Fix: API trả về nested message
			roundTypes.value = response.message?.message || response.message || [];
			console.log("🎨 Round types loaded:", roundTypes.value);
		}
	} catch (error) {
		console.error("Error loading round types:", error);
	}
};

// Load recruitment process for position
const loadPositionRecruitmentProcess = async (positionName) => {
	if (!positionName) return;

	try {
		console.log(
			"🔄 JobOpeningStepProcessApproval - Loading recruitment process for position:",
			positionName,
		);

		// Gọi cả 2 API đồng thời
		const [processResponse, roundTypesResponse] = await Promise.all([
			call("go1_cms.api.get_job_position_rounds", {
				job_position: positionName,
			}),
			call(
				"go1_cms.go1_cms.doctype.ats_recruitment_process.ats_recruitment_process.get_round_types_with_color",
			),
		]);

		// Update round types với màu sắc
		if (roundTypesResponse) {
			// Fix: API trả về nested message
			roundTypes.value =
				roundTypesResponse.message?.message || roundTypesResponse.message || [];
			console.log(
				"✅ JobOpeningStepProcessApproval - Round types with colors loaded:",
				roundTypes.value,
			);
		}

		// Update recruitment process
		if (processResponse && processResponse.success) {
			console.log("✅ JobOpeningStepProcessApproval - API response:", processResponse);

			// ✅ Double-check: Don't override if formData already has process data
			const currentProcessLength = formData.value.recruitment_process?.length || 0;
			if (currentProcessLength > 0) {
				console.log("🚫 loadPositionRecruitmentProcess - Skipping update, formData already has process data:", currentProcessLength);
				return;
			}

			// Update recruitmentRounds for display
			recruitmentRounds.value = {
				fixedStart: processResponse.fixedStart || [],
				draggableRounds: processResponse.draggableRounds || [],
				fixedEnd: processResponse.fixedEnd || [],
			};

			// Update formData.recruitment_process
			handleProcessUpdate(recruitmentRounds.value);

			console.log(
				"✅ JobOpeningStepProcessApproval - Updated recruitmentRounds:",
				recruitmentRounds.value,
			);
		} else {
			console.log(
				"⚠️ JobOpeningStepProcessApproval - No recruitment process found for position:",
				positionName,
			);
		}
	} catch (error) {
		console.error(
			"❌ JobOpeningStepProcessApproval - Error loading recruitment process:",
			error,
		);
	}
};

// Watch for changes in formData.recruitment_process to update UI
watch(
	() => formData.value.recruitment_process,
	() => {
		initializeRecruitmentRounds();
	},
	{ immediate: true },
);

// Watch for position changes to auto-load recruitment process
watch(
	() => formData.value.jo_position,
	(newPosition, oldPosition) => {
		console.log("🔍 JobOpeningStepProcessApproval - Position changed:", {
			newPosition,
			oldPosition,
			hasExistingProcess: formData.value.recruitment_process?.length || 0
		});
		
		// ✅ Only load process if position changed AND no existing process data
		if (newPosition && newPosition !== oldPosition) {
			const hasExistingProcess = formData.value.recruitment_process && formData.value.recruitment_process.length > 0;
			if (!hasExistingProcess) {
				console.log("📋 No existing process data, loading from API");
				loadPositionRecruitmentProcess(newPosition);
			} else {
				console.log("✅ Existing process data found, skipping API call");
			}
		}
	},
	{ immediate: true },
);

// Watch roundTypes để debug
watch(
	() => roundTypes.value,
	(newRoundTypes) => {
		console.log("🎨 JobOpeningStepProcessApproval - roundTypes updated:", newRoundTypes);
		console.log("🎨 Length:", newRoundTypes?.length, "Sample:", newRoundTypes?.[0]);
	},
	{ immediate: true },
);

onMounted(() => {
	console.log("🔄 JobOpeningStepProcessApproval - onMounted called");
	
	loadRoundTypes();
	initializeRecruitmentRounds();

	// ✅ Only load recruitment process if position is selected AND no existing process data
	if (formData.value.jo_position) {
		const hasExistingProcess = formData.value.recruitment_process && formData.value.recruitment_process.length > 0;
		
		console.log("🔍 JobOpeningStepProcessApproval - onMounted check:", {
			position: formData.value.jo_position,
			hasExistingProcess,
			processLength: formData.value.recruitment_process?.length || 0
		});
		
		if (!hasExistingProcess) {
			console.log("📋 No existing process data in onMounted, loading from API");
			loadPositionRecruitmentProcess(formData.value.jo_position);
		} else {
			console.log("✅ Existing process data found in onMounted, skipping API call");
		}
	}
});

// Removed deep watch to prevent recursive updates
// Changes are handled by Field components through provide/inject
</script>
