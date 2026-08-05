<script setup lang="ts">
import { ref, watch, computed, nextTick, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter, type RouteLocationNormalizedLoaded } from 'vue-router';
import { ElScrollbar } from 'element-plus';
import { ADMIN_HOME_PATH } from '@/config/adminRoute';

const route = useRoute();
const router = useRouter();

interface TagView {
  path: string;
  title: string;
  name?: string;
  fullPath?: string;
}

const visitedViews = ref<TagView[]>([]);
const affixTags = ref<TagView[]>([]);
const visible = ref(false);
const selectedTag = ref<TagView | null>(null);
const menuStyle = ref<Record<string, string>>({});
const scrollPaneRef = ref<InstanceType<typeof ElScrollbar> | null>(null);

// 添加标签
const addVisitedView = (view: RouteLocationNormalizedLoaded) => {
  const isExist = visitedViews.value.some(v => v.path === view.path);
  if (isExist) return;

  const title = (view.meta?.title as string) || 'No Title';
  visitedViews.value.push({
    path: view.path,
    title,
    name: view.name as string,
    fullPath: view.fullPath
  });
};

// 移除标签
const closeSelectedTag = (view: TagView) => {
  const index = visitedViews.value.findIndex(v => v.path === view.path);
  if (index !== -1) {
    visitedViews.value.splice(index, 1);
  }

  if (view.path === route.path) {
    toLastView(visitedViews.value, view);
  }
};

// 关闭其他标签
const closeOthersTags = () => {
  if (!selectedTag.value) return;

  visitedViews.value = visitedViews.value.filter(tag => {
    return tag.path === selectedTag.value?.path || isAffixTag(tag);
  });

  const isCurrentInTags = visitedViews.value.some(tag => tag.path === route.path);
  if (!isCurrentInTags && visitedViews.value.length) {
    router.push(visitedViews.value[0].path);
  }
};

// 关闭所有标签
const closeAllTags = () => {
  visitedViews.value = visitedViews.value.filter(tag => isAffixTag(tag));

  const isCurrentInTags = visitedViews.value.some(tag => tag.path === route.path);
  if (!isCurrentInTags && visitedViews.value.length) {
    router.push(visitedViews.value[0].path);
  } else if (!visitedViews.value.length) {
    router.push(ADMIN_HOME_PATH);
  }
};

// 判断是否为固定标签
const isAffixTag = (tag: TagView) => {
  return affixTags.value.some(affixTag => affixTag.path === tag.path);
};

// 跳转到上一个标签
const toLastView = (views: TagView[], view: TagView) => {
  const latestView = views.slice(-1)[0];
  if (latestView && latestView.path !== view.path) {
    router.push(latestView.path);
  } else {
    router.push(ADMIN_HOME_PATH);
  }
};

// 初始化固定标签
const initTags = () => {
  const routes = router.getRoutes();
  const affixRoutes = routes.filter(route => route.meta?.affix);

  affixTags.value = affixRoutes.map(route => ({
    path: route.path,
    title: (route.meta?.title as string) || 'No Title'
  }));

  affixTags.value.forEach(tag => {
    if (!visitedViews.value.some(v => v.path === tag.path)) {
      visitedViews.value.push(tag);
    }
  });
};

// 处理右键菜单
const openMenu = (tag: TagView, e: MouseEvent) => {
  const menuMinWidth = 105;
  const container = document.querySelector('.tags-view-container') as HTMLElement;
  const offsetLeft = container.getBoundingClientRect().left;
  const offsetWidth = container.offsetWidth;
  const maxLeft = offsetWidth - menuMinWidth;
  const left = e.clientX - offsetLeft + 15;

  selectedTag.value = tag;
  visible.value = true;

  nextTick(() => {
    const contextMenu = document.querySelector('.contextmenu') as HTMLElement;
    if (contextMenu) {
      contextMenu.style.left = `${Math.min(left, maxLeft)}px`;
      contextMenu.style.top = `${e.clientY}px`;
    }
  });
};

// 关闭右键菜单
const closeMenu = () => {
  visible.value = false;
};

watch(
  () => route.path,
  () => {
    addVisitedView(route);
  }
);

onMounted(() => {
  initTags();
  addVisitedView(route);
  document.addEventListener('click', closeMenu);
});

onUnmounted(() => {
  document.removeEventListener('click', closeMenu);
});
</script>

<template>
  <div class="tags-view-container">
    <el-scrollbar ref="scrollPaneRef" class="tags-view-wrapper">
      <div class="tags-view-item-wrapper">
        <router-link
          v-for="tag in visitedViews"
          :key="tag.path"
          :to="tag.path"
          class="tags-view-item"
          :class="{ active: tag.path === route.path }"
          @contextmenu.prevent="openMenu(tag, $event)"
        >
          <span class="tag-dot" v-if="tag.path === route.path"></span>
          {{ tag.title }}
          <el-icon
            v-if="!isAffixTag(tag)"
            class="close-icon"
            @click.prevent.stop="closeSelectedTag(tag)"
          >
            <Close />
          </el-icon>
        </router-link>
      </div>
    </el-scrollbar>

    <!-- 右键菜单 -->
    <div v-show="visible" class="contextmenu" @click="closeMenu">
      <ul>
        <li @click="closeSelectedTag(selectedTag!)">
          <el-icon><Close /></el-icon>
          关闭
        </li>
        <li @click="closeOthersTags">
          <el-icon><CircleClose /></el-icon>
          关闭其他
        </li>
        <li @click="closeAllTags">
          <el-icon><FolderDelete /></el-icon>
          关闭所有
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.tags-view-container {
  height: 38px;
  width: 100%;
  flex-shrink: 0;
  background: var(--app-header-bg);
  border-bottom: 1px solid var(--app-border);
  display: flex;
  align-items: center;
  transition:
    background-color 0.25s ease,
    border-color 0.25s ease;
}

.tags-view-wrapper {
  height: 100%;
  width: 100%;
  white-space: nowrap;
}

.tags-view-item-wrapper {
  padding: 5px 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.tags-view-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  height: 26px;
  line-height: 26px;
  border: 1px solid var(--app-border);
  color: var(--el-text-color-regular);
  background: var(--app-card-bg);
  padding: 0 10px;
  font-size: 12px;
  border-radius: 7px;
  text-decoration: none;
  transition: all 0.2s ease;
  user-select: none;
}

.tags-view-item:hover {
  border-color: var(--el-color-primary-light-5);
  color: var(--brand-primary);
}

.tags-view-item.active {
  background: var(--brand-primary-light);
  color: var(--brand-primary);
  border-color: var(--el-color-primary-light-5);
  font-weight: 600;
}

.tag-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--brand-primary);
  flex-shrink: 0;
}

.close-icon {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  text-align: center;
  transition: all 0.2s;
  color: var(--el-text-color-placeholder);
}

.close-icon:hover {
  background: var(--brand-primary);
  color: var(--app-sidebar-active-text);
}

.contextmenu {
  position: fixed;
  z-index: 3000;
  background: var(--app-card-bg);
  border: 1px solid var(--app-border);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
  padding: 5px;
  min-width: 120px;
}

.contextmenu ul {
  margin: 0;
  padding: 0;
  list-style-type: none;
}

.contextmenu ul li {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  color: var(--el-text-color-regular);
  border-radius: 6px;
  transition: background 0.15s;
}

.contextmenu ul li:hover {
  background: var(--brand-primary-light);
  color: var(--brand-primary);
}
</style>
