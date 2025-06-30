<template>
    <LayoutHeader>
        <template #left-header>
            <Breadcrumbs :items="breadcrumbs" />
        </template>
        <template #right-header>
            <Button variant="solid" :label="__('Add Data Import')" @click ="() =>navigateToImportNew()">
                <template #prefix>
                    <FeatherIcon name="plus" class="h-4" />
                </template>
            </Button>
        </template>
    </LayoutHeader>
    <ViewControls ref="viewControls" v-model="listData" v-model:loadMore="loadMore" v-model:resizeColumn="triggerResize"
        v-model:updatedPageCount="updatedPageCount" :doctype="'Data Import'" :enableGroupSearch="true"  />
    <DataImportListView ref="dataListView" v-if="listData.data && rows && rows.length"
        v-model="listData.data.page_length_count" v-model:list="listData" :doctype="doctype" :rows="rows"
        :columns="listData.data?.columns || []" :options="{
            showTooltip: false,
            resizeColumn: true,
            rowCount: listData.data?.row_count || 0,
            totalCount: listData.data?.total_count || 0,
        }" @showImport="navigateToImportDetail" @loadMore="() => loadMore++" @columnWidthUpdated="() => triggerResize++"
        @updatePageCount="(count) => (updatedPageCount = count)"        
        @applyFilter="(data) => viewControls.applyFilter(data)" />

    <div v-else-if="listData.data" class="flex h-full items-center justify-center">
        <div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500">
            <span>{{ __("No Data Found") }}</span>
            <Button :label="__('Create')" @click="handleCreateClick">
                <template #prefix>
                    <FeatherIcon name="plus" class="h-4" />
                </template>
            </Button>
        </div>
    </div>
    <DataImportModal v-model="showInfoModalData" :list_field_value="list_field_value" :editMode="editMode" :doctype="doctype"
        v-model:quickEntry="showQuickEntryModal" @updateList="handleCreate"></DataImportModal>

    <QuickEntryModal v-model="showQuickEntryModal" :doctype="doctype" />
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
const router = useRouter();
import {
    ref,
    onMounted,
    computed,
    provide
} from 'vue';


import LayoutHeader from "@/components/LayoutHeader.vue";
import ViewControls from "@/components/ViewControls.vue";
import QuickEntryModal from "@/components/Modals/QuickEntryModal.vue";
import DataImportModal from "@/components/Modals/DataImportModal.vue";
import DataImportListView from "@/components/ListViews/Data_Import_ListView.vue";


import { Breadcrumbs, Button, createResource } from "frappe-ui";

const breadcrumbs = ref([
    { label: 'Home', to: '/' },
    { label: 'Data Import', to: '/data-import' }
]);
const dataListView = ref(null);
const listData = ref({});
const loadMore = ref(1);
const triggerResize = ref(1);
const updatedPageCount = ref(20);
const showInfoModalData = ref(false);
const showQuickEntryModal = ref(false);
const list_field_value = ref(null);
const editMode = ref(false);
const viewControls = ref(null);

const props = defineProps({
    doctype: {
        type: String,
        default: "Data Import"
    },
});


const handleCreate =(ipID)=>{
    listData.value.reload()
    navigateToImportDetail(ipID)
}

const rows = computed(() => {        
        if (!listData.value?.data?.data) return [];

        return listData.value?.data.data;
    });
const showModal = (data) => {
    list_field_value.value = rows;
    showInfoModalData.value = true;
};
const showImport = (name) => {
    // Logic to show task details    
    showInfoModalData.value = true;
    if(name) {
        editMode.value = true;
        list_field_value.value = rows.value.find((row) => row.name === name);
    } else {
        editMode.value = false;
        list_field_value.value ={}
    }
};

const handleCreateClick = () => {
    // Logic to handle the creation of a new data import
    showInfoModalData.value = true;
    editMode.value = false;
};
const navigateToImportDetail = (id) => {
    let name = "Data Import Detail"
    
	router.push({
		name: name,
		params: { importId: encodeURIComponent(id)},
	});
};

const navigateToImportNew = (id) => {
    let importId = `new-data-import-${randomString()}`;
    let name = "Data Import New"
	router.push({
		name: name,
		params: { importId: importId},
	});
};

function randomString(length = 10) {
  const letters = 'abcdefghijklmnopqrstuvwxyz';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += letters.charAt(Math.floor(Math.random() * letters.length));
  }
  return result;
}
// const fetchData = async () => {
//     const resource = createResource({
//         url: "frappe.desk.reportview.get",
//         method: "GET",
//         params: {
//             doctype: props.doctype,
//             fields: ["*"],
//             limit_page_length: 20,
//             limit_start: 0,
//         },
//     });

//     try {
//         const response = await resource.fetch();
//         rows.value = response.data || [];
//         listData.value.data.total_count = response.total_count || 0;
//     } catch (error) {
//         console.error("Error fetching data:", error);
//     }
// };
onMounted(() => {
    
})


</script>