<script setup lang="ts">
import { ref, onMounted, defineProps, defineEmits } from 'vue';
import { roleService } from '@/services/roleService';
import type { Role } from '@/services/roleService';
import { userService } from '@/services/userService';
import type { User } from '@/services/userService';
import { useUserStore } from '@/stores/user';

// 获取用户信息
const userStore = useUserStore();

// 属性定义
const props = defineProps<{
  userId: number;
  username: string;
}>();

// 事件定义
const emit = defineEmits(['update']);

// 状态
const allRoles = ref<Role[]>([]);
const userRoles = ref<number[]>([]);
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

// 加载所有角色
const loadAllRoles = async () => {
  loading.value.roles = true;
  try {
    const response = await roleService.getRoles({ limit: 500 });
    if (response.code === 200) {
      allRoles.value = response.data.items;
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
  loading.value.userRoles = true;
  try {
    const response = await userService.getUser(props.userId);
    if (response.code === 200) {
      const user = response.data as User;
      userRoles.value = user.roles?.map(role => role.id) || [];
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

// 保存用户角色
const saveUserRoles = async () => {
  loading.value.saving = true;
  try {
    // 使用当前用户ID或默认值
    const operatorId = userStore.userInfo?.id.toString() || '-1';
    
    const operation = {
      role_ids: userRoles.value,
      operator: operatorId,
      operation_login: operatorId,
      user_id: props.userId
    };
    
    // 清空所有角色再分配新角色
    await userService.removeRolesFromUser(props.userId, {
      ...operation,
      role_ids: [] // 移除所有角色
    });
    
    // 如果选择了角色，则分配
    if (userRoles.value.length > 0) {
      const response = await userService.assignRolesToUser(props.userId, operation);
      if (response.code === 200) {
        showNotification('角色分配成功', 'success');
        emit('update');
      } else {
        console.error('角色分配失败:', response.message);
        showNotification('角色分配失败: ' + response.message, 'error');
      }
    } else {
      showNotification('角色已更新', 'success');
      emit('update');
    }
  } catch (error) {
    console.error('保存用户角色出错:', error);
    showNotification('保存用户角色出错', 'error');
  } finally {
    loading.value.saving = false;
  }
};

// 显示通知
const showNotification = (message: string, type: 'success' | 'error' | 'warning') => {
  notification.value.message = message;
  notification.value.type = type;
  notification.value.show = true;
  
  // 3秒后自动关闭
  setTimeout(() => {
    notification.value.show = false;
  }, 3000);
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

// 初始化
onMounted(() => {
  loadAllRoles();
  loadUserRoles();
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
      <h3 class="text-lg font-medium text-gray-900 mb-4">{{ username }} 的角色分配</h3>
      
      <div v-if="loading.roles || loading.userRoles" class="flex justify-center my-8">
        <svg class="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      
      <div v-else class="mb-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          <div 
            v-for="role in allRoles" 
            :key="role.id" 
            class="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
            :class="{ 'border-indigo-500 bg-indigo-50': userRoles.includes(role.id) }"
            @click="userRoles.includes(role.id) ? userRoles = userRoles.filter(id => id !== role.id) : userRoles.push(role.id)"
          >
            <input 
              type="checkbox" 
              :checked="userRoles.includes(role.id)" 
              class="h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              @click.stop
              @change="handleCheckboxChange($event, role.id)"
            />
            <div class="ml-3">
              <span class="text-sm font-medium text-gray-900">{{ role.role_name }}</span>
              <p class="text-xs text-gray-500">{{ role.role_code }}</p>
            </div>
          </div>
        </div>
        
        <div v-if="allRoles.length === 0" class="text-center text-gray-500 py-4">
          暂无可分配的角色
        </div>
      </div>
      
      <div class="flex justify-end mt-4">
        <button 
          @click="saveUserRoles"
          :disabled="loading.saving"
          class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="loading.saving">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            保存中...
          </span>
          <span v-else>保存</span>
        </button>
      </div>
    </div>
  </div>
</template> 