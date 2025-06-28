<template>
  <FormControl
    autocomplete="off"
    type="text"
    v-model="data"
    :placeholder="placeholder"
    :disabled="disabled"
    :hidden="hidden"
    @change="handleChange"
    @input="
      () => {
        emit('input');
      }
    "
  >
    <template #prefix>
      <Popover>
        <template #target="{ togglePopover, isOpen }">
          <span
            v-if="data"
            class="cursor-pointer w-5 h-5 rounded-sm"
            :style="{ background: data }"
            @click="() => togglePicker(togglePopover, isOpen)"
          ></span>
          <Avatar
            v-else
            class="cursor-pointer"
            size="sm"
            image="/assets/frappe/images/color-circle.png"
            @click="() => togglePicker(togglePopover, isOpen)"
          />
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
import Picker from "@/assets/js/color_picker/color_picker.js";

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

let picker = null;
const data = defineModel();
const colorPicker = ref(null);
const emit = defineEmits(["change", "input"]);

function togglePicker(togglePopover, isOpen) {
  if (!props.disabled) {
    togglePopover();
    if (!isOpen) {
      setTimeout(() => {
        this.picker.set_color(data.value);
        this.picker.refresh();
      }, 10);
    }
  }
}

// load color picker
onMounted(() => {
  let picker_wrapper = colorPicker.value;

  picker = new Picker({
    parent: picker_wrapper,
    color: get_color(),
    swatches: [
      "#449CF0",
      "#ECAD4B",
      "#29CD42",
      "#761ACB",
      "#CB2929",
      "#ED6396",
      "#29CD42",
      "#4463F0",
      "#EC864B",
      "#4F9DD9",
      "#39E4A5",
      "#B4CD29",
    ],
  });

  picker.on_change = (color) => {
    data.value = color;
    emit("input");
  };
});

function handleChange() {
  data.value = get_color();
  emit("change");
}

function get_color() {
  return validate(data.value);
}

function validate(value) {
  if (value === "") {
    return "";
  }
  var is_valid = /^#[0-9A-F]{6}$/i.test(value);
  if (is_valid) {
    return value;
  }
  return null;
}
</script>

<style>
.color-picker {
  font-size: 12px;
  color: #525252;
  --color-picker-width: 210px;
  width: var(--color-picker-width);
}
.color-picker .swatches {
  margin-top: 10px;
  margin-bottom: 10px;
  display: flex;
  flex-wrap: wrap;
}
.color-picker .swatch {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  margin-right: 10px;
  margin-bottom: 10px;
  cursor: pointer;
}
.color-picker .color-selector,
.color-picker .hue-selector {
  width: 12px;
  height: 12px;
  background: transparent;
  position: absolute;
  border-radius: 50%;
  /* box-shadow: 0 0 0 1px gray, 0 0 0 3px white, 0 0 0 4px gray; */
  border: 1px solid rgba(0, 0, 0, 0.2);
}
.color-picker .color-selector::before,
.color-picker .color-selector::after,
.color-picker .hue-selector::before,
.color-picker .hue-selector::after {
  position: absolute;
  background-color: transparent;
  border: 1px solid rgba(0, 0, 0, 0.2);
  content: " ";
  border-radius: 50%;
}
.color-picker .color-selector::before,
.color-picker .hue-selector::before {
  width: 100%;
  height: 100%;
  background-color: currentColor;
  border: 2px solid white;
}
.color-picker .color-selector::after,
.color-picker .hue-selector::after {
  width: calc(100% - 4px);
  height: calc(100% - 4px);
  border: 1px solid rgba(0, 0, 0, 0.2);
  top: 2px;
  left: 2px;
}
.color-picker .hue-selector {
  width: 14px;
  height: 14px;
}
.color-picker .color-map {
  margin-top: 10px;
  color: transparent;
  position: relative;
  width: auto;
  height: 140px;
  /* background: linear-gradient(0deg, black, transparent), linear-gradient(90deg, white, transparent), red; */
  border-radius: 6px;
  margin-bottom: 10px;
}
.color-picker .hue-map {
  color: transparent;
  width: auto;
  height: 14px;
  position: relative;
  background: linear-gradient(
    90deg,
    hsl(0, 100%, 50%),
    hsl(60, 100%, 50%),
    hsl(120, 100%, 50%),
    hsl(180, 100%, 50%),
    hsl(240, 100%, 50%),
    hsl(300, 100%, 50%),
    hsl(0, 100%, 50%)
  );
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 10px;
}
.color-picker-popover .picker-arrow {
  left: 15px !important;
}
</style>
