<template>
	<component
		:is="list.options.getRowRoute ? 'router-link' : 'div'"
		:class="{ 'cursor-pointer': isHoverable }"
		class="flex flex-col transition-all duration-300 ease-in-out relative group"
		v-bind="{
			to: list.options.getRowRoute ? list.options.getRowRoute(row) : undefined,
			onClick: list.options.onRowClick ? () => list.options.onRowClick(row) : undefined,
		}"
	>
		<!-- Nút ở cuối hàng, hiển thị khi hover và cố định ở bên phải -->
		<div
			class="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 z-10 bg-white"
		>
			<!-- Nút của bạn -->
			<div class="flex gap-2">
				<!-- <Button
          :variant="'solid'"
          :ref_for="true"
          theme="gray"
          size="sm"
          label="Button"
          :loading="false"
          :loadingText="null"
          :disabled="false"
          :link="null"
          >
            Sửa
          </Button> -->

				<Dropdown :options="quickOptions(row)">
					<Button icon="more-vertical" class="text-gray-600" variant="ghost" />
				</Dropdown>
				<!-- <Button
          :variant="'solid'"
          :ref_for="true"
          theme="gray"
          size="sm"
          label="Button"
          :loading="false"
          :loadingText="null"
          :disabled="false"
          :link="null"
        >
        Xóa
        </Button> -->
			</div>
		</div>
		<component
			:is="list.options.getRowRoute ? 'template' : 'button'"
			class="[all:unset] hover:[all:unset]"
		>
			<div
				class="grid items-center space-x-4 rounded px-2"
				:class="[
					isSelected ? 'bg-gray-100' : '',
					isHoverable ? (isSelected ? 'hover:bg-gray-200' : 'hover:bg-gray-50') : '',
				]"
				:style="{
					height: rowHeight,
					gridTemplateColumns: getGridTemplateColumns(list.columns, list.options.selectable),
				}"
			>
				<Checkbox
					v-if="list.options.selectable"
					:modelValue="list.selections.has(row[list.rowKey])"
					@click.stop="list.toggleRow(row[list.rowKey])"
					class="cursor-pointer duration-300"
				/>
				<div
					v-for="(column, i) in list.columns"
					:key="column.key"
					:class="[alignmentMap[column.align], i == 0 ? 'text-gray-900' : 'text-gray-700']"
				>
					<slot v-bind="{ idx: i, column, item: row[column.key] }">
						<component
							v-if="list.slots.cell"
							:is="list.slots.cell"
							v-bind="{
								column,
								row,
								item: row[column.key],
								align: column.align,
							}"
						/>
						<ListRowItem
							v-else
							:column="column"
							:row="row"
							:item="row[column.key]"
							:align="column.align"
						/>
					</slot>
				</div>
			</div>

			<div v-if="!isLastRow" class="mx-2 h-px border-t border-gray-200" />
		</component>
		<!-- Dialog hiển thị thông tin chi tiết -->
	</component>
</template>

<script setup>
import {
	Checkbox,
	ListRowItem,
	Button,
	createResource,
	createListResource,
	Dialog,
	FormControl,
	Tabs,
  Dropdown
} from "frappe-ui"
import { alignmentMap, getGridTemplateColumns } from "./utils"
import { computed, inject, onMounted, ref, defineEmits } from "vue"
import FormControlCustom from "../FormControlCustom/FormControlCustom.vue"
import { useRoute, useRouter } from "vue-router"

const router = useRouter()
const route = useRoute()

const emit = defineEmits(["setChildRecord", "deleteRecord"])

const props = defineProps({
	row: {
		type: Object,
		required: true,
	},
})

const setActiveRecord = (row) => {
	emit("setChildRecord", row.name)
}

const deleteRecord = (row) => {
	emit("deleteRecord", row.name)
}

const testDialog = ref(false)
const list_data_staff = ref([])
const tabs = computed(() => {
	return list_data_staff.value
})

const tabIndex = ref(0)

const list = inject("list")

const detailViewRoute = computed(() => {
	return "EmployeeDetailView"
})

const isLastRow = computed(() => {
	if (!list.value.rows?.length) return false
	return (
		list.value.rows[list.value.rows.length - 1][list.value.rowKey] === props.row[list.value.rowKey]
	)
})

const isSelected = computed(() => {
	return list.value.selections.has(props.row[list.value.rowKey])
})

const isHoverable = computed(() => {
	return list.value.options.getRowRoute || list.value.options.onRowClick
})

const rowHeight = computed(() => {
	if (typeof list.value.options.rowHeight === "number") {
		return `${list.value.options.rowHeight}px`
	}
	return list.value.options.rowHeight
})
function quickOptions(row) {
	let options = [
		{
			label: __('Edit'),
			icon: "edit",
			onClick: () => setActiveRecord(row),
		},
		{
			label: "__('Delete')",
			icon: "trash",
			onClick: () => deleteRecord(row),
		},
	]
	return options
}
</script>
