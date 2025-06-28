<template>
	<div>
		<label class="node">
			<input type="checkbox" :checked="isSelected" @change="toggleSelect" />
			{{ node.label }}
		</label>
		<div v-if="node.children" class="children">
			<TreeNode
				v-for="child in node.children"
				:key="child.id"
				:node="child"
				:selected-ids="selectedIds"
				@select="handleChildSelect"
			/>
		</div>
	</div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from "vue";

// Props
defineProps({
	node: {
		type: Object,
		required: true,
	},
	selectedIds: {
		type: Object, // Truyền Set từ TreeSelect
		required: true,
	},
});

// Emit
const emit = defineEmits(["select"]);

// Kiểm tra xem node có được chọn hay không
const isSelected = computed(() => selectedIds.has(node.id));

// Xử lý chọn/bỏ chọn
const toggleSelect = () => {
	emit("select", node);
};

// Truyền sự kiện từ node con lên
const handleChildSelect = (child) => {
	emit("select", child);
};
</script>

<style scoped>
.node {
	padding: 5px;
	display: flex;
	align-items: center;
	cursor: pointer;
}
.children {
	padding-left: 20px;
	border-left: 1px dashed #ccc;
}
</style>
