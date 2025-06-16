<template>
  <Teleport to="#app-header" v-if="showHeader">
    <header
      class="flex items-center justify-between px-5 py-2.5 min-h-14"
    >
      <div class="header_left flex-1">
        <slot name="left-header" />
      </div>
      <div class="header_center flex-1 flex justify-center">
        <slot name="center-header" />
      </div>
      <div class="header_right flex-1 flex justify-end">
        <slot name="right-header" />
      </div>
    </header>
  </Teleport>
</template>
<script setup>
import { ref, nextTick } from 'vue'

const showHeader = ref(false)

nextTick(() => {
  showHeader.value = true
})
</script>
<style>
.header_left > div > div {
  flex-wrap: wrap;
  white-space: normal;
}
</style>
