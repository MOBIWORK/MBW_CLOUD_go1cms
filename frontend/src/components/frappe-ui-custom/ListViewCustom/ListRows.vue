<template>
  <ListRows class="" id="list-rows">
    <ListRowCustom
      v-for="row in reactivieRows"
      :key="row.name"
      v-slot="{ idx, column, item }"
      :row="row"
      @setChildRecord="setChildRecord"
      @deleteRecord="deleteRecord"
    >
      <slot v-bind="{ idx, column, item, row }" />
    </ListRowCustom>
  </ListRows>
</template>

<script setup>
import { ListRows } from "frappe-ui";
import ListRowCustom from "./ListRowCustom2.vue";

import { ref, computed, watch, defineEmits } from "vue";

const emit = defineEmits(["setChildRecord", "deleteRecord"]);

const props = defineProps({
  rows: {
    type: Array,
    required: true,
  },
});

const reactivieRows = ref(props.rows);

const setChildRecord = (data) => {
   console.log(data)
   emit('setChildRecord', data)
}

const deleteRecord = (data) => {
   console.log(data)
   emit('deleteRecord', data)
}


watch(
  () => props.rows,
  (val) => (reactivieRows.value = val)
);
</script>
