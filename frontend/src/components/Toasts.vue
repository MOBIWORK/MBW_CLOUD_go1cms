<template>
  <Teleport to="body">
    <div
      id="toast-root"
      class="fixed inset-4 z-[9999] pointer-events-none"
    >
      <!-- Top Left -->
      <TransitionGroup
        tag="div"
        name="toast"
        class="absolute top-0 left-0"
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform translate-y-1 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in absolute"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform translate-y-1 opacity-0"
      >
        <div
          v-for="toast in getToastsByPosition('top-left')"
          :key="toast.key"
          class="pointer-events-auto flex"
        >
          <Toast v-bind="toast" @close="removeToast(toast)" />
        </div>
      </TransitionGroup>

      <!-- Top Center -->
      <TransitionGroup
        tag="div"
        name="toast"
        class="absolute top-0 left-1/2 -translate-x-1/2"
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform translate-y-1 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in absolute"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform translate-y-1 opacity-0"
      >
        <div
          v-for="toast in getToastsByPosition('top-center')"
          :key="toast.key"
          class="pointer-events-auto flex"
        >
          <Toast v-bind="toast" @close="removeToast(toast)" />
        </div>
      </TransitionGroup>

      <!-- Top Right -->
      <TransitionGroup
        tag="div"
        name="toast"
        class="absolute top-0 right-0"
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform translate-y-1 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in absolute"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform translate-y-1 opacity-0"
      >
        <div
          v-for="toast in getToastsByPosition('top-right')"
          :key="toast.key"
          class="pointer-events-auto flex"
        >
          <Toast v-bind="toast" @close="removeToast(toast)" />
        </div>
      </TransitionGroup>

      <!-- Bottom Left -->
      <TransitionGroup
        tag="div"
        name="toast"
        class="absolute bottom-0 left-0"
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform translate-y-1 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in absolute"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform translate-y-1 opacity-0"
      >
        <div
          v-for="toast in getToastsByPosition('bottom-left')"
          :key="toast.key"
          class="pointer-events-auto flex"
        >
          <Toast v-bind="toast" @close="removeToast(toast)" />
        </div>
      </TransitionGroup>

      <!-- Bottom Center -->
      <TransitionGroup
        tag="div"
        name="toast"
        class="absolute bottom-0 left-1/2 -translate-x-1/2"
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform translate-y-1 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in absolute"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform translate-y-1 opacity-0"
      >
        <div
          v-for="toast in getToastsByPosition('bottom-center')"
          :key="toast.key"
          class="pointer-events-auto flex"
        >
          <Toast v-bind="toast" @close="removeToast(toast)" />
        </div>
      </TransitionGroup>

      <!-- Bottom Right -->
      <TransitionGroup
        tag="div"
        name="toast"
        class="absolute bottom-0 right-0"
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="transform translate-y-1 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-200 ease-in absolute"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform translate-y-1 opacity-0"
      >
        <div
          v-for="toast in getToastsByPosition('bottom-right')"
          :key="toast.key"
          class="pointer-events-auto flex"
        >
          <Toast v-bind="toast" @close="removeToast(toast)" />
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>

import Toast from './Toast.vue'
import { toasts, removeToast } from '@/composables/useToast'

const getToastsByPosition = (position) => {
  return toasts.value.filter(toast => toast.position === position)
}
</script> 