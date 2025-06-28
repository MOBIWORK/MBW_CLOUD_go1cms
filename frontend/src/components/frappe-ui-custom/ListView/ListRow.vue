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

		<component class="[all:unset] hover:[all:unset]">
			<!-- Dòng chính -->
			<div
				class="relative grid items-center space-x-4 rounded px-2"
				:class="[
					isSelected ? 'bg-surface-gray-2' : '',
					isHoverable
						? isSelected
							? 'hover:bg-surface-gray-3'
							: 'hover:bg-surface-menu-bar'
						: '',
				]"
				:style="{
					height: rowHeight,
					gridTemplateColumns: getGridTemplateColumns(
						list.columns,
						list.options.selectable,
					),
				}"
			>
				<div
					class="absolute right-2 top-1/2 -translate-y-1/2 flex gap-2 duration-300"
					@click.stop
				>
					<Dropdown :options="quickOptions(quickOptions, row)">
						<Button
							icon="more-vertical"
							class="text-gray-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
							variant="ghost"
						/>
					</Dropdown>
				</div>
				<!-- Nội dung dòng -->
				<Checkbox
					v-if="list.options.selectable"
					:modelValue="list.selections.has(row[list.rowKey])"
					@click.stop="list.toggleRow(row[list.rowKey])"
					class="cursor-pointer duration-300"
				/>
				<div
					v-for="(column, i) in list.columns"
					:key="column.key"
					:class="[
						alignmentMap[column.align],
						i == 0 ? 'text-ink-gray-9' : 'text-ink-gray-7',
					]"
					:style="i === 0 ? { paddingLeft: `${level * 20}px` } : {}"
					class="truncate-text"
				>
				<!-- {{ console.log(">>>>>>>>>>>>>>>>>>>>>>", column) }} -->
					<div class="flex items-center">
						<!-- Nút collapse chỉ hiển thị ở cột đầu tiên -->
						<span
							v-show="i === 0 && row.children && row.children.length"
							class="collapse-icon cursor-pointer"
							@click.stop="toggleCollapse(row)"
						>
							<component
								:is="row.collapsed ? 'FeatherIcon' : 'span'"
								:name="row.collapsed ? 'plus-square' : 'minus-square'"
								class="size-4 text-black"
							>
								<span v-if="!row.collapsed">
									<FeatherIcon name="minus-square" class="size-4 text-black" />
								</span>
							</component>
						</span>
						<!-- <span v-if="i === 0">{{ row[column.key] }}</span> -->
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
			</div>
			<div v-if="isLastRow" class="mx-2 h-px border-t border-outline-gray-modals" />
			<!-- Hiển thị cấp con với hiệu ứng mở rộng -->
			<div
				v-show="!row.collapsed && row.children && row.children.length"
				class="overflow-hidden"
			>
				<ListRow
					v-for="child in row.children"
					:key="child[list.rowKey]"
					:row="child"
					:level="level + 1"
				/>
			</div>
		</component>
	</component>
</template>

<script setup>
import {
	Checkbox,
	Button,
	createResource,
	Dropdown,
	createListResource,
	Dialog,
	FormControl,
	Tabs,
} from "frappe-ui";
import ListRowItem from "./ListRowItem.vue";
import { alignmentMap, getGridTemplateColumns } from "./utils";
import { computed, inject } from "vue";
import { useFieldStore } from "../../../stores/activeRecord";

const fieldStore = useFieldStore();

const props = defineProps({
	row: {
		type: Object,
		required: true,
	},
	level: {
		type: Number,
		default: 0,
	},
});

const list = inject("list");
console.log(">>>>>", list.value)

// const isLastRow = computed(() => {
// 	if (!list.value.rows?.length) return false;
// 	return (
// 		list.value.rows[list.value.rows.length - 1][list.value.rowKey] ===
// 		props.row[list.value.rowKey]
// 	);
// });

const isLastRow = computed(() => {
	function findParentChildren(row, allRows) {
		// Tìm danh sách children của cha
		for (const r of allRows) {
			if (r.children && r.children.includes(row)) {
				return r.children;
			}
			// Tiếp tục tìm trong children
			if (r.children && r.children.length > 0) {
				const found = findParentChildren(row, r.children);
				if (found) return found;
			}
		}
		return allRows; // Nếu không tìm thấy, trả về danh sách gốc
	}

	// Lấy danh sách con của cha
	const parentChildren = findParentChildren(props.row, list.value.rows);

	// Kiểm tra nếu không có danh sách con hoặc không có row
	if (!parentChildren || parentChildren.length === 0) return false;

	// Kiểm tra nếu hàng hiện tại là hàng cuối 
	return parentChildren[parentChildren.length - 1][list.rowKey] === props.row[list.rowKey];
});

const isSelected = computed(() => {
	return list.value.selections.has(props.row[list.value.rowKey]);
});

const isHoverable = computed(() => {
	return list.value.options.getRowRoute || list.value.options.onRowClick;
});

const rowHeight = computed(() => {
	if (typeof list.value.options.rowHeight === "number") {
		return `${list.value.options.rowHeight}px`;
	}
	return list.value.options.rowHeight;
});

const toggleCollapse = (row) => {
	row.collapsed = !row.collapsed;
};

function quickOptions(action, row) {
	let options = [
		{
			label: "Sửa",
			icon: "edit",
			onClick: () => actionQuickEditRow(row?.name),
		},
		{
			label: "Xóa",
			icon: "trash",
			onClick: () => actionQuickDeleteRow(row?.name),
		},
	];
	return options;
}

const actionQuickDeleteRow = (name) => {
	// Hàm viết quick action Delete
	console.log(name);
	fieldStore.setChildTableField(name, "delete");
};
const actionQuickEditRow = (name) => {
	// Hàm viết quick action Edit
	console.log(name);
	fieldStore.setChildTableField(name, "edit");
};
</script>

<style scoped>
.collapse-icon {
	margin-right: 8px;
	font-size: 14px;
	font-weight: bold;
	cursor: pointer;
}

/* .expand-enter-active,
.expand-leave-active {
	transition: max-height 0.6s ease, opacity 0.6s ease;
}

.expand-enter-from,
.expand-leave-to {
	max-height: 0;
	opacity: 0;
}

.expand-enter-to,
.expand-leave-from {
	max-height: 1000px;
	opacity: 1;
} */
.truncate-text {
	overflow: hidden;
	white-space: nowrap;
	text-overflow: ellipsis;
	display: -webkit-box;
	-webkit-line-clamp: 1; /* Số dòng muốn hiển thị */
	-webkit-box-orient: vertical;
}
</style>
