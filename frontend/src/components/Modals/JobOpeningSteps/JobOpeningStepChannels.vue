<template>
	<div class="space-y-6">
		<div class="text-center">
			<h3 class="text-lg font-medium mb-2">{{ __('Publishing Channels') }}</h3>
			<p class="text-gray-600 mb-6">
				{{ __('Choose where to publish your job opening for maximum visibility') }}
			</p>
		</div>

		<div class="space-y-6">
			<!-- Career Page -->
			<div class="bg-white border border-gray-200 rounded-lg p-4">
				<div class="flex items-start space-x-3">
					<div class="flex-shrink-0 mt-1">
						<input 
							type="checkbox" 
							v-model="formData.publish_to_career_page"
							:value="1"
							class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						>
					</div>
					<div class="flex-1">
						<div class="flex items-center space-x-2">
							<FeatherIcon name="globe" class="h-5 w-5 text-blue-600" />
							<h4 class="text-lg font-medium text-gray-900">{{ __('Company Career Page') }}</h4>
							<span class="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">{{ __('Recommended') }}</span>
						</div>
						<p class="text-sm text-gray-600 mt-1">
							{{ __('Display on your company\'s career page for direct applications') }}
						</p>
					</div>
				</div>
			</div>

			<!-- Facebook -->
			<div class="bg-white border border-gray-200 rounded-lg p-4">
				<div class="flex items-start space-x-3">
					<div class="flex-shrink-0 mt-1">
						<input 
							type="checkbox" 
							v-model="formData.publish_to_facebook"
							:value="1"
							class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						>
					</div>
					<div class="flex-1">
						<div class="flex items-center space-x-2">
							<FeatherIcon name="facebook" class="h-5 w-5 text-blue-600" />
							<h4 class="text-lg font-medium text-gray-900">{{ __('Facebook Page') }}</h4>
						</div>
						<p class="text-sm text-gray-600 mt-1">
							{{ __('Share on your company\'s Facebook page to reach social network') }}
						</p>
						<div v-if="formData.publish_to_facebook" class="mt-3">
							<Field
								:field="{
									fieldname: 'facebook_page_id',
									fieldtype: 'Data',
									label: 'Facebook Page ID',
									placeholder: 'Enter Facebook page ID',
									visible: true
								}"
							/>
						</div>
					</div>
				</div>
			</div>

			<!-- TopCV -->
			<div class="bg-white border border-gray-200 rounded-lg p-4">
				<div class="flex items-start space-x-3">
					<div class="flex-shrink-0 mt-1">
						<input 
							type="checkbox" 
							v-model="formData.publish_to_topcv"
							:value="1"
							class="rounded border-gray-300 text-green-600 focus:ring-green-500"
						>
					</div>
					<div class="flex-1">
						<div class="flex items-center space-x-2">
							<div class="w-5 h-5 bg-green-600 rounded flex items-center justify-center">
								<span class="text-white text-xs font-bold">T</span>
							</div>
							<h4 class="text-lg font-medium text-gray-900">{{ __('TopCV') }}</h4>
							<span class="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded">{{ __('Popular') }}</span>
						</div>
						<p class="text-sm text-gray-600 mt-1">
							{{ __('Post to TopCV job portal for wider candidate reach') }}
						</p>
					</div>
				</div>
			</div>

			<!-- LinkedIn -->
			<div class="bg-white border border-gray-200 rounded-lg p-4">
				<div class="flex items-start space-x-3">
					<div class="flex-shrink-0 mt-1">
						<input 
							type="checkbox" 
							v-model="formData.publish_to_linkedin"
							:value="1"
							class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						>
					</div>
					<div class="flex-1">
						<div class="flex items-center space-x-2">
							<FeatherIcon name="linkedin" class="h-5 w-5 text-blue-600" />
							<h4 class="text-lg font-medium text-gray-900">{{ __('LinkedIn') }}</h4>
							<span class="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">{{ __('Professional') }}</span>
						</div>
						<p class="text-sm text-gray-600 mt-1">
							{{ __('Share on LinkedIn for professional network exposure') }}
						</p>
					</div>
				</div>
			</div>

			<!-- Custom CMS URL -->
			<div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
				<h4 class="text-lg font-medium text-gray-900 mb-3">{{ __('Custom URL') }}</h4>
				<Field
					:field="{
						fieldname: 'job_url_cms',
						fieldtype: 'Data',
						label: 'Custom Job URL',
						placeholder: 'Enter custom job posting URL (optional)',
						visible: true
					}"
				/>
				<p class="text-xs text-gray-500 mt-2">
					{{ __('If you have a custom job posting page, enter the URL here') }}
				</p>
			</div>
		</div>

		<!-- Publishing Summary -->
		<div v-if="selectedChannels.length > 0" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
			<h4 class="text-sm font-medium text-blue-900 mb-3">{{ __('Publishing Summary') }}</h4>
			<div class="space-y-2">
				<div class="flex items-center justify-between text-sm">
					<span class="text-blue-800">{{ __('Selected Channels:') }}</span>
					<span class="font-medium text-blue-900">{{ selectedChannels.length }}</span>
				</div>
				<div class="text-xs text-blue-700">
					<span class="font-medium">{{ __('Channels:') }}</span> {{ selectedChannels.join(', ') }}
				</div>
				<div class="flex items-center text-xs text-blue-600">
					<FeatherIcon name="info" class="h-3 w-3 mr-1" />
					<span>{{ __('Publishing will happen automatically after job opening creation') }}</span>
				</div>
			</div>
		</div>

		<!-- Channel Performance Insights -->
		<div class="bg-purple-50 border border-purple-200 rounded-lg p-4">
			<h4 class="text-sm font-medium text-purple-900 mb-3">{{ __('Channel Performance Tips') }}</h4>
			<div class="space-y-2 text-sm text-purple-800">
				<div class="flex items-start space-x-2">
					<FeatherIcon name="target" class="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
					<span><strong>Career Page:</strong> {{ __('Best for employer branding and direct applications') }}</span>
				</div>
				<div class="flex items-start space-x-2">
					<FeatherIcon name="users" class="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
					<span><strong>Facebook:</strong> {{ __('Great for reaching passive candidates through social sharing') }}</span>
				</div>
				<div class="flex items-start space-x-2">
					<FeatherIcon name="search" class="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
					<span><strong>TopCV:</strong> {{ __('High volume of active job seekers in Vietnam') }}</span>
				</div>
				<div class="flex items-start space-x-2">
					<FeatherIcon name="briefcase" class="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
					<span><strong>LinkedIn:</strong> {{ __('Premium candidates for professional roles') }}</span>
				</div>
			</div>
		</div>

		<!-- Quick Actions -->
		<div class="flex flex-wrap gap-2">
			<Button
				size="sm"
				variant="outline"
				theme="blue"
				@click="selectAllChannels"
			>
				{{ __('Select All') }}
			</Button>
			<Button
				size="sm"
				variant="outline"
				theme="gray"
				@click="clearAllChannels"
			>
				{{ __('Clear All') }}
			</Button>
			<Button
				size="sm"
				variant="outline"
				theme="green"
				@click="selectRecommended"
			>
				{{ __('Recommended Only') }}
			</Button>
		</div>
	</div>
</template>

<script setup>
import Field from '@/components/FieldLayout/Field.vue'
import { computed, provide, watch } from 'vue'
import { FeatherIcon, Button } from 'frappe-ui'

const props = defineProps({
	formData: {
		type: Object,
		required: true
	}
})

const emit = defineEmits(['update:formData'])

// Alias for clarity
const formData = computed(() => props.formData || {})

// Provide data for Field components
provide('data', formData)
provide('doctype', 'ATS_JobOpening')
provide('preview', false)

// Computed properties
const selectedChannels = computed(() => {
	const channels = []
	
	if (formData.value.publish_to_career_page) {
		channels.push('Career Page')
	}
	if (formData.value.publish_to_facebook) {
		channels.push('Facebook')
	}
	if (formData.value.publish_to_topcv) {
		channels.push('TopCV')
	}
	if (formData.value.publish_to_linkedin) {
		channels.push('LinkedIn')
	}
	
	return channels
})

// Methods
const selectAllChannels = () => {
	const updates = {
		publish_to_career_page: 1,
		publish_to_facebook: 1,
		publish_to_topcv: 1,
		publish_to_linkedin: 1
	}
	emit('update:formData', updates)
}

const clearAllChannels = () => {
	const updates = {
		publish_to_career_page: 0,
		publish_to_facebook: 0,
		publish_to_topcv: 0,
		publish_to_linkedin: 0,
		facebook_page_id: ''
	}
	emit('update:formData', updates)
}

const selectRecommended = () => {
	const updates = {
		publish_to_career_page: 1,
		publish_to_facebook: 0,
		publish_to_topcv: 1,
		publish_to_linkedin: 0
	}
	emit('update:formData', updates)
}

// Removed deep watch to prevent recursive updates
// Changes are handled by Field components through provide/inject
</script> 