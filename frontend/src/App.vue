<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
@import '@/assets/main.css';

/* Element Plus 主题定制 */
:root {
  --el-color-primary: #409EFF;
  --el-color-success: #67C23A;
  --el-color-warning: #E6A23C;
  --el-color-danger: #F56C6C;
  --el-color-info: #909399;
}

/* 全局样式 */
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
  font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB, Microsoft YaHei, Arial, sans-serif;
}

/* 修复Element Plus图标在按钮中的对齐问题 */
.el-button [class*="el-icon"] + span {
  margin-left: 6px;
}

/* 链接样式 */
a {
  color: var(--el-color-primary);
  text-decoration: none;
}

/* 修复路由链接样式 */
.router-link-active,
.router-link-exact-active {
  color: inherit;
}

/* 修复下拉菜单中的链接样式 */
.el-dropdown-menu__item a {
  display: block;
  width: 100%;
  color: inherit;
}
</style>
