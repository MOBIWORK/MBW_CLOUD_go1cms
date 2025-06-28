<template>
  <Popover class="w-full" v-model:show="showOptions">
    <template #target="{ open: openPopover, togglePopover }">
      <slot
        name="target"
        v-bind="{
          open: openPopover,
          togglePopover,
          isOpen: showOptions,
          displayValue,
        }"
      >
        <div class="w-full">
          <button
            class="flex w-full items-center justify-between focus:outline-none"
            :class="inputClasses"
            @click="() => togglePopover()"
          >
            <div class="flex items-center">
              <slot name="prefix" />
              <span
                class="overflow-hidden text-ellipsis whitespace-nowrap text-base leading-5"
                v-if="selectedValue.length"
              >
                {{ selectedValue[0] }}
              </span>
              <span class="text-base leading-5 text-gray-500" v-else>
                {{ placeholder || "" }}
              </span>
            </div>
            <FeatherIcon
              name="chevron-down"
              class="h-4 w-4 text-gray-600"
              aria-hidden="true"
            />
          </button>
        </div>
      </slot>
    </template>
    <template #body="{ isOpen }">
      <div v-show="isOpen">
        <div class="mt-1 rounded-lg bg-white py-1 text-base shadow-2xl">
          <div class="relative px-1.5 pt-0.5">
            <TextInput
              ref="search"
              class="w-full"
              type="text"
              v-model="query"
              autocomplete="off"
              placeholder="Search"
            />
            <button
              class="absolute top-0 right-1.5 inline-flex h-7 w-7 items-center justify-center"
              @click="selectedValue = null"
            >
              <FeatherIcon name="x" class="w-4" />
            </button>
          </div>
          <div class="mx-2 my-2">
            <treeview
              @nodeChecked="(node) => updateSelect('add', node)"
              @nodeUnchecked="(node) => updateSelect('remove', node)"
              @nodeFocus="(node) => updateSelect('add', node)"
              :config="config"
              :nodes="nodes"
            ></treeview>
          </div>
          <div v-if="slots.footer" class="border-t p-1.5 pb-0.5">
            <slot
              name="footer"
              v-bind="{ value: search?.el._value, clearSelected, close }"
            ></slot>
          </div>
        </div>
      </div>
    </template>
  </Popover>
</template>

<script setup>
import { Popover, Button, FeatherIcon, TextInput } from "frappe-ui";
import { ref, computed, useAttrs, useSlots, watch, nextTick } from "vue";
import treeview from "vue3-treeview";
import "vue3-treeview/dist/style.css";

const props = defineProps({
  options: {
    type: Array,
    default: () => [],
  },
  size: {
    type: String,
    default: "md",
  },
  variant: {
    type: String,
    default: "subtle",
  },
  placeholder: {
    type: String,
    default: "",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  filterable: {
    type: Boolean,
    default: true,
  },
  multiSelect: {
    type: Boolean,
    default: false,
  },
});
const emit = defineEmits(["update:modelValue", "update:query", "change"]);

const config = ref({
  roots: [],
  keyboardNavigation: false,
  dragAndDrop: false,
  checkboxes: false,
  editable: false,
  disabled: false,
  padding: 25,
  checkboxes: true,
  openedIcon: {
    type: "shape",
    stroke: "black",
    strokeWidth: 3,
    viewBox: "0 0 24 24",
    draw: "M 2 12 L 22 12",
  },
  closedIcon: {
    type: "shape",
    stroke: "black",
    strokeWidth: 3,
    viewBox: "0 0 24 24",
    draw: `M 12 2 L 12 22 M 2 12 L 22 12`,
  },
});
const nodes = ref({});

const query = ref("");
const showOptions = ref(false);
const search = ref(null);

const slots = useSlots();

const selectedValue = defineModel();

watch(
  () => props.multiSelect,
  (val) => {
    config.value.checkMode = val ? 0 : 1;
  },
  { immediate: true }
);

function checkedBox(id, checked) {
  if (nodes.value[id]) {
    nodes.value[id] = {
      ...nodes.value[id],
      state: {
        ...nodes.value[id].state,
        checked,
      },
    };
  }
}

function updateSelect(action, node) {
  let newSelected = [...selectedValue.value];
  let newNodes = { ...nodes.value };
  if (action == "add") {
    if (!props.multiSelect) {
      newSelected.forEach((id) => {
        if (id != node.id) {
          checkedBox(id, false);
        }
      });

      checkedBox(node.id, true);
      newSelected = [node.id];
    } else {
    }
  } else if (action == "remove") {
    if (!props.multiSelect) {
      checkedBox(node.id, false);
      newSelected = [];
    } else {
      newSelected = selectedValue.value.filter((el) => el != node.id);
    }
  }

  selectedValue.value = newSelected;
}

function clearSelected() {
  selectedValue.value.forEach((id) => {
    checkedBox(id, false);
  });
}

function close() {
  showOptions.value = false;
}

watch(
  () => props.options,
  (val) => {
    if (val) {
      nodes.value = { ...val.nodes };
      config.value.roots = [...val.roots];
    }
  },
  { immediate: true }
);

const groups = computed(() => {
  if (!props.options || props.options.length == 0) return [];
  let groups = props.options[0]?.group
    ? props.options
    : [{ group: "", items: props.options }];

  return groups
    .map((group, i) => {
      return {
        key: i,
        group: group.group,
        hideLabel: group.hideLabel || false,
        items: props.filterable ? filterOptions(group.items) : group.items,
      };
    })
    .filter((group) => group.items.length > 0);
});

function filterOptions(options) {
  if (!query.value) {
    return options;
  }
  return options.filter((option) => {
    let searchTexts = [option.label, option.value];
    return searchTexts.some((text) =>
      (text || "").toString().toLowerCase().includes(query.value.toLowerCase())
    );
  });
}

function displayValue(option) {
  if (typeof option === "string") {
    let allOptions = groups.value.flatMap((group) => group.items);
    let selectedOption = allOptions.find((o) => o.value === option);
    return selectedOption?.label || option;
  }
  return option?.label;
}

watch(query, (q) => {
  emit("update:query", q);
});

watch(showOptions, (val) => {
  if (val) {
    nextTick(() => {
      search.value.el.focus();
    });
  }
});

const textColor = computed(() => {
  return props.disabled ? "text-gray-600" : "text-gray-800";
});

const inputClasses = computed(() => {
  let sizeClasses = {
    sm: "text-base rounded h-7",
    md: "text-base rounded h-8",
    lg: "text-lg rounded-md h-10",
    xl: "text-xl rounded-md h-10",
  }[props.size];

  let paddingClasses = {
    sm: "py-1.5 px-2",
    md: "py-1.5 px-2.5",
    lg: "py-1.5 px-3",
    xl: "py-1.5 px-3",
  }[props.size];

  let variant = props.disabled ? "disabled" : props.variant;
  let variantClasses = {
    subtle:
      "border border-gray-100 bg-gray-100 placeholder-gray-500 hover:border-gray-200 hover:bg-gray-200 focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400",
    outline:
      "border border-gray-300 bg-white placeholder-gray-500 hover:border-gray-400 hover:shadow-sm focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400",
    disabled: [
      "border bg-gray-50 placeholder-gray-400",
      props.variant === "outline" ? "border-gray-300" : "border-transparent",
    ],
  }[variant];

  return [
    sizeClasses,
    paddingClasses,
    variantClasses,
    textColor.value,
    "transition-colors w-full",
  ];
});

defineExpose({ query });
</script>
