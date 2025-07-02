<template>
  <LayoutHeader v-if="!props.hideHeader">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs" />
    </template>
  </LayoutHeader>
  <div class="flex-1 flex flex-col h-full overflow-auto p-6 pt-2 pb-4">
    <ViewControls
      ref="viewControls"
      v-model="candidates"
      v-model:loadMore="loadMore"
      v-model:resizeColumn="triggerResize"
      v-model:updatedPageCount="updatedPageCount"
      :options="{
        hideColumnsButton: false,
      }"
      :filters="props.filters"
      doctype="CMS_Candidate"
    />
    <CandidateListView
      v-if="candidates.data && rows.length"
      v-model="candidates.data.page_length_count"
      v-model:list="candidates"
      :rows="rows"
      :columns="columns"
      :options="{
        rowCount: candidates.data.row_count,
        totalCount: candidates.data.total_count,
        selectable: false,
        showTooltip: false,
        resizeColumn: true,
      }"
      @loadMore="() => loadMore++"
      @columnWidthUpdated="() => triggerResize++"
      @updatePageCount="(count) => (updatedPageCount = count)"
      @applyFilter="(data) => viewControls.applyFilter(data)"
      @editCandidate="openEditModal"
      @viewCandidate="openViewModal"
    ></CandidateListView>
    <div
      v-else-if="candidates.data"
      class="flex flex-1 items-center justify-center"
    >
      <div
        class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
      >
        <LeadsIcon class="h-10 w-10" />
        <span>{{ __('No candidates available') }}</span>
      </div>
    </div>
  </div>

  <!-- Edit Candidate Modal -->
  <CandidateEditModal 
    v-model="showEditModal" 
    :candidate="editingCandidate"
    @saved="handleCandidateSaved"
  />

  <!-- View Candidate Modal -->
  <Dialog v-model="showViewModal" :options="{ size: '4xl' }">
    <template #body-title>
      <h3 class="text-lg font-medium">{{ __("Xem chi tiết ứng viên") }}</h3>
    </template>

    <template #body-content>
      <div v-if="viewingCandidate" class="max-h-[70vh] overflow-y-auto">
        <div class="space-y-6">
          <!-- Basic Information Section -->
          <div class="border rounded-lg p-4">
            <h4 class="text-md font-semibold mb-4 text-gray-800">{{ __("Thông tin cơ bản") }}</h4>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Candidate ID") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_id || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Họ và tên") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_full_name || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Email") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_email || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Số điện thoại") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_phone || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Ngày sinh") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_dob || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Giới tính") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_gender || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Địa chỉ") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_address || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Liên kết khác") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_other_links || '-' }}</p>
              </div>
            </div>
          </div>

          <!-- Education Information Section -->
          <div class="border rounded-lg p-4">
            <h4 class="text-md font-semibold mb-4 text-gray-800">{{ __("Thông tin học vấn") }}</h4>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Trình độ học vấn") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.educationlevel_id || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Trường học") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.institution_id || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Chuyên ngành") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.major_id || '-' }}</p>
              </div>
            </div>
          </div>

          <!-- Application Information Section -->
          <div class="border rounded-lg p-4">
            <h4 class="text-md font-semibold mb-4 text-gray-800">{{ __("Thông tin ứng tuyển") }}</h4>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Ngày ứng tuyển") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_application_date || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Trạng thái") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.status || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Người tuyển dụng") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_recruiter || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Người hỗ trợ") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_collaborator || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Người giới thiệu") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_referral || '-' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">{{ __("Nơi làm việc gần nhất") }}</label>
                <p class="text-sm text-gray-900 p-2 bg-gray-50 rounded">{{ viewingCandidate.can_last_workplace || '-' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <template #actions>
      <div class="flex justify-end">
        <Button variant="subtle" @click="showViewModal = false">
          {{ __("Đóng") }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import LayoutHeader from '@/components/LayoutHeader.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import CandidateListView from '@/components/ListViews/CandidateListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import { Breadcrumbs, Dialog, FormControl, Button, call } from 'frappe-ui'
import CandidateEditModal from '@/components/Modals/CandidateEditModal.vue'
import { ref, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { createToast } from "@/utils";
const breadcrumbs = [{ label: __('Candidate List'), route: { name: 'candidates' } }]


const props = defineProps({
	filters: {
		type: Object,
		default: {},
	},
	hideHeader: {
		type: Boolean,
		default: false,
	},
	displayCount: {
		type: Boolean,
		default: false,
	},
	jobOpeningId: {
		type: String,
		default: "",
	},

	candidateView: {
		type: Boolean,
		default: false,
	},
});


const candidates = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)
const isLoading = ref(false) // State to track loading

// Modal states
const showEditModal = ref(false)
const showViewModal = ref(false)
const editingCandidate = ref(null)
const viewingCandidate = ref(null)

// Columns
const columns = computed(() => {
  if (!candidates.value?.data?.columns) return []

  let _columns = candidates.value?.data?.columns
  return _columns
})

// Rows
const rows = computed(() => {
  if (!candidates.value?.data?.data) return []
  return candidates.value?.data.data.map((cat) => {
    let _rows = {}
    candidates.value?.data.rows.forEach((row) => {
      _rows[row] = cat[row]
    })
    _rows['action_button'] = { ...cat }
    return _rows
  })
})



// Removed unused field tabs configurations since we're using simple form layout

// Modal functions
async function openEditModal(candidate) {
  try {
    isLoading.value = true
    
    // Get full candidate data
    const candidateData = await call('frappe.client.get', {
      doctype: 'CMS_Candidate',
      name: candidate.name
    })
    
    editingCandidate.value = candidateData
    showEditModal.value = true
  } catch (error) {
    createToast({
      title: __("Lỗi"),
      text: __("Không thể tải thông tin ứng viên"),
      icon: "x",
      iconClasses: "text-red-600",
    })
  } finally {
    isLoading.value = false
  }
}

async function openViewModal(candidate) {
  try {
    isLoading.value = true
    
    // Get full candidate data
    const candidateData = await call('frappe.client.get', {
      doctype: 'CMS_Candidate',
      name: candidate.name
    })
    
    viewingCandidate.value = { ...candidateData }
    showViewModal.value = true
  } catch (error) {
    createToast({
      title: __("Lỗi"),
      text: __("Không thể tải thông tin ứng viên"),
      icon: "x",
      iconClasses: "text-red-600",
    })
  } finally {
    isLoading.value = false
  }
}

function handleCandidateSaved() {
  // Reload candidate list after successful save
  viewControls.value?.reloadData()
  editingCandidate.value = null
}

</script>
