import { createResource } from 'frappe-ui'
import { computed, ref } from 'vue'


export const mobileSidebarOpened = ref(false)

export const isMobileView = computed(() => window.innerWidth < 768)
