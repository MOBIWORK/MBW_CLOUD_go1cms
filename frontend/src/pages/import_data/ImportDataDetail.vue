<template>
  <header class="sticky top-0 z-10 flex items-center justify-between border-b bg-surface-white px-3 py-2.5 sm:px-5">
    <Breadcrumbs :items="breadcrumbs" />
    <div class="space-x-2">
      <Button variant="solid" @click="submitImport()" v-if="importDetails.data?.status != 'Success'">
        {{ action_primary }}
      </Button>
    </div>
  </header>
  <div class="p-6 overflow-auto">
    <div class="p-4 border border-gray-300 rounded-sm mb-4">
      <div class="mb-8">
        <div class="flex">
          <div class="font-semibold mb-4">
            {{ state }}
          </div>
          <Badge :variant="'subtle'" :theme="theme_status(status)" size="md" :label="__(status)" class="ml-2 mt-1" />

        </div>
        <div class="grid grid-cols-2 gap-5 mt-4 mb-8">
          <Link v-model="importData.reference_doctype" :label="__('Select a table')" doctype="DocType"
            v-if="!importDetails.data" :required="true" />
          <FormControl v-model="importData.reference_doctype" :label="__('Select a table')" :required="true"
            :disabled="true" v-if="importDetails.data?.name" />
          <FormControl v-model="importData.mute_emails" type="checkbox" :label="__('Dont Send Emails')"
            :disabled="true" />
          <FormControl v-if="!importDetails.data" :label="__('Import Type')" v-model="importData.import_type"
            type="select" :options="['', 'Insert New Records', 'Update Existing Records']" class="pb-2"
            :required="true" />
          <FormControl v-model="importData.import_type" :label="__('Import Type')" :required="true" :disabled="true"
            v-if="importDetails.data?.name" />
        </div>

        <div v-if="importDetails.data?.name">
          <div class="gap-5 mt-4 mb-8 space-y-1.5">
            <Button variant="subtle" @click="open = true">
              {{ __('Download Template') }}
            </Button>

            <div class="block text-xs text-ink-gray-5">Import file</div>

            <FileUploader :fileTypes="['.csv', '.xls', '.xlsx']" :upload-args="{
              doctype: 'Data Import',
              docname: importDetails.data?.name,
              private: false,
            }" v-model="importData.import_file" @success="
              (file) => {
                handleUploadSuccess(file)
              }
            ">
              <template v-slot="{
                file,
                uploading,
                progress,
                uploaded,
                message,
                error,
                total,
                success,
                openFileSelector,
              }">
                <div class="flex items-center gap-4">
                  <!-- Hiển thị tên file nếu có -->
                  <div v-if="importData.import_file" class="text-gray-700 truncate max-w-xs">
                    <a :href="importData.import_file" target="_blank" class="text-blue-600 underline">
                      {{ importData.import_file }}
                      <!-- Lấy tên file -->
                    </a>

                    <Button variant="ghost" @click="clearFile(importData.import_file)" class="text-red-500">
                      Clear
                    </Button>
                  </div>
                  <!-- Nút Upload -->
                  <Button v-if="!importData.import_file" variant="subtle" @click="openFileSelector()"
                    :loading="uploading">
                    <div class="flex gap-2">
                      {{ uploading ? `Uploading ${progress}%` : "Attach" }}
                    </div>
                  </Button>
                </div>
              </template>
            </FileUploader>

            <div class="block text-xs text-ink-gray-5">OR</div>
            <div class="p-2" description="Must be a publicly accessible Google Sheets URL">
              <FormControl v-model="importData.google_sheets_url" :label="__('Import from Google Sheets')" />
            </div>
            <div class="font-semibold mb-4">
              {{ __("Import File Errors and Warnings") }}
            </div>
            <template v-if="preview_from_template.data">
              <div class="row">
                <div class="col-sm-10 warnings">
                  <!-- Warnings grouped by row -->
                  <div v-for="(warnings, row) in warningsByRow" :key="row" class="warning space-y-2" :data-row="row">
                    <h4 class="text-uppercase">{{ __("Row " + [row]) }}</h4>
                    <div class="body">
                      <ul style="list-style:circle" class="p-30 text-p-base ml-30 space-y-1.5">
                        <li v-for="(w, index) in warnings" :key="index" style="margin-left: 35px;">
                          <template v-if="w.field">
                            <span v-html="w.field.label"></span>
                            <span v-if="w.field.parent !== importDetails.data?.reference_doctype">
                              ({{ w.field.parent }})
                            </span>
                            : <span v-html="w.message"></span>
                          </template>
                          <template v-else>
                            <span v-html="w.message"></span>
                          </template>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <!-- Other warnings (by column) -->
                  <div v-for="(warning, index) in otherWarnings" :key="'col-' + index" class="warning"
                    :data-col="warning.col">
                    <h4 v-if="columns[warning.col]">
                      <span class="text-uppercase">{{ __("Column " + [warning.col]) }}</span>
                      ({{ columns[warning.col].header_title }})
                    </h4>
                    <div class="body text-p-base space-y-2 ml-30"><span v-html="warning.message"></span></div>
                  </div>
                </div>
              </div>
            </template>
            <div v-if="import_log_count.data > 0" class="font-semibold mb-4">
              {{ __("Preview") }}
            </div>
            <template v-if="parsedLogs && parsedLogs.length > 0">
              <BaseTable :columns="[{ id: 1, 'row_indexes': 'Row number', 'status': 'Status', 'messages': 'Message' }]"
                :data="parsedLogs" mode="flat" />
              <!-- <table class="datatable dt-instance-3">
              <thead class="text-muted">
                <tr>
                  <th width="10%">{{ __("Row Number") }}</th>
                  <th width="10%">{{ __("Status") }}</th>
                  <th width="80%">{{ __("Message") }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="parsedLogs.length === 0">
                  <td class="text-center text-muted" colspan="3">
                    {{ __("No failed logs") }}
                  </td>
                </tr>
                <tr v-for="(log, index) in parsedLogs" :key="index">
                  <td>{{ log.rows }}</td>
                  <td>
                    <div :class="['indicator', log.indicator]">
                      {{ log.status }}
                    </div>
                  </td>
                  <td v-html="log.html"></td>
                </tr>
              </tbody>
            </table> -->
            </template>
          </div>
        </div>

      </div>
    </div>
  </div>

  <Dialog v-model="open" :options="{
    size: 'xl',
    title: 'Export Template',
  }">
    <template #title>Export Template</template>
    <template #body-content>
      <div class="max-h-[400px] overflow-y-auto">
        <div class="flex justify-between items-center mb-3">
          <div class="text-base font-semibold text-gray-800">Trường dữ liệu</div>
          <div class="space-x-2">
            <Button variant="outline" size="sm" @click="selectAll">{{ __("Select All") }}</Button>
            <Button variant="outline" size="sm" @click="selectMandatory">{{ __("Select Mandatory") }}</Button>
            <Button variant="outline" size="sm" @click="deselectAll">{{ __("UnSelect All") }}</Button>
          </div>
        </div>
        <div v-for="doc in allFields" :key="doc.name">
          <div class="font-semibold mb-4 mt-4 space-y-4">
            {{ doc.name }}
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="field in doc.fields" :key="field.name">
              <FormControl style="color:red" v-model="field.checked" type="checkbox"
                :label="__(field.label || field.fieldname)" />
            </div>
          </div>
        </div>
      </div>
    </template>
    <template #actions>
      <div class="flex justify-end gap-2">
        <Button variant="ghost" @click="open = false">{{ __("Cancel") }}</Button>
        <Button variant="solid" @click="downloadTemplate">{{ __("Export") }}</Button>
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import {
  Breadcrumbs,
  createResource,
  FormControl,
  ListSelectBanner,
  Button,
  toast,
  FileUploader,
  Dialog,
  Checkbox,
  call
} from 'frappe-ui'
import {
  computed,
  reactive,
  ref,
  onMounted,
  inject,
  onBeforeUnmount,
  watch,
} from 'vue'
import { showToast, updateDocumentTitle } from '@/utils'
import { useRouter, useRoute } from 'vue-router'
import BaseTable from "@/components/Table/BaseTable.vue";

const router = useRouter()
const route = useRoute()

const props = defineProps({
  importId: {
    type: String,
    required: true,
  },
})
const open = ref(false);
const loading = ref(false);
const allFields = ref([]);
const selectedFields = ref([]);
const chk = ref(false)

const importData = reactive({
  google_sheets_url: '',
  import_file: '',
  import_type: "",//["", "Insert New Records", "Update Existing Records"],
  mute_emails: true,
  payload_count: 0,
  reference_doctype: '',
  show_failed_logs: true,
  status: "Pending",//["Pending", "Success", "Partial Success", "Error", "Timed Out"],
  submit_after_import: false,
  template_options: '',
  template_warnings: []
})



onMounted(() => {
  if (props.importId.indexOf('new-data-import') == -1) {
    importDetails.reload()

  }
})

watch(
  () => props.importId.indexOf('new-data-import') == -1,
  (newVal) => {
    if (newVal) {
      importDetails.reload();

    }
  }
)
watch(open, (value) => {
  
  if (value && importData.reference_doctype) {
    getMeta(importData.reference_doctype);
  }
})

const getMeta = (doctype) => {
  console.log(doctype);
  const meta = createResource({
    url: "frappe.desk.form.load.getdoctype",
    params: {
      doctype: doctype,
      with_parent: 1,
      cached_timestamp: null,
    },
    cache: ["Meta", doctype]
    
  });
  meta.submit({},{
    onSuccess: (res) => {
      // let dtMetas = res.docs;
      // for (let dtMeta of dtMetas) {
      // 	doctypeMeta[dtMeta.name] = dtMeta;
      // }
      console.log(res);
      // userSettings[doctype] = JSON.parse(res.user_settings);
      allFields.value = res.docs
        .map(group => ({
          name: group.name,
          fields: group.fields
            .filter(f => f.fieldname && !['Section Break', 'Column Break', 'Link', 'Tab Break'].includes(f.fieldtype))
            .map(f => ({ ...f, checked: f.reqd ? true : false })) // Thêm thuộc tính checked
        }))
        .filter(group => group.fields.length > 0);
    },
    onError(err) {
      console.log(err);
    }
  })
}

const selectAll = () => {
  allFields.value.forEach(group => {
    group.fields.forEach(f => {
      f.checked = true;
    });
  });
};

function selectMandatory() {
  allFields.value.forEach(group => {
    group.fields.forEach(f => {
      f.checked = f.reqd ? true : false;
    });
  });
}

function deselectAll() {
  allFields.value.forEach(group => {
    group.fields.forEach(f => {
      f.checked = false;
    });
  });
}

const importDetails = createResource({
  url: 'frappe.client.get',
  makeParams(values) {
    return { doctype: 'Data Import', name: decodeURIComponent(props.importId) }
  },
  auto: false,
  onSuccess(data) {
    Object.keys(data).forEach((key) => {
      if (Object.hasOwn(importData, key)) importData[key] = data[key]
    })

    let checkboxes = [
      'mute_emails',
      'show_failed_logs',
      'submit_after_import',
    ]
    for (let idx in checkboxes) {
      let key = checkboxes[idx]
      importData[key] = importData[key] ? true : false
    }

    preview_from_template.fetch();
    import_log_count.reload();
    import_log.fetch()
  },
})
const importCreate = createResource({
  url: 'frappe.client.insert',
  auto: false,
  makeParams(values) {
    return {
      doc: {
        doctype: 'Data Import',
        ...importData,
      },
    }
  },
})

const importUpdate = createResource({
  url: 'frappe.client.set_value',
  auto: false,
  makeParams(values) {
    return {
      doctype: 'Data Import',
      name: values.importId,
      fieldname: {
        ...importData,
      },
    }
  },
})

const importStart = createResource({
  url: 'frappe.core.doctype.data_import.data_import.form_start_import',
  auto: false,
  makeParams(values) {
    return {
      doctype: 'Data Import',
      data_import: importDetails.data?.name,
    }
  },
})

const import_log = createResource({
  url: 'frappe.core.doctype.data_import.data_import.get_import_logs',
  makeParams(values) {
    return {
      data_import: importDetails.data?.name,
    }
  },
})
const preview_from_template = createResource({
  url: 'frappe.core.doctype.data_import.data_import.get_preview_from_template',
  makeParams(values) {
    return {
      data_import: importDetails.data?.name,
      import_file: importDetails.data?.import_file,
      google_sheets_url: importDetails.data?.google_sheets_url,
    }
  }
})
const import_log_count = createResource({
  url: 'frappe.client.get_count',
  auto: false,
  makeParams(values) {
    return {
      doctype: "Data Import Log",
      filters: {
        data_import: importDetails.data?.name,
      },
    }
  },
})

const download_template = createResource({
  url: 'frappe.core.doctype.data_import.data_import.download_template',
  method: 'POST',
  auto: false,
})

const getSelectedFields = () => {
  return allFields.value.flatMap(group =>
    group.fields.filter(f => f.checked)
  );
};
const downloadTemplate = () => {
  try {
    const selected = getSelectedFields();
    if (!selected.length) {
      showToast(__('Error'), __("Select field export"), 'x')
      return;
    }
    const grouped = {};

    for (const group of allFields.value) {
      const groupName = group.name;
      const selectedInGroup = group.fields
        .filter(f => f.checked)
        .map(f => f.fieldname);

      if (selectedInGroup.length > 0) {
        grouped[groupName] = selectedInGroup;
      }
    }


    const formData = new FormData();
    formData.append("doctype", importData.reference_doctype);
    formData.append("export_fields", JSON.stringify(grouped));
    formData.append('file_type', 'Excel'); // hoặc Excel
    formData.append('export_records', 'blank_template');
    formData.append('export_filters', null);

    // for (const [key, value] of formData.entries()) {
    //   console.log(`${key}:`, value);
    // }

    fetch("/api/method/frappe.core.doctype.data_import.data_import.download_template", {
      method: "POST",
      body: formData,
    })
      .then(async (res) => {
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = importData.reference_doctype + ".xlsx";
        a.click();
      })
      .catch((err) => {
        showToast(__('Error'), __("Export fail" + err), 'x')
      });
    // download_template.submit({
    //   body: formData,
    //   headers: {
    //     'Content-Type': undefined
    //   },
    //   onSuccess(response) {
    //     response.blob().then(blob => {
    //       const url = window.URL.createObjectURL(blob);
    //       const a = document.createElement('a');
    //       a.href = url;
    //       a.download = 'template.csv'; // hoặc .xlsx
    //       a.click();
    //       window.URL.revokeObjectURL(url);
    //     });
    //   },
    //   onError(e) {
    //     showToast(__('Error'), __("Export fail" + e), 'x')
    //   }
    // })
  } catch (e) {
    showToast(__('Error'), __("Export fail" + e), 'x')
  }
};

const submitImport = () => {
  if (importDetails.data?.status === "Pending" && (importDetails.data?.import_file || importDetails.data?.google_sheets_url)) {
    startImport();
  } else {

    if (importDetails.data?.name) updateImport()
    else createImport()
  }

}

const createImport = () => {
  importCreate.submit(
    {},
    {
      onSuccess(data) {
        showToast(__('Success'), __('Data Import created successfully'), 'check')
        router.push({
          name: 'Data Import Detail',
          params: { importId: encodeURIComponent(data.name) }
        })
      },
      onError(err) {
        showToast(__('Error'), __(err.messages?.[0] || err), 'x')
      },
    }
  )
}

const updateImport = () => {
  importUpdate.submit(
    { importId: importDetails.data?.name },
    {
      onSuccess(data) {
        importDetails.reload();
        showToast(__('Success'), __('Data Import updated successfully'), 'check')

      },
      onError(err) {
        showToast(__('Error'), __(err.messages?.[0] || err), 'x')
      },
    }
  )
}

const startImport = () => {
  importStart.submit({ data_import: importDetails.data?.name }, {
    onSuccess(data) {
      importDetails.reload();
      showToast(__('Success'), __('Data Import successfully'), 'check')
    },
    onError(err) {
      showToast(__('Error'), __(err.messages?.[0] || err), 'x')
    }
  })
}



const parsedLogs = computed(() => {
  return import_log.data?.map(log => {
    let html = '';
    if (log.success) {
      const link = ''//get_form_link(props.referenceDoctype, log.docname, true);
      html = importDetails.data?.importType === 'Insert New Records'
        ? __(`Successfully imported <span class="underline">${link}</span>`)
        : __(`Successfully updated <span class="underline">${link}</span>`);
    } else {
      const messages = JSON.parse(log || '[]')
        .map(m => {
          const title = m.title ? `<strong>${m.title}</strong>` : '';
          const message = m.message ? `<div>${m.message}</div>` : '';
          return title + message;
        }).join('');

      const id = `collapse-${Math.random().toString(36).substr(2, 8)}`; // unique ID

      html = `
          ${messages}
          <button class="btn btn-default btn-xs" type="button" @click="toggle('${id}')" style="margin-top: 15px;">
            ${__('Show Traceback')}
          </button>
          <div class="collapse" id="${id}" style="margin-top: 15px; display: none;">
            <div class="well">
              <pre>${log.exception}</pre>
            </div>
          </div>
        `;
    }

    return {
      rows: JSON.parse(log.row_indexes || '[]').join(', '),
      status: log.success ? __('Success') : __('Failure'),
      indicator: log.success ? 'green' : 'red',
      html
    };
  });
});

// columns from previewData
const columns = computed(() => {
  return preview_from_template.data?.columns || []
})

// merge all warnings
const allWarnings = computed(() => {
  const templateWarnings = JSON.parse(importData.template_warnings || '[]');
  return templateWarnings.concat(preview_from_template.data?.warnings || []);
});

// group warnings by row and collect others
const warningsByRow = computed(() => {
  const grouped = {};
  console.log(allWarnings.value)
  for (const warning of allWarnings.value) {
    if (warning.row) {
      if (!grouped[warning.row]) grouped[warning.row] = [];
      grouped[warning.row].push(warning);
    }
  }
  return grouped;
});

const otherWarnings = computed(() => {
  return allWarnings.value.filter(w => !w.row);
});



const action_primary = computed(() => {
  if (props.importId.indexOf('new-data-import') != -1) {
    return __("Save")
  } else {
    if (importDetails.data?.status !== "Success") {
      if (importDetails.data?.import_file || importDetails.data?.google_sheets_url) {
        let label = importDetails.data.status === "Pending" ? __("Start Import") : __("Retry");
        return label;
      } else {
        return __("Save")
      }

    }
  }
})

const state = computed(() => {
  if (props.importId.indexOf('new-data-import') != -1) {
    return __("New Data Import")
  } else {
    return importDetails.data?.name
  }
})

const status = computed(() => {
  if (props.importId.indexOf('new-data-import') != -1) {
    return __("Not Saved")
  } else {
    return importDetails.data?.status
  }
})

function validateFile(file) {
  let extn = file.name.split(".").pop().toLowerCase();
  if (!["png", "jpg", "jpeg"].includes(extn)) {
    return __("Only PNG and JPG images are allowed");
  }
}
function clearFile(fieldname) {
  importData.import_file = null;
}

const handleUploadSuccess = (file) => {
  importData.import_file = file.file_url
  submitImport()
}
const theme_status = (status) => {
  if (status == 'Success') {
    return 'green'
  } else if (status == 'Partial Success') {
    return 'blue'
  } else if (status == 'Error') {
    return 'red'
  } else if (status == 'Pending') {
    return 'orange'
  } else if (status == 'Timed Out') {
    return 'orange'
  } else {
    return 'orange'
  }
}
const breadcrumbs = computed(() => {
  let crumbs = [
    {
      label: __('Data Import'),
      route: {
        name: 'Data Import',
      },
    },
  ]
  crumbs.push({
    label: props.importId.indexOf('new-data-import') != -1 ? props.importId : importDetails.data?.name,
    route: { name: 'Data Import New', params: { importId: props.importId } },
  })
  return crumbs
})

const pageMeta = computed(() => {
  return {
    title: props.importId.indexOf('new-data-import') != -1 ? props.importId : importDetails.data?.name,
    description: __('Form to create and edit Import'),
  }
})

updateDocumentTitle(pageMeta)

</script>
