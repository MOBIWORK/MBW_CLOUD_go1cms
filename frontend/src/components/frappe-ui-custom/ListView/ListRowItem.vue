<template>
	<component
		:is="list.options.showTooltip ? Tooltip : 'div'"
		v-bind="list.options.showTooltip ? { text: label } : {}"
	>
		<div class="flex items-center space-x-2" :class="alignmentMap[align]">
			<slot name="prefix">
				<component
					v-if="column.prefix"
					:is="
						typeof column.prefix === 'function'
							? column.prefix({ row })
							: column.prefix
					"
				/>
			</slot>
			<slot v-bind="{ label }">
				<!-- {{ console.log(">>>>>>>>>>>>>>>>>>>>>>", column, label) }} -->
				<div v-if="column.key === 'cat_status'" class="cursor-pointer truncate">
					<Tooltip :text="label">
						<div
							v-if="label == 'Active'"
							@click="
								(event) => {
									applyDataFilter(event, 3, column, item);
								}
							"
						>
							<Badge
								:variant="'subtle'"
								theme="green"
								size="md"
								:label="__('Active')"
							/>
						</div>
						<div
							v-else
							@click="
								(event) => {
									applyDataFilter(event, 3, column, item);
								}
							"
						>
							<Badge
								:variant="'subtle'"
								theme="red"
								size="md"
								:label="__('Inactive')"
							/>
						</div>
					</Tooltip>
				</div>
				<div
					v-else-if="column.key === 'unit_name'"
					@click="
						(event) => {
							setChildTableField(props.row.name);
						}
					"
				>
					<Tooltip :text="label">
						<div class="flex items-center gap-2 truncate text-base cursor-pointer">
							<div v-if="label" class="truncate-text">
								{{ label }}
							</div>
						</div>
					</Tooltip>
				</div>
				<div
					v-else-if="column.key === 'unit_id'"
					@click="
						(event) => {
							setChildTableField(props.row.name);
						}
					"
				>
					<Tooltip :text="label">
						<div class="flex items-center gap-2 truncate text-base cursor-pointer">
							<div v-if="label" class="truncate-text">
								{{ label }}
							</div>
						</div>
					</Tooltip>
				</div>
				<div v-else class="truncate-text text-base">
					{{ column?.getLabel ? column.getLabel({ row }) : label }}
				</div>
			</slot>
			<slot name="suffix" />
		</div>
	</component>
</template>
<script setup>
import { computed, inject } from "vue";
import { Tooltip, Badge } from "frappe-ui";
import { alignmentMap } from "./utils";
import { useFieldStore } from "../../../stores/activeRecord";
import { useFilterStore } from "../../../stores/filter";

const filterStore = useFilterStore();
const fieldStore = useFieldStore();

const setChildTableField = (field) => {
	fieldStore.setChildTableField(field, "edit");
};

const props = defineProps({
	column: {
		type: Object,
		default: {},
	},
	row: {
		type: Object,
		default: {},
	},
	item: {
		type: [String, Number, Object],
		default: "",
	},
	align: {
		type: String,
		default: "left",
	},
});

const label = computed(() => {
	return getValue(props.item).label || "";
});

function getValue(value) {
	if (value && typeof value === "object") {
		return value;
	}
	return { label: value };
}

const list = inject("list");

const applyDataFilter = (event, index, column, item) => {
	console.log(event, index, column, item);
	filterStore.updateFilterData({ event, index, column, item });
};
</script>

<style scoped>
.truncate-text {
	overflow: hidden;
	white-space: nowrap;
	text-overflow: ellipsis;
	display: -webkit-box;
	-webkit-line-clamp: 1; /* Số dòng muốn hiển thị */
	-webkit-box-orient: vertical;
}
</style>
