<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header>
      <div>
        <Button
          :variant="'solid'"
          theme="blue"
          size="sm"
          :label="__('Add New')"
          iconLeft="plus-circle"
          route="/menu/create"
        >
        </Button>
      </div>
    </template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full overflow-auto p-6 pt-2 pb-4">
    <ViewControls
      ref="viewControls"
      v-model="menu"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      :options="{
        hideColumnsButton: true,
      }"
      doctype="Menu"
    />
    <MenuListView
      v-if="menu.data && rows.length"
      v-model="menu.data.page_length_count"
      v-model:list="menu"
      :rows="rows"
      :columns="columns"
      :options="{
        rowCount: menu.data.row_count,
        totalCount: menu.data.total_count,
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
    ></MenuListView>
    <div v-else-if="menu.data" class="flex flex-1 items-center justify-center">
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <PostIcon class="h-10 w-10" />
        <span>{{ __('No menus available') }}</span>
        <Button :label="__('Add New')" route="/menu/create">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import PostIcon from '@/components/Icons/PostIcon.vue'
import MenuListView from '@/components/ListViews/MenuListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'

const breadcrumbs = [{ label: 'Menu', route: { name: 'Menu' } }]

// leads data is loaded in the ViewControls component
const menu = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Columns
const columns = computed(() => {
  if (!menu.value?.data?.columns) return []
  let _columns = menu.value?.data?.columns
  if (!_columns.find((el) => el.key == 'action_button')) {
    _columns.push({ label: __('Action'), key: 'action_button' })
  }
  return _columns
})

// Rows
const rows = computed(() => {
  if (!menu.value?.data?.data) return []
  return menu.value?.data.data.map((cat) => {
    let _rows = {}
    menu.value?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    _rows['action_button'] = { ...cat }
    return _rows
  })
})
</script>
