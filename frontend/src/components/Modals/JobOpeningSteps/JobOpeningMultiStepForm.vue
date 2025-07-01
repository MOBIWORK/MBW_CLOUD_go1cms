<template>
	<DialogCustom v-model="show" :options="dialogOptions">
		<template #body>
			<div class="flex h-[85vh] bg-white">
				<!-- Sidebar Progress -->
				<div class="w-80 bg-gray-50 border-r border-gray-200 p-6 overflow-y-auto">
					<div class="mb-8">
						<h2 class="text-xl font-semibold text-gray-900 mb-2">{{ __('Create Job Opening') }}</h2>
						<p class="text-sm text-gray-600">{{ __('Complete all steps to publish your job opening') }}</p>
						
						<!-- Draft Indicator -->
						<div v-if="hasSavedDraft" class="mt-3 flex items-center space-x-2 text-xs text-orange-600 bg-orange-50 px-3 py-2 rounded-lg">
							<FeatherIcon name="edit-3" class="h-3 w-3" />
							<span>{{ __('Continuing from saved draft') }}</span>
						</div>
					</div>
					
					<div class="space-y-4">
						<div 
							v-for="(step, index) in steps" 
							:key="step.key"
							class="flex items-center space-x-3 p-3 rounded-lg transition-all cursor-pointer hover:bg-white"
							:class="{
								'bg-blue-50 border border-blue-200': currentStep === index,
								'bg-white border border-gray-200': completedSteps.includes(index) && currentStep !== index,
								'opacity-60': !completedSteps.includes(index) && currentStep !== index
							}"
							@click="goToStep(index)"
						>
							<div 
								class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
								:class="{
									'bg-blue-600 text-white': currentStep === index,
									'bg-green-600 text-white': completedSteps.includes(index) && currentStep !== index,
									'bg-gray-300 text-gray-600': !completedSteps.includes(index) && currentStep !== index
								}"
							>
								<FeatherIcon 
									v-if="completedSteps.includes(index) && currentStep !== index" 
									name="check" 
									class="h-4 w-4" 
								/>
								<span v-else>{{ index + 1 }}</span>
							</div>
							<div class="flex-1 min-w-0">
								<p class="text-sm font-medium text-gray-900" :class="{ 'text-blue-600': currentStep === index }">
									{{ __(step.title) }}
								</p>
								<p class="text-xs text-gray-500">{{ __(step.description) }}</p>
							</div>
						</div>
					</div>

					<!-- Progress Summary -->
					<div class="mt-8 p-4 bg-white rounded-lg border border-gray-200">
						<div class="flex items-center justify-between mb-2">
							<span class="text-sm font-medium text-gray-700">{{ __('Progress') }}</span>
							<span class="text-sm text-gray-500">{{ completedSteps.length }}/{{ steps.length }}</span>
						</div>
						<div class="w-full bg-gray-200 rounded-full h-2">
							<div 
								class="bg-blue-600 h-2 rounded-full transition-all duration-300"
								:style="{ width: (completedSteps.length / steps.length) * 100 + '%' }"
							></div>
						</div>
					</div>

					<!-- Draft Actions -->
					<div class="mt-6 space-y-2">
						<Button 
							variant="outline" 
							class="w-full" 
							@click="saveDraft"
							:disabled="!canSaveDraft"
						>
							<template #prefix>
								<FeatherIcon name="save" class="h-4 w-4" />
							</template>
							{{ __('Save Draft') }}
						</Button>
						
						<Button 
							v-if="hasSavedDraft"
							variant="outline" 
							theme="red"
							class="w-full" 
							@click="deleteDraft"
						>
							<template #prefix>
								<FeatherIcon name="trash-2" class="h-4 w-4" />
							</template>
							{{ __('Delete Draft') }}
						</Button>
					</div>
				</div>

				<!-- Main Content -->
				<div class="flex-1 flex flex-col">
					<!-- Header -->
					<div class="flex items-center justify-between p-6 border-b border-gray-200">
						<div>
							<h3 class="text-lg font-semibold text-gray-900">
								{{ __(steps[currentStep]?.title) }}
							</h3>
							<p class="text-sm text-gray-600 mt-1">
								{{ __(steps[currentStep]?.description) }}
							</p>
						</div>
						<Button variant="ghost" @click="show = false">
							<FeatherIcon name="x" class="h-5 w-5" />
						</Button>
					</div>

					<!-- Step Content -->
					<div class="flex-1 overflow-y-auto p-6">
						<component 
							:is="currentStepComponent" 
							:formData="formData"
							@update:formData="updateFormData"
							:key="currentStep"
						/>
					</div>

					<!-- Footer Actions -->
					<div class="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
						<Button 
							v-if="currentStep > 0"
							variant="outline" 
							@click="previousStep"
						>
							<template #prefix>
								<FeatherIcon name="arrow-left" class="h-4 w-4" />
							</template>
							{{ __('Previous') }}
						</Button>
						<div v-else></div>

						<div class="flex space-x-3">
							<Button 
								v-if="currentStep < steps.length - 1"
								variant="solid" 
								@click="nextStep"
								:disabled="!canProceedToNext"
							>
								{{ __('Next') }}
								<template #suffix>
									<FeatherIcon name="arrow-right" class="h-4 w-4" />
								</template>
							</Button>
							<Button 
								v-else
								variant="solid" 
								theme="green"
								@click="submitForm"
								:loading="isSubmitting"
								:disabled="!canSubmit"
							>
								<template #prefix>
									<FeatherIcon name="check" class="h-4 w-4" />
								</template>
								{{ __('Create Job Opening') }}
							</Button>
						</div>
					</div>
				</div>
			</div>
		</template>
	</DialogCustom>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { FeatherIcon, call, Button } from 'frappe-ui'
import { createToast, getRandom } from '@/utils'
import DialogCustom from '@/components/frappe-ui-custom/Dialog.vue'

// Step Components
import JobOpeningStepBasicInfo from './JobOpeningStepBasicInfo.vue'
import JobOpeningStepJobDescription from './JobOpeningStepJobDescription.vue'
import JobOpeningStepRecruitmentInfo from './JobOpeningStepRecruitmentInfo.vue'
import JobOpeningStepSalaryBenefits from './JobOpeningStepSalaryBenefits.vue'
import JobOpeningStepContactInfo from './JobOpeningStepContactInfo.vue'
import JobOpeningStepChannels from './JobOpeningStepChannels.vue'
import JobOpeningStepProcessApproval from './JobOpeningStepProcessApproval.vue'

const props = defineProps({
	// Remove selectedTemplate prop - no longer needed
})

const emit = defineEmits(['success', 'close', 'draft-deleted'])

const show = defineModel()
const currentStep = ref(0)
const isSubmitting = ref(false)
const formData = ref({})
const storageKey = 'cms_job_opening_draft'
// Add flag to prevent auto-save conflicts
const preventAutoSave = ref(false)
// Track visited steps and steps with data
const visitedSteps = ref(new Set([0])) // Always include step 0 as visited initially
const stepsWithData = ref(new Set())

// Steps configuration
const steps = [
	{ 
		key: 'basic_info', 
		title: 'Basic Information', 
		description: 'Job title, position, and department',
		component: JobOpeningStepBasicInfo
	},
	{ 
		key: 'job_description', 
		title: 'Job Description', 
		description: 'Description, requirements, and benefits',
		component: JobOpeningStepJobDescription
	},
	{ 
		key: 'recruitment_info', 
		title: 'Recruitment Info', 
		description: 'Location, work type, and deadline',
		component: JobOpeningStepRecruitmentInfo
	},
	{ 
		key: 'salary_benefits', 
		title: 'Salary & Benefits', 
		description: 'Compensation and benefits',
		component: JobOpeningStepSalaryBenefits
	},
	{ 
		key: 'contact_info', 
		title: 'Contact Info', 
		description: 'Recruiter contact information',
		component: JobOpeningStepContactInfo
	},
	{ 
		key: 'channels', 
		title: 'Publishing Channels', 
		description: 'Where to publish the job',
		component: JobOpeningStepChannels
	},
	{ 
		key: 'process_approval', 
		title: 'Process & Approval', 
		description: 'Recruitment workflow',
		component: JobOpeningStepProcessApproval
	}
]

// Current step component
const currentStepComponent = computed(() => steps[currentStep.value]?.component)

// Dialog options
const dialogOptions = computed(() => ({
	title: 'Create CMS Job Opening',
	size: '6xl'
}))

// Initialize form data
const initializeFormData = () => {
	return {
		jo_id: getRandom(10),
		jo_public_title: '',
		jo_internal_title: '',
		jo_position: '',
		jo_profession_id: '',
		jo_level_id: '',
		jo_using_unit: '',
		jo_department: '',
		jo_job_description: '',
		jo_job_requirement: '',
		jo_job_benefits: '',
		jo_location: '',
		jo_work_form: '',
		jo_display_quantity: 1,
		jo_language_requirement: '',
		jo_application_deadline: '',
		jo_salary_display_option: '',
		jo_currency: 'VND',
		jo_min_salary: 0,
		jo_max_salary: 0,
		jo_contact_person: '',
		jo_contact_email: '',
		jo_contact_phone: '',
		publish_to_career_page: 1,
		publish_to_facebook: 0,
		facebook_page_id: '',
		publish_to_topcv: 0,
		publish_to_linkedin: 0,
		job_url_cms: '',
		integration_status: '',
		recruitment_process: [],
		hiring_committee: [],
		status: 'Draft'
	}
}

// Load saved draft
const loadDraft = () => {
	console.log('🔍 loadDraft() called - checking sessionStorage...')
	const saved = sessionStorage.getItem(storageKey)
	
	if (saved) {
		try {
			const draftData = JSON.parse(saved)
			
			// ✅ Debug: Show what was loaded
			console.log('✅ Draft loaded from sessionStorage:', {
				recruitment_process_length: draftData.recruitment_process?.length || 0,
				hiring_committee_length: draftData.hiring_committee?.length || 0,
				jo_public_title: draftData.jo_public_title,
				visitedSteps: draftData._visitedSteps?.length || 0
			})
			
			// Restore visited steps if available
			if (draftData._visitedSteps) {
				visitedSteps.value = new Set(draftData._visitedSteps)
				delete draftData._visitedSteps // Remove meta data from form data
			}
			
			return draftData
		} catch (e) {
			console.error('❌ Failed to parse saved draft:', e)
		}
	} else {
		console.log('🚫 No saved draft found in sessionStorage')
	}
	return null
}

// Save to sessionStorage
const saveDraft = () => {
	const dataToSave = {
		...formData.value,
		_visitedSteps: Array.from(visitedSteps.value) // Save visited steps as meta data
	}
	sessionStorage.setItem(storageKey, JSON.stringify(dataToSave))
	createToast({
		title: __('Draft Saved'),
		text: __('Your progress has been saved'),
		icon: 'check',
		iconClasses: 'text-green-600'
	})
}

// Auto-save functionality
const autoSave = () => {
	console.log('🔍 autoSave() called - checking conditions...')
	
	if (preventAutoSave.value) {
		console.log('🚫 Auto-save prevented due to submit/cleanup state')
		return
	}
	
	// Only save if there's actual user data, not just default values
	if (hasUserData.value) {
		console.log('💾 Auto-saving user data to sessionStorage')
		const dataToSave = {
			...formData.value,
			_visitedSteps: Array.from(visitedSteps.value) // Save visited steps as meta data
		}
		
		// ✅ Debug: Show what's being saved
		console.log('💾 Data being saved:', {
			recruitment_process_length: dataToSave.recruitment_process?.length || 0,
			hiring_committee_length: dataToSave.hiring_committee?.length || 0,
			jo_public_title: dataToSave.jo_public_title,
			visitedSteps: dataToSave._visitedSteps
		})
		
		sessionStorage.setItem(storageKey, JSON.stringify(dataToSave))
		console.log('✅ Auto-save completed successfully')
	} else {
		console.log('🚫 Skipping auto-save - no user data detected')
		// ✅ Debug: Show current form data
		console.log('🔍 Current formData:', {
			recruitment_process_length: formData.value.recruitment_process?.length || 0,
			hiring_committee_length: formData.value.hiring_committee?.length || 0,
			jo_public_title: formData.value.jo_public_title
		})
	}
}

// Validation for each step - chỉ check những trường thực sự bắt buộc trong doctype
const stepValidations = {
	0: () => { // Basic Info
		const data = formData.value
		// Chỉ check trường bắt buộc: jo_public_title và jo_position
		return !!(data.jo_public_title?.trim() && data.jo_position?.trim())
	},
	1: () => { // Job Description
		// Không có trường bắt buộc trong step này
		return true
	},
	2: () => { // Recruitment Info
		// Không có trường bắt buộc trong step này
		return true
	},
	3: () => { // Salary & Benefits
		return true // Optional step
	},
	4: () => { // Contact Info
		// Không có trường bắt buộc trong step này
		return true
	},
	5: () => { // Channels
		return true // Optional step
	},
	6: () => { // Process & Approval
		return true // Optional step
	}
}

// Check if step has meaningful data
const stepHasData = (stepIndex) => {
	const stepFields = getStepFields(stepIndex)
	return stepFields.some(field => {
		const value = formData.value[field]
		return value && value !== '' && value !== 0 && (!Array.isArray(value) || value.length > 0)
	})
}

// Get fields for each step
const getStepFields = (stepIndex) => {
	const stepFieldMap = {
		0: ['jo_public_title', 'jo_internal_title', 'jo_position', 'jo_profession_id', 'jo_level_id', 'jo_using_unit', 'jo_department'],
		1: ['jo_job_description', 'jo_job_requirement', 'jo_job_benefits'],
		2: ['jo_location', 'jo_work_form', 'jo_display_quantity', 'jo_language_requirement', 'jo_application_deadline'],
		3: ['jo_salary_display_option', 'jo_currency', 'jo_min_salary', 'jo_max_salary'],
		4: ['jo_contact_person', 'jo_contact_email', 'jo_contact_phone'],
		5: ['publish_to_career_page', 'publish_to_facebook', 'publish_to_topcv', 'publish_to_linkedin'],
		6: ['recruitment_process', 'hiring_committee', 'status']
	}
	return stepFieldMap[stepIndex] || []
}

// Computed properties
const completedSteps = computed(() => {
	const completed = []
	for (let i = 0; i < steps.length; i++) {
		// Step is completed if:
		// 1. It has been visited AND meets validation requirements, OR
		// 2. It has meaningful data (from template or user input)
		const hasBeenVisited = visitedSteps.value.has(i)
		const passesValidation = stepValidations[i] && stepValidations[i]()
		const hasMeaningfulData = stepHasData(i)
		
		if ((hasBeenVisited && passesValidation) || hasMeaningfulData) {
			completed.push(i)
		}
	}
	return completed
})

const canProceedToNext = computed(() => {
	return stepValidations[currentStep.value]?.() || false
})

const canSubmit = computed(() => {
	// Chỉ check step thực sự bắt buộc theo doctype
	const requiredSteps = [0] // Chỉ Basic Info (jo_public_title + jo_position) là bắt buộc
	return requiredSteps.every(step => stepValidations[step]?.())
})

const canSaveDraft = computed(() => {
	return Object.keys(formData.value).some(key => 
		formData.value[key] && formData.value[key] !== ''
	)
})

const hasUserData = computed(() => {
	// ✅ If in cleanup/delete state, always return false
	if (preventAutoSave.value) {
		return false
	}
	
	// Check if form has meaningful user data (not just default values)
	const defaultData = initializeFormData()
	const hasData = Object.keys(formData.value).some(key => {
		const currentValue = formData.value[key]
		const defaultValue = defaultData[key]
		
		// Skip empty values
		if (!currentValue || currentValue === '') return false
		
		// ✅ Special handling for arrays
		if (Array.isArray(currentValue)) {
			// ✅ If array has items, consider it as user data
			if (currentValue.length > 0) {
				// ✅ Special handling for recruitment_process and hiring_committee
				if (key === 'recruitment_process' || key === 'hiring_committee') {
					console.log(`🔍 hasUserData - ${key}:`, currentValue.length, 'items')
					return true // Always consider non-empty process/committee as user data
				}
				// ✅ For other arrays, compare with default
				return JSON.stringify(currentValue) !== JSON.stringify(defaultValue)
			}
			return false
		}
		
		return currentValue !== defaultValue
	})
	
	// ✅ Debug log for hasUserData
	if (hasData) {
		console.log('✅ hasUserData: TRUE - form has user data')
	} else {
		console.log('🚫 hasUserData: FALSE - no user data detected')
	}
	
	return hasData
})

const hasSavedDraft = computed(() => {
	return Boolean(sessionStorage.getItem(storageKey))
})

// Methods
const updateFormData = (newData) => {
	console.log('🔄 updateFormData() called with:', newData)
	
	// Use nextTick to avoid recursive updates
	nextTick(() => {
		const oldData = { ...formData.value }
		formData.value = { ...formData.value, ...newData }
		
		// ✅ Debug: Show what changed
		console.log('🔄 Form data updated:', {
			before_recruitment_process: oldData.recruitment_process?.length || 0,
			after_recruitment_process: formData.value.recruitment_process?.length || 0,
			newData_keys: Object.keys(newData)
		})
		
		// Auto-save will handle the preventAutoSave check internally
		autoSave()
	})
}

const goToStep = (stepIndex) => {
	if (canProceedToNext.value || stepIndex <= currentStep.value) {
		currentStep.value = stepIndex
		// Mark step as visited
		visitedSteps.value.add(stepIndex)
	}
}

const nextStep = () => {
	if (canProceedToNext.value && currentStep.value < steps.length - 1) {
		currentStep.value++
		// Mark new step as visited
		visitedSteps.value.add(currentStep.value)
	}
}

const previousStep = () => {
	if (currentStep.value > 0) {
		currentStep.value--
		// Mark step as visited (going back still counts as visited)
		visitedSteps.value.add(currentStep.value)
	}
}

const deleteDraft = () => {
	console.log('🗑️ Manually deleting draft with key:', storageKey)
	
	// ✅ Prevent auto-save before any operations
	preventAutoSave.value = true
	
	// Remove from sessionStorage
	sessionStorage.removeItem(storageKey)
	
	// Reset form data and tracking
	console.log('🔄 Resetting form data and step')
	formData.value = initializeFormData()
	currentStep.value = 0
	visitedSteps.value = new Set([0])
	stepsWithData.value = new Set()
	
	createToast({
		title: __('Draft Deleted'),
		text: __('Your draft has been deleted'),
		icon: 'check',
		iconClasses: 'text-green-600'
	})
	
	emit('draft-deleted')
	show.value = false
	
	// ✅ Reset preventAutoSave after a delay to ensure cleanup is done
	setTimeout(() => {
		preventAutoSave.value = false
	}, 1000)
}

const submitForm = async () => {
	if (!canSubmit.value) return

	isSubmitting.value = true
	preventAutoSave.value = true // Prevent auto-save during submit
	try {
		// Prepare data for submission
		const submitData = { ...formData.value }
		
		// Convert recruitment_process if needed (remove automation_rules processing for CMS)
		if (submitData.recruitment_process) {
			submitData.recruitment_process = submitData.recruitment_process.map(r => ({
				...r
				// Removed automation_rules processing for CMS version
			}))
		}

		// Create job opening for CMS
		const doc = await call('frappe.client.insert', {
			doc: {
				doctype: 'CMS_JobOpening',
				...submitData
			}
		})

		if (doc.name) {
			// Skip Cal.com integration for CMS version
			// You can add CMS-specific post-creation logic here if needed

			// Clear saved draft and reset form
			console.log('🗑️ Clearing sessionStorage key:', storageKey)
			sessionStorage.removeItem(storageKey)
			console.log('🔄 Resetting form data and step')
			formData.value = initializeFormData()
			currentStep.value = 0
			visitedSteps.value = new Set([0])
			stepsWithData.value = new Set()

			createToast({
				title: __('Success'),
				text: __('Job opening created successfully'),
				icon: 'check',
				iconClasses: 'text-green-600'
			})

			emit('success', doc)
			show.value = false
		}
	} catch (error) {
		preventAutoSave.value = false // Re-enable auto-save on error
		createToast({
			title: __('Error'),
			text: __(error.messages?.[0] || 'Failed to create job opening'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
	} finally {
		isSubmitting.value = false
	}
}

// Lifecycle hooks
onMounted(() => {
	// Load existing draft or initialize new form (no template loading)
	const savedDraft = loadDraft()
	
	if (savedDraft) {
		console.log('✅ Found saved draft, loading from sessionStorage:', savedDraft)
		formData.value = { ...initializeFormData(), ...savedDraft }
	} else {
		formData.value = initializeFormData()
	}

	// Check for existing data and update steps with data
	nextTick(() => {
		updateStepsWithData()
		console.log('🔍 Initial steps with data:', Array.from(stepsWithData.value))
	})

	// Auto-save every 30 seconds
	const autoSaveInterval = setInterval(autoSave, 30000)
	
	onUnmounted(() => {
		clearInterval(autoSaveInterval)
	})
})

// Update visited steps based on template data
const updateStepsWithData = () => {
	for (let i = 0; i < steps.length; i++) {
		if (stepHasData(i)) {
			stepsWithData.value.add(i)
		}
	}
}

// Clean up on component unmount
onUnmounted(() => {
	// Only save if not in submit/cleanup state
	if (!preventAutoSave.value) {
		console.log('💾 Saving progress on unmount')
		autoSave()
	} else {
		console.log('🚫 Skipping save on unmount - already cleaned up')
	}
})
</script> 