# TODO.md — 订单管理系统开发计划

> 关联需求版本: DESIGN.md v1.1
> 创建时间: 2026-03-17
> 进度: 0/16

---

## 阶段一：项目骨架

### T01 - 初始化 Maven 项目结构
- **输入**: 无
- **输出**: `order/pom.xml`、`order/src/` 目录骨架、`order/src/main/java/com/openteam/order/OrderApplication.java`
- **完成标准**: `mvn clean compile` 在 order/ 目录下执行成功（无源文件报错）
- **涉及文件**:
  - `order/pom.xml`（新建，配置 Spring Boot 3.x 父 POM 及所有依赖）
  - `order/src/main/java/com/openteam/order/OrderApplication.java`（新建，启动类）
  - `order/src/main/resources/application.yml`（新建，H2 数据源 + MyBatis-Plus 配置）
- **依赖**: 无

- [ ] T01

---

## 阶段二：数据层

### T02 - 数据库初始化脚本
- **输入**: 5.1 节数据模型
- **输出**: `schema.sql`，H2 建表语句
- **完成标准**: 启动应用后 H2 控制台（或日志）可见 orders 表已创建
- **涉及文件**:
  - `order/src/main/resources/schema.sql`（新建）
- **依赖**: T01

- [ ] T02

### T03 - 订单状态枚举
- **输入**: 4.1 节状态机，5.2 节枚举值
- **输出**: `OrderStatus.java`
- **完成标准**: 枚举包含 PENDING/CONFIRMED/COMPLETED/CANCELLED 四个值及中文描述
- **涉及文件**:
  - `order/src/main/java/com/openteam/order/constants/OrderStatus.java`（新建）
- **依赖**: T01

- [ ] T03

### T04 - Order 实体类
- **输入**: 5.1 节数据模型，T03
- **输出**: `Order.java`，MyBatis-Plus 实体，含逻辑删除和自动填充注解
- **完成标准**: 字段与 schema.sql 一一对应，@TableLogic 和 @TableField(fill=...) 注解正确
- **涉及文件**:
  - `order/src/main/java/com/openteam/order/entity/Order.java`（新建）
- **依赖**: T02, T03

- [ ] T04

### T05 - MyBatis-Plus 自动填充配置
- **输入**: T04 中 createdAt/updatedAt 自动填充需求
- **输出**: `MetaObjectHandlerConfig.java`，实现 MetaObjectHandler
- **完成标准**: INSERT 时自动填充 createdAt 和 updatedAt，UPDATE 时自动更新 updatedAt
- **涉及文件**:
  - `order/src/main/java/com/openteam/order/config/MetaObjectHandlerConfig.java`（新建）
- **依赖**: T04

- [ ] T05

### T06 - OrderMapper
- **输入**: T04 Order 实体
- **输出**: `OrderMapper.java`，继承 BaseMapper<Order>
- **完成标准**: 接口定义正确，无需 XML，MyBatis-Plus 自动提供 CRUD 方法
- **涉及文件**:
  - `order/src/main/java/com/openteam/order/mapper/OrderMapper.java`（新建）
- **依赖**: T04

- [ ] T06

---

## 阶段三：公共基础设施

### T07 - 统一响应体 ApiResponse
- **输入**: 10.4 节统一响应体设计
- **输出**: `ApiResponse.java`，含 success/fail 静态工厂方法
- **完成标准**: 包含 code、message、data、timestamp 字段，泛型设计正确
- **涉及文件**:
  - `order/src/main/java/com/openteam/order/common/ApiResponse.java`（新建）
- **依赖**: T01

- [ ] T07

### T08 - 业务异常 BizException 和全局异常处理器
- **输入**: 10.5 节异常处理方案，T07
- **输出**: `BizException.java`、`GlobalExceptionHandler.java`
- **完成标准**:
  - BizException 含 httpStatus 和 message 字段
  - GlobalExceptionHandler 捕获 BizException、MethodArgumentNotValidException、Exception 三类
  - 不同异常返回对应 HTTP 状态码
- **涉及文件**:
  - `order/src/main/java/com/openteam/order/common/BizException.java`（新建）
  - `order/src/main/java/com/openteam/order/common/GlobalExceptionHandler.java`（新建）
- **依赖**: T07

- [ ] T08

---

## 阶段四：业务层

### T09 - DTO 和 VO 类
- **输入**: 10.3 节 DTO/VO 设计，4.2 节数据约束
- **输出**: `CreateOrderRequest.java`、`OrderVO.java`
- **完成标准**:
  - CreateOrderRequest 含 @NotBlank、@Min、@Max、@DecimalMin 等校验注解
  - OrderVO 含静态工厂方法 `from(Order order)`
- **涉及文件**:
  - `order/src/main/java/com/openteam/order/dto/CreateOrderRequest.java`（新建）
  - `order/src/main/java/com/openteam/order/dto/OrderVO.java`（新建）
- **依赖**: T03, T04

- [ ] T09

### T10 - IOrderService 接口
- **输入**: 10.3 节方法签名，T09
- **输出**: `IOrderService.java`
- **完成标准**: 定义 6 个业务方法，方法签名与设计文档一致，含 JavaDoc 注释
- **涉及文件**:
  - `order/src/main/java/com/openteam/order/service/IOrderService.java`（新建）
- **依赖**: T09

- [ ] T10

### T11 - OrderServiceImpl 业务实现
- **输入**: T10 接口，T06 Mapper，T08 异常，4.1 节状态机，10.7 节订单号生成
- **输出**: `OrderServiceImpl.java`，实现所有业务逻辑
- **完成标准**:
  - createOrder：生成 ORD-{timestamp}-{6位随机} 格式订单号，计算 totalAmount = unitPrice × quantity
  - getOrderByNo：不存在时抛 BizException(404)
  - listOrders：status 为 null 时返回全量，非 null 时用 QueryWrapper 过滤
  - confirmOrder：非 PENDING 状态抛 BizException(400, "当前订单状态不允许确认")
  - cancelOrder：非 PENDING/CONFIRMED 状态抛 BizException(400, "当前订单状态不允许取消")
  - deleteOrder：非 CANCELLED 状态抛 BizException(400, "只有已取消的订单可以删除")，删除使用 removeById（触发逻辑删除）
  - 创建和状态变更操作记录 INFO 日志（@Slf4j）
- **涉及文件**:
  - `order/src/main/java/com/openteam/order/service/impl/OrderServiceImpl.java`（新建）
- **依赖**: T10, T06, T08, T05

- [ ] T11

---

## 阶段五：接口层

### T12 - OrderController
- **输入**: 6 节 API 接口概览，T10 Service 接口，T07 ApiResponse，T08 异常处理
- **输出**: `OrderController.java`，实现 6 个 REST 接口
- **完成标准**:
  - 所有接口路径与设计一致
  - 使用 @Valid 触发参数校验
  - 接口方法含 @Operation 注解（OpenAPI）
  - 创建订单返回 HTTP 201，删除订单返回 HTTP 204（或 200 + 空 data）
  - Controller 不含任何业务逻辑，只做参数映射和响应包装
- **涉及文件**:
  - `order/src/main/java/com/openteam/order/controller/OrderController.java`（新建）
- **依赖**: T11, T12 依赖 T11

- [ ] T12

---

## 阶段六：单元测试

### T13 - OrderServiceImpl 单元测试（创建和查询）
- **输入**: T11 OrderServiceImpl，AC-01 ~ AC-05 验收标准
- **输出**: `OrderServiceTest.java` 中创建、查询相关测试方法
- **完成标准**:
  - `should_returnOrderVO_when_createOrderWithValidRequest`：验证订单号格式、金额计算、初始状态
  - `should_throwBizException_when_getOrderByNoNotFound`：验证 404 异常
  - `should_returnFilteredOrders_when_listOrdersByStatus`：验证状态过滤
  - 使用 @MockBean 或 Mockito.mock() 隔离 Mapper，测试不依赖数据库
- **涉及文件**:
  - `order/src/test/java/com/openteam/order/service/OrderServiceTest.java`（新建）
- **依赖**: T11

- [ ] T13

### T14 - OrderServiceImpl 单元测试（状态流转）
- **输入**: T11 OrderServiceImpl，AC-06 ~ AC-10 验收标准
- **输出**: `OrderServiceTest.java` 中状态变更相关测试方法
- **完成标准**:
  - `should_confirmOrder_when_statusIsPending`：验证 PENDING → CONFIRMED
  - `should_throwBizException_when_confirmNonPendingOrder`：验证非法状态确认
  - `should_cancelOrder_when_statusIsPendingOrConfirmed`：验证取消逻辑
  - `should_deleteOrder_when_statusIsCancelled`：验证逻辑删除
  - `should_throwBizException_when_deleteNonCancelledOrder`：验证非法删除
- **涉及文件**:
  - `order/src/test/java/com/openteam/order/service/OrderServiceTest.java`（修改，追加方法）
- **依赖**: T13

- [ ] T14

---

## 阶段七：验证与收尾

### T15 - 全量编译与测试验证
- **输入**: T01 ~ T14 所有文件
- **输出**: 编译通过，所有测试通过
- **完成标准**:
  - `mvn clean package -f order/pom.xml` 无报错
  - `mvn test -f order/pom.xml` 全部测试通过（AC-11, AC-12）
- **涉及文件**: 无新增文件，修复编译/测试中发现的问题
- **依赖**: T14

- [ ] T15

### T16 - 接口冒烟测试（curl 验证）
- **输入**: T12 OrderController，AC-01 ~ AC-10 验收标准
- **输出**: 验证脚本或手动测试记录
- **完成标准**:
  - 启动应用 `java -jar order/target/*.jar`
  - 验证所有 AC 验收标准均通过（按 AC-01 到 AC-10 逐一验证）
- **涉及文件**: 无代码变更，补充 `order/README.md`（接口测试命令示例）
- **依赖**: T15

- [ ] T16

---

## 任务依赖关系图

```
T01（项目骨架）
 ├── T02（schema.sql）
 ├── T03（OrderStatus 枚举）
 │    └── T04（Order 实体）
 │         ├── T05（自动填充配置）
 │         │    └── T11（ServiceImpl）←─────┐
 │         ├── T06（OrderMapper）→ T11       │
 │         └── T09（DTO/VO）                 │
 │              └── T10（IOrderService）→ T11│
 └── T07（ApiResponse）                      │
      └── T08（BizException + Handler）→ T11─┘
           └── T12（Controller）
                └── T13（测试-创建查询）
                     └── T14（测试-状态流转）
                          └── T15（全量验证）
                               └── T16（冒烟测试）
```

