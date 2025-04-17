<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { userService } from '@/services/userService';
import type { User, UserCreate, UserUpdate } from '@/services/userService';
import UserRoleSelector from '@/components/UserRoleSelector.vue';
import { useUserStore } from '@/stores/user';

// 获取用户信息
const userStore = useUserStore();

// 状态
const users = ref<User[]>([]);
const totalUsers = ref(0);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const searchForm = reactive({
  user_name: '',
  email: '',
  delete_flag: ''
});

// 模态框状态
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showPasswordModal = ref(false);
const showRoleModal = ref(false);
const currentUser = ref<User | null>(null);

// 消息通知状态
const notification = reactive({
  show: false,
  message: '',
  type: 'success' // success, error, warning
});

// 表单数据
const userForm = reactive<UserCreate & UserUpdate>({
  user_name: '',
  email: '',
  phone: '',
  password: '',
  delete_flag: 'N',
  created_by: '-1',
  last_updated_by: '-1',
  last_update_login: '-1'
});

// 密码表单
const passwordForm = reactive({
  password: '',
  confirmPassword: '',
  last_updated_by: '-1',
  last_update_login: '-1'
});

// 用户状态选项
const statusOptions = [
  { value: 'N', label: '启用' },
  { value: 'Y', label: '禁用' }
];

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

// 加载用户列表
const loadUsers = async () => {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * pageSize.value;
    const params = {
      skip,
      limit: pageSize.value,
      ...searchForm
    };
    const response = await userService.getUsers(params);
    if (response.code === 200) {
      users.value = response.data.items;
      totalUsers.value = response.data.total;
    } else {
      console.error('加载用户列表失败:', response.message);
      showNotification('加载用户列表失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('加载用户列表出错:', error);
    showNotification('加载用户列表出错', 'error');
  } finally {
    loading.value = false;
  }
};

// 搜索用户
const searchUsers = () => {
  currentPage.value = 1;
  loadUsers();
};

// 重置搜索
const resetSearch = () => {
  searchForm.user_name = '';
  searchForm.email = '';
  searchForm.delete_flag = '';
  searchUsers();
};

// 打开创建用户模态框
const openCreateModal = () => {
  // 使用当前用户ID或默认值
  const userId = userStore.userInfo?.id.toString() || '-1';
  
  userForm.user_name = '';
  userForm.email = '';
  userForm.phone = '';
  userForm.password = '';
  userForm.delete_flag = 'N';
  userForm.created_by = userId;
  userForm.last_updated_by = userId;
  userForm.last_update_login = userId;
  
  showCreateModal.value = true;
};

// 创建用户
const createUser = async () => {
  if (!userForm.password) {
    showNotification('请输入密码', 'error');
    return;
  }
  
  try {
    const response = await userService.createUser(userForm);
    if (response.code === 200) {
      showCreateModal.value = false;
      loadUsers();
      showNotification('用户创建成功', 'success');
    } else {
      console.error('创建用户失败:', response.message);
      showNotification('创建用户失败: ' + response.message, 'error');
    }
  } catch (error: unknown) {
    console.error('创建用户出错:', error);
    // 尝试提取API返回的详细错误信息
    let errorMsg = '创建用户出错';
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
        errorMsg = '创建用户出错';
      }
    }
    showNotification(errorMsg, 'error');
  }
};

// 打开编辑用户模态框
const openEditModal = (user: User) => {
  // 使用当前用户ID或默认值
  const userId = userStore.userInfo?.id.toString() || '-1';
  
  currentUser.value = user;
  userForm.user_name = user.user_name;
  userForm.email = user.email;
  userForm.phone = user.phone || '';
  userForm.delete_flag = user.delete_flag;
  userForm.last_updated_by = userId;
  userForm.last_update_login = userId;
  
  showEditModal.value = true;
};

// 更新用户
const updateUser = async () => {
  if (!currentUser.value) return;
  
  try {
    const response = await userService.updateUser(currentUser.value.id, userForm);
    if (response.code === 200) {
      showEditModal.value = false;
      loadUsers();
      showNotification('用户更新成功', 'success');
    } else {
      console.error('更新用户失败:', response.message);
      showNotification('更新用户失败: ' + response.message, 'error');
    }
  } catch (error: unknown) {
    console.error('更新用户出错:', error);
    showNotification('更新用户出错', 'error');
  }
};

// 打开修改密码模态框
const openPasswordModal = (user: User) => {
  // 使用当前用户ID或默认值
  const userId = userStore.userInfo?.id.toString() || '-1';
  
  currentUser.value = user;
  passwordForm.password = '';
  passwordForm.confirmPassword = '';
  passwordForm.last_updated_by = userId;
  passwordForm.last_update_login = userId;
  
  showPasswordModal.value = true;
};

// 修改密码
const updatePassword = async () => {
  if (!currentUser.value) return;
  
  if (passwordForm.password !== passwordForm.confirmPassword) {
    showNotification('两次输入的密码不一致', 'error');
    return;
  }
  
  try {
    const response = await userService.updateUserPassword(currentUser.value.id, {
      password: passwordForm.password,
      last_updated_by: passwordForm.last_updated_by,
      last_update_login: passwordForm.last_update_login
    });
    if (response.code === 200) {
      showPasswordModal.value = false;
      showNotification('密码修改成功', 'success');
    } else {
      console.error('修改密码失败:', response.message);
      showNotification('修改密码失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('修改密码出错:', error);
    showNotification('修改密码出错', 'error');
  }
};

// 删除用户
const deleteUser = async (user: User) => {
  if (!confirm(`确定要删除用户"${user.user_name}"吗？`)) return;
  
  try {
    const response = await userService.deleteUser(user.id);
    if (response.code === 200) {
      loadUsers();
      showNotification('用户删除成功', 'success');
    } else {
      console.error('删除用户失败:', response.message);
      showNotification('删除用户失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('删除用户出错:', error);
    showNotification('删除用户出错', 'error');
  }
};

// 打开角色分配模态框
const openRoleModal = (user: User) => {
  currentUser.value = user;
  showRoleModal.value = true;
};

// 角色更新后刷新用户列表
const handleUserUpdate = () => {
  loadUsers();
  showNotification('更新成功', 'success');
};

// 页面变化处理
const handlePageChange = (page: number) => {
  currentPage.value = page;
  loadUsers();
};

// 获取用户状态显示文本
const getUserStatusText = (deleteFlag: string) => {
  const option = statusOptions.find(opt => opt.value === deleteFlag);
  return option ? option.label : deleteFlag;
};

// 获取用户状态CSS类
const getUserStatusClass = (deleteFlag: string) => {
  switch (deleteFlag) {
    case 'N':
      return 'bg-green-100 text-green-800';
    case 'Y':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

// 初始化
onMounted(() => {
  loadUsers();
});
</script>

<template>
  <div class="user-management">
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
    
    <h1 class="text-2xl font-bold mb-4">用户管理</h1>
    
    <!-- 搜索表单 -->
    <div class="bg-white p-4 rounded shadow mb-4">
      <div class="flex flex-wrap gap-4 items-end">
        <div class="w-full md:w-auto">
          <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
          <input 
            v-model="searchForm.user_name"
            type="text" 
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="请输入用户名"
          />
        </div>
        <div class="w-full md:w-auto">
          <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
          <input 
            v-model="searchForm.email"
            type="text" 
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="请输入邮箱"
          />
        </div>
        <div class="w-full md:w-auto">
          <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
          <select 
            v-model="searchForm.delete_flag"
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option value="">全部</option>
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
        <div class="flex gap-2">
          <button 
            @click="searchUsers"
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
            创建用户
          </button>
        </div>
      </div>
    </div>
    
    <!-- 用户列表 -->
    <div class="bg-white rounded shadow overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户名</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">邮箱</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">电话</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
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
          <tr v-else-if="users.length === 0" class="text-center">
            <td colspan="6" class="px-6 py-4 whitespace-nowrap text-gray-500">
              暂无数据
            </td>
          </tr>
          <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-6 py-4 whitespace-nowrap">{{ user.user_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ user.email }}</td>
            <td class="px-6 py-4 whitespace-nowrap">{{ user.phone || '-' }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="getUserStatusClass(user.delete_flag)">
                {{ getUserStatusText(user.delete_flag) }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">{{ new Date(user.creation_date).toLocaleString() }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button 
                @click="openEditModal(user)"
                class="text-indigo-600 hover:text-indigo-900 mr-2 hover:underline transition duration-150"
              >
                编辑
              </button>
              <button 
                @click="openPasswordModal(user)"
                class="text-blue-600 hover:text-blue-900 mr-2 hover:underline transition duration-150"
              >
                密码
              </button>
              <button 
                @click="openRoleModal(user)"
                class="text-green-600 hover:text-green-900 mr-2 hover:underline transition duration-150"
              >
                角色
              </button>
              <button 
                @click="deleteUser(user)"
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
            共 <span class="font-medium">{{ totalUsers }}</span> 条记录
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
              :disabled="users.length < pageSize"
              @click="handlePageChange(currentPage + 1)"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建用户模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showCreateModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">创建用户</h3>
            <div class="mt-2">
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">用户名 <span class="text-red-500">*</span></label>
                <input 
                  v-model="userForm.user_name"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入用户名"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">邮箱 <span class="text-red-500">*</span></label>
                <input 
                  v-model="userForm.email"
                  type="email" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入邮箱"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">电话</label>
                <input 
                  v-model="userForm.phone"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入电话"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">密码 <span class="text-red-500">*</span></label>
                <input 
                  v-model="userForm.password"
                  type="password" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入密码"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">状态 <span class="text-red-500">*</span></label>
                <select 
                  v-model="userForm.delete_flag"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                >
                  <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="createUser"
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
    
    <!-- 编辑用户模态框 -->
    <div v-if="showEditModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showEditModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">编辑用户</h3>
            <div class="mt-2">
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">用户名 <span class="text-red-500">*</span></label>
                <input 
                  v-model="userForm.user_name"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入用户名"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">邮箱 <span class="text-red-500">*</span></label>
                <input 
                  v-model="userForm.email"
                  type="email" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入邮箱"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">电话</label>
                <input 
                  v-model="userForm.phone"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入电话"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">状态 <span class="text-red-500">*</span></label>
                <select 
                  v-model="userForm.delete_flag"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                >
                  <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="updateUser"
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
    
    <!-- 修改密码模态框 -->
    <div v-if="showPasswordModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showPasswordModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">修改密码 - {{ currentUser?.user_name }}</h3>
            <div class="mt-2">
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">新密码 <span class="text-red-500">*</span></label>
                <input 
                  v-model="passwordForm.password"
                  type="password" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入新密码"
                />
              </div>
              <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">确认密码 <span class="text-red-500">*</span></label>
                <input 
                  v-model="passwordForm.confirmPassword"
                  type="password" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请再次输入新密码"
                />
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="updatePassword"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              确认
            </button>
            <button 
              @click="showPasswordModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 角色分配模态框 -->
    <div v-if="showRoleModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showRoleModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-3xl sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">角色分配 - {{ currentUser?.user_name }}</h3>
            <div class="mt-2">
              <UserRoleSelector 
                v-if="currentUser"
                :userId="currentUser.id"
                :username="currentUser.user_name"
                @update="handleUserUpdate"
              />
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="showRoleModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:w-auto sm:text-sm transition duration-150"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template> 