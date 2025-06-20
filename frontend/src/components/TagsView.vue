<script setup lang="ts">
import { ref, watch, computed, nextTick, onMounted } from 'vue';
import { useRoute, useRouter, type RouteLocationNormalizedLoaded } from 'vue-router';
import { ElScrollbar, ElDropdown, ElDropdownMenu, ElDropdownItem } from 'element-plus';

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
const scrollPaneRef = ref<InstanceType<typeof ElScrollbar> | null>(null);

// 添加标签
const addVisitedView = (view: RouteLocationNormalizedLoaded) => {
  // 检查是否已存在
  const isExist = visitedViews.value.some(v => v.path === view.path);
  if (isExist) return;
  
  // 添加新标签
  const title = view.meta?.title as string || 'No Title';
  visitedViews.value.push({
    path: view.path,
    title: title,
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
  
  // 如果关闭的是当前标签，则跳转到其他标签
  if (view.path === route.path) {
    toLastView(visitedViews.value, view);
  }
};

// 关闭其他标签
const closeOthersTags = () => {
  if (!selectedTag.value) return;
  
  // 过滤出当前选中的标签和固定标签
  visitedViews.value = visitedViews.value.filter(tag => {
    return tag.path === selectedTag.value?.path || isAffixTag(tag);
  });
  
  // 如果当前路由不在剩余标签中，则跳转到第一个标签
  const isCurrentInTags = visitedViews.value.some(tag => tag.path === route.path);
  if (!isCurrentInTags && visitedViews.value.length) {
    router.push(visitedViews.value[0].path);
  }
};

// 关闭所有标签
const closeAllTags = () => {
  // 只保留固定标签
  visitedViews.value = visitedViews.value.filter(tag => isAffixTag(tag));
  
  // 如果当前路由不在剩余标签中，则跳转到第一个标签
  const isCurrentInTags = visitedViews.value.some(tag => tag.path === route.path);
  if (!isCurrentInTags && visitedViews.value.length) {
    router.push(visitedViews.value[0].path);
  } else if (!visitedViews.value.length) {
    router.push('/');
  }
};

// 判断是否为固定标签
const isAffixTag = (tag: TagView) => {
  return affixTags.value.some(affixTag => affixTag.path === tag.path);
};

// 跳转到上一个标签
const toLastView = (visitedViews: TagView[], view: TagView) => {
  const latestView = visitedViews.slice(-1)[0];
  if (latestView && latestView.path !== view.path) {
    router.push(latestView.path);
  } else {
    // 如果没有其他标签，则跳转到首页
    router.push('/');
  }
};

// 初始化固定标签
const initTags = () => {
  const routes = router.getRoutes();
  const affixRoutes = routes.filter(route => route.meta?.affix);
  
  affixTags.value = affixRoutes.map(route => ({
    path: route.path,
    title: route.meta?.title as string || 'No Title'
  }));
  
  // 添加固定标签到访问标签
  affixTags.value.forEach(tag => {
    if (!visitedViews.value.some(v => v.path === tag.path)) {
      visitedViews.value.push(tag);
    }
  });
};

// 处理右键菜单
const openMenu = (tag: TagView, e: MouseEvent) => {
  const menuMinWidth = 105;
  const offsetLeft = (document.querySelector('.tags-view-container') as HTMLElement).getBoundingClientRect().left;
  const offsetWidth = (document.querySelector('.tags-view-container') as HTMLElement).offsetWidth;
  const maxLeft = offsetWidth - menuMinWidth;
  const left = e.clientX - offsetLeft + 15;
  
  selectedTag.value = tag;
  visible.value = true;
  
  nextTick(() => {
    const contextMenu = document.querySelector('.contextmenu') as HTMLElement;
    if (contextMenu) {
      contextMenu.style.left = `${Math.min(left, maxLeft)}px`;
    }
  });
};

// 关闭右键菜单
const closeMenu = () => {
  visible.value = false;
};

// 监听路由变化，添加新标签
watch(
  () => route.path,
  () => {
    addVisitedView(route);
  }
);

// 初始化
onMounted(() => {
  initTags();
  addVisitedView(route);
  
  // 添加点击事件监听器关闭右键菜单
  document.addEventListener('click', closeMenu);
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
    <div 
      v-show="visible" 
      class="contextmenu"
      @click="closeMenu"
    >
      <ul>
        <li @click="closeSelectedTag(selectedTag!)">关闭</li>
        <li @click="closeOthersTags">关闭其他</li>
        <li @click="closeAllTags">关闭所有</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.tags-view-container {
  height: 34px;
  width: 100%;
  background: #fff;
  border-bottom: 1px solid #d8dce5;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.12), 0 0 3px 0 rgba(0, 0, 0, 0.04);
}

.tags-view-wrapper {
  height: 100%;
  width: 100%;
  white-space: nowrap;
}

.tags-view-item-wrapper {
  padding: 0 10px;
  display: inline-block;
}

.tags-view-item {
  display: inline-flex;
  align-items: center;
  margin-right: 5px;
  margin-top: 4px;
  height: 26px;
  line-height: 26px;
  border: 1px solid #d8dce5;
  color: #495060;
  background: #fff;
  padding: 0 8px;
  font-size: 12px;
  border-radius: 3px;
  text-decoration: none;
}

.tags-view-item.active {
  background-color: #42b983;
  color: #fff;
  border-color: #42b983;
}

.close-icon {
  width: 16px;
  height: 16px;
  margin-left: 5px;
  border-radius: 50%;
  text-align: center;
  transition: all .3s cubic-bezier(.645, .045, .355, 1);
  transform-origin: 100% 50%;
}

.close-icon:hover {
  background-color: #b4bccc;
  color: #fff;
}

.contextmenu {
  position: fixed;
  z-index: 3000;
  background: #fff;
  border: 1px solid #cfd4db;
  border-radius: 4px;
  box-shadow: 2px 2px 3px 0 rgba(0, 0, 0, 0.1);
}

.contextmenu ul {
  margin: 0;
  padding: 0;
  list-style-type: none;
}

.contextmenu ul li {
  margin: 0;
  padding: 7px 16px;
  cursor: pointer;
  font-size: 12px;
}

.contextmenu ul li:hover {
  background: #eee;
}
</style> 