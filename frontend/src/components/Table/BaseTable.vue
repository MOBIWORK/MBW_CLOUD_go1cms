<template>
	<div class="overflow-x-auto w-full">
		<table class="min-w-full divide-y divide-gray-200" :key="JSON.stringify(props.data)">
			<thead class="bg-gray-50">
				<template
					v-if="table?.getHeaderGroups()"
					v-for="(headerGroup, rowIndex) in table.getHeaderGroups()"
					:key="headerGroup.id"
				>
					<tr>
						<th
							v-for="header in headerGroup.headers"
							:key="header.id"
							:colspan="header.colSpan > 1 ? header.colSpan : undefined"
							:rowspan="
								!header.isPlaceholder && !header.column.columnDef.columns
									? table.getHeaderGroups().length - rowIndex
									: undefined
							"
							:style="
								header.column.columnDef.size
									? `width: ${header.column.columnDef.size}px`
									: ''
							"
							:class="[
								'px-4 py-2 text-xs font-medium uppercase border align-middle text-nowrap',
								headerGroup.depth === 0
									? 'text-center text-black'
									: 'text-left text-gray-600',
							]"
						>
							{{ header.isPlaceholder ? "" : header.column.columnDef.header }}
						</th>
					</tr>
				</template>
			</thead>

			<tbody class="divide-y divide-gray-200 bg-white">
				<template v-for="row in table.getRowModel().rows" :key="row.id">
					<!-- Group Header Row -->
					<tr v-if="row.getIsGrouped()">
						<td
							class="bg-gray-100 font-semibold text-sm text-center px-4 py-2"
							:colspan="columns.length"
						>
							{{ row.getValue(row.groupingColumnId) }} ({{ row.subRows.length }} mục)
						</td>
					</tr>

					<!-- Normal Row -->
					<tr v-else>
						<td
							v-for="cell in row.getVisibleCells()"
							:key="cell.id"
							class="px-4 py-2 whitespace-nowrap border"
							:style="
								cell.column.columnDef.size
									? `width: ${cell.column.columnDef.size}px`
									: ''
							"
						>
							{{ cell.getValue() }}
						</td>
					</tr>
				</template>
			</tbody>
		</table>
	</div>
</template>

<script setup>
import { watch, nextTick, ref } from "vue";
import {
	useVueTable,
	getCoreRowModel,
	getExpandedRowModel,
	getGroupedRowModel,
} from "@tanstack/vue-table";

const props = defineProps({
	columns: Array,
	data: Array,
	mode: { type: String, default: "flat" }, // 'flat', 'expandable', 'grouped'
	groupBy: { type: Array, default: () => [] },
	getSubComponent: Function,
});

const table = ref(null);

// ⚠️ Gắn size trực tiếp vào column khi build
const buildTable = (data, columns) =>
	useVueTable({
		data,
		columns,
		getCoreRowModel: getCoreRowModel(),
		columnResizeMode: "onChange", // 👈 giữ lại sizing khi resize
		...(props.mode === "expandable" && { getExpandedRowModel: getExpandedRowModel() }),
		...(props.mode === "grouped" && { getGroupedRowModel: getGroupedRowModel() }),
		...(props.groupBy.length && { state: { grouping: props.groupBy } }),
	});

table.value = buildTable(props.data, props.columns);

watch(
	() => props.data,
	(newData) => {
		nextTick(() => {
			table.value = buildTable(newData, props.columns);
		});
	},
	{ deep: true },
);
</script>

<style scoped></style>
