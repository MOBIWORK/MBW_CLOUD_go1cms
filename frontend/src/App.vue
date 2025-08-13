<template>
  <div>
    <router-view
      v-if="
        ['Login', 'Permission Denied Page', 'Invalid Page'].includes($route.name)
      "
    />
    <WizardLayout v-else-if="$route.meta?.layout === 'wizard'">
      <router-view />
    </WizardLayout>
    <DesktopLayout v-else-if="session().isLoggedIn">
      <router-view />
    </DesktopLayout>
    <Dialogs />
    <Toasts />
  </div>
</template>

<script setup>
import DesktopLayout from '@/components/Layouts/DesktopLayout.vue'
import WizardLayout from '@/layouts/WizardLayout.vue'
import { Dialogs } from '@/utils/dialogs.js'
import { sessionStore as session } from '@/stores/session'
import Toasts from '@/components/Toasts.vue'
</script>
