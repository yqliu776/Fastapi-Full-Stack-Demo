<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const title = computed(() => String(route.meta.title || '页面未配置'));
</script>

<template>
  <section class="unsupported-page">
    <div class="panel">
      <h1>{{ title }}</h1>
      <p>该菜单尚未绑定可渲染的前端页面。</p>
    </div>
  </section>
</template>

<style scoped>
.unsupported-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 360px;
}

.panel {
  width: min(520px, 100%);
  padding: 28px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
  text-align: center;
}

h1 {
  margin: 0 0 8px;
  color: #111827;
  font-size: 20px;
  font-weight: 600;
}

p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}
</style>
