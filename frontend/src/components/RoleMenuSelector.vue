<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { menuService } from '@/services/menuService';
import type { Menu } from '@/services/menuService';
import { roleService } from '@/services/roleService';

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

const menuById = computed(() => {
  return new Map(allMenus.value.map(menu => [menu.id, menu]));
});

// 计算属性 - 菜单树结构
const menuTree = computed(() => {
  if (!allMenus.value.length) return [];

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    return allMenus.value.filter(
      menu =>
        menu.menu_name.toLowerCase().includes(keyword) ||
        menu.menu_code.toLowerCase().includes(keyword)
    );
  }

  const rootMenus = allMenus.value.filter(menu => !menu.parent_id);

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

const getAncestorIds = (menuId: number) => {
  const ids: number[] = [];
  let parentId = menuById.value.get(menuId)?.parent_id;

  while (parentId) {
    ids.push(parentId);
    parentId = menuById.value.get(parentId)?.parent_id;
  }

  return ids;
};

const getDescendantIds = (menuId: number): number[] => {
  const children = allMenus.value.filter(menu => menu.parent_id === menuId);
  return children.flatMap(child => [child.id, ...getDescendantIds(child.id)]);
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
  const nextSelected = new Set(selectedMenus.value);
  if (!nextSelected.has(menuId)) {
    [menuId, ...getAncestorIds(menuId), ...getDescendantIds(menuId)].forEach(id => nextSelected.add(id));
  } else {
    [menuId, ...getDescendantIds(menuId)].forEach(id => nextSelected.delete(id));
  }
  selectedMenus.value = Array.from(nextSelected);
};

// 全选
const selectAll = () => {
  selectedMenus.value = allMenus.value.map(m => m.id);
};

// 全不选
const deselectAll = () => {
  selectedMenus.value = [];
};

// 菜单统计
const menuStats = computed(() => {
  return {
    total: allMenus.value.length,
    assigned: roleMenus.value.length,
    selected: selectedMenus.value.length,
    toAssign: selectedMenus.value.filter(id => !roleMenuIds.value.includes(id)).length,
    toRemove: roleMenuIds.value.filter(id => !selectedMenus.value.includes(id)).length
  };
});

// 计算菜单行状态 class
const menuRowClass = (menuId: number) => {
  if (hasRoleMenu(menuId) && isMenuSelected(menuId)) return 'is-assigned';
  if (isMenuSelected(menuId) && !hasRoleMenu(menuId)) return 'is-selected-new';
  if (hasRoleMenu(menuId) && !isMenuSelected(menuId)) return 'is-removing';
  return '';
};

// 初始化方法
const init = async () => {
  errorMsg.value = '';
  await Promise.all([loadAllMenus(), loadRoleMenus()]);
};

// 加载所有菜单
const loadAllMenus = async () => {
  loading.value.allMenus = true;
  try {
    const response = await menuService.getMenus({ limit: 1000 });
    if (response.code === 200) {
      allMenus.value = response.data.items;
    } else {
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
    const roleResponse = await roleService.getRole(props.roleId);
    if (roleResponse.code === 200 && roleResponse.data.menus) {
      roleMenus.value = roleResponse.data.menus as unknown as Menu[];
      selectedMenus.value = roleMenus.value.map(menu => menu.id);
    } else {
      const response = await menuService.getRoleMenus(props.roleId);
      if (response.code === 200) {
        roleMenus.value = response.data.items;
        selectedMenus.value = roleMenus.value.map(menu => menu.id);
      } else {
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

// 保存角色菜单完整集合
const saveMenus = async () => {
  errorMsg.value = '';

  loading.value.submit = true;
  try {
    const response = await roleService.replaceMenusForRole(props.roleId, {
      menu_ids: selectedMenus.value
    });
    if (response.code === 200) {
      await loadRoleMenus();
      emit('update');
    } else {
      errorMsg.value = '保存菜单失败: ' + response.message;
    }
  } catch (error) {
    console.error('保存菜单出错:', error);
    errorMsg.value = '保存菜单出错';
  } finally {
    loading.value.submit = false;
  }
};

// 监听visible变化
watch(
  () => props.visible,
  newValue => {
    if (newValue) {
      init();
    } else {
      selectedMenus.value = [];
      expandedMenus.value = [];
    }
  }
);

// 监听roleId变化
watch(
  () => props.roleId,
  () => {
    if (props.visible) {
      loadRoleMenus();
    }
  }
);

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
    <div class="selector-toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索菜单名称或代码"
        clearable
        :prefix-icon="'Search'"
        style="width: 260px"
      />
      <div class="toolbar-actions">
        <el-button size="small" @click="selectAll">全选</el-button>
        <el-button size="small" @click="deselectAll">全不选</el-button>
      </div>
    </div>

    <!-- 错误消息 -->
    <el-alert v-if="errorMsg" :title="errorMsg" type="error" show-icon :closable="false" />

    <!-- 菜单信息统计 -->
    <div class="stats-bar">
      <div class="stat-chip">
        <span class="stat-dot dot-total"></span>
        总菜单数 <strong>{{ menuStats.total }}</strong>
      </div>
      <div class="stat-chip">
        <span class="stat-dot dot-assigned"></span>
        已分配 <strong>{{ menuStats.assigned }}</strong>
      </div>
      <div class="stat-chip">
        <span class="stat-dot dot-selected"></span>
        已选择 <strong>{{ menuStats.selected }}</strong>
      </div>
      <div v-if="menuStats.toAssign > 0" class="stat-chip">
        <span class="stat-dot dot-new"></span>
        待分配 <strong>{{ menuStats.toAssign }}</strong>
      </div>
      <div v-if="menuStats.toRemove > 0" class="stat-chip">
        <span class="stat-dot dot-remove"></span>
        保存后移除 <strong>{{ menuStats.toRemove }}</strong>
      </div>
    </div>

    <!-- 菜单标签图例 -->
    <div class="legend-bar">
      <span class="legend-item"><span class="legend-dot dot-assigned"></span>已分配菜单</span>
      <span class="legend-item"><span class="legend-dot dot-new"></span>已选择待操作</span>
      <span class="legend-item">
        <el-icon :size="12"><CaretRight /></el-icon>
        展开子菜单
      </span>
    </div>

    <!-- 菜单列表 -->
    <div class="menu-list">
      <div v-if="loading.allMenus || loading.roleMenus" class="list-loading">
        <el-icon class="is-loading" :size="26"><Loading /></el-icon>
        <span>加载菜单中...</span>
      </div>
      <el-empty v-else-if="menuTree.length === 0" description="暂无数据" :image-size="80" />
      <div v-else>
        <!-- 扁平结构显示搜索结果 -->
        <div v-if="searchKeyword" class="space-y-1">
          <div
            v-for="menu in menuTree"
            :key="menu.id"
            class="menu-row"
            :class="menuRowClass(menu.id)"
            @click="toggleSelectMenu(menu.id)"
          >
            <el-checkbox
              :model-value="isMenuSelected(menu.id)"
              @click.stop
              @change="toggleSelectMenu(menu.id)"
            />
            <div class="menu-info">
              <span class="menu-name">{{ menu.menu_name }}</span>
              <span class="menu-code">{{ menu.menu_code }}</span>
            </div>
            <el-tag v-if="hasRoleMenu(menu.id)" type="success" effect="light" size="small" round>已分配</el-tag>
          </div>
        </div>

        <!-- 树结构显示所有菜单 -->
        <div v-else class="space-y-1">
          <template v-for="menu in menuTree" :key="menu.id">
            <div class="menu-item">
              <div class="menu-row" :class="menuRowClass(menu.id)" @click="toggleSelectMenu(menu.id)">
                <button
                  v-if="menu.children && menu.children.length > 0"
                  class="expand-btn"
                  :class="{ 'is-expanded': isMenuExpanded(menu.id) }"
                  @click.stop="toggleExpandMenu(menu.id)"
                >
                  <el-icon :size="12"><CaretRight /></el-icon>
                </button>
                <span v-else class="expand-placeholder"></span>

                <el-checkbox
                  :model-value="isMenuSelected(menu.id)"
                  @click.stop
                  @change="toggleSelectMenu(menu.id)"
                />
                <div class="menu-info">
                  <span class="menu-name">{{ menu.menu_name }}</span>
                  <span class="menu-code">{{ menu.menu_code }}</span>
                </div>
                <el-tag v-if="hasRoleMenu(menu.id)" type="success" effect="light" size="small" round>已分配</el-tag>
              </div>

              <!-- 子菜单递归显示 -->
              <div v-if="menu.children && menu.children.length > 0 && isMenuExpanded(menu.id)" class="children">
                <template v-for="child in menu.children" :key="child.id">
                  <div class="menu-item">
                    <div class="menu-row" :class="menuRowClass(child.id)" @click="toggleSelectMenu(child.id)">
                      <button
                        v-if="child.children && child.children.length > 0"
                        class="expand-btn"
                        :class="{ 'is-expanded': isMenuExpanded(child.id) }"
                        @click.stop="toggleExpandMenu(child.id)"
                      >
                        <el-icon :size="12"><CaretRight /></el-icon>
                      </button>
                      <span v-else class="expand-placeholder"></span>

                      <el-checkbox
                        :model-value="isMenuSelected(child.id)"
                        @click.stop
                        @change="toggleSelectMenu(child.id)"
                      />
                      <div class="menu-info">
                        <span class="menu-name">{{ child.menu_name }}</span>
                        <span class="menu-code">{{ child.menu_code }}</span>
                      </div>
                      <el-tag v-if="hasRoleMenu(child.id)" type="success" effect="light" size="small" round>已分配</el-tag>
                    </div>

                    <!-- 三级菜单递归显示 -->
                    <div v-if="child.children && child.children.length > 0 && isMenuExpanded(child.id)" class="children">
                      <div
                        v-for="grandchild in child.children"
                        :key="grandchild.id"
                        class="menu-row"
                        :class="menuRowClass(grandchild.id)"
                        @click="toggleSelectMenu(grandchild.id)"
                      >
                        <span class="expand-placeholder"></span>
                        <el-checkbox
                          :model-value="isMenuSelected(grandchild.id)"
                          @click.stop
                          @change="toggleSelectMenu(grandchild.id)"
                        />
                        <div class="menu-info">
                          <span class="menu-name">{{ grandchild.menu_name }}</span>
                          <span class="menu-code">{{ grandchild.menu_code }}</span>
                        </div>
                        <el-tag v-if="hasRoleMenu(grandchild.id)" type="success" effect="light" size="small" round>已分配</el-tag>
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
    <div class="selector-footer">
      <span class="selected-count">保存后拥有 {{ selectedMenus.length }} 项菜单</span>
      <el-button type="primary" :loading="loading.submit" @click="saveMenus">保存菜单</el-button>
    </div>
  </div>
</template>

<style scoped>
.role-menu-selector {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.selector-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.stats-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px 14px;
  background: var(--app-fill-1);
  border: 1px solid var(--app-border);
  border-radius: 10px;
}

.stat-chip,
.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.stat-chip strong {
  color: var(--el-text-color-primary);
}

.stat-dot,
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot-total {
  background: #94a3b8;
}

.dot-assigned {
  background: var(--el-color-success);
}

.dot-selected {
  background: var(--el-color-primary);
}

.dot-new {
  background: #8b5cf6;
}

.dot-remove {
  background: var(--el-color-danger);
}

.legend-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.legend-item .el-icon {
  color: var(--el-text-color-secondary);
}

.menu-list {
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid var(--app-border);
  border-radius: 12px;
  padding: 12px;
  background: var(--app-fill-2);
}

.list-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 40px 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.menu-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: var(--app-card-bg);
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 6px;
}

.menu-row:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
}

.menu-row.is-assigned {
  border-color: var(--el-color-success-light-5);
  background: var(--el-color-success-light-9);
}

.menu-row.is-selected-new {
  border-color: var(--el-color-primary-light-5);
  background: var(--el-color-primary-light-9);
}

.menu-row.is-removing {
  border-color: var(--el-color-danger-light-5);
  background: var(--el-color-danger-light-9);
}

.menu-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.menu-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-code {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.expand-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: 1px solid var(--app-border);
  border-radius: 6px;
  background: var(--app-card-bg);
  color: var(--el-text-color-secondary);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s;
}

.expand-btn:hover {
  border-color: var(--el-color-primary);
  color: var(--el-color-primary);
}

.expand-btn.is-expanded .el-icon {
  transform: rotate(90deg);
}

.expand-btn .el-icon {
  transition: transform 0.2s;
}

.expand-placeholder {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.children {
  margin-left: 26px;
  padding-left: 12px;
  border-left: 2px solid var(--el-border-color-lighter);
}

.selector-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.selected-count {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
</style>
