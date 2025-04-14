<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { roleService } from '@/services/roleService';
import type { Role, RoleCreate, RoleUpdate } from '@/services/roleService';
import RolePermissionSelector from '@/components/RolePermissionSelector.vue';
import RoleMenuSelector from '@/components/RoleMenuSelector.vue';
import { useUserStore } from '@/stores/user';

// 获取用户信息
const userStore = useUserStore();

// 状态
const roles = ref<Role[]>([]);
const totalRoles = ref(0);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const searchForm = reactive({
  role_name: '',
  role_code: ''
});

// 模态框状态
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showPermissionModal = ref(false);
const showMenuModal = ref(false);
const currentRole = ref<Role | null>(null);

// 消息通知状态
const notification = reactive({
  show: false,
  message: '',
  type: 'success' // success, error, warning
});

// 表单数据
const roleForm = reactive<RoleCreate & RoleUpdate>({
  role_name: '',
  role_code: '',
  created_by: '-1',
  last_updated_by: '-1',
  last_update_login: '-1'
});

// 显示通知
const showNotification = (message: string, type: 'success' | 'error' | 'warning') => {
  notification.message = message;
  notification.type = type;
  notification.show = true;
  
  // 3秒后自动关闭
  setTimeout(() => {
    notification.show = false;
  }, 3000);
};

// 加载角色列表
const loadRoles = async () => {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * pageSize.value;
    const params = {
      skip,
      limit: pageSize.value,
      ...searchForm
    };
    const response = await roleService.getRoles(params);
    if (response.code === 200) {
      roles.value = response.data.items;
      totalRoles.value = response.data.total;
    } else {
      console.error('加载角色列表失败:', response.message);
      showNotification('加载角色列表失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('加载角色列表出错:', error);
    showNotification('加载角色列表出错', 'error');
  } finally {
    loading.value = false;
  }
};

// 搜索角色
const searchRoles = () => {
  currentPage.value = 1;
  loadRoles();
};

// 重置搜索
const resetSearch = () => {
  searchForm.role_name = '';
  searchForm.role_code = '';
  searchRoles();
};

// 打开创建角色模态框
const openCreateModal = () => {
  // 使用当前用户ID或默认值
  const userId = userStore.userInfo?.id.toString() || '-1';
  
  roleForm.role_name = '';
  roleForm.role_code = '';
  roleForm.created_by = userId;
  roleForm.last_updated_by = userId;
  roleForm.last_update_login = userId;
  
  showCreateModal.value = true;
};

// 创建角色
const createRole = async () => {
  try {
    const response = await roleService.createRole(roleForm);
    if (response.code === 200) {
      showCreateModal.value = false;
      loadRoles();
      showNotification('角色创建成功', 'success');
    } else {
      console.error('创建角色失败:', response.message);
      showNotification('创建角色失败: ' + response.message, 'error');
    }
  } catch (error: unknown) {
    console.error('创建角色出错:', error);
    // 尝试提取API返回的详细错误信息
    let errorMsg = '创建角色出错';
    if (
      error && 
      typeof error === 'object' && 
      'response' in error && 
      error.response && 
      typeof error.response === 'object' && 
      'data' in error.response && 
      error.response.data && 
      typeof error.response.data === 'object' && 
      'detail' in error.response.data
    ) {
      try {
        const detail = error.response.data.detail;
        // 尝试格式化错误信息
        if (Array.isArray(detail)) {
          errorMsg += ': ' + detail.map((item: {msg: string}) => item.msg).join(', ');
        } else if (typeof detail === 'string') {
          errorMsg += ': ' + detail;
        }
      } catch {
        // 如果格式化失败，使用原始错误消息
        errorMsg = '创建角色出错';
      }
    }
    showNotification(errorMsg, 'error');
  }
};

// 打开编辑角色模态框
const openEditModal = (role: Role) => {
  // 使用当前用户ID或默认值
  const userId = userStore.userInfo?.id.toString() || '-1';
  
  currentRole.value = role;
  roleForm.role_name = role.role_name;
  roleForm.role_code = role.role_code;
  roleForm.last_updated_by = userId;
  roleForm.last_update_login = userId;
  
  showEditModal.value = true;
};

// 更新角色
const updateRole = async () => {
  if (!currentRole.value) return;
  
  try {
    const response = await roleService.updateRole(currentRole.value.id, roleForm);
    if (response.code === 200) {
      showEditModal.value = false;
      loadRoles();
      showNotification('角色更新成功', 'success');
    } else {
      console.error('更新角色失败:', response.message);
      showNotification('更新角色失败: ' + response.message, 'error');
    }
  } catch (error: unknown) {
    console.error('更新角色出错:', error);
    showNotification('更新角色出错', 'error');
  }
};

// 删除角色
const deleteRole = async (role: Role) => {
  if (!confirm(`确定要删除角色"${role.role_name}"吗？`)) return;
  
  try {
    const response = await roleService.deleteRole(role.id);
    if (response.code === 200) {
      loadRoles();
      showNotification('角色删除成功', 'success');
    } else {
      console.error('删除角色失败:', response.message);
      showNotification('删除角色失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('删除角色出错:', error);
    showNotification('删除角色出错', 'error');
  }
};

// 打开权限分配模态框
const openPermissionModal = (role: Role) => {
  currentRole.value = role;
  showPermissionModal.value = true;
};

// 打开菜单分配模态框
const openMenuModal = (role: Role) => {
  currentRole.value = role;
  showMenuModal.value = true;
};

// 权限或菜单更新后刷新角色列表
const handleRoleUpdate = () => {
  loadRoles();
  showNotification('更新成功', 'success');
};

// 页面变化处理
const handlePageChange = (page: number) => {
  currentPage.value = page;
  loadRoles();
};

// 初始化
onMounted(() => {
  loadRoles();
});
</script>

<template>
  <div class="role-management">
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
    
    <h1 class="text-2xl font-bold mb-4">角色管理</h1>
    
    <!-- 搜索表单 -->
    <div class="bg-white p-4 rounded shadow mb-4">
      <div class="flex flex-wrap gap-4 items-end">
        <div class="w-full md:w-auto">
          <label class="block text-sm font-medium text-gray-700 mb-1">角色名称</label>
          <input 
            v-model="searchForm.role_name"
            type="text" 
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="请输入角色名称"
          />
        </div>
        <div class="w-full md:w-auto">
          <label class="block text-sm font-medium text-gray-700 mb-1">角色代码</label>
          <input 
            v-model="searchForm.role_code"
            type="text" 
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="请输入角色代码"
          />
        </div>
        <div class="flex gap-2">
          <button 
            @click="searchRoles"
            class="bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-150"
          >
            搜索
          </button>
          <button 
            @click="resetSearch"
            class="bg-gray-100 text-gray-700 py-2 px-4 rounded hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition duration-150"
          >
            重置
          </button>
          <button 
            @click="openCreateModal"
            class="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-150"
          >
            创建角色
          </button>
        </div>
      </div>
    </div>
    
    <!-- 角色列表 -->
    <div class="bg-white rounded shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色名称</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">角色代码</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">更新时间</th>
            <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-if="loading" class="text-center">
            <td colspan="6" class="px-6 py-4 whitespace-nowrap text-gray-500">
              <div class="flex justify-center items-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                加载中...
              </div>
            </td>
          </tr>
          <tr v-else-if="roles.length === 0" class="text-center">
            <td colspan="6" class="px-6 py-4 whitespace-nowrap text-gray-500">
              暂无数据
            </td>
          </tr>
          <tr v-for="role in roles" :key="role.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-6 py-4 whitespace-nowrap">{{ role.role_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ role.role_code }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ new Date(role.creation_date).toLocaleString() }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ new Date(role.last_update_date).toLocaleString() }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button 
                @click="openEditModal(role)"
                class="text-indigo-600 hover:text-indigo-900 mr-3 hover:underline transition duration-150"
              >
                编辑
              </button>
              <button 
                @click="openPermissionModal(role)"
                class="text-green-600 hover:text-green-900 mr-3 hover:underline transition duration-150"
              >
                权限
              </button>
              <button 
                @click="openMenuModal(role)"
                class="text-blue-600 hover:text-blue-900 mr-3 hover:underline transition duration-150"
              >
                菜单
              </button>
              <button 
                @click="deleteRole(role)"
                class="text-red-600 hover:text-red-900 hover:underline transition duration-150"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- 分页 -->
      <div class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
        <div class="flex justify-between items-center">
          <div class="text-sm text-gray-700">
            共 <span class="font-medium">{{ totalRoles }}</span> 条记录
          </div>
          <div class="flex justify-end">
            <button 
              :disabled="currentPage <= 1"
              @click="handlePageChange(currentPage - 1)"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150"
            >
              上一页
            </button>
            <button 
              :disabled="roles.length < pageSize"
              @click="handlePageChange(currentPage + 1)"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建角色模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showCreateModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">创建角色</h3>
            <div class="mt-2">
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">角色名称 <span class="text-red-500">*</span></label>
                <input 
                  v-model="roleForm.role_name"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入角色名称"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">角色代码 <span class="text-red-500">*</span></label>
                <input 
                  v-model="roleForm.role_code"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入角色代码"
                />
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="createRole"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              确认
            </button>
            <button 
              @click="showCreateModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 编辑角色模态框 -->
    <div v-if="showEditModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showEditModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">编辑角色</h3>
            <div class="mt-2">
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">角色名称 <span class="text-red-500">*</span></label>
                <input 
                  v-model="roleForm.role_name"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入角色名称"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">角色代码 <span class="text-red-500">*</span></label>
                <input 
                  v-model="roleForm.role_code"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入角色代码"
                />
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="updateRole"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              确认
            </button>
            <button 
              @click="showEditModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 权限分配模态框 -->
    <div v-if="showPermissionModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showPermissionModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
              角色权限管理: {{ currentRole?.role_name }}
            </h3>
            <div class="mt-2">
              <RolePermissionSelector 
                v-if="currentRole"
                :role-id="currentRole.id"
                :visible="showPermissionModal"
                @update="handleRoleUpdate"
                @close="showPermissionModal = false"
              />
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="showPermissionModal = false"
              class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:w-auto sm:text-sm transition duration-150"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 菜单分配模态框 -->
    <div v-if="showMenuModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showMenuModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
              角色菜单管理: {{ currentRole?.role_name }}
            </h3>
            <div class="mt-2">
              <RoleMenuSelector 
                v-if="currentRole"
                :role-id="currentRole.id"
                :visible="showMenuModal"
                @update="handleRoleUpdate"
                @close="showMenuModal = false"
              />
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="showMenuModal = false"
              class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:w-auto sm:text-sm transition duration-150"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 动画效果 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>