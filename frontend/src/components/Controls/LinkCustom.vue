<template>
	<div class="space-y-1.5">
		<label class="block text-xs text-gray-600" v-if="attrs.label">
			{{ __(attrs.label) }}
		</label>
		<FormControl
			v-model="search"
			:placeholder="attrs.placeholder || __('Search...')"
			class="w-full"
		/>

		<!-- Danh sách kết quả -->
		<div v-if="filteredOptions.length > 0" class="mt-2 space-y-1 max-h-64 overflow-auto">
			<div
				v-for="option in filteredOptions"
				:key="option.value"
				class="flex items-center gap-2 p-2 cursor-pointer hover:bg-gray-100 rounded"
				@click="selectOption(option)"
			>
				<slot name="item-prefix" v-bind="{ option }" />
				<slot name="item-label" v-bind="{ option }">
					{{ option.label }}
				</slot>
			</div>
		</div>
		<div v-else class="text-sm text-gray-400 mt-2">{{ __("No results found") }}</div>
	</div>
</template>

<script setup>
import { ref, computed, useAttrs, watch } from "vue";
import { watchDebounced } from "@vueuse/core";
import { createToast, evaluate } from "@/utils";
import FormControl from "frappe-ui/src/components/FormControl.vue";
import { call } from "frappe-ui";

const props = defineProps({
	doctype: String,
	filters: {
		type: [Array, Object],
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
});

const emit = defineEmits(["update:modelValue", "change"]);
const attrs = useAttrs();

const search = ref("");
const options = ref([]);
const selected = ref(null);

// Hàm parse filters dạng Array -> Object
function parse_filters(link_filters) {
	if (Array.isArray(link_filters)) {
		let filters = {};
		link_filters.forEach(([_, fieldname, operator, value]) => {
			if (typeof value === "string" && value.startsWith("eval:")) {
				value = value.split("eval:")[1];
				let context = {};
				value = evaluate(value, context);
			}
			filters[fieldname] = [operator, value];
		});
		return filters;
	}
	return link_filters;
}

// Lấy dữ liệu từ API
async function fetchOptions(txt = "") {
	try {
		const res = await call("frappe.desk.search.search_link", {
			doctype: props.doctype,
			txt,
			filters: parse_filters(props.filters),
		});
        console.log(res)
		options.value = res.map((item) => ({
			label: item.value,
			value: item.value,
		}));
	} catch (err) {
		createToast({
			title: "Failed to load",
			text: err.message,
			icon: "x",
			iconClasses: "text-red-600",
		});
	}
}

watchDebounced(
	search,
	(val) => {
		fetchOptions(val);
	},
	{ debounce: 300, immediate: true },
);

function selectOption(option) {
	selected.value = option.value;
	emit("update:modelValue", option.value);
	emit("change", option.value);
}

const filteredOptions = computed(() => {
	return options.value;
});
</script>
