<template>
  <div class="flex items-center justify-between overflow-x-auto gap-2 py-4">
    <!-- <div class="flex items-center gap-2">
      <Dropdown :options="viewsDropdownOptions">
        <template #default="{ open }">
          <Button :label="__(currentView.label)">
            <template #prefix>
              <div v-if="isEmoji(currentView.icon)">{{ currentView.icon }}</div>
              <FeatherIcon
                v-else-if="typeof currentView.icon == 'string'"
                :name="currentView.icon"
                class="h-4"
              />
              <component v-else :is="currentView.icon" class="h-4" />
            </template>
            <template #suffix>
              <FeatherIcon
                :name="open ? 'chevron-up' : 'chevron-down'"
                class="h-4 text-gray-600"
              />
            </template>
          </Button>
        </template>
      </Dropdown>
      <Dropdown :options="viewActions">
        <template #default>
          <Button icon="more-horizontal" />
        </template>
      </Dropdown>
    </div> -->
    <!-- <div class="-mr-2 h-[70%] border-l" /> -->
    <FadedScrollableDiv
      class="flex flex-1 items-center overflow-x-auto min-w-72"
      orientation="horizontal"
    >
      <div
        v-for="filter in quickFilterList"
        :key="filter.name"
        class="m-1 min-w-36"
      >
        <QuickFilterField
          :filter="filter"
          @applyQuickFilter="(f, v) => applyQuickFilter(f, v)"
        />
      </div>
    </FadedScrollableDiv>
    <div class="-ml-2 h-[70%] border-l" />
    <div class="flex items-center gap-2">
      <div
        v-if="viewUpdated && route.query.view && (!view.public || isManager())"
        class="flex items-center gap-2 border-r pr-2"
      >
        <Button :label="__('Cancel')" @click="cancelChanges" />
        <Button :label="__('Save Changes')" @click="saveView" />
      </div>
      <div class="flex items-center gap-2">
        <Button :label="__('Refresh')" @click="reload()" :loading="isLoading">
          <template #icon>
            <RefreshIcon class="h-4 w-4" />
          </template>
        </Button>
        <GroupBy
          v-if="route.params.viewType === 'group_by'"
          v-model="list"
          :doctype="doctype"
          @update="updateGroupBy"
        />
        <Filter
          v-model="list"
          :doctype="doctype"
          :default_filters="filters"
          @update="updateFilter"
        />
        <SortBy v-model="list" :doctype="doctype" @update="updateSort" />
        <ColumnSettings
          v-if="!options.hideColumnsButton"
          v-model="list"
          :doctype="doctype"
          @update="(isDefault) => updateColumns(isDefault)"
        />
        <Dropdown
          v-if="!options.hideColumnsButton"
          :options="[
            {
              group: __('Options'),
              hideLabel: true,
              items: [
                {
                  label: __('Export'),
                  icon: () =>
                    h(FeatherIcon, { name: 'download', class: 'h-4 w-4' }),
                  onClick: () => (showExportDialog = true),
                },
              ],
            },
          ]"
        >
          <template #default>
            <Button icon="more-horizontal" />
          </template>
        </Dropdown>
      </div>
    </div>
  </div>
  <ViewModal
    v-model="showViewModal"
    v-model:view="viewModalObj"
    :doctype="doctype"
    :options="{
      afterCreate: async (v) => {
        await reloadView()
        viewUpdated = false
        router.push({
          name: route.name,
          params: { viewType: v.type || 'list' },
          query: { view: v.name },
        })
      },
      afterUpdate: () => {
        viewUpdated = false
        reloadView()
      },
    }"
  />
  <Dialog
    v-model="showExportDialog"
    :options="{
      title: __('Export'),
      actions: [
        {
          label: __('Download'),
          variant: 'solid',
          onClick: () => exportRows(),
        },
      ],
    }"
  >
    <template #body-content>
      <FormControl
        variant="outline"
        :label="__('Export Type')"
        type="select"
        :options="[
          {
            label: __('Excel'),
            value: 'Excel',
          },
          {
            label: __('CSV'),
            value: 'CSV',
          },
        ]"
        v-model="export_type"
        :placeholder="__('Excel')"
      />
      <div class="mt-3">
        <FormControl
          type="checkbox"
          :label="__('Export All {0} Record(s)', [list.data.total_count])"
          v-model="export_all"
        />
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
import QuickFilterField from '@/components/QuickFilterField.vue'
import RefreshIcon from '@/components/Icons/RefreshIcon.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import DuplicateIcon from '@/components/Icons/DuplicateIcon.vue'
import PinIcon from '@/components/Icons/PinIcon.vue'
import UnpinIcon from '@/components/Icons/UnpinIcon.vue'
import ViewModal from '@/components/Modals/ViewModal.vue'
import SortBy from '@/components/SortBy.vue'
import Filter from '@/components/Filter.vue'
import GroupBy from '@/components/GroupBy.vue'
import FadedScrollableDiv from '@/components/FadedScrollableDiv.vue'
import ColumnSettings from '@/components/ColumnSettings.vue'
import { globalStore } from '@/stores/global'
import { viewsStore } from '@/stores/views'
import { usersStore } from '@/stores/users'
import { isEmoji, validErrApi } from '@/utils'
import { createResource, Dropdown, call, FeatherIcon } from 'frappe-ui'
import { computed, ref, onMounted, watch, h, markRaw } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDebounceFn } from '@vueuse/core'
import _ from 'lodash'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  filters: {
    type: Object,
    default: {},
  },
  options: {
    type: Object,
    default: {
      hideColumnsButton: false,
      defaultViewName: '',
      allowedViews: ['list'],
    },
  },
})

const { $dialog } = globalStore()
const { reload: reloadView, getView } = viewsStore()
const { isManager } = usersStore()

const list = defineModel()
const loadMore = defineModel('loadMore')
const resizeColumn = defineModel('resizeColumn')
const updatedPageCount = defineModel('updatedPageCount')

const route = useRoute()
const router = useRouter()

const defaultParams = ref('')

const viewUpdated = ref(false)
const showViewModal = ref(false)

function getViewType() {
  let viewType = route.params.viewType || 'list'
  let types = {
    list: {
      label: __('List View'),
      icon: 'list',
    },
    group_by: {
      label: __('Group By View'),
      icon: markRaw(DetailsIcon),
    },
  }

  return types[viewType]
}

const currentView = computed(() => {
  let _view = getView(route.query.view, route.params.viewType, props.doctype)
  return {
    label:
      _view?.label || props.options?.defaultViewName || getViewType().label,
    icon: _view?.icon || getViewType().icon,
  }
})

const view = ref({
  name: '',
  label: '',
  type: 'list',
  icon: '',
  filters: {},
  order_by: 'modified desc',
  columns: '',
  rows: '',
  load_default_columns: false,
  pinned: false,
  public: false,
})

const pageLength = computed(() => list.value?.data?.page_length)
const pageLengthCount = computed(() => list.value?.data?.page_length_count)

watch(loadMore, (value) => {
  if (!value) return
  updatePageLength(value, true)
})

watch(resizeColumn, (value) => {
  if (!value) return
  updateColumns()
})

watch(updatedPageCount, (value) => {
  if (!value) return
  updatePageLength(value)
})

function getParams() {
  let _view = getView(route.query.view, route.params.viewType, props.doctype)
  const filters = (_view?.filters && JSON.parse(_view.filters)) || {}
  const order_by = _view?.order_by || 'modified desc'
  const columns = _view?.columns || ''
  const rows = _view?.rows || ''

  if (_view) {
    view.value = {
      name: _view.name,
      label: _view.label,
      type: _view.type || 'list',
      icon: _view.icon,
      filters: _view.filters,
      order_by: _view.order_by,
      group_by_field: _view.group_by_field,
      columns: _view.columns,
      rows: _view.rows,
      route_name: _view.route_name,
      load_default_columns: _view.row,
      pinned: _view.pinned,
      public: _view.public,
    }
  } else {
    view.value = {
      name: '',
      label: getViewType().label,
      type: route.params.viewType || 'list',
      icon: '',
      filters: {},
      order_by: 'modified desc',
      group_by_field: 'owner',
      columns: '',
      rows: '',
      route_name: route.name,
      load_default_columns: true,
      pinned: false,
      public: false,
    }
  }

  return {
    doctype: props.doctype,
    filters: filters,
    order_by: order_by,
    columns: columns,
    rows: rows,
    page_length: pageLength.value,
    page_length_count: pageLengthCount.value,
    view: {
      custom_view_name: _view?.name || '',
      view_type: _view?.type || route.params.viewType || 'list',
      group_by_field: _view?.group_by_field || 'owner',
    },
    default_filters: props.filters,
  }
}

list.value = createResource({
  url: 'go1_cms.api.doc.get_list_data',
  params: getParams(),
  cache: [props.doctype, route.query.view, route.params.viewType],
  onSuccess(data) {
    let cv = getView(route.query.view, route.params.viewType, props.doctype)
    let params = list.value.params ? list.value.params : getParams()
    defaultParams.value = {
      doctype: props.doctype,
      filters: params.filters,
      order_by: params.order_by,
      page_length: params.page_length,
      page_length_count: params.page_length_count,
      columns: data.columns,
      rows: data.rows,
      view: {
        custom_view_name: cv?.name || '',
        view_type: cv?.type || route.params.viewType || 'list',
        group_by_field: params?.view?.group_by_field || 'owner',
      },
      default_filters: props.filters,
    }
  },
  onError: (err) => {
    validErrApi(err, router)
  },
})

onMounted(() => useDebounceFn(reload, 100)())

const isLoading = computed(() => list.value?.loading)

function reload() {
  list.value.params = getParams()
  list.value.reload()
}

const showExportDialog = ref(false)
const export_type = ref('Excel')
const export_all = ref(false)

async function exportRows() {
  let fields = list.value.data.columns.filter(
    (f) => !['action_button'].includes(f.key),
  )
  fields = JSON.stringify(fields.map((f) => f.key))
  let filters = JSON.stringify(list.value.params.filters)
  let order_by = list.value.params.order_by
  let page_length = list.value.params.page_length
  if (export_all.value) {
    page_length = list.value.data.total_count
  }

  window.location.href = `/api/method/frappe.desk.reportview.export_query?file_format_type=${export_type.value}&title=${props.doctype}&doctype=${props.doctype}&fields=${fields}&filters=${filters}&order_by=${order_by}&page_length=${page_length}&start=0&view=Report&with_comment_count=1`
  showExportDialog.value = false
  export_all.value = false
  export_type.value = 'Excel'
}

let defaultViews = []
let allowedViews = props.options.allowedViews || ['list']

if (allowedViews.includes('list')) {
  defaultViews.push({
    label: __(props.options?.defaultViewName) || __('List View'),
    icon: 'list',
    onClick() {
      viewUpdated.value = false
      router.push({ name: route.name })
    },
  })
}
if (allowedViews.includes('group_by')) {
  defaultViews.push({
    label: __(props.options?.defaultViewName) || __('Group By View'),
    icon: markRaw(DetailsIcon),
    onClick() {
      viewUpdated.value = false
      router.push({ name: route.name, params: { viewType: 'group_by' } })
    },
  })
}

function getIcon(icon, type) {
  if (isEmoji(icon)) {
    return h('div', icon)
  } else if (!icon && type === 'group_by') {
    return markRaw(DetailsIcon)
  }
  return icon || 'list'
}

const viewsDropdownOptions = computed(() => {
  let _views = [
    {
      group: __('Default Views'),
      hideLabel: true,
      items: defaultViews,
    },
  ]

  // if (list.value?.data?.views) {
  //   list.value.data.views.forEach((view) => {
  //     view.label = __(view.label)
  //     view.type = view.type || 'list'
  //     view.icon = getIcon(view.icon, view.type)
  //     view.filters =
  //       typeof view.filters == 'string'
  //         ? JSON.parse(view.filters)
  //         : view.filters
  //     view.onClick = () => {
  //       viewUpdated.value = false
  //       router.push({
  //         name: route.name,
  //         params: { viewType: view.type },
  //         query: { view: view.name },
  //       })
  //     }
  //   })
  //   let publicViews = list.value.data.views.filter((v) => v.public)
  //   let savedViews = list.value.data.views.filter(
  //     (v) => !v.pinned && !v.public && !v.is_default
  //   )
  //   let pinnedViews = list.value.data.views.filter((v) => v.pinned)

  //   publicViews.length &&
  //     _views.push({
  //       group: __('Public Views'),
  //       items: publicViews,
  //     })

  //   savedViews.length &&
  //     _views.push({
  //       group: __('Saved Views'),
  //       items: savedViews,
  //     })
  //   pinnedViews.length &&
  //     _views.push({
  //       group: __('Pinned Views'),
  //       items: pinnedViews,
  //     })
  // }

  return _views
})

const quickFilterList = computed(() => {
  // let filters = [{ name: 'name', label: __('ID') }]
  let filters = []
  if (quickFilters.data) {
    filters.push(...quickFilters.data)
  }

  filters.forEach((filter) => {
    filter['value'] = filter.type == 'Check' ? false : ''
    if (list.value.params?.filters[filter.name]) {
      let value = list.value.params.filters[filter.name]
      if (Array.isArray(value)) {
        if (
          (['Check', 'Select', 'Link', 'Date', 'Datetime'].includes(
            filter.type,
          ) &&
            value[0]?.toLowerCase() == 'like') ||
          value[0]?.toLowerCase() != 'like'
        )
          return
        filter['value'] = value[1]?.replace(/%/g, '')
      } else if (typeof value == 'boolean') {
        filter['value'] = value
      } else {
        filter['value'] = value.replace(/%/g, '')
      }
    }
  })

  return filters
})

const quickFilters = createResource({
  url: 'go1_cms.api.doc.get_quick_filters',
  params: { doctype: props.doctype },
  cache: ['Quick Filters', props.doctype],
  auto: true,
})

function applyQuickFilter(filter, value) {
  let filters = { ...list.value.params.filters }
  let field = filter.name
  if (value) {
    if (['Check', 'Select', 'Link', 'Date', 'Datetime'].includes(filter.type)) {
      filters[field] = value
    } else {
      filters[field] = ['LIKE', `%${value}%`]
    }
    filter['value'] = value
  } else {
    delete filters[field]
    filter['value'] = ''
  }
  updateFilter(filters)
}

function updateFilter(filters) {
  viewUpdated.value = true
  if (!defaultParams.value) {
    defaultParams.value = getParams()
  }
  list.value.params = defaultParams.value
  list.value.params.filters = filters
  view.value.filters = filters
  list.value.reload()

  if (!route.query.view) {
    create_or_update_default_view()
  }
}

function updateSort(order_by) {
  viewUpdated.value = true
  if (!defaultParams.value) {
    defaultParams.value = getParams()
  }
  list.value.params = defaultParams.value
  list.value.params.order_by = order_by
  view.value.order_by = order_by
  list.value.reload()

  if (!route.query.view) {
    create_or_update_default_view()
  }
}

function updateGroupBy(group_by_field) {
  viewUpdated.value = true
  if (!defaultParams.value) {
    defaultParams.value = getParams()
  }
  list.value.params = defaultParams.value
  list.value.params.view.group_by_field = group_by_field
  view.value.group_by_field = group_by_field
  list.value.reload()

  if (!route.query.view) {
    create_or_update_default_view()
  }
}

function updateColumns(obj) {
  if (!obj) {
    obj = {
      columns: list.value.data.columns,
      rows: list.value.data.rows,
      isDefault: false,
    }
  }

  if (!defaultParams.value) {
    defaultParams.value = getParams()
  }
  defaultParams.value.columns = view.value.columns = obj.isDefault
    ? ''
    : obj.columns
  defaultParams.value.rows = view.value.rows = obj.isDefault ? '' : obj.rows
  view.value.load_default_columns = obj.isDefault

  if (obj.reset) {
    defaultParams.value.columns = getParams().columns
    defaultParams.value.rows = getParams().rows
  }

  if (obj.reload) {
    list.value.params = defaultParams.value
    list.value.reload()
  }
  viewUpdated.value = true

  if (!route.query.view) {
    create_or_update_default_view()
  }
}

function create_or_update_default_view() {
  if (route.query.view) return
  view.value.doctype = props.doctype
  call(
    'go1_cms.go1_cms.doctype.cms_view_settings.cms_view_settings.create_or_update_default_view',
    {
      view: view.value,
    },
  ).then(() => {
    reloadView()
    view.value = {
      label: view.value.label,
      type: view.value.type || 'list',
      icon: view.value.icon,
      name: view.value.name,
      filters: defaultParams.value.filters,
      order_by: defaultParams.value.order_by,
      group_by_field: defaultParams.value.view.group_by_field,
      columns: defaultParams.value.columns,
      rows: defaultParams.value.rows,
      route_name: route.name,
      load_default_columns: view.value.load_default_columns,
    }
    viewUpdated.value = false
  })
}

function updatePageLength(value, loadMore = false) {
  if (!defaultParams.value) {
    defaultParams.value = getParams()
  }
  list.value.params = defaultParams.value
  if (loadMore) {
    list.value.params.page_length += list.value.params.page_length_count
  } else {
    if (
      value == list.value.params.page_length &&
      value == list.value.params.page_length_count
    )
      return
    list.value.params.page_length = value
    list.value.params.page_length_count = value
  }
  list.value.reload()
}

// View Actions
const viewActions = computed(() => {
  let actions = [
    {
      group: __('Default Views'),
      hideLabel: true,
      items: [
        {
          label: __('Duplicate'),
          icon: () => h(DuplicateIcon, { class: 'h-4 w-4' }),
          onClick: () => duplicateView(),
        },
      ],
    },
  ]

  if (route.query.view && (!view.value.public || isManager())) {
    actions[0].items.push({
      label: __('Edit'),
      icon: () => h(EditIcon, { class: 'h-4 w-4' }),
      onClick: () => editView(),
    })

    if (!view.value.public) {
      actions[0].items.push({
        label: view.value.pinned ? __('Unpin View') : __('Pin View'),
        icon: () =>
          h(view.value.pinned ? UnpinIcon : PinIcon, { class: 'h-4 w-4' }),
        onClick: () => pinView(),
      })
    }

    if (isManager()) {
      actions[0].items.push({
        label: view.value.public ? __('Make Private') : __('Make Public'),
        icon: () =>
          h(FeatherIcon, {
            name: view.value.public ? 'lock' : 'unlock',
            class: 'h-4 w-4',
          }),
        onClick: () => publicView(),
      })
    }

    actions.push({
      group: __('Delete View'),
      hideLabel: true,
      items: [
        {
          label: __('Delete'),
          icon: 'trash-2',
          onClick: () =>
            $dialog({
              title: __('Delete View'),
              message: __('Are you sure you want to delete this view?'),
              variant: 'danger',
              actions: [
                {
                  label: __('Delete'),
                  variant: 'solid',
                  theme: 'red',
                  onClick: (close) => deleteView(close),
                },
              ],
            }),
        },
      ],
    })
  }
  return actions
})

const viewModalObj = ref({})

function duplicateView() {
  let label =
    __(
      getView(route.query.view, route.params.viewType, props.doctype)?.label,
    ) || getViewType().label
  view.value.name = ''
  view.value.label = label + __(' (New)')
  viewModalObj.value = view.value
  showViewModal.value = true
}

function editView() {
  let cView = getView(route.query.view, route.params.viewType, props.doctype)
  view.value.name = route.query.view
  view.value.label = __(cView?.label) || getViewType().label
  view.value.icon = cView?.icon || ''
  viewModalObj.value = view.value
  showViewModal.value = true
}

function publicView() {
  call('go1_cms.go1_cms.doctype.cms_view_settings.cms_view_settings.public', {
    name: route.query.view,
    value: !view.value.public,
  }).then(() => {
    view.value.public = !view.value.public
    reloadView()
  })
}

function pinView() {
  call('go1_cms.go1_cms.doctype.cms_view_settings.cms_view_settings.pin', {
    name: route.query.view,
    value: !view.value.pinned,
  }).then(() => {
    view.value.pinned = !view.value.pinned
    reloadView()
  })
}

function deleteView(close) {
  call('go1_cms.go1_cms.doctype.cms_view_settings.cms_view_settings.delete', {
    name: route.query.view,
  }).then(() => {
    router.push({ name: route.name })
    reloadView()
  })
  close()
}

function cancelChanges() {
  reload()
  viewUpdated.value = false
}

function saveView() {
  view.value = {
    label: view.value.label,
    type: view.value.type || 'list',
    icon: view.value.icon,
    name: view.value.name,
    filters: defaultParams.value.filters,
    order_by: defaultParams.value.order_by,
    group_by_field: defaultParams.value.view.group_by_field,
    columns: defaultParams.value.columns,
    rows: defaultParams.value.rows,
    route_name: route.name,
    load_default_columns: view.value.load_default_columns,
  }
  viewModalObj.value = view.value
  showViewModal.value = true
}

function applyFilter({ event, idx, column, item, firstColumn }) {
  let lstFieldIgnore = ['action_button']
  if (props.doctype == 'Mbw Blog Post') {
    lstFieldIgnore.push('category')
    lstFieldIgnore.push('tags')
  }
  if (lstFieldIgnore.includes(column.key)) return
  let restrictedFieldtypes = ['Duration', 'Datetime', 'Time']
  if (restrictedFieldtypes.includes(column.type) || idx === 0) return
  if (idx === 1 && firstColumn?.key == '_liked_by') return

  event.stopPropagation()
  event.preventDefault()

  let filters = { ...list.value.params.filters }

  let value = item.name || item.label || item

  if (value) {
    filters[column.key] = value
  } else {
    delete filters[column.key]
  }

  if (column.key == '_assign') {
    if (item.length > 1) {
      let target = event.target.closest('.user-avatar')
      if (target) {
        let name = target.getAttribute('data-name')
        filters['_assign'] = ['LIKE', `%${name}%`]
      }
    } else {
      filters['_assign'] = ['LIKE', `%${item[0].name}%`]
    }
  }
  updateFilter(filters)
}

function applyLikeFilter() {
  let filters = { ...list.value.params.filters }
  if (!filters._liked_by) {
    filters['_liked_by'] = ['LIKE', '%@me%']
  } else {
    delete filters['_liked_by']
  }
  updateFilter(filters)
}

function likeDoc({ name, liked }) {
  createResource({
    url: 'frappe.desk.like.toggle_like',
    params: { doctype: props.doctype, name: name, add: liked ? 'No' : 'Yes' },
    auto: true,
    onSuccess: () => reload(),
  })
}

defineExpose({ applyFilter, applyLikeFilter, likeDoc })

// Watchers
watch(
  () => getView(route.query.view, route.params.viewType, props.doctype),
  (value, old_value) => {
    if (_.isEqual(value, old_value)) return
    reload()
  },
  { deep: true },
)

watch([() => route, () => route.params.viewType], (value, old_value) => {
  if (value[0] === old_value[0] && value[1] === value[0]) return
  reload()
})
</script>
