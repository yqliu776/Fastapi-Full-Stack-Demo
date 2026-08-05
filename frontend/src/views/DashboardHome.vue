<script setup lang="ts">
import { computed } from 'vue';
import { useUserStore } from '@/stores/user';
import { toAdminPath } from '@/config/adminRoute';

const userStore = useUserStore();

const welcomeText = computed(() => {
  const hour = new Date().getHours();
  if (hour < 6) return '夜深了';
  if (hour < 12) return '早上好';
  if (hour < 14) return '中午好';
  if (hour < 18) return '下午好';
  return '晚上好';
});

const roleNames = computed(() => {
  const roles = userStore.userInfo?.roles;
  if (!roles || roles.length === 0) return [];
  return roles.map(role => role.role_name);
});

const statCards = computed(() => [
  {
    title: '用户角色',
    value: roleNames.value.length ? roleNames.value.length + ' 个' : '暂无',
    sub: roleNames.value.join('、') || '尚未分配角色',
    icon: 'UserFilled',
    gradient: 'linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)'
  },
  {
    title: '账号邮箱',
    value: userStore.userInfo?.email || '-',
    sub: '账号 ID: ' + (userStore.userInfo?.id ?? '-'),
    icon: 'Message',
    gradient: 'linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)'
  },
  {
    title: '联系电话',
    value: userStore.userInfo?.phone_number || '-',
    sub: '创建于 ' + (userStore.userInfo?.creation_date ? new Date(userStore.userInfo.creation_date).toLocaleDateString() : '-'),
    icon: 'Iphone',
    gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
  }
]);
</script>

<template>
  <div class="dashboard-home">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <div class="welcome-avatar">
          <el-avatar :size="56" :src="userStore.userInfo?.avatar || ''">
            {{ (userStore.userInfo?.user_name || '?').charAt(0).toUpperCase() }}
          </el-avatar>
        </div>
        <div>
          <h1 class="welcome-title">
            {{ welcomeText }}，{{ userStore.userInfo?.user_name || '用户' }}
          </h1>
          <p class="welcome-sub">
            欢迎使用管理系统 · 登录时间 {{ new Date().toLocaleString() }}
          </p>
        </div>
      </div>
      <div class="banner-deco"></div>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div v-for="card in statCards" :key="card.title" class="stat-card">
        <div class="stat-icon" :style="{ background: card.gradient }">
          <el-icon :size="22"><component :is="card.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-label">{{ card.title }}</span>
          <span class="stat-value">{{ card.value }}</span>
          <span class="stat-sub">{{ card.sub }}</span>
        </div>
      </div>
    </div>

    <div class="home-grid">
      <!-- 快速导航 -->
      <div class="page-card">
        <div class="page-card__header">
          <el-icon><Compass /></el-icon>
          快速导航
        </div>
        <div class="page-card__body quick-nav">
          <router-link :to="toAdminPath('/dashboard/profile')" class="nav-item">
            <el-icon :size="20"><User /></el-icon>
            <div>
              <span class="nav-title">个人信息</span>
              <span class="nav-desc">查看与维护我的账号资料</span>
            </div>
            <el-icon class="nav-arrow"><ArrowRight /></el-icon>
          </router-link>
          <router-link :to="toAdminPath('/dashboard/settings')" class="nav-item">
            <el-icon :size="20"><Setting /></el-icon>
            <div>
              <span class="nav-title">系统设置</span>
              <span class="nav-desc">管理个人偏好与账号选项</span>
            </div>
            <el-icon class="nav-arrow"><ArrowRight /></el-icon>
          </router-link>
        </div>
      </div>

      <!-- 系统通知 -->
      <div class="page-card">
        <div class="page-card__header">
          <el-icon><Bell /></el-icon>
          系统通知
        </div>
        <div class="page-card__body notice-body">
          <div class="notice-item">
            <div class="notice-dot notice-dot-primary"></div>
            <div>
              <p class="notice-text">欢迎使用 Fast Full Stack Demo 管理系统</p>
              <p class="notice-time">这是一个示例仪表盘页面，您可以根据实际需求自定义内容。</p>
            </div>
          </div>
          <div class="notice-item">
            <div class="notice-dot notice-dot-success"></div>
            <div>
              <p class="notice-text">系统运行正常</p>
              <p class="notice-time">所有核心服务状态健康，限流与权限模块已就绪。</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-home {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 欢迎横幅 */
.welcome-banner {
  position: relative;
  overflow: hidden;
  border-radius: 16px;
  background: linear-gradient(120deg, #1e1b4b 0%, #312e81 60%, #4338ca 100%);
  padding: 26px 30px;
  color: #fff;
  box-shadow: 0 10px 30px rgba(49, 46, 129, 0.3);
}

.welcome-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 18px;
}

.welcome-avatar :deep(.el-avatar) {
  background: rgba(255, 255, 255, 0.18);
  border: 2px solid rgba(255, 255, 255, 0.35);
  font-size: 22px;
  font-weight: 600;
}

.welcome-title {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 700;
}

.welcome-sub {
  margin: 0;
  font-size: 13px;
  color: rgba(226, 232, 240, 0.8);
}

.banner-deco {
  position: absolute;
  right: -40px;
  top: -70px;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.14), transparent 70%);
}

/* 统计卡片 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

@media (max-width: 992px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--app-card-bg);
  border: 1px solid var(--app-border);
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
  transition:
    transform 0.2s,
    box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.12);
}

.stat-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stat-sub {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 下方网格 */
.home-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}

@media (max-width: 992px) {
  .home-grid {
    grid-template-columns: 1fr;
  }
}

.quick-nav {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  color: var(--el-text-color-regular);
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item > .el-icon:first-child {
  color: var(--brand-primary);
  background: var(--brand-primary-light);
  border-radius: 10px;
  width: 40px;
  height: 40px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-item:hover {
  border-color: var(--el-color-primary-light-5);
  background: var(--brand-primary-light);
  transform: translateX(3px);
}

.nav-item:hover .nav-arrow {
  color: var(--brand-primary);
}

.nav-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.nav-desc {
  display: block;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 2px;
}

.nav-arrow {
  margin-left: auto;
  color: #c0c8d1;
  transition: color 0.2s;
}

.notice-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.notice-item {
  display: flex;
  gap: 12px;
}

.notice-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 7px;
  flex-shrink: 0;
}

.notice-dot-primary {
  background: var(--brand-primary);
  box-shadow: 0 0 0 4px var(--brand-primary-light);
}

.notice-dot-success {
  background: var(--el-color-success);
  box-shadow: 0 0 0 4px var(--el-color-success-light-9);
}

.notice-text {
  margin: 0 0 4px;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.notice-time {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}
</style>
