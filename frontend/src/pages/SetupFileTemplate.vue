<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">
        {{ __('An error has occurred') }}:
      </div>
      <ErrorMessage :message="msgError" />
    </div>
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <h2 class="font-bold text-lg mb-4">{{ __('Action') }}</h2>
      <div class="flex gap-6">
        <Button
          :variant="'solid'"
          theme="gray"
          size="sm"
          label="Tạo File"
          :loading="false"
          :disabled="false"
          @click="callCreateFile"
        >
        </Button>
        <Button
          :variant="'solid'"
          theme="gray"
          size="sm"
          label="Export Template"
          :loading="false"
         :disabled="false"
          @click="callExportTemplate"
        >
        </Button>
        <Button
          :variant="'solid'"
          theme="gray"
          size="sm"
          label="Cập nhật mẫu từ File"
          :loading="false"
         :disabled="false"
          @click="callUpdateTemplate"
        >
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import { Breadcrumbs, ErrorMessage, call } from 'frappe-ui'
import { ref } from 'vue'
import { createToast, errorMessage, validErrApi } from '@/utils'
import { globalStore } from '@/stores/global'
import { useRouter } from 'vue-router'
const router = useRouter()

const { changeLoadingValue } = globalStore()

const breadcrumbs = [
  { label: 'Trình tạo', route: { name: 'Setup File Template' } },
]

const msgError = ref()

async function callCreateFile() {
  changeLoadingValue(true, 'Đang tạo file...')
  try {
    let docUpdate = await call(
      'go1_cms.api.setup_file_template.create_file_json',
      {},
    )

    if (docUpdate.msg) {
      createToast({
        title: 'Tạo thành công',
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    }
  } catch (err) {
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}

async function callExportTemplate() {
  changeLoadingValue(true, 'Đang export...')
  try {
    let docUpdate = await call(
      'go1_cms.api.export_template.export_template',
      {},
    )

    if (docUpdate.msg) {
      createToast({
        title: __('Success'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    }
  } catch (err) {
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}

async function callUpdateTemplate() {
  changeLoadingValue(true, 'Đang cập nhật...')
  try {
    let docUpdate = await call(
      'go1_cms.api.setup_file_template.update_from_json',
      {},
    )

    if (docUpdate.msg) {
      createToast({
        title: __('Success'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
    }
  } catch (err) {
    validErrApi(err, router)

    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  }
  changeLoadingValue(false)
}
</script>
