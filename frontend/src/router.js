import { createRouter, createWebHistory } from 'vue-router'
import { usersStore } from '@/stores/user'
import { sessionStore } from '@/stores/session'
import { viewsStore } from '@/stores/views'

const routes = [
  {
    path: '/',
    redirect: { name: 'job_opening' },
    name: 'Home',
  },
  // {
  //   path: '/my-website',
  //   name: 'My Website',
  //   component: () => import('@/pages/MyWebsite.vue'),
  // },
  {
    path: '/interface-repository',
    name: 'Interface Repository',
    component: () => import('@/pages/InterfaceRepository.vue'),
  },
  {
    path: '/interface-repository/:interfaceId',
    name: 'Interface Template',
    component: () => import('@/pages/InterfaceTemplate.vue'),
    props: true,
  },
  {
    path: '/interface',
    name: 'Interface',
    component: () => import('@/pages/Interface.vue'),
  },
  {
    path: '/settings',
    name: 'CMS Settings',
    component: () => import('@/pages/CMSSettings.vue'),
  },
  {
    path: '/website-setup',
    name: 'Website Setup',
    component: () => import('@/pages/WebsiteSetup.vue'),
  },
  {
    path: '/setup-file-template',
    name: 'Setup File Template',
    component: () => import('@/pages/SetupFileTemplate.vue'),
  },
  // {
  //   path: '/form-setup',
  //   name: 'Form Setup',
  //   component: () => import('@/pages/FormSetup.vue'),
  // },
  // {
  //   path: '/contacts',
  //   name: 'Contacts',
  //   component: () => import('@/pages/contact/Contacts.vue'),
  // },
  // {
  //   path: '/contacts/:contactId',
  //   name: 'Contact Detail',
  //   component: () => import('@/pages/contact/ContactDetail.vue'),
  //   props: true,
  // },
  {
    path: '/candidates',
    name: 'candidates',
    component: () => import('@/pages/ats_candidate/Candidates.vue'),
  },
  {
    path: '/job_opening',
    name: 'job_opening',
    component: () => import('@/pages/ats_jobopening/JobOpenings.vue'),
  },
  {
    path: '/ats_job_opening',
    name: 'ats_job_opening',
    component: () => import('@/pages/ats_jobopening/ATS_JobOpenings.vue'),
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/page',
    name: 'Page',
    component: () => import('@/pages/Page.vue'),
  },
  {
    path: '/new-page',
    name: 'New Page',
    component: () => import('@/pages/NewPage.vue'),
  },
  {
    path: '/header-page',
    name: 'Header Page',
    component: () => import('@/pages/HeaderPage.vue'),
  },
  {
    path: '/footer-page',
    name: 'Footer Page',
    component: () => import('@/pages/FooterPage.vue'),
  },
  {
    path: '/posts',
    name: 'Posts',
    component: () => import('@/pages/post/Posts.vue'),
  },
  {
    path: '/posts/create',
    name: 'Post Create',
    component: () => import('@/pages/post/PostCreate.vue'),
  },
  {
    path: '/posts/:postId',
    name: 'Post Detail',
    component: () => import('@/pages/post/PostDetail.vue'),
    props: true,
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('@/pages/category/Categories.vue'),
  },
  {
    path: '/categories/create',
    name: 'Category Create',
    component: () => import('@/pages/category/CategoryCreate.vue'),
  },
  {
    path: '/categories/:categoryId',
    name: 'Category Detail',
    component: () => import('@/pages/category/CategoryDetail.vue'),
    props: true,
  },
  {
    path: '/blog-tags',
    name: 'Blog Tags',
    component: () => import('@/pages/BlogTag/Tags.vue'),
  },
  {
    path: '/blog-tags/create',
    name: 'Blog Tags Create',
    component: () => import('@/pages/BlogTag/TagCreate.vue'),
  },
  {
    path: '/blog-tags/:tagId',
    name: 'Blog Tags Detail',
    component: () => import('@/pages/BlogTag/TagDetail.vue'),
    props: true,
  },
  {
    path: '/menu',
    name: 'Menu',
    component: () => import('@/pages/menu/Menu.vue'),
  },
  {
    path: '/menu/create',
    name: 'Menu Create',
    component: () => import('@/pages/menu/MenuCreate.vue'),
  },
  {
    path: '/menu/:menuId',
    name: 'Menu Detail',
    component: () => import('@/pages/menu/MenuDetail.vue'),
    props: true,
  },
  {
    path: '/forms',
    name: 'Forms',
    component: () => import('@/pages/form/Forms.vue'),
  },
  {
    path: '/forms/:formId',
    name: 'Form Detail',
    component: () => import('@/pages/form/FormDetail.vue'),
    props: true,
  },
  {
    path: '/:invalidpath',
    name: 'Invalid Page',
    component: () => import('@/pages/InvalidPage.vue'),
  },
  {
    path: '/permission-denied',
    name: 'Permission Denied Page',
    component: () => import('@/pages/PermissionDeniedPage.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    path: '/company',
    name: 'Company',
    component: () => import('@/pages/ats_company/Company.vue'),
  },
  {
    path: '/unit',
    name: 'Unit',
    component: () => import('@/pages/ats_unit/Unit.vue'),
  },
  {
    path: '/profession',
    name: 'Profession',
    component: () => import('@/pages/ats_profession/Profession.vue'),
  },
  {
    path: '/level',
    name: 'Level',
    component: () => import('@/pages/ats_level/Level.vue'),
  },
  {
    path: '/location',
    name: 'Location',
    component: () => import('@/pages/ats_location/Location.vue'),
  },
  {
    path: '/position',
    name: 'Position',
    component: () => import('@/pages/ats_position/Position.vue'),
  },
  {
    path: '/country',
    name: 'Country',
    component: () => import('@/pages/ats_country/Country.vue'),
  },
  {
    path: '/province',
    name: 'Province',
    component: () => import('@/pages/ats_province/Province.vue'),
  },
  {
    path: '/district',
    name: 'District',
    component: () => import('@/pages/ats_district/District.vue'),
  },
  {
    path: '/ward',
    name: 'Ward',
    component: () => import('@/pages/ats_ward/Ward.vue'),
  },
  {
    path: '/process',
    name: 'Process',
    component: () => import('@/pages/ats_process/ATS_Process.vue'),
  },
  {
    path: '/email-account',
    name: 'EmailAccount',
    component: () => import('@/pages/email-account/EmailAccount.vue'),
  },
  {
    path: '/data-import',
    name: 'Data Import',
    component: () => import('@/pages/import_data/ImportData.vue'),
  },
  {
    path: '/data-import/:importId',
    name: 'Data Import Detail',
    component: () => import('@/pages/import_data/ImportDataDetail.vue'),
    props: true,
  },
  {
    path: '/data-import/:importId',
    name: 'Data Import New',
    component: () => import('@/pages/import_data/ImportDataDetail.vue'),
    props: true,
  },
  {
    path: '/ats_job_openings/:jobOpeningId',
    name: 'ats_job_opening_detail',
    component: () => import('@/pages/ats_jobopening/ATS_JobOpening_Detail.vue'),
    props: true,
    meta: { doctype: 'ATS_JobOpening' },
  },
  {
    path: '/ats_job_opening_view/:jobOpeningId',
    name: 'ats_job_opening_view',
    component: () => import('@/pages/ats_jobopening/ATS_JobOpening_View.vue'),
    props: true,
    meta: { doctype: 'ATS_JobOpening' },
  },
  {
    path: '/cms_candidates',
    name: 'cms_candidates',
    component: () => import('@/pages/cms_candidate/Candidates.vue'),
  },
  {
		path: "/wizard",
		name: "onboarding_wizard",
		component: () => import("@/pages/wizard/OnboardingWizard.vue"),
		meta: { 
			layout: 'wizard',
			// requiresAuth: true 
		}
	},
]

const scrollBehavior = (to, from, savedPosition) => {
  if (to.name === from.name) {
    to.meta?.scrollPos && (to.meta.scrollPos.top = 0)
    return { left: 0, top: 0 }
  }
  const scrollpos = to.meta?.scrollPos || { left: 0, top: 0 }

  if (scrollpos.top > 0) {
    setTimeout(() => {
      let el = document.querySelector('#list-rows')
      el.scrollTo({
        top: scrollpos.top,
        left: scrollpos.left,
        behavior: 'smooth',
      })
    }, 300)
  }
}

let router = createRouter({
  history: createWebHistory('/cms'),
  routes,
  scrollBehavior,
})

router.beforeEach(async (to, from, next) => {
  const { isLoggedIn, isSystemUser } = sessionStore()

  isLoggedIn && (await usersStore.promise)

  if (from.meta?.scrollPos) {
    from.meta.scrollPos.top = document.querySelector('#list-rows')?.scrollTop
  }

  if (to.name == 'Setup File Template' && isLoggedIn) {
    const { views } = viewsStore()
    const data = await views.fetch()
    if (!data?.developer_mode) {
      next({ name: 'Interface Repository' })
    }
  }

  // Check if trying to access Company route and redirect if mbw_ats_site_name exists
  if (
    (to.name == 'Company' ||
      to.name == 'Unit' ||
      to.name == 'Profession' ||
      to.name == 'Level' ||
      to.name == 'Location' ||
      to.name == 'Position' ||
      to.name == 'Country' ||
      to.name == 'Province' ||
      to.name == 'District' ||
      to.name == 'Ward' ||
      to.name == 'Process' ||
      to.name == 'EmailAccount' ||
      to.name == 'cms_candidates') &&
    isLoggedIn
  ) {
    try {
      const response = await fetch(
        '/api/method/go1_cms.api.site_config.get_site_config',
      )
      const data = await response.json()
      if (
        data.message &&
        data.message.success &&
        data.message.mbw_ats_site_name &&
        data.message.mbw_ats_site_name.trim() !== ''
      ) {
        next({ name: 'job_opening' })
        return
      }
    } catch (error) {
      console.error('Error checking site config:', error)
    }
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Interface Repository' })
  } else if (to.name !== 'Login' && to.name !== 'onboarding_wizard' && !isLoggedIn) {
    next({ name: 'Login' })
  } else if (
    isLoggedIn &&
    !isSystemUser &&
    !['Permission Denied Page', 'Invalid Page', 'onboarding_wizard'].includes(to.name)
  ) {
    next({ name: 'Permission Denied Page' })
  } else if (to.matched.length === 0) {
    next({ name: 'Invalid Page' })
  } else {
    next()
  }
})

export default router
