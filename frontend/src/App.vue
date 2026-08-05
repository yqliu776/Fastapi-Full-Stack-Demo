<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* 全局基础样式 */
html,
body {
  height: 100%;
  margin: 0;
  padding: 0;
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
}

/* 修复Element Plus图标在按钮中的对齐问题 */
.el-button [class*='el-icon'] + span {
  margin-left: 6px;
}

/* 链接样式 */
a {
  color: var(--el-color-primary);
  text-decoration: none;
}

/* 路由链接保持继承颜色 */
.router-link-active,
.router-link-exact-active {
  color: inherit;
}

/* 下拉菜单中的链接 */
.el-dropdown-menu__item a {
  display: block;
  width: 100%;
  color: inherit;
}

/* 主题切换菜单激活项 */
.theme-option-active {
  color: var(--brand-primary) !important;
  font-weight: 600;
}
</style>
