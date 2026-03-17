# 工作交接

> 最后更新: 2026-03-17 14:19
> 更新者: jdzhan
> 分支: master

## 当前状态
- DESIGN.md 已更新至 v1.1（设计已确认），技术方案完整
- TODO.md 已生成，共 16 个开发任务，进度 0/16
- order/ 目录尚未创建，等待 develop Agent 开始编码

## 本次改动
- `.claude/memory/handoff.md`
- `DESIGN.md`
- `TODO.md`

## 最近提交
```
fd55c44 chore(memory): 升级 handoff 持久化为三层架构
9f9a29e chore: 忽略 openteam.zip 临时压缩包
a48d373 chore: 完善 AI 协作框架配置与 handoff 持久化机制
b87fe76 添加/ot-page-style，用于只修改页面样式
e917079 refactor: 优化 OpenTeam spec token 消耗，整体下降 40.4%
```

## 关键决策
- handoff.md Stop hook 只更新元数据（时间/用户/分支），不覆盖正文
- CLAUDE.md 要求 Claude 在最后一条回复中主动写入 handoff，不依赖 Stop hook
- 技术选型：后端（Spring Boot 3.x + Java 21）+ H2 内存数据库，原因是验证项目无需真实环境，后端 CRUD 流程标准，能产生足够多的提交节点
- 单 Maven 模块（不拆分 api/common/dao/service 子模块），简化验证项目结构
- 包名定为 `com.openteam.order`，Spring Boot 启动类放在根包
- 使用 mybatis-plus-spring-boot3-starter（Boot3 专用版本，非 Boot2 版本）
- 统一响应体 ApiResponse 不包含 traceId（验证项目简化）
- 逻辑删除通过 MyBatis-Plus @TableLogic 实现，配置全局逻辑删除字段

## 注意事项
- sed -i '' 是 macOS BSD sed 语法，Linux 上需改为 sed -i（无引号）
- openteam.zip 已加入 .gitignore，不纳入版本控制
- order/ 目录尚未创建，由 develop Agent 负责创建项目骨架
- 无鉴权要求（验证项目简化），不需要集成 JWT/SSO
- 数据库使用 H2，不依赖外部 MySQL 服务
- H2 连接 URL 需加 MODE=MySQL 保证 MyBatis-Plus 方言兼容
- Spring Boot 3.x 使用 `spring.sql.init.mode: always` 而非旧版 `spring.datasource.initialization-mode`
- MyBatis-Plus 自动填充需要实现 MetaObjectHandler 并注册为 @Component，否则 createdAt/updatedAt 不会自动填充
- 创建订单返回 HTTP 201（使用 ResponseEntity<ApiResponse<OrderVO>>），删除订单可返回 HTTP 204 空响应
- listOrders 接口的 status 参数为可选查询参数（@RequestParam(required = false)）

## 下一步
- develop Agent 接手：按 TODO.md 顺序从 T01 开始执行，先创建 order/ 项目骨架和 pom.xml
- 建议每完成一个阶段（T01~T06、T07~T08、T09~T11、T12、T13~T14、T15~T16）提交一次 commit
- 所有任务完成后运行 `mvn clean package` 和 `mvn test` 验证
