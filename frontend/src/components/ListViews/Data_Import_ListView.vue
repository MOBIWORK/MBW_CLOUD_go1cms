<template>
  <ListView :columns="columns" :rows="rows" :options="{
    onRowClick: (row) => navigateToImportDetail(row.name),
    
    selectable: options.selectable,
    showTooltip: options.showTooltip,
    resizeColumn: options.resizeColumn,
  }" row-key="name">
    <ListHeader class="mx-3 sm:mx-5" @columnWidthUpdated="emit('columnWidthUpdated')">
      <ListHeaderItem v-for="column in columns" :key="column.key" :item="column"
        @columnWidthUpdated="emit('columnWidthUpdated', column)">
      </ListHeaderItem>
    </ListHeader>
    <ListRows class="mx-3 sm:mx-5" :rows="rows" v-slot="{ idx, column, item }" :doctype="doctype">
      <div v-if="column.key === 'name'">
        <Tooltip :text="item">
          <div class="flex items-center gap-2 truncate text-base cursor-pointer">
            <div v-if="item" class="truncate">
              {{ item }}
            </div>
          </div>
        </Tooltip>
      </div>
      <div v-else-if="column.key === 'status'">
        <Badge
							:variant="'subtle'"
							:theme="theme_status(item)"
							size="md"
							:label="__(item)"
							
						/>
      </div>
      <ListRowItem v-else :item="item" :align="column.align">
        <template #prefix></template>
        <template #default="{ label }">
					<Tooltip :text="label">
						<div class="truncate text-base">
							{{ label }}
						</div>
					</Tooltip>
				</template>
          <!-- <div v-if="column.key === 'status'">
            <div class="h-4 w-4" :class="{
              'text-orange-500': item === 'Pending',
              'text-green-500': item === 'Success',
              'text-yellow-500': item === 'Partial Success',
            }" >{{item}}</div>
          </div> -->
        
      </ListRowItem>
    </ListRows>
    <ListSelectBanner>
      <template #actions="{ selections, unselectAll }">
        <Dropdown :options="listBulkActionsRef.bulkActions(selections, unselectAll)">
          <Button icon="more-horizontal" variant="ghost" />
        </Dropdown>
      </template>
    </ListSelectBanner>
  </ListView>
  <ListFooter class="border-t px-3 py-2 sm:px-5" v-model="pageLengthCount" :options="{
    rowCount: options.rowCount,
    totalCount: options.totalCount,
  }" @loadMore="emit('loadMore')" />
  <ListBulkActions ref="listBulkActionsRef" v-model="list" :doctype="doctype" :options="{
    hideAssign: true,
  }" />
</template>
<script setup>
import { useRoute, useRouter } from "vue-router";
const router = useRouter();


import TaskStatusIcon from '@/components/Icons/TaskStatusIcon.vue'

import ListBulkActions from '@/components/ListBulkActions.vue'
import ListRows from '@/components/ListViews/ListRows.vue'
import { formatDate } from '@/utils'
import {
  Avatar,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListSelectBanner,
  ListRowItem,
  ListFooter,
  Dropdown,
  Tooltip,
  Badge,
} from 'frappe-ui'
import { sessionStore } from '@/stores/session'
import { ref, computed, watch,provide } from 'vue'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
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

provide("hideEdit",true)
provide("hideDelete",true)
provide("editMode",true)

const emit = defineEmits([
  'loadMore',
  'updatePageCount',
  'showImport',
  'columnWidthUpdated',
  'applyFilter',
  'applyLikeFilter',
  'likeDoc',
])

const pageLengthCount = defineModel()
const list = defineModel('list')

const isLikeFilterApplied = computed(() => {
  return list.value.params?.filters?._liked_by ? true : false
})

const { user } = sessionStore()

function isLiked(item) {
  if (item) {
    let likedByMe = JSON.parse(item)
    return likedByMe.includes(user)
  }
}

const navigateToImportDetail = (importId) => {
  router.push({
    name: "Data Import Detail",
    params: { importId: encodeURIComponent(importId)},
  });
};


watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return
  emit('updatePageCount', val)
})

const listBulkActionsRef = ref(null)

defineExpose({
  customListActions: computed(
    () => listBulkActionsRef.value?.customListActions,
  ),
})

const theme_status = (status)=>{
  if(status == 'Success'){
    return 'green'
  }else if(status == 'Partial Success'){
    return 'blue'
  }else if(status == 'Error'){
    return 'red'
  }else if(status == 'Pending'){
    return 'orange'
  }else if(status == 'Timed Out'){
    return 'orange'
  }
}

const COLOR_MAP = {
	blue: '#318AD8',
	pink: '#F683AE',
	green: '#48BB74',
	red: '#F56B6B',
	yellow: '#FACF7A',
	purple: '#44427B',
	teal: '#5FD8C4',
	orange: '#F8814F',
	cyan: '#15CCEF',
	grey: '#A6B1B9',
	'#449CF0': '#449CF0',
	'#ECAD4B': '#ECAD4B',
	'#761ACB': '#761ACB',
	'#CB2929': '#CB2929',
	'#ED6396': '#ED6396',
	'#29CD42': '#29CD42',
	'#4463F0': '#4463F0',
	'#EC864B': '#EC864B',
	'#4F9DD9': '#4F9DD9',
	'#39E4A5': '#39E4A5',
	'#B4CD29': '#B4CD29',
};
</script>