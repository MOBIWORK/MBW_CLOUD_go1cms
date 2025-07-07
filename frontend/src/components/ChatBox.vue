<template>
  <div>
    <!-- Nút mở chatbox -->
    <button
      v-if="!isOpen"
      class="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-blue-600 text-white text-3xl flex items-center justify-center shadow-lg hover:bg-blue-700 z-50"
      @click="isOpen = true"
      aria-label="Mở chat"
    >
      💬
    </button>
    <!-- Chatbox chính -->
    <div v-if="isOpen" class="fixed bottom-6 right-6 w-96 bg-white rounded-xl shadow-2xl overflow-hidden z-50 flex flex-col">
      <div class="flex items-center justify-between bg-blue-600 text-white px-5 py-4 font-bold">
        <span>Trợ lý Website</span>
        <div class="flex items-center gap-2">
          <span class="text-xs font-normal opacity-80">Đang hoạt động</span>
          <button class="ml-2 text-2xl font-bold hover:text-blue-200" @click="isOpen = false" aria-label="Đóng">×</button>
        </div>
      </div>
      <div class="flex-1 px-5 py-4 bg-blue-50 max-h-64 overflow-y-auto">
        <div v-for="(msg, idx) in messages" :key="idx" :class="['flex items-center mb-3', msg.from === 'user' ? 'justify-end' : 'justify-start']">
          <span v-if="msg.from === 'bot'" class="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-600 font-bold mr-2">i</span>
          <span class="bg-white px-3 py-2 rounded-lg shadow text-sm max-w-xs" :class="msg.from === 'bot' ? 'text-blue-700' : 'text-gray-800'">{{ msg.text }}</span>
          <span v-if="msg.from === 'user'" class="ml-2 text-lg">👤</span>
        </div>
      </div>
      <div class="flex flex-wrap gap-2 px-5 pt-2 pb-0 bg-white">
        <label v-for="opt in options" :key="opt.value" class="flex items-center gap-2 bg-blue-50 rounded px-3 py-1 text-sm cursor-pointer">
          <input type="checkbox" v-model="opt.checked" class="accent-blue-600 focus:outline-none focus:ring-0 focus:border-transparent focus:shadow-none" />
          {{ opt.label }}
        </label>
      </div>
      <button class="mx-5 my-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg py-3 font-bold text-base">Tiếp tục</button>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
const isOpen = ref(false)
const messages = [
  { from: 'bot', text: 'Xin chào! Bạn vui lòng cho mình biết tên công ty / tổ chức?' },
  { from: 'user', text: 'Công ty cổ phần Mobiwork Việt Nam' },
  { from: 'bot', text: 'Bạn có câu slogan không? Mình có thể gợi ý nếu bạn chưa có.' },
  { from: 'user', text: 'Gợi ý cho mình nhé' },
  { from: 'bot', text: 'Bạn muốn website có những menu nào?' },
  { from: 'user', text: 'Trang chủ, Giới thiệu công ty, Tuyển dụng, Tin tức, Liên hệ' },
  { from: 'bot', text: 'Bạn muốn hiển thị thông tin liên hệ nào ngay trên trang chủ?' },
]
const options = reactive([
  { label: 'Địa chỉ', value: 'address', checked: true },
  { label: 'Email', value: 'email', checked: true },
  { label: 'Số điện thoại', value: 'phone', checked: true },
  { label: 'Số fax', value: 'fax', checked: false },
  { label: 'Hotline', value: 'hotline', checked: false },
])
</script> 