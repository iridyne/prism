# Prism TODO / 产品与架构蓝图（v1）

## 1. 目标与定位

### 1.1 产品目标
把 Prism 打造成“基金投资组合一站式分析系统”，覆盖以下闭环：

1. 用户通过 Wizard 完成组合配置与风险偏好设置。
2. 系统自动汇聚基金、市场、情绪等多源数据。
3. 通过 MAS + LangGraph + 推理链输出结构化分析结论。
4. 在 Dashboard 持续查看结果、建议和风险预警。

### 1.2 产品边界
这是“AI 分析与决策辅助系统”，不是自动交易系统。

1. 不下单、不接券商交易接口。
2. 不做高频、毫秒级行情交易。
3. 以“分钟级分析 + 小时级监控 + 日度复盘”为主。
4. 面向国内基金场景，明确考虑 T+1 机制。

### 1.3 核心原则

1. 批处理优先：创建组合 -> 异步分析（1-5 分钟）-> 查看结果。
2. 结果可追溯：分析结论、版本、时间戳必须落库。
3. 可长期运行：支持 7x24 数据采集与事件监控。
4. 降级可用：数据源失败、模型失败时仍要给出可解释的 fallback 结果。

---

## 2. 用户流程（MVP）

### 2.1 首次使用（Wizard）

1. 输入组合名称。
2. 录入持仓基金代码与配置比例。
3. 设置风险收益偏好（风险等级、投资期限、目标收益）。
4. 提交后创建组合，状态为 `pending_analysis`。

### 2.2 分析触发（异步任务）

1. 用户点击 `Run Analysis`。
2. 后端创建 `task_id` 并立刻返回。
3. 后台执行 `PrismKernel`：
   1. 加载基金数据（AkShare/OpenBB/yFinance 可配置）。
   2. 加载市场情绪与指数信息。
   3. 执行 MAS 辩论与推理聚合。
   4. 生成评分、建议、风险提示并持久化。
4. 通过 WebSocket 持续推送任务进度。

### 2.3 结果消费（Dashboard）

1. 查看组合基础信息与偏好参数。
2. 查看最新分析报告（评分、建议、指标、风险提示）。
3. 查看任务状态（queued/running/completed/failed）。
4. 支持报告导出（MVP 可先提供 JSON 导出，PDF 延后）。

---

## 3. 架构设计（目标态）

### 3.1 三层分离

```text
Frontend (Vite + React)
- Wizard: 创建组合
- Dashboard: 展示分析结果
- WebSocket: 接收任务进度

Backend (FastAPI)
- REST API: 组合管理 + 分析触发 + 结果查询
- Services: 业务编排（任务、落库、状态机）
- WebSocket: 进度广播

Core Engine (PrismKernel)
- Fetchers: 多源数据抓取
- MAS: 多智能体辩论（LangGraph）
- Analytics: 绩效/相关性/风险分析
- Synthesizer: 汇总最终建议

Storage (SQLite MVP / PostgreSQL 生产)
- portfolios
- analysis_results
- portfolio_snapshots
- (可选) analysis_tasks
```

### 3.2 关键模块职责

1. `frontend`
   - 仅负责交互与可视化，不承载业务规则。
2. `api/routes`
   - 只做协议转换与参数校验，不写核心业务逻辑。
3. `services`
   - 业务编排中心，负责任务状态、调用 Kernel、入库。
4. `core/prism_kernel`
   - 纯分析引擎，输入标准化数据，输出结构化结果。
5. `fetchers`
   - 屏蔽各数据源差异，统一输出格式。
6. `monitoring`（可延后）
   - 周期采集、黑天鹅信号检测、告警分发。

---

## 4. 数据模型（MVP）

### 4.1 表结构（最小集合）

```sql
CREATE TABLE portfolios (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    positions JSON NOT NULL,       -- [{"code":"000273","allocation":0.30}]
    preferences JSON NOT NULL,     -- {"risk_level":"medium","horizon_months":24}
    status TEXT NOT NULL DEFAULT 'pending_analysis', -- pending_analysis/active/archived
    created_at TEXT NOT NULL
);

CREATE TABLE analysis_results (
    portfolio_id TEXT PRIMARY KEY,
    overall_score INTEGER,
    summary TEXT,
    recommendations JSON,
    correlation_warnings JSON,
    backtest_metrics JSON,
    agent_insights JSON,
    created_at TEXT NOT NULL,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);

CREATE TABLE portfolio_snapshots (
    id TEXT PRIMARY KEY,
    portfolio_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    total_value REAL,
    daily_return REAL,
    metrics JSON,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
);
```

### 4.2 字段约束建议

1. `positions` 总仓位和必须接近 1.0（允许 `±0.001` 浮动）。
2. `preferences.risk_level` 仅允许 `low/medium/high`。
3. `analysis_results.portfolio_id` 唯一，保存最新结果。
4. 时间字段统一 ISO8601（UTC），避免时区歧义。

---

## 5. API 合同（MVP）

### 5.1 REST

1. `POST /api/portfolios`
   - 创建组合，返回 `portfolio_id`。
2. `GET /api/portfolios`
   - 返回组合列表。
3. `GET /api/portfolios/{id}`
   - 返回组合详情。
4. `POST /api/portfolios/{id}/analyze`
   - 触发异步分析，返回 `task_id`。
5. `GET /api/tasks/{task_id}`
   - 查询任务状态与进度。
6. `GET /api/portfolios/{id}/analysis`
   - 查询最新分析结果。

### 5.2 WebSocket

1. `WS /ws/tasks/{task_id}`
2. 事件结构（建议）：
   - `task_id`
   - `status`
   - `progress`（0-100）
   - `message`
   - `timestamp`
   - `error`（可选）

### 5.3 任务状态机

1. `queued`
2. `running`
3. `completed`
4. `failed`

---

## 6. 数据源策略

### 6.1 数据源优先级（可配置）

1. 基金净值与基础信息：AkShare（主）-> OpenBB（备）-> yFinance（补充）
2. 指数与大盘信息：AkShare（主）-> yFinance（备）
3. 情绪与新闻：OpenBB + 新闻抓取（延后可做）

### 6.2 统一规范

1. 所有 Fetcher 输出统一 schema（`timestamp` + `data` + `source` + `quality`）。
2. 每个数据点记录 `source_name` 与 `fetched_at`，支持追溯。
3. 数据源失败时给出 degraded 标记，不直接中断整次分析。

---

## 7. MAS 与分析引擎设计

### 7.1 Agent 切分（MVP）

1. Fundamental Agent：基金基本面与历史净值表现。
2. Technical Agent：指数趋势、动量、波动。
3. Risk Agent：集中度、回撤风险、相关性风险。

### 7.2 输出格式（统一 JSON）

每个 Agent 必须返回：

1. `agent_name`
2. `score`（0-100）
3. `confidence`（0-1）
4. `analysis`（文字结论）
5. `evidence`（关键证据点）

### 7.3 聚合逻辑

1. LangGraph 编排执行顺序与依赖关系。
2. 汇总器生成：
   - `overall_score`
   - `summary`
   - `recommendations`
   - `correlation_warnings`
   - `backtest_metrics`

---

## 8. T+1 与黑天鹅应对策略

### 8.1 国内基金 T+1 约束

1. 预警目标是“早识别、早准备”，不是实时成交。
2. 输出建议应分层：
   - `立即关注`
   - `下一个交易日执行`
   - `观察等待`

### 8.2 黑天鹅监控（Phase 2）

1. 价格异常：指数跌幅/波动阈值触发。
2. 情绪异常：负面新闻激增、舆情极端化。
3. 相关性异常：组合内资产相关性突增。
4. 告警渠道：站内通知（MVP）-> 邮件/企业微信（后续）。

---

## 9. MVP 范围与非范围

### 9.1 MVP 必须完成

1. 组合创建（Wizard -> `portfolios` 落库）。
2. 异步分析链路（触发 -> 任务 -> 结果落库 -> Dashboard 展示）。
3. WebSocket 进度推送。
4. 最新结果查询与可视化。

### 9.2 明确延期项

1. 后台长期监控服务。
2. 多组合对比分析。
3. OCR 导入持仓。
4. 自动再平衡与回测优化。

---

## 10. 里程碑与验收标准

### M1：可跑通主链路（1 周）

1. 完成组合创建、分析触发、进度推送、结果展示。
2. 验收：
   - 创建组合成功率 > 99%
   - 分析任务完成率 > 95%
   - Dashboard 能稳定展示最新结果

### M2：稳定性增强（1 周）

1. 引入失败重试、超时与降级策略。
2. 增加基础监控（日志、错误率、任务耗时）。
3. 验收：
   - 平均任务耗时 < 5 分钟
   - 错误可定位率 > 90%

### M3：监控能力上线（后续）

1. 定时快照与黑天鹅检测。
2. 告警机制与操作建议分级。

---

## 11. 非功能要求

### 11.1 性能

1. `POST /analyze` 响应 < 500ms（仅创建任务）。
2. 单任务分析耗时目标 1-5 分钟。

### 11.2 可靠性

1. 任务状态可查询，失败有错误原因。
2. 数据源异常不导致系统整体不可用。

### 11.3 可维护性

1. 前后端接口契约稳定且版本化。
2. 服务层与核心引擎分离，便于替换数据源/模型。

### 11.4 安全与合规

1. API Key 仅通过环境变量注入，不入库不入日志。
2. 对外声明“仅供研究与决策辅助，不构成投资建议”。

---

## 12. 当前执行优先级（下一步）

1. 先固定 API 合同与任务状态机。
2. 再实现 Wizard -> Analyze -> Dashboard 的 MVP 闭环。
3. 最后补齐监控、告警与高级分析能力。

> 一句话总结：先把“可用闭环”做扎实，再把“智能深度”做上去。
