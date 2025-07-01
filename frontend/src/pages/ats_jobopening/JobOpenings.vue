<template>
  <div class="flex flex-col h-full">
    <LayoutHeader>
      <template #left-header>
        <Breadcrumbs :items="breadcrumbs" />
      </template>
      <template #right-header>
        <Button variant="solid" :label="__('Create')" @click="handleCreateClick">
          <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
        </Button>
      </template>
    </LayoutHeader>
    <div class="flex-1 flex flex-col h-full overflow-auto p-6 pt-2 pb-4">
      <ViewControls ref="viewControls" v-model="jobopenings" v-model:loadMore="loadMore"
        v-model:resizeColumn="triggerResize" v-model:updatedPageCount="updatedPageCount" :options="{
          hideColumnsButton: false,
        }" doctype="CMS_JobOpening" />
      <JobOpeningListView v-if="jobopenings.data && rows.length" v-model="jobopenings.data.page_length_count"
        v-model:list="jobopenings" :rows="rows" :columns="columns" :options="{
          rowCount: jobopenings.data.row_count,
          totalCount: jobopenings.data.total_count,
          selectable: false,
          showTooltip: false,
          resizeColumn: true,
        }" @loadMore="() => loadMore++" @columnWidthUpdated="() => triggerResize++"
        @updatePageCount="(count) => (updatedPageCount = count)"
        @applyFilter="(data) => viewControls.applyFilter(data)"
        @showModal="showModal">
      </JobOpeningListView>
      <div v-else-if="jobopenings.data" class="flex flex-1 items-center justify-center">
        <div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500">
          <LeadsIcon class="h-10 w-10" />
          <span>{{ __('No job opening available') }}</span>
          <Button :label="__('Create')" @click="handleCreateClick">
            <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
          </Button>
        </div>
      </div>
    </div>

    <!-- Job Opening Multi-Step Form Modal -->
    <JobOpeningMultiStepForm
      v-if="showJobOpeningModal"
      v-model="showJobOpeningModal"
      :editMode="editMode"
      :initialData="selectedJobOpening"
      @success="handleJobOpeningCreated"
      @draft-deleted="handleDraftDeleted"
    />
  </div>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import JobOpeningListView from '@/components/ListViews/JobOpeningListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import JobOpeningMultiStepForm from '@/components/Modals/JobOpeningSteps/JobOpeningMultiStepForm.vue'
import { Breadcrumbs, FeatherIcon } from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'
import { createResource, Button } from 'frappe-ui'

const breadcrumbs = [{ label: __('JobOpening List'), route: { name: 'job_opening' } }]

const jobopenings = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Modal states
const showJobOpeningModal = ref(false)
const editMode = ref(false)
const selectedJobOpening = ref({})

// Site config resource
const siteConfig = createResource({
  url: 'go1_cms.api.site_config.get_site_config',
  auto: true,
  onSuccess: (data) => {
    console.log('Site config loaded:', data)
  }
})

// Load site config on mount
onMounted(() => {
  siteConfig.fetch()
})

// Handle create button click
const handleCreateClick = () => {
  // Check if there's existing draft
  const existingDraft = sessionStorage.getItem('cms_job_opening_draft');
  
  console.log('🔍 handleCreateClick - existingDraft:', existingDraft);
  
  if (existingDraft) {
    // Show confirmation dialog
    const confirmed = window.confirm('Phát hiện bản nháp đã lưu. Bạn có muốn tiếp tục bản nháp không?\n\n- Chọn OK để tiếp tục với bản nháp.\n- Chọn Cancel để xóa bản nháp và tạo mới.');
    
    if (confirmed) {
      // Continue with existing draft
      console.log('✨ Continuing with existing draft');
      editMode.value = false;
      selectedJobOpening.value = {};
      showJobOpeningModal.value = true;
      return;
    } else {
      // Delete draft if user chooses to start fresh
      console.log('🗑️ User choose to delete draft and start fresh');
      sessionStorage.removeItem('cms_job_opening_draft');
    }
  }
  
  // Show form for new job opening
  console.log('✨ Showing job opening form');
  editMode.value = false;
  selectedJobOpening.value = {};
  showJobOpeningModal.value = true;
};

// Handle showing modal for editing existing job opening
const showModal = (name) => {
  const jobOpening = rows.value?.find((row) => row.name === name);
  if (jobOpening) {
    selectedJobOpening.value = { ...jobOpening };
  }
  editMode.value = true;
  showJobOpeningModal.value = true;
};

// Handle successful job opening creation
const handleJobOpeningCreated = (data) => {
  console.log("✅ CMS Job Opening created successfully:", data);
  
  // Force reload list data
  if (jobopenings.value && typeof jobopenings.value.reload === 'function') {
    jobopenings.value.reload();
    console.log("🔄 List data reloaded");
  } else {
    console.warn("❌ jobopenings.reload() not available");
  }
  
  // Close modal
  showJobOpeningModal.value = false;
  
  // Clear any remaining session storage
  const beforeClear = sessionStorage.getItem('cms_job_opening_draft');
  console.log("📝 SessionStorage before clear:", beforeClear);
  sessionStorage.removeItem('cms_job_opening_draft');
  const afterClear = sessionStorage.getItem('cms_job_opening_draft');
  console.log("🗑️ SessionStorage after clear:", afterClear);
};

// Handle draft deletion
const handleDraftDeleted = () => {
  // When draft is deleted, just close modal
  showJobOpeningModal.value = false;
};

// Columns
const columns = computed(() => {
  if (!jobopenings.value?.data?.columns) return []

  let _columns = jobopenings.value?.data?.columns
  return _columns
})

// Rows
const rows = computed(() => {
  if (!jobopenings.value?.data?.data) return []
  return jobopenings.value?.data.data.map((cat) => {
    let _rows = {}
    jobopenings.value?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    return _rows
  })
})
</script>
