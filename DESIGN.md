# DESIGN.md — 订单管理系统

> 版本: v1.0
> 状态: 需求已确认
> 最后更新: 2026-03-17
> 负责人: jdzhan

---

## 1. 需求背景

### 1.1 项目目的

本项目是一个验证项目，目的是验证 OpenTeam AI 协作框架的 handoff 持久化机制是否工作正常。通过完整走完「需求 → 设计 → 开发 → 测试 → 审查」流程，观察每个阶段的 Agent 交接是否能正确传递上下文。

### 1.2 业务背景

实现一个最小可用的订单管理系统，覆盖订单的创建、查询、状态变更、删除等核心 CRUD 操作和基本业务流程。系统足够简单但需结构完整，能体现标准后端开发的全流程。

### 1.3 技术选型决策

选择后端方案（Spring Boot 3.x + Java 21），原因：
- CRUD 流程标准明确，适合验证多阶段 Agent 协作
- 无需处理前端 UI 联调，减少无关变量
- 覆盖 Controller / Service / Mapper 三层架构，能产生足够多的提交节点

### 1.4 项目目录

```
order/           # 放置于项目根目录 /Users/jackiezhan/github/openteam/order/
```

---

## 2. 功能描述

系统提供订单的增删改查 REST API，支持订单状态流转。所有接口返回统一响应体。

---

## 3. 用户故事

| 编号 | 用户故事 | 优先级 |
|------|---------|--------|
| US-01 | 作为系统用户，我可以创建一笔订单，输入商品名称、数量、单价，系统返回订单编号 | P0 |
| US-02 | 作为系统用户，我可以根据订单编号查询订单详情，包括订单状态和金额 | P0 |
| US-03 | 作为系统用户，我可以查询所有订单列表，支持按状态过滤 | P0 |
| US-04 | 作为系统用户，我可以将待处理订单确认为已确认状态 | P0 |
| US-05 | 作为系统用户，我可以取消一笔未完成的订单 | P0 |
| US-06 | 作为系统用户，我可以删除已取消的订单 | P1 |

---

## 4. 业务规则

### 4.1 订单状态机

```
PENDING（待处理）
    ↓ 确认操作
CONFIRMED（已确认）
    ↓ 完成操作（预留，本期不实现）
COMPLETED（已完成）

PENDING / CONFIRMED → 取消操作 → CANCELLED（已取消）
```

- 只有 `PENDING` 状态的订单可以被确认
- 只有 `PENDING` 或 `CONFIRMED` 状态的订单可以被取消
- 只有 `CANCELLED` 状态的订单可以被删除
- 订单金额 = 单价 × 数量，在创建时自动计算，不允许外部传入

### 4.2 数据约束

- 商品名称：必填，1–100 个字符
- 数量：必填，正整数，最小值 1，最大值 9999
- 单价：必填，正数（精度 2 位小数），最小值 0.01
- 订单编号：系统自动生成，格式为 `ORD-{yyyyMMddHHmmss}-{6位随机数}`，全局唯一

---

## 5. 数据模型

### 5.1 orders 表

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| order_no | VARCHAR(32) | UNIQUE, NOT NULL | 订单编号 |
| product_name | VARCHAR(100) | NOT NULL | 商品名称 |
| quantity | INT | NOT NULL | 数量 |
| unit_price | DECIMAL(10,2) | NOT NULL | 单价 |
| total_amount | DECIMAL(10,2) | NOT NULL | 总金额（自动计算） |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'PENDING' | 订单状态 |
| created_at | DATETIME | NOT NULL | 创建时间（自动填充） |
| updated_at | DATETIME | NOT NULL | 更新时间（自动填充） |
| logic_delete | TINYINT | NOT NULL, DEFAULT 0 | 逻辑删除标记 |

### 5.2 状态枚举值

| 值 | 含义 |
|----|------|
| PENDING | 待处理 |
| CONFIRMED | 已确认 |
| CANCELLED | 已取消 |

---

## 6. API 接口概览

| 方法 | 路径 | 说明 | 对应用户故事 |
|------|------|------|------------|
| POST | /api/v1/orders | 创建订单 | US-01 |
| GET | /api/v1/orders/{orderNo} | 查询订单详情 | US-02 |
| GET | /api/v1/orders | 查询订单列表（?status=） | US-03 |
| PUT | /api/v1/orders/{orderNo}/confirm | 确认订单 | US-04 |
| PUT | /api/v1/orders/{orderNo}/cancel | 取消订单 | US-05 |
| DELETE | /api/v1/orders/{orderNo} | 删除已取消订单 | US-06 |

---

## 7. 非功能需求

| 类别 | 要求 |
|------|------|
| 代码规范 | 遵循 `/rules/context-backend.md` 所有约定 |
| 测试覆盖 | Service 层核心逻辑必须有单元测试，遵循 `/rules/testing.md` |
| 错误处理 | 业务异常使用 BizException，统一由 GlobalExceptionHandler 处理 |
| 日志 | 关键操作（创建、状态变更）记录 INFO 日志，异常记录 WARN/ERROR |
| 安全 | 无鉴权要求（验证项目，简化处理） |
| 数据库 | H2 内存数据库（验证项目，无需真实 MySQL 环境） |

---

## 8. 验收标准

| 编号 | 验收标准 | 判断方式 |
|------|---------|---------|
| AC-01 | POST /api/v1/orders 传入合法参数，返回 HTTP 200，响应体含 orderNo 字段 | 接口测试 |
| AC-02 | POST /api/v1/orders 传入非法参数（如数量为 0），返回 HTTP 400，含错误信息 | 接口测试 |
| AC-03 | GET /api/v1/orders/{orderNo} 查询已存在订单，返回完整订单数据 | 接口测试 |
| AC-04 | GET /api/v1/orders/{orderNo} 查询不存在订单，返回 HTTP 404 | 接口测试 |
| AC-05 | GET /api/v1/orders?status=PENDING，仅返回 PENDING 状态订单 | 接口测试 |
| AC-06 | PUT confirm 对 PENDING 订单操作，订单状态变为 CONFIRMED | 接口测试 |
| AC-07 | PUT confirm 对 CONFIRMED 订单操作，返回 HTTP 400，含「状态不允许」错误信息 | 接口测试 |
| AC-08 | PUT cancel 对 PENDING 或 CONFIRMED 订单操作，状态变为 CANCELLED | 接口测试 |
| AC-09 | DELETE 对 CANCELLED 订单操作，订单被逻辑删除，后续查询返回 404 | 接口测试 |
| AC-10 | DELETE 对非 CANCELLED 订单操作，返回 HTTP 400 | 接口测试 |
| AC-11 | Service 层单元测试全部通过（`mvn test`） | CI 验证 |
| AC-12 | `mvn clean package` 编译无报错 | CI 验证 |

---

## 9. 排除范围

以下内容明确不在本期实现范围内：

- 订单支付、退款流程
- 订单状态 COMPLETED 及其流转逻辑
- 用户认证与权限管理
- 分页查询（列表接口返回全量数据）
- 商品库存管理
- 多模块拆分（单 Maven 模块即可）
- 前端 UI 页面
- Docker / K8s 部署配置
- 性能压测与调优


---

## 10. 技术方案

> 版本: v1.1
> 状态: 设计已确认
> 最后更新: 2026-03-17

### 10.1 项目结构

单 Maven 模块，标准 Spring Boot 项目结构：

```
order/
├── pom.xml
└── src/
    ├── main/
    │   ├── java/com/openteam/order/
    │   │   ├── OrderApplication.java          # 启动类
    │   │   ├── common/
    │   │   │   ├── ApiResponse.java            # 统一响应体
    │   │   │   ├── BizException.java           # 业务异常
    │   │   │   └── GlobalExceptionHandler.java # 全局异常处理器
    │   │   ├── constants/
    │   │   │   └── OrderStatus.java            # 订单状态枚举
    │   │   ├── controller/
    │   │   │   └── OrderController.java        # REST 接口层
    │   │   ├── service/
    │   │   │   ├── IOrderService.java          # Service 接口
    │   │   │   └── impl/
    │   │   │       └── OrderServiceImpl.java   # Service 实现
    │   │   ├── mapper/
    │   │   │   └── OrderMapper.java            # MyBatis-Plus Mapper
    │   │   ├── entity/
    │   │   │   └── Order.java                  # 数据库实体
    │   │   └── dto/
    │   │       ├── CreateOrderRequest.java     # 创建订单请求 DTO
    │   │       └── OrderVO.java                # 订单响应 VO
    │   └── resources/
    │       ├── application.yml                 # 主配置
    │       └── schema.sql                      # H2 建表语句（自动执行）
    └── test/
        └── java/com/openteam/order/
            └── service/
                └── OrderServiceTest.java       # Service 单元测试
```

### 10.2 分层架构设计

```
HTTP 请求
    ↓
OrderController          # 参数接收、@Valid 校验、调用 Service、返回 ApiResponse
    ↓
IOrderService / OrderServiceImpl    # 业务逻辑：状态校验、金额计算、订单号生成
    ↓
OrderMapper              # MyBatis-Plus CRUD（继承 BaseMapper<Order>）
    ↓
H2 内存数据库（orders 表）
```

- Controller 不含任何业务判断，只做参数映射和响应包装
- Service 负责所有业务规则（状态机流转、约束校验、计算逻辑）
- Mapper 只做数据访问，复杂查询用 QueryWrapper，不写自定义 XML

### 10.3 核心类设计

#### Order.java（实体）

- 继承 MyBatis-Plus `Model<Order>` 或直接用注解
- 字段：id、orderNo、productName、quantity、unitPrice、totalAmount、status、createdAt、updatedAt、logicDelete
- `@TableLogic` 标注 logicDelete 字段，开启逻辑删除
- `@TableField(fill = FieldFill.INSERT)` 标注 createdAt，`@TableField(fill = FieldFill.INSERT_UPDATE)` 标注 updatedAt

#### OrderStatus.java（枚举）

```
PENDING("待处理")
CONFIRMED("已确认")
COMPLETED("已完成")   // 预留，本期不流转
CANCELLED("已取消")
```

#### CreateOrderRequest.java（请求 DTO）

- productName：@NotBlank，@Size(min=1, max=100)
- quantity：@NotNull，@Min(1)，@Max(9999)
- unitPrice：@NotNull，@DecimalMin("0.01")，@Digits(integer=8, fraction=2)

#### OrderVO.java（响应 VO）

- 包含 orders 表所有业务字段（排除 logicDelete）
- 从 Order 实体转换（用静态工厂方法 `OrderVO.from(Order order)`）

#### IOrderService / OrderServiceImpl

| 方法签名 | 说明 |
|----------|------|
| `OrderVO createOrder(CreateOrderRequest req)` | 创建订单，生成订单号，计算金额 |
| `OrderVO getOrderByNo(String orderNo)` | 查询订单，不存在抛 BizException(404) |
| `List<OrderVO> listOrders(String status)` | 按状态过滤（null 表示全量） |
| `OrderVO confirmOrder(String orderNo)` | 仅 PENDING 可确认，否则抛业务异常 |
| `OrderVO cancelOrder(String orderNo)` | PENDING/CONFIRMED 可取消 |
| `void deleteOrder(String orderNo)` | 仅 CANCELLED 可删除（逻辑删除） |

#### OrderController.java

- `POST /api/v1/orders` → `createOrder`，返回 201
- `GET /api/v1/orders/{orderNo}` → `getOrderByNo`
- `GET /api/v1/orders` → `listOrders`，接收可选 `?status=` 参数
- `PUT /api/v1/orders/{orderNo}/confirm` → `confirmOrder`
- `PUT /api/v1/orders/{orderNo}/cancel` → `cancelOrder`
- `DELETE /api/v1/orders/{orderNo}` → `deleteOrder`，返回 204 等效

#### BizException.java

```java
public class BizException extends RuntimeException {
    private final int httpStatus;   // HTTP 状态码（400/404 等）
    private final String message;
}
```

#### GlobalExceptionHandler.java

- 捕获 `BizException` → 按 httpStatus 返回对应 HTTP 状态码 + ApiResponse(code, message)
- 捕获 `MethodArgumentNotValidException` → HTTP 400 + 字段校验错误信息
- 捕获 `Exception` → HTTP 500 + 通用错误信息，error 日志

#### ApiResponse.java（统一响应体）

```java
public class ApiResponse<T> {
    private int code;       // 业务码，成功为 200
    private String message;
    private T data;
    private long timestamp;

    public static <T> ApiResponse<T> success(T data) { ... }
    public static ApiResponse<Void> success() { ... }
    public static ApiResponse<Void> fail(int code, String message) { ... }
}
```

### 10.4 统一响应体

所有接口统一返回 `ApiResponse<T>`，HTTP 状态码与业务场景对应：

| 场景 | HTTP 状态码 | code 字段 | message |
|------|------------|-----------|---------|
| 成功 | 200 | 200 | "success" |
| 参数校验失败 | 400 | 400 | 具体字段错误 |
| 业务规则违反 | 400 | 400 | 具体业务错误信息 |
| 资源不存在 | 404 | 404 | "订单不存在" |
| 服务器错误 | 500 | 500 | "服务器内部错误" |

### 10.5 异常处理方案

业务异常通过 `BizException` 抛出，由 `GlobalExceptionHandler` 统一处理：

```
OrderServiceImpl 抛出 BizException(400, "当前订单状态不允许确认")
    ↓
GlobalExceptionHandler.handleBizException()
    ↓
ResponseEntity(HttpStatus.BAD_REQUEST, ApiResponse.fail(400, "当前订单状态不允许确认"))
```

订单号不存在时抛 `BizException(404, "订单不存在")`，对应 HTTP 404。

### 10.6 数据库初始化

使用 H2 内存数据库，Spring Boot 自动执行 `src/main/resources/schema.sql`：

```sql
CREATE TABLE IF NOT EXISTS orders (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_no     VARCHAR(32)    NOT NULL,
    product_name VARCHAR(100)   NOT NULL,
    quantity     INT            NOT NULL,
    unit_price   DECIMAL(10,2)  NOT NULL,
    total_amount DECIMAL(10,2)  NOT NULL,
    status       VARCHAR(20)    NOT NULL DEFAULT 'PENDING',
    created_at   DATETIME       NOT NULL,
    updated_at   DATETIME       NOT NULL,
    logic_delete TINYINT        NOT NULL DEFAULT 0,
    CONSTRAINT uk_order_no UNIQUE (order_no)
);
```

`application.yml` 配置要点：
- `spring.datasource.url: jdbc:h2:mem:orderdb;MODE=MySQL`（MySQL 兼容模式）
- `spring.datasource.driver-class-name: org.h2.Driver`
- `spring.sql.init.mode: always`（每次启动执行 schema.sql）
- `mybatis-plus.global-config.db-config.logic-delete-field: logicDelete`（全局逻辑删除）
- `mybatis-plus.global-config.db-config.logic-delete-value: 1`
- `mybatis-plus.global-config.db-config.logic-not-delete-value: 0`

### 10.7 订单号生成策略

在 `OrderServiceImpl.createOrder()` 中生成：

```
格式：ORD-{yyyyMMddHHmmss}-{6位随机数}
示例：ORD-20260317143052-482917
实现：LocalDateTime.now() 格式化 + ThreadLocalRandom.current().nextInt(100000, 999999)
```

### 10.8 依赖清单（pom.xml）

| 依赖 | 说明 |
|------|------|
| spring-boot-starter-web | Web + Tomcat |
| spring-boot-starter-validation | @Valid 参数校验 |
| mybatis-plus-spring-boot3-starter | MyBatis-Plus（Boot3 专用） |
| com.h2database:h2 | H2 内存数据库（scope: runtime） |
| lombok | 简化样板代码 |
| spring-boot-starter-test | 单元测试（JUnit 5 + Mockito） |

