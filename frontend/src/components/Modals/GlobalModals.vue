<template>
  <CreateDocumentModal
    v-if="showCreateDocumentModal"
    v-model="showCreateDocumentModal"
    :doctype="createDocumentDoctype"
    :data="createDocumentData"
    @callback="(data) => {
      console.log('🎪 GlobalModals: CreateDocumentModal callback called', data)
      console.log('🔗 Reactive callback exists:', !!createDocumentCallback.value)
      
      const backupCallback = getCallbackBackup()
      console.log('🔗 Backup callback exists:', !!backupCallback)
      
      const callbackToUse = createDocumentCallback.value || backupCallback
      console.log('🔗 Using callback:', !!callbackToUse)
      
      if (callbackToUse) {
        console.log('📞 Calling Field callback...')
        callbackToUse(data)
      } else {
        console.log('❌ No callback function found in either reactive or backup!')
      }
    }"
  />
  	<!-- Temporarily commented QuickEntryModal -->
	<!-- <QuickEntryModal
		v-if="showQuickEntryModal"
		v-model="showQuickEntryModal"
		:doctype="quickEntryDoctype"
	/> -->
  <AboutModal v-model="showAboutModal" />
</template>
<script setup>
import CreateDocumentModal from '@/components/Modals/CreateDocumentModal.vue'
import AboutModal from '@/components/Modals/AboutModal.vue'
import {
  showCreateDocumentModal,
  createDocumentDoctype,
  createDocumentData,
  createDocumentCallback,
  getCallbackBackup,
} from '@/composables/document'
import { showAboutModal } from '@/composables/settings'
import { useLinkRefreshStore } from '@/stores/linkRefresh'
import { ref, watch } from 'vue'

// Temporarily commented quickEntry variables and function
/* const showQuickEntryModal = ref(false)
const quickEntryDoctype = ref('') */
const linkRefreshStore = useLinkRefreshStore()

/* function openQuickEntryModal(dt) {
  showQuickEntryModal.value = true
  quickEntryDoctype.value = dt
} */

// Debug: Watch createDocumentModal state
watch(() => showCreateDocumentModal.value, (newVal, oldVal) => {
  console.log('🎭 GlobalModals: showCreateDocumentModal changed', { 
    from: oldVal, 
    to: newVal,
    doctype: createDocumentDoctype.value,
    callbackExists: !!createDocumentCallback.value
  })
})

// Watch callback changes
watch(() => createDocumentCallback.value, (newVal, oldVal) => {
  console.log('🎭 GlobalModals: Callback changed!', {
    from: typeof oldVal,
    to: typeof newVal,
    hasCallback: !!newVal
  })
})

// Reset modal depth khi tất cả modal đóng
// Temporarily commented quickEntry watch
// Temporarily commented quickEntry watch
watch([() => showCreateDocumentModal.value], ([createModal]) => {
  console.log('🎭 GlobalModals: Modal states changed', { 
    createModal,
    callbackStillExists: !!createDocumentCallback.value 
  })
  if (!createModal) {
    // Reset modal depth khi không còn modal nào mở
    linkRefreshStore.modalDepth = 0
    console.log('🔄 Reset modal depth to 0 - all modals closed')
  }
})
</script>
