import { ref } from 'vue'
import { useLinkRefreshStore } from '@/stores/linkRefresh'

export const showCreateDocumentModal = ref(false)
export const createDocumentDoctype = ref('')
export const createDocumentData = ref({})
export const createDocumentCallback = ref(null)

// Backup callback in non-reactive variable
let _callbackBackup = null

export function getCallbackBackup() {
  return _callbackBackup
}

export function createDocument(doctype, obj, close, callback) {
  if (doctype) {
    const linkRefreshStore = useLinkRefreshStore()
    
    // Chỉ đóng modal hiện tại nếu không ở nested modal
    // Hoặc nếu đang ở modal depth 1, có thể đóng để replace
    if (linkRefreshStore.modalDepth <= 1) {
      close?.()
    }
    
    console.log('📝 Setting callback in composables:', {
      callbackBefore: !!createDocumentCallback.value,
      callbackProvided: !!callback,
      callbackType: typeof callback
    })
    
    createDocumentDoctype.value = doctype
    createDocumentData.value = obj || {}
    createDocumentCallback.value = callback || null
    _callbackBackup = callback || null // Store in non-reactive backup
    
    console.log('📝 Callback set, checking:', {
      callbackAfter: !!createDocumentCallback.value,
      callbackValueType: typeof createDocumentCallback.value
    })
    
    showCreateDocumentModal.value = true
    
    // Check lại sau khi set modal = true
    setTimeout(() => {
      console.log('⏰ Callback after timeout:', {
        exists: !!createDocumentCallback.value,
        type: typeof createDocumentCallback.value
      })
    }, 100)
    
    console.log('🔥 CreateDocument called:', {
      doctype,
      currentDepth: linkRefreshStore.modalDepth,
      closedCurrent: linkRefreshStore.modalDepth <= 1,
      callbackProvided: !!callback,
      callbackType: typeof callback
    })
  }
}
