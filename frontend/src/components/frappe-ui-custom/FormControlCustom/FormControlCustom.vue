<template>
  <div v-if="type != 'checkbox'" :class="['space-y-1.5', attrs.class]">
    <label class="block" :class="labelClasses" v-if="label" :for="id">
      {{ label }}
      <span class="text-red-500" v-if="required">*</span>
    </label>
    <SelectCustom
      v-if="type === 'select'"
      :id="id"
      v-bind="{ ...controlAttrs, size }"
    >
      <template #prefix v-if="$slots.prefix">
        <slot name="prefix" />
      </template>
    </SelectCustom>
    <Autocomplete
      v-else-if="type === 'autocomplete'"
      v-bind="{ ...controlAttrs }"
    >
      <template #prefix v-if="$slots.prefix">
        <slot name="prefix" />
      </template>
      <template #item-prefix="itemPrefixProps" v-if="$slots['item-prefix']">
        <slot name="item-prefix" v-bind="itemPrefixProps" />
      </template>
    </Autocomplete>
    <Textarea
      v-else-if="type === 'textarea'"
      :id="id"
      v-bind="{ ...controlAttrs, size }"
    />
    <TextInputCustom
      v-else
      :id="id"
      v-bind="{ ...controlAttrs, type, size }"
      :isCheckEmpty="checkEmpty"
      @input="onInput"
    >
      <template #prefix v-if="$slots.prefix">
        <slot name="prefix" />
      </template>
      <template #suffix v-if="$slots.suffix">
        <slot name="suffix" />
      </template>
    </TextInputCustom>
    <slot name="description">
      <p v-if="description" :class="descriptionClasses">{{ description }}</p>
    </slot>
    <!-- Thông báo lỗi -->
    <p v-if="errorMessage" class="text-red-500 text-sm">
      {{ errorMessage }}
    </p>
  </div>
  <Checkbox
    v-else
    :id="id"
    v-bind="{ ...controlAttrs, label, size, class: attrs.class }"
  />
</template>
<script setup lang="ts">
import { useAttrs, computed, ref, watch } from "vue";
import type { TextInputTypes } from "./TextInput";
import { TextInput, Select, Textarea, Checkbox, Autocomplete } from "frappe-ui";
import TextInputCustom from "./TextInputCustom.vue";
import SelectCustom from "./SelectCustom.vue";

interface FormControlProps {
  label?: string;
  description?: string;
  type?: TextInputTypes | "textarea" | "select" | "checkbox" | "autocomplete";
  size?: "sm" | "md";
  required?: boolean;
  checkEmpty?: boolean;
  rules?: Array<(value: string) => string | boolean>;
}

let id1 = 0;
function generateId() {
  return ++id1;
}

function useId() {
  return "frappe-ui-" + generateId();
}

const id = useId();
const props = withDefaults(defineProps<FormControlProps>(), {
  type: "text",
  size: "sm",
});

const attrs = useAttrs();
const controlAttrs = computed(() => {
  // pass everything except class and style
  let _attrs: typeof attrs = {};
  for (let key in attrs) {
    if (key !== "class" && key !== "style") {
      _attrs[key] = attrs[key];
    }
  }
  return _attrs;
});

const labelClasses = computed(() => {
  return [
    {
      sm: "text-xs",
      md: "text-base",
    }[props.size],
    "text-gray-600",
  ];
});

const descriptionClasses = computed(() => {
  return [
    {
      sm: "text-xs",
      md: "text-base",
    }[props.size],
    "text-gray-600",
  ];
});

const errorMessage = ref<string | null>(null);
// Hàm kiểm tra validation
const validate = (value: string) => {
  for (const rule of props?.rules ?? []) {
    const result = rule(value);
    if (result !== true) {
      errorMessage.value = result as string;
      return false;
    }
  }
  errorMessage.value = null;
  return true;
};

// Gọi hàm validate mỗi khi giá trị thay đổi
const onInput = (e: Event) => {
  const value = (e.target as HTMLInputElement).value;
  validate(value);
};


</script>
<script lang="ts">
export default {
  inheritAttrs: false,
};
</script>
