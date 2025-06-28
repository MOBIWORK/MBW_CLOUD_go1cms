<template>
	<div v-if="field.visible" class="field">
		<div v-if="field.fieldtype != 'Check'" class="mb-2 text-sm text-ink-gray-5">
			{{ __(field.label) }}
			<span
				v-if="field.reqd || (field.mandatory_depends_on && field.mandatory_via_depends_on)"
				class="text-ink-red-3"
				>*</span
			>
		</div>
		<FormControl
			v-if="field.read_only && field.fieldtype !== 'Check'"
			type="text"
			:placeholder="getPlaceholder(field)"
			v-model="data[field.fieldname]"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
		/>
		<Grid
			v-else-if="field.fieldtype === 'Table' && data[field.fieldname]"
			v-model="data[field.fieldname]"
			:doctype="field.options"
			:parentDoctype="doctype"
		/>
		<TableMultiselectInput
			v-else-if="field.fieldtype === 'Table MultiSelect'"
			v-model="data[field.fieldname]"
			:doctype="field.options"
		/>
		<FormControl
			v-else-if="field.fieldtype === 'Select'"
			type="select"
			class="form-control"
			:class="field.prefix ? 'prefix' : ''"
			:options="field.options"
			v-model="data[field.fieldname]"
			:disabled="Boolean(field.read_only_depends_on)"
			:hidden="Boolean(field.hidden)"
			:placeholder="getPlaceholder(field)"
		>
			<template v-if="field.prefix" #prefix>
				<IndicatorIcon :class="field.prefix" />
			</template>
		</FormControl>

		<div v-else-if="field.fieldtype == 'Check'" class="flex items-center gap-2">
			<FormControl
				class="form-control"
				type="checkbox"
				v-model="data[field.fieldname]"
				@change="(e) => (data[field.fieldname] = e.target.checked)"
				:disabled="Boolean(field.read_only)"
				:hidden="Boolean(field.hidden)"
			/>
			<label
				class="text-sm text-ink-gray-5"
				@click="
					() => {
						if (!Boolean(field.read_only)) {
							data[field.fieldname] = !data[field.fieldname];
						}
					}
				"
			>
				{{ __(field.label) }}
				<span class="text-ink-red-3" v-if="field.mandatory">*</span>
			</label>
		</div>
		<div class="flex gap-1" v-else-if="field.fieldtype === 'Link'">
			<Link
				class="form-control flex-1 truncate"
				:value="data[field.fieldname]"
				:doctype="field.options"
				:filters="field.filters"
				@change="(v) => (data[field.fieldname] = v)"
				:placeholder="getPlaceholder(field)"
				:doc="data"
				:onCreate="field.create"
			/>
			<Button
				v-if="data[field.fieldname] && field.edit"
				class="shrink-0"
				:label="__('Edit')"
				@click="field.edit(data[field.fieldname])"
			>
				<template #prefix>
					<EditIcon class="h-4 w-4" />
				</template>
			</Button>
		</div>
		<div v-else-if="field.fieldtype === 'Text Editor'">
			<TextEditor
				ref="content"
				variant="outline"
				:class="'w-full'"
				:content="data ? data[field.fieldname] || '' : ''"
				:placeholder="getPlaceholder(field)"
				:bubbleMenu="true"
				:fixedMenu="true"
				@change="
					(content) => {
						// console.log(content);
						if (content != '<p></p>') {
							data[field.fieldname] = content;
						}
					}
				"
				editor-class="!prose-sm !w-full overflow-auto !max-w-full min-h-[180px] max-h-80 py-1.5 px-2 rounded border border-gray-300 bg-white hover:border-gray-400 hover:shadow-sm focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors"
			/>
		</div>

		<Link
			v-else-if="field.fieldtype === 'User'"
			class="form-control"
			:value="data[field.fieldname] && getUser(data[field.fieldname]).full_name"
			:doctype="field.options"
			:filters="field.filters"
			@change="(v) => (data[field.fieldname] = v)"
			:placeholder="getPlaceholder(field)"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
		>
			<template #prefix>
				<UserAvatar
					v-if="data[field.fieldname]"
					class="mr-2"
					:user="data[field.fieldname]"
					size="sm"
				/>
			</template>
			<template #item-prefix="{ option }">
				<UserAvatar class="mr-2" :user="option.value" size="sm" />
			</template>
			<template #item-label="{ option }">
				<Tooltip :text="option.value">
					<div class="cursor-pointer">
						{{ getUser(option.value).full_name }}
					</div>
				</Tooltip>
			</template>
		</Link>
		<DateTimePicker
			v-else-if="field.fieldtype === 'Datetime'"
			v-model="data[field.fieldname]"
			icon-left=""
			:formatter="(date) => getFormat(date, '', true, true)"
			:placeholder="getPlaceholder(field)"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
			input-class="border-none"
		/>
		<DatePicker
			v-else-if="field.fieldtype === 'Date'"
			icon-left=""
			v-model="data[field.fieldname]"
			:formatter="(date) => getFormat(date, '', true)"
			:placeholder="getPlaceholder(field)"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
			input-class="border-none"
		/>
		<FormControl
			v-else-if="['Small Text', 'Text', 'Long Text', 'Code'].includes(field.fieldtype)"
			type="textarea"
			:placeholder="getPlaceholder(field)"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
			v-model="data[field.fieldname]"
		/>
		<FormControl
			v-else-if="['Int'].includes(field.fieldtype)"
			type="number"
			:placeholder="getPlaceholder(field)"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
			v-model="data[field.fieldname]"
		/>
		<FormControl
			v-else-if="field.fieldtype === 'Percent'"
			type="text"
			:value="getFormattedPercent(field.fieldname, data)"
			:placeholder="getPlaceholder(field)"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
			@change="data[field.fieldname] = flt($event.target.value)"
		/>
		<FormControl
			v-else-if="field.fieldtype === 'Float'"
			type="text"
			:value="getFormattedFloat(field.fieldname, data)"
			:placeholder="getPlaceholder(field)"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
			@change="data[field.fieldname] = flt($event.target.value)"
		/>
		<!-- <div v-else-if="field.fieldtype === 'Currency'">
      {{ console.log("Test log Currency field.fieldname",field.fieldname) }}
      {{ console.log("Test log Currency data",data) }}
    </div> -->

		<FormControl
			v-else-if="field.fieldtype === 'Currency'"
			type="text"
			:value="getFormattedCurrency(field.fieldname, data)"
			:placeholder="getPlaceholder(field)"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
			@change="data[field.fieldname] = flt($event.target.value)"
		/>
		<FileUploader
			v-else-if="field.fieldtype === 'Attach'"
			:fileTypes="['files/*']"
			:upload-args="{
				doctype: props.doctype,
				docname: props.employeeId,
				private: false,
			}"
			FileUploaderv-model="data[field.fieldname]"
			@success="
				(file) => {
					// dirtyChange();
					handleFileUploadSuccess(file, field.fieldname);
				}
			"
		>
			<template
				v-slot="{
					file,
					uploading,
					progress,
					uploaded,
					message,
					error,
					total,
					success,
					openFileSelector,
				}"
			>
				<div class="flex items-center gap-4">
					<!-- Hiển thị tên file nếu có -->
					<div v-if="data[field.fieldname]" class="text-gray-700 truncate max-w-xs">
						<a
							:href="data[field.fieldname]"
							target="_blank"
							class="text-blue-600 underline"
						>
							{{ data[field.fieldname].split("/").pop() }}
							<!-- Lấy tên file -->
						</a>
						<!-- Nút Clear
            <Button variant="ghost" @click="clearFile(field.name)" class="text-red-500">
              Clear
            </Button> -->
					</div>
					<!-- Nút Upload -->
					<Button variant="ghost" @click="openFileSelector()" :loading="uploading">
						<div class="flex gap-2">
							{{ uploading ? `Uploading ${progress}%` : "Upload File" }}
							<AttachmentIcon class="h-4" />
						</div>
					</Button>
				</div>
			</template>
		</FileUploader>
		<div v-else-if="field.fieldtype === 'Attach Image'">
			<FileUploader
				@success="(file) => (data[field.fieldname] = file.file_url)"
				:validateFile="validateFile"
			>
				<template #default="{ openFileSelector, error }">
					<div class="flex items-center justify-start gap-5 p-1">
						<div class="group relative size-12">
							<div v-if="data[field.fieldname]">
								<Avatar
									size="3xl"
									class="size-12"
									:label="__('Avatar')"
									:image="data[field.fieldname]"
								/>
							</div>
							<div v-else class="group size-12">
								<div
									class="relative inline-block shrink-0 w-11.5 h-11.5 rounded-full size-12"
								>
									<div
										class="flex h-full w-full items-center justify-center bg-gray-100 text-gray-600 font-normal text-[8px] rounded-full text-center"
									>
										{{ __("Upload Image") }}
									</div>
								</div>
							</div>
							<component
								:is="data[field.fieldname] ? Dropdown : 'div'"
								v-bind="
									data[field.fieldname]
										? {
												options: [
													{
														icon: 'upload',
														label: data[field.fieldname]
															? __('Change image')
															: __('Upload image'),
														onClick: openFileSelector,
													},
													{
														icon: 'trash-2',
														label: __('Remove image'),
														onClick: () =>
															(data[field.fieldname] = ''),
													},
												],
											}
										: { onClick: openFileSelector }
								"
								class="!absolute bottom-0 left-0 right-0"
							>
								<div
									class="z-1 absolute bottom-0.5 left-0 right-0.5 flex h-9 cursor-pointer items-center justify-center rounded-b-full bg-black bg-opacity-40 pt-3 opacity-0 duration-300 ease-in-out group-hover:opacity-100"
									style="
										-webkit-clip-path: inset(12px 0 0 0);
										clip-path: inset(12px 0 0 0);
									"
								>
									<CameraIcon class="size-4 cursor-pointer text-white" />
								</div>
							</component>
						</div>
						<div class="flex flex-col justify-center text-xs text-gray-500 space-y-1">
							<div v-if="error" class="text-red-500" v-html="error" />

							<div v-else-if="data[field.fieldname]">
								<span class="font-medium text-gray-700">
									{{ __("Image uploaded:") }}
								</span>
								<span class="truncate block w-40 text-gray-500">
									{{ data[field.fieldname] }}
									{{ data[field.fieldname].split("/").pop() }}
								</span>
								<span
									class="text-[10px] text-black italic flex items-center gap-1"
								>
									<FeatherIcon name="arrow-left" class="h-4 w-4" />
									{{ __("Click here to change or remove") }}
								</span>
							</div>

							<div v-else class="text-black italic flex items-center gap-1">
								<FeatherIcon name="arrow-left" class="h-4 w-4" />
								{{ __("Click here to upload image") }}
							</div>
						</div>
					</div>
				</template>
			</FileUploader>
		</div>
		<ColorPicker
			v-else-if="field.fieldtype === 'Color'"
			:placeholder="getPlaceholder(field)"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
			v-model="data[field.fieldname]"
			@input="dirtyChange"
		></ColorPicker>
		<div v-else-if="field.fieldtype === 'Rating'" class="flex flex-col justify-center">
			<StarRating
				:rating="data[field.fieldname]"
				:static="false"
				@update:rating="
					(rating) => (console.log(rating), (data[field.fieldname] = rating))
				"
			/>
		</div>
		<IconPicker
			v-else-if="field.fieldtype === 'Icon'"
			:placeholder="getPlaceholder(field)"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
			v-model="data[field.fieldname]"
			@input="dirtyChange"
		></IconPicker>
		<TextInput
			v-else-if="field.fieldtype === 'Time'"
			:type="'time'"
			:ref_for="true"
			size="sm"
			variant="subtle"
			placeholder="Placeholder"
			:disabled="false"
			v-model="data[field.fieldname]"
		/>
		<FormControl
			v-else
			type="text"
			:placeholder="getPlaceholder(field)"
			v-model="data[field.fieldname]"
			:disabled="Boolean(field.read_only)"
			:hidden="Boolean(field.hidden)"
		/>
	</div>
</template>
<script setup>
import ColorPicker from "@/components/ColorPicker.vue";
import IconPicker from "@/components/IconPicker.vue";
import EditIcon from "@/components/Icons/EditIcon.vue";
import IndicatorIcon from "@/components/Icons/IndicatorIcon.vue";
import CameraIcon from "@/components/Icons/CameraIcon.vue";
import UserAvatar from "@/components/UserAvatar.vue";
import Link from "@/components/Controls/Link.vue";
import Grid from "@/components/Controls/Grid.vue";
import { getFormat, evaluateDependsOnValue } from "@/utils";
import { flt } from "@/utils/numberFormat.js";
import { getMeta } from "@/stores/meta";
import { usersStore } from "@/stores/users";
import {
	Tooltip,
	DatePicker,
	DateTimePicker,
	FileUploader,
	TextEditor,
	Avatar,
	Dropdown,
	TextInput,
} from "frappe-ui";
import MultipleSelect from "@/components/Controls/MultipleSelect.vue";
import { computed, inject } from "vue";
import StarRating from "@/components/StarRating.vue";
import TableMultiselectInput from '@/components/Controls/TableMultiselectInput.vue'

const props = defineProps({
	field: Object,
});

const data = inject("data");
const doctype = inject("doctype");
const preview = inject("preview");

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } = getMeta(doctype);
const { getUser } = usersStore();

const field = computed(() => {
	let field = props.field;
	if (field.fieldtype == "Select" && typeof field.options === "string") {
		field.options = field.options.split("\n").map((option) => {
			return { label: option, value: option };
		});

		if (field.options[0].value !== "") {
			field.options.unshift({ label: "", value: "" });
		}
	}

	if (field.fieldtype === "Link" && field.options === "User") {
		field.fieldtype = "User";
	}

	let _field = {
		...field,
		filters: field.link_filters && JSON.parse(field.link_filters),
		placeholder: field.placeholder || field.label,
		display_via_depends_on: evaluateDependsOnValue(field.depends_on, data.value),
		mandatory_via_depends_on: evaluateDependsOnValue(field.mandatory_depends_on, data.value),
		read_only_depends_on: field.read_only_depends_on
			? evaluateDependsOnValue(field.read_only_depends_on, data.value)
			: null,
	};

	_field.visible = isFieldVisible(_field);
	return _field;
});

function isFieldVisible(field) {
	if (preview.value) return true;
	return (
		(field.fieldtype == "Check" ||
			(field.read_only && data.value[field.fieldname]) ||
			!field.read_only) &&
		(!field.depends_on || field.display_via_depends_on) &&
		!field.hidden
	);
}

const getPlaceholder = (field) => {
	if (field.placeholder) {
		return __(field.placeholder);
	}
	if (["Select", "Link"].includes(field.fieldtype)) {
		return __("Select {0}", [__(field.label)]);
	} else {
		return __("Enter {0}", [__(field.label)]);
	}
};

function validateFile(file) {
	let extn = file.name.split(".").pop().toLowerCase();
	if (!["png", "jpg", "jpeg"].includes(extn)) {
		return __("Only PNG and JPG images are allowed");
	}
}

const handleFileUploadSuccess = (file, fieldName) => {
	console.log("Uploaded file:", file);
	console.log("Field name:", fieldName);
	console.log(data.value);
	data.value[fieldName] = file.file_url; // Lưu URL hoặc tên file
};

const updateMultiSelect = () => {
	emit("updateRecord");
};

const addDraftMultipleSelect = (data, fieldName) => {
	console.log("Data:", data);
	console.log("Field Name:", fieldName);
	data.value[fieldName] = data;
};

const deleteDraftMultipleSelect = (data, fieldName) => {
	console.log("Data:", data);
	console.log("Field Name:", fieldName);
	data.value[fieldName] = data;
};
</script>
<style scoped>
:deep(.form-control.prefix select) {
	padding-left: 2rem;
}
</style>
