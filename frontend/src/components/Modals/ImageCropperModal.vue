<template>
    <Dialog v-model="visible" :options="dialogOptions">
      <template #body-content>
        <div v-if="imageDataUrl">
          <Cropper
            class="cropper"
            :src="imageDataUrl"
            :stencil-props="{ aspectRatio }"
            :auto-zoom="true"
            image-restriction="stencil"
            @change="onCropChange"
            ref="cropper"
          />
        </div>
      </template>
      <!-- <template #actions>
			<div class="flex justify-end gap-2">
				<Button variant="solid" @click="handleClose">Hủy</Button>
        <Button variant="solid" @click="handleCrop">Crop</Button>
			</div>
		</template> -->
    </Dialog>
  </template>
  
  <script setup>
  import { ref, watch, defineProps, defineEmits,computed } from 'vue'
  import { Cropper } from 'vue-advanced-cropper'
  import 'vue-advanced-cropper/dist/style.css'
  
  const props = defineProps({
    modelValue: Boolean,
    imageDataUrl: String,
    aspectRatio: {
      type: Number,
      default: 1,
    },
  })
  
  const emit = defineEmits(['update:modelValue', 'cropped'])
  
  const visible = ref(props.modelValue)
  watch(() => props.modelValue, (val) => (visible.value = val))
  watch(visible, (val) => emit('update:modelValue', val))
  
  const cropper = ref()
  const cropResult = ref(null)
  
  function onCropChange({ coordinates, canvas }) {
    cropResult.value = { coordinates, canvas }
  }
  
  async function handleCrop() {
  const canvas = cropper.value?.getResult()?.canvas;
  if (canvas) {
    // Chuyển canvas thành Blob
    canvas.toBlob((blob) => {
      if (!blob) return;

      const name = `cropped-${Date.now()}.png`;
      const file = new File([blob], name, { type: blob.type });

      const url = URL.createObjectURL(blob); // blob preview

      emit('cropped', { file, name, url });

      visible.value = false;
    }, 'image/png');
  }
}

  
  function handleClose() {
    visible.value = false
  }

  const dialogOptions = computed(() => {
	return {
		title: __("Crop image"),
		size: '3xl',
		actions: [
			{
				label: __('Crop'),
				variant: 'solid',
				onClick: (close) => {
					handleCrop(close)
				},
			},{
				label: __('Cancel'),
				variant: 'solid',
				onClick: (close) => {
					handleClose(close)
				},
			},
		],
	}
})

  </script>
  
  <style scoped>
  .cropper {
    width: 100%;
    height: 400px;
    background: #f0f0f0;
    overflow: hidden;
  }
  </style>
  