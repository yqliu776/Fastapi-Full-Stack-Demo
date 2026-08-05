<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const title = computed(() => String(route.meta.title || '页面未配置'));
</script>

<template>
  <div class="unsupported-page">
    <el-result icon="warning" :title="title" sub-title="该菜单尚未绑定可渲染的前端页面，请联系管理员配置组件。">
    </el-result>
  </div>
</template>

<style scoped>
.unsupported-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 420px;
  background: var(--app-card-bg);
  border: 1px solid var(--app-border);
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}
</style>
