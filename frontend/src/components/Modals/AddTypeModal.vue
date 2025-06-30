<template>
	<Dialog
		v-model="open"
		:options="{
			position: 'center',
		}"
	>
		<template #body-title>
			<slot name="title"></slot>
		</template>
		<template #body-content>
			<slot name="content"></slot>
		</template>
		<template #actions>
			<div class="flex justify-end gap-2">
				<Button @click="open = false"> {{ __("Cancel") }} </Button>
				<Button
					@click="
						() => {
							// open = false;
							emit('action');
						}
					"
					class="bg-red-500"
					variant="solid"
				>
					{{ edit ? __("Save") : __("Add") }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
const open = defineModel();
const edit = defineModel('edit', { type: Boolean, default: false });
const emit = defineEmits(["action"]);
</script>
