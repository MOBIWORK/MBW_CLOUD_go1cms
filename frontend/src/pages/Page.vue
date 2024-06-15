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
  <div ref="refToTop" class="p-6 overflow-auto">
    <div v-if="msgError" class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="text-base text-red-600 font-bold mb-2">Có lỗi xảy ra:</div>
      <ErrorMessage :message="msgError" />
    </div>
    <div
      v-if="_page?.fields_cp && _page?.fields_cp.length"
      class="p-4 border border-gray-300 rounded-sm mb-4"
    >
      <div class="p-2">
        <div class="mb-4">
          <h2 class="font-bold text-xl">Thông tin chung</h2>
        </div>
        <div v-for="(field, idx) in _page?.fields_cp" :key="field.name">
          <div v-if="field.allow_edit" class="border-t py-4">
            <div class="mb-4">
              <h2 class="font-bold text-lg">{{ field.section_title }}</h2>
            </div>
            <div class="grid lg:grid-cols-2 gap-4">
              <template v-for="fd in field.fields">
                <template v-if="fd.group_name">
                  <div class="lg:col-span-2">
                    <div class="grid lg:grid-cols-2 gap-4">
                      <template v-for="fsc in fd.fields">
                        <FieldSection
                          :field="fsc"
                          :sectionName="field.section_title"
                        ></FieldSection>
                      </template>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <FieldSection
                    :field="fd"
                    :sectionName="field.section_title"
                  ></FieldSection>
                </template>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      v-if="_page?.fields_st_cp && _page?.fields_st_cp.length"
      class="p-4 border border-gray-300 rounded-sm mb-4"
    >
      <div class="p-2">
        <div class="mb-4">
          <h2 class="font-bold text-xl">Các thành phần của trang</h2>
        </div>
        <div v-for="(field, idx) in _page?.fields_st_cp" :key="field.name">
          <div v-if="field.allow_edit" class="border-t py-4">
            <div class="mb-2">
              <h2 class="font-bold text-lg">{{ field.section_title }}</h2>
            </div>
            <div class="grid lg:grid-cols-2 gap-4">
              <template v-for="fd in field.fields">
                <template v-if="fd.group_name">
                  <div class="lg:col-span-2">
                    <div class="grid lg:grid-cols-2 gap-4">
                      <template v-for="fsc in fd.fields">
                        <FieldSection
                          :field="fsc"
                          :sectionName="field.section_title"
                        ></FieldSection>
                      </template>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <FieldSection
                    :field="fd"
                    :sectionName="field.section_title"
                  ></FieldSection>
                </template>
              </template>
              <template v-for="fd in field.fields_ps">
                <FieldSection :field="fd"></FieldSection>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import FieldSection from '../components/FieldSection.vue'
import { Breadcrumbs, ErrorMessage, createResource, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { createToast, errorMessage, uploadFile, scrollToTop } from '@/utils'
import { globalStore } from '@/stores/global'

const { changeLoadingValue } = globalStore()
const route = useRoute()

const _page = ref({})
const msgError = ref()
const refToTop = ref(null)

// get detail
const page = createResource({
  url: 'go1_cms.api.page.get_info_page',
  method: 'GET',
  params: { name: route.query.view },
  auto: true,
  transform: (data) => {
    _page.value = JSON.parse(JSON.stringify(data))
    return data
  },
})

watch(route, (val, oldVal) => {
  page.update({
    params: { name: route.query.view },
  })
  page.reload()
  scrollToTop(refToTop)
})

// handle allow actions
const alreadyActions = ref(false)
const dirty = computed(() => {
  return JSON.stringify(page.data) !== JSON.stringify(_page.value)
})

watch(dirty, (val) => {
  alreadyActions.value = true
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
  changeLoadingValue(true, 'Đang lưu...')
  try {
    let data = JSON.parse(JSON.stringify(_page.value))

    // upload image
    for (const [idx_cp, field] of _page.value.fields_cp.entries()) {
      for (const [idx_f, f] of field.fields.entries()) {
        if (f.group_name) {
          for (const [idx, f_st] of f.fields.entries()) {
            if (f_st.field_type == 'Attach' && f_st.upload_file_image) {
              // upload file
              let file_url = await uploadFile(
                'Web Page Builder',
                _page.value?.web_page?.doc_page,
                f_st.field_key,
                f_st.content,
                f_st.upload_file_image
              )
              data['fields_cp'][idx_cp]['fields'][idx_f]['fields'][idx][
                'content'
              ] = file_url
            }
          }
        } else {
          if (f.field_type == 'Attach' && f.upload_file_image) {
            // upload file
            let file_url = await uploadFile(
              'Web Page Builder',
              _page.value?.web_page?.doc_page,
              f.field_key,
              f.content,
              f.upload_file_image
            )
            data['fields_cp'][idx_cp]['fields'][idx_f]['content'] = file_url
          }
        }
      }
    }

    for (const [idx_cp, field] of _page.value.fields_st_cp.entries()) {
      for (const [idx_f, f] of field.fields.entries()) {
        if (f.group_name) {
          for (const [idx, f_st] of f.fields.entries()) {
            if (f_st.field_type == 'Attach' && f_st.upload_file_image) {
              // upload file
              let file_url = await uploadFile(
                'Web Page Builder',
                _page.value?.web_page?.doc_page,
                f_st.field_key,
                f_st.content,
                f_st.upload_file_image
              )
              data['fields_st_cp'][idx_cp]['fields'][idx_f]['fields'][idx][
                'content'
              ] = file_url
            } else if (f_st.field_type == 'List') {
              for (const [idx_f_ps, f_ps] of f_st.content.entries()) {
                for (const [idx_f_js, f_js] of f_st.fields_json.entries()) {
                  if (
                    f_js.field_type == 'Attach' &&
                    f_ps['upload_file_image_' + f_js.field_key]
                  ) {
                    // upload file
                    let file_url = await uploadFile(
                      'Web Page Builder',
                      _page.value?.web_page?.doc_page,
                      f_js.field_key,
                      f_ps[f_js.field_key],
                      f_ps['upload_file_image_' + f_js.field_key]
                    )
                    f_ps[f_js.field_key] = file_url
                  }
                  delete f_ps['upload_file_image_' + f_js.field_key]
                  data['fields_st_cp'][idx_cp]['fields'][idx_f]['fields'][idx][
                    'content'
                  ][idx_f_ps] = { ...f_ps }
                }
              }
            }
          }
        } else {
          if (f.field_type == 'Attach' && f.upload_file_image) {
            // upload file
            let file_url = await uploadFile(
              'Web Page Builder',
              _page.value?.web_page?.doc_page,
              f.field_key,
              f.content,
              f.upload_file_image
            )
            data['fields_st_cp'][idx_cp]['fields'][idx_f]['content'] = file_url
          } else if (f.field_type == 'List') {
            for (const [idx_f_ps, f_ps] of f.content.entries()) {
              for (const [idx_f_js, f_js] of f.fields_json.entries()) {
                if (
                  f_js.field_type == 'Attach' &&
                  f_ps['upload_file_image_' + f_js.field_key]
                ) {
                  // upload file
                  let file_url = await uploadFile(
                    'Web Page Builder',
                    _page.value?.web_page?.doc_page,
                    f_js.field_key,
                    f_ps[f_js.field_key],
                    f_ps['upload_file_image_' + f_js.field_key]
                  )

                  f_ps[f_js.field_key] = file_url
                }
                delete f_ps['upload_file_image_' + f_js.field_key]
                data['fields_st_cp'][idx_cp]['fields'][idx_f]['content'][
                  idx_f_ps
                ] = { ...f_ps }
              }
            }
          }
        }
      }
    }

    let docUpdate = await call('go1_cms.api.page.update_info_page', {
      data: data,
    })

    if (docUpdate.name) {
      page.reload()

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
  await page.reload()
}
</script>