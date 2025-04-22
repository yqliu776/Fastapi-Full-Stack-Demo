# Fast Full Stack Demo - 前端

这是一个基于Vue 3和Vite的前端项目，使用TypeScript提供类型支持，采用Tailwind CSS进行样式设计。本项目作为全栈应用的前端部分，提供现代化的用户界面和交互体验。

## 技术栈

- **框架**: Vue 3
- **构建工具**: Vite
- **语言**: TypeScript
- **路由**: Vue Router
- **状态管理**: Pinia
- **样式**: Tailwind CSS
- **测试工具**: Vitest (单元测试), Cypress (E2E测试)
- **代码规范**: ESLint

## 项目结构

```
frontend/
├── public/           # 静态资源目录
├── src/              # 源代码目录
│   ├── assets/       # 资源文件(CSS, 图片等)
│   ├── components/   # 组件
│   ├── router/       # 路由配置
│   ├── stores/       # Pinia 状态管理
│   ├── views/        # 页面视图
│   ├── App.vue       # 根组件
│   └── main.ts       # 入口文件
├── index.html        # HTML模板
├── vite.config.ts    # Vite配置
└── tailwind.config.js # Tailwind配置
```

## 推荐的IDE设置

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (并禁用Vetur)。

## TypeScript对`.vue`导入的类型支持

TypeScript默认无法处理`.vue`导入的类型信息，因此我们用`vue-tsc`替代`tsc` CLI进行类型检查。在编辑器中，需要[Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar)来使TypeScript语言服务识别`.vue`类型。

## 自定义配置

详见[Vite配置参考](https://vitejs.dev/config/)。

## 项目安装

```sh
npm install
```

### 开发环境编译和热重载

```sh
npm run dev
```

### 类型检查、编译和生产环境压缩

```sh
npm run build
```

### 使用[Vitest](https://vitest.dev/)运行单元测试

```sh
npm run test:unit
```

### 使用[Cypress](https://www.cypress.io/)运行端到端测试

```sh
npm run test:e2e:dev
```

这会针对Vite开发服务器运行端到端测试，速度比生产构建快得多。

但在部署前（例如在CI环境中）仍建议使用`test:e2e`测试生产构建：

```sh
npm run build
npm run test:e2e
```

### 使用[ESLint](https://eslint.org/)进行代码检查

```sh
npm run lint
```

## 与后端连接

本前端应用设计为与后端API服务通信。确保后端服务运行并正确配置API端点。

## 贡献指南

1. Fork项目仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

[MIT](LICENSE)
