<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #center-header>
      <!-- Preview Mode Toggle Buttons - Center -->
      <div v-if="isPreviewMode && alreadyActions" class="flex gap-1">
        <Button
          :variant="previewMode === 'desktop' ? 'solid' : 'subtle'"
          theme="blue"
          size="sm"
          @click="previewMode = 'desktop'"
        >
          <template #prefix>
            <FeatherIcon name="monitor" class="h-4 w-4" />
          </template>
          Desktop
        </Button>
        <Button
          :variant="previewMode === 'mobile' ? 'solid' : 'subtle'"
          theme="blue"
          size="sm"
          @click="previewMode = 'mobile'"
        >
          <template #prefix>
            <FeatherIcon name="smartphone" class="h-4 w-4" />
          </template>
          Mobile
        </Button>
      </div>
    </template>
    <template #right-header>
      <div class="flex gap-2" v-if="alreadyActions">
        <Tooltip
          v-if="!_page?.web_page?.is_detail_page"
          :text="isPreviewMode ? __('Edit page') : __('Preview page')"
          :hover-delay="1"
          :placement="'top'"
        >
          <div>
            <Button
              variant="subtle"
              :theme="isPreviewMode ? 'green' : 'blue'"
              size="md"
              label=""
              :icon="isPreviewMode ? 'edit-3' : 'eye'"
              @click="togglePreviewMode"
            >
            </Button>
          </div>
        </Tooltip>
        <!-- tinh nang sau -->
        <!-- <Tooltip text="Nhân bản trang" :hover-delay="1" placement="top">
          <div>
            <Button
              variant="subtle"
              theme="green"
              size="md"
              label="Nhân bản trang"
              :disabled="!dirty"
            >
            </Button>
          </div>
        </Tooltip> -->
        <Dropdown
          v-if="_page?.web_page?.allow_delete && !isPreviewMode"
          :options="[
            {
              group: __('Delete'),
              items: [
                {
                  label: __('Delete page'),
                  icon: 'trash',
                  onClick: () => {
                    showModalDelete = true
                  },
                },
              ],
            },
          ]"
        >
          <Button size="md">
            <template #icon>
              <FeatherIcon name="more-horizontal" class="h-4 w-4" />
            </template>
          </Button>
        </Dropdown>
        <Button
          v-if="!isPreviewMode"
          variant="subtle"
          theme="gray"
          size="md"
          :label="__('Cancel')"
          :disabled="!dirty"
          @click="cancelSaveDoc"
        ></Button>
        <Button
          v-if="!isPreviewMode"
          :variant="'solid'"
          theme="blue"
          size="md"
          :label="__('Save')"
          :disabled="!dirty"
          @click="callUpdateDoc"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div ref="refToTop" class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">
        {{ __('An error has occurred') }}:
      </div>
      <ErrorMessage :message="msgError" />
    </div>
    
    <!-- Edit Mode -->
    <div v-if="JSON.stringify(_page) != '{}' && !isPreviewMode">
      <FieldsComponent v-model="_page.fields_cp"></FieldsComponent>
      <FieldsSectionComponent
        v-model="_page.fields_st_cp"
      ></FieldsSectionComponent>
    </div>
    
    <!-- Preview Mode -->
    <div v-else-if="JSON.stringify(_page) != '{}' && isPreviewMode">
      <!-- Debug URL Info -->
      <div class="mb-4 p-3 bg-gray-50 rounded-lg border">
        <div class="text-sm text-gray-600 mb-2">
          <strong>Preview URL:</strong> 
          <a :href="previewUrl" target="_blank" class="text-blue-600 hover:underline ml-2">
            {{ previewUrl }}
          </a>
          <Button
            size="sm"
            variant="subtle"
            theme="blue"
            class="ml-2"
            @click="openInNewTab"
          >
            <template #prefix>
              <FeatherIcon name="external-link" class="h-3 w-3" />
            </template>
            Mở tab mới
          </Button>
        </div>
        <div class="text-xs text-gray-500">
          Domain: {{ views.data?.config_domain?.domain || 'Chưa cấu hình' }} | 
          Route: {{ _page?.web_page?.route || 'Chưa có route' }}
        </div>
      </div>
      
      <div
        class="mx-auto relative"
        :style="previewMode === 'mobile'
          ? 'width: 390px; height: 844px; border: 2px solid #e5e7eb; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.1);'
          : 'width: 100%; height: 80vh; border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden;'"
      >
        <!-- Loading overlay -->
        <div 
          v-if="iframeLoading"
          class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 z-10"
        >
          <div class="text-center">
            <LoadingIndicator class="h-8 w-8 mx-auto mb-2" />
            <p class="text-sm text-gray-600">Đang tải preview...</p>
          </div>
        </div>
        
        <!-- Error overlay -->
        <div 
          v-if="iframeError"
          class="absolute inset-0 flex items-center justify-center bg-red-50 z-10"
        >
          <div class="text-center p-6">
            <FeatherIcon name="alert-circle" class="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 class="text-lg font-semibold text-red-700 mb-2">Không thể tải preview</h3>
            <p class="text-sm text-red-600 mb-4">
              Trang web có thể chặn việc hiển thị trong iframe hoặc URL không hợp lệ
            </p>
            <Button
              variant="solid"
              theme="blue"
              size="sm"
              @click="openInNewTab"
            >
              <template #prefix>
                <FeatherIcon name="external-link" class="h-4 w-4" />
              </template>
              Mở trong tab mới
            </Button>
          </div>
        </div>
        
        <!-- Overlay to block clicks only, allow scroll -->
        <div 
          class="absolute inset-0 z-20 bg-transparent cursor-default"
          title="Preview mode - chỉ xem, không thể click"
          style="pointer-events: none;"
          @click.prevent
          @mousedown.prevent
          @mouseup.prevent
        ></div>
        
        <iframe
          ref="previewIframe"
          :src="previewUrl"
          style="width: 100%; height: 100%; border: none;"
          frameborder="0"
          @load="onIframeLoad"
          @error="onIframeError"
          @click.prevent.capture
          @mousedown.prevent.capture
          @mouseup.prevent.capture
        ></iframe>
      </div>
    </div>
    
    <!-- Loading -->
    <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="flex justify-center h-screen mt-40 text-gray-700">
        <LoadingIndicator class="h-8 w-8" />
      </div>
    </div>
  </div>

  <!-- Delete Modal -->
  <Dialog
    :options="{
      title: __('Delete page'),
      actions: [
        {
          label: __('Delete'),
          variant: 'solid',
          theme: 'red',
          onClick: (close) => deleteDoc(close),
        },
      ],
    }"
    v-model="showModalDelete"
  >
    <template v-slot:body-content>
      <div>
        <div>
          {{ __('Are you sure you want to delete the page') }}:
          <b>"{{ _page?.web_page?.name_page }}"</b>?
        </div>
        <div class="text-base">
          <p>
            <b class="text-red-600">- {{ __('Cannot be undone.') }}</b>
          </p>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import FieldsComponent from '@/components/FieldsPage/FieldsComponent.vue'
import FieldsSectionComponent from '@/components/FieldsPage/FieldsSectionComponent.vue'
import {
  Breadcrumbs,
  ErrorMessage,
  createResource,
  call,
  Dropdown,
} from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  createToast,
  errorMessage,
  handleUploadFieldImage,
  scrollToTop,
  customSlugify,
  validErrApi,
} from '@/utils'

import { globalStore } from '@/stores/global'
import { viewsStore } from '@/stores/views'
const { views } = viewsStore()

const { changeLoadingValue } = globalStore()
const route = useRoute()
const router = useRouter()

const _page = ref({})
const msgError = ref()
const refToTop = ref(null)
const alreadyActions = ref(false)

// Preview states
const isPreviewMode = ref(false)
const previewMode = ref('desktop') // 'desktop' or 'mobile'

// Toggle between edit and preview mode
function togglePreviewMode() {
  isPreviewMode.value = !isPreviewMode.value
  if (isPreviewMode.value) {
    iframeLoading.value = true
    iframeError.value = false
  }
}

// get detail
const page = createResource({
  url: 'go1_cms.api.page.get_info_page',
  method: 'GET',
  params: { name: route.query.view },
  auto: true,
  transform: (data) => {
    _page.value = JSON.parse(JSON.stringify(data))
    alreadyActions.value = true
    return data
  },
  onError: (err) => {
    validErrApi(err, router)
    if (err.messages && err.messages.length) {
      msgError.value = err.messages.join(', ')
      errorMessage(__('An error has occurred'), err.messages.join(', '))
    } else {
      errorMessage(__('An error has occurred'), err)
    }
  },
})

watch(route, (val, oldVal) => {
  _page.value = {}
  isPreviewMode.value = false // Reset preview mode when route changes
  page.update({
    params: { name: route.query.view },
  })
  page.reload()
  scrollToTop(refToTop)
})

// handle allow actions
const dirty = computed(() => {
  if (!_page.value?.web_page?.is_detail_page) {
    // if (_page.value?.fields_cp) {
    //   let route = _page.value?.fields_cp[1].fields[0].content
    //   let new_route = ''
    //   if (route) {
    //     let lst_route = route.split('/')
    //     lst_route = lst_route.map((el) => {
    //       return customSlugify(el)
    //     })
    //     new_route = lst_route.filter((el) => el !== '').join('/')
    //   }
    //   if (!new_route) {
    //     new_route = _page.value?.fields_cp[1].fields[1].content
    //   }
    //   _page.value.fields_cp[1].fields[0].description = new_route
    // }
  }

  if (JSON.stringify(_page.value) == '{}') {
    return false
  }

  return JSON.stringify(page.data) !== JSON.stringify(_page.value)
})

const breadcrumbs = computed(() => {
  let items = []
  items.push({
    label: page.data?.web_page.name_page,
    route: {
      name: 'Page',
      query: { view: route.query.view },
    },
  })
  return items
})

async function callUpdateDoc() {
  changeLoadingValue(true, __('Saving...'))
  try {
    let data = JSON.parse(JSON.stringify(_page.value))
    // upload image
    await handleUploadFieldImage(
      data,
      _page,
      'Web Page Builder',
      _page.value?.web_page?.doc_page,
    )

    let docUpdate = await call('go1_cms.api.page.update_info_page', {
      data: data,
    })

    if (docUpdate.name) {
      page.reload()

      createToast({
        title: __('Saved'),
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

async function cancelSaveDoc() {
  await page.reload()
}

// delete page
const showModalDelete = ref(false)
async function deleteDoc(close) {
  changeLoadingValue(true, __('Deleting...'))
  try {
    await call('go1_cms.api.page.delete_page', {
      name: route.query.view,
    }).then(() => {
      createToast({
        title: __('Deleted'),
        icon: 'check',
        iconClasses: 'text-green-600',
      })
      close()
      window.location.href = '/cms/interface-repository'
    })
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

// Preview URL
const previewUrl = computed(() => {
  if (_page.value?.web_page?.route) {
    // Check protocol: http = local, https = production
    const isLocal = window.location.protocol === 'http:'
    const domain = isLocal 
      ? 'http://cms_fix:8010'
      : views.data?.config_domain?.domain
    
    return domain + _page.value.web_page.route
  }
  return ''
})

// Preview iframe
const previewIframe = ref(null)
const iframeLoading = ref(false)
const iframeError = ref(false)

function onIframeLoad() {
  iframeLoading.value = false
  iframeError.value = false
}

function onIframeError() {
  iframeLoading.value = false
  iframeError.value = true
}

function openInNewTab() {
  window.open(previewUrl.value, '_blank')
}
</script>
