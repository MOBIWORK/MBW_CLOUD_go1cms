<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div
        class="gap-2 justify-end"
        :class="alreadyActions ? 'flex' : 'hidden'"
      >
        <Button
          variant="subtle"
          theme="gray"
          size="md"
          label="Hủy"
          :disabled="!dirty"
          @click="cacelSaveDoc"
        ></Button>
        <Button
          :variant="'solid'"
          theme="blue"
          size="md"
          label="Lưu"
          :disabled="!dirty"
          @click="callUpdateDoc"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">Có lỗi xảy ra:</div>
      <ErrorMessage :message="msgError" />
    </div>
    <FieldsComponent v-model="_header.fields_cp"></FieldsComponent>
    <FieldsSectionComponent
      v-model="_header.fields_st_cp"
    ></FieldsSectionComponent>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import FieldsComponent from '@/components/FieldsPage/FieldsComponent.vue'
import FieldsSectionComponent from '@/components/FieldsPage/FieldsSectionComponent.vue'
import { Breadcrumbs, ErrorMessage, createResource, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { createToast, errorMessage, handleUploadFieldImage } from '@/utils'
import { globalStore } from '@/stores/global'
const { changeLoadingValue } = globalStore()

const breadcrumbs = [{ label: 'Đầu trang', route: { name: 'Header Page' } }]
const _header = ref({})
const msgError = ref()

const header = createResource({
  url: 'go1_cms.api.header.get_info_header_component',
  auto: true,
  transform: (data) => {
    _header.value = JSON.parse(JSON.stringify(data))
    return data
  },
})

// handle allow actions
const alreadyActions = ref(false)
const dirty = computed(() => {
  return JSON.stringify(header.data) !== JSON.stringify(_header.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
})

async function callUpdateDoc() {
  changeLoadingValue(true, 'Đang lưu...')
  try {
    let data = JSON.parse(JSON.stringify(_header.value))

    // upload image
    await handleUploadFieldImage(
      data,
      _header,
      'Header Component',
      _header.value.docname,
    )

    let docUpdate = await call(
      'go1_cms.api.header.update_info_header_component',
      {
        data: data,
      },
    )

    if (docUpdate.name) {
      header.reload()

      createToast({
        title: 'Cập nhật thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    }
  } catch (err) {
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage('Có lỗi xảy ra', err.messages.join(', '))
    } else {
      errorMessage('Có lỗi xảy ra', err)
    }
  }
  changeLoadingValue(false)
}

async function cacelSaveDoc() {
  await header.reload()
}
</script>
