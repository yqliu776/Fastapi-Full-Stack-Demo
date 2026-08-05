<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { roleService } from '@/services/roleService';
import type { Role } from '@/services/roleService';
import { userService } from '@/services/userService';
import type { User } from '@/services/userService';
import { useUserStore } from '@/stores/user';
import type { PropType } from 'vue';

const userStore = useUserStore();

// 属性定义
const props = defineProps({
  userId: {
    type: Number,
    required: false,
    default: 0
  },
  username: {
    type: String,
    required: false,
    default: ''
  },
  mode: {
    type: String,
    required: true,
    validator: (value: string) => ['create', 'edit'].includes(value),
    default: 'create'
  },
  initialRoles: {
    type: Array as PropType<string[]>,
    default: () => []
  }
});

// 事件定义
const emit = defineEmits(['update', 'roleChange']);

// 状态
const allRoles = ref<Role[]>([]);
const userRoles = ref<number[]>([]);
const initialUserRoles = ref<number[]>([]);
const initialRoleCodes = ref<string[]>([]);
const searchKeyword = ref('');
const loading = ref({
  roles: false,
  userRoles: false,
  saving: false
});

// 过滤角色列表
const filteredRoles = computed(() => {
  const keyword = searchKeyword.value.toLowerCase().trim();
  if (!keyword) return allRoles.value;

  return allRoles.value.filter(role =>
    role.role_name.toLowerCase().includes(keyword) ||
    role.role_code.toLowerCase().includes(keyword)
  );
});

// 角色状态统计
const roleStats = computed(() => {
  const total = allRoles.value.length;
  const assigned = initialUserRoles.value.length;
  const selected = userRoles.value.length;

  const toAssign = userRoles.value.filter(id => !initialUserRoles.value.includes(id)).length;
  const toRemove = initialUserRoles.value.filter(id => !userRoles.value.includes(id)).length;

  return { total, assigned, selected, toAssign, toRemove };
});

// 加载所有角色
const loadAllRoles = async () => {
  loading.value.roles = true;
  try {
    const response = await roleService.getRoles({ limit: 500 });
    if (response.code === 200) {
      allRoles.value = response.data.items;
      matchUserRolesByCode();
    } else {
      ElMessage.error('加载角色列表失败: ' + response.message);
    }
  } catch (error) {
    console.error('加载角色列表出错:', error);
    ElMessage.error('加载角色列表出错');
  } finally {
    loading.value.roles = false;
  }
};

// 加载用户已有角色
const loadUserRoles = async () => {
  if (!props.userId) return;

  loading.value.userRoles = true;
  try {
    const response = await userService.getUser(props.userId);
    if (response.code === 200) {
      const userData = response.data as User;
      if (userData.roles && Array.isArray(userData.roles)) {
        initialRoleCodes.value = userData.roles.map(role => role.role_code);
      } else {
        initialRoleCodes.value = [];
      }
    } else {
      ElMessage.error('加载用户角色失败: ' + response.message);
    }
  } catch (error) {
    console.error('加载用户角色出错:', error);
    ElMessage.error('加载用户角色出错');
  } finally {
    loading.value.userRoles = false;
  }
};

// 根据角色代码匹配角色ID
const matchUserRolesByCode = () => {
  if (allRoles.value.length === 0) {
    return;
  }

  let roleCodeSource: string[] = [];

  if (props.mode === 'create') {
    roleCodeSource = props.initialRoles || [];
  } else {
    roleCodeSource = initialRoleCodes.value;
  }

  if (roleCodeSource.length === 0) {
    initialUserRoles.value = [];
    userRoles.value = [];
    return;
  }

  const matchedRoleIds = allRoles.value
    .filter(role => roleCodeSource.includes(role.role_code))
    .map(role => role.id);
  initialUserRoles.value = [...matchedRoleIds];
  userRoles.value = [...matchedRoleIds];
};

// 保存用户角色
const saveUserRoles = async () => {
  if (props.mode === 'create') {
    const selectedRoleCodes = userRoles.value
      .map(roleId => {
        const role = allRoles.value.find(r => r.id === roleId);
        return role ? role.role_code : '';
      })
      .filter(code => code !== '');

    emit('roleChange', selectedRoleCodes);
    ElMessage.success('角色已选择');
    return;
  }

  if (areArraysEqual(userRoles.value, initialUserRoles.value)) {
    ElMessage.info('角色没有变化');
    return;
  }

  loading.value.saving = true;
  try {
    const selectedRoleCodes = userRoles.value
      .map(roleId => {
        const role = allRoles.value.find(r => r.id === roleId);
        return role ? role.role_code : '';
      })
      .filter(code => code !== '');

    const operatorId = userStore.userInfo?.id.toString() || '-1';

    const roleData = {
      role_codes: selectedRoleCodes,
      operator: operatorId,
      operation_login: operatorId
    };

    const response = await userService.assignRolesToUser(props.userId, roleData);

    if (response.code === 200) {
      ElMessage.success('保存用户角色成功');
      initialUserRoles.value = [...userRoles.value];
      initialRoleCodes.value = [...selectedRoleCodes];
      emit('update');
    } else {
      ElMessage.error('保存用户角色失败: ' + response.message);
    }
  } catch (error) {
    console.error('保存用户角色出错:', error);
    ElMessage.error('保存用户角色出错');
  } finally {
    loading.value.saving = false;
  }
};

// 比较两个数组是否相等
const areArraysEqual = (arr1: number[], arr2: number[]) => {
  if (arr1.length !== arr2.length) return false;
  const set1 = new Set(arr1);
  return arr2.every(id => set1.has(id));
};

// 处理复选框变更
const handleCheckboxChange = (event: Event, roleId: number) => {
  const target = event.target as HTMLInputElement;
  if (target && target.checked) {
    if (!userRoles.value.includes(roleId)) {
      userRoles.value.push(roleId);
    }
  } else {
    userRoles.value = userRoles.value.filter(id => id !== roleId);
  }
};

// 检查角色是否在初始分配列表中
const hasRoleInitially = (roleId: number): boolean => {
  return initialUserRoles.value.includes(roleId);
};

// 检查角色是否当前选中
const isRoleSelected = (roleId: number): boolean => {
  return userRoles.value.includes(roleId);
};

// 全选
const selectAll = () => {
  userRoles.value = allRoles.value.map(role => role.id);
};

// 全不选
const deselectAll = () => {
  userRoles.value = [];
};

// 切换角色选中状态
const toggleRole = (roleId: number) => {
  if (isRoleSelected(roleId)) {
    userRoles.value = userRoles.value.filter(id => id !== roleId);
  } else {
    userRoles.value.push(roleId);
  }
};

// 初始化
onMounted(async () => {
  await loadAllRoles();
  if (props.mode === 'edit' && props.userId) {
    await loadUserRoles();
    matchUserRolesByCode();
  }
});

// 监听initialRoles变化
watch(
  () => props.initialRoles,
  () => {
    if (props.mode === 'create' && allRoles.value.length > 0) {
      matchUserRolesByCode();
    }
  },
  { deep: true }
);

// 当角色选择改变时触发事件
watch(userRoles, newValue => {
  if (props.mode === 'create') {
    const selectedCodes = allRoles.value
      .filter(role => newValue.includes(role.id))
      .map(role => role.role_code);

    emit('roleChange', selectedCodes);
  }
});
</script>

<template>
  <div class="user-role-selector">
    <div class="selector-title">
      <template v-if="mode === 'create'">选择用户角色</template>
      <template v-else>{{ username || '用户' }} 的角色分配</template>
    </div>

    <!-- 顶部操作栏 -->
    <div class="selector-toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索角色名称或代码"
        clearable
        :prefix-icon="'Search'"
        style="width: 260px"
      />
      <div class="toolbar-actions">
        <el-button size="small" @click="selectAll">全选</el-button>
        <el-button size="small" @click="deselectAll">全不选</el-button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats-bar">
      <div class="stat-chip">
        <span class="stat-dot dot-total"></span>
        总角色数 <strong>{{ roleStats.total }}</strong>
      </div>
      <div class="stat-chip">
        <span class="stat-dot dot-assigned"></span>
        已分配 <strong>{{ roleStats.assigned }}</strong>
      </div>
      <div class="stat-chip">
        <span class="stat-dot dot-selected"></span>
        已选择 <strong>{{ roleStats.selected }}</strong>
      </div>
      <div v-if="roleStats.toAssign > 0" class="stat-chip">
        <span class="stat-dot dot-new"></span>
        待分配 <strong>{{ roleStats.toAssign }}</strong>
      </div>
      <div v-if="roleStats.toRemove > 0" class="stat-chip">
        <span class="stat-dot dot-remove"></span>
        待移除 <strong>{{ roleStats.toRemove }}</strong>
      </div>
    </div>

    <div v-if="loading.roles || loading.userRoles" class="selector-loading">
      <el-icon class="is-loading" :size="28"><Loading /></el-icon>
      <span>加载角色中...</span>
    </div>

    <!-- 角色列表 -->
    <div v-else class="role-list">
      <el-empty v-if="filteredRoles.length === 0" description="暂无匹配的角色" :image-size="80" />
      <div v-else class="role-grid">
        <div
          v-for="role in filteredRoles"
          :key="role.id"
          class="role-card"
          :class="{
            'is-selected-new': isRoleSelected(role.id) && !hasRoleInitially(role.id),
            'is-removing': hasRoleInitially(role.id) && !isRoleSelected(role.id),
            'is-assigned': hasRoleInitially(role.id) && isRoleSelected(role.id)
          }"
          @click="toggleRole(role.id)"
        >
          <el-checkbox
            :model-value="isRoleSelected(role.id)"
            @click.stop
            @change="handleCheckboxChange($event, role.id)"
          />
          <div class="role-card-info">
            <span class="role-card-name">{{ role.role_name }}</span>
            <span class="role-card-code">{{ role.role_code }}</span>
          </div>
          <el-tag
            v-if="hasRoleInitially(role.id)"
            :type="isRoleSelected(role.id) ? 'success' : 'danger'"
            effect="light"
            size="small"
            round
          >
            {{ isRoleSelected(role.id) ? '已分配' : '将被移除' }}
          </el-tag>
          <el-tag v-else-if="isRoleSelected(role.id)" type="primary" effect="light" size="small" round>
            将被分配
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 底部 -->
    <div class="selector-footer">
      <span class="selected-count">已选择 {{ userRoles.length }} 项</span>
      <el-button
        v-if="mode !== 'create'"
        type="primary"
        :loading="loading.saving"
        :disabled="roleStats.toAssign === 0 && roleStats.toRemove === 0"
        @click="saveUserRoles"
      >
        保存更改
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.user-role-selector {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.selector-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.selector-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.stats-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px 14px;
  background: var(--app-fill-1);
  border: 1px solid var(--app-border);
  border-radius: 10px;
}

.stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.stat-chip strong {
  color: var(--el-text-color-primary);
}

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot-total {
  background: #94a3b8;
}

.dot-assigned {
  background: var(--el-color-success);
}

.dot-selected {
  background: var(--el-color-primary);
}

.dot-new {
  background: #8b5cf6;
}

.dot-remove {
  background: var(--el-color-danger);
}

.selector-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.role-list {
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 12px;
  background: var(--app-fill-2);
}

.role-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

@media (max-width: 640px) {
  .role-grid {
    grid-template-columns: 1fr;
  }
}

.role-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: var(--app-card-bg);
  cursor: pointer;
  transition: all 0.2s;
}

.role-card:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
}

.role-card.is-assigned {
  border-color: var(--el-color-success-light-5);
  background: var(--el-color-success-light-9);
}

.role-card.is-selected-new {
  border-color: var(--el-color-primary-light-5);
  background: var(--el-color-primary-light-9);
}

.role-card.is-removing {
  border-color: var(--el-color-danger-light-5);
  background: var(--el-color-danger-light-9);
}

.role-card-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.role-card-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-card-code {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.selector-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.selected-count {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
</style>
