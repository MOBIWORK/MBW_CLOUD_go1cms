import { ref, reactive } from 'vue'

export const toasts = ref([])

export function toast(options) {
  const id = `toast-${Math.random().toString(36).slice(2, 9)}`
  const toastObj = reactive({
    key: id,
    position: 'bottom-right',
    timeout: 5,
    ...options,
  })
  
  toasts.value.push(toastObj)
  
  return id
}

export function removeToast(toastToRemove) {
  const index = toasts.value.findIndex(toast => toast === toastToRemove)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

export function clearAllToasts() {
  toasts.value = []
}

export function removeToastById(id) {
  const index = toasts.value.findIndex(toast => toast.key === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
} 