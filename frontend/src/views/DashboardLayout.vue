<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { RouterView, useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useMenuStore } from '@/stores/menu';
import { logout } from '@/services/authService';
import { ElMessage, ElMessageBox } from 'element-plus';
import Breadcrumb from '@/components/Breadcrumb.vue';
import TagsView from '@/components/TagsView.vue';
import { ADMIN_HOME_PATH, ADMIN_LOGIN_PATH, toAdminPath } from '@/config/adminRoute';
import { getThemeMode, setThemeMode, type ThemeMode } from '@/utils/theme';

const userStore = useUserStore();
const menuStore = useMenuStore();
const router = useRouter();
const route = useRoute();

// 主题模式
const themeMode = getThemeMode();
const themeIcon = computed(() => {
  if (themeMode.value === 'auto') return 'Monitor';
  return themeMode.value === 'dark' ? 'Moon' : 'Sunny';
});

const handleThemeChange = (mode: ThemeMode) => {
  setThemeMode(mode);
};

// 侧边栏状态
const isCollapse = ref(false);
const device = ref<'desktop' | 'mobile'>('desktop');
const mobileMenuOpen = ref(false);

// 切换侧边栏折叠状态（桌面） / 打开抽屉（移动）
const toggleSideBar = () => {
  if (device.value === 'mobile') {
    mobileMenuOpen.value = !mobileMenuOpen.value;
  } else {
    isCollapse.value = !isCollapse.value;
  }
};

// 关闭移动端抽屉
const closeMobileMenu = () => {
  mobileMenuOpen.value = false;
};

// 判断当前路由是否活跃
const isRouteActive = (path: string) => {
  return route.path === path;
};

// 处理退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出系统吗？', '退出确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--primary'
    });

    await userStore.logout();
    menuStore.resetState();
    logout();
    ElMessage.success('退出成功');
    router.push(ADMIN_LOGIN_PATH);
  } catch (error) {
    // 用户取消或退出失败
    console.error('退出登录失败:', error);
  }
};

// 创建菜单项接口
interface MenuItem {
  id: number;
  name: string;
  path: string;
  icon: string;
  children?: Array<{
    id: number;
    menu_name: string;
    menu_path: string;
    menu_code: string;
    children?: any[];
  }>;
}

// 计算属性：动态菜单
const navItems = computed<MenuItem[]>(() => {
  const dynamicMenus = menuStore.menuTree.filter(menu => !menu.parent_id).map(menu => ({
    id: menu.id,
    name: menu.menu_name,
    path: toAdminPath(menu.menu_path),
    icon: getIconByMenuCode(menu.menu_code),
    children: (menu.children || []).map(child => ({
      ...child,
      menu_path: toAdminPath(child.menu_path)
    }))
  }));

  return dynamicMenus;
});

// 默认展开所有父级菜单（仅含子菜单的顶级菜单）
const defaultOpenMenus = computed(() =>
  navItems.value.filter(item => item.children && item.children.length > 0).map(item => item.path)
);

// 根据菜单代码获取对应图标
function getIconByMenuCode(menuCode: string): string {
  const iconMap: Record<string, string> = {
    dashboard: 'HomeFilled',
    user: 'User',
    role: 'UserFilled',
    permission: 'Lock',
    menu: 'Menu',
    profile: 'User',
    setting: 'Setting',
    rate_limit: 'Lightning',
    whitelist: 'CircleCheck',
    blacklist: 'CircleClose',
    api_docs: 'Document',
    swagger: 'Document'
  };

  // 从menuCode中提取相关部分作为图标查询键
  const key = menuCode.toLowerCase().split('_')[0];
  return iconMap[key] || 'Setting';
}

// 当前用户名首字母
const avatarText = computed(() => {
  const name = userStore.userInfo?.user_name || '';
  return name ? name.charAt(0).toUpperCase() : '?';
});

// 响应式布局处理
const handleResize = () => {
  const width = document.body.getBoundingClientRect().width;
  if (width <= 992) {
    device.value = 'mobile';
    mobileMenuOpen.value = false;
  } else {
    device.value = 'desktop';
    mobileMenuOpen.value = false;
  }
};

// 移动设备上点击菜单后关闭抽屉
const handleClickMenuItem = () => {
  if (device.value === 'mobile') {
    mobileMenuOpen.value = false;
  }
};

// 加载用户信息和菜单数据
onMounted(async () => {
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo();
  }

  // 加载菜单数据并生成路由
  if (!menuStore.hasMenus) {
    await menuStore.fetchMenuTree();
    await menuStore.fetchMenus();
    menuStore.addRoutes();
  }

  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize);
  handleResize(); // 初始化时执行一次
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});

// 监听路由变化，高亮当前菜单
watch(
  () => route.path,
  () => {
    if (device.value === 'mobile') {
      mobileMenuOpen.value = false;
    }
  }
);
</script>

<template>
  <div class="app-wrapper" :class="{ 'is-mobile': device === 'mobile' }">
    <!-- 移动端遮罩 -->
    <transition name="fade">
      <div v-if="device === 'mobile' && mobileMenuOpen" class="sidebar-mask" @click="closeMobileMenu"></div>
    </transition>

    <!-- 侧边栏 -->
    <aside
      class="sidebar-container"
      :class="{
        'is-collapse': isCollapse && device === 'desktop',
        'mobile-open': device === 'mobile' && mobileMenuOpen
      }"
    >
      <div class="logo-container">
        <router-link :to="ADMIN_HOME_PATH" class="logo-link" @click="handleClickMenuItem">
          <span class="logo-mark">
            <el-icon><HomeFilled /></el-icon>
          </span>
          <transition name="fade">
            <span v-if="!(isCollapse && device === 'desktop')" class="logo-title">管理系统</span>
          </transition>
        </router-link>
      </div>

      <el-scrollbar class="sidebar-scrollbar">
        <el-menu
          v-if="menuStore.hasMenus"
          :default-active="route.path"
          :default-openeds="defaultOpenMenus"
          :collapse="isCollapse && device === 'desktop'"
          :unique-opened="true"
          class="sidebar-menu"
          router
        >
          <template v-for="item in navItems" :key="item.id">
            <!-- 无子菜单的菜单项 -->
            <el-menu-item
              v-if="!item.children || item.children.length === 0"
              :index="item.path"
              @click="handleClickMenuItem"
            >
              <el-icon><component :is="item.icon" /></el-icon>
              <template #title>{{ item.name }}</template>
            </el-menu-item>

            <!-- 有子菜单的菜单项 -->
            <el-sub-menu v-else :index="item.path">
              <template #title>
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.name }}</span>
              </template>

              <el-menu-item
                v-for="child in item.children"
                :key="child.id"
                :index="child.menu_path"
                @click="handleClickMenuItem"
              >
                <template #title>{{ child.menu_name }}</template>
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </el-scrollbar>
    </aside>

    <!-- 主内容区 -->
    <div
      class="main-container"
      :class="{
        'is-collapse': isCollapse && device === 'desktop'
      }"
    >
      <!-- 头部导航 -->
      <header class="app-header">
        <div class="header-left">
          <div class="hamburger-container" @click="toggleSideBar">
            <el-icon :size="20" :class="{ 'is-active': !isCollapse && device === 'desktop' }">
              <Expand v-if="device === 'mobile' || isCollapse" />
              <Fold v-else />
            </el-icon>
          </div>
          <Breadcrumb class="breadcrumb-container" />
        </div>

        <div class="header-right">
          <!-- 主题切换 -->
          <el-dropdown trigger="click" @command="handleThemeChange">
            <div class="theme-toggle" title="主题切换">
              <el-icon :size="17"><component :is="themeIcon" /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="auto" :class="{ 'theme-option-active': themeMode === 'auto' }">
                  <el-icon><Monitor /></el-icon>
                  跟随系统
                </el-dropdown-item>
                <el-dropdown-item command="light" :class="{ 'theme-option-active': themeMode === 'light' }">
                  <el-icon><Sunny /></el-icon>
                  浅色模式
                </el-dropdown-item>
                <el-dropdown-item command="dark" :class="{ 'theme-option-active': themeMode === 'dark' }">
                  <el-icon><Moon /></el-icon>
                  深色模式
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>

          <el-dropdown trigger="click">
            <div class="avatar-container">
              <div class="avatar-wrapper">
                <el-avatar :size="32" class="user-avatar" :src="userStore.userInfo?.avatar || ''">
                  {{ avatarText }}
                </el-avatar>
                <span class="user-name">{{ userStore.userInfo?.user_name || '加载中...' }}</span>
                <el-icon class="caret-icon"><CaretBottom /></el-icon>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <router-link :to="toAdminPath('/dashboard/profile')">
                    <el-icon><User /></el-icon>
                    个人信息
                  </router-link>
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 标签视图 -->
      <TagsView />

      <!-- 主要内容区域 -->
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-wrapper {
  position: relative;
  height: 100%;
  width: 100%;
  background: var(--app-bg);
}

/* ===== 侧边栏 ===== */
.sidebar-container {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 1001;
  display: flex;
  flex-direction: column;
  width: var(--app-sidebar-width);
  background: var(--app-sidebar-bg);
  border-right: 1px solid var(--app-sidebar-border);
  box-shadow: 2px 0 12px rgba(15, 23, 42, 0.08);
  transition:
    width 0.28s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.sidebar-container.is-collapse {
  width: var(--app-sidebar-collapsed-width);
}

/* 移动端抽屉 */
.app-wrapper.is-mobile .sidebar-container {
  transform: translateX(-100%);
  box-shadow: none;
}

.app-wrapper.is-mobile .sidebar-container.mobile-open {
  transform: translateX(0);
  box-shadow: 6px 0 24px rgba(15, 23, 42, 0.18);
}

.sidebar-mask {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
}

/* Logo */
.logo-container {
  flex-shrink: 0;
  height: var(--app-header-height);
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid var(--app-sidebar-border);
  background: var(--app-fill-1);
  overflow: hidden;
}

.logo-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 100%;
  width: 100%;
  text-decoration: none;
  white-space: nowrap;
}

.logo-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  flex-shrink: 0;
  border-radius: 9px;
  background: var(--brand-gradient);
  color: #fff;
  font-size: 16px;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
}

.logo-title {
  color: var(--app-sidebar-logo-text);
  font-weight: 700;
  font-size: 17px;
  letter-spacing: 0.03em;
}

/* 菜单 */
.sidebar-scrollbar {
  flex: 1;
  min-height: 0;
}

.sidebar-menu {
  border-right: none;
  background: transparent;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  height: 46px;
  line-height: 46px;
  margin: 4px 10px;
  border-radius: 10px;
  color: var(--app-sidebar-text);
  font-size: 14px;
  transition: all 0.2s ease;
}

.sidebar-menu :deep(.el-menu-item .el-icon),
.sidebar-menu :deep(.el-sub-menu__title .el-icon) {
  color: inherit;
  font-size: 17px;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background: var(--app-sidebar-hover-bg);
  color: var(--app-sidebar-text-hover);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: var(--app-sidebar-active-bg);
  color: var(--app-sidebar-active-text);
  font-weight: 600;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);
}

.sidebar-menu :deep(.el-menu--collapse .el-menu-item),
.sidebar-menu :deep(.el-menu--collapse .el-sub-menu__title) {
  margin: 4px 8px;
  justify-content: center;
  padding: 0 !important;
}

.sidebar-menu :deep(.el-menu-item.is-active .el-icon) {
  color: var(--app-sidebar-active-text);
}

/* 子菜单浮层 */
.sidebar-menu :deep(.el-menu--popup) {
  background: var(--app-sidebar-popup-bg);
  border: 1px solid var(--app-sidebar-popup-border);
  border-radius: 10px;
  padding: 4px;
  min-width: 160px;
}

.sidebar-menu :deep(.el-menu--popup .el-menu-item) {
  color: var(--app-sidebar-popup-text);
  border-radius: 8px;
  margin: 2px 0;
}

.sidebar-menu :deep(.el-menu--popup .el-menu-item:hover),
.sidebar-menu :deep(.el-menu--popup .el-menu-item.is-active) {
  background: var(--app-sidebar-active-bg);
  color: var(--app-sidebar-active-text);
}

/* ===== 主内容区 ===== */
.main-container {
  min-height: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin-left: var(--app-sidebar-width);
  transition: margin-left 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-container.is-collapse {
  margin-left: var(--app-sidebar-collapsed-width);
}

.app-wrapper.is-mobile .main-container {
  margin-left: 0;
}

/* 头部 */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: var(--app-header-height);
  flex-shrink: 0;
  background: var(--app-header-bg);
  border-bottom: 1px solid var(--app-border);
  box-shadow: var(--app-header-shadow);
  padding: 0 16px 0 0;
  position: relative;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  min-width: 0;
}

.hamburger-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: var(--app-header-height);
  cursor: pointer;
  color: var(--el-text-color-regular);
  transition:
    background 0.2s,
    color 0.2s;
}

.hamburger-container:hover {
  background: var(--app-fill-1);
  color: var(--brand-primary);
}

.hamburger-container .is-active {
  transform: rotate(180deg);
}

.breadcrumb-container {
  margin-left: 6px;
  min-width: 0;
  overflow: hidden;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  color: var(--el-text-color-regular);
  cursor: pointer;
  transition:
    background 0.2s,
    color 0.2s;
}

.theme-toggle:hover {
  background: var(--app-fill-1);
  color: var(--brand-primary);
}

.avatar-container {
  cursor: pointer;
  outline: none;
}

.avatar-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 20px;
  transition: background 0.2s;
}

.avatar-wrapper:hover {
  background: var(--app-fill-1);
}

.user-avatar {
  background: var(--brand-gradient);
  font-weight: 600;
  flex-shrink: 0;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-regular);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.caret-icon {
  color: var(--el-text-color-placeholder);
  font-size: 12px;
}

/* 主内容 */
.app-main {
  flex: 1;
  min-height: 0;
  padding: 20px;
  overflow: auto;
  background: var(--app-bg);
}

@media (max-width: 768px) {
  .app-main {
    padding: 14px;
  }

  .user-name,
  .caret-icon {
    display: none;
  }
}
</style>
