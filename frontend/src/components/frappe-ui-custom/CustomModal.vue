<template>
  <Teleport to="body">
    <Transition
      enter-active-class="duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
      @after-leave="$emit('after-leave')"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 overflow-y-auto custom-modal-container"
        :style="{ zIndex: zIndex }"
        :data-modal-z-index="zIndex"
        @click.self="handleBackdropClick"
      >
        <!-- Backdrop với z-index thấp hơn modal content -->
        <div 
          class="fixed inset-0 bg-black/50 backdrop-blur-sm"
          :style="{ zIndex: zIndex - 500 }"
        ></div>
        
        <!-- Modal Container -->
        <div class="flex min-h-full items-center justify-center p-4">
          <div
            v-if="modelValue"
            class="relative w-full rounded-lg bg-white shadow-xl"
            :class="sizeClasses"
            :style="{ 
              zIndex: zIndex + 100, 
              position: 'relative',
              transform: 'translateZ(0)' 
            }"
            @click.stop
          >
              <!-- Header -->
              <div class="border-b px-6 py-4 flex items-center justify-between">
                <h3 class="text-xl font-semibold text-gray-900">
                  {{ options.title || 'Modal' }}
                </h3>
                <div class="flex items-center gap-2">
                  <slot name="header-actions" />
                  <button
                    @click="close"
                    class="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
                  >
                    <FeatherIcon name="x" class="h-5 w-5" />
                  </button>
                </div>
              </div>

              <!-- Body -->
              <div class="px-6 py-4">
                <slot />
              </div>

              <!-- Footer -->
              <div v-if="options.actions?.length" class="border-t px-6 py-4 flex justify-end gap-3">
                <Button
                  v-for="action in options.actions"
                  :key="action.label"
                  v-bind="action"
                  @click="handleActionClick(action)"
                >
                  {{ action.label }}
                </Button>
              </div>
            </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted, watch, ref } from 'vue'
import { Button, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  options: {
    type: Object,
    default: () => ({})
  },
  closeOnBackdropClick: {
    type: Boolean,
    default: true
  },
  zIndexBase: {
    type: Number,
    default: 1000
  }
})

const emit = defineEmits(['update:modelValue', 'close', 'after-leave'])

// Reset counter và sử dụng z-index cố định thấp
if (!window.modalZIndexCounter) {
  window.modalZIndexCounter = 0
}

// Z-index thấp để dropdown 9999999 luôn trên top
const modalZIndex = ref(100 + (++window.modalZIndexCounter * 10))

const zIndex = computed(() => modalZIndex.value)

// Đã loại bỏ hasOpenDropdown tracking để tránh side effects

const sizeClasses = computed(() => {
  const size = props.options.size || 'lg'
  const sizeMap = {
    xs: 'max-w-xs',
    sm: 'max-w-sm', 
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    '3xl': 'max-w-3xl',
    '4xl': 'max-w-4xl',
    '5xl': 'max-w-5xl',
    '6xl': 'max-w-6xl',
    '7xl': 'max-w-7xl'
  }
  return sizeMap[size] || sizeMap.lg
})

function close() {
  emit('update:modelValue', false)
  emit('close')
}

function handleBackdropClick(event) {
  // Kiểm tra xem click có phải từ dropdown/popover không
  const isDropdownClick = event.target.closest('[data-headlessui-state="open"], [role="listbox"], [role="menu"], .popover, .rounded-lg.bg-white.shadow-2xl')
  
  if (isDropdownClick) {
    return
  }
  
  if (props.closeOnBackdropClick) {
    close()
  }
}

async function handleActionClick(action) {
  if (action.onClick) {
    try {
      await action.onClick({ close })
    } catch (error) {
      console.error('Action error:', error)
    }
  }
}

// Quản lý body scroll và đánh dấu modal đang mở
onMounted(() => {
  if (props.modelValue) {
    document.body.style.overflow = 'hidden'
    document.body.setAttribute('data-modal-open', 'true')
    document.body.classList.add('modal-active')
    
    // DISABLE tạm thời để modal hoạt động bình thường  
    // setTimeout(() => {
    //   forceOverrideDropdownZIndex()
    //   startDropdownObserver()
    // }, 100)
  }
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  // Cleanup observer và event listener
      stopDropdownObserver()
    document.removeEventListener('keydown', handleKeydown)
  
  // Chỉ khôi phục scroll nếu không còn modal nào khác đang mở
  const openModals = document.querySelectorAll('[data-modal-open="true"]').length
  if (openModals <= 1) {
    document.body.style.overflow = ''
    document.body.removeAttribute('data-modal-open')
    document.body.classList.remove('modal-active')
  }
})

// Force override z-index cho tất cả dropdown/popover elements
function forceOverrideDropdownZIndex() {
  try {
    // Selectors cho các dropdown elements
    const selectors = [
      '[data-headlessui-state="open"]',
      '[role="listbox"]',
      '[role="menu"]',
      '.popover',
      '.rounded-lg.bg-white.shadow-2xl',
      '.mt-1.rounded-lg.bg-white.py-1.text-base.shadow-2xl',
      // frappe-ui Popover specific selectors
      '#frappeui-popper-root .z-\\[100\\]',
      '#frappeui-popper-root > div',
      '.relative.z-\\[100\\]',
      '#frappeui-popper-root [class*="z-"]'
    ]
    
    selectors.forEach(selector => {
      try {
        const elements = document.querySelectorAll(selector)
        elements.forEach(el => {
          if (el) {
            el.style.setProperty('z-index', '9999999', 'important')
            // Thêm debug info
            if (el.classList.contains('z-[100]')) {
              console.log('🔧 Force override z-index for frappe-ui Popover:', el)
            }
          }
        })
      } catch (e) {
        // Ignore selector errors (như escaping issues)
      }
    })
    
    console.log('🚀 Force override z-index applied')
  } catch (error) {
    console.error('Error in forceOverrideDropdownZIndex:', error)
  }
}

// Observer để theo dõi DOM changes và override z-index
let dropdownObserver = null

function startDropdownObserver() {
  if (dropdownObserver) return
  
  try {
    dropdownObserver = new MutationObserver((mutations) => {
      let needsOverride = false
      
      mutations.forEach((mutation) => {
        // Kiểm tra node được thêm vào
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === 1) { // Element node
            // Kiểm tra nếu là popover hoặc dropdown
            if (
              node.classList?.contains('z-[100]') ||
              node.querySelector?.('.z-\\[100\\]') ||
              node.id === 'frappeui-popper-root' ||
              node.closest?.('#frappeui-popper-root')
            ) {
              needsOverride = true
            }
          }
        })
      })
      
      if (needsOverride) {
        // Delay nhỏ để đảm bảo DOM đã stable
        setTimeout(() => {
          forceOverrideDropdownZIndex()
        }, 10)
      }
    })
    
    // Observe toàn bộ document
    dropdownObserver.observe(document.body, {
      childList: true,
      subtree: true
    })
    
    console.log('🔍 Dropdown observer started')
  } catch (error) {
    console.error('Error starting dropdown observer:', error)
  }
}

function stopDropdownObserver() {
  if (dropdownObserver) {
    dropdownObserver.disconnect()
    dropdownObserver = null
  }
}

// Watch modelValue changes
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden'
    document.body.setAttribute('data-modal-open', 'true')
    document.body.classList.add('modal-active')
    
    // DISABLE tạm thời để modal hoạt động bình thường
    // setTimeout(() => {
    //   forceOverrideDropdownZIndex()
    //   startDropdownObserver()
    // }, 100)
  } else {
    stopDropdownObserver()
    
    // Delay để chờ transition hoàn thành
    setTimeout(() => {
      const openModals = document.querySelectorAll('[data-modal-open="true"]').length
      if (openModals <= 1) {
        document.body.style.overflow = ''
        document.body.removeAttribute('data-modal-open')
        document.body.classList.remove('modal-active')
      }
    }, 300)
  }
})

// Ngăn ESC key đóng modal cha khi có modal con
function handleKeydown(event) {
  if (event.key === 'Escape' && props.modelValue) {
    // Tìm modal có z-index cao nhất
    const allModalContainers = document.querySelectorAll('.custom-modal-container')
    let highestZIndex = 0
    let highestModal = null
    
    allModalContainers.forEach(modal => {
      const modalZIndex = parseInt(modal.style.zIndex || '0')
      if (modalZIndex > highestZIndex) {
        highestZIndex = modalZIndex
        highestModal = modal
      }
    })
    
    // Chỉ đóng modal hiện tại nếu nó có z-index cao nhất
    const currentModalContainer = event.target.closest('.custom-modal-container')
    
    if (currentModalContainer && currentModalContainer === highestModal) {
      close()
    }
  }
}


</script>

<style>
/* Minimal CSS - chỉ giữ những gì cần thiết */
</style> 