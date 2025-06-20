<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute, useRouter, type RouteLocationMatched } from 'vue-router';
import { ElBreadcrumb, ElBreadcrumbItem } from 'element-plus';

const route = useRoute();
const router = useRouter();

// 自定义面包屑项类型
interface BreadcrumbItem {
  path: string;
  title: string;
}

// 面包屑导航数据
const levelList = ref<BreadcrumbItem[]>([]);

// 生成面包屑导航数据
const getBreadcrumb = () => {
  // 过滤掉没有meta或meta.title的路由
  const matched = route.matched.filter(
    item => item.meta && item.meta.title
  );
  
  // 将RouteLocationMatched转换为简单的BreadcrumbItem
  const breadcrumbs: BreadcrumbItem[] = matched.map(item => ({
    path: item.path,
    title: item.meta?.title as string
  }));
  
  // 如果第一个不是dashboard，添加dashboard作为首页
  if (breadcrumbs.length > 0 && breadcrumbs[0].path !== '/dashboard') {
    breadcrumbs.unshift({
      path: '/dashboard',
      title: '首页'
    });
  }
  
  levelList.value = breadcrumbs;
};

// 点击面包屑导航项
const handleLink = (path: string) => {
  router.push(path);
};

// 初始化和路由变化时更新面包屑
watch(
  () => route.path,
  () => getBreadcrumb(),
  { immediate: true }
);
</script>

<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item 
      v-for="(item, index) in levelList" 
      :key="item.path"
    >
      <span 
        v-if="index === levelList.length - 1" 
        class="no-redirect"
      >
        {{ item.title }}
      </span>
      <a 
        v-else 
        @click.prevent="handleLink(item.path)"
        class="redirect"
      >
        {{ item.title }}
      </a>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<style scoped>
.redirect {
  color: #409EFF;
  font-weight: 600;
  cursor: pointer;
}

.no-redirect {
  color: #97a8be;
  cursor: text;
}
</style> 