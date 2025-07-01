<template>
	<div class="space-y-6">
		<div class="text-center">
			<h3 class="text-lg font-medium mb-2">{{ __('Salary & Benefits') }}</h3>
			<p class="text-gray-600 mb-6">
				{{ __('Set compensation details and how they should be displayed') }}
			</p>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<!-- Salary Display Option -->
			<div class="md:col-span-2">
				<label class="block text-sm font-medium text-gray-700 mb-2">
					{{ __('Salary Display Option') }}
				</label>
				<FormControl
					type="select"
					:options="salaryDisplayOptions"
					v-model="formData.jo_salary_display_option"
				/>
			</div>

			<!-- Currency -->
			<div>
				<label class="block text-sm font-medium text-gray-700 mb-2">
					{{ __('Currency') }}
				</label>
				<FormControl
					type="select"
					:options="currencyOptions"
					v-model="formData.jo_currency"
					:placeholder="__('Select currency')"
				/>
			</div>

			<!-- Min Salary -->
			<div v-if="formData.jo_salary_display_option === 'Details'">
				<Field
					:field="{
						fieldname: 'jo_min_salary',
						fieldtype: 'Currency',
						label: 'Minimum Salary',
						options: 'jo_currency',
						placeholder: 'Enter minimum salary',
						visible: true
					}"
				/>
			</div>

			<!-- Max Salary -->
			<div v-if="formData.jo_salary_display_option === 'Details'">
				<Field
					:field="{
						fieldname: 'jo_max_salary',
						fieldtype: 'Currency',
						label: 'Maximum Salary (Optional)',
						options: 'jo_currency',
						placeholder: 'Enter maximum salary for range',
						visible: true
					}"
				/>
			</div>
		</div>

		<!-- Salary Preview -->
		<div v-if="salaryPreview" class="bg-green-50 border border-green-200 rounded-lg p-4">
			<div class="flex items-start space-x-3">
				<FeatherIcon name="dollar-sign" class="h-5 w-5 text-green-500 mt-0.5" />
				<div>
					<p class="text-sm font-medium text-green-900">{{ __('Salary Display Preview') }}</p>
					<p class="text-lg font-semibold text-green-800 mt-1">{{ salaryPreview }}</p>
				</div>
			</div>
		</div>

		<!-- Salary Guidelines -->
		<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
			<h4 class="text-sm font-medium text-blue-900 mb-3">{{ __('Salary Display Guidelines') }}</h4>
			<div class="space-y-2 text-sm text-blue-800">
				<div class="flex items-start space-x-2">
					<FeatherIcon name="check-circle" class="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
					<span><strong>Details:</strong> {{ __('Hiển thị mức lương cụ thể (có thể là mức cố định hoặc khoảng lương)') }}</span>
				</div>
				<div class="flex items-start space-x-2">
					<FeatherIcon name="check-circle" class="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
					<span><strong>Agreement:</strong> {{ __('Lương theo thỏa thuận dựa trên kinh nghiệm và khả năng') }}</span>
				</div>
				<div class="flex items-start space-x-2">
					<FeatherIcon name="check-circle" class="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
					<span><strong>Form:</strong> {{ __('Ứng viên điền mức lương mong muốn vào form ứng tuyển') }}</span>
				</div>
			</div>
		</div>

		<!-- Market Rate Comparison -->
		<div v-if="showMarketRate && marketRateData" class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
			<div class="flex items-start space-x-3">
				<FeatherIcon name="trending-up" class="h-5 w-5 text-yellow-600 mt-0.5" />
				<div class="flex-1">
					<h4 class="text-sm font-medium text-yellow-900">{{ __('Market Rate Comparison') }}</h4>
					<div class="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
						<div class="text-center">
							<div class="font-semibold text-yellow-800">{{ formatCurrency(marketRateData.min) }}</div>
							<div class="text-yellow-600">{{ __('Market Min') }}</div>
						</div>
						<div class="text-center">
							<div class="font-semibold text-yellow-800">{{ formatCurrency(marketRateData.average) }}</div>
							<div class="text-yellow-600">{{ __('Market Average') }}</div>
						</div>
						<div class="text-center">
							<div class="font-semibold text-yellow-800">{{ formatCurrency(marketRateData.max) }}</div>
							<div class="text-yellow-600">{{ __('Market Max') }}</div>
						</div>
					</div>
					<div class="mt-2 text-xs text-yellow-700">
						{{ __('Based on similar positions in your area') }}
					</div>
				</div>
			</div>
		</div>

		<!-- Market Rate Toggle -->
		<div class="text-center">
			<Button
				variant="outline"
				size="sm"
				@click="toggleMarketRate"
				:loading="loadingMarketRate"
			>
				<template #prefix>
					<FeatherIcon name="bar-chart" class="h-4 w-4" />
				</template>
				{{ showMarketRate ? __('Hide Market Rate') : __('Show Market Rate') }}
			</Button>
		</div>
	</div>
</template>

<script setup>
import Field from '@/components/FieldLayout/Field.vue'
import { computed, provide, watch, ref, reactive } from 'vue'
import { FeatherIcon, Button, call, FormControl } from 'frappe-ui'
import { createToast } from '@/utils'

const props = defineProps({
	formData: {
		type: Object,
		required: true
	}
})

const emit = defineEmits(['update:formData'])

const showMarketRate = ref(false)
const loadingMarketRate = ref(false)
const marketRateData = ref(null)

// Reactive formData với default values
const formData = reactive({
	jo_currency: 'VND',
	...props.formData
})

// Watch để sync với props
watch(() => props.formData, (newData) => {
	Object.assign(formData, {
		jo_currency: 'VND',
		...newData
	})
}, { deep: true, immediate: true })

// Watch để emit changes
watch(formData, (newData) => {
	emit('update:formData', { ...newData })
}, { deep: true })

// Provide data for Field components
provide('data', formData)
provide('doctype', 'ATS_JobOpening')
provide('preview', false)

// Options - theo format cho FormControl
const salaryDisplayOptions = [
	{ label: '', value: '' },
	{ label: 'Details', value: 'Details' },
	{ label: 'Agreement', value: 'Agreement' },
	{ label: 'Form', value: 'Form' }
]

const currencyOptions = [
	{ label: 'VND', value: 'VND' },
	{ label: 'USD', value: 'USD' },
	{ label: 'EUR', value: 'EUR' }
]

// Computed properties
const salaryPreview = computed(() => {
	const option = formData.jo_salary_display_option
	const currency = formData.jo_currency || 'VND'
	const minSalary = formData.jo_min_salary
	const maxSalary = formData.jo_max_salary

	if (!option) return null

	switch (option) {
		case 'Details':
			if (minSalary && maxSalary) {
				return `${formatCurrency(minSalary, currency)} - ${formatCurrency(maxSalary, currency)}`
			} else if (minSalary) {
				return `${formatCurrency(minSalary, currency)}`
			}
			break
		case 'Agreement':
			return 'Salary: Theo thỏa thuận'
		case 'Form':
			return 'Salary: Điền vào form ứng tuyển'
	}

	return null
})

// Methods
const formatCurrency = (amount, currency = 'VND') => {
	if (!amount) return ''
	
	if (currency === 'VND') {
		return new Intl.NumberFormat('vi-VN').format(amount) + ' VND'
	} else if (currency === 'USD') {
		return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
	} else if (currency === 'EUR') {
		return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(amount)
	}
	
	return amount + ' ' + currency
}

const toggleMarketRate = async () => {
	if (showMarketRate.value) {
		showMarketRate.value = false
		return
	}

	if (!formData.jo_position) {
		createToast({
			title: __('Error'),
			text: __('Please select a position first'),
			icon: 'x',
			iconClasses: 'text-red-600'
		})
		return
	}

	loadingMarketRate.value = true
	try {
		// Mock API call for market rate data
		const response = await call('mbw_ats.api.salary.get_market_rate', {
			position: formData.jo_position,
			location: formData.jo_location,
			level: formData.jo_level_id
		})

		if (response) {
			marketRateData.value = response
		}
	} catch (error) {
		// Mock data for demo
		const baseSalary = 15000000 // 15M VND base
		marketRateData.value = {
			min: baseSalary * 0.8,
			average: baseSalary,
			max: baseSalary * 1.5,
			currency: 'VND'
		}
	} finally {
		loadingMarketRate.value = false
		showMarketRate.value = true
	}
}

// Watch for salary display option changes to trigger preview update
// watch(() => [
// 	formData.value.jo_salary_display_option,
// 	formData.value.jo_currency,
// 	formData.value.jo_min_salary,
// 	formData.value.jo_max_salary
// ], () => {
// 	// Trigger reactivity for salaryPreview computed
// }, { deep: false })
</script> 