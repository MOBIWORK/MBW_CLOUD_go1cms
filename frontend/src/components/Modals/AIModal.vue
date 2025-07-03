<template>
	<Dialog
		v-model="show"
		:options="{
			size: '6xl',
			title: __('Generate Job Description AI'),
		}"
	>
		<template #body-content class="">
			<div class="grid grid-cols-3 gap-4">
				<div class="flex flex-col justify-between gap-4 col-span-1">
					<div class="flex flex-col gap-2">
						<div>
							<div class="mb-1.5 text-sm text-gray-600">{{ __("Job Title") }}</div>
							<TextInput
								v-model="formData.job_title"
								variant="outline"
								:placeholder="__('job_title')"
							/>
						</div>
						<!-- <div>
							<div class="mb-1.5 text-sm text-gray-600">{{ __("Designation") }}</div>
							<TextInput
								v-model="formData.designation"
								variant="outline"
								:placeholder="__('Designation')"
							/>
						</div>
						<div>
							<div class="mb-1.5 text-sm text-gray-600">{{ __("Rank") }}</div>
							<TextInput
								v-model="formData.rank"
								variant="outline"
								:placeholder="__('Rank')"
							/>
						</div>
						<div>
							<div class="mb-1.5 text-sm text-gray-600">{{ __("Experience") }}</div>
							<TextInput
								v-model="formData.experience"
								variant="outline"
								:placeholder="__('Experience')"
							/>
						</div> -->
						<div>
							<div class="mb-1.5 text-sm text-gray-600">{{ __("Tone") }}</div>
							<FormControl
								type="select"
								v-model="formData.tone"
								:options="[
									{ label: __('Professional'), value: __('Professional') },
									{ label: __('Friendly'), value: __('Friendly') },
									{ label: __('Creative'), value: __('Creative') },
									{ label: __('Formal'), value: __('Formal') },
									{ label: __('Casual'), value: __('Casual') }
								]"
								variant="outline"
								:placeholder="__('Select Tone')"
							/>
						</div>
						<div>
							<div class="mb-1.5 text-sm text-gray-600">
								{{ __("Comments") }}
							</div>
							<Textarea
								v-model="formData.comments"
								variant="outline"
								:placeholder="__('Write your comments here. Example: I want to create a job description for a software engineer with 3 years of experience in React and Node.js.')"
								:rows="10"
							/>
						</div>
					</div>

					<div class="flex justify-end">
						<Button
							variant="solid"
							:label="__('Generate')"
							@click="() => triggerFakeAI('')"
							:loading="typingEffect || isCallingAPI"
						/>
					</div>
				</div>
				<div class="flex-1 flex flex-col gap-2 col-span-2">
					<div>
						<div class="mb-1.5 text-sm text-gray-600 flex items-center justify-between">
							<span>{{ __("Job Description") }}</span>
							<Button
								v-if="formData.description"
								variant="subtle"
								theme="blue"
								size="sm"
								@click="() => rewriteSection('description')"
								:loading="isRewritingSection === 'description'"
							>
								<template #prefix>
									<FeatherIcon name="cpu" class="h-3 w-3" />
								</template>
								{{ __("Rewrite with AI") }}
							</Button>
						</div>
						<!-- Hiển thị Skeleton khi đang call API AI *hoặc* đang typing -->
						<div
							v-if="isTyping.description"
							class="relative h-[150px] w-full rounded bg-gray-200 overflow-hidden"
						>
							<!-- Dải gradient chạy ngang -->
							<div
								class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-skeleton"
							></div>
						</div>

						<TextEditor
							v-else
							ref="descriptionEditor"
							variant="outline"
							editor-class="!prose-sm !max-w-full overflow-auto !w-full min-h-[120px] max-h-[150px] py-1.5 px-2 rounded border border-gray-300 bg-white hover:border-gray-400 hover:shadow-sm focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors"
							:bubbleMenu="true"
							:fixedMenu="true"
							:content="formData.description"
							:placeholder="__('Job Description')"
						/>
						
						<!-- Rewrite Input for Description -->
						<div v-if="showRewriteInput === 'description'" class="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
							<div class="mb-2 text-sm text-gray-600">
								{{ __("How would you like to rewrite the Job Description?") }}
							</div>
							<div class="flex gap-2">
								<TextInput
									:id="`rewrite-input-description`"
									v-model="rewriteInstructions.description"
									variant="outline"
									:placeholder="__('Example: Make it more detailed, shorter, more professional...')"
									class="flex-1"
									@keyup.enter="() => executeRewrite('description')"
								/>
								<Button
									variant="solid"
									size="sm"
									@click="() => executeRewrite('description')"
									:loading="isRewritingSection === 'description'"
									:disabled="!rewriteInstructions.description.trim()"
								>
									{{ __("Send") }}
								</Button>
								<Button
									variant="outline"
									size="sm"
									@click="showRewriteInput = null"
								>
									{{ __("Cancel") }}
								</Button>
							</div>
						</div>
					</div>
					<div>
						<div class="mb-1.5 text-sm text-gray-600 flex items-center justify-between">
							<span>{{ __("Job Requirement") }}</span>
							<Button
								v-if="formData.candidateRequirements"
								variant="subtle"
								theme="blue"
								size="sm"
								@click="() => rewriteSection('candidateRequirements')"
								:loading="isRewritingSection === 'candidateRequirements'"
							>
								<template #prefix>
									<FeatherIcon name="cpu" class="h-3 w-3" />
								</template>
								{{ __("Rewrite with AI") }}
							</Button>
						</div>
						<div
							v-if="isTyping.candidateRequirements"
							class="relative h-[150px] w-full rounded bg-gray-200 overflow-hidden"
						>
							<!-- Dải gradient chạy ngang -->
							<div
								class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-skeleton"
							></div>
						</div>
						<TextEditor
							v-else
							ref="candidateRequirementsEditor"
							variant="outline"
							editor-class="!prose-sm !max-w-full overflow-auto !w-full min-h-[120px] max-h-[150px] py-1.5 px-2 rounded border border-gray-300 bg-white hover:border-gray-400 hover:shadow-sm focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors"
							:bubbleMenu="true"
							:fixedMenu="true"
							:content="formData.candidateRequirements"
							:placeholder="__('Job Requirement')"
						/>
						
						<!-- Rewrite Input for Requirements -->
						<div v-if="showRewriteInput === 'candidateRequirements'" class="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
							<div class="mb-2 text-sm text-gray-600">
								{{ __("How would you like to rewrite the Job Requirements?") }}
							</div>
							<div class="flex gap-2">
								<TextInput
									:id="`rewrite-input-candidateRequirements`"
									v-model="rewriteInstructions.candidateRequirements"
									variant="outline"
									:placeholder="__('Example: Add more technical skills, be more specific...')"
									class="flex-1"
									@keyup.enter="() => executeRewrite('candidateRequirements')"
								/>
								<Button
									variant="solid"
									size="sm"
									@click="() => executeRewrite('candidateRequirements')"
									:loading="isRewritingSection === 'candidateRequirements'"
									:disabled="!rewriteInstructions.candidateRequirements.trim()"
								>
									{{ __("Send") }}
								</Button>
								<Button
									variant="outline"
									size="sm"
									@click="showRewriteInput = null"
								>
									{{ __("Cancel") }}
								</Button>
							</div>
						</div>
					</div>
					<div>
						<div class="mb-1.5 text-sm text-gray-600 flex items-center justify-between">
							<span>{{ __("Job Benefits") }}</span>
							<Button
								v-if="formData.candidateBenefits"
								variant="subtle"
								theme="blue"
								size="sm"
								@click="() => rewriteSection('candidateBenefits')"
								:loading="isRewritingSection === 'candidateBenefits'"
							>
								<template #prefix>
									<FeatherIcon name="cpu" class="h-3 w-3" />
								</template>
								{{ __("Rewrite with AI") }}
							</Button>
						</div>
						<div
							v-if="isTyping.candidateBenefits"
							class="relative h-[150px] w-full rounded bg-gray-200 overflow-hidden"
						>
							<!-- Dải gradient chạy ngang -->
							<div
								class="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-skeleton"
							></div>
						</div>
						<TextEditor
							v-else
							ref="candidateBenefitsEditor"
							:content="formData.candidateBenefits"
							variant="outline"
							editor-class="!prose-sm !max-w-full overflow-auto !w-full min-h-[120px] max-h-[150px] py-1.5 px-2 rounded border border-gray-300 bg-white hover:border-gray-400 hover:shadow-sm focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors"
							:bubbleMenu="true"
							:fixedMenu="true"
							:placeholder="__('Job Benefits')"
						/>
						
						<!-- Rewrite Input for Benefits -->
						<div v-if="showRewriteInput === 'candidateBenefits'" class="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
							<div class="mb-2 text-sm text-gray-600">
								{{ __("How would you like to rewrite the Job Benefits?") }}
							</div>
							<div class="flex gap-2">
								<TextInput
									:id="`rewrite-input-candidateBenefits`"
									v-model="rewriteInstructions.candidateBenefits"
									variant="outline"
									:placeholder="__('Example: Add more benefits, be more attractive...')"
									class="flex-1"
									@keyup.enter="() => executeRewrite('candidateBenefits')"
								/>
								<Button
									variant="solid"
									size="sm"
									@click="() => executeRewrite('candidateBenefits')"
									:loading="isRewritingSection === 'candidateBenefits'"
									:disabled="!rewriteInstructions.candidateBenefits.trim()"
								>
									{{ __("Send") }}
								</Button>
								<Button
									variant="outline"
									size="sm"
									@click="showRewriteInput = null"
								>
									{{ __("Cancel") }}
								</Button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</template>
		<template #actions>
			<div class="flex flex-col justify-end gap-2" v-if="fakeAIHistory.length > 0">
				<div class="flex justify-end gap-2">
					<Button
						variant="outline"
						label="Bản trước"
						@click="showPrevious"
						:disabled="currentIndex <= 0 || typingEffect || isCallingAPI"
						:loading="typingEffect"
					/>
					<Button
						variant="outline"
						label="Bản sau"
						@click="showNext"
						:disabled="
							currentIndex >= fakeAIHistory.length - 1 ||
							typingEffect ||
							isCallingAPI
						"
						:loading="typingEffect"
					/>
					<Button
						variant="solid"
						label="Use Generated Content"
						@click="useGeneratedContent"
						:loading="typingEffect"
					/>
				</div>
				<!-- AI suggestion -->
				<div
					class="flex gap-2 rounded-lg border border-blue-400 p-2 w-2/3 ml-auto"
					v-if="!isCallingAPI && !typingEffect"
				>
					<div class="flex items-center">
						<FeatherIcon name="cpu" class="h-10 w-10 text-blue-600" />
					</div>
					<div class="flex flex-1 flex-col gap-2">
						<div class="mt-2 flex items-center w-full justify-between bg-white p-2">
							<div class="flex flex-wrap gap-2 py-3">
								<button
									v-for="suggestion in aiSuggestions"
									:key="suggestion"
									class="px-4 py-2 text-sm rounded-full border border-blue-400 hover:bg-blue-600 hover:text-white"
									@click="() => triggerFakeAI(suggestion)"
								>
									{{ suggestion }}
								</button>
							</div>
							<div class="flex gap-2">
								<Dropdown
									:options="[
										{
											label: 'Vui vẻ hơn',
											onClick: () => triggerFakeAI('Vui vẻ hơn'),
										},
										{
											label: 'Ngắn gọn hơn',
											onClick: () => triggerFakeAI('Ngắn gọn hơn'),
										},
									]"
								>
									<Button class="border border-blue-500">
										<template #icon>
											<FeatherIcon name="more-horizontal" class="h-4 w-4" />
										</template>
									</Button>
								</Dropdown>
								<Button
									class="border border-blue-500"
									@click="showInputAI = !showInputAI"
								>
									<template #icon>
										<FeatherIcon name="plus-circle" class="h-4 w-4" />
									</template>
								</Button>
							</div>
						</div>
						<!-- AI Input Section -->
						<div v-if="showInputAI">
							<FormControl
								placeholder="Nhập thông tin bạn cần AI trợ giúp"
								type="text"
								v-model="suggestion_content"
								class="border border-blue-400 rounded p-2"
							>
								<template #suffix>
									<FeatherIcon
										name="send"
										class="h-4 w-4 cursor-pointer"
										@click="
											() => {
												sendSuggestionAi();
											}
										"
									/>
								</template>
							</FormControl>
						</div>
					</div>
				</div>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
import { capture } from "@/telemetry";
import { TextEditor, call, createResource, Textarea, Dropdown, FormControl, FeatherIcon, Button, TextInput } from "frappe-ui";
import { ref, nextTick, watch, reactive, computed } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
	doctype: {
		type: String,
		default: "Job Opening",
	},
	doc: {
		type: String,
		default: "",
	},
	note: {
		type: Object,
		default: {},
	},
	jo_job_description:{
		type: String,
		default: "",
	},
	jo_job_requirement:{
		type: String,
		default: "",
	},
	jo_job_benefits:{
		type: String,
		default: "",
	}
});

console.log(props.note);

const fakeAIHistory = ref([]); // Danh sách lưu các nội dung đã nhận
const currentIndex = ref(0); // Chỉ mục của nội dung hiện tại
const isCallingAPI = ref(false); // Trạng thái gọi API
const showInputAI = ref(false);
const suggestion_content = ref("");
// Danh sách gợi ý
const aiSuggestions = ref([
	"Dài hơn/Chi tiết hơn",
	"Ngắn hơn",
	"Chuyên nghiệp hơn",
	"Sáng tạo hơn",
	"Thân thiện hơn",
]);

const show = defineModel();
const formData = reactive({
	designation: props.note?.jo_position || "",
	rank: props.note?.jo_level_id || "",
	experience: "",
	job_title: props.note?.jo_public_title || "",
	additional_info: "",
	tone: "Professional",
	rewrite_request: "",
	description: props.jo_job_description,
	candidateRequirements: props.jo_job_requirement,
	candidateBenefits: props.jo_job_benefits,
	comments: "",
});
const isTyping = ref({
	description: false,
	candidateRequirements: false,
	candidateBenefits: false,
});
const typingEffect = computed(() => {
	return isTyping.value.description || isTyping.value.candidateRequirements || isTyping.value.candidateBenefits;
});
const isRewritingSection = ref(null);
const showRewriteInput = ref(null);
const rewriteInstructions = ref({
	description: "",
	candidateRequirements: "",
	candidateBenefits: ""
});

const emit = defineEmits(["after"]);

const router = useRouter();

// const fakeAIResource = createResource({
// 	url: "mbw_recruitment.api.AIContent.generate_fake_content", // Đường dẫn tới API
// 	auto: false, // Không tự động fetch dữ liệu khi khởi tạo
// 	params: {
// 		designation: formData.designation,
// 		rank: formData.rank,
// 		experience: formData.experience,
// 	},
// 	onSuccess: (response) => {
// 		// Bind dữ liệu từ API vào infoJR

// 		startTypingEffect("description", response.description)
// 		startTypingEffect("candidateRequirements", response.custom_candidate_requirements)
// 		startTypingEffect("candidateBenefits", response.custom_candidate_benefits)

// 		// Hiển thị thông báo thành công
// 	},
// 	onError: (error) => {
// 		// Hiển thị thông báo lỗi
// 	},
// })

function convertDataToHtmlLists(data) {
	// Chuyển đổi từng phần thành HTML riêng
	const dataHtml = `<ul>${data.map((item) => `<li>${item}</li>`).join("")}</ul>`;
	return dataHtml;
}
// Trigger AI Generation
async function triggerFakeAI(suggestion) {
	console.log(suggestion);
	try {
		isCallingAPI.value = true;
		
		// Reset all typing states and form data for full generation
		isTyping.value = {
			description: false,
			candidateRequirements: false,
			candidateBenefits: false,
		};
		
		for (const key in isTyping.value) {
			isTyping.value[key] = true;
			formData[key] = "";
		}

		// Always use main generation API for triggerFakeAI (initial generation or full regeneration)
		if (suggestion) formData.comments += ` ${suggestion}`;

		const generateJobDescription = createResource({
			url: "go1_cms.api.ai.generate_job_description_v2",
			method: "POST",
			params: {
				jobTitle: formData.job_title || "",
				tone: formData.tone || "Professional",
				comments: formData.comments,
			},
			onSuccess(data) {
				console.log("Job Description Generated Successfully:", data);
			},
			onError(error) {
				console.error("Error Generating Job Description:", error);
				throw error;
			},
			auto: false,
		});

		await generateJobDescription.fetch();
		const apiData = generateJobDescription.data;

		// Kiểm tra dữ liệu trả về từ API v2
		if (!apiData) {
			throw new Error("Dữ liệu API trả về không hợp lệ");
		}

		// Chuẩn hóa dữ liệu từ API v2 format
		const normalized = {
			description: apiData?.jobDescription || "",
			candidateRequirements: apiData?.jobRequirements || "",
			candidateBenefits: apiData?.jobResponsibilities || "", // Map jobResponsibilities to benefits
		};

		// Generate all sections
		await Promise.all([
			startTypingEffect("description", normalized.description),
			startTypingEffect("candidateRequirements", normalized.candidateRequirements),
			startTypingEffect("candidateBenefits", normalized.candidateBenefits),
		]);

		Object.assign(formData, normalized);
		fakeAIHistory.value.push(normalized);
		currentIndex.value = fakeAIHistory.value.length - 1;

		// Cập nhật formData với dữ liệu mới
		updateFormData(normalized);
	} catch (error) {
		console.error("Error generating AI content:", error);
	} finally {
		isCallingAPI.value = false;
		isRewritingSection.value = null;
	}
}

const sendSuggestionAi = () => {
	console.log("Send suggestion");
	triggerFakeAI(suggestion_content.value);
};
// Hiệu ứng gõ chữ
async function startTypingEffect(field, content) {
	isTyping.value[field] = true;
	formData[field] = "";

	const chunkSize = 5;
	for (let i = 0; i < content.length; i += chunkSize) {
		formData[field] += content.substring(i, i + chunkSize);
		await new Promise((resolve) => setTimeout(resolve, 20));
	}

	isTyping.value[field] = false;
}

// Emit generated content to parent
function useGeneratedContent() {
	emit("after", {
		jo_job_description: formData.description,
		jo_job_requirement: formData.candidateRequirements,
		jo_job_benefits: formData.candidateBenefits,
	});
	show.value = false; // Close modal
}

function showPrevious() {
	if (currentIndex.value > 0) {
		currentIndex.value--;
		updateFormData(fakeAIHistory.value[currentIndex.value]);
	}
}

function showNext() {
	if (currentIndex.value < fakeAIHistory.value.length - 1) {
		currentIndex.value++;
		updateFormData(fakeAIHistory.value[currentIndex.value]);
	}
}

function updateFormData(data) {
	// Cập nhật nội dung vào formData
	formData.description = data.description || "";
	formData.candidateRequirements = data.candidateRequirements || "";
	formData.candidateBenefits = data.candidateBenefits || "";
}

function rewriteSection(field) {
	// Toggle the input field for this section
	if (showRewriteInput.value === field) {
		showRewriteInput.value = null;
	} else {
		showRewriteInput.value = field;
		// Focus on the input field after it appears
		nextTick(() => {
			const input = document.querySelector(`#rewrite-input-${field}`);
			if (input) input.focus();
		});
	}
}

async function executeRewrite(field) {
	const instruction = rewriteInstructions.value[field];
	if (!instruction.trim()) {
		return;
	}
	
	try {
		// Set loading state for this specific field only
		isRewritingSection.value = field;

		// Prepare current content for refinement (DON'T clear the field yet)
		const currentContent = {
			description: formData.description,
			candidateRequirements: formData.candidateRequirements,
			candidateBenefits: formData.candidateBenefits,
		};

		const originalJD = {
			jobDescription: currentContent.description,
			jobRequirements: currentContent.candidateRequirements,
			jobResponsibilities: currentContent.candidateBenefits,
		};

		// Map frontend field names to API field names
		const fieldMapping = {
			description: "jobDescription",
			candidateRequirements: "jobRequirements",
			candidateBenefits: "jobResponsibilities"
		};

		// Only rewrite the selected field
		const fieldsToRewrite = [fieldMapping[field]];

		const refineJobDescription = createResource({
			url: "mbw_ats.api.ai.jd_section_refine",
			method: "POST",
			params: {
				originalJD: originalJD,
				fieldsToRewrite: fieldsToRewrite,
				comments: instruction,
			},
			onSuccess(data) {
				console.log("Job Description Section Refined Successfully:", data);
			},
			onError(error) {
				console.error("Error Refining Job Description Section:", error);
				throw error;
			},
			auto: false,
		});

		await refineJobDescription.fetch();
		const apiData = refineJobDescription.data;

		if (!apiData) {
			throw new Error("Dữ liệu API trả về không hợp lệ");
		}

		// Get the rewritten content for the specific field
		let newContent;
		if (field === 'description') {
			newContent = apiData?.jobDescription || currentContent.description;
		} else if (field === 'candidateRequirements') {
			newContent = apiData?.jobRequirements || currentContent.candidateRequirements;
		} else if (field === 'candidateBenefits') {
			newContent = apiData?.jobResponsibilities || currentContent.candidateBenefits;
		}

		// Now clear the field and start typing effect
		isTyping.value[field] = true;
		formData[field] = "";
		await startTypingEffect(field, newContent);

		// Create complete updated state for history
		const updatedState = {
			description: field === 'description' ? newContent : currentContent.description,
			candidateRequirements: field === 'candidateRequirements' ? newContent : currentContent.candidateRequirements,
			candidateBenefits: field === 'candidateBenefits' ? newContent : currentContent.candidateBenefits,
		};

		// Add to history
		fakeAIHistory.value.push(updatedState);
		currentIndex.value = fakeAIHistory.value.length - 1;

		// Clear the input and hide it after successful rewrite
		rewriteInstructions.value[field] = "";
		showRewriteInput.value = null;

	} catch (error) {
		console.error("Error rewriting section:", error);
	} finally {
		isRewritingSection.value = null;
		isTyping.value[field] = false;
	}
}
</script>

<style scoped>
.animate-skeleton {
	animation: skeleton-keyframe 1.5s ease-in-out infinite;
}

@keyframes skeleton-keyframe {
	0% {
		transform: translateX(-100%);
	}
	100% {
		transform: translateX(100%);
	}
}
</style>
