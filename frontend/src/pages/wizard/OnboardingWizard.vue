<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-4 py-8 sm:py-12">
    <!-- Header -->
    <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-center mb-2">Chào mừng đến với CMS</h1>
    <p class="text-center text-gray-600 mb-6 sm:mb-8 text-sm sm:text-base">Thiết lập thông tin cơ bản cho website của bạn</p>

    <!-- Stepper -->
    <div class="flex items-center justify-center mb-6 sm:mb-10">
      <div class="flex items-center">
        <div 
          class="w-7 h-7 sm:w-9 sm:h-9 flex items-center justify-center rounded-full font-bold text-sm sm:text-base"
          :class="currentStep > 1 ? 'bg-green-500 text-white' : currentStep === 1 ? 'bg-gradient-to-r from-[#8e9fff] to-[#6c7ae0] text-white' : 'bg-gray-200 text-gray-500'"
        >
          <svg v-if="currentStep > 1" class="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
          </svg>
          <span v-else>1</span>
        </div>
        <div class="w-16 h-1 bg-gray-300 mx-2"></div>
        <div 
          class="w-7 h-7 sm:w-9 sm:h-9 flex items-center justify-center rounded-full font-bold text-sm sm:text-base"
          :class="currentStep > 2 ? 'bg-green-500 text-white' : currentStep === 2 ? 'bg-gradient-to-r from-[#8e9fff] to-[#6c7ae0] text-white' : 'bg-gray-200 text-gray-500'"
        >
          <svg v-if="currentStep > 2" class="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
          </svg>
          <span v-else>2</span>
        </div>
        <div class="w-16 h-1 bg-gray-300 mx-2"></div>
        <div 
          class="w-7 h-7 sm:w-9 sm:h-9 flex items-center justify-center rounded-full font-bold text-sm sm:text-base"
          :class="currentStep > 3 ? 'bg-green-500 text-white' : currentStep === 3 ? 'bg-gradient-to-r from-[#8e9fff] to-[#6c7ae0] text-white' : 'bg-gray-200 text-gray-500'"
        >
          <svg v-if="currentStep > 3" class="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
          </svg>
          <span v-else>3</span>
        </div>
        <div class="w-16 h-1 bg-gray-300 mx-2"></div>
        <div 
          class="w-7 h-7 sm:w-9 sm:h-9 flex items-center justify-center rounded-full font-bold text-sm sm:text-base"
          :class="currentStep > 4 ? 'bg-green-500 text-white' : currentStep === 4 ? 'bg-gradient-to-r from-[#8e9fff] to-[#6c7ae0] text-white' : 'bg-gray-200 text-gray-500'"
        >
          <svg v-if="currentStep > 4" class="w-4 h-4 sm:w-5 sm:h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
          </svg>
          <span v-else>4</span>
        </div>
      </div>
    </div>

    <!-- Step 1 Content -->
    <div v-if="currentStep === 1" class="bg-white rounded-xl shadow-md w-full max-w-sm sm:max-w-xl p-4 sm:p-8 flex flex-col items-center">
      <h2 class="text-lg sm:text-xl font-bold mb-2 text-center">Bước 1: Thông tin website</h2>
      <p class="text-center text-gray-700 mb-4 sm:mb-6 text-sm sm:text-base">Bạn đã có website công ty chưa? Chúng tôi có thể tự động đọc thông tin từ website của bạn.</p>

      <!-- Option 1: Có website -->
      <div 
        @click="showWebsiteInput = true"
        class="w-full border-2 border-dashed border-blue-400 rounded-lg p-4 sm:p-6 mb-4 flex flex-col items-center cursor-pointer hover:bg-blue-50 transition"
        :class="{ 'bg-blue-50': showWebsiteInput }"
      >
        <div class="font-bold text-base sm:text-lg mb-1">Có, tôi đã có website</div>
        <div class="text-gray-600 text-center mb-2 text-sm sm:text-base">Nhập URL website để tự động đọc thông tin</div>
        
        <!-- Input field và button chỉ hiện khi click -->
        <div v-if="showWebsiteInput" class="w-full max-w-xs mt-4">
          <input 
            v-model="websiteUrl"
            type="text" 
            placeholder="https://example.com" 
            class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300 mb-3 text-sm sm:text-base" 
          />
          <button 
            @click.stop="readWebsiteInfo"
            class="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition text-sm sm:text-base"
          >
            Đọc thông tin website
          </button>
        </div>
      </div>

      <div class="my-2 text-gray-500">hoặc</div>

      <!-- Option 2: Nhập thủ công -->
      <div 
        @click="goToStep(2)"
        class="w-full border-2 border-dashed border-gray-300 rounded-lg p-4 sm:p-6 flex flex-col items-center cursor-pointer hover:bg-gray-50 transition"
      >
        <div class="font-bold text-base sm:text-lg mb-1">Chưa có, nhập thủ công</div>
        <div class="text-gray-600 text-center text-sm sm:text-base">Tôi sẽ nhập thông tin công ty thủ công</div>
      </div>
    </div>

    <!-- Step 2 Content -->
    <div v-if="currentStep === 2" class="bg-white rounded-xl shadow-md w-full max-w-sm sm:max-w-2xl lg:max-w-4xl p-4 sm:p-6 lg:p-8">
      <h2 class="text-lg sm:text-xl font-bold mb-4 sm:mb-6 text-center">Bước 2: Thông tin công ty</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
        <!-- Tên công ty -->
        <div class="col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-2">Tên công ty *</label>
          <input 
            v-model="companyInfo.name"
            type="text" 
            placeholder="Nhập tên công ty" 
            class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300 text-sm sm:text-base" 
          />
        </div>

        <!-- Số điện thoại -->
        <div class="col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-2">Số điện thoại</label>
          <input 
            v-model="companyInfo.phone"
            type="text" 
            placeholder="0123 456 789" 
            class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300 text-sm sm:text-base" 
          />
        </div>

        <!-- Email -->
        <div class="col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
          <input 
            v-model="companyInfo.email"
            type="email" 
            placeholder="info@company.com" 
            class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300 text-sm sm:text-base" 
          />
        </div>

        <!-- YouTube -->
        <div class="col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-2">YouTube</label>
          <input 
            v-model="companyInfo.youtube"
            type="url" 
            placeholder="https://youtube.com/@channel" 
            class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300 text-sm sm:text-base" 
          />
        </div>

        <!-- Facebook -->
        <div class="col-span-1">
          <label class="block text-sm font-medium text-gray-700 mb-2">Facebook</label>
          <input 
            v-model="companyInfo.facebook"
            type="url" 
            placeholder="https://facebook.com/page" 
            class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300 text-sm sm:text-base" 
          />
        </div>

        <!-- Địa chỉ -->
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-2">Địa chỉ</label>
          <textarea 
            v-model="companyInfo.address"
            placeholder="Nhập địa chỉ công ty" 
            rows="3"
            class="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300 text-sm sm:text-base" 
          ></textarea>
        </div>

        <!-- Map placeholder -->
        <div class="col-span-2">
          <div class="w-full h-32 sm:h-48 bg-gray-200 rounded-lg flex items-center justify-center text-gray-500 text-sm sm:text-base">
            Bản đồ sẽ hiển thị khi nhập địa chỉ
          </div>
        </div>
      </div>

      <!-- Navigation buttons -->
      <div class="flex justify-between mt-6 sm:mt-8">
        <button 
          @click="goToStep(1)"
          class="px-4 sm:px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition text-sm sm:text-base"
        >
          Quay lại
        </button>
        <button 
          @click="goToStep(3)"
          class="px-4 sm:px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition text-sm sm:text-base"
        >
          Tiếp tục
        </button>
      </div>
    </div>

    <!-- Step 3 Content -->
    <div v-if="currentStep === 3" class="bg-white rounded-xl shadow-md w-full max-w-2xl p-8">
      <h2 class="text-xl font-bold mb-6 text-center">Bước 3: Hình ảnh</h2>
      <div class="mb-6">
        <label class="block font-medium mb-2">Ảnh Favicon <span class="text-xs text-gray-500">(32x32px)</span></label>
        <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center mb-2">
          <input 
            ref="faviconInput"
            type="file" 
            accept="image/png, image/jpeg"
            class="hidden"
            @change="onFaviconChange"
          />
          <button 
            class="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 transition mb-2"
            @click.prevent="$refs.faviconInput.click()"
          >
            Chọn ảnh favicon
          </button>
          <div v-if="faviconFileName" class="text-sm text-gray-700 mb-1">{{ faviconFileName }}</div>
          <div class="text-xs text-gray-500">PNG, JPG tối đa 2MB</div>
        </div>
      </div>
      <div class="mb-6">
        <label class="block font-medium mb-2">Ảnh trang chủ</label>
        <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center mb-2">
          <input 
            ref="mainImgInput"
            type="file" 
            accept="image/png, image/jpeg"
            class="hidden"
            @change="onMainImgChange"
          />
          <button 
            class="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600 transition mb-2"
            @click.prevent="$refs.mainImgInput.click()"
          >
            Chọn ảnh trang chủ
          </button>
          <div v-if="mainImgFileName" class="text-sm text-gray-700 mb-1">{{ mainImgFileName }}</div>
          <div class="text-xs text-gray-500">PNG, JPG tối đa 5MB - Có thể crop sau khi upload</div>
        </div>
      </div>
      <div class="flex justify-between mt-8">
        <button 
          @click="goToStep(2)"
          class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
        >
          Quay lại
        </button>
        <button 
          @click="goToStep(4)"
          class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition"
        >
          Tiếp tục
        </button>
      </div>
    </div>

    <!-- Step 4 Content -->
    <div v-if="currentStep === 4" class="bg-white rounded-xl shadow-md w-full max-w-2xl p-8">
      <h2 class="text-xl font-bold mb-6 text-center">Bước 4: Giới thiệu công ty</h2>
      <div class="mb-6">
        <label class="block font-medium mb-2">Nội dung giới thiệu (HTML)</label>
        <div class="border border-gray-300 rounded-t-lg px-4 pt-3 pb-2 flex items-center space-x-2 bg-gray-50">
          <button v-for="i in 5" :key="i" class="w-8 h-8 border border-gray-300 rounded bg-white flex items-center justify-center mr-1">
            <i class="fa fa-globe text-gray-400"></i>
          </button>
          <span class="border-l border-gray-300 h-6 mx-2"></span>
          <button 
            class="px-3 py-1 rounded border border-gray-300 bg-white text-gray-700 font-semibold text-sm"
            :class="{ 'bg-gray-200': isHtmlMode }"
            @click="isHtmlMode = !isHtmlMode"
          >HTML</button>
        </div>
        <textarea
          v-model="introModel"
          rows="7"
          :placeholder="isHtmlMode ? '<p>Nhập nội dung giới thiệu công ty của bạn tại đây...</p>' : 'Nhập nội dung giới thiệu công ty của bạn tại đây...'"
          :class="[
            'w-full border-t-0 border border-gray-300 rounded-b-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-300 resize-none',
            isHtmlMode ? 'font-mono text-sm' : ''
          ]"
        ></textarea>
      </div>
      <div class="mb-6">
        <label class="block font-medium mb-2">Xem trước:</label>
        <div class="w-full min-h-[80px] border border-gray-200 rounded-lg bg-gray-50 px-3 py-2 text-gray-600" v-html="companyIntro || 'Nội dung xem trước sẽ hiển thị ở đây...'">
        </div>
      </div>
      <div class="flex justify-between mt-8">
        <button 
          @click="goToStep(3)"
          class="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
        >
          Quay lại
        </button>
        <button 
          @click="finishSetup"
          class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
        >
          Hoàn thành thiết lập
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const currentStep = ref(1)
const showWebsiteInput = ref(false)
const showManualInput = ref(false)
const websiteUrl = ref('')

const companyInfo = ref({
  name: '',
  phone: '',
  email: '',
  youtube: '',
  facebook: '',
  address: ''
})

const faviconFileName = ref('')
const mainImgFileName = ref('')
const companyIntro = ref('') // HTML code
const plainText = ref('')    // Plain text
const isHtmlMode = ref(false)

// Khi chuyển đổi chế độ, đồng bộ dữ liệu
watch(isHtmlMode, (val, oldVal) => {
  if (val && !oldVal) {
    // Chuyển từ plain text sang HTML
    companyIntro.value = plainText.value
      ? `<p>${plainText.value.replace(/\n/g, '</p><p>')}</p>`
      : ''
  } else if (!val && oldVal) {
    // Chuyển từ HTML sang plain text
    const tmp = document.createElement('div')
    tmp.innerHTML = companyIntro.value
    // Lấy text, giữ xuống dòng nếu có nhiều <p>
    plainText.value = Array.from(tmp.querySelectorAll('p')).map(p => p.textContent).join('\n') || tmp.textContent || ''
  }
})

const introModel = computed({
  get() {
    return isHtmlMode.value ? companyIntro.value : plainText.value
  },
  set(val) {
    if (isHtmlMode.value) {
      companyIntro.value = val
    } else {
      plainText.value = val
    }
  }
})

const goToStep = (step) => {
  currentStep.value = step
}

const readWebsiteInfo = () => {
  // Logic để đọc thông tin website sẽ được implement sau
  console.log('Reading website info from:', websiteUrl.value)
}

const onFaviconChange = (e) => {
  const file = e.target.files[0]
  faviconFileName.value = file ? file.name : ''
}
const onMainImgChange = (e) => {
  const file = e.target.files[0]
  mainImgFileName.value = file ? file.name : ''
}

const finishSetup = () => {
  // Logic hoàn thành thiết lập sẽ bổ sung sau
  alert('Thiết lập hoàn tất!')
}
</script>

<style scoped>
/* Nếu không dùng Tailwind, có thể thêm CSS custom ở đây */
</style>