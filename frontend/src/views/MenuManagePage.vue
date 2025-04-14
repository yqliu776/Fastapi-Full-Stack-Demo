<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { menuService } from '@/services/menuService';
import type { Menu, MenuCreate, MenuUpdate } from '@/services/menuService';
import { useUserStore } from '@/stores/user';

// 获取用户信息
const userStore = useUserStore();

// 状态
const menus = ref<Menu[]>([]);
const totalMenus = ref(0);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const searchForm = reactive({
  menu_name: ''
});

// 模态框状态
const showCreateModal = ref(false);
const showEditModal = ref(false);
const currentMenu = ref<Menu | null>(null);

// 父菜单选择相关
const parentMenus = ref<Menu[]>([]);

// 消息通知状态
const notification = reactive({
  show: false,
  message: '',
  type: 'success' // success, error, warning
});

// 表单数据
const menuForm = reactive<MenuCreate & MenuUpdate>({
  menu_name: '',
  menu_code: '',
  menu_path: '',
  parent_id: undefined,
  sort_order: 0,
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

// 加载菜单列表
const loadMenus = async () => {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * pageSize.value;
    const params = {
      skip,
      limit: pageSize.value,
      ...searchForm
    };
    const response = await menuService.getMenus(params);
    if (response.code === 200) {
      menus.value = response.data.items;
      totalMenus.value = response.data.total;
    } else {
      console.error('加载菜单列表失败:', response.message);
      showNotification('加载菜单列表失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('加载菜单列表出错:', error);
    showNotification('加载菜单列表出错', 'error');
  } finally {
    loading.value = false;
  }
};

// 加载所有菜单用于父菜单选择
const loadAllMenus = async () => {
  try {
    const response = await menuService.getMenus({ limit: 999 });
    if (response.code === 200) {
      parentMenus.value = response.data.items;
    } else {
      console.error('加载所有菜单失败:', response.message);
    }
  } catch (error) {
    console.error('加载所有菜单出错:', error);
  }
};

// 搜索菜单
const searchMenus = () => {
  currentPage.value = 1;
  loadMenus();
};

// 重置搜索
const resetSearch = () => {
  searchForm.menu_name = '';
  searchMenus();
};

// 打开创建菜单模态框
const openCreateModal = () => {
  // 使用当前用户ID或默认值
  const userId = userStore.userInfo?.id.toString() || '-1';
  
  menuForm.menu_name = '';
  menuForm.menu_code = '';
  menuForm.menu_path = '';
  menuForm.parent_id = undefined;
  menuForm.sort_order = 0;
  menuForm.created_by = userId;
  menuForm.last_updated_by = userId;
  menuForm.last_update_login = userId;
  
  showCreateModal.value = true;
};

// 创建菜单
const createMenu = async () => {
  try {
    const response = await menuService.createMenu(menuForm);
    if (response.code === 200) {
      showCreateModal.value = false;
      loadMenus();
      showNotification('菜单创建成功', 'success');
    } else {
      console.error('创建菜单失败:', response.message);
      showNotification('创建菜单失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('创建菜单出错:', error);
    showNotification('创建菜单出错', 'error');
  }
};

// 打开编辑菜单模态框
const openEditModal = (menu: Menu) => {
  currentMenu.value = menu;
  
  // 使用当前用户ID或默认值
  const userId = userStore.userInfo?.id.toString() || '-1';
  
  menuForm.menu_name = menu.menu_name;
  menuForm.menu_code = menu.menu_code;
  menuForm.menu_path = menu.menu_path;
  menuForm.parent_id = menu.parent_id;
  menuForm.sort_order = menu.sort_order;
  menuForm.last_updated_by = userId;
  menuForm.last_update_login = userId;
  
  showEditModal.value = true;
};

// 更新菜单
const updateMenu = async () => {
  if (!currentMenu.value) return;
  
  try {
    const response = await menuService.updateMenu(currentMenu.value.id, menuForm);
    if (response.code === 200) {
      showEditModal.value = false;
      loadMenus();
      showNotification('菜单更新成功', 'success');
    } else {
      console.error('更新菜单失败:', response.message);
      showNotification('更新菜单失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('更新菜单出错:', error);
    showNotification('更新菜单出错', 'error');
  }
};

// 删除菜单
const deleteMenu = async (menu: Menu) => {
  if (!confirm(`确定要删除菜单"${menu.menu_name}"吗？这将同时删除其所有子菜单！`)) return;
  
  try {
    const response = await menuService.deleteMenu(menu.id);
    if (response.code === 200) {
      loadMenus();
      showNotification('菜单删除成功', 'success');
    } else {
      console.error('删除菜单失败:', response.message);
      showNotification('删除菜单失败: ' + response.message, 'error');
    }
  } catch (error) {
    console.error('删除菜单出错:', error);
    showNotification('删除菜单出错', 'error');
  }
};

// 获取父菜单名称
const getParentMenuName = (parentId?: number) => {
  if (!parentId) return '无';
  const parent = parentMenus.value.find(m => m.id === parentId);
  return parent ? parent.menu_name : `未知(ID:${parentId})`;
};

// 页面变化处理
const handlePageChange = (page: number) => {
  currentPage.value = page;
  loadMenus();
};

// 初始化
onMounted(() => {
  loadMenus();
  loadAllMenus();
});
</script>

<template>
  <div>
    <h1 class="text-2xl font-semibold text-gray-900 mb-6">菜单管理</h1>
    
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
          <label class="block text-sm font-medium text-gray-700 mb-1">菜单名称</label>
          <input 
            v-model="searchForm.menu_name"
            type="text" 
            class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            placeholder="请输入菜单名称"
          />
        </div>
        <div class="flex gap-2">
          <button 
            @click="searchMenus"
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
            创建菜单
          </button>
        </div>
      </div>
    </div>
    
    <!-- 菜单列表 -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">菜单名称</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">菜单代码</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">菜单路径</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">父菜单</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">排序</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">创建时间</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="loading" class="text-center">
              <td colspan="8" class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500 text-center w-full">加载中...</div>
              </td>
            </tr>
            <tr v-else-if="menus.length === 0" class="text-center">
              <td colspan="8" class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500 text-center w-full">暂无菜单数据</div>
              </td>
            </tr>
            <tr v-for="menu in menus" :key="menu.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ menu.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ menu.menu_name }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ menu.menu_code }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ menu.menu_path }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ getParentMenuName(menu.parent_id) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500">{{ menu.sort_order }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ new Date(menu.creation_date).toLocaleString() }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div class="flex gap-2">
                  <button 
                    @click="openEditModal(menu)" 
                    class="text-indigo-600 hover:text-indigo-900 transition duration-150"
                  >
                    编辑
                  </button>
                  <button 
                    @click="deleteMenu(menu)" 
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
              <span class="font-medium">{{ Math.min(currentPage * pageSize, totalMenus) }}</span>
              条，共
              <span class="font-medium">{{ totalMenus }}</span>
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
                :disabled="currentPage * pageSize >= totalMenus"
                :class="[
                  'relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium',
                  currentPage * pageSize >= totalMenus 
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
    
    <!-- 创建菜单模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showCreateModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
              创建菜单
            </h3>
            <div class="mt-2">
              <div class="mb-4">
                <label for="menu_name" class="block text-sm font-medium text-gray-700 mb-1">菜单名称</label>
                <input 
                  id="menu_name"
                  v-model="menuForm.menu_name"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入菜单名称"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="menu_code" class="block text-sm font-medium text-gray-700 mb-1">菜单代码</label>
                <input 
                  id="menu_code"
                  v-model="menuForm.menu_code"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入菜单代码"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="menu_path" class="block text-sm font-medium text-gray-700 mb-1">菜单路径</label>
                <input 
                  id="menu_path"
                  v-model="menuForm.menu_path"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入菜单路径"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="parent_id" class="block text-sm font-medium text-gray-700 mb-1">父菜单</label>
                <select 
                  id="parent_id"
                  v-model="menuForm.parent_id"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                >
                  <option :value="undefined">无 (作为顶级菜单)</option>
                  <option v-for="menu in parentMenus" :key="menu.id" :value="menu.id">
                    {{ menu.menu_name }} ({{ menu.menu_code }})
                  </option>
                </select>
              </div>
              <div class="mb-4">
                <label for="sort_order" class="block text-sm font-medium text-gray-700 mb-1">排序号</label>
                <input 
                  id="sort_order"
                  v-model="menuForm.sort_order"
                  type="number" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入排序号"
                  min="0"
                />
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="createMenu"
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
    
    <!-- 编辑菜单模态框 -->
    <div v-if="showEditModal" class="fixed inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- 背景遮罩 -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="showEditModal = false"></div>
        
        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
              编辑菜单
            </h3>
            <div class="mt-2">
              <div class="mb-4">
                <label for="edit_menu_name" class="block text-sm font-medium text-gray-700 mb-1">菜单名称</label>
                <input 
                  id="edit_menu_name"
                  v-model="menuForm.menu_name"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入菜单名称"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="edit_menu_code" class="block text-sm font-medium text-gray-700 mb-1">菜单代码</label>
                <input 
                  id="edit_menu_code"
                  v-model="menuForm.menu_code"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入菜单代码"
                  disabled
                />
                <p class="mt-1 text-xs text-gray-500">菜单代码不可修改</p>
              </div>
              <div class="mb-4">
                <label for="edit_menu_path" class="block text-sm font-medium text-gray-700 mb-1">菜单路径</label>
                <input 
                  id="edit_menu_path"
                  v-model="menuForm.menu_path"
                  type="text" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入菜单路径"
                  required
                />
              </div>
              <div class="mb-4">
                <label for="edit_parent_id" class="block text-sm font-medium text-gray-700 mb-1">父菜单</label>
                <select 
                  id="edit_parent_id"
                  v-model="menuForm.parent_id"
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                >
                  <option :value="undefined">无 (作为顶级菜单)</option>
                  <option 
                    v-for="menu in parentMenus.filter(m => m.id !== currentMenu?.id)" 
                    :key="menu.id" 
                    :value="menu.id"
                  >
                    {{ menu.menu_name }} ({{ menu.menu_code }})
                  </option>
                </select>
                <p class="mt-1 text-xs text-gray-500">菜单不能选择自己作为父菜单</p>
              </div>
              <div class="mb-4">
                <label for="edit_sort_order" class="block text-sm font-medium text-gray-700 mb-1">排序号</label>
                <input 
                  id="edit_sort_order"
                  v-model="menuForm.sort_order"
                  type="number" 
                  class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="请输入排序号"
                  min="0"
                />
              </div>
            </div>
          </div>
          <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="updateMenu"
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