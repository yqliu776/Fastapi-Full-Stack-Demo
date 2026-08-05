<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { roleService } from '@/services/roleService';
import type { Role, RoleCreate, RoleUpdate } from '@/services/roleService';
import RolePermissionSelector from '@/components/RolePermissionSelector.vue';
import RoleMenuSelector from '@/components/RoleMenuSelector.vue';
import { useUserStore } from '@/stores/user';
import { handleComponentError } from '@/utils/errorHandlers';

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

// 表单数据
const roleForm = reactive<RoleCreate & RoleUpdate>({
  role_name: '',
  role_code: '',
  created_by: '-1',
  last_updated_by: '-1',
  last_update_login: '-1'
});

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
      ElMessage.error('加载角色列表失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '加载角色列表出错'));
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
      ElMessage.success('角色创建成功');
    } else {
      ElMessage.error('创建角色失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '创建角色出错'));
  }
};

// 打开编辑角色模态框
const openEditModal = (role: Role) => {
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
    const updateData: RoleUpdate = {
      role_name: roleForm.role_name,
      last_updated_by: roleForm.last_updated_by,
      last_update_login: roleForm.last_update_login
    };

    const response = await roleService.updateRole(currentRole.value.id, updateData);
    if (response.code === 200) {
      showEditModal.value = false;
      loadRoles();
      ElMessage.success('角色更新成功');
    } else {
      ElMessage.error('更新角色失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '更新角色出错'));
  }
};

// 删除角色
const deleteRole = async (role: Role) => {
  try {
    await ElMessageBox.confirm(`确定要删除角色"${role.role_name}"吗？`, '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    });
  } catch {
    return;
  }

  try {
    const response = await roleService.deleteRole(role.id);
    if (response.code === 200) {
      loadRoles();
      ElMessage.success('角色删除成功');
    } else {
      ElMessage.error('删除角色失败: ' + response.message);
    }
  } catch (error: any) {
    ElMessage.error(handleComponentError(error, '删除角色出错'));
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
  ElMessage.success('更新成功');
};

// 分页处理
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
    <div class="page-heading">
      <h1 class="page-heading__title">
        <span class="page-heading__icon"><el-icon><UserFilled /></el-icon></span>
        角色管理
      </h1>
      <el-button type="primary" :icon="'Plus'" @click="openCreateModal">创建角色</el-button>
    </div>

    <!-- 搜索表单 -->
    <div class="page-card search-card">
      <div class="page-card__body">
        <el-form inline @submit.prevent="searchRoles">
          <el-form-item label="角色名称">
            <el-input v-model="searchForm.role_name" placeholder="请输入角色名称" clearable style="width: 180px" />
          </el-form-item>
          <el-form-item label="角色代码">
            <el-input v-model="searchForm.role_code" placeholder="请输入角色代码" clearable style="width: 180px" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="'Search'" @click="searchRoles">搜索</el-button>
            <el-button :icon="'Refresh'" @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 角色列表 -->
    <div class="page-card">
      <el-table v-loading="loading" :data="roles" stripe style="width: 100%">
        <el-table-column label="角色" min-width="160">
          <template #default="{ row }">
            <div class="role-cell">
              <el-avatar :size="30" class="role-cell-avatar">
                <el-icon><Avatar /></el-icon>
              </el-avatar>
              <div>
                <div class="role-cell-name">{{ row.role_name }}</div>
                <div class="role-cell-code">{{ row.role_code }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="role_code" label="角色代码" min-width="150">
          <template #default="{ row }">
            <el-tag effect="plain" type="info">{{ row.role_code }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">{{ new Date(row.creation_date).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="更新时间" min-width="170">
          <template #default="{ row }">{{ new Date(row.last_update_date).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button size="small" :icon="'Edit'" @click="openEditModal(row)">编辑</el-button>
              <el-button size="small" type="success" plain :icon="'Lock'" @click="openPermissionModal(row)">权限</el-button>
              <el-button size="small" type="primary" plain :icon="'Menu'" @click="openMenuModal(row)">菜单</el-button>
              <el-button size="small" type="danger" plain :icon="'Delete'" @click="deleteRole(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无数据" />
        </template>
      </el-table>

      <div class="table-footer">
        <span class="table-total">共 {{ totalRoles }} 条记录</span>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalRoles"
          background
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 创建角色弹窗 -->
    <el-dialog v-model="showCreateModal" title="创建角色" width="480px" destroy-on-close>
      <el-form :model="roleForm" label-width="90px">
        <el-form-item label="角色名称" required>
          <el-input v-model="roleForm.role_name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色代码" required>
          <el-input v-model="roleForm.role_code" placeholder="请输入角色代码（如 ROLE_ADMIN）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateModal = false">取消</el-button>
        <el-button type="primary" @click="createRole">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑角色弹窗 -->
    <el-dialog v-model="showEditModal" title="编辑角色" width="480px" destroy-on-close>
      <el-form :model="roleForm" label-width="90px">
        <el-form-item label="角色名称" required>
          <el-input v-model="roleForm.role_name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色代码">
          <el-input v-model="roleForm.role_code" disabled />
          <div class="form-tip">角色代码创建后不可修改</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditModal = false">取消</el-button>
        <el-button type="primary" @click="updateRole">保存修改</el-button>
      </template>
    </el-dialog>

    <!-- 权限分配弹窗 -->
    <el-dialog
      v-model="showPermissionModal"
      :title="`角色权限管理 - ${currentRole?.role_name || ''}`"
      width="720px"
      destroy-on-close
    >
      <RolePermissionSelector
        v-if="currentRole"
        :role-id="currentRole.id"
        :visible="showPermissionModal"
        @update="handleRoleUpdate"
        @close="showPermissionModal = false"
      />
      <template #footer>
        <el-button type="primary" @click="showPermissionModal = false">完成</el-button>
      </template>
    </el-dialog>

    <!-- 菜单分配弹窗 -->
    <el-dialog
      v-model="showMenuModal"
      :title="`角色菜单管理 - ${currentRole?.role_name || ''}`"
      width="720px"
      destroy-on-close
    >
      <RoleMenuSelector
        v-if="currentRole"
        :role-id="currentRole.id"
        :visible="showMenuModal"
        @update="handleRoleUpdate"
        @close="showMenuModal = false"
      />
      <template #footer>
        <el-button type="primary" @click="showMenuModal = false">完成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.search-card :deep(.el-form--inline .el-form-item) {
  margin-right: 16px;
  margin-bottom: 0;
}

.role-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.role-cell-avatar {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  flex-shrink: 0;
}

.role-cell-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.role-cell-code {
  font-size: 12px;
  color: var(--el-text-color-secondary);
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
  margin-top: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
