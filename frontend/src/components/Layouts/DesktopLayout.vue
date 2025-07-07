<template>
  <div class="flex h-screen w-screen relative">
    <div class="h-full bg-gray-50 border-r-2">
      <AppSidebar />
    </div>
    <GlobalModals />
    <div class="flex-1 flex flex-col h-full overflow-auto">
      <AppHeader />
      <slot />
    </div>
    <LoadingFullScreen></LoadingFullScreen>
    <ChatBox v-if="showChatBox" class="fixed bottom-6 right-6 z-50" />
  </div>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'
import { createResource } from 'frappe-ui'
import LoadingFullScreen from '@/components/Loading.vue'
import AppSidebar from '@/components/Layouts/AppSidebar.vue'
import AppHeader from '@/components/Layouts/AppHeader.vue'
import GlobalModals from '@/components/Modals/GlobalModals.vue'
import ChatBox from '@/components/ChatBox.vue'

const siteConfig = createResource({
  url: 'go1_cms.api.site_config.get_site_config',
  auto: true,
})

const showChatBox = computed(() => {
  const data = siteConfig.data
  return !data?.mbw_ats_site_name || data.mbw_ats_site_name === ''
})

</script>
