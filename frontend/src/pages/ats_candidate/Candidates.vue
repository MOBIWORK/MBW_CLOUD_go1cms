<template>
  <LayoutHeader>
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full overflow-auto p-6 pt-2 pb-4">
    <ViewControls
      ref="viewControls"
      v-model="candidates"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      :options="{
        hideColumnsButton: false,
      }"
      doctype="ATS_Candidate"
    />
    <CandidateListView
      v-if="candidates.data && rows.length"
      v-model="candidates.data.page_length_count"
      v-model:list="candidates"
      :rows="rows"
      :columns="columns"
      :options="{
        rowCount: candidates.data.row_count,
        totalCount: candidates.data.total_count,
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
    ></CandidateListView>
    <div
      v-else-if="candidates.data"
      class="flex flex-1 items-center justify-center"
    >
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <LeadsIcon class="h-10 w-10" />
        <span>{{ __('No candidates available') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import CandidateListView from '@/components/ListViews/CandidateListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { Breadcrumbs } from 'frappe-ui'
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { createToast } from "@/utils";
const breadcrumbs = [{ label: __('Candidate List'), route: { name: 'candidates' } }]


const candidates = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)
const isLoading = ref(false) // State to track loading

// Columns
const columns = computed(() => {
  if (!candidates.value?.data?.columns) return []

  let _columns = candidates.value?.data?.columns
  return _columns
})

// Rows
const rows = computed(() => {
  if (!candidates.value?.data?.data) return []
  return candidates.value?.data.data.map((cat) => {
    let _rows = {}
    candidates.value?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    _rows['action_button'] = { ...cat }
    return _rows
  })
})

</script>
