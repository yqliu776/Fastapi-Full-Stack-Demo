<script setup lang="ts">
import { useRouter } from 'vue-router';
import { ADMIN_LOGIN_PATH, ADMIN_HOME_PATH } from '@/config/adminRoute';
import { getToken } from '@/services/authService';

const router = useRouter();
const appName = import.meta.env.VITE_APP_TITLE || 'Fast Full Stack Demo';
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8090';

const goConsole = () => {
  router.push(getToken() ? ADMIN_HOME_PATH : ADMIN_LOGIN_PATH);
};
</script>

<template>
  <main class="front-home">
    <section class="hero">
      <div class="hero-badge">
        <el-icon><Lightning /></el-icon>
        FastAPI × Vue 3 × Element Plus
      </div>
      <h1>{{ appName }}</h1>
      <p class="hero-summary">
        一套开箱即用的全栈应用模板：JWT 认证、RBAC 权限、动态菜单、API 限流，
        覆盖现代化 Web 应用的完整技术栈与最佳实践。
      </p>
      <div class="hero-actions">
        <el-button type="primary" size="large" round @click="goConsole">
          进入管理后台
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </section>

    <section class="features">
      <div class="feature-card">
        <div class="feature-icon">
          <el-icon :size="22"><Lock /></el-icon>
        </div>
        <h3>安全认证</h3>
        <p>JWT 令牌、OAuth2 支持，开箱即用的登录注册与权限守卫。</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">
          <el-icon :size="22"><Grid /></el-icon>
        </div>
        <h3>RBAC 权限</h3>
        <p>角色、权限、菜单三级模型，页面与接口双重鉴权。</p>
      </div>
      <div class="feature-card">
        <div class="feature-icon">
          <el-icon :size="22"><DataLine /></el-icon>
        </div>
        <h3>限流防护</h3>
        <p>令牌桶 / 滑动窗口算法，白名单、黑名单与违规日志。</p>
      </div>
    </section>

    <footer class="footer">
      <span class="status-label">API 服务地址</span>
      <code class="api-url">{{ apiBaseUrl }}</code>
    </footer>
  </main>
</template>

<style scoped>
.front-home {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 44px;
  padding: 40px 24px;
  background:
    radial-gradient(900px 500px at 80% -10%, rgba(99, 102, 241, 0.22), transparent 60%),
    radial-gradient(700px 500px at 0% 110%, rgba(124, 58, 237, 0.18), transparent 55%),
    var(--app-bg);
}

.hero {
  text-align: center;
  max-width: 720px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: var(--brand-primary-light);
  color: var(--brand-primary);
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 20px;
}

.hero h1 {
  margin: 0 0 16px;
  font-size: clamp(32px, 6vw, 48px);
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--el-text-color-primary);
}

.hero-summary {
  margin: 0 auto 28px;
  max-width: 560px;
  font-size: 16px;
  line-height: 1.8;
  color: var(--el-text-color-secondary);
}

.hero-actions {
  display: flex;
  justify-content: center;
}

.features {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  width: min(920px, 100%);
}

@media (max-width: 768px) {
  .features {
    grid-template-columns: 1fr;
  }
}

.feature-card {
  background: var(--app-card-bg);
  border: 1px solid var(--app-border);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 30px rgba(15, 23, 42, 0.1);
}

.feature-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: var(--brand-gradient);
  color: #fff;
  margin-bottom: 14px;
}

.feature-card h3 {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.feature-card p {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: var(--el-text-color-secondary);
}

.footer {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.status-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.api-url {
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 13px;
  background: var(--app-card-bg);
  border: 1px solid var(--app-border);
  padding: 5px 12px;
  border-radius: 8px;
  color: var(--brand-primary);
}
</style>
