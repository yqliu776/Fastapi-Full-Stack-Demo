<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { menuService } from '@/services/menuService';
import type { Menu, MenuCreate, MenuUpdate } from '@/services/menuService';
import { useUserStore } from '@/stores/user';

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
const componentOptions = [
  { key: '', label: '自动匹配' },
  { key: 'dashboard', label: 'dashboard - 仪表盘/系统父级' },
  { key: 'profile', label: 'profile - 个人中心' },
  { key: 'user', label: 'user - 用户管理' },
  { key: 'role', label: 'role - 角色管理' },
  { key: 'permission', label: 'permission - 权限管理' },
  { key: 'menu', label: 'menu - 菜单管理' },
  { key: 'rate_limit', label: 'rate_limit - API限流管理' },
  { key: 'swagger', label: 'swagger - API文档' },
  { key: 'unsupported', label: 'unsupported - 未绑定页面' }
];

// 模态框状态
const showCreateModal = ref(false);
const showEditModal = ref(false);
const currentMenu = ref<Menu | null>(null);

// 父菜单选择相关
const parentMenus = ref<Menu[]>([]);

// 表单数据
const menuForm = reactive<MenuCreate & MenuUpdate>({
  menu_name: '',
  menu_code: '',
  menu_path: '',
  component_key: '',
  parent_id: undefined,
  sort_order: 0,
  created_by: '-1',
  last_updated_by: '-1',
  last_update_login: '-1'
});

const selectedParentMenu = computed(() => {
  if (!menuForm.parent_id) return null;
  return parentMenus.value.find(menu => menu.id === menuForm.parent_id) || null;
});

const menuPathError = computed(() => {
  if (!menuForm.menu_path) return '菜单路径不能为空';
  if (!menuForm.menu_path.startsWith('/')) return '菜单路径必须以 / 开头';
  if (/\s/.test(menuForm.menu_path)) return '菜单路径不能包含空格';
  if (!menuForm.menu_path.startsWith('/system') && !menuForm.menu_path.startsWith('/dashboard')) {
    return '菜单路径需位于 /system 或 /dashboard 下';
  }
  return '';
});

const parentChildPreview = computed(() => {
  const parentName = selectedParentMenu.value ? selectedParentMenu.value.menu_name : '顶级菜单';
  const currentName = menuForm.menu_name || '当前菜单';
  return `${parentName} / ${currentName}`;
});

const normalizeMenuPayload = () => ({
  ...menuForm,
  component_key: menuForm.component_key || undefined
});

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
      ElMessage.error('加载菜单列表失败: ' + response.message);
    }
  } catch (error) {
    console.error('加载菜单列表出错:', error);
    ElMessage.error('加载菜单列表出错');
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
  const userId = userStore.userInfo?.id.toString() || '-1';

  menuForm.menu_name = '';
  menuForm.menu_code = '';
  menuForm.menu_path = '';
  menuForm.component_key = '';
  menuForm.parent_id = undefined;
  menuForm.sort_order = 0;
  menuForm.created_by = userId;
  menuForm.last_updated_by = userId;
  menuForm.last_update_login = userId;

  showCreateModal.value = true;
};

// 创建菜单
const createMenu = async () => {
  if (menuPathError.value) {
    ElMessage.warning(menuPathError.value);
    return;
  }
  try {
    const response = await menuService.createMenu(normalizeMenuPayload());
    if (response.code === 200) {
      showCreateModal.value = false;
      loadMenus();
      loadAllMenus();
      ElMessage.success('菜单创建成功');
    } else {
      ElMessage.error('创建菜单失败: ' + response.message);
    }
  } catch (error) {
    console.error('创建菜单出错:', error);
    ElMessage.error('创建菜单出错');
  }
};

// 打开编辑菜单模态框
const openEditModal = (menu: Menu) => {
  currentMenu.value = menu;

  const userId = userStore.userInfo?.id.toString() || '-1';

  menuForm.menu_name = menu.menu_name;
  menuForm.menu_code = menu.menu_code;
  menuForm.menu_path = menu.menu_path;
  menuForm.component_key = menu.component_key || '';
  menuForm.parent_id = menu.parent_id;
  menuForm.sort_order = menu.sort_order;
  menuForm.last_updated_by = userId;
  menuForm.last_update_login = userId;

  showEditModal.value = true;
};

// 更新菜单
const updateMenu = async () => {
  if (!currentMenu.value) return;
  if (menuPathError.value) {
    ElMessage.warning(menuPathError.value);
    return;
  }

  try {
    const response = await menuService.updateMenu(currentMenu.value.id, normalizeMenuPayload());
    if (response.code === 200) {
      showEditModal.value = false;
      loadMenus();
      loadAllMenus();
      ElMessage.success('菜单更新成功');
    } else {
      ElMessage.error('更新菜单失败: ' + response.message);
    }
  } catch (error) {
    console.error('更新菜单出错:', error);
    ElMessage.error('更新菜单出错');
  }
};

// 删除菜单
const deleteMenu = async (menu: Menu) => {
  try {
    await ElMessageBox.confirm(`确定要删除菜单"${menu.menu_name}"吗？这将同时删除其所有子菜单！`, '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    });
  } catch {
    return;
  }

  try {
    const response = await menuService.deleteMenu(menu.id);
    if (response.code === 200) {
      loadMenus();
      loadAllMenus();
      ElMessage.success('菜单删除成功');
    } else {
      ElMessage.error('删除菜单失败: ' + response.message);
    }
  } catch (error) {
    console.error('删除菜单出错:', error);
    ElMessage.error('删除菜单出错');
  }
};

// 获取父菜单名称
const getParentMenuName = (parentId?: number) => {
  if (!parentId) return '无';
  const parent = parentMenus.value.find(m => m.id === parentId);
  return parent ? parent.menu_name : `未知(ID:${parentId})`;
};

// 分页处理
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
  <div class="menu-management">
    <div class="page-heading">
      <h1 class="page-heading__title">
        <span class="page-heading__icon"><el-icon><Menu /></el-icon></span>
        菜单管理
      </h1>
      <el-button type="primary" :icon="'Plus'" @click="openCreateModal">创建菜单</el-button>
    </div>

    <!-- 搜索表单 -->
    <div class="page-card search-card">
      <div class="page-card__body">
        <el-form inline @submit.prevent="searchMenus">
          <el-form-item label="菜单名称">
            <el-input v-model="searchForm.menu_name" placeholder="请输入菜单名称" clearable style="width: 220px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="'Search'" @click="searchMenus">搜索</el-button>
            <el-button :icon="'Refresh'" @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 菜单列表 -->
    <div class="page-card">
      <el-table v-loading="loading" :data="menus" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="菜单名称" min-width="140">
          <template #default="{ row }">
            <span class="menu-name">{{ row.menu_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="menu_code" label="菜单代码" min-width="130">
          <template #default="{ row }">
            <el-tag effect="plain" size="small">{{ row.menu_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="menu_path" label="菜单路径" min-width="160" show-overflow-tooltip />
        <el-table-column label="组件Key" min-width="120">
          <template #default="{ row }">{{ row.component_key || '自动匹配' }}</template>
        </el-table-column>
        <el-table-column label="父菜单" min-width="120">
          <template #default="{ row }">{{ getParentMenuName(row.parent_id) }}</template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">{{ new Date(row.creation_date).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button size="small" :icon="'Edit'" @click="openEditModal(row)">编辑</el-button>
              <el-button size="small" type="danger" plain :icon="'Delete'" @click="deleteMenu(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无菜单数据" />
        </template>
      </el-table>

      <div class="table-footer">
        <span class="table-total">
          显示 {{ menus.length === 0 ? 0 : (currentPage - 1) * pageSize + 1 }} 至
          {{ Math.min(currentPage * pageSize, totalMenus) }} 条，共 {{ totalMenus }} 条记录
        </span>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalMenus"
          background
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 创建菜单弹窗 -->
    <el-dialog v-model="showCreateModal" title="创建菜单" width="560px" destroy-on-close>
      <el-form :model="menuForm" label-width="90px">
        <el-form-item label="菜单名称" required>
          <el-input v-model="menuForm.menu_name" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="菜单代码" required>
          <el-input v-model="menuForm.menu_code" placeholder="请输入菜单代码" />
        </el-form-item>
        <el-form-item label="菜单路径" required :error="menuPathError || undefined">
          <el-input v-model="menuForm.menu_path" placeholder="如 /dashboard/profile" />
          <div class="form-tip">用于浏览器地址和旧版动态路由回退</div>
        </el-form-item>
        <el-form-item label="组件Key">
          <el-select v-model="menuForm.component_key" style="width: 100%">
            <el-option v-for="option in componentOptions" :key="option.key" :label="option.label" :value="option.key" />
          </el-select>
          <div class="form-tip">优先用组件Key绑定页面；留空时按菜单代码和路径自动匹配</div>
        </el-form-item>
        <el-form-item label="父菜单">
          <el-select v-model="menuForm.parent_id" placeholder="无（作为顶级菜单）" clearable style="width: 100%">
            <el-option v-for="menu in parentMenus" :key="menu.id" :label="`${menu.menu_name} (${menu.menu_code})`" :value="menu.id" />
          </el-select>
          <div class="form-tip">父子预览：{{ parentChildPreview }}</div>
        </el-form-item>
        <el-form-item label="排序号">
          <el-input-number v-model="menuForm.sort_order" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateModal = false">取消</el-button>
        <el-button type="primary" @click="createMenu">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑菜单弹窗 -->
    <el-dialog v-model="showEditModal" title="编辑菜单" width="560px" destroy-on-close>
      <el-form :model="menuForm" label-width="90px">
        <el-form-item label="菜单名称" required>
          <el-input v-model="menuForm.menu_name" placeholder="请输入菜单名称" />
        </el-form-item>
        <el-form-item label="菜单代码">
          <el-input v-model="menuForm.menu_code" disabled />
          <div class="form-tip">菜单代码不可修改</div>
        </el-form-item>
        <el-form-item label="菜单路径" required :error="menuPathError || undefined">
          <el-input v-model="menuForm.menu_path" placeholder="如 /dashboard/profile" />
          <div class="form-tip">用于浏览器地址和旧版动态路由回退</div>
        </el-form-item>
        <el-form-item label="组件Key">
          <el-select v-model="menuForm.component_key" style="width: 100%">
            <el-option v-for="option in componentOptions" :key="option.key" :label="option.label" :value="option.key" />
          </el-select>
          <div class="form-tip">优先用组件Key绑定页面；留空时按菜单代码和路径自动匹配</div>
        </el-form-item>
        <el-form-item label="父菜单">
          <el-select v-model="menuForm.parent_id" placeholder="无（作为顶级菜单）" clearable style="width: 100%">
            <el-option
              v-for="menu in parentMenus.filter(m => m.id !== currentMenu?.id)"
              :key="menu.id"
              :label="`${menu.menu_name} (${menu.menu_code})`"
              :value="menu.id"
            />
          </el-select>
          <div class="form-tip">父子预览：{{ parentChildPreview }}；菜单不能选择自己作为父菜单</div>
        </el-form-item>
        <el-form-item label="排序号">
          <el-input-number v-model="menuForm.sort_order" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditModal = false">取消</el-button>
        <el-button type="primary" @click="updateMenu">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.search-card :deep(.el-form--inline .el-form-item) {
  margin-right: 16px;
  margin-bottom: 0;
}

.menu-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 20px;
  border-top: 1px solid var(--app-border);
  flex-wrap: wrap;
}

.table-total {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.form-tip {
  width: 100%;
  margin-top: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}
</style>
