<template>
	<Dialog v-model="open" :options="{
     position: 'center',
  }">
		<template #body-title>
			<slot name="title"></slot>
		</template>
		<template #body-content>
			<slot name="content"></slot>
		</template>
		<template #actions>
			<div class="flex justify-center gap-2">
				<Button @click="open = false"> {{ __("Cancel") }} </Button>
				<Button
					@click="
						() => {
							open = false;
							emit('confirm');
						}
					"
          class="bg-red-500"
					variant="solid"
				>
					{{ __("Confirm") }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>

<script setup>
const open = defineModel();
const emit = defineEmits(["confirm"]);
</script>
