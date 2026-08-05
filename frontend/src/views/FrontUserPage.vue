<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessageBox } from 'element-plus';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const userStore = useUserStore();

onMounted(async () => {
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo();
  }
});

const userInitial = computed(() => {
  return (userStore.userInfo?.user_name || '?').charAt(0).toUpperCase();
});

const roleNames = computed(() => {
  const roles = userStore.userInfo?.roles || [];
  return roles.length ? roles.map(role => role.role_name).join('、') : '普通用户';
});

const profileItems = computed(() => {
  const info = userStore.userInfo;
  if (!info) return [];

  return [
    { label: '用户名', value: info.user_name, icon: 'User' },
    { label: '邮箱', value: info.email || '-', icon: 'Message' },
    { label: '手机号', value: info.phone_number || '-', icon: 'Iphone' },
    { label: '账号角色', value: roleNames.value, icon: 'Medal' },
    {
      label: '注册时间',
      value: info.creation_date ? new Date(info.creation_date).toLocaleString() : '-',
      icon: 'Calendar'
    }
  ];
});

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出当前账号吗？', '退出确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    });
    userStore.logout('/');
  } catch {
    // 用户取消退出
  }
}
</script>

<template>
  <main class="front-user-page">
    <header class="topbar">
      <router-link to="/" class="brand-link">
        <span class="brand-mark">
          <el-icon><Lightning /></el-icon>
        </span>
        <span>Fast Full Stack Demo</span>
      </router-link>

      <div class="topbar-actions">
        <el-button text @click="router.push('/')">首页</el-button>
        <el-button type="primary" plain @click="handleLogout">
          <el-icon><SwitchButton /></el-icon>
          退出
        </el-button>
      </div>
    </header>

    <section class="user-hero">
      <div v-if="userStore.loading" class="content-panel">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else-if="userStore.userInfo" class="user-layout">
        <aside class="profile-panel">
          <el-avatar :size="76" class="profile-avatar">
            {{ userInitial }}
          </el-avatar>
          <h1>{{ userStore.userInfo.user_name }}</h1>
          <p>{{ userStore.userInfo.email || '未设置邮箱' }}</p>
          <div class="role-list">
            <el-tag
              v-for="role in userStore.userInfo.roles || []"
              :key="role.role_code"
              effect="light"
              round
            >
              {{ role.role_name }}
            </el-tag>
            <el-tag v-if="!userStore.userInfo.roles || userStore.userInfo.roles.length === 0" type="info" round>
              普通用户
            </el-tag>
          </div>
        </aside>

        <section class="content-panel">
          <div class="panel-heading">
            <div>
              <h2>用户中心</h2>
              <p>查看当前前台业务账号的基础资料</p>
            </div>
            <el-button type="primary" @click="router.push('/')">
              返回首页
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>

          <div class="profile-list">
            <div v-for="item in profileItems" :key="item.label" class="profile-row">
              <span class="row-label">
                <el-icon><component :is="item.icon" /></el-icon>
                {{ item.label }}
              </span>
              <span class="row-value">{{ item.value }}</span>
            </div>
          </div>
        </section>
      </div>

      <div v-else-if="userStore.error" class="content-panel">
        <el-result icon="error" title="加载用户信息失败" :sub-title="userStore.error">
          <template #extra>
            <el-button type="primary" @click="userStore.fetchUserInfo()">重新加载</el-button>
          </template>
        </el-result>
      </div>
    </section>
  </main>
</template>

<style scoped>
.front-user-page {
  min-height: 100vh;
  background:
    radial-gradient(900px 500px at 80% -10%, rgba(99, 102, 241, 0.2), transparent 60%),
    radial-gradient(700px 500px at 0% 110%, rgba(124, 58, 237, 0.16), transparent 55%),
    var(--app-bg);
  padding: 28px 24px 44px;
}

.topbar {
  width: min(1080px, 100%);
  margin: 0 auto 34px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--app-text-strong);
  font-weight: 700;
  text-decoration: none;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  color: #fff;
  background: var(--brand-gradient);
  box-shadow: 0 8px 20px rgba(79, 70, 229, 0.25);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-hero {
  width: min(1080px, 100%);
  margin: 0 auto;
}

.user-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 18px;
  align-items: start;
}

.profile-panel,
.content-panel {
  background: var(--app-card-bg);
  border: 1px solid var(--app-border);
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.profile-panel {
  padding: 30px 24px;
  text-align: center;
}

.profile-avatar {
  background: var(--brand-gradient);
  font-size: 28px;
  font-weight: 700;
  box-shadow: 0 10px 24px rgba(79, 70, 229, 0.28);
  margin-bottom: 14px;
}

.profile-panel h1 {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.profile-panel p {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.role-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 18px;
}

.content-panel {
  padding: 26px;
}

.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.panel-heading h2 {
  margin: 0 0 4px;
  font-size: 22px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.panel-heading p {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.profile-list {
  display: grid;
  gap: 12px;
}

.profile-row {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 16px;
  align-items: center;
  padding: 14px 16px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: var(--app-fill-1);
}

.row-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
}

.row-label .el-icon {
  color: var(--brand-primary);
}

.row-value {
  min-width: 0;
  font-size: 14px;
  color: var(--el-text-color-primary);
  word-break: break-word;
}

@media (max-width: 768px) {
  .front-user-page {
    padding: 22px 16px 32px;
  }

  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .user-layout {
    grid-template-columns: 1fr;
  }

  .panel-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .profile-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
</style>
