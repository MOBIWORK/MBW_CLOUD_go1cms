<template>
  <FormControl
    autocomplete="off"
    type="text"
    v-model="data"
    :placeholder="placeholder"
    :disabled="disabled"
    :hidden="hidden"
    @change="
      () => {
        emit('change');
      }
    "
    @input="
      () => {
        emit('input');
      }
    "
  >
    <template #prefix>
      <Popover>
        <template #target="{ togglePopover, isOpen }">
          <div
            class="selected-icon flex justify-center items-center"
            @click="() => togglePicker(togglePopover, isOpen)"
            v-html="utils.icon(get_icon(), 'sm')"
          ></div>
        </template>
        <template #body-main>
          <div class="p-4">
            <div class="popover color-picker-popover">
              <div ref="colorPicker" class="popover-body popover-content"></div>
            </div>
          </div>
        </template>
      </Popover>
    </template>
  </FormControl>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { Popover, Avatar } from "frappe-ui";
import Picker from "@/assets/js/icon_picker/icon_picker.js";
import utils from "@/assets/js/icon_picker/utils";

const props = defineProps({
  placeholder: {
    type: String,
    default: "",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  hidden: {
    type: Boolean,
    default: false,
  },
});

const popoverTarget = ref(null); // Tham chiếu đến Popover

function toggleMainPopover() {
  if (!props.disabled && popoverTarget.value) {
    popoverTarget.value.togglePopover(); // Kích hoạt togglePopover
  }
}

let picker = null;
const data = defineModel();
const colorPicker = ref(null);
const emit = defineEmits(["change", "input"]);

// load color picker
onMounted(() => {
  let picker_wrapper = colorPicker.value;

  picker = new Picker({
    parent: picker_wrapper,
    icon: get_icon(),
    icons: get_all_icons(),
  });

  picker.on_change = (icon) => {
    data.value = icon;
    emit("input");
  };
});

function togglePicker(togglePopover, isOpen) {
  if (!props.disabled) {
    togglePopover();
    if (!isOpen) {
      setTimeout(() => {}, 10);
    }
  }
}

function get_icon() {
  return data.value || "folder-normal";
}

function get_all_icons() {
  let icons = [];
  const symbols = document.querySelectorAll("#all-symbols > svg > symbol[id]");
  symbols.forEach(function (symbol) {
    if (symbol.id.includes("icon-")) {
      icons.push(symbol.id.replace("icon-", ""));
    }
  });
  return icons;
}
</script>

<style>
#icon-close {
  --invert-neutral: #000000;
  fill: var(--invert-neutral);
}
.selected-icon {
  cursor: pointer;
  max-width: 22px;
  max-height: 22px;
  border-radius: 5px;
}
.icon-picker {
  --text-xs: 12px;
  --text-muted: var(--gray-700);
  font-size: var(--text-xs);
  color: var(--text-muted);
  --icon-picker-width: 240px;
  width: var(--icon-picker-width);
}
.icon-picker .form-control {
  width: 100%;
  border-radius: 5px;
}
.icon-picker svg {
  overflow: hidden;
  vertical-align: middle;
}
.icon-picker .icons {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  overflow-y: scroll;
  max-height: 210px;
  cursor: pointer;
  /* Hide scrollbar for IE, Edge and Firefox */
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
  /* Hide scrollbar for Chrome, Safari and Opera */
}
.icon-picker .icons::-webkit-scrollbar {
  display: none;
}
.icon-picker .icons .icon-wrapper {
  display: flex;
  width: 30px;
  height: 30px;
  text-align: center;
  align-items: center;
}
.icon-picker .icons .icon-wrapper.hidden {
  display: none;
}
.icon-picker .search-icons {
  position: relative;
}
.icon-picker .search-icons input[type="search"] {
  height: 34px;
  padding-left: 30px;
}
.icon-picker .search-icons .search-icon {
  position: absolute;
  top: 7px;
  left: 7px;
}
.icon-picker-popover .picker-arrow {
  left: 15px !important;
}
.icon-picker .icon,
.icon-picker .es-icon,
.selected-icon .icon {
  --icon-fill: transparent;
  --icon-stroke: #383838;
  display: inline-block;
  font-size: 0;
  width: 20px;
  height: 20px;
  margin: 0 auto;
  background-size: cover;
  background-repeat: no-repeat;
  background-position: 50% 50%;
  fill: var(--icon-fill);
  stroke: var(--icon-stroke);
}
.icon-picker .icons {
  cursor: pointer;
}
</style>
