import { ref } from 'vue';

export type ThemeMode = 'light' | 'dark' | 'auto';

const STORAGE_KEY = 'app-theme-mode';
const media = window.matchMedia('(prefers-color-scheme: dark)');

// 当前模式：light / dark / auto
const themeMode = ref<ThemeMode>(
  (localStorage.getItem(STORAGE_KEY) as ThemeMode) || 'auto'
);

function applyTheme() {
  const resolved: 'light' | 'dark' =
    themeMode.value === 'auto'
      ? media.matches
        ? 'dark'
        : 'light'
      : themeMode.value;

  const root = document.documentElement;
  root.setAttribute('data-theme', resolved);
  root.classList.toggle('dark', resolved === 'dark');
}

// 初始化
applyTheme();

// 系统主题变化时自动跟随
media.addEventListener('change', () => {
  if (themeMode.value === 'auto') {
    applyTheme();
  }
});

export function setThemeMode(mode: ThemeMode) {
  themeMode.value = mode;
  localStorage.setItem(STORAGE_KEY, mode);
  applyTheme();
}

export function getThemeMode() {
  return themeMode;
}
