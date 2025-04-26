<template>
  <ListView
    :class="$attrs.class"
    :columns="columns"
    :rows="rows"
    :options="{
      selectable: options.selectable,
      showTooltip: options.showTooltip,
      resizeColumn: options.resizeColumn,
    }"
    row-key="name"
  >
    <ListHeader @columnWidthUpdated="emit('columnWidthUpdated')" />
    <ListRows id="list-rows" v-if="rows && rows.length">
      <ListRow
        v-for="row in rows"
        :key="row.name_web"
        v-slot="{ idx, column, item }"
        :row="row"
      >
        <ListRowItem
          :item="item"
          @click="(event) => emit('applyFilter', { event, idx, column, item })"
        >
          <template #prefix> </template>
          <Tooltip
            :text="item.label"
            v-if="
              [
                'modified',
                'creation',
                'first_response_time',
                'first_responded_on',
                'response_by',
              ].includes(column.key)
            "
            class="truncate text-base"
          >
            {{ item.timeAgo }}
          </Tooltip>
          <div
            v-else-if="column.key === 'sla_status'"
            class="truncate text-base"
          >
            <Badge
              v-if="item.value"
              :variant="'subtle'"
              :theme="item.color"
              size="md"
              :label="item.value"
            />
          </div>
        </ListRowItem>
      </ListRow>
    </ListRows>
  </ListView>
  <ListFooter
    v-if="pageLengthCount"
    class="border-t py-2"
    v-model="pageLengthCount"
    :options="{
      rowCount: options.rowCount,
      totalCount: options.totalCount,
    }"
    @loadMore="emit('loadMore')"
  />

</template>

<script setup>
import {
  ListView,
  ListHeader,
  ListRows,
  ListRow,
  ListRowItem,
  ListFooter,
  Tooltip,
} from 'frappe-ui'
import { ref, watch } from 'vue'
import { globalStore } from '@/stores/global'

const { changeLoadingValue } = globalStore()
const props = defineProps({
  rows: {
    type: Array,
    required: true,
  },
  columns: {
    type: Array,
    required: true,
  },
  options: {
    type: Object,
    default: () => ({
      selectable: true,
      showTooltip: true,
      resizeColumn: false,
      totalCount: 0,
      rowCount: 0,
    }),
  },
})

const emit = defineEmits([
  'loadMore',
  'updatePageCount',
  'columnWidthUpdated',
  'applyFilter',
])

const pageLengthCount = defineModel()
const list = defineModel('list')
const selectedItem = ref()

watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return
  emit('updatePageCount', val)
})

</script>
