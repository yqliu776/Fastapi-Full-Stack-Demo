<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ADMIN_HOME_PATH } from '@/config/adminRoute';

const route = useRoute();
const router = useRouter();

interface BreadcrumbItem {
  path: string;
  title: string;
}

const levelList = ref<BreadcrumbItem[]>([]);

const getBreadcrumb = () => {
  const matched = route.matched.filter(item => item.meta && item.meta.title);

  const breadcrumbs: BreadcrumbItem[] = matched.map(item => ({
    path: item.path,
    title: item.meta?.title as string
  }));

  if (breadcrumbs.length > 0 && breadcrumbs[0].path !== ADMIN_HOME_PATH) {
    breadcrumbs.unshift({
      path: ADMIN_HOME_PATH,
      title: '首页'
    });
  }

  levelList.value = breadcrumbs;
};

const handleLink = (path: string) => {
  router.push(path);
};

watch(
  () => route.path,
  () => getBreadcrumb(),
  { immediate: true }
);
</script>

<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item v-for="(item, index) in levelList" :key="item.path">
      <span v-if="index === levelList.length - 1" class="no-redirect">{{ item.title }}</span>
      <a v-else @click.prevent="handleLink(item.path)" class="redirect">{{ item.title }}</a>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<style scoped>
.redirect {
  color: var(--el-color-primary);
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s;
}

.redirect:hover {
  color: var(--el-color-primary-dark-2);
}

.no-redirect {
  color: var(--el-text-color-secondary);
  font-weight: 500;
  cursor: text;
}
</style>
