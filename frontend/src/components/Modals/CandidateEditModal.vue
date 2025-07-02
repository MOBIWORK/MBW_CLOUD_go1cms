<template>
  <!-- Edit Candidate Modal -->
  <Dialog v-model="showModal" :options="{ size: '4xl' }">
    <template #body-title>
      <h3 class="text-lg font-medium">{{ __("Chỉnh sửa ứng viên") }}</h3>
    </template>

    <template #body-content>
      <div v-if="candidateData" class="max-h-[70vh] overflow-y-auto">
        <FieldLayout 
          :tabs="candidateTabs" 
          :data="candidateData" 
          doctype="CMS_Candidate"
        />
      </div>
    </template>

    <template #actions>
      <div class="flex justify-end gap-2">
        <Button variant="subtle" @click="closeModal">
          {{ __("Huỷ") }}
        </Button>
        <Button variant="solid" @click="saveCandidate" :loading="isSaving">
          {{ __("Lưu") }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Dialog, FormControl, Button, call } from 'frappe-ui'
import { ref, computed, watch } from 'vue'
import { createToast } from "@/utils"
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  candidate: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

// Reactive data
const showModal = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const candidateData = ref(null)
const isSaving = ref(false)
const statusOptions = ref([])

// Candidate tabs structure using exact format requested
const candidateTabs = computed(() => [
  {
    label: __("Thông tin cơ bản"),
    name: "tab_basic_info",
    sections: [
      {
        label: __("Thông tin cá nhân"),
        name: "section_personal_info",
        columns: [
          {
            name: "column_left",
            fields: [
              {
                fieldname: "can_avatar",
                label: __("Ảnh đại diện"),
                fieldtype: "Attach Image"
              },
              {
                fieldname: "can_full_name",
                label: __("Họ và tên"),
                fieldtype: "Data",
                reqd: 1
              },
              {
                fieldname: "can_phone",
                label: __("Số điện thoại"),
                fieldtype: "Data"
              },
              {
                fieldname: "can_gender",
                label: __("Giới tính"),
                fieldtype: "Select",
                options: "Male\nFemale\nOther"
              }
            ]
          },
          {
            name: "column_right",
            fields: [
              {
                fieldname: "can_id",
                label: __("Candidate ID"),
                fieldtype: "Data",
                read_only: 1
              },
              {
                fieldname: "can_email",
                label: __("Email"),
                fieldtype: "Data",
                reqd: 1
              },
              {
                fieldname: "can_dob",
                label: __("Ngày sinh"),
                fieldtype: "Date"
              },
              {
                fieldname: "can_address",
                label: __("Địa chỉ"),
                fieldtype: "Small Text"
              }
            ]
          }
        ]
      },
      {
        label: __("Thông tin học vấn"),
        name: "section_education",
        columns: [
          {
            name: "column_education",
            fields: [
              {
                fieldname: "educationlevel_id",
                label: __("Trình độ học vấn"),
                fieldtype: "Link",
                options: "ATS_EducationLevel"
              },
              {
                fieldname: "institution_id",
                label: __("Trường học"),
                fieldtype: "Link", 
                options: "ATS_Institution"
              },
              {
                fieldname: "major_id",
                label: __("Chuyên ngành"),
                fieldtype: "Link",
                options: "ATS_Major"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    label: __("Ứng tuyển & Khác"),
    name: "tab_application",
    sections: [
      {
        label: __("Thông tin ứng tuyển"),
        name: "section_application",
        columns: [
          {
            name: "column_app_left",
            fields: [
              {
                fieldname: "can_application_date",
                label: __("Ngày ứng tuyển"),
                fieldtype: "Date"
              },
              {
                fieldname: "can_recruiter",
                label: __("Người tuyển dụng"),
                fieldtype: "Link",
                options: "User"
              },
              {
                fieldname: "can_referral",
                label: __("Người giới thiệu"),
                fieldtype: "Data"
              },
              {
                fieldname: "can_cv",
                label: __("CV"),
                fieldtype: "Attach"
              }
            ]
          },
          {
            name: "column_app_right",
            fields: [
              {
                fieldname: "status",
                label: __("Trạng thái"),
                fieldtype: "Select",
                options: statusOptions.value || ""
              },
              {
                fieldname: "can_collaborator",
                label: __("Người hỗ trợ"),
                fieldtype: "Link",
                options: "User"
              },
              {
                fieldname: "can_last_workplace",
                label: __("Nơi làm việc gần nhất"),
                fieldtype: "Data"
              },
              {
                fieldname: "candidatesource_id",
                label: __("Nguồn ứng viên"),
                fieldtype: "Link",
                options: "ATS_CandidateSource"
              }
            ]
          }
        ]
      },
      {
        label: __("Thông tin khác"),
        name: "section_other",
        columns: [
          {
            name: "column_other",
            fields: [
              {
                fieldname: "can_other_links",
                label: __("Liên kết khác"),
                fieldtype: "Small Text"
              },
              {
                fieldname: "can_region",
                label: __("Vùng/Tỉnh"),
                fieldtype: "Link",
                options: "ATS_Province"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    label: __("Kinh nghiệm & Thành tích"),
    name: "tab_experience",
    sections: [
      {
        label: __("Kinh nghiệm làm việc"),
        name: "section_work_experience",
        columns: [
          {
            name: "column_work_exp",
            fields: [
              {
                fieldname: "candidate_work_experience",
                label: __("Kinh nghiệm làm việc"),
                fieldtype: "Table",
                options: "Candidate_Work_Experience"
              }
            ]
          }
        ]
      },
      {
        label: __("Dự án"),
        name: "section_projects",
        columns: [
          {
            name: "column_projects",
            fields: [
              {
                fieldname: "candidate_project",
                label: __("Dự án"),
                fieldtype: "Table",
                options: "Candidate_Project"
              }
            ]
          }
        ]
      },
      {
        label: __("Chứng chỉ & Kỹ năng"),
        name: "section_certs_skills",
        columns: [
          {
            name: "column_certs",
            fields: [
              {
                fieldname: "candidate_certification",
                label: __("Chứng chỉ"),
                fieldtype: "Table",
                options: "Candidate_Certification"
              },
              {
                fieldname: "candidate_skill",
                label: __("Kỹ năng"),
                fieldtype: "Table",
                options: "Candidate_Skill"
              }
            ]
          }
        ]
      },
      {
        label: __("Giải thưởng & Khóa học"),
        name: "section_awards_courses",
        columns: [
          {
            name: "column_awards_courses",
            fields: [
              {
                fieldname: "candidate_award",
                label: __("Giải thưởng"),
                fieldtype: "Table",
                options: "Candidate_Award"
              },
              {
                fieldname: "candidate_course",
                label: __("Khóa học"),
                fieldtype: "Table",
                options: "Candidate_Course"
              }
            ]
          }
        ]
      }
    ]
  },
  // {
  //   label: __("Lịch sử & Stages"),
  //   name: "tab_history",
  //   sections: [
  //     {
  //       label: __("Stages ứng viên"),
  //       name: "section_stages",
  //       columns: [
  //         {
  //           name: "column_stages",
  //           fields: [
  //             {
  //               fieldname: "candidate_stages",
  //               label: __("Candidate Stages"),
  //               fieldtype: "Table",
  //               options: "Candidate Stages"
  //             }
  //           ]
  //         }
  //       ]
  //     },
  //     // {
  //     //   label: __("Lịch sử vòng tuyển"),
  //     //   name: "section_round_history",
  //     //   columns: [
  //     //     {
  //     //       name: "column_round_history",
  //     //       fields: [
  //     //         {
  //     //           fieldname: "round_history",
  //     //           label: __("Lịch sử vòng tuyển"),
  //     //           fieldtype: "Table",
  //     //           options: "ATS_CandidateRoundHistory"
  //     //         }
  //     //       ]
  //     //     }
  //     //   ]
  //     // },
  //     // {
  //     //   label: __("Từ chối"),
  //     //   name: "section_reject",
  //     //   columns: [
  //     //     {
  //     //       name: "column_reject",
  //     //       fields: [
  //     //         {
  //     //           fieldname: "rejected",
  //     //           label: __("Đã từ chối"),
  //     //           fieldtype: "Check"
  //     //         },
  //     //         {
  //     //           fieldname: "rejected_reason",
  //     //           label: __("Lý do từ chối"),
  //     //           fieldtype: "Data"
  //     //         },
  //     //         {
  //     //           fieldname: "rejected_round",
  //     //           label: __("Vòng từ chối"),
  //     //           fieldtype: "Data"
  //     //         }
  //     //       ]
  //     //     }
  //     //   ]
  //     // }
  //   ]
  // }
])

// Watch for candidate prop changes
watch(() => props.candidate, async (newCandidate) => {
  if (newCandidate) {
    // Deep clone to avoid mutating original data
    candidateData.value = JSON.parse(JSON.stringify(newCandidate))
    
    // Get status options if job_opening_id exists
    if (newCandidate.job_opening_id) {
      await getStatusOptions(newCandidate.job_opening_id)
    }
  }
}, { immediate: true })

// Methods
async function getStatusOptions(jobOpeningId) {
  if (!jobOpeningId) {
    statusOptions.value = ""
    return
  }
  
  try {
    const response = await call('go1_cms.go1_cms.doctype.cms_candidate.cms_candidate.get_job_opening_rounds', {
      job_opening: jobOpeningId
    })
    
    // Format as string for Select field in FieldLayout (newline separated)
    statusOptions.value = response.map(round => round.round_name).join('\n')
  } catch (error) {
    console.error('Error fetching status options:', error)
    statusOptions.value = ""
  }
}

async function saveCandidate() {
  if (!candidateData.value) return
  
  // Validation
  if (!candidateData.value.can_full_name || !candidateData.value.can_email) {
    createToast({
      title: __("Lỗi"),
      text: __("Họ tên và email là bắt buộc"),
      icon: "x",
      iconClasses: "text-red-600",
    })
    return
  }
  
  try {
    isSaving.value = true
    
    // Save entire document using frappe.client.save
    await call('frappe.client.save', {
      doc: candidateData.value
    })
    
    createToast({
      title: __("Thành công"),
      text: __("Cập nhật ứng viên thành công"),
      icon: "check",
      iconClasses: "text-green-600",
    })
    
    emit('saved')
    closeModal()
    
  } catch (error) {
    console.error('Error saving candidate:', error)
    createToast({
      title: __("Lỗi"),
      text: __(error.messages?.[0] || "Không thể cập nhật ứng viên"),
      icon: "x",
      iconClasses: "text-red-600",
    })
  } finally {
    isSaving.value = false
  }
}

function closeModal() {
  showModal.value = false
  candidateData.value = null
  statusOptions.value = ""
}
</script> 