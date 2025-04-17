<script setup lang="ts">
import { ref, onMounted, defineProps, defineEmits, computed, watch } from 'vue';
import { roleService } from '@/services/roleService';
import type { Role } from '@/services/roleService';
import { userService } from '@/services/userService';
import type { User } from '@/services/userService';
import { useUserStore } from '@/stores/user';
import type { PropType } from 'vue';

// 获取用户信息
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
const notification = ref({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error' | 'warning'
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
  
  // 新增的角色（当前选中但初始未分配）
  const toAssign = userRoles.value.filter(id => !initialUserRoles.value.includes(id)).length;
  
  // 要移除的角色（初始已分配但当前未选中）
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
      // 在加载所有角色后，根据角色代码匹配设置用户角色
      matchUserRolesByCode();
    } else {
      console.error('加载角色列表失败:', response.message);
      showNotification('加载角色列表失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('加载角色列表出错:', error);
    showNotification('加载角色列表出错', 'error');
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
      // 保存角色代码，之后用于匹配角色ID
      if (userData.roles && Array.isArray(userData.roles)) {
        initialRoleCodes.value = userData.roles.map(role => role.role_code);
        console.log('用户已有角色代码:', initialRoleCodes.value);
      } else {
        initialRoleCodes.value = [];
        console.log('用户没有角色或角色数据格式不正确');
      }
    } else {
      console.error('加载用户角色失败:', response.message);
      showNotification('加载用户角色失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('加载用户角色出错:', error);
    showNotification('加载用户角色出错', 'error');
  } finally {
    loading.value.userRoles = false;
  }
};

// 根据角色代码匹配角色ID
const matchUserRolesByCode = () => {
  // 如果角色列表为空，不进行处理
  if (allRoles.value.length === 0) {
    console.log('角色列表为空，无法匹配角色');
    return;
  }
  
  // 根据模式和可用数据选择角色代码源
  let roleCodeSource: string[] = [];
  
  if (props.mode === 'create') {
    // 创建模式：使用传入的initialRoles
    roleCodeSource = props.initialRoles || [];
  } else {
    // 编辑模式：使用从API加载的角色代码
    roleCodeSource = initialRoleCodes.value;
  }
  
  if (roleCodeSource.length === 0) {
    console.log('没有角色代码可匹配');
    initialUserRoles.value = [];
    userRoles.value = [];
    return;
  }
  
  // 查找角色ID
  const matchedRoleIds = allRoles.value
    .filter(role => roleCodeSource.includes(role.role_code))
    .map(role => role.id);
  
  console.log('匹配到的角色ID:', matchedRoleIds);
  initialUserRoles.value = [...matchedRoleIds];
  userRoles.value = [...matchedRoleIds]; // 初始化选中状态
  
  console.log('初始角色IDs:', initialUserRoles.value);
  console.log('当前选中角色IDs:', userRoles.value);
};

// 显示通知
const showNotification = (message: string, type: 'success' | 'error' | 'warning' | 'info') => {
  notification.value.message = message;
  notification.value.type = type as 'success' | 'error' | 'warning'; // 转换类型以匹配声明
  notification.value.show = true;
  
  // 3秒后自动关闭
  setTimeout(() => {
    notification.value.show = false;
  }, 3000);
};

// 保存用户角色
const saveUserRoles = async () => {
  // 如果是创建模式，则只发射事件通知父组件
  if (props.mode === 'create') {
    // 获取选中角色的代码列表
    const selectedRoleCodes = userRoles.value.map(roleId => {
      const role = allRoles.value.find(r => r.id === roleId);
      return role ? role.role_code : '';
    }).filter(code => code !== '');
    
    emit('roleChange', selectedRoleCodes);
    showNotification('角色已选择', 'success');
    return;
  }
  
  // 如果是编辑模式，且没有发生变化，则不做任何操作
  if (areArraysEqual(userRoles.value, initialUserRoles.value)) {
    showNotification('角色没有变化', 'info');
    return;
  }
  
  // 否则，调用API保存用户角色
  loading.value.saving = true;
  try {
    // 获取选中角色的代码列表
    const selectedRoleCodes = userRoles.value.map(roleId => {
      const role = allRoles.value.find(r => r.id === roleId);
      return role ? role.role_code : '';
    }).filter(code => code !== '');
    
    // 使用当前用户ID或默认值
    const operatorId = userStore.userInfo?.id.toString() || '-1';
    
    // 构造请求数据
    const roleData = {
      role_codes: selectedRoleCodes,
      operator: operatorId,
      operation_login: operatorId
    };
    
    // 直接分配新的角色集合（后端将处理删除不在列表中的角色）
    const response = await userService.assignRolesToUser(props.userId, roleData);
    
    if (response.code === 200) {
      showNotification('保存用户角色成功', 'success');
      initialUserRoles.value = [...userRoles.value]; // 更新初始状态
      initialRoleCodes.value = [...selectedRoleCodes]; // 更新角色代码
      emit('update');
    } else {
      showNotification('保存用户角色失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('保存用户角色出错:', error);
    showNotification('保存用户角色出错', 'error');
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

// 初始化
onMounted(async () => {
  await loadAllRoles();
  if (props.mode === 'edit' && props.userId) {
    await loadUserRoles();
    // 在加载完所有角色和用户角色后，将再次调用matchUserRolesByCode
    matchUserRolesByCode();
  }
  // 如果是创建模式，也需要根据initialRoles设置初始选中的角色
  else if (props.mode === 'create' && props.initialRoles.length > 0) {
    // matchUserRolesByCode将在loadAllRoles完成后自动调用
  }
});

// 监听initialRoles变化
watch(() => props.initialRoles, () => {
  if (props.mode === 'create' && allRoles.value.length > 0) {
    matchUserRolesByCode();
  }
}, { deep: true });

// 当角色选择改变时触发事件
watch(userRoles, (newValue) => {
  if (props.mode === 'create') {
    // 创建模式：当用户选择角色时，通知父组件
    const selectedCodes = allRoles.value
      .filter(role => newValue.includes(role.id))
      .map(role => role.role_code);
    
    emit('roleChange', selectedCodes);
  }
});
</script>

<template>
  <div class="user-role-selector">
    <!-- 通知栏 -->
    <div 
      v-if="notification.show" 
      class="fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 transition-opacity duration-500 opacity-95 flex items-center max-w-md"
      :class="{
        'bg-green-600 text-white': notification.type === 'success',
        'bg-red-600 text-white': notification.type === 'error',
        'bg-yellow-500 text-white': notification.type === 'warning'
      }"
    >
      <div class="mr-3" v-if="notification.type === 'success'">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <div class="mr-3" v-else-if="notification.type === 'error'">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <div class="mr-3" v-else-if="notification.type === 'warning'">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <span>{{ notification.message }}</span>
    </div>
    
    <div class="bg-white p-4 rounded-lg shadow mb-4">
      <h3 class="text-lg font-medium text-gray-900 mb-4">
        <template v-if="mode === 'create'">选择用户角色</template>
        <template v-else>{{ username || '用户' }} 的角色分配</template>
      </h3>
      
      <!-- 顶部操作栏 -->
      <div class="mb-4 flex items-center justify-between">
        <div class="w-64">
          <input
            v-model="searchKeyword"
            type="text"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="搜索角色名称或代码"
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

      <!-- 角色信息统计 -->
      <div class="mb-3 p-2 bg-gray-50 rounded border border-gray-200 text-xs">
        <div class="flex flex-wrap gap-3">
          <div>总角色数: <span class="font-semibold">{{ roleStats.total }}</span></div>
          <div>已分配: <span class="font-semibold text-green-600">{{ roleStats.assigned }}</span></div>
          <div>已选择: <span class="font-semibold text-blue-600">{{ roleStats.selected }}</span></div>
          <div v-if="roleStats.toAssign > 0">待分配: <span class="font-semibold text-indigo-600">{{ roleStats.toAssign }}</span></div>
          <div v-if="roleStats.toRemove > 0">待移除: <span class="font-semibold text-red-600">{{ roleStats.toRemove }}</span></div>
        </div>
      </div>
      
      <!-- 角色标签图例 - 更新更明显的标记 -->
      <div class="mb-3 flex flex-wrap items-center gap-4 text-xs">
        <div class="flex items-center">
          <div class="w-5 h-5 rounded bg-green-100 border border-green-300 flex items-center justify-center mr-1">
            <svg class="w-3 h-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <span>已分配角色</span>
        </div>
        <div class="flex items-center">
          <div class="w-5 h-5 rounded bg-blue-100 border border-blue-300 flex items-center justify-center mr-1">
            <svg class="w-3 h-3 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
          </div>
          <span>新选择待分配</span>
        </div>
        <div class="flex items-center">
          <div class="w-5 h-5 rounded bg-red-100 border border-red-300 flex items-center justify-center mr-1">
            <svg class="w-3 h-3 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </div>
          <span>已取消选择(将被移除)</span>
        </div>
      </div>
      
      <div v-if="loading.roles || loading.userRoles" class="flex justify-center my-8">
        <svg class="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      
      <!-- 角色列表 - 改进卡片样式使已分配角色更加明显 -->
      <div v-else class="max-h-60 overflow-y-auto border rounded-md p-2 mb-4">
        <div v-if="filteredRoles.length === 0" class="text-center text-gray-500 py-4">
          暂无匹配的角色
        </div>
        
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 gap-3">
          <div 
            v-for="role in filteredRoles" 
            :key="role.id" 
            class="flex items-center p-3 border-2 rounded-lg cursor-pointer transition-colors"
            :class="{
              'bg-blue-50 border-blue-400 shadow': isRoleSelected(role.id) && !hasRoleInitially(role.id),
              'bg-red-50 border-red-400 shadow': hasRoleInitially(role.id) && !isRoleSelected(role.id),
              'bg-green-50 border-green-400 shadow': hasRoleInitially(role.id) && isRoleSelected(role.id),
              'hover:bg-gray-50 border-gray-200': !isRoleSelected(role.id) && !hasRoleInitially(role.id)
            }"
            @click="isRoleSelected(role.id) ? userRoles = userRoles.filter(id => id !== role.id) : userRoles.push(role.id)"
          >
            <!-- 角色状态图标区域 -->
            <div class="mr-2 flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center"
                :class="{
                  'bg-green-100': hasRoleInitially(role.id) && isRoleSelected(role.id),
                  'bg-blue-100': isRoleSelected(role.id) && !hasRoleInitially(role.id),
                  'bg-red-100': hasRoleInitially(role.id) && !isRoleSelected(role.id),
                  'bg-gray-100': !isRoleSelected(role.id) && !hasRoleInitially(role.id)
                }">
              <svg v-if="hasRoleInitially(role.id) && isRoleSelected(role.id)" class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <svg v-else-if="isRoleSelected(role.id) && !hasRoleInitially(role.id)" class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              <svg v-else-if="hasRoleInitially(role.id) && !isRoleSelected(role.id)" class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </div>
            
            <!-- 复选框 -->
            <input 
              type="checkbox" 
              :checked="isRoleSelected(role.id)" 
              class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              @click.stop
              @change="handleCheckboxChange($event, role.id)"
            />
            
            <!-- 角色信息 -->
            <div class="ml-3 flex-1 min-w-0">
              <span class="text-sm font-medium text-gray-900 block truncate">{{ role.role_name }}</span>
              <p class="text-xs text-gray-500 truncate">{{ role.role_code }}</p>
            </div>
            
            <!-- 状态标签 -->
            <div
              v-if="hasRoleInitially(role.id)" 
              class="ml-auto flex-shrink-0 text-xs font-medium py-1 px-2 rounded-full flex items-center"
              :class="{
                'bg-green-100 text-green-800': isRoleSelected(role.id),
                'bg-red-100 text-red-800': !isRoleSelected(role.id)
              }"
            >
              <svg v-if="isRoleSelected(role.id)" class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <svg v-else class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              {{ isRoleSelected(role.id) ? '已分配' : '将被移除' }}
            </div>
            <div
              v-else-if="isRoleSelected(role.id)"
              class="ml-auto flex-shrink-0 bg-blue-100 text-blue-800 text-xs py-1 px-2 rounded-full font-medium flex items-center"
            >
              <svg class="h-3.5 w-3.5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              将被分配
            </div>
          </div>
        </div>
      </div>
      
      <div class="flex justify-between">
        <div>
          <span class="text-sm text-gray-500">已选择 {{ userRoles.length }} 项</span>
        </div>
        <div class="flex space-x-2" v-if="mode !== 'create'">
          <button 
            @click="saveUserRoles"
            :disabled="loading.saving || (roleStats.toAssign === 0 && roleStats.toRemove === 0)"
            class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="loading.saving">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              保存中...
            </span>
            <span v-else>保存更改</span>
          </button>
        </div>
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