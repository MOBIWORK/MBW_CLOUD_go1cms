<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
    <template #right-header></template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full overflow-auto p-6 pt-2 pb-4">
    <ViewControls
      ref="viewControls"
      v-model="jobopenings"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      :options="{
        hideColumnsButton: false,
      }"
      doctype="CMS_JobOpening"
    />
    <JobOpeningListView
      v-if="jobopenings.data && rows.length"
      v-model="jobopenings.data.page_length_count"
      v-model:list="jobopenings"
      :rows="rows"
      :columns="columns"
      :options="{
        rowCount: jobopenings.data.row_count,
        totalCount: jobopenings.data.total_count,
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
    ></JobOpeningListView>
    <div
      v-else-if="jobopenings.data"
      class="flex flex-1 items-center justify-center"
    >
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <LeadsIcon class="h-10 w-10" />
        <span>{{ __('No job opening available') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import JobOpeningListView from '@/components/ListViews/JobOpeningListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'

const breadcrumbs = [{ label: __('JobOpening List'), route: { name: 'job_opening' } }]


const jobopenings = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Columns
const columns = computed(() => {
  if (!jobopenings.value?.data?.columns) return []

  let _columns = jobopenings.value?.data?.columns
  return _columns
})

// Rows
const rows = computed(() => {
  if (!jobopenings.value?.data?.data) return []
  return jobopenings.value?.data.data.map((cat) => {
    let _rows = {}
    jobopenings.value?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    return _rows
  })
})
</script>
