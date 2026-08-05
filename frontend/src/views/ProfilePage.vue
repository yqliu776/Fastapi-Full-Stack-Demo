<script setup lang="ts">
import { useUserStore } from '@/stores/user';
import { onMounted, computed } from 'vue';

const userStore = useUserStore();

onMounted(async () => {
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo();
  }
});

const profileItems = computed(() => {
  const info = userStore.userInfo;
  if (!info) return [];

  return [
    { label: '用户名', value: info.user_name, icon: 'User' },
    { label: '用户ID', value: String(info.id), icon: 'Postcard' },
    { label: '电子邮箱', value: info.email, icon: 'Message' },
    { label: '电话号码', value: info.phone_number || '-', icon: 'Iphone' },
    {
      label: '创建时间',
      value: new Date(info.creation_date).toLocaleString(),
      icon: 'Calendar'
    },
    {
      label: '最后更新时间',
      value: new Date(info.last_update_date).toLocaleString(),
      icon: 'Refresh'
    }
  ];
});
</script>

<template>
  <div class="profile-page">
    <div class="page-heading">
      <h1 class="page-heading__title">
        <span class="page-heading__icon"><el-icon><User /></el-icon></span>
        个人信息
      </h1>
    </div>

    <div v-if="userStore.loading" class="page-card loading-card">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else-if="userStore.userInfo" class="profile-grid">
      <!-- 用户卡片 -->
      <div class="page-card user-card">
        <div class="user-card__top">
          <el-avatar :size="72" :src="userStore.userInfo.avatar || ''">
            {{ userStore.userInfo.user_name.charAt(0).toUpperCase() }}
          </el-avatar>
          <h2>{{ userStore.userInfo.user_name }}</h2>
          <p>{{ userStore.userInfo.email }}</p>
        </div>
        <div class="user-card__roles">
          <span class="role-label">我的角色</span>
          <div class="role-tags">
            <el-tag
              v-for="(role, index) in userStore.userInfo.roles || []"
              :key="index"
              effect="light"
              round
            >
              {{ role.role_name }}（{{ role.role_code }}）
            </el-tag>
            <el-tag v-if="!userStore.userInfo.roles || userStore.userInfo.roles.length === 0" type="info" round>
              暂无角色
            </el-tag>
          </div>
        </div>
      </div>

      <!-- 资料详情 -->
      <div class="page-card">
        <div class="page-card__header">
          <el-icon><Tickets /></el-icon>
          账号资料
        </div>
        <div class="page-card__body profile-detail">
          <el-descriptions :column="1" border>
            <el-descriptions-item v-for="item in profileItems" :key="item.label" :label="item.label">
              <div class="detail-value">
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.value }}</span>
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </div>

    <div v-else-if="userStore.error" class="page-card">
      <div class="page-card__body">
        <el-result icon="error" title="加载用户信息失败" :sub-title="userStore.error">
          <template #extra>
            <el-button type="primary" @click="userStore.fetchUserInfo()">重新加载</el-button>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 18px;
  align-items: start;
}

@media (max-width: 992px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

.loading-card {
  padding: 20px;
}

.user-card__top {
  padding: 28px 20px 20px;
  text-align: center;
  border-bottom: 1px solid var(--app-border);
}

.user-card__top :deep(.el-avatar) {
  background: var(--brand-gradient);
  font-size: 28px;
  font-weight: 700;
  box-shadow: 0 10px 24px rgba(79, 70, 229, 0.3);
  margin-bottom: 12px;
}

.user-card__top h2 {
  margin: 0 0 6px;
  font-size: 18px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.user-card__top p {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.user-card__roles {
  padding: 18px 20px;
}

.role-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-regular);
  margin-bottom: 10px;
}

.role-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-value {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-primary);
}

.detail-value .el-icon {
  color: var(--brand-primary);
}
</style>
