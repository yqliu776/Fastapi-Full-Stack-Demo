<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { permissionService } from '@/services/permissionService';
import type {
  ApiPermission,
  ApiPermissionCreate,
  Permission,
  PermissionCreate,
  PermissionUpdate
} from '@/services/permissionService';
import { useUserStore } from '@/stores/user';
import { handleComponentError } from '@/utils/errorHandlers';

// 获取用户信息
const userStore = useUserStore();

// 状态
const permissions = ref<Permission[]>([]);
const permissionOptions = ref<Permission[]>([]);
const totalPermissions = ref(0);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const searchForm = reactive({
  permission_name: '',
  permission_code: ''
});
const apiPermissions = ref<ApiPermission[]>([]);
const totalApiPermissions = ref(0);
const apiLoading = ref(false);
const currentApiPage = ref(1);
const apiPageSize = ref(10);
const apiSearchForm = reactive({
  method: '',
  path_pattern: '',
  permission_code: ''
});
const methodOptions = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

// 模态框状态
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showCreateApiModal = ref(false);
const showEditApiModal = ref(false);
const currentPermission = ref<Permission | null>(null);
const currentApiPermission = ref<ApiPermission | null>(null);

// 消息通知状态
const notification = reactive({
  show: false,
  message: '',
  type: 'success' // success, error, warning
});

// 表单数据
const permissionForm = reactive<PermissionCreate & PermissionUpdate>({
  permission_name: '',
  permission_code: '',
  created_by: '-1',
  last_updated_by: '-1',
  last_update_login: '-1'
});
const apiPermissionForm = reactive<ApiPermissionCreate>({
  method: 'GET',
  path_pattern: '',
  permission_code: '',
  description: '',
  enabled: true,
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

// 加载权限列表
const loadPermissions = async () => {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * pageSize.value;
    const params = {
      skip,
      limit: pageSize.value,
      ...searchForm
    };
    const response = await permissionService.getPermissions(params);
    if (response.code === 200) {
      permissions.value = response.data.items;
      totalPermissions.value = response.data.total;
    } else {
      console.error('加载权限列表失败:', response.message);
      showNotification('加载权限列表失败: ' + response.message, 'error');
    }
  } catch (error: any) {
    const errorMessage = handleComponentError(error, '加载权限列表出错');
    showNotification(errorMessage, 'error');
  } finally {
    loading.value = false;
  }
};

const loadPermissionOptions = async () => {
  try {
    const response = await permissionService.getPermissions({ skip: 0, limit: 1000 });
    if (response.code === 200) {
      permissionOptions.value = response.data.items;
    }
  } catch (error) {
    console.error('加载权限选项失败:', error);
  }
};

const loadApiPermissions = async () => {
  apiLoading.value = true;
  try {
    const skip = (currentApiPage.value - 1) * apiPageSize.value;
    const params = {
      skip,
      limit: apiPageSize.value,
      ...apiSearchForm
    };
    const response = await permissionService.getApiPermissions(params);
    if (response.code === 200) {
      apiPermissions.value = response.data.items;
      totalApiPermissions.value = response.data.total;
    } else {
      showNotification('加载API权限绑定失败: ' + response.message, 'error');
    }
  } catch (error: any) {
    const errorMessage = handleComponentError(error, '加载API权限绑定出错');
    showNotification(errorMessage, 'error');
  } finally {
    apiLoading.value = false;
  }
};

// 搜索权限
const searchPermissions = () => {
  currentPage.value = 1;
  loadPermissions();
};

// 重置搜索
const resetSearch = () => {
  searchForm.permission_name = '';
  searchForm.permission_code = '';
  searchPermissions();
};

const searchApiPermissions = () => {
  currentApiPage.value = 1;
  loadApiPermissions();
};

const resetApiSearch = () => {
  apiSearchForm.method = '';
  apiSearchForm.path_pattern = '';
  apiSearchForm.permission_code = '';
  searchApiPermissions();
};

// 打开创建权限模态框
const openCreateModal = () => {
  // 使用当前用户ID或默认值
  const userId = userStore.userInfo?.id.toString() || '-1';
  
  permissionForm.permission_name = '';
  permissionForm.permission_code = '';
  permissionForm.created_by = userId;
  permissionForm.last_updated_by = userId;
  permissionForm.last_update_login = userId;
  
  showCreateModal.value = true;
};

const resetApiPermissionForm = () => {
  const userId = userStore.userInfo?.id.toString() || '-1';

  apiPermissionForm.method = 'GET';
  apiPermissionForm.path_pattern = '';
  apiPermissionForm.permission_code = permissionOptions.value[0]?.permission_code || '';
  apiPermissionForm.description = '';
  apiPermissionForm.enabled = true;
  apiPermissionForm.created_by = userId;
  apiPermissionForm.last_updated_by = userId;
  apiPermissionForm.last_update_login = userId;
};

const openCreateApiModal = () => {
  resetApiPermissionForm();
  showCreateApiModal.value = true;
};

// 创建权限
const createPermission = async () => {
  try {
    const response = await permissionService.createPermission(permissionForm);
    if (response.code === 200) {
      showCreateModal.value = false;
      loadPermissions();
      showNotification('权限创建成功', 'success');
    } else {
      console.error('创建权限失败:', response.message);
      showNotification('创建权限失败: ' + response.message, 'error');
    }
  } catch (error: any) {
    const errorMessage = handleComponentError(error, '创建权限出错');
    showNotification(errorMessage, 'error');
  }
};

// 打开编辑权限模态框
const openEditModal = (permission: Permission) => {
  currentPermission.value = permission;
  
  // 使用当前用户ID或默认值
  const userId = userStore.userInfo?.id.toString() || '-1';
  
  permissionForm.permission_name = permission.permission_name;
  permissionForm.permission_code = permission.permission_code;
  permissionForm.last_updated_by = userId;
  permissionForm.last_update_login = userId;
  
  showEditModal.value = true;
};

// 更新权限
const updatePermission = async () => {
  if (!currentPermission.value) return;
  
  try {
    const response = await permissionService.updatePermission(currentPermission.value.id, permissionForm);
    if (response.code === 200) {
      showEditModal.value = false;
      loadPermissions();
      showNotification('权限更新成功', 'success');
    } else {
      console.error('更新权限失败:', response.message);
      showNotification('更新权限失败: ' + response.message, 'error');
    }
  } catch (error: any) {
    const errorMessage = handleComponentError(error, '更新权限出错');
    showNotification(errorMessage, 'error');
  }
};

// 删除权限
const deletePermission = async (permission: Permission) => {
  if (!confirm(`确定要删除权限"${permission.permission_name}"吗？`)) return;
  
  try {
    const response = await permissionService.deletePermission(permission.id);
    if (response.code === 200) {
      loadPermissions();
      showNotification('权限删除成功', 'success');
    } else {
      console.error('删除权限失败:', response.message);
      showNotification('删除权限失败: ' + response.message, 'error');
    }
  } catch (error: any) {
    const errorMessage = handleComponentError(error, '删除权限出错');
    showNotification(errorMessage, 'error');
  }
};

const createApiPermission = async () => {
  try {
    const response = await permissionService.createApiPermission(apiPermissionForm);
    if (response.code === 200) {
      showCreateApiModal.value = false;
      loadApiPermissions();
      showNotification('API权限绑定创建成功', 'success');
    } else {
      showNotification('API权限绑定创建失败: ' + response.message, 'error');
    }
  } catch (error: any) {
    const errorMessage = handleComponentError(error, 'API权限绑定创建出错');
    showNotification(errorMessage, 'error');
  }
};

const openEditApiModal = (apiPermission: ApiPermission) => {
  currentApiPermission.value = apiPermission;
  const userId = userStore.userInfo?.id.toString() || '-1';

  apiPermissionForm.method = apiPermission.method;
  apiPermissionForm.path_pattern = apiPermission.path_pattern;
  apiPermissionForm.permission_code = apiPermission.permission_code;
  apiPermissionForm.description = apiPermission.description || '';
  apiPermissionForm.enabled = apiPermission.enabled;
  apiPermissionForm.last_updated_by = userId;
  apiPermissionForm.last_update_login = userId;

  showEditApiModal.value = true;
};

const updateApiPermission = async () => {
  if (!currentApiPermission.value) return;

  try {
    const response = await permissionService.updateApiPermission(currentApiPermission.value.id, {
      method: apiPermissionForm.method,
      path_pattern: apiPermissionForm.path_pattern,
      permission_code: apiPermissionForm.permission_code,
      description: apiPermissionForm.description,
      enabled: apiPermissionForm.enabled,
      last_updated_by: apiPermissionForm.last_updated_by,
      last_update_login: apiPermissionForm.last_update_login
    });
    if (response.code === 200) {
      showEditApiModal.value = false;
      loadApiPermissions();
      showNotification('API权限绑定更新成功', 'success');
    } else {
      showNotification('API权限绑定更新失败: ' + response.message, 'error');
    }
  } catch (error: any) {
    const errorMessage = handleComponentError(error, 'API权限绑定更新出错');
    showNotification(errorMessage, 'error');
  }
};

const deleteApiPermission = async (apiPermission: ApiPermission) => {
  if (!confirm(`确定要删除API权限绑定"${apiPermission.method} ${apiPermission.path_pattern}"吗？`)) return;

  try {
    const response = await permissionService.deleteApiPermission(apiPermission.id);
    if (response.code === 200) {
      loadApiPermissions();
      showNotification('API权限绑定删除成功', 'success');
    } else {
      showNotification('API权限绑定删除失败: ' + response.message, 'error');
    }
  } catch (error: any) {
    const errorMessage = handleComponentError(error, 'API权限绑定删除出错');
    showNotification(errorMessage, 'error');
  }
};

// 页面变化处理
const handlePageChange = (page: number) => {
  currentPage.value = page;
  loadPermissions();
};

const handleApiPageChange = (page: number) => {
  currentApiPage.value = page;
  loadApiPermissions();
};

// 初始化
onMounted(() => {
  loadPermissions();
  loadPermissionOptions();
  loadApiPermissions();
});
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-gray-900 mb-6">权限管理</h1>
    
    <!-- 消息通知 -->
    <transition name="fade">
      <div 
        v-if="notification.show" 
        :class="[
          'fixed top-4 right-4 z-50 py-2 px-4 rounded shadow-lg transition-opacity',
          notification.type === 'success' ? 'bg-green-500 text-white' : 
          notification.type === 'error' ? 'bg-red-500 text-white' : 'bg-yellow-500 text-white'
        ]"
      >
        {{ notification.message }}
      </div>
    </transition>
    
    <!-- 搜索表单 -->
    <div class="bg-white p-4 rounded shadow mb-4">
      <div class="flex flex-wrap gap-4 items-end">
        <div class="w-full md:w-auto">
          <label class="block text-sm font-medium text-gray-700 mb-1">权限名称</label>
          <input 
            v-model="searchForm.permission_name"
            type="text" 
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="请输入权限名称"
          />
        </div>
        <div class="w-full md:w-auto">
          <label class="block text-sm font-medium text-gray-700 mb-1">权限代码</label>
          <input 
            v-model="searchForm.permission_code"
            type="text" 
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="请输入权限代码"
          />
        </div>
        <div class="flex gap-2">
          <button 
            @click="searchPermissions"
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
            创建权限
          </button>
        </div>
      </div>
    </div>
    
    <!-- 权限列表 -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">权限名称</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">权限代码</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">最后更新</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="loading" class="text-center">
              <td colspan="6" class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500 text-center w-full">加载中...</div>
              </td>
            </tr>
            <tr v-else-if="permissions.length === 0" class="text-center">
              <td colspan="6" class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500 text-center w-full">暂无权限数据</div>
              </td>
            </tr>
            <tr v-for="permission in permissions" :key="permission.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ permission.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ permission.permission_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ permission.permission_code }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ new Date(permission.creation_date).toLocaleString() }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ new Date(permission.last_update_date).toLocaleString() }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex gap-2">
                  <button 
                    @click="openEditModal(permission)" 
                    class="text-indigo-600 hover:text-indigo-900 transition duration-150"
                  >
                    编辑
                  </button>
                  <button 
                    @click="deletePermission(permission)" 
                    class="text-red-600 hover:text-red-900 transition duration-150"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页 -->
      <div class="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              显示 
              <span class="font-medium">{{ (currentPage - 1) * pageSize + 1 }}</span>
              至
              <span class="font-medium">{{ Math.min(currentPage * pageSize, totalPermissions) }}</span>
              条，共
              <span class="font-medium">{{ totalPermissions }}</span>
              条记录
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button
                @click="handlePageChange(currentPage - 1)"
                :disabled="currentPage === 1"
                :class="[
                  'relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium',
                  currentPage === 1 
                    ? 'text-gray-300 cursor-not-allowed' 
                    : 'text-gray-500 hover:bg-gray-50 cursor-pointer'
                ]"
              >
                上一页
              </button>
              <button
                @click="handlePageChange(currentPage + 1)"
                :disabled="currentPage * pageSize >= totalPermissions"
                :class="[
                  'relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium',
                  currentPage * pageSize >= totalPermissions 
                    ? 'text-gray-300 cursor-not-allowed' 
                    : 'text-gray-500 hover:bg-gray-50 cursor-pointer'
                ]"
              >
                下一页
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-4">API权限绑定</h2>

      <div class="bg-white p-4 rounded shadow mb-4">
        <div class="flex flex-wrap gap-4 items-end">
          <div class="w-full md:w-auto">
            <label class="block text-sm font-medium text-gray-700 mb-1">HTTP方法</label>
            <select
              v-model="apiSearchForm.method"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="">全部</option>
              <option v-for="method in methodOptions" :key="method" :value="method">{{ method }}</option>
            </select>
          </div>
          <div class="w-full md:w-auto">
            <label class="block text-sm font-medium text-gray-700 mb-1">API路径</label>
            <input
              v-model="apiSearchForm.path_pattern"
              type="text"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="/roles/{role_id}"
            />
          </div>
          <div class="w-full md:w-auto">
            <label class="block text-sm font-medium text-gray-700 mb-1">权限代码</label>
            <input
              v-model="apiSearchForm.permission_code"
              type="text"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="PERMISSION_MANAGE"
            />
          </div>
          <div class="flex gap-2">
            <button
              @click="searchApiPermissions"
              class="bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition duration-150"
            >
              搜索
            </button>
            <button
              @click="resetApiSearch"
              class="bg-gray-100 text-gray-700 py-2 px-4 rounded hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition duration-150"
            >
              重置
            </button>
            <button
              @click="openCreateApiModal"
              class="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition duration-150"
            >
              创建绑定
            </button>
          </div>
        </div>
      </div>

      <div class="bg-white shadow rounded-lg overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">方法</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">API路径</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">权限代码</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">说明</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-if="apiLoading" class="text-center">
                <td colspan="7" class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-500 text-center w-full">加载中...</div>
                </td>
              </tr>
              <tr v-else-if="apiPermissions.length === 0" class="text-center">
                <td colspan="7" class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-500 text-center w-full">暂无API权限绑定</div>
                </td>
              </tr>
              <tr v-for="apiPermission in apiPermissions" :key="apiPermission.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ apiPermission.id }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center rounded px-2 py-1 text-xs font-medium bg-gray-100 text-gray-700">
                    {{ apiPermission.method }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ apiPermission.path_pattern }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ apiPermission.permission_code }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'inline-flex items-center rounded px-2 py-1 text-xs font-medium',
                      apiPermission.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                    ]"
                  >
                    {{ apiPermission.enabled ? '启用' : '停用' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ apiPermission.description || '-' }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <div class="flex gap-2">
                    <button
                      @click="openEditApiModal(apiPermission)"
                      class="text-indigo-600 hover:text-indigo-900 transition duration-150"
                    >
                      编辑
                    </button>
                    <button
                      @click="deleteApiPermission(apiPermission)"
                      class="text-red-600 hover:text-red-900 transition duration-150"
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                显示
                <span class="font-medium">{{ totalApiPermissions === 0 ? 0 : (currentApiPage - 1) * apiPageSize + 1 }}</span>
                至
                <span class="font-medium">{{ Math.min(currentApiPage * apiPageSize, totalApiPermissions) }}</span>
                条，共
                <span class="font-medium">{{ totalApiPermissions }}</span>
                条记录
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  @click="handleApiPageChange(currentApiPage - 1)"
                  :disabled="currentApiPage === 1"
                  :class="[
                    'relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium',
                    currentApiPage === 1
                      ? 'text-gray-300 cursor-not-allowed'
                      : 'text-gray-500 hover:bg-gray-50 cursor-pointer'
                  ]"
                >
                  上一页
                </button>
                <button
                  @click="handleApiPageChange(currentApiPage + 1)"
                  :disabled="currentApiPage * apiPageSize >= totalApiPermissions"
                  :class="[
                    'relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium',
                    currentApiPage * apiPageSize >= totalApiPermissions
                      ? 'text-gray-300 cursor-not-allowed'
                      : 'text-gray-500 hover:bg-gray-50 cursor-pointer'
                  ]"
                >
                  下一页
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 创建权限模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showCreateModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
              创建权限
            </h3>
            <div class="mt-2">
              <div class="mb-4">
                <label for="permission_name" class="block text-sm font-medium text-gray-700 mb-1">权限名称</label>
                <input 
                  id="permission_name"
                  v-model="permissionForm.permission_name"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入权限名称"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="permission_code" class="block text-sm font-medium text-gray-700 mb-1">权限代码</label>
                <input 
                  id="permission_code"
                  v-model="permissionForm.permission_code"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入权限代码"
                  required
                />
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="createPermission"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              创建
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
    
    <!-- 编辑权限模态框 -->
    <div v-if="showEditModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showEditModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
              编辑权限
            </h3>
            <div class="mt-2">
              <div class="mb-4">
                <label for="edit_permission_name" class="block text-sm font-medium text-gray-700 mb-1">权限名称</label>
                <input 
                  id="edit_permission_name"
                  v-model="permissionForm.permission_name"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入权限名称"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="edit_permission_code" class="block text-sm font-medium text-gray-700 mb-1">权限代码</label>
                <input 
                  id="edit_permission_code"
                  v-model="permissionForm.permission_code"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入权限代码"
                  required
                  disabled
                />
                <p class="mt-1 text-xs text-gray-500">权限代码不可修改</p>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="updatePermission"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              更新
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

    <div v-if="showCreateApiModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showCreateApiModal = false"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
              创建API权限绑定
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="api_method" class="block text-sm font-medium text-gray-700 mb-1">HTTP方法</label>
                <select
                  id="api_method"
                  v-model="apiPermissionForm.method"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                >
                  <option v-for="method in methodOptions" :key="method" :value="method">{{ method }}</option>
                </select>
              </div>
              <div>
                <label for="api_permission_code" class="block text-sm font-medium text-gray-700 mb-1">权限代码</label>
                <select
                  id="api_permission_code"
                  v-model="apiPermissionForm.permission_code"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                >
                  <option value="" disabled>请选择权限代码</option>
                  <option
                    v-for="permission in permissionOptions"
                    :key="permission.id"
                    :value="permission.permission_code"
                  >
                    {{ permission.permission_code }} - {{ permission.permission_name }}
                  </option>
                </select>
              </div>
              <div class="md:col-span-2">
                <label for="api_path_pattern" class="block text-sm font-medium text-gray-700 mb-1">API路径</label>
                <input
                  id="api_path_pattern"
                  v-model="apiPermissionForm.path_pattern"
                  type="text"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="/roles/{role_id}"
                  required
                />
              </div>
              <div class="md:col-span-2">
                <label for="api_description" class="block text-sm font-medium text-gray-700 mb-1">说明</label>
                <input
                  id="api_description"
                  v-model="apiPermissionForm.description"
                  type="text"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入说明"
                />
              </div>
              <label class="inline-flex items-center gap-2 text-sm text-gray-700">
                <input
                  v-model="apiPermissionForm.enabled"
                  type="checkbox"
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                启用
              </label>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="createApiPermission"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              创建
            </button>
            <button
              @click="showCreateApiModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showEditApiModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showEditApiModal = false"></div>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
              编辑API权限绑定
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="edit_api_method" class="block text-sm font-medium text-gray-700 mb-1">HTTP方法</label>
                <select
                  id="edit_api_method"
                  v-model="apiPermissionForm.method"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                >
                  <option v-for="method in methodOptions" :key="method" :value="method">{{ method }}</option>
                </select>
              </div>
              <div>
                <label for="edit_api_permission_code" class="block text-sm font-medium text-gray-700 mb-1">权限代码</label>
                <select
                  id="edit_api_permission_code"
                  v-model="apiPermissionForm.permission_code"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  required
                >
                  <option
                    v-for="permission in permissionOptions"
                    :key="permission.id"
                    :value="permission.permission_code"
                  >
                    {{ permission.permission_code }} - {{ permission.permission_name }}
                  </option>
                </select>
              </div>
              <div class="md:col-span-2">
                <label for="edit_api_path_pattern" class="block text-sm font-medium text-gray-700 mb-1">API路径</label>
                <input
                  id="edit_api_path_pattern"
                  v-model="apiPermissionForm.path_pattern"
                  type="text"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="/roles/{role_id}"
                  required
                />
              </div>
              <div class="md:col-span-2">
                <label for="edit_api_description" class="block text-sm font-medium text-gray-700 mb-1">说明</label>
                <input
                  id="edit_api_description"
                  v-model="apiPermissionForm.description"
                  type="text"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入说明"
                />
              </div>
              <label class="inline-flex items-center gap-2 text-sm text-gray-700">
                <input
                  v-model="apiPermissionForm.enabled"
                  type="checkbox"
                  class="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                启用
              </label>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="updateApiPermission"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              更新
            </button>
            <button
              @click="showEditApiModal = false"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition duration-150"
            >
              取消
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
