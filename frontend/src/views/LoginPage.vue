<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { ADMIN_HOME_PATH, ADMIN_REGISTER_PATH } from '@/config/adminRoute';

const username = ref('');
const password = ref('');
const isLoading = ref(false);
const showPassword = ref(false);
const successMessage = ref<string | null>(null);

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();

onMounted(() => {
  if (route.query.registered === 'true') {
    successMessage.value = '注册成功，请登录';
    if (route.query.username) {
      username.value = route.query.username as string;
    }
  }
});

async function handleLogin() {
  if (!username.value || !password.value) {
    return;
  }

  isLoading.value = true;
  successMessage.value = null;
  const success = await userStore.login(username.value, password.value);

  if (success) {
    router.push((route.query.redirect as string) || ADMIN_HOME_PATH);
  }
  isLoading.value = false;
}

function clearSuccessMessage() {
  successMessage.value = null;
}
</script>

<template>
  <div class="login-page">
    <div class="deco deco-1"></div>
    <div class="deco deco-2"></div>
    <div class="deco deco-3"></div>

    <div class="login-card">
      <div class="brand">
        <div class="brand-logo">
          <el-icon :size="26"><Monitor /></el-icon>
        </div>
        <div class="brand-text">
          <h1>管理系统</h1>
          <p>Fast Full Stack Demo · 后台控制台</p>
        </div>
      </div>

      <div class="welcome">
        <h2>欢迎回来</h2>
        <p>请输入您的账号和密码继续访问</p>
      </div>

      <el-alert
        v-if="successMessage"
        :title="successMessage"
        type="success"
        :closable="true"
        show-icon
        class="mb-4"
        @close="clearSuccessMessage"
      />

      <el-alert
        v-if="userStore.error"
        :title="userStore.error"
        type="error"
        :closable="true"
        show-icon
        class="mb-4"
        @close="userStore.clearError()"
      />

      <el-form
        class="login-form"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item>
          <el-input
            v-model="username"
            size="large"
            placeholder="用户名"
            :prefix-icon="'User'"
            clearable
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="password"
            size="large"
            :type="showPassword ? 'text' : 'password'"
            placeholder="密码"
            :prefix-icon="'Lock'"
            autocomplete="current-password"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          class="submit-btn"
          :loading="isLoading"
          native-type="submit"
          @click="handleLogin"
        >
          {{ isLoading ? '登录中...' : '登 录' }}
        </el-button>

        <div class="register-link">
          <router-link :to="ADMIN_REGISTER_PATH" class="link">
            还没有账号？立即注册
          </router-link>
        </div>
      </el-form>
    </div>

    <p class="copyright">© 2026 Fast Full Stack Demo</p>
  </div>
</template>

<style scoped>
.login-page {
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

/* 装饰光斑 */
.deco {
  position: absolute;
  border-radius: 50%;
  filter: blur(2px);
  opacity: 0.35;
  pointer-events: none;
}

.deco-1 {
  width: 280px;
  height: 280px;
  left: -80px;
  bottom: -60px;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.5), transparent 70%);
}

.deco-2 {
  width: 180px;
  height: 180px;
  right: 8%;
  top: 12%;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.5), transparent 70%);
}

.deco-3 {
  width: 120px;
  height: 120px;
  left: 12%;
  top: 16%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.4), transparent 70%);
}

.login-card {
  position: relative;
  z-index: 1;
  width: min(420px, 100%);
  background: rgba(255, 255, 255, 0.98);
  border-radius: 20px;
  padding: 36px 36px 28px;
  box-shadow: 0 24px 60px rgba(2, 6, 23, 0.45);
  backdrop-filter: blur(10px);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 28px;
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

.welcome {
  margin-bottom: 22px;
}

.welcome h2 {
  margin: 0 0 6px;
  font-size: 24px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.welcome p {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.login-form :deep(.el-input__wrapper) {
  padding: 4px 14px;
  border-radius: 10px;
  box-shadow: 0 0 0 1px var(--el-border-color) inset;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--brand-primary) inset;
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

.register-link {
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
