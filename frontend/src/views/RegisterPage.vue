<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { register } from '@/services/authService';
import { ADMIN_LOGIN_PATH } from '@/config/adminRoute';

const router = useRouter();

const username = ref('');
const email = ref('');
const phoneNumber = ref('');
const password = ref('');
const confirmPassword = ref('');
const showPassword = ref(false);
const isLoading = ref(false);
const error = ref<string | null>(null);

function validateUsername(value: string): boolean {
  return /^[a-zA-Z0-9_]+$/.test(value);
}

function validateEmail(value: string): boolean {
  return /\S+@\S+\.\S+/.test(value);
}

function validatePhoneNumber(value: string): boolean {
  return /^1[3-9]\d{9}$/.test(value);
}

function validatePassword(value: string): boolean {
  return value.length >= 6;
}

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
      router.push({
        path: ADMIN_LOGIN_PATH,
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
  <div class="register-page">
    <div class="deco deco-1"></div>
    <div class="deco deco-2"></div>

    <div class="register-card">
      <div class="brand">
        <div class="brand-logo">
          <el-icon :size="26"><User /></el-icon>
        </div>
        <div class="brand-text">
          <h1>创建账号</h1>
          <p>注册一个新账号加入管理系统</p>
        </div>
      </div>

      <el-alert
        v-if="error"
        :title="error"
        type="error"
        :closable="true"
        show-icon
        class="mb-4"
        @close="clearError"
      />

      <el-form class="register-form" label-position="top" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input
            v-model="username"
            size="large"
            placeholder="用户名（仅允许字母、数字和下划线）"
            :prefix-icon="'User'"
            clearable
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="email"
            size="large"
            placeholder="邮箱"
            :prefix-icon="'Message'"
            clearable
            autocomplete="email"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="phoneNumber"
            size="large"
            placeholder="手机号"
            :prefix-icon="'Iphone'"
            clearable
            autocomplete="tel"
          />
        </el-form-item>

        <div class="form-row">
          <el-form-item>
            <el-input
              v-model="password"
              size="large"
              :type="showPassword ? 'text' : 'password'"
              placeholder="密码（至少6个字符）"
              :prefix-icon="'Lock'"
              show-password
              autocomplete="new-password"
            />
          </el-form-item>

          <el-form-item>
            <el-input
              v-model="confirmPassword"
              size="large"
              :type="showPassword ? 'text' : 'password'"
              placeholder="确认密码"
              :prefix-icon="'Lock'"
              autocomplete="new-password"
            />
          </el-form-item>
        </div>

        <el-button
          type="primary"
          size="large"
          class="submit-btn"
          :loading="isLoading"
          native-type="submit"
          @click="handleRegister"
        >
          {{ isLoading ? '注册中...' : '注 册' }}
        </el-button>

        <div class="login-link">
          <router-link :to="ADMIN_LOGIN_PATH" class="link">
            已有账号？返回登录
          </router-link>
        </div>
      </el-form>
    </div>

    <p class="copyright">© 2026 Fast Full Stack Demo</p>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(1200px 600px at 15% -10%, rgba(99, 102, 241, 0.28), transparent 60%),
    radial-gradient(1000px 700px at 110% 110%, rgba(124, 58, 237, 0.25), transparent 55%),
    linear-gradient(135deg, #0f172a 0%, #1e1b4b 55%, #312e81 100%);
  padding: 24px;
}

.deco {
  position: absolute;
  border-radius: 50%;
  opacity: 0.3;
  pointer-events: none;
}

.deco-1 {
  width: 260px;
  height: 260px;
  left: -70px;
  bottom: -50px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.5), transparent 70%);
}

.deco-2 {
  width: 160px;
  height: 160px;
  right: 10%;
  top: 14%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.4), transparent 70%);
}

.register-card {
  position: relative;
  z-index: 1;
  width: min(480px, 100%);
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20px;
  padding: 32px 36px 26px;
  box-shadow: 0 24px 60px rgba(2, 6, 23, 0.45);
  max-height: calc(100vh - 60px);
  overflow-y: auto;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: var(--brand-gradient);
  color: #fff;
  box-shadow: 0 8px 20px rgba(79, 70, 229, 0.35);
  flex-shrink: 0;
}

.brand-text h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.brand-text p {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.register-form :deep(.el-input__wrapper) {
  padding: 4px 14px;
  border-radius: 10px;
  box-shadow: 0 0 0 1px var(--el-border-color) inset;
}

.register-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--brand-primary) inset;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

@media (max-width: 480px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}

.submit-btn {
  width: 100%;
  height: 44px;
  margin-top: 4px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.2em;
  background: var(--brand-gradient);
  border: none;
}

.submit-btn:hover,
.submit-btn:focus {
  background: var(--brand-gradient);
  opacity: 0.92;
}

.login-link {
  margin-top: 18px;
  text-align: center;
}

.link {
  font-size: 14px;
  color: var(--brand-primary);
  font-weight: 500;
}

.link:hover {
  color: var(--brand-primary-dark);
}

.copyright {
  position: absolute;
  bottom: 18px;
  left: 0;
  right: 0;
  text-align: center;
  color: rgba(226, 232, 240, 0.55);
  font-size: 12px;
  margin: 0;
}
</style>
