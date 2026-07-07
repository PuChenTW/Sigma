# AI Investment Research Studio — Design Context for Codex

> 目的：整理目前對「AI 投資研究工作室」的討論與架構決策，作為與 Codex Agent 進一步討論 codebase 設計、prototype、整合策略的上下文。
>
> 本文件不是最終規格。它描述目前已形成的產品方向、對 TradingAgents 的評估、推薦架構，以及仍需要進一步驗證的問題。

---

## 1. 背景與產品目標

我們想建立一套 **AI Investment Research Studio**。

它不是單純的：

- 股票問答 Chatbot
- 單一股票分析器
- 自動交易 Bot
- 固定 workflow 的 multi-agent demo

而是更接近一個由 AI agents 組成的投資研究團隊。

使用者的角色是：

> **Capital Provider / Investor / CIO**

使用者希望做到：

1. 提供各種外部資訊與媒體給研究團隊
2. 讓不同研究角色獨立研究
3. 看見目前團隊正在研究什麼
4. 看見各研究主題的進度與產出
5. 對研究員提出問題、追問、挑戰 thesis
6. 讓研究結果累積成有生命週期的投資 thesis
7. 最後由 Trader / Portfolio Manager 綜合研究做投資決策
8. 在事後追蹤 thesis 與決策是否正確，形成 feedback loop

---

## 2. 原始角色構想

### 2.1 Trader

責任：

- 綜合各研究員輸出
- 評估目前是否值得交易
- 給出最終 investment action
- 考量：
  - conviction
  - position sizing
  - horizon
  - entry condition
  - invalidation
  - risk

---

### 2.2 Industry Research

責任：

- 產業背景
- 產業結構
- 上下游供應鏈
- 競爭格局
- 估值框架
- 產業 narrative
- 二階受益者
- 長期結構性趨勢

例：

- AI Datacenter
- Nuclear / SMR
- Semiconductor Equipment
- Copper
- Stablecoin infrastructure

---

### 2.3 Macro Research

責任：

- 全球經濟
- 利率
- 通膨
- 成長
- 流動性
- 央行政策
- 國際政治
- 地緣政治
- 貿易與制裁
- 主要經濟體差異

理想上可以拆成：

- Monetary Policy
- Growth & Inflation
- Liquidity
- Geopolitical

---

### 2.4 Market Heat / Market Intelligence

責任：

- 市場情緒
- 資金流
- Positioning
- Attention
- Crowding
- 過熱 / 過冷程度

可能資料：

- ETF flow
- options positioning
- put/call
- IV skew
- dealer gamma
- short interest
- market breadth
- CFTC positioning
- institutional positioning

台股額外：

- 外資
- 投信
- 自營商
- 融資融券
- 借券
- 期貨 OI
- 選擇權 positioning

---

### 2.5 Technical / Quant

責任：

- 價格與量
- 技術指標
- 趨勢
- volatility
- regime
- factor
- relative strength
- cross-sectional signal

重要原則：

> 不要讓 LLM 自己計算 RSI、MACD、volatility 等 deterministic 指標。

建議：

```text
Python / Quant Engine
        ↓
Structured JSON
        ↓
LLM interpretation
```

---

## 3. 產品體驗目標

使用者希望能像管理一個研究團隊。

例如：

```text
最近我聽到 SMR 很值得研究
```

系統不應該要求使用者先指定 ticker。

理想流程：

```text
Investor
  ↓
Chief Investment Officer / Chief of Staff
  ↓
理解這是一個 topic-driven research request
  ↓
拆解研究任務
  ├─ Industry Structure
  ├─ Supply Chain
  ├─ Macro / Policy
  ├─ Narrative
  ├─ Public Companies
  ├─ Valuation
  └─ Risks
  ↓
形成 research project
  ↓
逐步建立 thesis
  ↓
最後才決定是否需要送進 Trading Committee
```

---

# 4. TradingAgents 評估

我們發現已有：

> **TradingAgents — Multi-Agents LLM Financial Trading Framework**

主要官方專案：

- GitHub: `TauricResearch/TradingAgents`
- Project site: `tradingagents-ai.github.io`
- Paper: `TradingAgents: Multi-Agents LLM Financial Trading Framework`

目前評估結論：

> **TradingAgents 不能直接完整符合 Investment Research Studio 的需求，但非常適合拿來當「Trading Committee Engine」。**

---

## 5. TradingAgents 已有能力

TradingAgents 的典型 workflow：

```text
Analysts
  ↓
Bull / Bear Researchers
  ↓
Research Manager
  ↓
Trader
  ↓
Risk Debate
  ↓
Portfolio Manager
```

現有主要 analyst：

- Market Analyst
- Social / Sentiment Analyst
- News Analyst
- Fundamentals Analyst

其他角色：

- Bull Researcher
- Bear Researcher
- Research Manager
- Trader
- Aggressive Risk Analyst
- Conservative Risk Analyst
- Neutral Risk Analyst
- Portfolio Manager

---

## 6. TradingAgents 適配度

### 6.1 Trader

適配度：

> 9 / 10

非常接近需求。

現有：

```text
Analysts
  ↓
Bull / Bear
  ↓
Research Manager
  ↓
Trader
  ↓
Risk
  ↓
Portfolio Manager
```

這比單一 Trader Agent 更完整。

---

### 6.2 Industry Research

適配度：

> 4 / 10

現有 Fundamentals Analyst 主要偏：

- company fundamentals
- balance sheet
- cash flow
- income statement

不足：

- industry structure
- upstream/downstream
- supply chain mapping
- second-order beneficiaries
- narrative evolution
- industry valuation framework
- competitive dynamics

因此應另建：

```text
Industry Research Desk
  ├─ Industry Structure Analyst
  ├─ Supply Chain Analyst
  └─ Narrative Analyst
```

---

### 6.3 Macro

適配度：

> 7 / 10

TradingAgents 已具備部分：

- global news
- macro indicators
- FRED
- prediction markets
- geopolitical queries

但目前比較像：

> News Analyst 擁有 macro tools

而不是：

> 真正獨立的 Macro Research Desk

建議拆出：

```text
Macro Desk
  ├─ Monetary Policy
  ├─ Growth & Inflation
  ├─ Liquidity
  └─ Geopolitical
```

---

### 6.4 Market Heat

適配度：

> 5 / 10

已有：

- Yahoo News
- StockTwits
- Reddit
- sentiment related data

不足：

- ETF flow
- options positioning
- gamma
- IV skew
- short interest
- breadth
- CFTC
- institutional flow

建議拆成：

```text
Market Intelligence Desk
  ├─ Sentiment
  ├─ Flow
  ├─ Positioning
  └─ Attention
```

---

### 6.5 Technical / Quant

適配度：

> 8 / 10

已有：

- stock data
- indicators
- verified market snapshot

適合作為基礎。

但建議：

```text
Quant Engine
  ↓
deterministic calculations
  ↓
structured feature payload
  ↓
Technical Analyst Agent
```

---

## 7. TradingAgents 最大缺口

### 7.1 User-provided Media Ingestion

適配度：

> 2 / 10

我們真正需要 ingest：

- YouTube
- Podcast
- News article
- PDF research reports
- X / Twitter posts
- Interviews
- Earnings calls
- Personal notes
- Screenshots
- Conference transcripts

TradingAgents 核心比較偏：

```python
propagate(company_name, trade_date)
```

也就是：

> ticker/date-driven

而我們需要：

> topic/evidence/media-driven

這是最大的產品差異。

---

### 7.2 Thesis Lifecycle

適配度：

> 4 / 10

TradingAgents 有 reports。

但是：

> Report != Thesis

Thesis 應該有生命週期。

建議 domain model：

```python
class Thesis:
    thesis_id: str
    topic: str
    asset_universe: list[str]

    claim: str

    evidence_for: list[str]
    evidence_against: list[str]

    assumptions: list[str]
    catalysts: list[str]
    invalidation_conditions: list[str]

    horizon: str
    confidence: float

    valuation_context: str | None

    status: str
    version: int

    outcome: str | None
```

可能狀態：

```text
draft
researching
active
challenged
invalidated
closed
```

---

### 7.3 Research Team Dashboard

適配度：

> 2 / 10

使用者需要看到：

```text
Research Projects
  ├─ SMR
  │   ├─ Industry: done
  │   ├─ Supply Chain: running
  │   ├─ Macro: blocked
  │   └─ Valuation: queued
  │
  └─ Copper
      ├─ China Demand: done
      └─ Mine Supply: running
```

TradingAgents 目前比較像：

- CLI execution
- workflow report output

不是：

- research operating system
- task dashboard
- team status UI

---

### 7.4 Free-form Topic Discussion

適配度：

> 2 / 10

使用者希望問：

```text
最近我聽到 SMR 很值得研究，你們怎麼看？
```

這需要：

- topic understanding
- task planning
- dynamic agent activation
- research project creation

而不是：

```text
ticker + date
```

因此需要一個：

> Chief of Staff / CIO Router

---

# 8. 核心判斷

目前最重要的架構判斷：

> **TradingAgents 是 trade-decision pipeline，不是 research operating system。**

所以不應該要求 TradingAgents 負責整個產品。

更合理的定位：

> **TradingAgents = Trading Committee Engine**

---

# 9. 建議整體架構

```text
Investor Interface
  Chat / Dashboard / Research Status
        ↓
Chief Investment Officer / Chief of Staff
  intent routing
  research planning
  task assignment
        ↓
Research OS + Topic Studio
        ↓
Research Desks
  ├─ Industry
  ├─ Macro
  ├─ Fundamental
  ├─ Market Intelligence
  ├─ Quant
  └─ Narrative
        ↓
Thesis Registry
Evidence Store
Research Memory
        ↓
TradingAgents-based Committee
  ├─ Bull
  ├─ Bear
  ├─ Research Manager
  ├─ Trader
  ├─ Risk
  └─ Portfolio Manager
```

---

# 10. Bounded Context 建議

不要把所有功能都塞進 TradingAgents fork。

推薦：

```text
investment-studio/
  src/
    studio_api/
    studio_domain/
    studio_schemas/
    source_tools/

  tests/
    source_tools/
    studio_api/
    studio_domain/
    studio_schemas/
```

未實作前不要保留空的 `packages/`、`services/`、`vendor/` scaffold。當 workflow、committee 或外部 TradingAgents integration 變成具體需求時，再新增具名模組或依賴邊界。

另一種做法：

```text
TradingAgentsGraph
    ↓
wrap as
    ↓
Trading Committee Service
```

---

## 11. Trading Committee API 概念

例如：

```http
POST /committee/evaluate
```

Input：

```json
{
  "topic": "SMR",
  "assets": ["OKLO", "SMR", "CCJ"],
  "thesis_ids": [
    "thesis-001",
    "thesis-002"
  ],
  "evidence_ids": [
    "ev-101",
    "ev-102"
  ],
  "portfolio_context": {
    "cash": 0.35,
    "existing_positions": [],
    "risk_budget": "medium"
  }
}
```

Output：

```json
{
  "decision": "WATCH",
  "asset": "OKLO",
  "conviction": 0.68,
  "position_size": 0.0,
  "horizon": "6-18 months",
  "entry_conditions": [
    "valuation compression",
    "regulatory milestone"
  ],
  "invalidation_conditions": [
    "project delay beyond X",
    "capital requirement exceeds Y"
  ],
  "risk_review": {
    "primary_risks": []
  }
}
```

---

# 12. 不建議方案

## 12.1 不建議：直接深度 fork TradingAgents

原因：

TradingAgents state 本質偏向：

```text
company_of_interest
trade_date
market_report
sentiment_report
news_report
fundamentals_report
investment_debate
trader_plan
risk_debate
final_trade_decision
```

但 Investment Research Studio 需要：

```text
research_project
research_task
topic
evidence
source
media
thesis
hypothesis
open_question
agent_assignment
status
dependency
discussion
revision
```

兩者 domain 不同。

硬塞容易造成：

- state explosion
- graph complexity
- tight coupling
- difficult upgrade path
- difficult debugging

---

## 12.2 不建議：全部重寫成 PydanticAI

TradingAgents 已經有：

- LangGraph orchestration
- conditional routing
- checkpoints
- debate rounds
- risk rounds
- reports
- provider abstraction
- tools
- decision log
- reflection

全部重寫成本高，且暫時沒有明確收益。

---

## 12.3 不建議：用 Hermes / OpenClaw 取代所有核心 workflow

高階 autonomous agent 適合：

- open-ended exploration
- ad-hoc task
- broad tool use

但 investment decision pipeline 需要：

- reproducibility
- deterministic state
- clear audit trail
- bounded workflow
- evaluation
- replay
- checkpoint

因此：

> autonomous agent 適合 research exploration，不一定適合 final trading committee。

---

# 13. 推薦技術方向

## Frontend

```text
Next.js
```

用途：

- Chat
- Research project dashboard
- Thesis board
- Evidence viewer
- Agent activity timeline
- Decision review

---

## Backend API

```text
FastAPI
```

---

## Research Orchestration

候選：

```text
PydanticAI
LangGraph
```

目前偏向：

- open-ended research：PydanticAI / agentic
- bounded committee workflow：LangGraph / TradingAgents

---

## Trading Committee

```text
TradingAgents
LangGraph
```

---

## Domain Model

```text
Pydantic
```

---

## Main Database

```text
PostgreSQL
```

---

## Evidence Retrieval

```text
PostgreSQL FTS
+
pgvector
+
RRF / hybrid search
```

這與目前既有技術經驗一致。

---

## Raw Media

```text
S3 / MinIO
```

---

## Background Jobs

初期：

```text
Celery
```

長期：

```text
Temporal
```

---

## Observability

```text
Langfuse
OpenTelemetry
```

---

# 14. 建議 Domain Model

至少需要以下核心 entity。

---

## ResearchProject

```python
class ResearchProject:
    id: str
    title: str
    topic: str

    objective: str

    status: str

    created_by: str

    asset_universe: list[str]

    created_at: datetime
    updated_at: datetime
```

---

## ResearchTask

```python
class ResearchTask:
    id: str
    project_id: str

    title: str
    description: str

    desk: str
    assigned_agent: str | None

    status: str

    dependencies: list[str]

    output_artifact_ids: list[str]

    created_at: datetime
    updated_at: datetime
```

可能狀態：

```text
queued
running
blocked
review
done
failed
```

---

## Evidence

```python
class Evidence:
    id: str

    source_type: str
    source_uri: str | None

    title: str
    content: str

    published_at: datetime | None
    ingested_at: datetime

    author: str | None

    entities: list[str]
    topics: list[str]

    credibility_score: float | None
```

---

## Thesis

```python
class Thesis:
    id: str
    project_id: str

    title: str
    claim: str

    evidence_for: list[str]
    evidence_against: list[str]

    assumptions: list[str]
    catalysts: list[str]
    invalidation_conditions: list[str]

    horizon: str
    confidence: float

    status: str
    version: int
```

---

## ResearchArtifact

```python
class ResearchArtifact:
    id: str
    project_id: str
    task_id: str | None

    artifact_type: str

    title: str
    content: str

    created_by_agent: str

    source_evidence_ids: list[str]

    created_at: datetime
```

可能 artifact：

```text
industry_report
macro_report
supply_chain_map
valuation_report
risk_report
technical_snapshot
market_heat_report
```

---

## Decision

```python
class InvestmentDecision:
    id: str

    project_id: str
    asset: str

    action: str

    conviction: float
    position_size: float | None

    horizon: str

    entry_conditions: list[str]
    invalidation_conditions: list[str]

    supporting_thesis_ids: list[str]

    created_at: datetime
```

---

# 15. 建議實作階段

## Phase 1 — Validate Trading Committee

目標：

> 先確認 TradingAgents 本身是否真的能產生有價值的 decision process。

做法：

- clone / vendor TradingAgents
- 跑單一 ticker
- 保存完整：
  - analyst reports
  - bull/bear debate
  - research manager
  - trader
  - risk debate
  - portfolio decision

不要先大改 core。

---

## Phase 2 — External Research Context

目前：

```python
propagate(
    company_name,
    trade_date,
)
```

理想包裝成：

```python
evaluate(
    instrument,
    trade_date,
    research_context,
    portfolio_context,
)
```

其中：

```python
research_context = {
    "theses": [],
    "evidence": [],
    "industry_reports": [],
    "macro_reports": [],
}
```

關鍵概念：

> TradingAgents 不需要自己完成所有 research。

它應該：

> consume upstream research output

---

## Phase 3 — Research Studio

建立：

- Topic Research
- Media Ingestion
- Research Projects
- Research Tasks
- Thesis Registry
- Evidence Store
- Dashboard
- Investor Chat

---

## Phase 4 — Feedback Loop

追蹤：

- thesis outcome
- decision outcome
- forecast calibration
- analyst accuracy
- source reliability
- missed risks
- invalidation timing

---

# 16. 對 Codex Agent 的討論目標

請 Codex 優先協助分析以下問題。

---

## Q1. 如何把 TradingAgents 隔離成 Bounded Context？

需要評估：

```text
direct Python import
vs
internal package
vs
separate service
```

考量：

- upgrade upstream
- state sharing
- latency
- debugging
- deployment
- schema coupling

---

## Q2. 是否應直接 vendor / fork TradingAgents？

候選：

### Option A

```text
git submodule
```

### Option B

```text
fork repository
```

### Option C

```text
copy selected modules
```

### Option D

```text
independent service dependency
```

需要分析長期 maintainability。

---

## Q3. TradingAgents state 如何接收 external research context？

需要檢查：

- `AgentState`
- graph input
- prompt construction
- reports
- memory

希望避免：

```text
把整個 Evidence Store 塞進 graph state
```

可能設計：

```text
graph state
  ↓
only references / compact context
```

例如：

```python
research_context_ref: str
selected_thesis_ids: list[str]
selected_artifact_ids: list[str]
```

agent 執行時再 fetch。

---

## Q4. Research Orchestrator 要用 PydanticAI 還是 LangGraph？

需要根據實際 code complexity 比較。

### Research Studio 特性

- open-ended
- topic driven
- dynamic tasks
- agent delegation
- user interruption
- partial results
- long-running jobs

### Trading Committee 特性

- bounded
- repeatable
- stateful
- auditable
- fixed review stages

目前假設：

```text
Research Orchestrator → PydanticAI
Trading Committee → LangGraph / TradingAgents
```

但需驗證。

---

## Q5. Agent Task Model 如何設計？

例如：

```python
class AgentTask:
    id: str
    project_id: str

    objective: str

    assigned_role: str

    input_artifact_ids: list[str]
    output_schema: str

    status: str

    parent_task_id: str | None

    dependencies: list[str]
```

需要支援：

- dynamic task decomposition
- retry
- human intervention
- cancellation
- partial result
- dependency graph

---

## Q6. 如何實作 Investor 可見的 Agent Activity？

使用者需要看到：

```text
Industry Analyst
  Researching SMR regulatory landscape
  60%

Supply Chain Analyst
  Waiting for Industry Structure output
  blocked

Macro Analyst
  Completed
```

需要討論：

- event model
- task state
- streaming
- durable event log
- WebSocket / SSE

---

## Q7. Evidence Citation Contract

所有 research artifact 應該可以追溯 evidence。

可能要求：

```python
class EvidenceCitation:
    evidence_id: str
    quote_span: str | None
    claim: str
```

需要避免：

- unsupported claim
- citation drift
- hallucinated source

---

## Q8. Thesis Versioning

Thesis 應該是 mutable 還是 append-only？

候選：

```text
mutable row + history table
```

或：

```text
event sourced
```

需要考慮：

- audit
- diff
- rollback
- outcome attribution

---

## Q9. Memory 邊界

至少可能有：

```text
Agent Memory
Project Memory
Thesis Memory
Decision Memory
User Memory
```

需要避免所有 memory 混在一起。

---

## Q10. MVP 的最小 vertical slice 是什麼？

目前建議：

```text
User submits topic
  ↓
CIO creates research project
  ↓
2-3 desks produce artifacts
  ↓
Create one thesis
  ↓
User reviews
  ↓
Send one ticker into Trading Committee
  ↓
Return decision
```

例：

```text
SMR
  ↓
Industry
Macro
Fundamental
  ↓
Thesis
  ↓
OKLO
  ↓
Trading Committee
```

---

# 17. 重要設計原則

## 17.1 Research 與 Trading Decision 分離

```text
Research
!=
Decision
```

---

## 17.2 Evidence 與 Agent Output 分離

```text
Raw Evidence
!=
Research Artifact
```

---

## 17.3 Report 與 Thesis 分離

```text
Report
!=
Thesis
```

---

## 17.4 Agent 與 Role 分離

```text
Role
!=
Runtime Agent Instance
```

一個 role 可以由不同 model / agent runtime 執行。

---

## 17.5 Deterministic Computation 與 LLM Reasoning 分離

```text
Quant Calculation
!=
LLM Interpretation
```

---

## 17.6 TradingAgents 不應成為整個 Domain Model

TradingAgents 只是：

```text
Trading Committee bounded context
```

---

# 18. 目前暫定結論

### TradingAgents 適合：

- analyst workflow
- bull/bear debate
- trader
- risk review
- portfolio manager
- single instrument decision process
- post-decision reflection

### TradingAgents 不適合直接負責：

- arbitrary media ingestion
- free-form topic research
- industry research
- supply chain mapping
- thesis lifecycle
- research task management
- team dashboard
- investor discussion layer

---

# 19. 最終推薦方向

目前最佳方向：

```text
Investment Research Studio
        ↓
Research OS
        ↓
Research Desks
        ↓
Thesis Registry
        ↓
Evidence Store
        ↓
Trading Committee
        ↓
TradingAgents
```

不是：

```text
TradingAgents
  ↓
硬塞所有功能
```

---

# 20. Codex Agent 工作方式建議

在提出 code change 前，請先：

1. 閱讀目前 repository structure
2. 閱讀 README / architecture docs / ADR
3. 找出：
   - domain model
   - orchestration boundary
   - persistence layer
   - event model
4. 檢查是否已存在類似 abstraction
5. 再討論設計

請避免一開始直接產生大量程式碼。

優先輸出：

```text
1. Current state understanding
2. Relevant existing code
3. Architecture constraints
4. Candidate designs
5. Trade-offs
6. Recommended design
7. Minimal implementation path
8. Risks / unknowns
```

在 context 不足時，明確指出缺失，不要自行假設。

---

# 21. 下一步建議討論順序

與 Codex 建議依序討論：

```text
1. Repository / monorepo boundary
2. Domain model
3. TradingAgents integration boundary
4. Research task state machine
5. Evidence model
6. Thesis model
7. Event / activity stream
8. Research orchestrator
9. MVP vertical slice
10. Observability / evaluation
```

---

## TL;DR

核心判斷只有一句：

> **把 TradingAgents 當成一個成熟的 Trading Committee Engine，而不是整個 Investment Research Studio。**

Research Studio 應該有自己的：

- Research Project
- Research Task
- Evidence
- Research Artifact
- Thesis
- Activity
- Decision

然後在需要形成具體投資決策時，把整理過的 research context 送入 TradingAgents。
