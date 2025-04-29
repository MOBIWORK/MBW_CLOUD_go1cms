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
    <ListRows id="list-rows" v-if="rows && rows.length" doctype="ATS_Candidate" 	class="relative">
      <ListRow
        v-for="row in rows"
        :key="row.name_web"
        v-slot="{ idx, column, item }"
        :row="row"
      >

        <div v-if="column.key === 'can_id'">
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
        <div v-else-if="column.key === 'can_application_date'">
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
        <div v-else-if="column.key === '_user_tags'">
          <div class="flex flex-col justify-center gap-1 max-w-full h-full">
            <span
              v-for="tag in item?.split(',').filter(Boolean)"
              :key="tag"
              class="px-2 py-1 text-xs rounded-md w-fit max-w-[160px] overflow-hidden whitespace-nowrap text-ellipsis"
              :style="{
                backgroundColor:
                  tagStore.tagByName[tag.trim()]?.candidatelabel_color || '#E5E7EB',
                color: getContrastTextColor(tagStore.tagByName[tag.trim()]?.candidatelabel_color), // Màu chữ nhẹ nhàng, dễ đọc
              }"
              :title="tag.trim()"
            >
              <Tooltip :text="tag.trim()">
                {{ tag.trim() }}
              </Tooltip>
            </span>
          </div>
        </div>
        <ListRowItem v-else :item="item" class="">
				<template #prefix> 
          <div v-if="column.key === 'can_phone'">
              <PhoneIcon class="h-4 w-4" />
          </div>
          <div v-if="column.key === 'can_email'">
            <EmailIcon class="h-4 w-4" />
          </div>
          <div v-if="column.key === 'can_full_name'">
            <Avatar
              class="flex items-center"
              :image="null"
              :label="item"
              size="md"
            />
          </div>
        </template>
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

function getContrastTextColor(hex) {
	const cleanedHex = hex?.replace('#', '');
	const r = parseInt(cleanedHex?.substring(0, 2), 16);
	const g = parseInt(cleanedHex?.substring(2, 4), 16);
	const b = parseInt(cleanedHex?.substring(4, 6), 16);

	// Công thức tính độ sáng (perceived brightness)
	const brightness = (r * 299 + g * 587 + b * 114) / 1000;

	// Nếu độ sáng lớn hơn 128 thì nền sáng → dùng chữ tối
	return brightness > 128 ? '#111827' : '#ffffff';
}

function formattedDateTooltip(dateStr) {
  const [year, month, day] = dateStr.split("-");
  return `${day}/${month}/${year}`;
}

watch(pageLengthCount, (val, old_value) => {
  if (val === old_value) return
  emit('updatePageCount', val)
})

</script>
