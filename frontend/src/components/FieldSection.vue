<template>
  <template v-if="field.show_edit">
    <template v-if="field.field_type == 'List'">
      <div class="lg:col-span-2 overflow-y-hidden">
        <div class="text-base text-gray-700 font-bold mb-2">
          {{ __(field.field_label) }}
        </div>
        <div class="border overflow-auto max-h-[500px]">
          <table
            class="table-section text-base border-spacing-0 border-collapse w-full"
          >
            <thead class="sticky top-0 z-[2]">
              <tr class="box-border border-b bg-gray-50 min-h-16">
                <th class="p-2 w-auto sticky left-0 py-5">{{ __('No.') }}</th>
                <template v-for="f in field.fields_json">
                  <th class="p-2 min-w-48">
                    {{ __(f.field_label) }}
                  </th>
                </template>
                <th class="p-2 min-w-32 sticky right-0 py-5"></th>
              </tr>
            </thead>

            <template v-if="field.content?.length">
              <Draggable
                :list="field.content"
                @change="applySort(field)"
                item-key="idx"
                tag="tbody"
                handle=".handle"
              >
                <template #item="{ element, index }">
                  <tr
                    class="border-t border-b border-collapse hover:bg-gray-50 table-item"
                  >
                    <td class="p-2 text-center sticky left-0 z-[1] bg-white">
                      <div class="flex items-center gap-2 max-h-20">
                        <DragVerticalIconV1
                          class="h-8 text-gray-700 cursor-move handle"
                        />
                        <div>{{ element.idx }}</div>
                      </div>
                    </td>
                    <template v-for="fj in field.fields_json">
                      <td v-if="fj.field_type == 'Attach'">
                        <div class="shadow-inner p-2 text-center max-h-20">
                          <img
                            :src="element[fj.field_key]"
                            alt=""
                            class="h-15 w-20 border"
                          />
                        </div>
                      </td>
                      <td v-else>
                        <div
                          v-html="element[fj.field_key]"
                          class="p-2 shadow-inner max-h-20 overflow-hidden"
                          :class="
                            ['Text Editor', 'Long Text'].includes(fj.field_type)
                              ? 'ck-content'
                              : ''
                          "
                        ></div>
                      </td>
                    </template>
                    <td class="sticky right-0 z-[1]">
                      <div class="p-2 flex gap-2">
                        <Button
                          variant="solid"
                          theme="gray"
                          size="sm"
                          :label="__('Edit')"
                          @click="editItemSection(field, index)"
                        ></Button>
                        <Button
                          variant="solid"
                          theme="red"
                          size="sm"
                          :label="__('Delete')"
                          @click="deleteItemSection(field, index)"
                        ></Button>
                      </div>
                    </td>
                  </tr>
                </template>
              </Draggable>
            </template>
            <template v-else>
              <tbody>
                <tr class="border">
                  <td
                    class="p-3 text-center text-base text-gray-600"
                    :colspan="field.fields_json?.length + 2"
                  >
                    {{ __('No data available') }}
                  </td>
                </tr>
              </tbody>
            </template>
          </table>
        </div>
        <div class="flex py-3">
          <Button
            variant="solid"
            theme="blue"
            size="sm"
            :label="__('Add Row')"
            @click="createItemSection(field)"
          ></Button>
        </div>
      </div>
    </template>
    <template v-else-if="field.field_type == 'Button'">
      <div class="lg:col-span-2">
        <div class="text-base text-gray-700 font-bold mb-2">
          {{ __(field.field_label) }}
        </div>
        <div class="grid lg:grid-cols-2 gap-4">
          <div class="flex flex-col" v-for="f in field.fields_json">
            <Field
              :field="{
                label: f.field_label,
                name: f.field_key,
                type: getTypeField(f.field_type),
                placeholder: f.field_label,
                rows: 7,
              }"
              v-model="field['content'][f.field_key]"
            ></Field>
          </div>
        </div>
      </div>
    </template>
    <template v-else-if="field.field_type == 'texteditor'">
      <div class="lg:col-span-2">
        <Field
          :field="{
            label: field.field_label,
            name: field.field_key,
            type: getTypeField(field.field_type),
            placeholder: field.field_label,
            rows: 7,
            doctype: field.doctype,
            filters: field.filters,
            options: field.options,
            labelInput: field.label_input,
          }"
          v-model="field['content']"
        ></Field>
      </div>
    </template>
    <div class="flex flex-col" v-else>
      <Field
        v-if="getTypeField(field.field_type) == 'upload_image'"
        :field="{
          label: field.field_label,
          name: field.field_key,
          type: getTypeField(field.field_type),
          placeholder: field.field_label,
          classSize: field.classSize,
        }"
        :imgPreview="field['content']"
        v-model="field['upload_file_image']"
      ></Field>
      <Field
        v-else
        :field="{
          label: field.field_label,
          name: field.field_key,
          type: getTypeField(field.field_type),
          placeholder: field.placeholder || field.field_label,
          rows: 7,
          doctype: field.doctype,
          filters: field.filters,
          options: field.options,
          labelInput: field.label_input,
          disabled: !field.allow_edit,
          description: field.description,
          label_des: field.label_des,
          actions: field.actions,
        }"
        v-model:actions="field['actions']"
        v-model="field['content']"
      ></Field>
    </div>
  </template>
  <SectionModal
    :fields="currentItemFields"
    v-model="showSectionModal"
    v-model:section="currentItemSection"
    :editMode="editMode"
    :title="sectionName"
    :positionEdit="positionEdit"
  />
</template>

<script setup>
import Field from '@/components/Field.vue'
import DragVerticalIconV1 from '@/components/Icons/DragVerticalIconV1.vue'
import Draggable from 'vuedraggable'
import SectionModal from '@/components/Modals/SectionModal.vue'
import { getTypeField } from '@/utils'
import { ref } from 'vue'

const props = defineProps({
  field: {
    type: Object,
    default: {},
  },
  sectionName: {
    type: String,
    default: '',
  },
})

const showSectionModal = ref(false)
const currentItemSection = ref()
const currentItemFields = ref([])
const editMode = ref(false)
const positionEdit = ref()

function createItemSection(field) {
  let fields = field.fields_json.map((fj) => ({
    field_label: fj.field_label,
    field_key: fj.field_key,
    field_type: fj.field_type,
    value: null,
    upload_file_image: null,
  }))

  fields.unshift({
    field_label: 'No.',
    field_key: 'idx',
    field_type: 'number',
    disabled: true,
    value: field.content?.length + 1,
  })

  editMode.value = false
  currentItemFields.value = fields
  currentItemSection.value = field.content
  showSectionModal.value = true
}

function editItemSection(field, idx) {
  let item = field.content[idx]
  let fields = field.fields_json.map((fj) => ({
    field_label: fj.field_label,
    field_key: fj.field_key,
    field_type: fj.field_type,
    value: item[fj.field_key],
    upload_file_image: null,
  }))
  fields.unshift({
    field_label: 'No.',
    field_key: 'idx',
    field_type: 'number',
    disabled: true,
    value: item.idx,
  })

  positionEdit.value = idx
  editMode.value = true
  currentItemFields.value = fields
  currentItemSection.value = field.content
  showSectionModal.value = true
}

function deleteItemSection(field, idx) {
  field.content.splice(idx, 1)
  applySort(field)
}

function applySort(field) {
  field['content'] = field.content.map((el, idx) => ({ ...el, idx: idx + 1 }))
}
</script>

<style>
.table-item:hover > td {
  background-color: rgb(249 250 251);
}
.table-section td:first-child,
.table-section td:last-child,
.table-section th:first-child,
.table-section th:last-child {
  background-color: rgb(248 248 248);
}
</style>
