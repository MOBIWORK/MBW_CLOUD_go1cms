import router from '@/router'
import { defineStore } from 'pinia'
import { createResource, call } from 'frappe-ui'
import { ref, computed } from 'vue'

export const usersStore = defineStore('go-user', () => {
  // Thêm state user để lưu trạng thái người dùng
  const user = ref({ name: 'Guest', is_guest: true })
  
  const allUsers = createResource({
    url: 'go1_cms.api.get_all_users',
    cache: ['allUsers'],
  })

  const getUser = createResource({
    url: 'go1_cms.api.get_user_info',
    cache: 'UserInfo',
    // Chỉ tự động tải nếu đã đăng nhập
    auto: computed(() => user.value.name !== 'Guest'),
    // Thêm mặc định cho data
    data: {},
  })

  // Computed để kiểm tra xem người dùng có phải là khách không
  const isGuest = computed(() => user.value.is_guest === true || user.value.name === 'Guest')
  

  return {
    user,
    getUser,
    allUsers,
    isGuest
  }
})