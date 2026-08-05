<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { Document, Refresh, FullScreen } from '@element-plus/icons-vue';

// 状态
const loading = ref(false);
const swaggerUrl = ref('');
const iframeLoadError = ref(false);

// 获取Swagger UI URL
const loadSwaggerUrl = () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8090';
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
    <div class="page-card swagger-header">
      <div class="header-content">
        <div class="title-section">
          <span class="title-icon"><el-icon :size="20"><Document /></el-icon></span>
          <div>
            <h1 class="page-title">API 文档</h1>
            <p class="page-sub">Swagger UI - 自动生成的接口文档</p>
          </div>
        </div>
        <div class="header-actions">
          <el-button type="primary" :icon="Document" @click="openInNewTab" :disabled="!swaggerUrl || iframeLoadError">
            新窗口打开
          </el-button>
          <el-button :icon="Refresh" :loading="loading" @click="refreshSwagger">刷新</el-button>
          <el-button :icon="FullScreen" @click="goFullscreen" :disabled="!swaggerUrl || iframeLoadError">全屏</el-button>
        </div>
      </div>
    </div>

    <!-- Swagger UI 容器 -->
    <div class="swagger-container">
      <div class="swagger-card">
        <div v-if="swaggerUrl" v-loading="loading" class="iframe-wrapper">
          <div class="url-bar">
            <span class="url-dot"></span>
            <code>{{ swaggerUrl }}</code>
          </div>
          <iframe
            :src="swaggerUrl"
            frameborder="0"
            width="100%"
            height="100%"
            class="swagger-iframe"
            allowfullscreen
            @load="handleIframeLoad"
            @error="handleIframeError"
          ></iframe>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="iframeLoadError" class="error-state">
          <el-result icon="error" title="API文档加载失败" sub-title="无法加载API文档，请检查后端服务是否正常运行">
            <template #extra>
              <el-button type="primary" :icon="Refresh" @click="refreshSwagger">重新加载</el-button>
            </template>
          </el-result>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.swagger-ui-page {
  height: calc(100vh - 154px);
  min-height: 480px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.swagger-header {
  flex-shrink: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  flex-wrap: wrap;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--brand-primary-light);
  color: var(--brand-primary);
}

.page-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.page-sub {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.swagger-container {
  flex: 1;
  min-height: 0;
}

.swagger-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--app-card-bg);
  border: 1px solid var(--app-border);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
}

.iframe-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.url-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: var(--app-fill-1);
  border-bottom: 1px solid var(--app-border);
  flex-shrink: 0;
}

.url-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--el-color-success);
  flex-shrink: 0;
}

.url-bar code {
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.swagger-iframe {
  flex: 1;
  width: 100%;
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

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }
}
</style>
