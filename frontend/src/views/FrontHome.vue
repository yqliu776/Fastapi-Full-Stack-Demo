<script setup lang="ts">
const appName = import.meta.env.VITE_APP_TITLE || 'Fast Full Stack Demo';
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8090';
</script>

<template>
  <main class="front-home">
    <section class="front-shell">
      <p class="eyebrow">Public App</p>
      <h1>{{ appName }}</h1>
      <p class="summary">
        前台业务首页。这里用于承载用户侧页面，后台管理入口由环境变量单独配置。
      </p>
      <div class="status-row">
        <span>API</span>
        <strong>{{ apiBaseUrl }}</strong>
      </div>
    </section>
  </main>
</template>

<style scoped>
.front-home {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #f3f4f6;
  color: #111827;
  padding: 32px;
}

.front-shell {
  width: min(720px, 100%);
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}

.eyebrow {
  margin: 0 0 12px;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
}

h1 {
  margin: 0;
  font-size: 34px;
  line-height: 1.2;
}

.summary {
  margin: 18px 0 28px;
  color: #4b5563;
  line-height: 1.7;
}

.status-row {
  display: flex;
  gap: 12px;
  align-items: center;
  padding-top: 18px;
  border-top: 1px solid #e5e7eb;
  color: #6b7280;
}

.status-row strong {
  color: #111827;
  font-weight: 600;
}
</style>
