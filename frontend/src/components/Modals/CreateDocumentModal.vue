<template>
  <CustomModal v-model="show" :options="dialogOptions" :close-on-backdrop-click="false">
    <template #header-actions>
      <!-- Temporarily commented quickEntry button -->
      <!-- <Button
        v-if="isManager() && !isMobileView"
        variant="ghost"
        class="w-7"
        @click="openQuickEntryModal"
      >
        <EditIcon class="h-4 w-4" />
      </Button> -->
    </template>
    
    <div v-if="tabs.data" class="space-y-4">
      <FieldLayout :tabs="tabs.data" :data="_data" :doctype="doctype" :disableCreate="true" />
      <ErrorMessage class="mt-2" :message="error" />
    </div>
  </CustomModal>
</template>

<script setup>
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import CustomModal from '@/components/frappe-ui-custom/CustomModal.vue'
import { usersStore } from '@/stores/users'
import { Button, createResource, ErrorMessage, call } from 'frappe-ui'
import { ref, nextTick, watch, computed, onUnmounted } from 'vue'
import { useLinkRefreshStore } from '@/stores/linkRefresh'

const props = defineProps({
  doctype: {
    type: String,
    required: true,
  },
  data: {
    type: Object,
    default: () => ({}),
  },
  disableOutsideClickToClose: {
    type: Boolean,
    default: true,
  },
})

// Temporarily commented quickEntry emit
const emit = defineEmits([/* 'showQuickEntryModal', */ 'callback'])

const { isManager } = usersStore()
const linkRefreshStore = useLinkRefreshStore()

const show = defineModel()

const loading = ref(false)
const error = ref(null)
const isCreating = ref(false) // Prevent duplicate calls

let _data = ref({})

const dialogOptions = computed(() => {
  let doctype = props.doctype;

  console.log('📥 Original doctype:', doctype);

  // Kiểm tra nếu bắt đầu bằng ATS_
  if (doctype.startsWith('ATS_')) {
    doctype = doctype.replace(/^ATS_/, '');
    console.log('🔧 Doctype after stripping ATS_ prefix:', doctype);
  }

  // Dịch tiêu đề
  const title = __('New {0}', [doctype]);
  const size = 'xl';

  const actions = [
    {
      label: __('Create'),
      variant: 'solid',
      loading: loading.value,
      disabled: isCreating.value,
      onClick: () => {
        console.log('🎯 Button clicked! Calling handleCreate...');
        handleCreate();
      },
    },
  ];

  console.log('📦 Computed dialogOptions:', { title, size, actions });

  return { title, size, actions };
});


const tabs = createResource({
  url: 'go1_cms.go1_cms.doctype.mbw_ats_fields_layout.mbw_ats_fields_layout.get_fields_layout',
  cache: ['QuickEntry', props.doctype],
  params: { doctype: props.doctype, type: 'Quick Entry' },
  auto: true,
})

async function handleCreate() {
  // Prevent duplicate calls
  if (isCreating.value) {
    console.log('🚫 Create already in progress, ignoring duplicate call')
    return
  }

  console.log('🚀 Starting create process...')
  isCreating.value = true
  loading.value = true
  error.value = null

  try {
    let doc = await call(
      'frappe.client.insert',
      {
        doc: {
          doctype: props.doctype,
          ..._data.value,
        },
      }
    )

    console.log('✅ Document created successfully:', doc)
    loading.value = false
    isCreating.value = false
    show.value = false
    
    console.log('🔄 Emitting callback with doc:', doc)
    emit('callback', doc)
  } catch (err) {
    console.log('❌ Create failed:', err)
    loading.value = false
    isCreating.value = false
    if (err.error) {
      error.value = err.error.messages?.[0]
    }
  }
}

watch(
  () => show.value,
  (value) => {
    if (value) {
      // Track modal khi mở
      linkRefreshStore.pushModal()
      // Reset states when opening modal
      isCreating.value = false
      loading.value = false
      error.value = null
      nextTick(() => {
        _data.value = { ...props.data }
      })
    } else {
      // Track modal khi đóng
      linkRefreshStore.popModal()
      // Reset creating state when closing
      isCreating.value = false
    }
  },
)

// Cleanup modal depth nếu component bị unmount khi modal còn mở
onUnmounted(() => {
  if (show.value) {
    linkRefreshStore.popModal()
  }
  // Reset creating state on unmount
  isCreating.value = false
})

// Temporarily commented quickEntry function
/* function openQuickEntryModal() {
  emit('showQuickEntryModal', props.doctype)
  nextTick(() => {
    show.value = false
  })
} */
</script>
