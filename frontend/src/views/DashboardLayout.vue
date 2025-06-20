<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import { RouterView, useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { useMenuStore } from '@/stores/menu';
import { logout } from '@/services/authService';
import { ElMessage, ElMessageBox } from 'element-plus';
import Breadcrumb from '@/components/Breadcrumb.vue';
import TagsView from '@/components/TagsView.vue';

const userStore = useUserStore();
const menuStore = useMenuStore();
const router = useRouter();
const route = useRoute();

// 侧边栏状态
const isCollapse = ref(false);
const device = ref('desktop');
const showDrawer = ref(false);

// 父菜单展开状态
const expandedMenus = ref<Set<number>>(new Set());

// 切换侧边栏折叠状态
const toggleSideBar = () => {
  isCollapse.value = !isCollapse.value;
};

// 切换菜单展开状态
const toggleMenuExpand = (menuId: number) => {
  if (expandedMenus.value.has(menuId)) {
    expandedMenus.value.delete(menuId);
  } else {
    expandedMenus.value.add(menuId);
  }
};

// 判断当前路由是否活跃
const isRouteActive = (path: string) => {
  return route.path === path;
};

// 处理退出登录
const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出系统吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    
    await userStore.logout();
    menuStore.resetState();
    logout();
    ElMessage.success('退出成功');
    router.push('/login');
  } catch (error) {
    console.error('退出登录失败:', error);
  }
};

// 创建菜单项接口
interface MenuItem {
  id: number;
  name: string;
  path: string;
  icon: string;
  action?: () => Promise<void>;
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
    path: menu.menu_path,
    icon: getIconByMenuCode(menu.menu_code),
    children: menu.children || []
  }));
  
  return dynamicMenus;
});

// 根据菜单代码获取对应图标
function getIconByMenuCode(menuCode: string): string {
  const iconMap: Record<string, string> = {
    'dashboard': 'HomeFilled',
    'user': 'User',
    'role': 'UserFilled',
    'permission': 'Lock',
    'menu': 'Menu',
    'profile': 'User',
    'setting': 'Setting'
  };
  
  // 从menuCode中提取相关部分作为图标查询键
  const key = menuCode.toLowerCase().split('_')[0];
  return iconMap[key] || 'Setting'; // 默认返回设置图标
}

// 响应式布局处理
const handleResize = () => {
  const rect = document.body.getBoundingClientRect();
  const width = rect.width;
  
  if (width <= 992) {
    device.value = 'mobile';
    isCollapse.value = true;
  } else {
    device.value = 'desktop';
    isCollapse.value = false;
  }
};

// 移动设备上点击菜单后关闭抽屉
const handleClickMenuItem = () => {
  if (device.value === 'mobile') {
    showDrawer.value = false;
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
    
    // 自动展开包含当前路由的父菜单
    menuStore.menuTree.forEach(menu => {
      if (menu.id && menu.children?.some(child => child.menu_path === route.path)) {
        expandedMenus.value.add(menu.id);
      }
    });
  }
  
  // 添加窗口大小变化监听
  window.addEventListener('resize', handleResize);
  handleResize(); // 初始化时执行一次
});

onUnmounted(() => {
  // 移除事件监听器
  window.removeEventListener('resize', handleResize);
});

// 监听路由变化，高亮当前菜单
watch(
  () => route.path,
  () => {
    if (device.value === 'mobile') {
      showDrawer.value = false;
    }
  }
);
</script>

<template>
  <el-container class="app-wrapper">
    <!-- 侧边栏 -->
    <el-aside 
      :width="isCollapse ? '64px' : '210px'" 
      class="sidebar-container"
      :class="{ 'is-collapse': isCollapse }"
    >
      <div class="logo-container">
        <router-link to="/dashboard" class="logo-link">
          <span v-if="!isCollapse" class="logo-title">管理系统</span>
          <el-icon v-else><HomeFilled /></el-icon>
        </router-link>
      </div>
      
      <el-scrollbar>
        <el-menu
          :default-active="route.path"
          :collapse="isCollapse"
          :unique-opened="true"
          class="el-menu-vertical"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <template v-for="item in navItems" :key="item.id">
            <!-- 无子菜单的菜单项 -->
            <el-menu-item 
              v-if="!item.children || item.children.length === 0" 
              :index="item.path"
              @click="() => router.push(item.path)"
            >
              <el-icon><component :is="item.icon" /></el-icon>
              <template #title>{{ item.name }}</template>
            </el-menu-item>
            
            <!-- 有子菜单的菜单项 -->
            <el-sub-menu 
              v-else 
              :index="item.path"
            >
              <template #title>
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.name }}</span>
              </template>
              
              <el-menu-item 
                v-for="child in item.children" 
                :key="child.id"
                :index="child.menu_path"
                @click="() => router.push(child.menu_path)"
              >
                <template #title>{{ child.menu_name }}</template>
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </el-scrollbar>
    </el-aside>
    
    <el-container class="main-container">
      <!-- 头部导航 -->
      <el-header class="app-header">
        <div class="header-left">
          <div class="hamburger-container" @click="toggleSideBar">
            <el-icon :class="{'is-active': !isCollapse}">
              <Expand v-if="isCollapse" />
              <Fold v-else />
            </el-icon>
          </div>
          <Breadcrumb class="breadcrumb-container" />
        </div>
        
        <div class="header-right">
          <el-dropdown trigger="click">
            <div class="avatar-container">
              <div class="avatar-wrapper">
                <el-avatar 
                  :size="30" 
                  class="user-avatar"
                  :src="userStore.userInfo?.avatar || ''"
                >
                  {{ userStore.userInfo?.user_name.charAt(0).toUpperCase() || '?' }}
                </el-avatar>
                <span class="user-name">{{ userStore.userInfo?.user_name || '加载中...' }}</span>
                <el-icon><CaretBottom /></el-icon>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  <router-link to="/dashboard/profile">
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
      </el-header>
      
      <!-- 标签视图 -->
      <TagsView />
      
      <!-- 主要内容区域 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
/* 全局布局样式 */
.app-wrapper {
  position: relative;
  height: 100%;
  width: 100%;
}

/* 侧边栏样式 */
.sidebar-container {
  transition: width 0.28s;
  height: 100%;
  background-color: #304156;
  overflow: hidden;
}

.sidebar-container.is-collapse {
  width: 64px !important;
}

.logo-container {
  height: 50px;
  line-height: 50px;
  background: #2b2f3a;
  text-align: center;
  overflow: hidden;
}

.logo-link {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
}

.logo-title {
  display: inline-block;
  color: #fff;
  font-weight: 600;
  font-size: 18px;
  font-family: Avenir, Helvetica Neue, Arial, Helvetica, sans-serif;
  vertical-align: middle;
}

.el-menu-vertical:not(.el-menu--collapse) {
  width: 210px;
  min-height: 400px;
}

/* 头部样式 */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 50px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  position: relative;
  padding: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.hamburger-container {
  line-height: 46px;
  height: 100%;
  padding: 0 15px;
  cursor: pointer;
  transition: background 0.3s;
}

.hamburger-container:hover {
  background: rgba(0, 0, 0, 0.025);
}

.hamburger-container .is-active {
  transform: rotate(180deg);
}

.breadcrumb-container {
  margin-left: 8px;
}

.header-right {
  display: flex;
  align-items: center;
  padding-right: 15px;
}

.avatar-container {
  margin-right: 30px;
}

.avatar-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.user-avatar {
  margin-right: 8px;
  background: #409EFF;
}

.user-name {
  margin-right: 5px;
  font-size: 14px;
}

/* 主内容区域样式 */
.main-container {
  min-height: 100%;
  transition: margin-left 0.28s;
  position: relative;
}

.app-main {
  padding: 20px;
  background-color: #f0f2f5;
  position: relative;
  overflow: auto;
  height: calc(100vh - 84px); /* 减去头部和标签视图的高度 */
}

/* 响应式布局 */
@media screen and (max-width: 992px) {
  .app-wrapper {
    position: relative;
  }
  
  .sidebar-container {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1001;
    height: 100%;
    transition: transform 0.28s;
    transform: translate3d(-210px, 0, 0);
  }
  
  .sidebar-container.is-collapse {
    transform: translate3d(0, 0, 0);
  }
}
</style>
