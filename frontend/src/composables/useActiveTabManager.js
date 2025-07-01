import { ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

export function useActiveTabManager(tabs) {
  const route = useRoute();
  const router = useRouter();

  function setActiveTabInUrl(tabName) {
    let hash = "#" + tabName.toLowerCase();
    if (route.hash === hash) return;
    router.push({ ...route, hash });
  }

  function getActiveTabFromUrl() {
    return route.hash.replace("#", "");
  }

  function findTabIndex(tabName) {
    return tabs.value?.findIndex(
      (tabOptions) => tabOptions.name.toLowerCase() === tabName
    );
  }

  function getTabIndex(tabName) {
    let index = findTabIndex(tabName);
    return index !== -1 ? index : 0; // Default to the first tab if not found
  }

  function getActiveTab() {
    let _activeTab = getActiveTabFromUrl();
    if (_activeTab) {
      let index = findTabIndex(_activeTab);
      if (index !== -1) {
        return index;
      }
      return 0;
    }

    return 0; // Default to the first tab if nothing is found
  }

  const tabIndex = ref(getActiveTab());

  // Watch tabIndex and update the URL
  watch(tabIndex, (tabIndexValue) => {
    let currentTab = tabs.value?.[tabIndexValue].name;
    setActiveTabInUrl(currentTab);
  });

  // Watch URL hash and update the active tab
  watch(
    () => route.hash,
    (tabValue) => {
      if (!tabValue) return;

      let tabName = tabValue.replace("#", "");
      let index = findTabIndex(tabName);
      if (index === -1) index = 0;

      tabIndex.value = index;
    }
  );

  // Reset tabIndex when tabs change
  watch(tabs, () => {
    tabIndex.value = getActiveTab();
  });

  return { tabIndex };
}
