<template>
	<div class="space-y-6">
		<div class="text-center">
			<h3 class="text-lg font-medium mb-2">{{ __('Contact Information') }}</h3>
			<p class="text-gray-600 mb-6">
				{{ __('Set up recruiter contact details for candidate inquiries') }}
			</p>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<!-- Contact Person -->
			<div class="md:col-span-2">
				<Field
					:field="{
						fieldname: 'jo_contact_person',
						fieldtype: 'Data',
						label: 'Contact Person',
						placeholder: 'Enter recruiter name',
						visible: true
					}"
				/>
			</div>

			<!-- Contact Email -->
			<div>
				<Field
					:field="{
						fieldname: 'jo_contact_email',
						fieldtype: 'Data',
						label: 'Contact Email',
						placeholder: 'Enter contact email',
						visible: true
					}"
				/>
			</div>

			<!-- Contact Phone -->
			<div>
				<Field
					:field="{
						fieldname: 'jo_contact_phone',
						fieldtype: 'Data',
						label: 'Contact Phone',
						placeholder: 'Enter contact phone number',
						visible: true
					}"
				/>
			</div>
		</div>

		<!-- Use Current User Info -->
		<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
			<div class="flex items-start space-x-3">
				<FeatherIcon name="user" class="h-5 w-5 text-blue-500 mt-0.5" />
				<div class="flex-1">
					<p class="text-sm font-medium text-blue-900">{{ __('Use My Information') }}</p>
					<p class="text-xs text-blue-700 mt-1">
						{{ __('Automatically fill contact details with your profile information') }}
					</p>
					<div class="mt-3">
						<Button
							size="sm"
							variant="solid"
							theme="blue"
							@click="useCurrentUserInfo"
							:loading="loadingUserInfo"
						>
							<template #prefix>
								<FeatherIcon name="copy" class="h-3 w-3" />
							</template>
							{{ __('Use My Info') }}
						</Button>
					</div>
				</div>
			</div>
		</div>

		<!-- Contact Preview Card -->
		<div v-if="hasContactInfo" class="bg-gray-50 border border-gray-200 rounded-lg p-4">
			<h4 class="text-sm font-medium text-gray-900 mb-3">{{ __('Contact Card Preview') }}</h4>
			<div class="bg-white border rounded-lg p-4 shadow-sm">
				<div class="flex items-start space-x-3">
					<div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
						<FeatherIcon name="user" class="h-6 w-6 text-blue-600" />
					</div>
					<div class="flex-1">
						<h5 class="font-medium text-gray-900">{{ formData.jo_contact_person }}</h5>
						<p class="text-sm text-gray-600">{{ __('Recruiter') }}</p>
						<div class="mt-2 space-y-1">
							<div v-if="formData.jo_contact_email" class="flex items-center text-sm text-gray-600">
								<FeatherIcon name="mail" class="h-4 w-4 mr-2" />
								{{ formData.jo_contact_email }}
							</div>
							<div v-if="formData.jo_contact_phone" class="flex items-center text-sm text-gray-600">
								<FeatherIcon name="phone" class="h-4 w-4 mr-2" />
								{{ formData.jo_contact_phone }}
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Contact Guidelines -->
		<div class="bg-green-50 border border-green-200 rounded-lg p-4">
			<h4 class="text-sm font-medium text-green-900 mb-3">{{ __('Contact Best Practices') }}</h4>
			<div class="space-y-2 text-sm text-green-800">
				<div class="flex items-start space-x-2">
					<FeatherIcon name="check-circle" class="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
					<span>{{ __('Use a professional email address that candidates can easily reach') }}</span>
				</div>
				<div class="flex items-start space-x-2">
					<FeatherIcon name="check-circle" class="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
					<span>{{ __('Provide a phone number for urgent inquiries or clarifications') }}</span>
				</div>
				<div class="flex items-start space-x-2">
					<FeatherIcon name="check-circle" class="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
					<span>{{ __('Ensure contact information is monitored regularly during application period') }}</span>
				</div>
				<div class="flex items-start space-x-2">
					<FeatherIcon name="check-circle" class="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
					<span>{{ __('Consider using a dedicated recruitment email for tracking purposes') }}</span>
				</div>
			</div>
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

const loadingUserInfo = ref(false)

// Alias for clarity
const formData = computed(() => props.formData || {})

// Provide data for Field components
provide('data', formData)
provide('doctype', 'ATS_JobOpening')
provide('preview', false)

// Computed properties
const hasContactInfo = computed(() => {
	return formData.value.jo_contact_person || formData.value.jo_contact_email || formData.value.jo_contact_phone
})

// Validation
const validationErrors = computed(() => {
	const errors = []
	
	// Chỉ validate email format nếu có nhập email
	if (formData.value.jo_contact_email?.trim() && !isValidEmail(formData.value.jo_contact_email)) {
		errors.push('Please enter a valid email address')
	}
	
	return errors
})

// Methods
const isValidEmail = (email) => {
	const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
	return emailRegex.test(email)
}

const useCurrentUserInfo = async () => {
	loadingUserInfo.value = true
	try {
		// Get current user information
		const response = await call('frappe.client.get_value', {
			doctype: 'User',
			fieldname: ['full_name', 'email', 'phone'],
			filters: { name: 'Administrator' } // Replace with actual current user
		})

		if (response) {
			const updates = {}
			if (response.full_name) {
				updates.jo_contact_person = response.full_name
			}
			if (response.email) {
				updates.jo_contact_email = response.email
			}
			if (response.phone) {
				updates.jo_contact_phone = response.phone
			}

			if (Object.keys(updates).length > 0) {
				emit('update:formData', updates)
				createToast({
					title: __('Success'),
					text: __('Your information has been filled in'),
					icon: 'check',
					iconClasses: 'text-green-600'
				})
			}
		}
	} catch (error) {
		// Fallback with mock data
		const mockUserInfo = {
			jo_contact_person: 'John Doe',
			jo_contact_email: 'john.doe@company.com',
			jo_contact_phone: '+84 901 234 567'
		}
		
		emit('update:formData', mockUserInfo)
		createToast({
			title: __('Info Filled'),
			text: __('Contact information filled (demo mode)'),
			icon: 'check',
			iconClasses: 'text-green-600'
		})
	} finally {
		loadingUserInfo.value = false
	}
}

// Removed deep watch to prevent recursive updates
// Changes are handled by Field components through provide/inject
</script> 