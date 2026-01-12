<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { Document, Refresh, FullScreen } from '@element-plus/icons-vue';

// 状态
const loading = ref(false);
const swaggerUrl = ref('');
const iframeLoadError = ref(false);

// 计算iframe高度 - 使用CSS变量来适应父容器
const iframeHeight = computed(() => {
  // 让iframe填满可用空间，通过CSS来处理具体高度
  return '100%';
});

// 获取Swagger UI URL
const loadSwaggerUrl = () => {
  // 使用后端提供的Swagger UI地址
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  swaggerUrl.value = `${baseUrl}/api/docs`;
  iframeLoadError.value = false;
};

// 处理iframe加载事件
const handleIframeLoad = () => {
  loading.value = false;
  iframeLoadError.value = false;
  ElMessage.success('API文档加载完成');
};

// 处理iframe加载错误
const handleIframeError = () => {
  loading.value = false;
  iframeLoadError.value = true;
  ElMessage.error('API文档加载失败，请检查后端服务是否正常运行');
};

// 在新标签页中打开Swagger UI
const openInNewTab = () => {
  if (swaggerUrl.value) {
    window.open(swaggerUrl.value, '_blank');
  }
};

// 刷新iframe
const refreshSwagger = () => {
  loading.value = true;
  iframeLoadError.value = false;
  const iframe = document.querySelector('iframe') as HTMLIFrameElement;
  if (iframe) {
    iframe.src = iframe.src;
  } else {
    loadSwaggerUrl();
  }
};

// 全屏显示
const goFullscreen = () => {
  const iframe = document.querySelector('iframe') as HTMLIFrameElement;
  if (iframe) {
    if (iframe.requestFullscreen) {
      iframe.requestFullscreen();
    } else if ((iframe as any).webkitRequestFullscreen) {
      (iframe as any).webkitRequestFullscreen();
    } else if ((iframe as any).mozRequestFullScreen) {
      (iframe as any).mozRequestFullScreen();
    } else if ((iframe as any).msRequestFullscreen) {
      (iframe as any).msRequestFullscreen();
    }
  }
};

onMounted(() => {
  loading.value = true;
  loadSwaggerUrl();
});
</script>

<template>
  <div class="swagger-ui-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <el-icon size="24"><Document /></el-icon>
          <h1 class="page-title">API 文档</h1>
        </div>
        <div class="header-actions">
          <el-button
            type="primary"
            :icon="Document"
            @click="openInNewTab"
            :disabled="!swaggerUrl || iframeLoadError"
          >
            新窗口打开
          </el-button>
          <el-button
            type="info"
            @click="refreshSwagger"
            :loading="loading"
            :icon="Refresh"
          >
            刷新
          </el-button>
          <el-button
            type="warning"
            @click="goFullscreen"
            :icon="FullScreen"
            :disabled="!swaggerUrl || iframeLoadError"
          >
            全屏
          </el-button>
        </div>
      </div>
    </div>

    <!-- Swagger UI 容器 -->
    <div class="swagger-container">
      <el-card v-loading="loading" class="swagger-card">
        <template #header>
          <div class="card-header">
            <span>Swagger UI - API 接口文档</span>
            <el-tag type="info" size="small" v-if="swaggerUrl">
              {{ swaggerUrl }}
            </el-tag>
          </div>
        </template>

        <!-- iframe 容器 -->
        <div class="iframe-wrapper" v-if="swaggerUrl">
          <iframe
            :src="swaggerUrl"
            frameborder="0"
            width="100%"
            height="100%"
            @load="handleIframeLoad"
            @error="handleIframeError"
            class="swagger-iframe"
            allowfullscreen
          ></iframe>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="iframeLoadError" class="error-state">
          <el-empty description="API文档加载失败">
            <template #description>
              <p class="text-gray-600 mb-4">无法加载API文档，请检查后端服务是否正常运行</p>
            </template>
            <el-button type="primary" @click="refreshSwagger" :icon="Refresh">
              重新加载
            </el-button>
          </el-empty>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.swagger-ui-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 0;
}

.page-header {
  background: #fff;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.swagger-container {
  flex: 1;
  overflow: hidden;
  padding: 20px;
}

.swagger-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.iframe-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
  min-height: 600px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.swagger-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #fff;
}

.error-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .swagger-container {
    padding: 10px;
  }
}

/* 加载动画 */
:deep(.el-loading-spinner) {
  top: 50%;
  transform: translateY(-50%);
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .page-header {
    background: #1f1f1f;
    border-bottom-color: #303133;
  }

  .page-title {
    color: #e8e8e8;
  }

  .iframe-wrapper {
    border-color: #303133;
  }
}
</style>