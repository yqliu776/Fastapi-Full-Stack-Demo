<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
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

const userStore = useUserStore();

// 权限列表状态
const permissions = ref<Permission[]>([]);
const permissionOptions = ref<Permission[]>([]);
const totalPermissions = ref(0);
const loading = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const searchForm = reactive({
  permission_name: '',
  permission_code: '',
  deleted: ''
});

// 删除状态筛选选项
const deletedStatusOptions = [
  { value: '', label: '全部' },
  { value: 'false', label: '正常' },
  { value: 'true', label: '已删除' }
];

// API权限绑定状态
const apiPermissions = ref<ApiPermission[]>([]);
const totalApiPermissions = ref(0);
const apiLoading = ref(false);
const currentApiPage = ref(1);
const apiPageSize = ref(10);
const apiSearchForm = reactive({
  method: '',
  path_pattern: '',
  permission_code: '',
  deleted: ''
});
const methodOptions = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];

// 模态框状态
const showCreateModal = ref(false);
const showEditModal = ref(false);
const showCreateApiModal = ref(false);
const showEditApiModal = ref(false);
const currentPermission = ref<Permission | null>(null);
const currentApiPermission = ref<ApiPermission | null>(null);

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

// 加载权限列表
const loadPermissions = async () => {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * pageSize.value;
    const params: Record<string, unknown> = { skip, limit: pageSize.value };
    Object.entries(searchForm).forEach(([key, value]) => {
      if (value !== '' && value !== undefined && value !== null) {
        params[key] = value;
      }
    });
    const response = await permissionService.getPermissions(params);
    if (response.code === 200) {
      permissions.value = response.data.items;
      totalPermissions.value = response.data.total;
    } else {
      ElMessage.error('加载权限列表失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '加载权限列表出错'));
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
    const params: Record<string, unknown> = { skip, limit: apiPageSize.value };
    Object.entries(apiSearchForm).forEach(([key, value]) => {
      if (value !== '' && value !== undefined && value !== null) {
        params[key] = value;
      }
    });
    const response = await permissionService.getApiPermissions(params);
    if (response.code === 200) {
      apiPermissions.value = response.data.items;
      totalApiPermissions.value = response.data.total;
    } else {
      ElMessage.error('加载API权限绑定失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '加载API权限绑定出错'));
  } finally {
    apiLoading.value = false;
  }
};

// 搜索权限
const searchPermissions = () => {
  currentPage.value = 1;
  loadPermissions();
};

const resetSearch = () => {
  searchForm.permission_name = '';
  searchForm.permission_code = '';
  searchForm.deleted = '';
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
  apiSearchForm.deleted = '';
  searchApiPermissions();
};

// 打开创建权限模态框
const openCreateModal = () => {
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
      loadPermissionOptions();
      ElMessage.success('权限创建成功');
    } else {
      ElMessage.error('创建权限失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '创建权限出错'));
  }
};

// 打开编辑权限模态框
const openEditModal = (permission: Permission) => {
  currentPermission.value = permission;

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
    const response = await permissionService.updatePermission(currentPermission.value.id, {
      permission_name: permissionForm.permission_name,
      last_updated_by: permissionForm.last_updated_by,
      last_update_login: permissionForm.last_update_login
    });
    if (response.code === 200) {
      showEditModal.value = false;
      loadPermissions();
      loadPermissionOptions();
      ElMessage.success('权限更新成功');
    } else {
      ElMessage.error('更新权限失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '更新权限出错'));
  }
};

// 删除权限
const deletePermission = async (permission: Permission) => {
  try {
    await ElMessageBox.confirm(`确定要删除权限"${permission.permission_name}"吗？`, '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    });
  } catch {
    return;
  }

  try {
    const response = await permissionService.deletePermission(permission.id);
    if (response.code === 200) {
      loadPermissions();
      loadPermissionOptions();
      ElMessage.success('权限删除成功');
    } else {
      ElMessage.error('删除权限失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '删除权限出错'));
  }
};

// 恢复权限
const restorePermission = async (permission: Permission) => {
  try {
    const response = await permissionService.restorePermission(permission.id);
    if (response.code === 200) {
      loadPermissions();
      loadPermissionOptions();
      ElMessage.success(`权限"${permission.permission_name}"已恢复`);
    } else {
      ElMessage.error('恢复权限失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '恢复权限出错'));
  }
};

// 彻底删除权限
const purgePermission = async (permission: Permission) => {
  try {
    await ElMessageBox.confirm(
      `确定要彻底删除权限"${permission.permission_name}"吗？该操作将物理删除数据及其关联关系，不可恢复！`,
      '彻底删除确认',
      {
        confirmButtonText: '彻底删除',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger'
      }
    );
  } catch {
    return;
  }

  try {
    const response = await permissionService.purgePermission(permission.id);
    if (response.code === 200) {
      loadPermissions();
      loadPermissionOptions();
      ElMessage.success('权限已彻底删除');
    } else {
      ElMessage.error('彻底删除权限失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '彻底删除权限出错'));
  }
};

const createApiPermission = async () => {
  try {
    const response = await permissionService.createApiPermission(apiPermissionForm);
    if (response.code === 200) {
      showCreateApiModal.value = false;
      loadApiPermissions();
      ElMessage.success('API权限绑定创建成功');
    } else {
      ElMessage.error('API权限绑定创建失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, 'API权限绑定创建出错'));
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
      ElMessage.success('API权限绑定更新成功');
    } else {
      ElMessage.error('API权限绑定更新失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, 'API权限绑定更新出错'));
  }
};

const deleteApiPermission = async (apiPermission: ApiPermission) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除API权限绑定"${apiPermission.method} ${apiPermission.path_pattern}"吗？`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );
  } catch {
    return;
  }

  try {
    const response = await permissionService.deleteApiPermission(apiPermission.id);
    if (response.code === 200) {
      loadApiPermissions();
      ElMessage.success('API权限绑定删除成功');
    } else {
      ElMessage.error('API权限绑定删除失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, 'API权限绑定删除出错'));
  }
};

// 恢复API权限绑定
const restoreApiPermission = async (apiPermission: ApiPermission) => {
  try {
    const response = await permissionService.restoreApiPermission(apiPermission.id);
    if (response.code === 200) {
      loadApiPermissions();
      ElMessage.success(`API权限绑定"${apiPermission.method} ${apiPermission.path_pattern}"已恢复`);
    } else {
      ElMessage.error('恢复API权限绑定失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '恢复API权限绑定出错'));
  }
};

// 彻底删除API权限绑定
const purgeApiPermission = async (apiPermission: ApiPermission) => {
  try {
    await ElMessageBox.confirm(
      `确定要彻底删除API权限绑定"${apiPermission.method} ${apiPermission.path_pattern}"吗？该操作不可恢复！`,
      '彻底删除确认',
      {
        confirmButtonText: '彻底删除',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger'
      }
    );
  } catch {
    return;
  }

  try {
    const response = await permissionService.purgeApiPermission(apiPermission.id);
    if (response.code === 200) {
      loadApiPermissions();
      ElMessage.success('API权限绑定已彻底删除');
    } else {
      ElMessage.error('彻底删除API权限绑定失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '彻底删除API权限绑定出错'));
  }
};

// 分页处理
const handlePageChange = (page: number) => {
  currentPage.value = page;
  loadPermissions();
};

const handleApiPageChange = (page: number) => {
  currentApiPage.value = page;
  loadApiPermissions();
};

// HTTP 方法标签类型
const getMethodType = (method: string): 'primary' | 'success' | 'warning' | 'danger' | 'info' => {
  switch (method) {
    case 'GET':
      return 'primary';
    case 'POST':
      return 'success';
    case 'PUT':
    case 'PATCH':
      return 'warning';
    case 'DELETE':
      return 'danger';
    default:
      return 'info';
  }
};

// 初始化
onMounted(() => {
  loadPermissions();
  loadPermissionOptions();
  loadApiPermissions();
});
</script>

<template>
  <div class="permission-management">
    <div class="page-heading">
      <h1 class="page-heading__title">
        <span class="page-heading__icon"><el-icon><Lock /></el-icon></span>
        权限管理
      </h1>
    </div>

    <!-- 权限列表 -->
    <div class="page-card">
      <div class="page-card__header">
        <el-icon><Key /></el-icon>
        权限列表
        <div class="header-spacer"></div>
        <el-button type="primary" size="small" :icon="'Plus'" @click="openCreateModal">创建权限</el-button>
      </div>
      <div class="page-card__body search-body">
        <el-form inline @submit.prevent="searchPermissions">
          <el-form-item label="权限名称">
            <el-input v-model="searchForm.permission_name" placeholder="请输入权限名称" clearable style="width: 180px" />
          </el-form-item>
          <el-form-item label="权限代码">
            <el-input v-model="searchForm.permission_code" placeholder="请输入权限代码" clearable style="width: 180px" />
          </el-form-item>
          <el-form-item label="删除状态">
            <el-select v-model="searchForm.deleted" style="width: 120px">
              <el-option v-for="option in deletedStatusOptions" :key="option.value" :label="option.label" :value="option.value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="'Search'" @click="searchPermissions">搜索</el-button>
            <el-button :icon="'Refresh'" @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table v-loading="loading" :data="permissions" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="权限名称" min-width="160">
          <template #default="{ row }">
            <span class="permission-name">{{ row.permission_name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="权限代码" min-width="160">
          <template #default="{ row }">
            <el-tag effect="plain" type="primary">{{ row.permission_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">{{ new Date(row.creation_date).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="最后更新" min-width="170">
          <template #default="{ row }">{{ new Date(row.last_update_date).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div v-if="row.delete_flag === 'Y'" class="table-actions">
              <el-button size="small" type="success" plain :icon="'RefreshLeft'" @click="restorePermission(row)">恢复</el-button>
              <el-button size="small" type="danger" :icon="'DeleteFilled'" @click="purgePermission(row)">彻底删除</el-button>
            </div>
            <div v-else class="table-actions">
              <el-button size="small" :icon="'Edit'" @click="openEditModal(row)">编辑</el-button>
              <el-button size="small" type="danger" plain :icon="'Delete'" @click="deletePermission(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无权限数据" />
        </template>
      </el-table>

      <div class="table-footer">
        <span class="table-total">共 {{ totalPermissions }} 条记录</span>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalPermissions"
          background
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- API权限绑定 -->
    <div class="page-card">
      <div class="page-card__header">
        <el-icon><Connection /></el-icon>
        API权限绑定
        <div class="header-spacer"></div>
        <el-button type="success" size="small" :icon="'Plus'" @click="openCreateApiModal">创建API绑定</el-button>
      </div>
      <div class="page-card__body search-body">
        <el-form inline @submit.prevent="searchApiPermissions">
          <el-form-item label="HTTP方法">
            <el-select v-model="apiSearchForm.method" placeholder="全部" clearable style="width: 120px">
              <el-option v-for="method in methodOptions" :key="method" :label="method" :value="method" />
            </el-select>
          </el-form-item>
          <el-form-item label="API路径">
            <el-input v-model="apiSearchForm.path_pattern" placeholder="请输入API路径" clearable style="width: 200px" />
          </el-form-item>
          <el-form-item label="权限代码">
            <el-input v-model="apiSearchForm.permission_code" placeholder="请输入权限代码" clearable style="width: 180px" />
          </el-form-item>
          <el-form-item label="删除状态">
            <el-select v-model="apiSearchForm.deleted" style="width: 120px">
              <el-option v-for="option in deletedStatusOptions" :key="option.value" :label="option.label" :value="option.value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="'Search'" @click="searchApiPermissions">搜索</el-button>
            <el-button :icon="'Refresh'" @click="resetApiSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table v-loading="apiLoading" :data="apiPermissions" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="HTTP方法" width="110">
          <template #default="{ row }">
            <el-tag :type="getMethodType(row.method)" effect="dark" size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="API路径" min-width="200">
          <template #default="{ row }">
            <code class="path-code">{{ row.path_pattern }}</code>
          </template>
        </el-table-column>
        <el-table-column label="权限代码" min-width="150">
          <template #default="{ row }">{{ row.permission_code }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" effect="light" round>
              {{ row.enabled ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="说明" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">{{ row.description || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div v-if="row.delete_flag === 'Y'" class="table-actions">
              <el-button size="small" type="success" plain :icon="'RefreshLeft'" @click="restoreApiPermission(row)">恢复</el-button>
              <el-button size="small" type="danger" :icon="'DeleteFilled'" @click="purgeApiPermission(row)">彻底删除</el-button>
            </div>
            <div v-else class="table-actions">
              <el-button size="small" :icon="'Edit'" @click="openEditApiModal(row)">编辑</el-button>
              <el-button size="small" type="danger" plain :icon="'Delete'" @click="deleteApiPermission(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无API权限绑定" />
        </template>
      </el-table>

      <div class="table-footer">
        <span class="table-total">共 {{ totalApiPermissions }} 条记录</span>
        <el-pagination
          v-model:current-page="currentApiPage"
          :page-size="apiPageSize"
          :total="totalApiPermissions"
          background
          layout="prev, pager, next"
          @current-change="handleApiPageChange"
        />
      </div>
    </div>

    <!-- 创建权限弹窗 -->
    <el-dialog v-model="showCreateModal" title="创建权限" width="480px" destroy-on-close>
      <el-form :model="permissionForm" label-width="90px">
        <el-form-item label="权限名称" required>
          <el-input v-model="permissionForm.permission_name" placeholder="请输入权限名称" />
        </el-form-item>
        <el-form-item label="权限代码" required>
          <el-input v-model="permissionForm.permission_code" placeholder="如 user:create" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateModal = false">取消</el-button>
        <el-button type="primary" @click="createPermission">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑权限弹窗 -->
    <el-dialog v-model="showEditModal" title="编辑权限" width="480px" destroy-on-close>
      <el-form :model="permissionForm" label-width="90px">
        <el-form-item label="权限名称" required>
          <el-input v-model="permissionForm.permission_name" placeholder="请输入权限名称" />
        </el-form-item>
        <el-form-item label="权限代码">
          <el-input v-model="permissionForm.permission_code" disabled />
          <div class="form-tip">权限代码创建后不可修改，代码会用于 API 绑定和路由鉴权</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditModal = false">取消</el-button>
        <el-button type="primary" @click="updatePermission">保存修改</el-button>
      </template>
    </el-dialog>

    <!-- 创建API权限绑定弹窗 -->
    <el-dialog v-model="showCreateApiModal" title="创建API权限绑定" width="600px" destroy-on-close>
      <el-form :model="apiPermissionForm" label-width="90px">
        <div class="form-grid">
          <el-form-item label="HTTP方法" required>
            <el-select v-model="apiPermissionForm.method" style="width: 100%">
              <el-option v-for="method in methodOptions" :key="method" :label="method" :value="method" />
            </el-select>
          </el-form-item>
          <el-form-item label="权限代码" required>
            <el-select v-model="apiPermissionForm.permission_code" placeholder="请选择权限代码" style="width: 100%">
              <el-option
                v-for="permission in permissionOptions"
                :key="permission.id"
                :label="`${permission.permission_code} - ${permission.permission_name}`"
                :value="permission.permission_code"
              />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="API路径" required>
          <el-input v-model="apiPermissionForm.path_pattern" placeholder="/roles/{role_id}" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="apiPermissionForm.description" placeholder="请输入说明" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="apiPermissionForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateApiModal = false">取消</el-button>
        <el-button type="primary" @click="createApiPermission">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑API权限绑定弹窗 -->
    <el-dialog v-model="showEditApiModal" title="编辑API权限绑定" width="600px" destroy-on-close>
      <el-form :model="apiPermissionForm" label-width="90px">
        <div class="form-grid">
          <el-form-item label="HTTP方法" required>
            <el-select v-model="apiPermissionForm.method" style="width: 100%">
              <el-option v-for="method in methodOptions" :key="method" :label="method" :value="method" />
            </el-select>
          </el-form-item>
          <el-form-item label="权限代码" required>
            <el-select v-model="apiPermissionForm.permission_code" style="width: 100%">
              <el-option
                v-for="permission in permissionOptions"
                :key="permission.id"
                :label="`${permission.permission_code} - ${permission.permission_name}`"
                :value="permission.permission_code"
              />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="API路径" required>
          <el-input v-model="apiPermissionForm.path_pattern" placeholder="/roles/{role_id}" />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="apiPermissionForm.description" placeholder="请输入说明" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="apiPermissionForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditApiModal = false">取消</el-button>
        <el-button type="primary" @click="updateApiPermission">保存修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.permission-management {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-card__header .header-spacer {
  flex: 1;
}

.search-body :deep(.el-form--inline .el-form-item) {
  margin-right: 16px;
  margin-bottom: 0;
}

.permission-name {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.path-code {
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 12px;
  background: var(--app-fill-3);
  border: 1px solid var(--app-border);
  padding: 2px 8px;
  border-radius: 6px;
  color: var(--el-text-color-regular);
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

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 12px;
}

@media (max-width: 640px) {
  .form-grid {
    grid-template-columns: 1fr;
    gap: 0;
  }
}

.form-tip {
  width: 100%;
  margin-top: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.5;
}
</style>
