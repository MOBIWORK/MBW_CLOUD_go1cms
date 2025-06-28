<template>
	<EditValueModal
		v-if="showEditModal"
		v-model="showEditModal"
		:doctype="doctype"
		:selectedValues="selectedValues"
		@reload="reload"
	/>
	<AssignmentModal
		v-if="showAssignmentModal"
		v-model="showAssignmentModal"
		v-model:assignees="bulkAssignees"
		:docs="selectedValues"
		:doctype="doctype"
		@reload="reload"
	/>
</template>

<script setup>
import EditValueModal from "@/components/Modals/EditValueModal.vue";
import AssignmentModal from "@/components/Modals/AssignmentModal.vue";
import { setupListCustomizations, createToast } from "@/utils";
import { globalStore } from "@/stores/global";
import { capture } from "@/telemetry";
import { call, createResource } from "frappe-ui";
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

const props = defineProps({
	doctype: {
		type: String,
		default: "",
	},
	options: {
		type: Object,
		default: () => ({
			hideEdit: false,
			hideDelete: false,
			hideAssign: false,
		}),
	},
	eProfileId: {
		type: String,
		default: "",
	},
});

const emit = defineEmits(["eventhiddenModal", "updateJobOpening"]);
const list = defineModel();
const route = useRoute();
const router = useRouter();

const { $dialog, $socket } = globalStore();

const showEditModal = ref(false);
const selectedValues = ref([]);
const unselectAllAction = ref(() => {});

function editValues(selections, unselectAll) {
	selectedValues.value = selections;
	showEditModal.value = true;
	unselectAllAction.value = unselectAll;
}

// function convertToDeal(selections, unselectAll) {
//   $dialog({
//     title: __('Convert to Deal'),
//     message: __('Are you sure you want to convert {0} Lead(s) to Deal(s)?', [
//       selections.size,
//     ]),
//     variant: 'solid',
//     theme: 'blue',
//     actions: [
//       {
//         label: __('Convert'),
//         variant: 'solid',
//         onClick: (close) => {
//           capture('bulk_convert_to_deal')
//           Array.from(selections).forEach((name) => {
//             call('crm.fcrm.doctype.crm_lead.crm_lead.convert_to_deal', {
//               lead: name,
//             }).then(() => {
//               createToast({
//                 title: __('Converted successfully'),
//                 icon: 'check',
//                 iconClasses: 'text-green-600',
//               })
//               list.value.reload()
//               unselectAll()
//               close()
//             })
//           })
//         },
//       },
//     ],
//   })
// }

// function convertToProfile(selections, unselectAll){
//   // Chuyển `selections` từ `Set` thành mảng
//   const selectedIds = Array.from(selections);
//   // Gọi API với danh sách ID đã chọn
//   const actionIns = createResource({
//     url: "i_van.mbw_i_van.doctype.ivan_document.api.create_profile_records",
//     method: 'POST',
//     params: {
//       profile_id: props.eProfileId,
//       list_employee: selectedIds, // Truyền danh sách ID bản ghi đã chọn vào params
//     },
//     onSuccess(data) {
//       // Sử dung emit để truyền trạng thái lên component cha để đóng modal list nhân viên và load lại data trên các tab tờ khai
//       emit('eventStatusUpdateEmployee', "Success");
//       createToast({
//         title: __("Cập nhật người lao động thành công."),
//         icon: "check",
//         iconClasses: "text-green-800",
//       });

//       // Tải lại danh sách sau khi cập nhật
//       list.value.reload();
//       // Bỏ chọn các bản ghi
//       unselectAll();
//     },
//   });
//   actionIns.fetch();
// }

function parseServerMessages(serverMessages) {
	try {
		if (!serverMessages) return null;

		// Bước 1: Parse chuỗi JSON thành mảng các thông báo lỗi
		const messagesArray = JSON.parse(serverMessages).map((msg) => JSON.parse(msg));

		// Bước 2: Lọc ra phần "message" và làm sạch chuỗi HTML nếu cần
		const errorMessages = messagesArray.map((msg) => msg.message).join("<br>");

		return errorMessages;
	} catch (error) {
		console.error("Error parsing _server_messages:", error);
		return __("An error occurred while processing server messages.");
	}
}

let errorFlag = ref(false); // Cờ để ngăn lỗi lặp lại

const deleteItemsResource = createResource({
  url: "go1_cms.api.deleteItems.delete_items",
  auto: false,
  onSuccess(response) {
    console.log("API Response:", response);

    let message = "";

    // 🔥 Nếu có bản ghi bị lỗi
    if (response.errors?.length > 0) {
      let errorMessage = response.errors
        .map(entry => `• ${entry.item}: ${entry.error.replace(/<a[^>]*>(.*?)<\/a>/g, "$1")}`)
        .join("\n");

      message += `<strong>${__("Failed to delete some items:")}</strong><br>${errorMessage.replace(/\n/g, "<br>")}`;
    }

    // ✅ Nếu có bản ghi đã xóa, hiển thị số lượng
    if (response.deleted_count > 0) {
      message += `<br><strong>${__(`Successfully deleted ${response.deleted_count} items.`)}</strong>`;
    }

    createToast({
      title: response.deleted_count > 0 ? __("Partial Delete Success") : __("Failed to delete items"),
      text: message,
      icon: response.deleted_count > 0 ? "check" : "alert-circle",
      iconClasses: response.deleted_count > 0 ? "text-green-600" : "text-red-600",
    });

    // ✅ Nếu có ít nhất một bản ghi đã xóa, reload danh sách
    if (response.deleted_count > 0) {
      list.value.reload();
	  emit("updateJobOpening");
    }
  },
  onError(error) {
    console.log("Delete API error:", error.messages);

    // Nếu lỗi đã hiển thị, không chạy tiếp
    if (errorFlag.value) return;
    errorFlag.value = true; // Đánh dấu đã xử lý lỗi

    let errorMessage = __("An error occurred while deleting the items.");

    if (error?.messages?.length > 0) {
      let rawMessage = error.messages[0];
      errorMessage = rawMessage.replace(/<a[^>]*>(.*?)<\/a>/g, "$1");
    }

    createToast({
      title: __("Failed to delete items"),
      text: errorMessage,
      icon: "alert-circle",
      iconClasses: "text-red-600",
    });

    // Đặt timeout để reset cờ sau một khoảng thời gian (tránh lỗi liên tục)
    setTimeout(() => {
      errorFlag.value = false;
    }, 2000);
  }
});


function deleteValues(selections, unselectAll) {
	$dialog({
		title: __("Delete"),
		message: __(`Are you sure you want to delete ${selections.size} item(s)?`),
		variant: "solid",
		theme: "red",
		actions: [
			{
				label: __("Delete"),
				variant: "solid",
				theme: "red",
				onClick: (closeDialog) => {
					capture("bulk_delete");

					deleteItemsResource.fetch({
						items: JSON.stringify(Array.from(selections)), // Chuyển thành JSON string
						doctype: props.doctype,
					});

					// Bỏ chọn tất cả sau khi gọi API
					unselectAll();
					closeDialog();
				},
			},
		],
	});
}

const showAssignmentModal = ref(false);
const bulkAssignees = ref([]);

function assignValues(selections, unselectAll) {
	showAssignmentModal.value = true;
	selectedValues.value = selections;
	unselectAllAction.value = unselectAll;
}

function clearAssignemnts(selections, unselectAll) {
	$dialog({
		title: __("Clear Assignment"),
		message: __("Are you sure you want to clear assignment for {0} item(s)?", [
			selections.size,
		]),
		variant: "solid",
		theme: "red",
		actions: [
			{
				label: __("Clear Assignment"),
				variant: "solid",
				theme: "red",
				onClick: (close) => {
					capture("bulk_clear_assignment");
					call("frappe.desk.form.assign_to.remove_multiple", {
						doctype: props.doctype,
						names: JSON.stringify(Array.from(selections)),
						ignore_permissions: true,
					}).then((response) => {
						createToast({
							title: __("Assignment cleared successfully"),
							icon: "check",
							iconClasses: "text-green-600",
						});
						reload(unselectAll);
						close();
					});
				},
			},
		],
	});
}

const customBulkActions = ref([]);
const customListActions = ref([]);

function bulkActions(selections, unselectAll) {
	let actions = [];

	// if (props.doctype === 'IVAN_Employee') {
	//   actions.push({
	//     label: __('Save'),
	//     onClick: () => convertToProfile(selections, unselectAll),
	//   })
	// }

	if (!props.options.hideEdit) {
		actions.push({
			label: __("Edit"),
			onClick: () => editValues(selections, unselectAll),
		});
	}

	if (!props.options.hideDelete) {
		actions.push({
			label: __("Delete"),
			onClick: () => deleteValues(selections, unselectAll),
		});
	}

	if (!props.options.hideAssign) {
		actions.push({
			label: __("Assign To"),
			onClick: () => assignValues(selections, unselectAll),
		});
		actions.push({
			label: __("Clear Assignment"),
			onClick: () => clearAssignemnts(selections, unselectAll),
		});
	}

	// if (props.doctype === 'CRM Lead') {
	//   actions.push({
	//     label: __('Convert to Deal'),
	//     onClick: () => convertToDeal(selections, unselectAll),
	//   })
	// }

	customBulkActions.value.forEach((action) => {
		actions.push({
			label: __(action.label),
			onClick: () =>
				action.onClick({
					list: list.value,
					selections,
					unselectAll,
					call,
					createToast,
					$dialog,
					router,
				}),
		});
	});
	return actions;
}

function reload(unselectAll) {
	unselectAllAction.value?.();
	unselectAll?.();
	list.value?.reload();
}

onMounted(async () => {
	if (!list.value?.data) return;
	let customization = await setupListCustomizations(list.value.data, {
		list: list.value,
		call,
		createToast,
		$dialog,
		$socket,
		router,
	});
	customBulkActions.value = customization?.bulkActions || list.value?.data?.bulkActions || [];
	customListActions.value = customization?.actions || list.value?.data?.listActions || [];
});

defineExpose({
	bulkActions,
	customListActions,
});
</script>
