---
description: 前端 Vue/TypeScript 代码风格底线
globs: "**/*.{vue,ts,tsx}"
---

# 前端代码风格底线

## 框架约束

1. 只使用 Composition API + `<script setup>`，禁止 Options API
2. 只使用 pnpm 管理依赖，禁止 npm / yarn
3. 样式方案以 Tailwind CSS 原子化类为主，动态样式使用 `v-bind:class`

## 命名规范

4. Vue 组件文件 PascalCase（`ChatPanel.vue`），弹窗组件以 Dialog 结尾（`CreateAgentDialog.vue`）
5. 组合式函数 camelCase + use 前缀（`useRequest.ts`）
6. TypeScript 类型/接口 PascalCase + I 前缀（`IUser`、`IApiResponse`）
7. CSS 类名 kebab-case（`app-layout`、`menu-root`）
8. 常量 UPPER_SNAKE_CASE

## 组件规范

9. 单个 Vue 文件不超过 500 行，style 独立成同名 scss 文件
10. `src/components/` 中 vue 文件的 style 标签不加 scoped：`<style lang="scss">`
11. `src/views/` 只负责组件布局和数据调度，不含业务逻辑、原生 HTML 元素、CSS 样式代码
12. template 不使用表达式，只根据单一字段数据渲染
13. 一个功能点一个函数，一个字段一个组件（文件上传、下载、预览等独立成组件）
14. `if-else if-else` 不能省略最后的 `else` 部分
