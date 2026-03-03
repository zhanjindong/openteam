---
description: 后端 Java/Spring Boot 代码风格底线
globs: "**/*.java"
---

# 后端代码风格底线

## 命名规范

1. 类名 PascalCase，后缀遵循约定: Controller / IService / ServiceImpl / Mapper / Entity / DTO / VO / Client / Utils / Config / Enum / Constants
2. 方法名 camelCase，查询 `get/query/find/list`、创建 `create/add/save`、更新 `update/modify`、删除 `delete/remove`、布尔 `is/has/can`
3. 常量 UPPER_SNAKE_CASE

## 分层约束

4. Controller 禁止包含业务逻辑，只负责参数接收、校验、调用 Service、返回结果
5. Service 层必须定义接口（I*Service），实现类为 *ServiceImpl
6. 禁止跨层调用: Controller 不能直接调用 Mapper，Service 不能直接操作 HttpServletRequest

## 代码质量

7. 使用 Lombok 简化样板代码，禁止手写 getter/setter/toString
8. 公共类和方法必须添加 JavaDoc 注释
9. Controller 方法必须添加 OpenAPI 注解（`@Operation`、`@Parameter`）
10. 使用 `@Valid` 进行请求参数校验，禁止在 Controller 中手动校验参数
