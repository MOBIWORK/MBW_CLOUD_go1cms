<template>
  <div class="flex flex-wrap gap-4">
    <div>
      <label v-if="title" class="block text-base text-gray-600 mb-2">
        {{ __(title) }}
      </label>
      <Button
        iconLeft="paperclip"
        :label="__('Upload image')"
        @click="$refs.refFile.click()"
      ></Button>
      <input
        ref="refFile"
        class="hidden"
        type="file"
        accept="image/*"
        @change="(e) => validateFile(e.target.files)"
      />
      <div v-if="nameFile" class="text-sm my-2">{{ nameFile }}</div>
      <ErrorMessage v-if="messageError" class="my-1" :message="messageError" />
    </div>
    <slot name="preview"></slot>
  </div>
</template>

<script setup>
import { ErrorMessage } from 'frappe-ui'
import { ref, watch } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Image',
  },
})

const refImg = defineModel('refImg')
const inputFile = defineModel()
const messageError = ref()
const nameFile = ref()

watch(inputFile, (val) => {
  if (!val) {
    nameFile.value = ''
  }
})

const reader = new FileReader()
reader.addEventListener(
  'load',
  () => {
    refImg.value.src = reader.result
  },
  false,
)

function validateFile(files) {
  if (files && files[0]) {
    let file = files[0]
    let extn = file.name.split('.').pop().toLowerCase()
    if (!['png', 'jpg', 'jpeg', 'svg'].includes(extn)) {
      messageError.value = __(
        'Only images with PNG, JPG, JPEG, SVG extensions are allowed.',
      )
      return
    } else {
      messageError.value = ''
    }
    inputFile.value = file
    nameFile.value = file.name
    reader.readAsDataURL(file)
  }
}
</script>
