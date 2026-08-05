<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { Lightning, CircleCheck, CircleClose, Refresh, Plus, Search } from '@element-plus/icons-vue';
import { rateLimitService } from '@/services/rateLimitService';
import type { RateLimitConfig, RateLimitStats, ListEntry, RateLimitScope } from '@/services/rateLimitService';

// 状态
const loading = ref(false);
const savingConfig = ref(false);
const activeTab = ref('config');

// 限流配置
const rateLimitConfig = reactive<RateLimitConfig>({
  enabled: true,
  algorithm: 'token_bucket',
  storage: 'redis',
  default_requests: 100,
  default_burst: 10,
  block_duration: 60,
  enable_whitelist: true,
  enable_blacklist: true,
  log_violations: true
});

// 白名单数据
const whitelist = ref<ListEntry[]>([]);
const whitelistLoading = ref(false);
const whitelistTotal = ref(0);

// 黑名单数据
const blacklist = ref<ListEntry[]>([]);
const blacklistLoading = ref(false);
const blacklistTotal = ref(0);

// 限流统计
const rateLimitStats = ref<RateLimitStats>({
  scope: '',
  identifier: '',
  rate_limit_key: '',
  whitelisted: false,
  blacklisted: false
});

// 检查表单
const checkForm = reactive({
  scope: 'global' as RateLimitScope,
  identifier: '',
  endpoint: '',
  user_id: ''
});

// 添加白名单表单
const whitelistForm = reactive({
  identifier: '',
  expire_time: 3600
});

// 添加黑名单表单
const blacklistForm = reactive({
  identifier: '',
  expire_time: 3600
});

// 限流作用域选项
const scopeOptions = [
  { label: '全局', value: 'global' },
  { label: 'IP地址', value: 'ip' },
  { label: '用户', value: 'user' },
  { label: 'API端点', value: 'endpoint' },
  { label: 'IP+用户', value: 'ip_user' },
  { label: 'IP+端点', value: 'ip_endpoint' },
  { label: '用户+端点', value: 'user_endpoint' }
];

// 算法选项
const algorithmOptions = [
  { label: '令牌桶', value: 'token_bucket' },
  { label: '滑动窗口', value: 'sliding_window' },
  { label: '固定窗口', value: 'fixed_window' }
];

// 存储选项
const storageOptions = [
  { label: 'Redis', value: 'redis' }
];

// 获取限流配置
const loadRateLimitConfig = async () => {
  try {
    loading.value = true;
    const response = await rateLimitService.getRateLimitConfig();

    if (response.code === 200) {
      Object.assign(rateLimitConfig, response.data);
    } else {
      ElMessage.error('获取限流配置失败: ' + response.message);
    }
  } catch (error) {
    console.error('获取限流配置出错:', error);
    ElMessage.error('获取限流配置出错');
  } finally {
    loading.value = false;
  }
};

// 保存限流配置
const saveRateLimitConfig = async () => {
  try {
    savingConfig.value = true;
    const response = await rateLimitService.updateRateLimitConfig({ ...rateLimitConfig });

    if (response.code === 200) {
      Object.assign(rateLimitConfig, response.data);
      ElMessage.success('限流配置已保存并生效');
    } else {
      ElMessage.error('保存限流配置失败: ' + response.message);
    }
  } catch (error) {
    console.error('保存限流配置出错:', error);
    ElMessage.error('保存限流配置出错');
  } finally {
    savingConfig.value = false;
  }
};

// 获取白名单
const loadWhitelist = async () => {
  try {
    whitelistLoading.value = true;
    const response = await rateLimitService.getWhitelist();

    if (response.code === 200) {
      whitelist.value = response.data || [];
      whitelistTotal.value = whitelist.value.length;
    } else {
      ElMessage.error('获取白名单失败: ' + response.message);
    }
  } catch (error) {
    console.error('获取白名单出错:', error);
    ElMessage.error('获取白名单出错');
  } finally {
    whitelistLoading.value = false;
  }
};

// 获取黑名单
const loadBlacklist = async () => {
  try {
    blacklistLoading.value = true;
    const response = await rateLimitService.getBlacklist();

    if (response.code === 200) {
      blacklist.value = response.data || [];
      blacklistTotal.value = blacklist.value.length;
    } else {
      ElMessage.error('获取黑名单失败: ' + response.message);
    }
  } catch (error) {
    console.error('获取黑名单出错:', error);
    ElMessage.error('获取黑名单出错');
  } finally {
    blacklistLoading.value = false;
  }
};

// 检查限流状态
const checkRateLimit = async () => {
  if (!checkForm.identifier.trim()) {
    ElMessage.warning('请输入标识符');
    return;
  }

  try {
    loading.value = true;
    const response = await rateLimitService.getRateLimitStats(
      checkForm.scope,
      checkForm.identifier.trim(),
      checkForm.endpoint || undefined,
      checkForm.user_id || undefined
    );

    if (response.code === 200) {
      rateLimitStats.value = response.data;
      ElMessage.success('限流检查完成');
    } else {
      ElMessage.error('限流检查失败: ' + response.message);
    }
  } catch (error) {
    console.error('限流检查出错:', error);
    ElMessage.error('限流检查出错');
  } finally {
    loading.value = false;
  }
};

// 添加到白名单
const addToWhitelist = async () => {
  if (!whitelistForm.identifier.trim()) {
    ElMessage.warning('请输入标识符');
    return;
  }

  try {
    const response = await rateLimitService.addToWhitelist(
      whitelistForm.identifier.trim(),
      whitelistForm.expire_time
    );

    if (response.code === 200) {
      ElMessage.success('添加到白名单成功');
      whitelistForm.identifier = '';
      loadWhitelist();
    } else {
      ElMessage.error('添加到白名单失败: ' + response.message);
    }
  } catch (error) {
    console.error('添加到白名单出错:', error);
    ElMessage.error('添加到白名单出错');
  }
};

// 从白名单移除
const removeFromWhitelist = async (identifier: string) => {
  try {
    const response = await rateLimitService.removeFromWhitelist(identifier);

    if (response.code === 200) {
      ElMessage.success('从白名单移除成功');
      loadWhitelist();
    } else {
      ElMessage.error('从白名单移除失败: ' + response.message);
    }
  } catch (error) {
    console.error('从白名单移除出错:', error);
    ElMessage.error('从白名单移除出错');
  }
};

// 添加到黑名单
const addToBlacklist = async () => {
  if (!blacklistForm.identifier.trim()) {
    ElMessage.warning('请输入标识符');
    return;
  }

  try {
    const response = await rateLimitService.addToBlacklist(
      blacklistForm.identifier.trim(),
      blacklistForm.expire_time
    );

    if (response.code === 200) {
      ElMessage.success('添加到黑名单成功');
      blacklistForm.identifier = '';
      loadBlacklist();
    } else {
      ElMessage.error('添加到黑名单失败: ' + response.message);
    }
  } catch (error) {
    console.error('添加到黑名单出错:', error);
    ElMessage.error('添加到黑名单出错');
  }
};

// 从黑名单移除
const removeFromBlacklist = async (identifier: string) => {
  try {
    const response = await rateLimitService.removeFromBlacklist(identifier);

    if (response.code === 200) {
      ElMessage.success('从黑名单移除成功');
      loadBlacklist();
    } else {
      ElMessage.error('从黑名单移除失败: ' + response.message);
    }
  } catch (error) {
    console.error('从黑名单移除出错:', error);
    ElMessage.error('从黑名单移除出错');
  }
};

// 获取状态标签类型
const getStatusType = (whitelisted: boolean, blacklisted: boolean) => {
  if (whitelisted) return 'success';
  if (blacklisted) return 'danger';
  return 'info';
};

// 获取状态文本
const getStatusText = (whitelisted: boolean, blacklisted: boolean) => {
  if (whitelisted) return '白名单';
  if (blacklisted) return '黑名单';
  return '正常';
};

// 标签页切换
const handleTabClick = (tab: any) => {
  if (tab.props.name === 'whitelist') {
    loadWhitelist();
  } else if (tab.props.name === 'blacklist') {
    loadBlacklist();
  } else if (tab.props.name === 'config') {
    loadRateLimitConfig();
  }
};

onMounted(() => {
  loadRateLimitConfig();
});
</script>

<template>
  <div class="rate-limit-management">
    <div class="page-heading">
      <h1 class="page-heading__title">
        <span class="page-heading__icon"><el-icon><Lightning /></el-icon></span>
        API限流管理
      </h1>
    </div>

    <!-- 限流配置卡片 -->
    <div class="page-card">
      <div class="page-card__header">
        <el-icon><Setting /></el-icon>
        限流配置
      </div>
      <div class="page-card__body">
        <el-form :model="rateLimitConfig" label-position="top" v-loading="loading">
          <div class="switch-row">
            <div class="switch-item">
              <span class="switch-label">启用限流</span>
              <el-switch v-model="rateLimitConfig.enabled" />
            </div>
            <div class="switch-item">
              <span class="switch-label">记录违规</span>
              <el-switch v-model="rateLimitConfig.log_violations" />
            </div>
            <div class="switch-item">
              <span class="switch-label">启用白名单</span>
              <el-switch v-model="rateLimitConfig.enable_whitelist" />
            </div>
            <div class="switch-item">
              <span class="switch-label">启用黑名单</span>
              <el-switch v-model="rateLimitConfig.enable_blacklist" />
            </div>
          </div>

          <div class="config-grid">
            <el-form-item label="限流算法">
              <el-select v-model="rateLimitConfig.algorithm" placeholder="选择限流算法" style="width: 100%">
                <el-option v-for="option in algorithmOptions" :key="option.value" :label="option.label" :value="option.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="存储方式">
              <el-select v-model="rateLimitConfig.storage" placeholder="选择存储方式" style="width: 100%">
                <el-option v-for="option in storageOptions" :key="option.value" :label="option.label" :value="option.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="默认请求数">
              <el-input-number v-model="rateLimitConfig.default_requests" :min="1" :max="10000" controls-position="right" style="width: 100%" />
            </el-form-item>
            <el-form-item label="突发容量">
              <el-input-number v-model="rateLimitConfig.default_burst" :min="1" :max="1000" controls-position="right" style="width: 100%" />
            </el-form-item>
            <el-form-item label="封禁时长（秒）">
              <el-input-number v-model="rateLimitConfig.block_duration" :min="1" :max="86400" controls-position="right" style="width: 100%" />
            </el-form-item>
          </div>

          <div class="action-row">
            <el-button type="primary" :icon="CircleCheck" :loading="savingConfig" :disabled="loading" @click="saveRateLimitConfig">
              保存配置
            </el-button>
            <el-button :icon="Refresh" :disabled="savingConfig || loading" @click="loadRateLimitConfig">
              重新加载
            </el-button>
          </div>
        </el-form>
      </div>
    </div>

    <!-- 限流状态检查 -->
    <div class="page-card">
      <div class="page-card__header">
        <el-icon><Search /></el-icon>
        限流状态检查
      </div>
      <div class="page-card__body">
        <el-form :model="checkForm" label-position="top">
          <div class="config-grid">
            <el-form-item label="作用域">
              <el-select v-model="checkForm.scope" placeholder="选择作用域" style="width: 100%">
                <el-option v-for="option in scopeOptions" :key="option.value" :label="option.label" :value="option.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="标识符">
              <el-input v-model="checkForm.identifier" placeholder="IP地址或用户ID" />
            </el-form-item>
            <el-form-item label="API端点">
              <el-input v-model="checkForm.endpoint" placeholder="可选" />
            </el-form-item>
            <el-form-item label="用户ID">
              <el-input v-model="checkForm.user_id" placeholder="可选" />
            </el-form-item>
          </div>

          <el-button
            type="primary"
            :icon="Search"
            :loading="loading"
            :disabled="!checkForm.identifier.trim()"
            @click="checkRateLimit"
          >
            检查限流状态
          </el-button>
        </el-form>

        <!-- 检查结果 -->
        <div v-if="rateLimitStats.rate_limit_key" class="check-result">
          <div class="check-result-title">检查结果</div>
          <div class="result-grid">
            <div class="result-item">
              <span class="result-label">限流键</span>
              <code class="result-value result-mono">{{ rateLimitStats.rate_limit_key }}</code>
            </div>
            <div class="result-item">
              <span class="result-label">状态</span>
              <el-tag :type="getStatusType(rateLimitStats.whitelisted, rateLimitStats.blacklisted)" effect="light" round>
                {{ getStatusText(rateLimitStats.whitelisted, rateLimitStats.blacklisted) }}
              </el-tag>
            </div>
            <div class="result-item">
              <span class="result-label">作用域</span>
              <span class="result-value">{{ rateLimitStats.scope }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">标识符</span>
              <span class="result-value">{{ rateLimitStats.identifier }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 白名单和黑名单管理 -->
    <div class="page-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="list-tabs">
        <!-- 白名单 -->
        <el-tab-pane label="白名单" name="whitelist">
          <div class="tab-pane">
            <div class="add-form">
              <div class="add-form-title">
                <el-icon><CircleCheck /></el-icon>
                添加白名单
              </div>
              <el-form :model="whitelistForm" inline>
                <el-form-item label="标识符">
                  <el-input v-model="whitelistForm.identifier" placeholder="IP地址或用户ID" style="width: 240px" />
                </el-form-item>
                <el-form-item label="过期时间（秒）">
                  <el-input-number v-model="whitelistForm.expire_time" :min="1" :max="2592000" controls-position="right" style="width: 180px" />
                </el-form-item>
                <el-form-item>
                  <el-button type="success" :icon="Plus" :disabled="!whitelistForm.identifier.trim()" @click="addToWhitelist">
                    添加到白名单
                  </el-button>
                </el-form-item>
              </el-form>
            </div>

            <el-table v-loading="whitelistLoading" :data="whitelist" stripe style="width: 100%">
              <el-table-column prop="identifier" label="标识符" min-width="200">
                <template #default="{ row }">
                  <span class="identifier-cell">{{ row.identifier }}</span>
                </template>
              </el-table-column>
              <el-table-column label="添加时间" min-width="160">
                <template #default="{ row }">{{ row.created_at || '-' }}</template>
              </el-table-column>
              <el-table-column label="过期时间" min-width="120">
                <template #default="{ row }">{{ row.ttl ? row.ttl + ' 秒' : '永久' }}</template>
              </el-table-column>
              <el-table-column label="状态" width="110" align="center">
                <template #default>
                  <el-tag type="success" effect="light" round>
                    <el-icon><CircleCheck /></el-icon>
                    白名单
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button size="small" type="danger" plain :icon="'Delete'" @click="removeFromWhitelist(row.identifier)">
                    移除
                  </el-button>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="暂无白名单数据" />
              </template>
            </el-table>

            <div v-if="whitelistTotal > 0" class="table-total-row">共 {{ whitelistTotal }} 条记录</div>
          </div>
        </el-tab-pane>

        <!-- 黑名单 -->
        <el-tab-pane label="黑名单" name="blacklist">
          <div class="tab-pane">
            <div class="add-form">
              <div class="add-form-title">
                <el-icon><CircleClose /></el-icon>
                添加黑名单
              </div>
              <el-form :model="blacklistForm" inline>
                <el-form-item label="标识符">
                  <el-input v-model="blacklistForm.identifier" placeholder="IP地址或用户ID" style="width: 240px" />
                </el-form-item>
                <el-form-item label="过期时间（秒）">
                  <el-input-number v-model="blacklistForm.expire_time" :min="1" :max="2592000" controls-position="right" style="width: 180px" />
                </el-form-item>
                <el-form-item>
                  <el-button type="danger" :icon="Plus" :disabled="!blacklistForm.identifier.trim()" @click="addToBlacklist">
                    添加到黑名单
                  </el-button>
                </el-form-item>
              </el-form>
            </div>

            <el-table v-loading="blacklistLoading" :data="blacklist" stripe style="width: 100%">
              <el-table-column prop="identifier" label="标识符" min-width="200">
                <template #default="{ row }">
                  <span class="identifier-cell">{{ row.identifier }}</span>
                </template>
              </el-table-column>
              <el-table-column label="添加时间" min-width="160">
                <template #default="{ row }">{{ row.created_at || '-' }}</template>
              </el-table-column>
              <el-table-column label="过期时间" min-width="120">
                <template #default="{ row }">{{ row.ttl ? row.ttl + ' 秒' : '永久' }}</template>
              </el-table-column>
              <el-table-column label="状态" width="110" align="center">
                <template #default>
                  <el-tag type="danger" effect="light" round>
                    <el-icon><CircleClose /></el-icon>
                    黑名单
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="{ row }">
                  <el-button size="small" type="success" plain :icon="'Check'" @click="removeFromBlacklist(row.identifier)">
                    移除
                  </el-button>
                </template>
              </el-table-column>
              <template #empty>
                <el-empty description="暂无黑名单数据" />
              </template>
            </el-table>

            <div v-if="blacklistTotal > 0" class="table-total-row">共 {{ blacklistTotal }} 条记录</div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style scoped>
.rate-limit-management {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.switch-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 8px;
  padding: 16px;
  background: var(--app-fill-1);
  border: 1px solid var(--app-border);
  border-radius: 12px;
}

@media (max-width: 768px) {
  .switch-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

.switch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.switch-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-regular);
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0 16px;
  margin-top: 8px;
}

@media (max-width: 1200px) {
  .config-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .config-grid {
    grid-template-columns: 1fr;
  }
}

.action-row {
  display: flex;
  gap: 10px;
  margin-top: 6px;
}

.check-result {
  margin-top: 22px;
  padding: 18px;
  background: var(--app-fill-1);
  border: 1px solid var(--app-border);
  border-radius: 12px;
}

.check-result-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 14px;
}

.result-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

@media (max-width: 640px) {
  .result-grid {
    grid-template-columns: 1fr;
  }
}

.result-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: var(--app-card-bg);
  border: 1px solid var(--app-border);
  border-radius: 10px;
  padding: 12px 14px;
}

.result-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.result-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.result-mono {
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 12px;
  background: var(--app-fill-3);
  padding: 4px 8px;
  border-radius: 6px;
  word-break: break-all;
}

.list-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
  padding: 0 20px;
  background: var(--app-fill-1);
  border-bottom: 1px solid var(--app-border);
  border-radius: 12px 12px 0 0;
}

.tab-pane {
  padding: 20px;
}

.add-form {
  padding: 16px;
  background: var(--app-fill-1);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  margin-bottom: 18px;
}

.add-form-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 14px;
}

.add-form-title .el-icon {
  color: var(--brand-primary);
}

.identifier-cell {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.table-total-row {
  padding: 12px 4px 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

@media (max-width: 768px) {
  .add-form :deep(.el-form--inline .el-form-item) {
    margin-right: 0;
    width: 100%;
  }

  .add-form :deep(.el-form-item__content),
  .add-form :deep(.el-input),
  .add-form :deep(.el-input-number),
  .add-form :deep(.el-button) {
    width: 100%;
  }
}
</style>
