import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLinkRefreshStore = defineStore('linkRefresh', () => {
  const refreshTrigger = ref(0)
  const lastCreatedDocument = ref(null)
  
  // Modal depth tracking
  const modalDepth = ref(0)
  const maxModalDepth = 2 // Giới hạn tối đa 2 cấp modal
  const modalStack = ref([])

  // Trigger refresh cho tất cả Link fields của doctype cụ thể
  function triggerLinkRefresh(doctype, docName = null) {
    lastCreatedDocument.value = {
      doctype,
      docName,
      timestamp: Date.now()
    }
    refreshTrigger.value++
    console.log(`🔄 Triggered Link refresh for ${doctype}`, docName)
  }

  // Clear trigger
  function clearRefreshTrigger() {
    lastCreatedDocument.value = null
  }

  // Modal depth management  
  function pushModal(modalName = 'Unknown') {
    modalDepth.value++
    modalStack.value.push(modalName)
    console.log(`📱 Modal opened [${modalName}]. Depth: ${modalDepth.value}/${maxModalDepth}`)
  }

  function popModal() {
    if (modalDepth.value > 0) {
      const closedModal = modalStack.value.pop()
      modalDepth.value--
      console.log(`📱 Modal closed [${closedModal}]. Depth: ${modalDepth.value}/${maxModalDepth}`)
    }
  }

  // Check if can show "Create New" button
  function canShowCreateNew() {
    const canShow = modalDepth.value < maxModalDepth
    console.log(`🔍 CanShowCreateNew check: depth=${modalDepth.value}, max=${maxModalDepth}, canShow=${canShow}, stack=[${modalStack.value.join(', ')}]`)
    if (!canShow) {
      console.log(`🚫 Cannot show "Create New" - reached max depth (${modalDepth.value}/${maxModalDepth})`)
    }
    return canShow
  }

  return {
    refreshTrigger,
    lastCreatedDocument,
    modalDepth,
    maxModalDepth,
    modalStack,
    triggerLinkRefresh,
    clearRefreshTrigger,
    pushModal,
    popModal,
    canShowCreateNew
  }
}) 