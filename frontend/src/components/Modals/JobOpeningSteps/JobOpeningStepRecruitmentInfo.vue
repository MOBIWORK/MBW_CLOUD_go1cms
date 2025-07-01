<template>
	<div class="space-y-6">
		<div class="text-center">
			<h3 class="text-lg font-medium mb-2">{{ __('Recruitment Information') }}</h3>
			<p class="text-gray-600 mb-6">
				{{ __('Configure recruitment details and application requirements') }}
			</p>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<!-- Location -->
			<div class="md:col-span-2">
				<Field
					:field="{
						fieldname: 'jo_location',
						fieldtype: 'Link',
						label: 'Work Location',
						options: 'ATS_Location',
						placeholder: 'Select work location',
						visible: true
					}"
				/>
			</div>

			<!-- Work Form -->
			<div>
				<Field
					:field="{
						fieldname: 'jo_work_form',
						fieldtype: 'Select',
						label: 'Work Type',
						options: workFormOptions,
						placeholder: 'Select work type',
						visible: true
					}"
				/>
			</div>

			<!-- Display Quantity -->
			<div>
				<Field
					:field="{
						fieldname: 'jo_display_quantity',
						fieldtype: 'Int',
						label: 'Number of Positions',
						placeholder: 'Enter number of positions to hire',
						visible: true
					}"
				/>
			</div>

			<!-- Language Requirement -->
			<div class="md:col-span-2">
				<Field
					:field="{
						fieldname: 'jo_language_requirement',
						fieldtype: 'Small Text',
						label: 'Language Requirements',
						placeholder: 'e.g. English (Fluent), Vietnamese (Native)',
						visible: true
					}"
				/>
			</div>

			<!-- Application Deadline -->
			<div>
				<Field
					:field="{
						fieldname: 'jo_application_deadline',
						fieldtype: 'Date',
						label: 'Application Deadline',
						placeholder: 'Select deadline',
						visible: true
					}"
				/>
			</div>

			<!-- Urgent Hiring Toggle -->
			<div class="flex items-center justify-center">
				<div class="bg-orange-50 border border-orange-200 rounded-lg p-4 w-full">
					<div class="flex items-center space-x-3">
						<div class="flex-shrink-0">
							<FeatherIcon name="clock" class="h-5 w-5 text-orange-500" />
						</div>
						<div class="flex-1">
							<label class="flex items-center cursor-pointer">
								<input 
									type="checkbox" 
									v-model="isUrgentHiring" 
									class="rounded border-gray-300 text-orange-600 focus:ring-orange-500"
								>
								<span class="ml-2 text-sm font-medium text-gray-900">
									{{ __('Urgent Hiring') }}
								</span>
							</label>
							<p class="text-xs text-gray-600 mt-1">
								{{ __('Mark this position as urgent to prioritize applications') }}
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Quick Deadline Options -->
		<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
			<h4 class="text-sm font-medium text-blue-900 mb-3">{{ __('Quick Deadline Options') }}</h4>
			<div class="grid grid-cols-2 md:grid-cols-4 gap-2">
				<Button
					v-for="option in deadlineOptions"
					:key="option.days"
					size="sm"
					variant="outline"
					theme="blue"
					@click="setDeadline(option.days)"
					class="text-xs"
				>
					{{ __(option.label) }}
				</Button>
			</div>
		</div>

		<!-- Application Statistics Preview -->
		<div v-if="showStats" class="bg-gray-50 border border-gray-200 rounded-lg p-4">
			<h4 class="text-sm font-medium text-gray-900 mb-3">{{ __('Expected Application Volume') }}</h4>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
				<div class="text-center">
					<div class="text-2xl font-bold text-blue-600">{{ estimatedApplications.low }}-{{ estimatedApplications.high }}</div>
					<div class="text-xs text-gray-600">{{ __('Expected Applications') }}</div>
				</div>
				<div class="text-center">
					<div class="text-2xl font-bold text-green-600">{{ daysUntilDeadline }}</div>
					<div class="text-xs text-gray-600">{{ __('Days to Apply') }}</div>
				</div>
				<div class="text-center">
					<div class="text-2xl font-bold text-purple-600">{{ recommendedInterviews }}</div>
					<div class="text-xs text-gray-600">{{ __('Recommended Interviews') }}</div>
				</div>
			</div>
		</div>

		<!-- Toggle Stats -->
		<div class="text-center">
			<Button
				variant="outline"
				size="sm"
				@click="showStats = !showStats"
			>
				<template #prefix>
					<FeatherIcon name="bar-chart-2" class="h-4 w-4" />
				</template>
				{{ showStats ? __('Hide Stats') : __('Show Stats') }}
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
import { computed, provide, watch, ref, onMounted } from 'vue'
import { FeatherIcon, Button } from 'frappe-ui'

const props = defineProps({
	formData: {
		type: Object,
		required: true
	}
})

const emit = defineEmits(['update:formData'])

const showStats = ref(false)
const isUrgentHiring = ref(false)

// Alias for clarity
const formData = computed(() => props.formData || {})

// Provide data for Field components
provide('data', formData)
provide('doctype', 'ATS_JobOpening')
provide('preview', false)

// Options
const workFormOptions = [
	{ label: '', value: '' },
	{ label: 'Full-Time', value: 'Full-Time' },
	{ label: 'Part-Time', value: 'Part-Time' },
	{ label: 'Temporary Contract', value: 'Temporary Contract' },
	{ label: 'Intern', value: 'Intern' },
	{ label: 'Collaborator', value: 'Collaborator' }, 
	{ label: 'Freelance', value: 'Freelance' },
]

const deadlineOptions = [
	{ label: '1 Week', days: 7 },
	{ label: '2 Weeks', days: 14 },
	{ label: '1 Month', days: 30 },
	{ label: '2 Months', days: 60 }
]

// Computed properties
const daysUntilDeadline = computed(() => {
	if (!formData.value.jo_application_deadline) return 0
	const deadline = new Date(formData.value.jo_application_deadline)
	const today = new Date()
	const diffTime = Math.abs(deadline - today)
	return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
})

const estimatedApplications = computed(() => {
	const baseApplications = 20
	const locationMultiplier = formData.value.jo_location?.includes('Ho Chi Minh') ? 1.5 : 1
	const urgencyMultiplier = isUrgentHiring.value ? 1.3 : 1
	const timeMultiplier = daysUntilDeadline.value > 30 ? 1.2 : daysUntilDeadline.value < 7 ? 0.7 : 1
	
	const base = Math.round(baseApplications * locationMultiplier * urgencyMultiplier * timeMultiplier)
	return {
		low: Math.max(base - 10, 5),
		high: base + 15
	}
})

const recommendedInterviews = computed(() => {
	const avgApplications = (estimatedApplications.value.low + estimatedApplications.value.high) / 2
	return Math.max(Math.round(avgApplications * 0.2), 3)
})

// Validation
const validationErrors = computed(() => {
	const errors = []
	
	// Không có validation errors vì các trường này không bắt buộc trong doctype
	
	return errors
})

// Methods
const setDeadline = (days) => {
	const deadline = new Date()
	deadline.setDate(deadline.getDate() + days)
	const formattedDate = deadline.toISOString().split('T')[0]
	emit('update:formData', { jo_application_deadline: formattedDate })
}

// Watch for urgent hiring changes
watch(isUrgentHiring, (newValue) => {
	if (newValue && !formData.value.jo_application_deadline) {
		// Set default deadline to 2 weeks for urgent hiring
		setDeadline(14)
	}
})

// Set default deadline khi component mount
onMounted(() => {
	// Chỉ set default nếu chưa có deadline
	if (!formData.value.jo_application_deadline) {
		const defaultDeadline = new Date()
		defaultDeadline.setMonth(defaultDeadline.getMonth() + 1) // 1 tháng từ hôm nay
		const formattedDate = defaultDeadline.toISOString().split('T')[0]
		emit('update:formData', { jo_application_deadline: formattedDate })
	}
})

// Removed deep watch to prevent recursive updates
// Changes are handled by Field components through provide/inject
</script> 