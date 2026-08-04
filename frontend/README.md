# 🚀 Fast Full Stack Demo - 前端

<p align="center">
  <img src="https://img.shields.io/badge/Vue-3.5+-brightgreen.svg" alt="Vue 3.5+">
  <img src="https://img.shields.io/badge/TypeScript-5.8+-blue.svg" alt="TypeScript 5.8+">
  <img src="https://img.shields.io/badge/Vite-6.2+-yellow.svg" alt="Vite 6.2+">
  <img src="https://img.shields.io/badge/Element%20Plus-2.10+-red.svg" alt="Element Plus 2.10+">
  <img src="https://img.shields.io/badge/Pinia-3.0+-orange.svg" alt="Pinia 3.0+">
</p>

<p align="center">
  基于 Vue 3 + TypeScript + Vite 的企业级管理后台前端框架
</p>

## ✨ 项目特性

- 🎯 **现代化技术栈** - Vue 3.5 + TypeScript 5.8 + Vite 6.2
- 🔐 **企业级权限管理** - JWT认证 + RBAC权限控制 + 动态路由
- 🎨 **专业UI设计** - Element Plus + Tailwind CSS 双样式体系
- 📱 **响应式布局** - 完美适配PC、平板、手机多端设备
- ⚡ **高性能构建** - Vite构建，热更新秒级响应
- 🛡️ **类型安全** - 全链路TypeScript支持，开发体验极佳
- 🧪 **完整测试体系** - Vitest单元测试 + Cypress E2E测试
- 🌍 **国际化支持** - 预留多语言扩展能力

## 🏗️ 技术架构

### 核心技术
- **前端框架**: [Vue 3.5.13](https://vuejs.org/) - 渐进式JavaScript框架
- **构建工具**: [Vite 6.2.1](https://vitejs.dev/) - 下一代前端构建工具
- **类型系统**: [TypeScript 5.8](https://www.typescriptlang.org/) - JavaScript的超集
- **路由管理**: [Vue Router 4.5.0](https://router.vuejs.org/) - 官方路由管理器
- **状态管理**: [Pinia 3.0.1](https://pinia.vuejs.org/) - Vue官方状态管理库

### UI框架
- **组件库**: [Element Plus 2.10.2](https://element-plus.org/) - 企业级Vue 3组件库
- **样式框架**: [Tailwind CSS 3.4.1](https://tailwindcss.com/) - 实用优先的CSS框架
- **图标系统**: [@element-plus/icons-vue 2.3.1](https://element-plus.org/en-US/component/icon.html)

### 开发工具
- **代码检查**: [ESLint 9.21.0](https://eslint.org/) + [@vue/eslint-config-typescript](https://www.npmjs.com/package/@vue/eslint-config-typescript)
- **代码格式化**: [Prettier 3.5.3](https://prettier.io/) - 代码格式化工具
- **类型检查**: [vue-tsc](https://github.com/vuejs/language-tools) - Vue TypeScript检查工具

### 测试框架
- **单元测试**: [Vitest 3.0.8](https://vitest.dev/) - 极速单元测试框架
- **端到端测试**: [Cypress 14.1.0](https://www.cypress.io/) - E2E测试工具
- **组件测试**: [@vue/test-utils 2.4.6](https://test-utils.vuejs.org/) - Vue测试工具库

## 📁 项目结构

```
frontend/
├── src/                    # 源代码目录
│   ├── api/               # API接口服务层
│   ├── assets/            # 静态资源(CSS, 图片, 字体等)
│   │   └── svgs/          # SVG图标资源
│   ├── components/        # 公共Vue组件
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia状态管理
│   ├── services/         # 业务接口服务
│   ├── utils/            # 工具函数
│   ├── views/            # 页面视图组件
│   ├── App.vue           # 根组件
│   └── main.ts           # 应用入口文件
├── .env*                  # 环境变量配置
├── cypress.config.ts      # Cypress E2E配置
├── eslint.config.ts       # ESLint配置
├── vite.config.ts         # Vite构建配置
├── tailwind.config.js     # Tailwind CSS配置
├── tsconfig.json          # TypeScript配置
└── package.json           # 项目依赖配置
```

### 推荐的IDE设置

<table>
<tr>
  <td width="200px"><p align="center"><a href="https://code.visualstudio.com/"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/vscode/vscode-original.svg" alt="VSCode" width="40" height="40"></a></p></td>
  <td>
    <strong>Visual Studio Code</strong> - 推荐安装的扩展：
    <ul>
      <li><a href="https://marketplace.visualstudio.com/items?itemName=Vue.volar">Volar</a> - Vue 3官方插件（必须，禁用Vetur）</li>
      <li><a href="https://marketplace.visualstudio.com/items?itemName=Vue.vscode-typescript-vue-plugin">TypeScript Vue Plugin</a> - TypeScript支持</li>
      <li><a href="https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss">Tailwind CSS IntelliSense</a> - Tailwind智能提示</li>
      <li><a href="https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode">Prettier</a> - 代码格式化</li>
      <li><a href="https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint">ESLint</a> - 代码检查</li>
    </ul>
  </td>
</tr>
</table>

### 开发环境要求

- **Node.js**: >= 18.0.0
- **npm**: >= 8.0.0
- **Git**: >= 2.20.0

### TypeScript配置

本项目使用 <code>vue-tsc</code> 进行类型检查，确保在VSCode中安装 <strong>Volar</strong> 插件以获得最佳的TypeScript支持。

> **💡 提示**: 禁用Vetur插件以避免与Volar冲突。

### 环境变量配置

项目支持多环境配置，复制对应的环境文件：

```bash
cp .env.example .env.development  # 开发环境
cp .env.example .env.production   # 生产环境
```

环境变量说明：

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `VITE_API_BASE_URL` | API基础URL | `http://localhost:8090` |
| `VITE_OAUTH_CLIENT_ID` | OAuth2公开客户端ID | `frontend` |

> `VITE_` 环境变量会被打包到前端产物中，不要在这里配置 OAuth client secret、数据库密码、JWT 密钥等敏感信息。

## 🚀 快速开始

### 📦 安装依赖

```bash
# 使用npm
npm install

# 或使用yarn
yarn install

# 或使用pnpm（推荐）
pnpm install
```

### 🔥 启动开发服务器

```bash
npm run dev
```

启动后访问: http://localhost:5173

### 📋 可用脚本

| 命令 | 说明 | 输出位置 |
|------|------|----------|
| `npm run dev` | 启动开发服务器 | http://localhost:5173 |
| `npm run build` | 构建生产版本 | `dist/` 目录 |
| `npm run preview` | 预览生产构建 | http://localhost:4173 |
| `npm run test:unit` | 运行单元测试 | 控制台输出 |
| `npm run test:e2e` | 运行E2E测试 | 控制台输出 |
| `npm run test:e2e:dev` | 开发环境E2E测试 | Cypress UI |
| `npm run lint` | 代码检查 | 控制台输出 |
| `npm run lint:fix` | 自动修复代码问题 | 控制台输出 |
| `npm run type-check` | TypeScript类型检查 | 控制台输出 |

### 🏗️ 构建与部署

#### 开发环境构建
```bash
# 启动开发服务器（带热更新）
npm run dev
```

#### 生产环境构建
```bash
# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

#### 环境变量
构建时会根据模式自动加载对应的环境变量文件：
- `.env.development` - 开发环境
- `.env.production` - 生产环境
- `.env.staging` - 预发布环境

### 🧪 测试

#### 单元测试
```bash
# 运行所有单元测试
npm run test:unit

# 运行指定测试文件
npm run test:unit -- --run path/to/test.spec.ts

# 监听模式
npm run test:unit -- --watch
```

#### E2E测试
```bash
# 开发环境E2E测试（带UI界面）
npm run test:e2e:dev

# 生产环境E2E测试（无头模式）
npm run build
npm run test:e2e

# 打开Cypress UI
npx cypress open
```

### 🔍 代码质量检查

```bash
# 运行ESLint检查
npm run lint

# 自动修复ESLint问题
npm run lint:fix

# TypeScript类型检查
npm run type-check

# 运行所有检查（推荐在提交前执行）
npm run lint && npm run type-check
```

## 🔗 后端集成

### API配置

项目使用axios进行HTTP请求，基础配置在 `src/api/client.ts` 中：

- **基础URL**: 通过环境变量 `VITE_API_BASE_URL` 配置
- **超时时间**: 默认15秒
- **认证方式**: JWT Token
- **错误处理**: 统一错误拦截和处理

### 环境要求

确保后端服务已启动并可访问：

```bash
# 开发环境（默认）
http://localhost:8090

# 生产环境
https://your-api-domain.com
```

### 跨域配置

如果前后端分离部署，需要在后端配置CORS：

```javascript
// 允许的跨域源
Access-Control-Allow-Origin: http://localhost:5173

// 允许的请求方法
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS

// 允许的请求头
Access-Control-Allow-Headers: Content-Type, Authorization
```

### 认证流程

1. **登录**: 用户登录获取JWT token
2. **Token存储**: 存储在localStorage中
3. **请求拦截**: 自动在请求头中添加Authorization
4. **Token刷新**: 自动刷新过期token
5. **登出**: 清除token并跳转登录页

## 🌟 核心功能

### 🔐 认证与权限
- **JWT认证**: Token-based身份验证
- **RBAC权限**: 基于角色的访问控制
- **动态路由**: 根据权限动态生成路由
- **菜单管理**: 支持多级菜单和权限过滤

### 📊 状态管理
- **Pinia状态库**: 现代化状态管理
- **模块化设计**: 状态按业务模块划分
- **类型安全**: 完整的TypeScript支持
- **持久化存储**: 支持状态本地持久化

### 🎨 UI/UX特性
- **Element Plus**: 企业级Vue 3组件库
- **Tailwind CSS**: 实用优先的样式框架
- **响应式设计**: 适配多种屏幕尺寸
- **暗色主题**: 支持明暗主题切换
- **国际化**: 预留多语言支持

### ⚡ 性能优化
- **代码分割**: 路由级别代码分割
- **组件懒加载**: 按需加载组件
- **Tree Shaking**: 消除未使用代码
- **Gzip压缩**: 资源压缩优化
- **CDN加速**: 支持CDN资源加载

## 📚 开发指南

### 代码规范

- **命名规范**: 组件使用PascalCase，变量使用camelCase
- **文件组织**: 按功能模块组织文件
- **TypeScript**: 严格模式，强制类型定义
- **ESLint规则**: 遵循Vue和TypeScript最佳实践

### 组件开发

```typescript
// 推荐的组件结构
<script setup lang="ts">
import { ref, computed } from 'vue'

// 类型定义
interface Props {
  title: string
  visible?: boolean
}

// 组件props
const props = withDefaults(defineProps<Props>(), {
  visible: true
})

// 组件emit
const emit = defineEmits<{
  update: [value: string]
  close: []
}>()

// 响应式数据
const count = ref(0)

// 计算属性
const doubleCount = computed(() => count.value * 2)
</script>

<template>
  <div class="component-wrapper">
    <h1>{{ props.title }}</h1>
    <p>Count: {{ count }}</p>
    <p>Double: {{ doubleCount }}</p>
  </div>
</template>

<style scoped>
.component-wrapper {
  @apply p-4 bg-white rounded-lg shadow;
}
</style>
```

### API服务开发

```typescript
// src/services/authService.ts
import apiClient from '@/api/client'

export async function login(username: string, password: string) {
  const response = await apiClient.post('/auth/login', { username, password })
  return response.data
}

export async function getUserInfo() {
  const response = await apiClient.get('/auth/me')
  return response.data
}
```

### 状态管理开发

```typescript
// src/stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface UserInfo {
  id: number
  user_name: string
  email: string
}

export const useUserStore = defineStore('user', () => {
  // 状态
  const userInfo = ref<UserInfo | null>(null)
  const token = ref<string>('')

  // 计算属性
  const isLogin = computed(() => !!token.value)

  // 方法
  function setUserInfo(info: UserInfo) {
    userInfo.value = info
  }

  function logout() {
    userInfo.value = null
    token.value = ''
  }

  return {
    userInfo,
    token,
    isLogin,
    setUserInfo,
    logout
  }
})
```

## 🔧 部署指南

### 环境准备

1. **Node.js环境**: 确保服务器安装Node.js >= 18.0.0
2. **Web服务器**: Nginx/Apache用于静态资源服务
3. **API服务**: 后端API服务可正常访问

### 构建部署

```bash
# 1. 安装依赖
npm install

# 2. 构建生产版本
npm run build

# 3. 构建产物在 dist/ 目录
ls -la dist/
```

### Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态资源
    location / {
        root /path/to/your/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API代理（解决跨域）
    location /api/ {
        proxy_pass http://localhost:8090/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 开启Gzip压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

### Docker部署（可选）

```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  frontend:
    build: .
    ports:
      - "80:80"
    environment:
      - VITE_API_BASE_URL=http://api.example.com
    restart: unless-stopped
```

## 🤝 贡献指南

我们欢迎所有形式的贡献，包括问题报告、功能建议、代码提交和文档改进。

### 开发流程

1. **Fork项目仓库**
   ```bash
   # 点击GitHub上的Fork按钮，然后克隆您的fork
   git clone https://github.com/your-username/fast-full-stack-demo.git
   cd fast-full-stack-demo/frontend
   ```

2. **创建特性分支**
   ```bash
   git checkout -b feature/AmazingFeature
   # 或
   git checkout -b fix/some-bug
   # 或
   git checkout -b docs/some-doc-improvement
   ```

3. **进行开发**
   - 遵循项目的代码规范和开发指南
   - 确保所有测试通过
   - 更新相关文档

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加AmazingFeature功能"
   # 使用规范的commit message格式
   ```

5. **推送到您的fork**
   ```bash
   git push origin feature/AmazingFeature
   ```

6. **创建Pull Request**
   - 在GitHub上创建PR到主仓库
   - 详细描述您的更改
   - 等待代码审查

### Commit Message规范

我们遵循[Conventional Commits](https://www.conventionalcommits.org/)规范：

- `feat:` - 新功能
- `fix:` - Bug修复
- `docs:` - 文档更新
- `style:` - 代码格式调整
- `refactor:` - 代码重构
- `test:` - 测试相关
- `chore:` - 构建/工具相关

示例：
```
feat: 添加用户管理模块
fix: 修复登录页面响应式布局问题
docs: 更新API文档说明
```

### 代码规范检查

在提交PR前，请确保通过所有代码检查：

```bash
# 运行代码检查
npm run lint

# 运行类型检查
npm run type-check

# 运行测试
npm run test:unit

# 构建项目
npm run build
```

## 📝 许可证

本项目基于 [MIT](LICENSE) 许可证开源 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Vue.js](https://vuejs.org/) - 优秀的前端框架
- [Element Plus](https://element-plus.org/) - 出色的组件库
- [Vite](https://vitejs.dev/) - 极速的开发体验
- [Pinia](https://pinia.vuejs.org/) - 现代化的状态管理
- 所有为这个项目做出贡献的开发者们

---

<p align="center">
  ⭐ 如果这个项目对您有帮助，请给我一个星星！
</p>
