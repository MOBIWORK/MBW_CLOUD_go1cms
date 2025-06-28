<template>
	<div>
		<div class="dropdown" @click="toggleDropdown">
			<span>{{ selectedLabels.length ? selectedLabels.join(", ") : "Please select" }}</span>
			<span class="caret">▼</span>
		</div>
		<div v-if="isOpen" class="dropdown-content">
			<TreeNode
				v-for="node in treeData"
				:key="node.id"
				:node="node"
				:selected-ids="selectedIds"
				@select="handleSelect"
			/>
		</div>
	</div>
</template>

<script setup>
import { ref, computed } from "vue";
import TreeNode from "./TreeNode.vue";

// Props
const props = defineProps({
	treeData: {
		type: Array,
		required: true,
	},
});

// Emit
const emit = defineEmits(["select"]);

// Trạng thái
const isOpen = ref(false);
const selectedIds = ref(new Set()); // Sử dụng Set để quản lý ID đã chọn

// Hiển thị label từ ID
const selectedLabels = computed(() => {
	const findLabels = (nodes) => {
		let labels = [];
		nodes.forEach((node) => {
			if (selectedIds.value.has(node.id)) {
				labels.push(node.label);
			}
			if (node.children) {
				labels = labels.concat(findLabels(node.children));
			}
		});
		return labels;
	};
	return findLabels(props.treeData);
});

// Toggle dropdown
const toggleDropdown = () => {
	isOpen.value = !isOpen.value;
};

// Xử lý khi chọn node
const handleSelect = (node) => {
	if (selectedIds.value.has(node.id)) {
		selectedIds.value.delete(node.id); // Bỏ chọn
	} else {
		selectedIds.value.add(node.id); // Chọn
	}
	emit("select", Array.from(selectedIds.value)); // Emit danh sách ID đã chọn
};
</script>

<style scoped>
.dropdown {
	border: 1px solid #ccc;
	padding: 8px;
	cursor: pointer;
	display: flex;
	justify-content: space-between;
}
.dropdown-content {
	border: 1px solid #ccc;
	margin-top: 5px;
	padding: 10px;
	background: #fff;
}
.caret {
	margin-left: 8px;
}
</style>
