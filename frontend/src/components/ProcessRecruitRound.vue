<template>
	<div v-if="data" class="bg-white p-4 rounded-lg w-full shadow">
		<div
			v-for="round in data.fixedStart"
			:key="round.name"
			class="flex items-center justify-between bg-gray-100 p-3 mb-2 border-l-4 shadow-md"
		>
			<div class="flex gap-2 items-center flex-1 ml-6 font-medium text-gray-700">
				<div
					class="h-3 w-3 rounded-full"
					:style="{ backgroundColor: getRoundColor(round.round_type) }"
				></div>
				<span>{{ round.round_name }}</span>
			</div>

			<button @click="$emit('edit', round)" class="text-black hover:text-blue-700">
				<FeatherIcon class="h-4" name="edit" />
			</button>
		</div>

		<Draggable
			v-model="data.draggableRounds"
			item-key="name"
			handle=".drag-handle"
			@end="onDragEnd"
		>
			<template #item="{ element }">
				<div
					class="flex items-center justify-between bg-white p-3 mb-2 border-l-4 shadow-md"
				>
					<FeatherIcon class="h-4 drag-handle cursor-grab" name="list" />
					<div class="flex gap-2 items-center flex-1 ml-2 font-medium text-gray-700">
						<div
							class="h-3 w-3 rounded-full"
							:style="{ backgroundColor: getRoundColor(element.round_type) }"
						></div>
						<span>{{ element.round_name }}</span>
					</div>
					<div class="flex gap-2">
						<button
							@click="$emit('edit', element)"
							class="text-black hover:text-blue-700"
						>
							<FeatherIcon class="h-4" name="edit" />
						</button>
						<button
							v-if="!element.default"
							@click="$emit('delete', element)"
							class="text-red-500 hover:text-red-700"
						>
							<FeatherIcon class="h-4" name="trash-2" />
						</button>
					</div>
				</div>
			</template>
		</Draggable>

		<div
			@click="$emit('add')"
			class="flex items-center justify-center bg-blue-100 p-3 mb-2 border-l-4 border-blue-500 shadow-md cursor-pointer hover:bg-blue-200"
		>
			<FeatherIcon class="h-4 text-blue-600" name="plus" />
			<span class="ml-2 text-blue-600 font-medium">{{ __("Add New Round") }}</span>
		</div>

		<div
			v-for="round in data.fixedEnd"
			:key="round.name"
			class="flex items-center justify-between bg-gray-100 p-3 mt-2 border-l-4 shadow-md"
		>
			<div class="flex gap-2 items-center flex-1 ml-6 font-medium text-gray-700">
				<div
					class="h-3 w-3 rounded-full"
					:style="{ backgroundColor: getRoundColor(round.round_type) }"
				></div>
				<span>{{ round.round_name }}</span>
			</div>

			<button @click="$emit('edit', round)" class="text-black hover:text-blue-700">
				<FeatherIcon class="h-4" name="edit" />
			</button>
		</div>
	</div>
	<p v-else class="text-center text-gray-500">{{__('Loading data')}}</p>
</template>

<script setup>
import Draggable from "vuedraggable";

const props = defineProps({
	data: Object,
	roundTypes: {
		type: Array,
		default: [() => []],
	},
});

const emit = defineEmits(["edit", "delete", "add", "reorder"]);

const onDragEnd = (e) => {
	const { oldIndex, newIndex } = e;
	if (oldIndex !== newIndex) emit("reorder", { oldIndex, newIndex });
};

const getRoundColor = (roundType) => {
	const found = props.roundTypes.find((r) => r.value === roundType);
	return found ? found.color : "#ccc"; // Nếu không tìm thấy, trả về màu xám mặc định
};
</script>
