<template>
  <div class="relative flex h-full flex-col justify-between transition-all duration-300 ease-in-out"
    :class="isSidebarCollapsed ? 'w-15' : 'w-56'">
    <div class="flex justify-center border-b">
      <UserDropdown class="p-2" :isCollapsed="isSidebarCollapsed" />
    </div>
    <div class="flex-1 overflow-y-auto pt-2">
      <!-- <div class="mb-3 flex flex-col">
        <SidebarLink
          id="notifications-btn"
          label="Notifications"
          :icon="NotificationsIcon"
          :isCollapsed="isSidebarCollapsed"
          @click="() => toggleNotificationPanel()"
          class="relative mx-2 my-0.5"
        >
          <template #right>
            <Badge
              v-if="
                !isSidebarCollapsed &&
                notificationsStore().unreadNotificationsCount
              "
              :label="notificationsStore().unreadNotificationsCount"
              variant="subtle"
            />
            <div
              v-else-if="notificationsStore().unreadNotificationsCount"
              class="absolute -left-1.5 top-1 z-20 h-[5px] w-[5px] translate-x-6 translate-y-1 rounded-full bg-gray-800 ring-1 ring-white"
            ></div>
          </template>
</SidebarLink>
</div> -->
      <div v-if="!isSidebarCollapsed && name_website_edit" class="m-2 text-base p-2 rounded-md border-2 bg-gray-200">
        <p class="text-gray-700 font-bold">{{ name_website_edit }}</p>
      </div>
      <div v-for="view in allViews" :key="view.label">
        <div v-if="!view.hideLabel && isSidebarCollapsed && view.views?.length" class="mx-2 my-2 h-1 border-b"></div>
        <Section :label="view.name" :hideLabel="view.hideLabel" :isOpened="view.opened">
          <template #header="{ opened, hide, toggle }">
            <div v-if="!hide"
              class="flex justify-between cursor-pointer gap-1.5 px-3 text-sm font-medium text-gray-600 transition-all duration-300 ease-in-out"
              :class="isSidebarCollapsed
                ? 'ml-0 h-0 overflow-hidden opacity-0'
                : 'ml-2 mt-4 h-7 w-auto opacity-100'
                " @click="toggle()">
              <div class="flex gap-1.5">
                <component :is="view.icon" class="h-4 w-4 text-gray-700" />
                <span class="uppercase">
                  {{ __(view.name) }}
                </span>
              </div>
              <FeatherIcon name="chevron-right" class="h-4 text-gray-900 transition-all duration-300 ease-in-out"
                :class="{ 'rotate-90': opened }" />
            </div>
          </template>
          <nav class="flex flex-col">
            <SidebarLink v-for="link in view.views" :key="link.label" :icon="link.icon" :label="link.label"
              :to="link.to" :isCollapsed="isSidebarCollapsed" class="mx-2 my-0.5" />
          </nav>
        </Section>
      </div>
    </div>
    <div class="m-2 flex flex-col gap-1">
      <!-- <SidebarLink label="Docs" :isCollapsed="isSidebarCollapsed" icon="book-open" @click="() => openDocs()" /> -->
      <SidebarLink :label="isSidebarCollapsed ? 'Expand' : 'Collapse'" :isCollapsed="isSidebarCollapsed"
        @click="isSidebarCollapsed = !isSidebarCollapsed" class="">
        <template #icon>
          <span class="grid h-5 w-6 flex-shrink-0 place-items-center">
            <CollapseSidebar class="h-4.5 w-4.5 text-gray-700 duration-300 ease-in-out"
              :class="{ '[transform:rotateY(180deg)]': isSidebarCollapsed }" />
          </span>
        </template>
      </SidebarLink>
    </div>
    <!-- <Notifications /> -->
    <ChangeLanguageDialog />
  </div>
</template>

<script setup>
import Section from '@/components/Section.vue'
import FormSetupIcon from '@/components/Icons/FormSetupIcon.vue'
import NewsIcon from '@/components/Icons/NewsIcon.vue'
import TemplatePageIcon from '@/components/Icons/TemplatePageIcon.vue'
import WebpageIcon from '@/components/Icons/WebpageIcon.vue'
import DisplayIcon from '@/components/Icons/DisplayIcon.vue'
import HeaderIcon from '@/components/Icons/HeaderIcon.vue'
import FooterIcon from '@/components/Icons/FooterIcon.vue'
import HomeIcon from '@/components/Icons/HomeIcon.vue'
import ServiceIcon from '@/components/Icons/ServiceIcon.vue'
import NewPageIcon from '@/components/Icons/NewPageIcon.vue'
import FormIcon from '@/components/Icons/FormIcon.vue'
import DescriptionIcon from '@/components/Icons/DescriptionIcon.vue'
import ChartIcon from '@/components/Icons/ChartIcon.vue'
import UserDropdown from '@/components/UserDropdown.vue'
import PolicyIconV1 from '@/components/Icons/PolicyIconV1.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import SettingsIcon from '@/components/Icons/SettingsIcon.vue'
import MenuIcon from '@/components/Icons/MenuIcon.vue'
import CollapseSidebar from '@/components/Icons/CollapseSidebar.vue'
import SidebarLink from '@/components/SidebarLink.vue'
import { viewsStore } from '@/stores/views'
import { FeatherIcon } from 'frappe-ui'
import { useStorage } from '@vueuse/core'
import { computed, ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { globalStore } from '@/stores/global'
import { createResource } from 'frappe-ui'
const { changeNameWebsiteEdit } = globalStore()
const { name_website_edit } = storeToRefs(globalStore())
import ChangeLanguageDialog from '@/components/Settings/ChangeLanguageDialog.vue'
import Company from '@/components/Icons/Company.vue'
import Unit from '@/components/Icons/Unit.vue'
import Profession from '@/components/Icons/Profession.vue'
import Level from '@/components/Icons/Level.vue'
import Location from '@/components/Icons/Location.vue'
import Position from '@/components/Icons/Position.vue'
import Country from '@/components/Icons/Country.vue'
import Province from '@/components/Icons/Province.vue'
import District from '@/components/Icons/District.vue'
import Ward from '@/components/Icons/Ward.vue'
import Recruitment from '@/components/Icons/Recruitment.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'

const { views } = viewsStore()

const isSidebarCollapsed = useStorage('isSidebarCollapsed', false)
const showSettings = ref(true)
const siteConfigLoaded = ref(false)

// Site config resource
const siteConfig = createResource({
  url: 'go1_cms.api.site_config.get_site_config',
  auto: true,
  onSuccess: (data) => {
    if (data.success) {
      // Hide settings if mbw_ats_site_name exists and is not empty
      showSettings.value = !data.mbw_ats_site_name || data.mbw_ats_site_name === ""
    }
    siteConfigLoaded.value = true // Đánh dấu đã load xong
  }
})

// Load site config on mount
onMounted(() => {
  siteConfig.fetch()
})

const links = [
  // {
  //   label: 'Website của tôi',
  //   icon: MyWebsiteIcon,
  //   to: 'My Website',
  // },
  {
    label: 'Interface Repository',
    icon: DisplayIcon,
    to: 'Interface Repository',
  },
  {
    label: 'Candidate',
    icon: DisplayIcon,
    to: 'candidates',
  },
  {
    label: 'Job Opening',
    icon: DisplayIcon,
    to: 'ats_job_opening',
  },
  {
    label: "Posts",
    icon: NewsIcon,
    to: 'Posts',
  }
]

const dashboardSection = {
  name: 'Dashboard',
  opened: false,
  views: [
    {
      label: 'Dashboard',
      icon: ChartIcon,
      to: 'Dashboard',
    },
  ],
}

const jobOpeningSection = {
  name: 'Recruitment news',
  opened: true,
  views: [
    {
      label: 'Job Opening',
      icon: DisplayIcon,
      to: 'job_opening',
    },
    {
      label: __('Company'),
      icon: Company,
      to: 'Company',
    },
    {
      label: __('Unit'),
      icon: Unit,
      to: 'Unit',
    },
    {
      label: __('Profession'),
      icon: Profession,
      to: 'Profession',
    },
    {
      label: __('Level'),
      icon: Level,
      to: 'Level',
    },
    {
      label: __('Location'),
      icon: Location,
      to: 'Location',
    },
    {
      label: __('Position'),
      icon: Position,
      to: 'Position',
    },
    {
      label: __('Country'),
      icon: Country,
      to: 'Country',
    },
    {
      label: __('Province'),
      icon: Province,
      to: 'Province',
    },
    // {
    //   label: __('District'),
    //   icon: District,
    //   to: 'District',
    // },
    {
      label: __('Ward'),
      icon: Ward,
      to: 'Ward',
    },
    {
      label: __('Email Account'),
      icon: EmailIcon,
      to: 'EmailAccount',
    },
    {
      label: __('Recruitment'),
      icon: Recruitment,
      to: 'Process',
    },
  ],
}

const candidatePages = ['Candidate Login', 'Reset Password', 'Forgot Password', 'Create Password']

function getCmsCandidateViews() {
  if (!views.data?.list_page) return []
  return views.data.list_page
    .filter(page => candidatePages.includes(page.name_page))
    .map(page => ({
      label: page.name_page,
      icon: DisplayIcon, // hoặc getIcon(page.icon) nếu muốn động
      to: {
        name: 'Page',
        query: { view: page.name },
      },
    }))
}

const settingSection = {
  name: 'General Settings',
  opened: false,
  // icon: SettingsIcon,
  views: [
    {
      label: 'Website Settings',
      icon: SettingsIcon,
      to: 'Website Setup',
    },
    {
      label: 'Menu',
      icon: MenuIcon,
      to: 'Menu',
    },
    {
      label: 'Settings',
      icon: FormSetupIcon,
      to: 'CMS Settings',
    },
    {
      label: 'Header',
      icon: HeaderIcon,
      to: 'Header Page',
    },
    {
      label: 'Footer',
      icon: FooterIcon,
      to: 'Footer Page',
    },
  ],
}

const allViews = computed(() => {
  if (!siteConfigLoaded.value) {
    return []
  }

  // Nhánh giao diện mới
  if (views.data?.website_primary == 1 && showSettings.value) {
    changeNameWebsiteEdit(views.data?.name_web)
    let _views = []
    _views.push(dashboardSection)
    _views.push(jobOpeningSection)
    _views.push({
      name: 'Candidate account',
      opened: false,
      views: [
        {
          label: 'CMS Candidate',
          icon: DisplayIcon,
          to: 'cms_candidates',
        },
        ...getCmsCandidateViews()
      ]
    })
    _views.push(settingSection)
    if (views.data?.list_page) {
      let items_view = []
      views.data?.list_page.forEach((el) => {
        if (!candidatePages.includes(el.name_page)) {
          items_view.push({
            label: el.name_page,
            icon: getIcon(el.icon),
            to: {
              name: 'Page',
              query: { view: el.name },
            },
          })
        }
      })
      if (views.data?.open_add_new_page) {
        items_view.push({
          label: 'Add New Page',
          icon: NewPageIcon,
          to: 'New Page',
        })
      }
      _views.push({
        name: 'Page List',
        opened: false,
        views: items_view,
      })
    }
    return _views
  }

  // Nhánh else: dùng giao diện cũ
  let _views = [
    {
      name: 'Publish',
      hideLabel: true,
      opened: true,
      views: links,
    },
  ]

  if (views.data?.website_primary == 1) {
    changeNameWebsiteEdit(views.data?.name_web)
    _views.push({
      name: 'Dashboard',
      opened: true,
      views: [
        {
          label: 'Dashboard',
          icon: ChartIcon,
          to: 'Dashboard',
        },
      ],
    })
    _views.push({
      name: 'General Settings',
      opened: true,
      views: [
        {
          label: 'Website Settings',
          icon: SettingsIcon,
          to: 'Website Setup',
        },
        {
          label: 'Menu',
          icon: MenuIcon,
          to: 'Menu',
        },
        {
          label: 'Settings',
          icon: FormSetupIcon,
          to: 'CMS Settings',
        },
      ],
    })
    if (views.data?.list_page) {
      let items_view = [
        {
          label: 'Header',
          icon: HeaderIcon,
          to: 'Header Page',
        },
        {
          label: 'Footer',
          icon: FooterIcon,
          to: 'Footer Page',
        },
      ]
      views.data?.list_page.forEach((el) => {
        items_view.push({
          label: el.name_page,
          icon: getIcon(el.icon),
          to: {
            name: 'Page',
            query: { view: el.name },
          },
        })
      })
      if (views.data?.open_add_new_page) {
        items_view.push({
          label: 'Add New Page',
          icon: NewPageIcon,
          to: 'New Page',
        })
      }
      _views.push({
        name: 'Page List',
        opened: true,
        views: items_view,
      })
    }
    _views.push({
      name: 'Forms',
      opened: true,
      views: [
        {
          label: 'Form management',
          icon: FormIcon,
          to: 'Forms',
        },
      ],
    })
  }
  return _views
})

function parseView(views) {
  return views.map((view) => {
    return {
      label: view.label,
      icon: getIcon(view.route_name),
      to: {
        name: view.route_name,
        query: { view: view.name },
      },
    }
  })
}

function getIcon(name) {
  switch (name) {
    case 'PolicyIconV1':
      return PolicyIconV1
    case 'WebpageIcon':
      return WebpageIcon
    case 'TemplatePageIcon':
      return TemplatePageIcon
    case 'HeaderIcon':
      return HeaderIcon
    case 'FooterIcon':
      return FooterIcon
    case 'HomeIcon':
      return HomeIcon
    case 'OrganizationsIcon':
      return OrganizationsIcon
    case 'ServiceIcon':
      return ServiceIcon
    case 'NewPageIcon':
      return NewPageIcon
    case 'NewsIcon':
      return NewsIcon
    case 'ContactsIcon':
      return ContactsIcon
    case 'DescriptionIcon':
      return DescriptionIcon
    default:
      return WebpageIcon
  }
}

function openDocs() {
  window.open('#', '_blank')
}
</script>
