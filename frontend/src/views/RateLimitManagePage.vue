<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { Lightning, CircleCheck, CircleClose, Refresh, Plus, Search } from '@element-plus/icons-vue';
import { rateLimitService } from '@/services/rateLimitService';
import type { RateLimitConfig, RateLimitStats, ListEntry, RateLimitScope } from '@/services/rateLimitService';

// 状态
const loading = ref(false);
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
  { label: '用户+端点', value: 'user_endpoint' },
  { label: 'IP+用户+端点', value: 'ip_user_endpoint' }
];

// 算法选项
const algorithmOptions = [
  { label: '令牌桶', value: 'token_bucket' },
  { label: '滑动窗口', value: 'sliding_window' },
  { label: '固定窗口', value: 'fixed_window' }
];

// 存储选项
const storageOptions = [
  { label: 'Redis', value: 'redis' },
  { label: '内存', value: 'memory' },
  { label: '数据库', value: 'database' }
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
    const response = await rateLimitService.checkRateLimit(
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
    <!-- 页面标题 -->
    <h1 class="text-2xl font-bold mb-4">API限流管理</h1>

    <!-- 限流配置卡片 -->
    <div class="bg-white p-4 rounded shadow mb-4">
      <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
        <el-icon><Lightning /></el-icon>
        限流配置
      </h2>

      <el-form :model="rateLimitConfig" label-width="120px" v-loading="loading">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <!-- 启用限流 -->
          <div class="form-group">
            <div class="flex items-center gap-2 mb-2">              <label class="text-sm font-medium text-gray-700">启用限流</label>
              <el-switch v-model="rateLimitConfig.enabled" />
            </div>
          </div>

          <!-- 记录违规 -->
          <div class="form-group">
            <div class="flex items-center gap-2 mb-2">              <label class="text-sm font-medium text-gray-700">记录违规</label>
              <el-switch v-model="rateLimitConfig.log_violations" />
            </div>
          </div>

          <!-- 启用白名单 -->
          <div class="form-group">
            <div class="flex items-center gap-2 mb-2">              <label class="text-sm font-medium text-gray-700">启用白名单</label>
              <el-switch v-model="rateLimitConfig.enable_whitelist" />
            </div>
          </div>

          <!-- 启用黑名单 -->
          <div class="form-group">
            <div class="flex items-center gap-2 mb-2">              <label class="text-sm font-medium text-gray-700">启用黑名单</label>
              <el-switch v-model="rateLimitConfig.enable_blacklist" />
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">          <!-- 限流算法 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">限流算法</label>
            <el-select v-model="rateLimitConfig.algorithm" placeholder="选择限流算法" class="w-full">
              <el-option
                v-for="option in algorithmOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </div>

          <!-- 存储方式 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">存储方式</label>
            <el-select v-model="rateLimitConfig.storage" placeholder="选择存储方式" class="w-full">
              <el-option
                v-for="option in storageOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </div>

          <!-- 默认请求数 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">默认请求数</label>
            <el-input-number
              v-model="rateLimitConfig.default_requests"
              :min="1"
              :max="10000"
              controls-position="right"
              class="w-full"
            />
          </div>

          <!-- 突发容量 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">突发容量</label>
            <el-input-number
              v-model="rateLimitConfig.default_burst"
              :min="1"
              :max="1000"
              controls-position="right"
              class="w-full"
            />
          </div>

          <!-- 封禁时长 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">封禁时长(秒)</label>
            <el-input-number
              v-model="rateLimitConfig.block_duration"
              :min="1"
              :max="86400"
              controls-position="right"
              class="w-full"
            />
          </div>
        </div>
      </el-form>
    </div>

    <!-- 限流状态检查 -->
    <div class="bg-white p-4 rounded shadow mb-4">
      <h2 class="text-lg font-semibold mb-4 flex items-center gap-2">
        <el-icon><Search /></el-icon>
        限流状态检查
      </h2>

      <el-form :model="checkForm" label-width="100px">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">          <!-- 作用域 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">作用域</label>
            <el-select v-model="checkForm.scope" placeholder="选择作用域" class="w-full">
              <el-option
                v-for="option in scopeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </div>

          <!-- 标识符 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">标识符</label>
            <el-input v-model="checkForm.identifier" placeholder="IP地址或用户ID" class="w-full" />
          </div>

          <!-- API端点 -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">API端点</label>
            <el-input v-model="checkForm.endpoint" placeholder="可选" class="w-full" />
          </div>

          <!-- 用户ID -->
          <div class="form-group">
            <label class="block text-sm font-medium text-gray-700 mb-2">用户ID</label>
            <el-input v-model="checkForm.user_id" placeholder="可选" class="w-full" />
          </div>
        </div>

        <div class="mt-4">
          <button
            @click="checkRateLimit"
            :disabled="loading || !checkForm.identifier.trim()"
            class="bg-indigo-600 text-white py-2 px-6 rounded hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150 flex items-center gap-2"
          >
            <el-icon v-if="!loading"><Search /></el-icon>
            <span v-if="loading">检查中...</span>
            <span v-else>检查限流状态</span>
          </button>
        </div>
      </el-form>

      <!-- 检查结果 -->
      <div v-if="rateLimitStats.rate_limit_key" class="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 class="text-md font-semibold mb-3">检查结果</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">          <div class="bg-white p-3 rounded border">
            <label class="text-sm font-medium text-gray-600">限流键</label>
            <div class="text-sm font-mono bg-gray-100 p-2 rounded mt-1">{{ rateLimitStats.rate_limit_key }}</div>
          </div>

          <div class="bg-white p-3 rounded border">
            <label class="text-sm font-medium text-gray-600">状态</label>
            <div class="mt-1">
              <el-tag :type="getStatusType(rateLimitStats.whitelisted, rateLimitStats.blacklisted)">
                {{ getStatusText(rateLimitStats.whitelisted, rateLimitStats.blacklisted) }}
              </el-tag>
            </div>
          </div>

          <div class="bg-white p-3 rounded border">
            <label class="text-sm font-medium text-gray-600">作用域</label>
            <div class="text-sm mt-1">{{ rateLimitStats.scope }}</div>
          </div>

          <div class="bg-white p-3 rounded border">
            <label class="text-sm font-medium text-gray-600">标识符</label>
            <div class="text-sm mt-1">{{ rateLimitStats.identifier }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 白名单和黑名单管理 -->
    <div class="bg-white rounded shadow overflow-hidden">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick" class="rate-limit-tabs">        <!-- 白名单 -->
        <el-tab-pane label="白名单" name="whitelist">          <div class="p-4">            <!-- 添加白名单表单 -->
            <div class="bg-gray-50 p-4 rounded mb-4">              <h3 class="text-md font-semibold mb-3 flex items-center gap-2">
                <el-icon><CircleCheck /></el-icon>
                添加白名单
              </h3>

              <el-form :model="whitelistForm" label-width="100px">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">                  <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">标识符</label>
                    <el-input v-model="whitelistForm.identifier" placeholder="IP地址或用户ID" class="w-full" />
                  </div>

                  <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">过期时间(秒)</label>
                    <el-input-number
                      v-model="whitelistForm.expire_time"
                      :min="1"
                      :max="2592000"
                      controls-position="right"
                      class="w-full"
                    />
                  </div>

                  <div class="form-group flex items-end">
                    <button
                      @click="addToWhitelist"
                      :disabled="!whitelistForm.identifier.trim()"
                      class="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150 flex items-center gap-2 w-full"
                    >
                      <el-icon><Plus /></el-icon>
                      添加到白名单
                    </button>
                  </div>
                </div>
              </el-form>
            </div>

            <!-- 白名单表格 -->
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">标识符</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">添加时间</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">过期时间</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-if="whitelistLoading">
                    <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                      <div class="flex justify-center items-center">
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        加载中...
                      </div>
                    </td>
                  </tr>

                  <tr v-else-if="whitelist.length === 0">
                    <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                      暂无白名单数据
                    </td>
                  </tr>

                  <tr v-for="item in whitelist" :key="item.identifier" class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ item.identifier }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.created_at }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.expire_time ? item.expire_time + '秒' : '永久' }}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <el-tag type="success" size="small">
                        <el-icon><CircleCheck /></el-icon>
                        白名单
                      </el-tag>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        @click="removeFromWhitelist(item.identifier)"
                        class="text-red-600 hover:text-red-900 hover:underline transition duration-150"
                      >
                        移除
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="bg-gray-50 px-4 py-3 border-t border-gray-200 sm:px-6" v-if="whitelistTotal > 0">
              <div class="flex justify-between items-center">
                <div class="text-sm text-gray-700">
                  共 <span class="font-medium">{{ whitelistTotal }}</span> 条记录
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 黑名单 -->
        <el-tab-pane label="黑名单" name="blacklist">          <div class="p-4">            <!-- 添加黑名单表单 -->
            <div class="bg-gray-50 p-4 rounded mb-4">              <h3 class="text-md font-semibold mb-3 flex items-center gap-2">
                <el-icon><CircleClose /></el-icon>
                添加黑名单
              </h3>

              <el-form :model="blacklistForm" label-width="100px">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">                  <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">标识符</label>
                    <el-input v-model="blacklistForm.identifier" placeholder="IP地址或用户ID" class="w-full" />
                  </div>

                  <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700 mb-2">过期时间(秒)</label>
                    <el-input-number
                      v-model="blacklistForm.expire_time"
                      :min="1"
                      :max="2592000"
                      controls-position="right"
                      class="w-full"
                    />
                  </div>

                  <div class="form-group flex items-end">
                    <button
                      @click="addToBlacklist"
                      :disabled="!blacklistForm.identifier.trim()"
                      class="bg-orange-600 text-white py-2 px-4 rounded hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition duration-150 flex items-center gap-2 w-full"
                    >
                      <el-icon><Plus /></el-icon>
                      添加到黑名单
                    </button>
                  </div>
                </div>
              </el-form>
            </div>

            <!-- 黑名单表格 -->
            <div class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">标识符</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">添加时间</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">过期时间</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-if="blacklistLoading">
                    <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                      <div class="flex justify-center items-center">
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        加载中...
                      </div>
                    </td>
                  </tr>

                  <tr v-else-if="blacklist.length === 0">
                    <td colspan="5" class="px-6 py-4 text-center text-gray-500">
                      暂无黑名单数据
                    </td>
                  </tr>

                  <tr v-for="item in blacklist" :key="item.identifier" class="hover:bg-gray-50 transition-colors">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ item.identifier }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.created_at }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.expire_time ? item.expire_time + '秒' : '永久' }}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <el-tag type="danger" size="small">
                        <el-icon><CircleClose /></el-icon>
                        黑名单
                      </el-tag>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        @click="removeFromBlacklist(item.identifier)"
                        class="text-green-600 hover:text-green-900 hover:underline transition duration-150"
                      >
                        移除
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="bg-gray-50 px-4 py-3 border-t border-gray-200 sm:px-6" v-if="blacklistTotal > 0">
              <div class="flex justify-between items-center">
                <div class="text-sm text-gray-700">
                  共 <span class="font-medium">{{ blacklistTotal }}</span> 条记录
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style scoped>
.rate-limit-management {
  padding: 20px;
}

.form-group {
  margin-bottom: 1rem;
}

.rate-limit-tabs :deep(.el-tabs__content) {
  overflow: visible;
}

:deep(.el-input-number) {
  width: 100% !important;
}

:deep(.el-select) {
  width: 100%;
}

:deep(.el-tag .el-icon) {
  margin-right: 4px;
}

@media (max-width: 768px) {
  .rate-limit-management {
    padding: 10px;
  }
}
</style>