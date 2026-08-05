<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { permissionService } from '@/services/permissionService';
import type { Permission } from '@/services/permissionService';
import { roleService } from '@/services/roleService';

// 组件属性
const props = defineProps<{
  roleId: number;
  visible: boolean;
}>();

// 组件事件
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'update'): void;
}>();

// 状态
const allPermissions = ref<Permission[]>([]);
const rolePermissions = ref<Permission[]>([]);
const selectedPermissions = ref<number[]>([]);
const loading = ref({
  allPermissions: false,
  rolePermissions: false,
  submit: false
});
const searchKeyword = ref('');
const errorMsg = ref('');

// 计算属性 - 过滤后的权限列表
const filteredPermissions = computed(() => {
  if (!searchKeyword.value) return allPermissions.value;

  const keyword = searchKeyword.value.toLowerCase();
  return allPermissions.value.filter(
    permission =>
      permission.permission_name.toLowerCase().includes(keyword) ||
      permission.permission_code.toLowerCase().includes(keyword)
  );
});

// 计算属性 - 角色已有权限的ID集合
const rolePermissionIds = computed(() => {
  return rolePermissions.value.map(p => p.id);
});

// 是否已选择权限
const isPermissionSelected = (permissionId: number) => {
  return selectedPermissions.value.includes(permissionId);
};

// 是否角色已有该权限
const hasRolePermission = (permissionId: number) => {
  return rolePermissionIds.value.includes(permissionId);
};

// 权限统计
const permissionStats = computed(() => {
  return {
    total: allPermissions.value.length,
    assigned: rolePermissions.value.length,
    selected: selectedPermissions.value.length,
    toAssign: selectedPermissions.value.filter(id => !rolePermissionIds.value.includes(id)).length,
    toRemove: rolePermissionIds.value.filter(id => !selectedPermissions.value.includes(id)).length
  };
});

// 初始化方法
const init = async () => {
  errorMsg.value = '';
  await Promise.all([loadAllPermissions(), loadRolePermissions()]);
};

// 加载所有权限
const loadAllPermissions = async () => {
  loading.value.allPermissions = true;
  try {
    const response = await permissionService.getPermissions({ limit: 1000 });
    if (response.code === 200) {
      allPermissions.value = response.data.items;
    } else {
      errorMsg.value = '加载权限列表失败: ' + response.message;
    }
  } catch (error) {
    console.error('加载权限列表出错:', error);
    errorMsg.value = '加载权限列表出错';
  } finally {
    loading.value.allPermissions = false;
  }
};

// 加载角色拥有的权限
const loadRolePermissions = async () => {
  if (!props.roleId) return;

  loading.value.rolePermissions = true;
  try {
    const roleResponse = await roleService.getRole(props.roleId);
    if (roleResponse.code === 200 && roleResponse.data.permissions) {
      rolePermissions.value = roleResponse.data.permissions as unknown as Permission[];
      selectedPermissions.value = rolePermissions.value.map(permission => permission.id);
    } else {
      const response = await permissionService.getRolePermissions(props.roleId);
      if (response.code === 200) {
        rolePermissions.value = response.data.items;
        selectedPermissions.value = rolePermissions.value.map(permission => permission.id);
      } else {
        errorMsg.value = '加载角色权限失败: ' + response.message;
      }
    }
  } catch (error) {
    console.error('加载角色权限出错:', error);
    errorMsg.value = '加载角色权限出错';
  } finally {
    loading.value.rolePermissions = false;
  }
};

// 切换选择权限
const toggleSelectPermission = (permissionId: number) => {
  const index = selectedPermissions.value.indexOf(permissionId);
  if (index === -1) {
    selectedPermissions.value.push(permissionId);
  } else {
    selectedPermissions.value.splice(index, 1);
  }
};

// 全选
const selectAll = () => {
  selectedPermissions.value = filteredPermissions.value.map(p => p.id);
};

// 全不选
const deselectAll = () => {
  selectedPermissions.value = [];
};

// 保存角色权限完整集合
const savePermissions = async () => {
  errorMsg.value = '';

  loading.value.submit = true;
  try {
    const response = await roleService.replacePermissionsForRole(props.roleId, {
      permission_ids: selectedPermissions.value
    });
    if (response.code === 200) {
      await loadRolePermissions();
      emit('update');
    } else {
      errorMsg.value = '保存权限失败: ' + response.message;
    }
  } catch (error) {
    console.error('保存权限出错:', error);
    errorMsg.value = '保存权限出错';
  } finally {
    loading.value.submit = false;
  }
};

// 监听visible变化
watch(
  () => props.visible,
  newValue => {
    if (newValue) {
      init();
    } else {
      selectedPermissions.value = [];
    }
  }
);

// 监听roleId变化
watch(
  () => props.roleId,
  () => {
    if (props.visible) {
      loadRolePermissions();
    }
  }
);

// 生命周期钩子
onMounted(() => {
  if (props.visible) {
    init();
  }
});
</script>

<template>
  <div class="role-permission-selector">
    <!-- 顶部操作栏 -->
    <div class="selector-toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索权限名称或代码"
        clearable
        :prefix-icon="'Search'"
        style="width: 260px"
      />
      <div class="toolbar-actions">
        <el-button size="small" @click="selectAll">全选</el-button>
        <el-button size="small" @click="deselectAll">全不选</el-button>
      </div>
    </div>

    <!-- 错误消息 -->
    <el-alert v-if="errorMsg" :title="errorMsg" type="error" show-icon :closable="false" />

    <!-- 统计信息 -->
    <div class="stats-bar">
      <div class="stat-chip">
        <span class="stat-dot dot-total"></span>
        总权限数 <strong>{{ permissionStats.total }}</strong>
      </div>
      <div class="stat-chip">
        <span class="stat-dot dot-assigned"></span>
        已分配 <strong>{{ permissionStats.assigned }}</strong>
      </div>
      <div class="stat-chip">
        <span class="stat-dot dot-selected"></span>
        已选择 <strong>{{ permissionStats.selected }}</strong>
      </div>
      <div v-if="permissionStats.toAssign > 0" class="stat-chip">
        <span class="stat-dot dot-new"></span>
        待分配 <strong>{{ permissionStats.toAssign }}</strong>
      </div>
      <div v-if="permissionStats.toRemove > 0" class="stat-chip">
        <span class="stat-dot dot-remove"></span>
        保存后移除 <strong>{{ permissionStats.toRemove }}</strong>
      </div>
    </div>

    <!-- 权限列表 -->
    <div class="permission-list">
      <div v-if="loading.allPermissions || loading.rolePermissions" class="list-loading">
        <el-icon class="is-loading" :size="26"><Loading /></el-icon>
        <span>加载权限中...</span>
      </div>
      <el-empty v-else-if="filteredPermissions.length === 0" description="暂无数据" :image-size="80" />
      <div v-else class="permission-grid">
        <div
          v-for="permission in filteredPermissions"
          :key="permission.id"
          class="permission-card"
          :class="{
            'is-selected-new': isPermissionSelected(permission.id) && !hasRolePermission(permission.id),
            'is-removing': hasRolePermission(permission.id) && !isPermissionSelected(permission.id),
            'is-assigned': hasRolePermission(permission.id) && isPermissionSelected(permission.id)
          }"
          @click="toggleSelectPermission(permission.id)"
        >
          <el-checkbox
            :model-value="isPermissionSelected(permission.id)"
            @click.stop
            @change="toggleSelectPermission(permission.id)"
          />
          <div class="permission-info">
            <span class="permission-name">{{ permission.permission_name }}</span>
            <span class="permission-code">{{ permission.permission_code }}</span>
          </div>
          <el-tag
            v-if="hasRolePermission(permission.id)"
            type="success"
            effect="light"
            size="small"
            round
          >
            已分配
          </el-tag>
          <el-tag v-else-if="isPermissionSelected(permission.id)" type="primary" effect="light" size="small" round>
            待分配
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 底部按钮 -->
    <div class="selector-footer">
      <span class="selected-count">保存后拥有 {{ selectedPermissions.length }} 项权限</span>
      <el-button type="primary" :loading="loading.submit" @click="savePermissions">
        保存权限
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.role-permission-selector {
  display: flex;
  flex-direction: column;
  gap: 14px;
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

.permission-list {
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 12px;
  background: var(--app-fill-2);
}

.list-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.permission-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

@media (max-width: 640px) {
  .permission-grid {
    grid-template-columns: 1fr;
  }
}

.permission-card {
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

.permission-card:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
}

.permission-card.is-assigned {
  border-color: var(--el-color-success-light-5);
  background: var(--el-color-success-light-9);
}

.permission-card.is-selected-new {
  border-color: var(--el-color-primary-light-5);
  background: var(--el-color-primary-light-9);
}

.permission-card.is-removing {
  border-color: var(--el-color-danger-light-5);
  background: var(--el-color-danger-light-9);
}

.permission-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.permission-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.permission-code {
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
