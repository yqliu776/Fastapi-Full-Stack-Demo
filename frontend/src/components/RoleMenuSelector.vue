<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { menuService } from '@/services/menuService';
import type { Menu } from '@/services/menuService';
import { roleService } from '@/services/roleService';
import type { RoleMenuOperation } from '@/services/roleService';
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
const allMenus = ref<Menu[]>([]);
const roleMenus = ref<Menu[]>([]);
const selectedMenus = ref<number[]>([]);
const expandedMenus = ref<number[]>([]);
const loading = ref({
  allMenus: false,
  roleMenus: false,
  submit: false
});
const searchKeyword = ref('');
const errorMsg = ref('');

// 计算属性 - 角色已有菜单的ID集合
const roleMenuIds = computed(() => {
  return roleMenus.value.map(m => m.id);
});

// 计算属性 - 菜单树结构
const menuTree = computed(() => {
  if (!allMenus.value.length) return [];

  // 如果有搜索关键字，以扁平结构返回所有包含关键字的菜单
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    return allMenus.value.filter(
      menu => menu.menu_name.toLowerCase().includes(keyword) || 
              menu.menu_code.toLowerCase().includes(keyword)
    );
  }

  // 否则构建树形结构
  const rootMenus = allMenus.value.filter(menu => !menu.parent_id);
  
  // 递归添加子菜单
  const addChildren = (menu: Menu): Menu => {
    const children = allMenus.value.filter(m => m.parent_id === menu.id);
    return {
      ...menu,
      children: children.length ? children.map(addChildren) : []
    };
  };
  
  return rootMenus.map(addChildren);
});

// 是否已选择菜单
const isMenuSelected = (menuId: number) => {
  return selectedMenus.value.includes(menuId);
};

// 是否角色已有该菜单
const hasRoleMenu = (menuId: number) => {
  return roleMenuIds.value.includes(menuId);
};

// 切换菜单展开状态
const toggleExpandMenu = (menuId: number) => {
  const index = expandedMenus.value.indexOf(menuId);
  if (index === -1) {
    expandedMenus.value.push(menuId);
  } else {
    expandedMenus.value.splice(index, 1);
  }
};

// 判断菜单是否展开
const isMenuExpanded = (menuId: number) => {
  return expandedMenus.value.includes(menuId);
};

// 切换选择菜单
const toggleSelectMenu = (menuId: number) => {
  const index = selectedMenus.value.indexOf(menuId);
  if (index === -1) {
    selectedMenus.value.push(menuId);
  } else {
    selectedMenus.value.splice(index, 1);
  }
};

// 全选
const selectAll = () => {
  selectedMenus.value = allMenus.value.map(m => m.id);
};

// 全不选
const deselectAll = () => {
  selectedMenus.value = [];
};

// 添加一个计算属性显示菜单统计
const menuStats = computed(() => {
  return {
    total: allMenus.value.length,
    assigned: roleMenus.value.length,
    selected: selectedMenus.value.length,
    toAssign: selectedMenus.value.filter(id => !roleMenuIds.value.includes(id)).length,
    toRemove: selectedMenus.value.filter(id => roleMenuIds.value.includes(id)).length
  };
});

// 获取用户ID或默认值
const getUserId = () => {
  return userStore.userInfo?.id.toString() || '-1';
};

// 初始化方法
const init = async () => {
  errorMsg.value = '';
  await Promise.all([
    loadAllMenus(),
    loadRoleMenus()
  ]);
};

// 加载所有菜单
const loadAllMenus = async () => {
  loading.value.allMenus = true;
  try {
    const response = await menuService.getMenus({ limit: 1000 });
    if (response.code === 200) {
      allMenus.value = response.data.items;
    } else {
      console.error('加载菜单列表失败:', response.message);
      errorMsg.value = '加载菜单列表失败: ' + response.message;
    }
  } catch (error) {
    console.error('加载菜单列表出错:', error);
    errorMsg.value = '加载菜单列表出错';
  } finally {
    loading.value.allMenus = false;
  }
};

// 加载角色拥有的菜单
const loadRoleMenus = async () => {
  if (!props.roleId) return;
  
  loading.value.roleMenus = true;
  try {
    // 获取角色详情，包含menus列表
    const roleResponse = await roleService.getRole(props.roleId);
    if (roleResponse.code === 200 && roleResponse.data.menus) {
      // 使用更具体的类型转换方式
      roleMenus.value = roleResponse.data.menus as unknown as Menu[];
    } else {
      // 如果角色详情中没有menus或获取失败，尝试使用菜单服务获取
      const response = await menuService.getRoleMenus(props.roleId);
      if (response.code === 200) {
        roleMenus.value = response.data.items;
      } else {
        console.error('加载角色菜单失败:', response.message);
        errorMsg.value = '加载角色菜单失败: ' + response.message;
      }
    }
  } catch (error) {
    console.error('加载角色菜单出错:', error);
    errorMsg.value = '加载角色菜单出错';
  } finally {
    loading.value.roleMenus = false;
  }
};

// 为角色分配菜单
const assignMenus = async () => {
  if (selectedMenus.value.length === 0) return;
  errorMsg.value = '';
  
  loading.value.submit = true;
  try {
    // 筛选出未分配给角色的菜单
    const menusToAssign = selectedMenus.value.filter(
      id => !roleMenuIds.value.includes(id)
    );
    
    if (menusToAssign.length === 0) {
      loading.value.submit = false;
      return;
    }
    
    const userId = getUserId();
    const operation: RoleMenuOperation = {
      menu_ids: menusToAssign,
      operator: userId,
      operation_login: userId,
      role_id: props.roleId
    };
    
    const response = await roleService.assignMenusToRole(props.roleId, operation);
    if (response.code === 200) {
      await loadRoleMenus();
      emit('update');
    } else {
      console.error('分配菜单失败:', response.message);
      errorMsg.value = '分配菜单失败: ' + response.message;
    }
  } catch (error) {
    console.error('分配菜单出错:', error);
    errorMsg.value = '分配菜单出错';
  } finally {
    loading.value.submit = false;
  }
};

// 移除角色菜单
const removeMenus = async () => {
  if (selectedMenus.value.length === 0) return;
  errorMsg.value = '';
  
  loading.value.submit = true;
  try {
    // 筛选出已分配给角色的菜单
    const menusToRemove = selectedMenus.value.filter(
      id => roleMenuIds.value.includes(id)
    );
    
    if (menusToRemove.length === 0) {
      loading.value.submit = false;
      return;
    }
    
    const userId = getUserId();
    const operation: RoleMenuOperation = {
      menu_ids: menusToRemove,
      operator: userId,
      operation_login: userId,
      role_id: props.roleId
    };
    
    const response = await roleService.removeMenusFromRole(props.roleId, operation);
    if (response.code === 200) {
      await loadRoleMenus();
      emit('update');
    } else {
      console.error('移除菜单失败:', response.message);
      errorMsg.value = '移除菜单失败: ' + response.message;
    }
  } catch (error) {
    console.error('移除菜单出错:', error);
    errorMsg.value = '移除菜单出错';
  } finally {
    loading.value.submit = false;
  }
};

// 监听visible变化
watch(() => props.visible, (newValue) => {
  if (newValue) {
    init();
  } else {
    selectedMenus.value = [];
    expandedMenus.value = [];
  }
});

// 监听roleId变化
watch(() => props.roleId, () => {
  if (props.visible) {
    loadRoleMenus();
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
  <div class="role-menu-selector">
    <!-- 顶部操作栏 -->
    <div class="mb-4 flex items-center justify-between">
      <div class="w-64">
        <input
          v-model="searchKeyword"
          type="text"
          class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          placeholder="搜索菜单名称或代码"
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

    <!-- 菜单信息统计 -->
    <div class="mb-3 p-2 bg-gray-50 rounded border border-gray-200 text-xs">
      <div class="flex flex-wrap gap-3">
        <div>总菜单数: <span class="font-semibold">{{ menuStats.total }}</span></div>
        <div>已分配: <span class="font-semibold text-green-600">{{ menuStats.assigned }}</span></div>
        <div>已选择: <span class="font-semibold text-blue-600">{{ menuStats.selected }}</span></div>
        <div v-if="menuStats.toAssign > 0">待分配: <span class="font-semibold text-indigo-600">{{ menuStats.toAssign }}</span></div>
        <div v-if="menuStats.toRemove > 0">待移除: <span class="font-semibold text-red-600">{{ menuStats.toRemove }}</span></div>
      </div>
    </div>
    
    <!-- 菜单标签图例 -->
    <div class="mb-3 flex items-center gap-3 text-xs">
      <div class="flex items-center">
        <div class="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
        <span>已分配菜单</span>
      </div>
      <div class="flex items-center">
        <div class="w-3 h-3 rounded-full bg-blue-500 mr-1"></div>
        <span>已选择待操作</span>
      </div>
      <div class="flex items-center">
        <div class="w-3 h-3 rounded border border-gray-300 mr-1 flex items-center justify-center text-xs leading-none">
          <span>+</span>
        </div>
        <span>展开子菜单</span>
      </div>
    </div>
    
    <!-- 菜单列表 -->
    <div class="max-h-60 overflow-y-auto border rounded-md p-2 mb-4">
      <div v-if="loading.allMenus || loading.roleMenus" class="text-center py-4">
        <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600 mr-2"></div>
        加载中...
      </div>
      <div v-else-if="menuTree.length === 0" class="text-center py-4 text-gray-500">
        暂无数据
      </div>
      <div v-else>
        <!-- 扁平结构显示搜索结果 -->
        <div v-if="searchKeyword" class="space-y-1">
          <div
            v-for="menu in menuTree"
            :key="menu.id"
            class="flex items-center p-2 rounded cursor-pointer transition-colors"
            :class="{
              'bg-blue-50 border border-blue-200': isMenuSelected(menu.id) && !hasRoleMenu(menu.id),
              'bg-green-50 border border-green-200': hasRoleMenu(menu.id) && !isMenuSelected(menu.id),
              'bg-gradient-to-r from-green-50 to-blue-50 border border-blue-200': hasRoleMenu(menu.id) && isMenuSelected(menu.id),
              'hover:bg-gray-100 border border-transparent': !isMenuSelected(menu.id) && !hasRoleMenu(menu.id)
            }"
            @click="toggleSelectMenu(menu.id)"
          >
            <input
              type="checkbox"
              :checked="isMenuSelected(menu.id)"
              class="mr-2 h-4 w-4 text-indigo-600 rounded"
              @click.stop
              @change="toggleSelectMenu(menu.id)"
            />
            <div class="flex-1 min-w-0">
              <div class="text-sm font-medium truncate">{{ menu.menu_name }}</div>
              <div class="text-xs text-gray-500 truncate">{{ menu.menu_code }}</div>
            </div>
            <div
              v-if="hasRoleMenu(menu.id)"
              class="flex-shrink-0 bg-green-100 text-green-800 text-xs py-0.5 px-2 rounded-full font-medium flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              已分配
            </div>
          </div>
        </div>
        
        <!-- 树结构显示所有菜单 -->
        <div v-else class="space-y-1">
          <template v-for="menu in menuTree" :key="menu.id">
            <div class="menu-item">
              <div 
                class="flex items-center p-2 rounded cursor-pointer transition-colors"
                :class="{
                  'bg-blue-50 border border-blue-200': isMenuSelected(menu.id) && !hasRoleMenu(menu.id),
                  'bg-green-50 border border-green-200': hasRoleMenu(menu.id) && !isMenuSelected(menu.id),
                  'bg-gradient-to-r from-green-50 to-blue-50 border border-blue-200': hasRoleMenu(menu.id) && isMenuSelected(menu.id),
                  'hover:bg-gray-100 border border-transparent': !isMenuSelected(menu.id) && !hasRoleMenu(menu.id)
                }"
                @click="toggleSelectMenu(menu.id)"
              >
                <button 
                  v-if="menu.children && menu.children.length > 0"
                  class="mr-1 w-5 h-5 flex items-center justify-center text-gray-500 border border-gray-300 rounded hover:bg-gray-200"
                  @click.stop="toggleExpandMenu(menu.id)"
                >
                  {{ isMenuExpanded(menu.id) ? '-' : '+' }}
                </button>
                <span v-else class="mr-1 w-5 h-5"></span>
                
                <input
                  type="checkbox"
                  :checked="isMenuSelected(menu.id)"
                  class="mr-2 h-4 w-4 text-indigo-600 rounded"
                  @click.stop
                  @change="toggleSelectMenu(menu.id)"
                />
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium truncate">{{ menu.menu_name }}</div>
                  <div class="text-xs text-gray-500 truncate">{{ menu.menu_code }}</div>
                </div>
                <div
                  v-if="hasRoleMenu(menu.id)"
                  class="flex-shrink-0 bg-green-100 text-green-800 text-xs py-0.5 px-2 rounded-full font-medium flex items-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  已分配
                </div>
              </div>
              
              <!-- 子菜单递归显示 -->
              <div v-if="menu.children && menu.children.length > 0 && isMenuExpanded(menu.id)" class="pl-6 mt-1 border-l-2 border-gray-200">
                <template v-for="child in menu.children" :key="child.id">
                  <div class="menu-item">
                    <div 
                      class="flex items-center p-2 rounded cursor-pointer transition-colors"
                      :class="{
                        'bg-blue-50 border border-blue-200': isMenuSelected(child.id) && !hasRoleMenu(child.id),
                        'bg-green-50 border border-green-200': hasRoleMenu(child.id) && !isMenuSelected(child.id),
                        'bg-gradient-to-r from-green-50 to-blue-50 border border-blue-200': hasRoleMenu(child.id) && isMenuSelected(child.id),
                        'hover:bg-gray-100 border border-transparent': !isMenuSelected(child.id) && !hasRoleMenu(child.id)
                      }"
                      @click="toggleSelectMenu(child.id)"
                    >
                      <button 
                        v-if="child.children && child.children.length > 0"
                        class="mr-1 w-5 h-5 flex items-center justify-center text-gray-500 border border-gray-300 rounded hover:bg-gray-200"
                        @click.stop="toggleExpandMenu(child.id)"
                      >
                        {{ isMenuExpanded(child.id) ? '-' : '+' }}
                      </button>
                      <span v-else class="mr-1 w-5 h-5"></span>
                      
                      <input
                        type="checkbox"
                        :checked="isMenuSelected(child.id)"
                        class="mr-2 h-4 w-4 text-indigo-600 rounded"
                        @click.stop
                        @change="toggleSelectMenu(child.id)"
                      />
                      <div class="flex-1 min-w-0">
                        <div class="text-sm font-medium truncate">{{ child.menu_name }}</div>
                        <div class="text-xs text-gray-500 truncate">{{ child.menu_code }}</div>
                      </div>
                      <div
                        v-if="hasRoleMenu(child.id)"
                        class="flex-shrink-0 bg-green-100 text-green-800 text-xs py-0.5 px-2 rounded-full font-medium flex items-center"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        已分配
                      </div>
                    </div>
                    
                    <!-- 三级菜单递归显示（可根据需求扩展更多层级） -->
                    <div v-if="child.children && child.children.length > 0 && isMenuExpanded(child.id)" class="pl-6 mt-1 border-l-2 border-gray-200">
                      <div 
                        v-for="grandchild in child.children" 
                        :key="grandchild.id"
                        class="flex items-center p-2 rounded cursor-pointer transition-colors"
                        :class="{
                          'bg-blue-50 border border-blue-200': isMenuSelected(grandchild.id) && !hasRoleMenu(grandchild.id),
                          'bg-green-50 border border-green-200': hasRoleMenu(grandchild.id) && !isMenuSelected(grandchild.id),
                          'bg-gradient-to-r from-green-50 to-blue-50 border border-blue-200': hasRoleMenu(grandchild.id) && isMenuSelected(grandchild.id),
                          'hover:bg-gray-100 border border-transparent': !isMenuSelected(grandchild.id) && !hasRoleMenu(grandchild.id)
                        }"
                        @click="toggleSelectMenu(grandchild.id)"
                      >
                        <span class="mr-1 w-5 h-5"></span>
                        <input
                          type="checkbox"
                          :checked="isMenuSelected(grandchild.id)"
                          class="mr-2 h-4 w-4 text-indigo-600 rounded"
                          @click.stop
                          @change="toggleSelectMenu(grandchild.id)"
                        />
                        <div class="flex-1 min-w-0">
                          <div class="text-sm font-medium truncate">{{ grandchild.menu_name }}</div>
                          <div class="text-xs text-gray-500 truncate">{{ grandchild.menu_code }}</div>
                        </div>
                        <div
                          v-if="hasRoleMenu(grandchild.id)"
                          class="flex-shrink-0 bg-green-100 text-green-800 text-xs py-0.5 px-2 rounded-full font-medium flex items-center"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                          </svg>
                          已分配
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
    
    <!-- 底部按钮 -->
    <div class="flex justify-between">
      <div>
        <span class="text-sm text-gray-500">已选择 {{ selectedMenus.length }} 项</span>
      </div>
      <div class="flex space-x-2">
        <button
          @click="assignMenus"
          :disabled="loading.submit || menuStats.toAssign === 0"
          class="bg-green-600 text-white py-1 px-3 rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="loading.submit && menuStats.toAssign > 0" class="inline-block animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></span>
          分配菜单 {{ menuStats.toAssign > 0 ? `(${menuStats.toAssign})` : '' }}
        </button>
        <button
          @click="removeMenus"
          :disabled="loading.submit || menuStats.toRemove === 0"
          class="bg-red-600 text-white py-1 px-3 rounded hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <span v-if="loading.submit && menuStats.toRemove > 0" class="inline-block animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1"></span>
          移除菜单 {{ menuStats.toRemove > 0 ? `(${menuStats.toRemove})` : '' }}
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

.menu-item {
  margin-bottom: 4px;
}
</style> 