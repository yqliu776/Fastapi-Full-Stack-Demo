<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '@/services/authService';

const router = useRouter();

const username = ref('');
const email = ref('');
const phoneNumber = ref('');
const password = ref('');
const confirmPassword = ref('');
const showPassword = ref(false);
const isLoading = ref(false);
const error = ref<string | null>(null);

// 验证用户名只包含字母、数字和下划线
function validateUsername(value: string): boolean {
  return /^[a-zA-Z0-9_]+$/.test(value);
}

// 简单的邮箱验证
function validateEmail(value: string): boolean {
  return /\S+@\S+\.\S+/.test(value);
}

// 简单的手机号验证（中国大陆手机号格式）
function validatePhoneNumber(value: string): boolean {
  return /^1[3-9]\d{9}$/.test(value);
}

// 密码验证 - 至少6个字符
function validatePassword(value: string): boolean {
  return value.length >= 6;
}

// 验证表单
function validateForm(): boolean {
  if (!username.value) {
    error.value = '用户名不能为空';
    return false;
  }
  
  if (!validateUsername(username.value)) {
    error.value = '用户名只能包含字母、数字和下划线';
    return false;
  }
  
  if (!email.value) {
    error.value = '邮箱不能为空';
    return false;
  }
  
  if (!validateEmail(email.value)) {
    error.value = '请输入有效的邮箱地址';
    return false;
  }
  
  if (!phoneNumber.value) {
    error.value = '手机号不能为空';
    return false;
  }
  
  if (!validatePhoneNumber(phoneNumber.value)) {
    error.value = '请输入有效的手机号码';
    return false;
  }
  
  if (!password.value) {
    error.value = '密码不能为空';
    return false;
  }
  
  if (!validatePassword(password.value)) {
    error.value = '密码长度至少为6个字符';
    return false;
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致';
    return false;
  }
  
  return true;
}

async function handleRegister() {
  if (!validateForm()) {
    return;
  }

  isLoading.value = true;
  error.value = null;
  
  try {
    const response = await register(
      username.value, 
      email.value, 
      phoneNumber.value, 
      password.value
    );
    
    if (response.code === 200) {
      // 注册成功，跳转到登录页
      router.push({
        path: '/login',
        query: { 
          registered: 'true',
          username: username.value
        }
      });
    } else {
      error.value = response.message || '注册失败，请稍后重试';
    }
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const apiError = err as { response?: { data?: { message?: string } } };
      error.value = apiError.response?.data?.message || '注册失败，请稍后重试';
    } else {
      error.value = '注册失败，请稍后重试';
    }
    console.error('注册出错:', err);
  } finally {
    isLoading.value = false;
  }
}

function clearError() {
  error.value = null;
}
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-md">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          用户注册
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          注册一个新账号
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div v-if="error" class="bg-red-50 p-4 rounded-md">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-red-800">
                {{ error }}
              </h3>
            </div>
            <div class="ml-auto pl-3">
              <div class="-mx-1.5 -my-1.5">
                <button
                  type="button"
                  @click="clearError"
                  class="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <span class="sr-only">关闭</span>
                  <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="username" class="sr-only">用户名</label>
            <input
              id="username"
              v-model="username"
              name="username"
              type="text"
              autocomplete="username"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="用户名（仅允许字母、数字和下划线）"
            />
          </div>
          <div>
            <label for="email" class="sr-only">邮箱</label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="邮箱"
            />
          </div>
          <div>
            <label for="phoneNumber" class="sr-only">手机号</label>
            <input
              id="phoneNumber"
              v-model="phoneNumber"
              name="phoneNumber"
              type="tel"
              autocomplete="tel"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="手机号"
            />
          </div>
          <div class="relative">
            <label for="password" class="sr-only">密码</label>
            <input
              id="password"
              v-model="password"
              name="password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="new-password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="密码（至少6个字符）"
            />
          </div>
          <div class="relative">
            <label for="confirmPassword" class="sr-only">确认密码</label>
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              name="confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="new-password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="确认密码"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-sm"
              @click="showPassword = !showPassword"
            >
              <svg v-if="showPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd" />
                <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
              </svg>
            </button>
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <span class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg v-if="!isLoading" class="h-5 w-5 text-indigo-500 group-hover:text-indigo-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
              </svg>
              <svg v-else class="animate-spin h-5 w-5 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ isLoading ? '注册中...' : '注册' }}
          </button>
        </div>
        <div class="flex items-center justify-center">
          <div class="text-sm">
            <router-link to="/login" class="font-medium text-indigo-600 hover:text-indigo-500">
              已有账号？点此登录
            </router-link>
          </div>
        </div>
      </form>
    </div>
  </div>
</template> 