import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import { createPinia } from 'pinia'
import CKEditor from '@ckeditor/ckeditor5-vue'
import { usePermissionStore } from "./stores/permission";
import { usersStore } from "./stores/user";

import {
  Button,
  Input,
  TextInput,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  setConfig,
  frappeRequest,
  FeatherIcon,
  Tooltip,
} from 'frappe-ui'
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'

import translationPlugin from './translation'
import { createDialog } from './utils/dialogs'
import { initSocket } from './socket'

import vue3PhotoPreview from 'vue3-photo-preview'
import 'vue3-photo-preview/dist/index.css'

import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

import './index.css'

let globalComponents = {
  Button,
  TextInput,
  Input,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  FeatherIcon,
  Tooltip,
  LoadingIndicator,
  VueDatePicker,
}

// create a pinia instance
let pinia = createPinia()

let app = createApp(App)
const socket = initSocket()

setConfig('resourceFetcher', frappeRequest)

app.use(CKEditor)
app.use(pinia)
app.use(router)
app.use(translationPlugin)
app.use(vue3PhotoPreview)
for (let key in globalComponents) {
  app.component(key, globalComponents[key])
}

// app.provide('$socket', socket)

app.config.globalProperties.$dialog = createDialog

// router.isReady().then(() => {
//   if (import.meta.env.DEV) {
//     frappeRequest({
//       url: '/api/method/go1_cms.www.cms.get_context_for_dev',
//     }).then((values) => {
//       for (let key in values) {
//         window[key] = values[key]
//       }
//       app.mount('#app')
//     })
//   } else {
//     app.mount('#app')
//   }
// })

// if (import.meta.env.DEV) {
//   window.$dialog = createDialog
// }

async function bootstrap() {
	const { allUsers, getUser } = usersStore();
	const permissionStore = usePermissionStore();

	try {
		// Đảm bảo đã load user data
		await getUser.promise;
		
		// Kiểm tra xem getUser.data có tồn tại và có roles không
		if (getUser.data && getUser.data.roles) {
			await permissionStore.loadPermissions(getUser.data.roles);
		} else {
			// Nếu không có data hoặc roles, khởi tạo với quyền truy cập tối thiểu
			console.log("User data or roles not available, initializing with minimal permissions");
			await permissionStore.loadPermissions([]);
		}
	} catch (error) {
		console.error("Error loading user data:", error);
		// Khởi tạo với quyền truy cập trống nếu có lỗi
		await permissionStore.loadPermissions([]);
	}

	app.provide("$allUsers", allUsers);

	let socket;
	if (import.meta.env.DEV) {
		try {
			const values = await frappeRequest({
				url: "/api/method/go1_cms.www.cms.get_context_for_dev",
			});
			for (let key in values) {
				window[key] = values[key];
			}
		} catch (err) {
			console.error("Error loading dev context:", err);
		}
		
		socket = initSocket();
		app.config.globalProperties.$socket = socket;
		window.$dialog = createDialog;
	} else {
		socket = initSocket();
		app.config.globalProperties.$socket = socket;
	}

	app.mount("#app");
}

bootstrap();
