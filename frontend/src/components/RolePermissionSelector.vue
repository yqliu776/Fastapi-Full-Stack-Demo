<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { permissionService } from '@/services/permissionService';
import type { Permission } from '@/services/permissionService';
import { roleService } from '@/services/roleService';
import type { RolePermissionOperation } from '@/services/roleService';
import { useUserStore } from '@/stores/user';

// 获取用户信息
const userStore = useUserStore();

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

// 添加一个计算属性显示权限统计
const permissionStats = computed(() => {
  return {
    total: allPermissions.value.length,
    assigned: rolePermissions.value.length,
    selected: selectedPermissions.value.length,
    toAssign: selectedPermissions.value.filter(id => !rolePermissionIds.value.includes(id)).length,
    toRemove: selectedPermissions.value.filter(id => rolePermissionIds.value.includes(id)).length
  };
});

// 初始化方法
const init = async () => {
  errorMsg.value = '';
  await Promise.all([
    loadAllPermissions(),
    loadRolePermissions()
  ]);
};

// 加载所有权限
const loadAllPermissions = async () => {
  loading.value.allPermissions = true;
  try {
    const response = await permissionService.getPermissions({ limit: 1000 });
    if (response.code === 200) {
      allPermissions.value = response.data.items;
    } else {
      console.error('加载权限列表失败:', response.message);
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
    // 获取角色详情，包含permissions列表
    const roleResponse = await roleService.getRole(props.roleId);
    if (roleResponse.code === 200 && roleResponse.data.permissions) {
      // 使用类型转换确保类型匹配
      rolePermissions.value = roleResponse.data.permissions as unknown as Permission[];
    } else {
      // 如果角色详情中没有permissions或获取失败，尝试使用权限服务获取
      const response = await permissionService.getRolePermissions(props.roleId);
      if (response.code === 200) {
        rolePermissions.value = response.data.items;
      } else {
        console.error('加载角色权限失败:', response.message);
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

// 获取用户ID或默认值
const getUserId = () => {
  return userStore.userInfo?.id.toString() || '-1';
};

// 为角色分配权限
const assignPermissions = async () => {
  if (selectedPermissions.value.length === 0) return;
  errorMsg.value = '';
  
  loading.value.submit = true;
  try {
    // 筛选出未分配给角色的权限
    const permissionsToAssign = selectedPermissions.value.filter(
      id => !rolePermissionIds.value.includes(id)
    );
    
    if (permissionsToAssign.length === 0) {
      loading.value.submit = false;
      return;
    }
    
    const userId = getUserId();
    const operation: RolePermissionOperation = {
      permission_ids: permissionsToAssign,
      operator: userId,
      operation_login: userId,
      role_id: props.roleId
    };
    
    const response = await roleService.assignPermissionsToRole(props.roleId, operation);
    if (response.code === 200) {
      await loadRolePermissions();
      emit('update');
    } else {
      console.error('分配权限失败:', response.message);
      errorMsg.value = '分配权限失败: ' + response.message;
    }
  } catch (error) {
    console.error('分配权限出错:', error);
    errorMsg.value = '分配权限出错';
  } finally {
    loading.value.submit = false;
  }
};

// 移除角色权限
const removePermissions = async () => {
  if (selectedPermissions.value.length === 0) return;
  errorMsg.value = '';
  
  loading.value.submit = true;
  try {
    // 筛选出已分配给角色的权限
    const permissionsToRemove = selectedPermissions.value.filter(
      id => rolePermissionIds.value.includes(id)
    );
    
    if (permissionsToRemove.length === 0) {
      loading.value.submit = false;
      return;
    }
    
    const userId = getUserId();
    const operation: RolePermissionOperation = {
      permission_ids: permissionsToRemove,
      operator: userId,
      operation_login: userId,
      role_id: props.roleId
    };
    
    const response = await roleService.removePermissionsFromRole(props.roleId, operation);
    if (response.code === 200) {
      await loadRolePermissions();
      emit('update');
    } else {
      console.error('移除权限失败:', response.message);
      errorMsg.value = '移除权限失败: ' + response.message;
    }
  } catch (error) {
    console.error('移除权限出错:', error);
    errorMsg.value = '移除权限出错';
  } finally {
    loading.value.submit = false;
  }
};

// 监听visible变化
watch(() => props.visible, (newValue) => {
  if (newValue) {
    init();
  } else {
    selectedPermissions.value = [];
  }
});

// 监听roleId变化
watch(() => props.roleId, () => {
  if (props.visible) {
    loadRolePermissions();
  }
});

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
    <div class="mb-4 flex items-center justify-between">
      <div class="w-64">
        <input
          v-model="searchKeyword"
          type="text"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          placeholder="搜索权限名称或代码"
        />
      </div>
      <div class="flex space-x-2">
        <button
          @click="selectAll"
          class="bg-gray-200 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-300 transition-colors"
        >
          全选
        </button>
        <button
          @click="deselectAll"
          class="bg-gray-200 text-gray-700 px-3 py-1 rounded text-sm hover:bg-gray-300 transition-colors"
        >
          全不选
        </button>
      </div>
    </div>

    <!-- 错误消息 -->
    <div v-if="errorMsg" class="mb-3 p-2 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
      {{ errorMsg }}
    </div>

    <!-- 权限信息统计 -->
    <div class="mb-3 p-2 bg-gray-50 rounded border border-gray-200 text-xs">
      <div class="flex flex-wrap gap-3">
        <div>总权限数: <span class="font-semibold">{{ permissionStats.total }}</span></div>
        <div>已分配: <span class="font-semibold text-green-600">{{ permissionStats.assigned }}</span></div>
        <div>已选择: <span class="font-semibold text-blue-600">{{ permissionStats.selected }}</span></div>
        <div v-if="permissionStats.toAssign > 0">待分配: <span class="font-semibold text-indigo-600">{{ permissionStats.toAssign }}</span></div>
        <div v-if="permissionStats.toRemove > 0">待移除: <span class="font-semibold text-red-600">{{ permissionStats.toRemove }}</span></div>
      </div>
    </div>
    
    <!-- 权限标签图例 -->
    <div class="mb-3 flex items-center gap-3 text-xs">
      <div class="flex items-center">
        <div class="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
        <span>已分配权限</span>
      </div>
      <div class="flex items-center">
        <div class="w-3 h-3 rounded-full bg-blue-500 mr-1"></div>
        <span>已选择待操作</span>
      </div>
    </div>
    
    <!-- 权限列表 -->
    <div class="max-h-60 overflow-y-auto border rounded-md p-2 mb-4">
      <div v-if="loading.allPermissions || loading.rolePermissions" class="text-center py-4">
        <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600 mr-2"></div>
        加载中...
      </div>
      <div v-else-if="filteredPermissions.length === 0" class="text-center py-4 text-gray-500">
        暂无数据
      </div>
      <div v-else class="grid grid-cols-2 gap-2">
        <div
          v-for="permission in filteredPermissions"
          :key="permission.id"
          class="flex items-center p-2 rounded cursor-pointer transition-colors"
          :class="{
            'bg-blue-50 border border-blue-200': isPermissionSelected(permission.id) && !hasRolePermission(permission.id),
            'bg-green-50 border border-green-200': hasRolePermission(permission.id) && !isPermissionSelected(permission.id),
            'bg-gradient-to-r from-green-50 to-blue-50 border border-blue-200': hasRolePermission(permission.id) && isPermissionSelected(permission.id),
            'hover:bg-gray-100 border border-transparent': !isPermissionSelected(permission.id) && !hasRolePermission(permission.id)
          }"
          @click="toggleSelectPermission(permission.id)"
        >
          <input
            type="checkbox"
            :checked="isPermissionSelected(permission.id)"
            class="mr-2 h-4 w-4 text-indigo-600 rounded"
            @click.stop
            @change="toggleSelectPermission(permission.id)"
          />
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium truncate">{{ permission.permission_name }}</div>
            <div class="text-xs text-gray-500 truncate">{{ permission.permission_code }}</div>
          </div>
          <div
            v-if="hasRolePermission(permission.id)"
            class="ml-auto flex-shrink-0 bg-green-100 text-green-800 text-xs py-0.5 px-2 rounded-full font-medium flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            已分配
          </div>
        </div>
      </div>
    </div>
    
    <!-- 底部按钮 -->
    <div class="flex justify-between">
      <div>
        <span class="text-sm text-gray-500">已选择 {{ selectedPermissions.length }} 项</span>
      </div>
      <div class="flex space-x-2">
        <button
          @click="assignPermissions"
          :disabled="loading.submit || permissionStats.toAssign === 0"
          class="bg-green-600 text-white py-1 px-3 rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="loading.submit && permissionStats.toAssign > 0" class="inline-block animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></span>
          分配权限 {{ permissionStats.toAssign > 0 ? `(${permissionStats.toAssign})` : '' }}
        </button>
        <button
          @click="removePermissions"
          :disabled="loading.submit || permissionStats.toRemove === 0"
          class="bg-red-600 text-white py-1 px-3 rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="loading.submit && permissionStats.toRemove > 0" class="inline-block animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></span>
          移除权限 {{ permissionStats.toRemove > 0 ? `(${permissionStats.toRemove})` : '' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 滚动条美化 */
.max-h-60::-webkit-scrollbar {
  width: 6px;
}

.max-h-60::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.max-h-60::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.max-h-60::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>