<template>
  <div class="flex h-screen w-screen relative">
    <div class="h-full bg-gray-50 border-r-2">
      <AppSidebar />
    </div>
    <div class="flex-1 flex flex-col h-full overflow-auto">
      <AppHeader />
      <slot />
    </div>
    <LoadingFullScreen></LoadingFullScreen>
  </div>
</template>
<script setup>
import LoadingFullScreen from '@/components/Loading.vue'
import AppSidebar from '@/components/Layouts/AppSidebar.vue'
import AppHeader from '@/components/Layouts/AppHeader.vue'
</script>
