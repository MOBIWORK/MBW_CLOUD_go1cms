<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div class="flex gap-2 justify-end" v-if="alreadyActions">
        <Tooltip
          v-if="!_page?.web_page?.is_detail_page"
          :text="__('View page')"
          :hover-delay="1"
          :placement="'top'"
        >
          <div>
            <Button
              variant="subtle"
              theme="blue"
              size="md"
              label=""
              icon="eye"
              :link="views.data?.config_domain?.domain + _page?.web_page?.route"
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
          v-if="_page?.web_page?.allow_delete"
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
          variant="subtle"
          theme="gray"
          size="md"
          :label="__('Cancel')"
          :disabled="!dirty"
          @click="cancelSaveDoc"
        ></Button>
        <Button
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
    <div v-if="JSON.stringify(_page) != '{}'">
      <FieldsComponent v-model="_page.fields_cp"></FieldsComponent>
      <FieldsSectionComponent
        v-model="_page.fields_st_cp"
      ></FieldsSectionComponent>
    </div>
    <div v-else class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="flex justify-center h-screen mt-40 text-gray-700">
        <LoadingIndicator class="h-8 w-8" />
      </div>
    </div>
  </div>
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
</script>
