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
    <ListRows id="list-rows" v-if="rows && rows.length" doctype="CMS_JobOpening" 	class="relative">
      <ListRow
        v-for="row in rows"
        :key="row.name_web"
        v-slot="{ idx, column, item }"
        :row="row"
      >
        <div v-if="column.key === 'jo_id'">
          <Tooltip :text="item">
            <div
              class="flex items-center gap-2 truncate text-base cursor-pointer"
            >
              <div v-if="item" class="truncate">
                {{ item }}
              </div>
            </div>
          </Tooltip>
        </div>
        <div v-else-if="column.key === 'jo_application_deadline'">
          <Tooltip
            :text="item && formattedDateTooltip(item)"
          >
            <div class="flex items-center gap-2 truncate text-base">
              <div><CalendarIcon /></div>
              <div v-if="item" class="truncate">
                {{ formattedDateTooltip(item) }}
              </div>
            </div>
          </Tooltip>
        </div>
        <div v-else-if="column.key === 'jo_public_title'">
          <Tooltip :text="item">
            <div
              class="flex items-center gap-2 truncate text-base cursor-pointer"
            >
              <div v-if="item" class="truncate">
                {{ item }}
              </div>
            </div>
          </Tooltip>
        </div>
        <div v-else-if="column.key === 'status'" class="truncate text-base">
          <div v-if="slaStatusColorMap.hasOwnProperty(item)">
            <Badge
              :variant="'subtle'"
              :theme="slaStatusColorMap[item]"
              size="md"
              :label="__(item)"
              @click="
                (event) =>
                  emit('applyFilter', {
                    event,
                    idx,
                    column,
                    item,
                    firstColumn: columns[0],
                  })
              "
            />
          </div>
        </div>
        <div v-else-if="column.key === 'publish_to_career_page'" class="truncate text-base">
          <div v-if="item === 0">
            <Badge
              :variant="'subtle'"
              :theme="publishColorMap[item]"
              size="md"
              :label="__(publishLabelMap[item])"
            />
          </div>
          <div v-else-if="item === 1">
            <Badge
              :variant="'subtle'"
              :theme="publishColorMap[item]"
              size="md"
              :label="__(publishLabelMap[item])"
            />
          </div>
        </div>
        <ListRowItem v-else :item="item" class="">
				<template #prefix> </template>
				<template #default="{ label }">
					<Tooltip :text="label">
						<div class="truncate text-base">
							{{ label }}
						</div>
					</Tooltip>
				</template>
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
  Avatar
} from 'frappe-ui'
import { ref, watch } from 'vue'
import { globalStore } from '@/stores/global'
import CalendarIcon from '@/components/Icons/CalendarIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
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

const slaStatusColorMap = {
	Draft: "gray",
	Open: "green",
	Paused: "yellow",
	"Closed for Applications": "red",
	Filled: "blue",
};

const publishColorMap = {
	0: "red",
	1: "green",
};

const publishLabelMap = {
	0: "UnPublish",
	1: "Published",
};

function formattedDateTooltip(dateStr) {
  const [year, month, day] = dateStr.split("-");
  return `${day}/${month}/${year}`;
}

watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return
  emit('updatePageCount', val)
})

</script>
