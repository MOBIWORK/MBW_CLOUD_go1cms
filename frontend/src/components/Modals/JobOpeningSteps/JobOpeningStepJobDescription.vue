<template>
	<div class="space-y-6">
		<div class="text-center">
			<h3 class="text-lg font-medium mb-2">{{ __('Job Description') }}</h3>
			<p class="text-gray-600 mb-6">
				{{ __('Define the job responsibilities, requirements, and benefits') }}
			</p>
		</div>

		<!-- AI Generation Section -->
		<div class="bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-300 rounded-xl p-5 shadow-sm">
			<div class="flex items-start space-x-4">
				<div class="flex-shrink-0">
					<div class="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center shadow-md">
						<FeatherIcon name="zap" class="h-5 w-5 text-white" />
					</div>
				</div>
				<div class="flex-1">
					<p class="text-base font-semibold text-gray-900 mb-1">✨ {{ __('AI Assistant') }}</p>
					<p class="text-sm text-gray-700 mb-3">
						{{ __('Save time! Let AI generate professional job content instantly. Click the buttons below first, then edit as needed.') }}
					</p>
					
					<!-- AI Generation Controls -->
					<div class="space-y-4">
						<!-- Generate All Button (when no content) -->
						<div v-if="!hasAnyContent" class="text-center">
							<Button
								size="md"
								variant="solid"
								theme="purple"
								@click="generateAllContent"
								:loading="isAnyGenerating"
								:disabled="!formData.jo_position"
								class="font-medium px-6 py-2"
							>
								<template #prefix>
									<FeatherIcon name="zap" class="h-5 w-5" />
								</template>
								{{ __('🚀 Generate Complete Job Description') }}
							</Button>
						</div>

						<!-- Individual Generate Buttons (when has content) -->
						<div v-else class="space-y-3">
							<div class="flex flex-wrap gap-3">
								<Button
									size="sm"
									variant="solid"
									theme="purple"
									@click="generateJobDescription"
									:loading="generatingDescription"
									:disabled="!formData.jo_position"
									class="font-medium"
								>
									<template #prefix>
										<FeatherIcon name="edit-3" class="h-4 w-4" />
									</template>
									{{ __('Generate Description') }}
								</Button>
								<Button
									size="sm"
									variant="solid"
									theme="blue"
									@click="generateJobRequirements"
									:loading="generatingRequirements"
									:disabled="!formData.jo_position"
									class="font-medium"
								>
									<template #prefix>
										<FeatherIcon name="list" class="h-4 w-4" />
									</template>
									{{ __('Generate Requirements') }}
								</Button>
								<Button
									size="sm"
									variant="solid"
									theme="green"
									@click="generateJobBenefits"
									:loading="generatingBenefits"
									:disabled="!formData.jo_position"
									class="font-medium"
								>
									<template #prefix>
										<FeatherIcon name="gift" class="h-4 w-4" />
									</template>
									{{ __('Generate Benefits') }}
								</Button>
							</div>
							
							<!-- Regenerate All Button -->
							<div class="text-center border-t border-purple-100 pt-2">
								<Button
									size="sm"
									variant="outline"
									theme="purple"
									@click="generateAllContent"
									:loading="isAnyGenerating"
									:disabled="!formData.jo_position"
									class="font-medium text-xs"
								>
									<template #prefix>
										<FeatherIcon name="refresh-ccw" class="h-3 w-3" />
									</template>
									{{ __('Regenerate All Content') }}
								</Button>
							</div>
						</div>
						
						<!-- Custom Description -->
						<div class="border-t border-purple-200 pt-3 mt-3">
							<p class="text-xs font-medium text-gray-700 mb-2">📝 {{ __('Custom Instructions:') }}</p>
							<textarea
								v-model="customDescription"
								:placeholder="__('Enter custom instructions for AI (e.g., mention specific skills, company culture, remote work options...)')"
								class="w-full text-xs px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-purple-400 bg-white resize-none"
								rows="2"
								maxlength="500"
							></textarea>
							<div class="flex justify-between items-center mt-1">
								<span class="text-xs text-gray-500">{{ customDescription.length }}/500 {{ __('characters') }}</span>
								<Button
									v-if="customDescription.trim()"
									size="sm"
									variant="ghost"
									@click="customDescription = ''"
									class="text-xs"
								>
									<FeatherIcon name="x" class="h-3 w-3" />
								</Button>
							</div>
						</div>

						<!-- Refine Options -->
						<div class="border-t border-purple-200 pt-3 mt-3">
							<p class="text-xs font-medium text-gray-700 mb-2">🔧 {{ __('Refine Content:') }}</p>
							<div class="flex items-center space-x-3">
								<select 
									v-model="selectedRefineStyle"
									class="text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none focus:border-purple-400 bg-white"
								>
									<option value="">{{ __('Choose refine style...') }}</option>
									<option 
										v-for="preset in refinePresets" 
										:key="preset.value"
										:value="preset.value"
									>
										{{ preset.label }}
									</option>
								</select>
								<Button
									size="sm"
									variant="solid"
									theme="purple"
									@click="executeRefine"
									:disabled="!selectedRefineStyle || isAnyGenerating"
									class="text-xs font-medium"
								>
									<template #prefix>
										<FeatherIcon name="refresh-cw" class="h-3 w-3" />
									</template>
									{{ __('✨ Refine') }}
								</Button>
							</div>
						</div>
					</div>
					
					<div v-if="!formData.jo_position" class="mt-2 text-xs text-orange-600 font-medium">
						⚠️ {{ __('Please select a position in Step 1 first to enable AI generation') }}
					</div>
				</div>
			</div>
		</div>

		<!-- Form Fields Section -->
		<div class="space-y-6">
			<!-- Job Description -->
			<div>
				<Field
					:field="{
						fieldname: 'jo_job_description',
						fieldtype: 'Text Editor',
						label: 'Job Description',
						placeholder: 'Describe the main responsibilities and duties of this position...',
						visible: true
					}"
				/>
				<div class="mt-2 text-xs text-gray-500">
					{{ __('Provide a detailed description of the job responsibilities and day-to-day tasks') }}
				</div>
			</div>

			<!-- Job Requirements -->
			<div>
				<Field
					:field="{
						fieldname: 'jo_job_requirement',
						fieldtype: 'Text Editor',
						label: 'Job Requirements',
						placeholder: 'List the required skills, qualifications, and experience...',
						visible: true
					}"
				/>
				<div class="mt-2 text-xs text-gray-500">
					{{ __('Specify required qualifications, skills, experience, and education') }}
				</div>
			</div>

			<!-- Job Benefits -->
			<div>
				<Field
					:field="{
						fieldname: 'jo_job_benefits',
						fieldtype: 'Text Editor',
						label: 'Benefits & Perks',
						placeholder: 'Describe the benefits, perks, and compensation package...',
						visible: true
					}"
				/>
				<div class="mt-2 text-xs text-gray-500">
					{{ __('Highlight the benefits, perks, and what makes this role attractive') }}
				</div>
			</div>
		</div>

		<!-- Preview Section -->
		<div v-if="showPreview" class="bg-gray-50 border border-gray-200 rounded-lg p-4">
			<div class="flex items-center justify-between mb-3">
				<h4 class="text-sm font-medium text-gray-900">{{ __('Job Posting Preview') }}</h4>
				<Button
					size="sm"
					variant="ghost"
					@click="showPreview = false"
				>
					<FeatherIcon name="x" class="h-4 w-4" />
				</Button>
			</div>
			<div class="space-y-4 text-sm">
				<div v-if="formData.jo_job_description">
					<h5 class="font-medium text-gray-800">{{ __('Job Description') }}</h5>
					<div class="text-gray-600 mt-1" v-html="formData.jo_job_description"></div>
				</div>
				<div v-if="formData.jo_job_requirement">
					<h5 class="font-medium text-gray-800">{{ __('Requirements') }}</h5>
					<div class="text-gray-600 mt-1" v-html="formData.jo_job_requirement"></div>
				</div>
				<div v-if="formData.jo_job_benefits">
					<h5 class="font-medium text-gray-800">{{ __('Benefits') }}</h5>
					<div class="text-gray-600 mt-1" v-html="formData.jo_job_benefits"></div>
				</div>
			</div>
		</div>

		<!-- Preview Toggle -->
		<div class="text-center">
			<Button
				variant="outline"
				size="sm"
				@click="showPreview = !showPreview"
			>
				<template #prefix>
					<FeatherIcon name="eye" class="h-4 w-4" />
				</template>
				{{ showPreview ? __('Hide Preview') : __('Show Preview') }}
			</Button>
		</div>

		<!-- Validation Messages -->
		<div v-if="validationErrors.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-4">
			<div class="flex items-start space-x-3">
				<FeatherIcon name="alert-circle" class="h-5 w-5 text-red-500 mt-0.5" />
				<div>
					<p class="text-sm font-medium text-red-900">{{ __('Please fix the following errors:') }}</p>
					<ul class="mt-1 text-xs text-red-700 list-disc list-inside">
						<li v-for="error in validationErrors" :key="error">{{ __(error) }}</li>
					</ul>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import Field from '@/components/FieldLayout/Field.vue'
import { computed, provide, watch, ref } from 'vue'
import { FeatherIcon, Button, call } from 'frappe-ui'
import { createToast } from '@/utils'

const props = defineProps({
	formData: {
		type: Object,
		required: true
	}
})

const emit = defineEmits(['update:formData'])

const showPreview = ref(false)
const generatingDescription = ref(false)
const generatingRequirements = ref(false)
const generatingBenefits = ref(false)
const selectedRefineStyle = ref('')
const customDescription = ref('')

// Refine presets
const refinePresets = ref([
	{ label: '💼 Chuyên nghiệp hơn', value: 'professional', comment: 'làm cho chuyên nghiệp và trang trọng hơn' },
	{ label: '📏 Ngắn gọn hơn', value: 'shorter', comment: 'làm ngắn hơn và súc tích hơn' },
	{ label: '📖 Chi tiết hơn', value: 'detailed', comment: 'thêm chi tiết và mở rộng nội dung' },
	{ label: '😊 Thân thiện hơn', value: 'friendly', comment: 'làm cho thân thiện và dễ tiếp cận hơn' },
	{ label: '🎯 Tập trung hơn', value: 'focused', comment: 'tập trung vào những điểm quan trọng nhất' }
])

// Alias for clarity
const formData = computed(() => props.formData || {})

// Provide data for Field components
provide('data', formData)
provide('doctype', 'ATS_JobOpening')
provide('preview', false)

// Validation
const validationErrors = computed(() => {
	const errors = []
	
	// Không có validation errors vì các trường này không bắt buộc trong doctype
	
	return errors
})

// Helper computed properties
const hasAnyContent = computed(() => {
	return formData.value.jo_job_description?.trim() || 
		   formData.value.jo_job_requirement?.trim() || 
		   formData.value.jo_job_benefits?.trim()
})

const isAnyGenerating = computed(() => {
	return generatingDescription.value || generatingRequirements.value || generatingBenefits.value
})

// AI Generation methods
const generateAllContent = async () => {
	if (!formData.value.jo_position) {
		createToast({
			title: __('Error'),
			text: __('Please select a position first'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
		return
	}

	// Set all generating flags
	generatingDescription.value = true
	generatingRequirements.value = true
	generatingBenefits.value = true
	
	try {
		// Build comments with custom description
		let comments = `Create a complete and professional job description for position: ${formData.value.jo_position}. Include detailed job description, candidate requirements and attractive benefits.`
		
		// Add refine style if selected
		if (selectedRefineStyle.value) {
			const selectedPreset = refinePresets.value.find(p => p.value === selectedRefineStyle.value)
			if (selectedPreset) {
				comments += ` Please ${selectedPreset.comment}.`
			}
		}
		
		// Add custom description if provided
		if (customDescription.value.trim()) {
			comments += ` Additional requirements: ${customDescription.value.trim()}`
		}

		// Use generate_job_description_v2 for initial generation
		const response = await call('go1_cms.api.ai.generate_job_description_v2', {
			jobTitle: formData.value.jo_position,
			tone: 'professional',
			comments: `Tạo bản mô tả công việc hoàn chỉnh và chuyên nghiệp cho vị trí: ${formData.value.jo_position}. Bao gồm mô tả chi tiết về công việc, yêu cầu ứng viên và quyền lợi hấp dẫn.`
		})

		// Update all fields from response
		const updates = {}
		if (response.jobDescription) {
			updates.jo_job_description = response.jobDescription
		}
		if (response.jobRequirements) {
			updates.jo_job_requirement = response.jobRequirements
		}
		if (response.jobResponsibilities) {
			updates.jo_job_benefits = response.jobResponsibilities
		}

		if (Object.keys(updates).length > 0) {
			emit('update:formData', updates)
			createToast({
				title: __('Success'),
				text: __('Complete job description generated successfully'),
				icon: 'check',
				iconClasses: 'text-green-600'
			})
		}
	} catch (error) {
		console.error('AI generation error:', error)
		createToast({
			title: __('Error'),
			text: __('Failed to generate complete job description. Please try again.'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
	} finally {
		generatingDescription.value = false
		generatingRequirements.value = false
		generatingBenefits.value = false
	}
}

const generateJobDescription = async () => {
	if (!formData.value.jo_position) {
		createToast({
			title: __('Error'),
			text: __('Please select a position first'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
		return
	}

	generatingDescription.value = true
	try {
		// Get comment based on selected style
		let baseComment = `Tạo mô tả công việc cho vị trí: ${formData.value.jo_position}. Bao gồm về vai trò, trách nhiệm chính, và tầm quan trọng của vị trí trong tổ chức.`
		
		if (selectedRefineStyle.value) {
			const selectedPreset = refinePresets.value.find(p => p.value === selectedRefineStyle.value)
			if (selectedPreset) {
				baseComment += ` Hãy ${selectedPreset.comment}.`
			}
		}

		// Add custom description if provided
		if (customDescription.value.trim()) {
			baseComment += ` Additional requirements: ${customDescription.value.trim()}`
		}

		// Prepare current JD data for refinement
		const originalJD = {
			jobDescription: formData.value.jo_job_description || `Mô tả công việc cho vị trí: ${formData.value.jo_position}`,
			jobRequirements: formData.value.jo_job_requirement || '',
			jobResponsibilities: formData.value.jo_job_benefits || ''
		}

		const response = await call('go1_cms.api.ai.jd_section_refine', {
			originalJD: originalJD,
			fieldsToRewrite: ['jobDescription'],
			comments: baseComment
		})

		if (response && response.jobDescription) {
			emit('update:formData', { jo_job_description: response.jobDescription })
			createToast({
				title: __('Success'),
				text: selectedRefineStyle.value ? 
					__(`Job description generated with ${refinePresets.value.find(p => p.value === selectedRefineStyle.value)?.label.toLowerCase()}`) :
					__('Job description generated successfully'),
				icon: 'check',
				iconClasses: 'text-green-600'
			})
		}
	} catch (error) {
		console.error('AI generation error:', error)
		createToast({
			title: __('Error'),
			text: __('Failed to generate job description. Please try again.'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
	} finally {
		generatingDescription.value = false
	}
}

const generateJobRequirements = async () => {
	if (!formData.value.jo_position) {
		createToast({
			title: __('Error'),
			text: __('Please select a position first'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
		return
	}

	generatingRequirements.value = true
	try {
		// Get comment based on selected style
		let baseComment = `Tạo yêu cầu ứng viên cho vị trí: ${formData.value.jo_position}. Bao gồm trình độ học vấn, kinh nghiệm, kỹ năng chuyên môn, kỹ năng mềm và phẩm chất cá nhân cần thiết.`
		
		if (selectedRefineStyle.value) {
			const selectedPreset = refinePresets.value.find(p => p.value === selectedRefineStyle.value)
			if (selectedPreset) {
				baseComment += ` Hãy ${selectedPreset.comment}.`
			}
		}

		// Add custom description if provided
		if (customDescription.value.trim()) {
			baseComment += ` Additional requirements: ${customDescription.value.trim()}`
		}

		// Prepare current JD data for refinement
		const originalJD = {
			jobDescription: formData.value.jo_job_description || '',
			jobRequirements: formData.value.jo_job_requirement || `Yêu cầu ứng viên cho vị trí: ${formData.value.jo_position}`,
			jobResponsibilities: formData.value.jo_job_benefits || ''
		}

		const response = await call('go1_cms.api.ai.jd_section_refine', {
			originalJD: originalJD,
			fieldsToRewrite: ['jobRequirements'],
			comments: baseComment
		})

		if (response && response.jobRequirements) {
			emit('update:formData', { jo_job_requirement: response.jobRequirements })
			createToast({
				title: __('Success'),
				text: selectedRefineStyle.value ? 
					__(`Job requirements generated with ${refinePresets.value.find(p => p.value === selectedRefineStyle.value)?.label.toLowerCase()}`) :
					__('Job requirements generated successfully'),
				icon: 'check',
				iconClasses: 'text-green-600'
			})
		}
	} catch (error) {
		console.error('AI generation error:', error)
		createToast({
			title: __('Error'),
			text: __('Failed to generate job requirements. Please try again.'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
	} finally {
		generatingRequirements.value = false
	}
}

const generateJobBenefits = async () => {
	if (!formData.value.jo_position) {
		createToast({
			title: __('Error'),
			text: __('Please select a position first'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
		return
	}

	generatingBenefits.value = true
	try {
		// Get comment based on selected style
		let baseComment = `Tạo phần quyền lợi và phúc lợi hấp dẫn cho vị trí: ${formData.value.jo_position}. Bao gồm mức lương, bảo hiểm, cân bằng công việc-cuộc sống, cơ hội phát triển, văn hóa công ty và các phúc lợi khác.`
		
		if (selectedRefineStyle.value) {
			const selectedPreset = refinePresets.value.find(p => p.value === selectedRefineStyle.value)
			if (selectedPreset) {
				baseComment += ` Hãy ${selectedPreset.comment}.`
			}
		}

		// Add custom description if provided
		if (customDescription.value.trim()) {
			baseComment += ` Additional requirements: ${customDescription.value.trim()}`
		}

		// Prepare current JD data for refinement
		const originalJD = {
			jobDescription: formData.value.jo_job_description || '',
			jobRequirements: formData.value.jo_job_requirement || '',
			jobResponsibilities: formData.value.jo_job_benefits || `Quyền lợi và phúc lợi cho vị trí: ${formData.value.jo_position}`
		}

		const response = await call('go1_cms.api.ai.jd_section_refine', {
			originalJD: originalJD,
			fieldsToRewrite: ['jobResponsibilities'],
			comments: baseComment
		})

		if (response && response.jobResponsibilities) {
			emit('update:formData', { jo_job_benefits: response.jobResponsibilities })
			createToast({
				title: __('Success'),
				text: selectedRefineStyle.value ? 
					__(`Job benefits generated with ${refinePresets.value.find(p => p.value === selectedRefineStyle.value)?.label.toLowerCase()}`) :
					__('Job benefits generated successfully'),
				icon: 'check',
				iconClasses: 'text-green-600'
			})
		}
	} catch (error) {
		console.error('AI generation error:', error)
		createToast({
			title: __('Error'),
			text: __('Failed to generate job benefits. Please try again.'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
	} finally {
		generatingBenefits.value = false
	}
}

// Refine functions
const executeRefine = async () => {
	if (!selectedRefineStyle.value) return
	
	// Find the selected preset
	const selectedPreset = refinePresets.value.find(p => p.value === selectedRefineStyle.value)
	if (!selectedPreset) return
	
	const comment = selectedPreset.comment

	// Add custom description if provided
	if (customDescription.value.trim()) {
		comment += `. Additional requirements: ${customDescription.value.trim()}`
	}
	const fieldsToRefine = []
	
	// Determine which fields have content to refine
	if (formData.value.jo_job_description?.trim()) fieldsToRefine.push('jobDescription')
	if (formData.value.jo_job_requirement?.trim()) fieldsToRefine.push('jobRequirements')
	if (formData.value.jo_job_benefits?.trim()) fieldsToRefine.push('jobResponsibilities')
	
	if (fieldsToRefine.length === 0) {
		createToast({
			title: __('Warning'),
			text: __('No content to refine. Please generate content first.'),
			icon: 'alert-triangle',
			iconClasses: 'text-yellow-600'
		})
		return
	}
	
	// Set all generating flags to prevent multiple calls
	generatingDescription.value = true
	generatingRequirements.value = true
	generatingBenefits.value = true
	
	try {
		const originalJD = {
			jobDescription: formData.value.jo_job_description || '',
			jobRequirements: formData.value.jo_job_requirement || '',
			jobResponsibilities: formData.value.jo_job_benefits || ''
		}

		const response = await call('mbw_ats.api.ai.jd_section_refine', {
			originalJD: originalJD,
			fieldsToRewrite: fieldsToRefine,
			comments: comment
		})

		// Update fields based on response
		const updates = {}
		if (response.jobDescription && fieldsToRefine.includes('jobDescription')) {
			updates.jo_job_description = response.jobDescription
		}
		if (response.jobRequirements && fieldsToRefine.includes('jobRequirements')) {
			updates.jo_job_requirement = response.jobRequirements
		}
		if (response.jobResponsibilities && fieldsToRefine.includes('jobResponsibilities')) {
			updates.jo_job_benefits = response.jobResponsibilities
		}

		if (Object.keys(updates).length > 0) {
			emit('update:formData', updates)
			createToast({
				title: __('Success'),
				text: __(`Content refined with ${selectedPreset.label.toLowerCase()}`),
				icon: 'check',
				iconClasses: 'text-green-600'
			})
			selectedRefineStyle.value = '' // Reset selection after success
		}
	} catch (error) {
		console.error('AI refine error:', error)
		createToast({
			title: __('Error'),
			text: __('Failed to refine content. Please try again.'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
	} finally {
		generatingDescription.value = false
		generatingRequirements.value = false
		generatingBenefits.value = false
	}
}

// Removed deep watch to prevent recursive updates
// Changes are handled by Field components through provide/inject
</script> 