<template>
	<div class="space-y-1.5">
		<label class="block" :class="labelClasses" v-if="attrs.label">
			{{ __(attrs.label) }}
		</label>
		<!-- <Autocomplete
			:options="options"
			v-model="people"
			placeholder="Select people"
			multiple="true"
		/> -->
		<div class="flex items-center gap-2 border p-[6px] rounded w-full">
			<!-- <MultiselectInput class="flex-1" v-model="toEmails" v-model:options="options" /> -->
			<div class="w-full">
				<div class="flex flex-wrap gap-1 w-full">
					<Button
						ref="emails"
						v-for="value in toEmails"
						:key="value"
						:label="value"
						theme="gray"
						variant="subtle"
						class="rounded"
						@keydown.delete.capture.stop="removeLastValue"
					>
						<template #suffix>
							<FeatherIcon class="h-3.5" name="x" @click.stop="removeValue(value)" />
						</template>
					</Button>
					<div class="flex-1">
						<Combobox v-model="selectedValue" nullable>
							<Popover class="" v-model:show="showOptions">
								<template #target="{ togglePopover }">
									<ComboboxInput
										ref="search"
										class="search-input form-input w-full border-none bg-white hover:bg-white focus:border-none focus:!shadow-none focus-visible:!ring-0"
										type="text"
										:value="query"
										@change="
											(e) => {
												query = e.target.value
												showOptions = true
											}
										"
										autocomplete="off"
										@focus="() => togglePopover()"
										:place
										@keydown.delete.capture.stop="removeLastValue"
									/>
								</template>
								<template #body="{ isOpen }">
									<div v-show="isOpen">
										<div class="mt-1 rounded-lg bg-white py-1 text-base shadow-2xl w-fit max-w-full">
											<ComboboxOptions class="my-1 max-h-[12rem] overflow-y-auto px-1.5" static>
												<ComboboxOption
													v-for="option in options"
													:key="option.value"
													:value="option"
													v-slot="{ active }"
												>
													<li
														:class="[
															'flex cursor-pointer items-center px-2 py-1 text-base border-b',
															{ 'bg-gray-100': active },
														]"
													>
														<div class="flex flex-col gap-1 p-1 text-gray-800">
															<div class="text-base font-medium">
																{{ option.label }}
															</div>
														</div>
													</li>
												</ComboboxOption>
											</ComboboxOptions>
										</div>
									</div>
								</template>
							</Popover>
						</Combobox>
					</div>
				</div>
				<ErrorMessage class="mt-2 pl-2" v-if="error" :message="error" />
			</div>
		</div>
	</div>
</template>

<script setup>
import { watchDebounced } from "@vueuse/core"
import { createResource, call, Autocomplete } from "frappe-ui"
import { useAttrs, computed, ref, onMounted, nextTick } from "vue"
import MultiselectInput from "./MultiselectInput.vue"
import { validateEmail } from "@/utils"
import { Combobox, ComboboxInput, ComboboxOptions, ComboboxOption } from "@headlessui/vue"
import Popover from "@/components/frappe-ui/Popover.vue"

const props = defineProps({
	doctype: {
		type: String,
		required: true,
	},
	filters: {
		type: Array,
		default: () => [],
	},
	modelValue: {
		type: String,
		default: "",
	},
	hideMe: {
		type: Boolean,
		default: false,
	},
	value: {
		type: Array,
		default: () => [],
	},
	parentDoc: {
		type: String,
		default: "",
	},
	name: {
		type: String,
		default: "",
	},
	parentName: {
		type: String,
		default: "",
	},
})

const people = ref([])


const emit = defineEmits(["update:modelValue", "change"])

const attrs = useAttrs()

const valuePropPassed = computed(() => "value" in attrs)

const autocomplete = ref(null)
const text = ref("")
const data = ref([]) // Thay thế `options.data` bằng `data`
const linkedFieldss = ref([]) // Thay thế `options.linkedFields` bằng `linkedFields`

const toEmails = ref([])
const options = ref([])
const emails = ref([])
const search = ref(null)
const error = ref(null)
const query = ref("")
const showOptions = ref(false)
const activeField = ref("")

const selectedValue = computed({
	get: () => query.value || "",
	set: (val) => {
		query.value = ""
		if (val) {
			showOptions.value = false
		}
		val?.value && addValue(val.value)
	},
})

// Lấy Doctype liên kết động
function getLinkedDoctype(currentDoctype) {
	return createResource({
		url: "go1_cms.api.multiselect.get_linked_fields",
		params: { doctype: currentDoctype },
		cache: false,
		auto: true,
		onSuccess: (response) => {
			activeField.value = response[0].fieldname

			for (const field of response) {


				// Lấy danh sách các bản ghi từ bảng liên kết
				const intermediateData = createResource({
					url: "frappe.client.get_list",
					cache: false,
					params: {
						doctype: field.options,
						fields: [field.fieldname],
					},
					onSuccess: (response) => {
						console.log(response)
					},
				})

				intermediateData.fetch()

				// Xử lý dữ liệu liên kết

				toEmails.value = props.value.map((item) => item[field.fieldname])

				// Gọi API tìm kiếm liên kết
				const finalData = createResource({
					url: "frappe.desk.search.search_link",
					method: "POST",
					cache: false,
					params: {
						txt: "",
						doctype: field.options,
						filters: [],
					},
					onSuccess: (response) => {

						options.value.push(
							...response.map((item) => ({
								label: item.value,
								value: item.value,
							}))
						)
					},
				})

				finalData.fetch()
			}
		},
	})
}

const getlistData = () => {
	return createResource({
		url: "frappe.client.get_list",
		cache: [props.doctype, props.filters],
		params: {
			doctype: props.doctype,
			fields: ["name"],
			filters: props.filters,
		},
	})
}

async function reload(val = "") {
	try {
		// Xóa dữ liệu cũ trước khi reload
		data.value = []
		// Lấy thông tin liên kết động
		await getLinkedDoctype(props.doctype)

		// Xử lý từng trường liên kết
		// for (const field of linkedFieldss?.value) {

		// 	console.log(field)

		// 	// Lấy danh sách các bản ghi từ bảng liên kết
		// 	const intermediateData = await createResource({
		// 		url: "frappe.client.get_list",
		// 		cache: false,
		// 		params: {
		// 			doctype: field.options,
		// 			fields: [field.fieldname],
		// 		},
		// 	}).fetch()

		// 	if (!intermediateData.data) {
		// 		console.warn(`Không có dữ liệu từ bảng: ${field.options}`)
		// 		continue
		// 	}

		// 	// Xử lý dữ liệu liên kết
		// 	const linkedValues = intermediateData.data.map((item) => item[field.fieldname])

		// 	// Gọi API tìm kiếm liên kết
		// 	const finalData = await createResource({
		// 		url: "frappe.desk.search.search_link",
		// 		method: "POST",
		// 		cache: false,
		// 		params: {
		// 			txt: val,
		// 			doctype: field.options,
		// 			filters: [],
		// 		},
		// 	}).fetch()

		// 	if (finalData.data) {
		// 		allData.push(
		// 			...finalData.data.map((item) => ({
		// 				label: item.value,
		// 				value: item.value,
		// 			}))
		// 		)
		// 	}
		// }

		// Cập nhật danh sách hiển thị
		// options.value = allData
		// data.value = allData
	} catch (error) {
		console.error("Lỗi khi tải dữ liệu:", error)
	}
}

function clearValue(close) {
	emit(valuePropPassed.value ? "change" : "update:modelValue", "")
	close()
}

onMounted(() => {
	reload("")
})

const labelClasses = computed(() => {
	return [
		{
			sm: "text-xs",
			md: "text-base",
		}[attrs.size || "sm"],
		"text-gray-600",
	]
})

const addValue = (value) => {
	error.value = null
	if (value) {
		const splitValues = value.split(",")
		splitValues.forEach((value) => {
			value = value.trim()
			if (value) {
				// check if value is not already in the values array
				if (!toEmails.value?.includes(value)) {
					// add value to values array
					if (!toEmails.value) {
						toEmails.value = [value]
					} else {
						toEmails.value.push(value)
						callInsertDoc(value)
					}
					value = value.replace(value, "")
				}
			}
		})
		!error.value && (value = "")
	}
}

const removeValue = (value) => {
	toEmails.value = toEmails.value.filter((v) => v !== value)
	const childName = props.value.find((item) => item[activeField.value] === value).name
	deleteChildResource(childName)
}

const removeLastValue = () => {
	if (query.value) return

	let emailRef = emails.value[emails.value.length - 1]?.$el
	if (document.activeElement === emailRef) {
		toEmails.value.pop()
		nextTick(() => {
			if (toEmails.value.length) {
				emailRef = emails.value[emails.value.length - 1].$el
				emailRef?.focus()
			} else {
				setFocus()
			}
		})
	} else {
		emailRef?.focus()
	}
}

function setFocus() {
	search.value.$el.focus()
}

function deleteChildResource(childName) {
	// Tạo resource cho việc xóa
	const resource = createResource({
		url: "mbw_recruitment.api.doc.delete_child_record", // API URL
		method: "POST", // Phương thức HTTP POST
		params: {
			parent_doctype: props.parentDoc,
			parent_name: props.parentName,
			child_table_field: props.name,
			child_name: childName,
		},
		onSuccess: (response) => {
			console.log("Xóa thành công:", response)
		},
		onError: (error) => {
			console.error("Lỗi khi xóa:", error)
		},
		auto: false, // Không tự động gọi, chỉ gọi khi cần
	})
	// Gọi API xóa bản ghi
	resource.fetch()
}

async function callInsertDoc(value) {
	const doc = await call("frappe.client.insert", {
		doc: {
			doctype: props.doctype,
			[activeField.value]: value,
			parenttype: props.parentDoc, // Tên của Doctype cha
			parent: props.parentName, // Tên của bản ghi cha
			parentfield: props.name, // Trường trong Doctype cha liên kết với bảng con
		},
	})
	if (doc.name) {
		// capture("contact_created")
		// handleContactUpdate(doc)
		// createToast({
		// 	title: __("Thêm bản ghi thành công"),
		// 	icon: "check",
		// 	iconClasses: "text-green-600",
		// })

		emit("change", doc)
	} else {
		// createToast({
		// 	title: __("Co loi xay ra"),
		// 	icon: "x",
		// 	iconClasses: "text-red-600",
		// })
		console.log("Co loi xay ra")
	}
}
</script>
