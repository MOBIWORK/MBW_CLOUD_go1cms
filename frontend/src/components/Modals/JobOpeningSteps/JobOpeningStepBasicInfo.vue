<template>
	<div class="space-y-6">
		<div class="text-center">
			<h3 class="text-lg font-medium mb-2">{{ __('Basic Information') }}</h3>
			<p class="text-gray-600 mb-6">
				{{ __('Set up the essential details for your job opening') }}
			</p>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<!-- Position -->
			<div class="md:col-span-2">
				<Field
					:field="{
						fieldname: 'jo_position',
						fieldtype: 'Link',
						label: 'Position',
						options: 'ATS_Position',
						reqd: 1,
						placeholder: 'Select the position',
						visible: true
					}"
				/>
			</div>
			<!-- Public Title -->
			<div class="md:col-span-2">
				<Field
					:field="{
						fieldname: 'jo_public_title',
						fieldtype: 'Data',
						label: 'Job Title (Public)',
						reqd: 1,
						placeholder: 'e.g. Senior Software Engineer',
						visible: true
					}"
				/>
			</div>

			<!-- Internal Title -->
			<div class="md:col-span-2">
				<Field
					:field="{
						fieldname: 'jo_internal_title',
						fieldtype: 'Data',
						label: 'Internal Title',
						placeholder: 'Internal reference title (optional)',
						visible: true
					}"
				/>
			</div>

			<!-- Profession -->
			<div>
				<Field
					:field="{
						fieldname: 'jo_profession_id',
						fieldtype: 'Link',
						label: 'Profession/Industry',
						options: 'ATS_Profession',
						placeholder: 'Select profession',
						visible: true
					}"
				/>
			</div>

			<!-- Level -->
			<div>
				<Field
					:field="{
						fieldname: 'jo_level_id',
						fieldtype: 'Link',
						label: 'Job Level',
						options: 'ATS_Level',
						placeholder: 'Select job level',
						visible: true
					}"
				/>
			</div>

			<!-- Using Unit -->
			<div class="md:col-span-2">
				<Field
					:field="{
						fieldname: 'jo_using_unit',
						fieldtype: 'Link',
						label: 'Department/Unit',
						options: 'ATS_Unit',
						placeholder: 'Select department',
						visible: true
					}"
				/>
			</div>

			<!-- Department (additional field) -->
			<!-- <div class="md:col-span-2">
				<Field
					:field="{
						fieldname: 'jo_department',
						fieldtype: 'Data',
						label: 'Department (Additional)',
						placeholder: 'Additional department information',
						visible: true
					}"
				/>
			</div> -->
		</div>

		<!-- Template Loading Section -->
		<!-- <div v-if="formData.jo_position && !templateLoaded" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
			<div class="flex items-start space-x-3">
				<FeatherIcon name="info" class="h-5 w-5 text-blue-500 mt-0.5" />
				<div class="flex-1">
					<p class="text-sm font-medium text-blue-900">{{ __('Load Job Template') }}</p>
					<p class="text-xs text-blue-700 mt-1">
						{{ __('We found a template for this position. Would you like to load job description, requirements, and benefits?') }}
					</p>
					<div class="mt-3 flex space-x-2">
						<Button
							size="sm"
							variant="solid"
							theme="blue"
							@click="loadJobTemplate"
							:loading="loadingTemplate"
						>
							{{ __('Load Template') }}
						</Button>
						<Button
							size="sm"
							variant="outline"
							@click="templateLoaded = true"
						>
							{{ __('Skip') }}
						</Button>
					</div>
				</div>
			</div>
		</div> -->

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

const templateLoaded = ref(false)
const loadingTemplate = ref(false)

// Alias for clarity
const formData = computed(() => props.formData || {})

// Provide data for Field components
provide('data', formData)
provide('doctype', 'CMS_JobOpening')
provide('preview', false)

// Validation
const validationErrors = computed(() => {
	const errors = []
	
	if (!formData.value.jo_public_title?.trim()) {
		errors.push('Job Title (Public) is required')
	}
	
	if (!formData.value.jo_position?.trim()) {
		errors.push('Position is required')
	}
	
	return errors
})

// Load job template when position is selected
const loadJobTemplate = async () => {
	if (!formData.value.jo_position) return
	
	loadingTemplate.value = true
	try {
		const response = await call('frappe.client.get_value', {
			doctype: 'ATS_Position',
			fieldname: ['position_description', 'required_skills', 'position_benefits'],
			filters: { name: formData.value.jo_position }
		})

		if (response) {
			const updates = {}
			if (response.position_description && !formData.value.jo_job_description) {
				updates.jo_job_description = response.position_description
			}
			if (response.required_skills && !formData.value.jo_job_requirement) {
				updates.jo_job_requirement = response.required_skills
			}
			if (response.position_benefits && !formData.value.jo_job_benefits) {
				updates.jo_job_benefits = response.position_benefits
			}

			if (Object.keys(updates).length > 0) {
				emit('update:formData', updates)
				createToast({
					title: __('Template Loaded'),
					text: __('Job template has been loaded successfully'),
					icon: 'check',
					iconClasses: 'text-green-600'
				})
			}
		}
		
		templateLoaded.value = true
	} catch (error) {
		console.error('Error loading job template:', error)
		createToast({
			title: __('Error'),
			text: __('Failed to load job template'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
	} finally {
		loadingTemplate.value = false
	}
}

// Watch for position changes and auto-generate title
watch(() => formData.value.jo_position, (newPosition, oldPosition) => {
	if (newPosition && newPosition !== oldPosition) {
		console.log('👀 Position changed in BasicInfo:', newPosition)
		
		// Auto-mark template as loaded since main form handles loading
		templateLoaded.value = true
		
		// Don't auto-generate title here since main form handles it
		// if (!formData.value.jo_public_title) {
		// 	const updates = { jo_public_title: `Tuyển dụng ${newPosition}` }
		// 	emit('update:formData', updates)
		// }
	}
})
</script> 