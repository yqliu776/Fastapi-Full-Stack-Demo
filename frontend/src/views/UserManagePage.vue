<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { userService } from '@/services/userService';
import type { User, UserCreate, UserUpdate } from '@/services/userService';
import UserRoleSelector from '@/components/UserRoleSelector.vue';
import { useUserStore } from '@/stores/user';
import { roleService } from '@/services/roleService';
import type { Role } from '@/services/roleService';

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

// 表单数据
const userForm = reactive<UserCreate & UserUpdate>({
  user_name: '',
  email: '',
  phone_number: '',
  password: '',
  delete_flag: 'N',
  created_by: '-1',
  last_updated_by: '-1',
  last_update_login: '-1',
  role_codes: ['ROLE_USER']
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

// 角色数据
const allRoles = ref<Role[]>([]);
const selectedRoleCodes = ref<string[]>(['ROLE_USER']);

// 获取所有角色
const loadAllRoles = async () => {
  try {
    const response = await roleService.getRoles({ limit: 500 });
    if (response.code === 200) {
      allRoles.value = response.data.items;
    } else {
      ElMessage.error('加载角色列表失败: ' + response.message);
    }
  } catch (error) {
    console.error('加载角色列表出错:', error);
    ElMessage.error('加载角色列表出错');
  }
};

// 处理角色选择变更
const handleRoleChange = (codes: string[]) => {
  selectedRoleCodes.value = codes;
  userForm.role_codes = [...codes];
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
      ElMessage.error('加载用户列表失败: ' + response.message);
    }
  } catch (error) {
    console.error('加载用户列表出错:', error);
    ElMessage.error('加载用户列表出错');
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
  const userId = userStore.userInfo?.id.toString() || '-1';

  userForm.user_name = '';
  userForm.email = '';
  userForm.phone_number = '';
  userForm.password = '';
  userForm.delete_flag = 'N';
  userForm.created_by = userId;
  userForm.last_updated_by = userId;
  userForm.last_update_login = userId;
  userForm.role_codes = ['ROLE_USER'];
  selectedRoleCodes.value = ['ROLE_USER'];

  showCreateModal.value = true;
};

// 创建用户
const createUser = async () => {
  if (!userForm.password) {
    ElMessage.warning('请输入密码');
    return;
  }

  if (userForm.role_codes.length === 0) {
    userForm.role_codes = ['ROLE_USER'];
  }

  try {
    const response = await userService.createUser(userForm);
    if (response.code === 200) {
      showCreateModal.value = false;
      loadUsers();
      ElMessage.success('用户创建成功');
    } else {
      ElMessage.error('创建用户失败: ' + response.message);
    }
  } catch (error: unknown) {
    console.error('创建用户出错:', error);
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
        if (Array.isArray(detail)) {
          errorMsg += ': ' + detail.map((item: { msg: string }) => item.msg).join(', ');
        } else if (typeof detail === 'string') {
          errorMsg += ': ' + detail;
        }
      } catch {
        errorMsg = '创建用户出错';
      }
    }
    ElMessage.error(errorMsg);
  }
};

// 打开编辑用户模态框
const openEditModal = (user: User) => {
  const userId = userStore.userInfo?.id.toString() || '-1';

  currentUser.value = user;
  userForm.user_name = user.user_name;
  userForm.email = user.email;
  userForm.phone_number = user.phone_number || '';
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
      ElMessage.success('用户更新成功');
    } else {
      ElMessage.error('更新用户失败: ' + response.message);
    }
  } catch (error: unknown) {
    console.error('更新用户出错:', error);
    ElMessage.error('更新用户出错');
  }
};

// 打开修改密码模态框
const openPasswordModal = (user: User) => {
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

  if (!passwordForm.password) {
    ElMessage.warning('请输入新密码');
    return;
  }

  if (passwordForm.password !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致');
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
      ElMessage.success('密码修改成功');
    } else {
      ElMessage.error('修改密码失败: ' + response.message);
    }
  } catch (error) {
    console.error('修改密码出错:', error);
    ElMessage.error('修改密码出错');
  }
};

// 删除用户
const deleteUser = async (user: User) => {
  try {
    await ElMessageBox.confirm(`确定要删除用户"${user.user_name}"吗？`, '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    });
  } catch {
    return;
  }

  try {
    const response = await userService.deleteUser(user.id);
    if (response.code === 200) {
      loadUsers();
      ElMessage.success('用户删除成功');
    } else {
      ElMessage.error('删除用户失败: ' + response.message);
    }
  } catch (error) {
    console.error('删除用户出错:', error);
    ElMessage.error('删除用户出错');
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
  ElMessage.success('更新成功');
};

// 分页处理
const handlePageChange = (page: number) => {
  currentPage.value = page;
  loadUsers();
};

// 获取用户状态显示文本
const getUserStatusText = (deleteFlag: string) => {
  const option = statusOptions.find(opt => opt.value === deleteFlag);
  return option ? option.label : deleteFlag;
};

// 获取用户状态标签类型
const getStatusType = (deleteFlag: string): 'success' | 'danger' | 'info' => {
  switch (deleteFlag) {
    case 'N':
      return 'success';
    case 'Y':
      return 'danger';
    default:
      return 'info';
  }
};

// 初始化
onMounted(() => {
  loadUsers();
  loadAllRoles();
});
</script>

<template>
  <div class="user-management">
    <div class="page-heading">
      <h1 class="page-heading__title">
        <span class="page-heading__icon"><el-icon><User /></el-icon></span>
        用户管理
      </h1>
      <el-button type="primary" :icon="'Plus'" @click="openCreateModal">创建用户</el-button>
    </div>

    <!-- 搜索表单 -->
    <div class="page-card search-card">
      <div class="page-card__body">
        <el-form inline @submit.prevent="searchUsers">
          <el-form-item label="用户名">
            <el-input
              v-model="searchForm.user_name"
              placeholder="请输入用户名"
              clearable
              style="width: 180px"
            />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input
              v-model="searchForm.email"
              placeholder="请输入邮箱"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="searchForm.delete_flag" placeholder="全部" clearable style="width: 120px">
              <el-option v-for="option in statusOptions" :key="option.value" :label="option.label" :value="option.value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :icon="'Search'" @click="searchUsers">搜索</el-button>
            <el-button :icon="'Refresh'" @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="page-card">
      <el-table v-loading="loading" :data="users" stripe style="width: 100%">
        <el-table-column prop="user_name" label="用户名" min-width="120">
          <template #default="{ row }">
            <div class="user-cell">
              <el-avatar :size="28" class="user-cell-avatar">
                {{ row.user_name.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="user-cell-name">{{ row.user_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="phone_number" label="电话" min-width="130">
          <template #default="{ row }">{{ row.phone_number || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.delete_flag)" effect="light" round>
              {{ getUserStatusText(row.delete_flag) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" min-width="170">
          <template #default="{ row }">{{ new Date(row.creation_date).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="230" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button size="small" :icon="'Edit'" @click="openEditModal(row)">编辑</el-button>
              <el-button size="small" type="warning" plain :icon="'Key'" @click="openPasswordModal(row)">密码</el-button>
              <el-button size="small" type="success" plain :icon="'UserFilled'" @click="openRoleModal(row)">角色</el-button>
              <el-button size="small" type="danger" plain :icon="'Delete'" @click="deleteUser(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无数据" />
        </template>
      </el-table>

      <div class="table-footer">
        <span class="table-total">共 {{ totalUsers }} 条记录</span>
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="totalUsers"
          background
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 创建用户弹窗 -->
    <el-dialog v-model="showCreateModal" title="创建用户" width="540px" destroy-on-close>
      <el-form :model="userForm" label-width="80px">
        <el-form-item label="用户名" required>
          <el-input v-model="userForm.user_name" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" required>
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="userForm.phone_number" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="密码" required>
          <el-input v-model="userForm.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="状态" required>
          <el-select v-model="userForm.delete_flag" style="width: 100%">
            <el-option v-for="option in statusOptions" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="用户角色">
          <div class="role-checkbox-group">
            <el-checkbox-group v-model="selectedRoleCodes" @change="handleRoleChange">
              <el-checkbox v-for="role in allRoles" :key="role.id" :value="role.role_code" border>
                <div class="role-checkbox-label">
                  <span class="role-name">{{ role.role_name }}</span>
                  <span class="role-code">{{ role.role_code }}</span>
                </div>
              </el-checkbox>
            </el-checkbox-group>
            <el-empty v-if="allRoles.length === 0" description="暂无可用角色" :image-size="60" />
          </div>
          <div class="form-tip">至少选择一个角色，默认为普通用户（ROLE_USER）</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateModal = false">取消</el-button>
        <el-button type="primary" @click="createUser">确认创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑用户弹窗 -->
    <el-dialog v-model="showEditModal" title="编辑用户" width="540px" destroy-on-close>
      <el-form :model="userForm" label-width="80px">
        <el-form-item label="用户名" required>
          <el-input v-model="userForm.user_name" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" required>
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="userForm.phone_number" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="状态" required>
          <el-select v-model="userForm.delete_flag" style="width: 100%">
            <el-option v-for="option in statusOptions" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditModal = false">取消</el-button>
        <el-button type="primary" @click="updateUser">保存修改</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码弹窗 -->
    <el-dialog v-model="showPasswordModal" :title="`修改密码 - ${currentUser?.user_name || ''}`" width="480px" destroy-on-close>
      <el-form :model="passwordForm" label-width="90px">
        <el-form-item label="新密码" required>
          <el-input v-model="passwordForm.password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" required>
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordModal = false">取消</el-button>
        <el-button type="primary" @click="updatePassword">确认修改</el-button>
      </template>
    </el-dialog>

    <!-- 角色分配弹窗 -->
    <el-dialog
      v-model="showRoleModal"
      :title="`角色分配 - ${currentUser?.user_name || ''}`"
      width="760px"
      destroy-on-close
    >
      <UserRoleSelector
        v-if="currentUser"
        :user-id="currentUser.id"
        :username="currentUser.user_name"
        mode="edit"
        @update="handleUserUpdate"
      />
      <template #footer>
        <el-button type="primary" @click="showRoleModal = false">完成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.search-card :deep(.el-form--inline .el-form-item) {
  margin-right: 16px;
  margin-bottom: 0;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-cell-avatar {
  background: var(--brand-gradient);
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-cell-name {
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

.role-checkbox-group {
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  padding: 12px;
  background: var(--app-fill-2);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.role-checkbox-group :deep(.el-checkbox) {
  display: flex;
  height: auto;
  margin-right: 0;
  white-space: normal;
}

.role-checkbox-group :deep(.el-checkbox__label) {
  flex: 1;
}

.role-checkbox-label {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.role-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.role-code {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
