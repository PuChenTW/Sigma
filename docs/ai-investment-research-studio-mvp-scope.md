# AI Investment Research Studio — MVP Scope

> 本文件定義第一個可驗證 MVP 的範圍。
>
> 背景與長期架構請參考 `docs/ai-investment-research-studio-codex-context.md`。本文件只回答：第一版要做什麼、不做什麼，以及如何判斷 MVP 成立。

---

## 1. MVP 目標

MVP 要驗證一件事：

> 使用者能從一個 free-form investment topic 出發，讓 AI research team 產生 source-grounded thesis，並把該 thesis 交給 Trading Committee 形成一個可審核的 investment decision proposal。

這個 MVP 不是要先做完整投資平台，而是要證明核心 workflow 可以跑通：

```text
Topic
  -> Research Project
  -> Research Tasks
  -> Evidence
  -> Research Artifacts
  -> Thesis
  -> Trading Committee
  -> Decision Proposal
  -> User Approve / Reject
```

---

## 2. MVP Vertical Slice

第一版的主流程：

1. 使用者輸入一個研究主題。
2. CIO / Chief of Staff layer 解析主題，建立一個 `ResearchProject`。
3. 系統建立 2-3 個 `ResearchTask`，分派給研究面向。
4. 研究任務使用 `source_tools` 或其他資料來源取得 evidence。
5. 每個研究面向產出 source-grounded `ResearchArtifact`。
6. 系統彙整 artifact，建立一個 `Thesis`。
7. 使用者在 UI 中 review thesis、evidence、key assumptions、risks、catalysts。
8. 使用者選擇或確認一個 ticker / asset candidate。
9. 系統把 selected thesis + compact research context 送入 Trading Committee。
10. Trading Committee 產出 `DecisionProposal`。
11. 使用者 approve 或 reject proposal。
12. 系統記錄 decision outcome。

範例：

```text
SMR 值得研究嗎？
  -> ResearchProject: Small Modular Reactor investment opportunity
  -> Tasks:
       Industry: SMR industry structure and supply chain
       Macro / Policy: regulation, energy policy, financing environment
       Fundamental: public company candidates such as OKLO / SMR / CCJ
  -> Thesis
  -> Candidate asset: OKLO
  -> Trading Committee decision
```

---

## 3. In Scope

### 3.1 Product Workflow

- Free-form topic submission.
- Research project creation.
- Basic task planning by research facet.
- Task status tracking:
  - queued
  - running
  - review
  - done
  - failed
- Research artifact generation with citations.
- Thesis generation from artifacts.
- Thesis review screen.
- One-asset Trading Committee evaluation.
- Decision proposal review.
- User approve / reject action.

### 3.2 Research Desks

MVP only needs 2-3 desks:

- **Industry Research**
  - industry structure
  - supply chain
  - competitive landscape
  - second-order beneficiaries
- **Macro / Policy Research**
  - rates
  - regulation
  - policy support / constraints
  - geopolitical or energy-policy context
- **Fundamental / Company Candidate Research**
  - public company candidates
  - business exposure
  - basic financial / valuation context

Market Intelligence, Technical / Quant, and Narrative can be represented as future desks unless needed for the specific MVP demo.

### 3.3 Evidence

MVP evidence should support:

- URL / article ingestion.
- RSS item ingestion where useful.
- YouTube / transcript ingestion where `source_tools` already supports it.
- Manual note input.
- Evidence citation by `evidence_id`.

Every generated research artifact should preserve which evidence it used.

### 3.4 UI Screens

Use the prototype as workflow reference. MVP UI should include:

- **Dashboard**
  - current research projects
  - task status
  - pending decision proposals
- **Assign Task**
  - topic input
  - research facet selection
  - priority
- **Research Project / Thesis Detail**
  - thesis claim
  - summary
  - evidence for / against
  - assumptions
  - catalysts
  - invalidation conditions
  - related artifacts
- **Decision Desk**
  - action
  - asset
  - conviction
  - suggested size
  - entry conditions
  - invalidation / stop conditions
  - supporting thesis references
  - approve / reject

Positions can be minimal in MVP: record approved proposals as decision outcomes, but full portfolio management is out of scope.

---

## 4. Out of Scope

MVP should not include:

- Automated trade execution.
- Full portfolio accounting.
- Multi-user collaboration.
- Production-grade auth / permissions.
- Mobile-first optimization beyond basic responsive layout.
- All asset classes.
- Full market data platform.
- Full feedback-loop analytics.
- Analyst accuracy scoring.
- Source reliability scoring beyond simple metadata.
- Full thesis version diff UI.
- Deep fork of TradingAgents.
- Large autonomous agent framework before the vertical slice works.
- Complex event sourcing unless required by implementation.

---

## 5. Core Domain Objects

MVP should model these explicitly:

```text
ResearchProject
ResearchTask
Evidence
EvidenceCitation
ResearchArtifact
Thesis
DecisionProposal
InvestmentDecision
ActivityEvent
```

Minimum required relationships:

```text
ResearchProject
  has many ResearchTask
  has many Evidence
  has many ResearchArtifact
  has many Thesis

ResearchTask
  belongs to ResearchProject
  outputs ResearchArtifact

ResearchArtifact
  cites Evidence
  may support Thesis

Thesis
  cites Evidence
  derives from ResearchArtifact
  may be sent to Trading Committee

DecisionProposal
  references Thesis
  becomes InvestmentDecision after approve / reject
```

---

## 6. Trading Committee Boundary

TradingAgents, if used, should be wrapped as a bounded Trading Committee engine.

MVP input should be compact and explicit:

```json
{
  "topic": "SMR",
  "asset": "OKLO",
  "thesis_ids": ["thesis-001"],
  "artifact_ids": ["artifact-001", "artifact-002"],
  "evidence_ids": ["ev-001", "ev-002"],
  "portfolio_context": {
    "risk_budget": "medium",
    "existing_positions": []
  }
}
```

MVP output should be a decision proposal:

```json
{
  "action": "WATCH",
  "asset": "OKLO",
  "conviction": 0.68,
  "suggested_position_size": 0.0,
  "horizon": "6-18 months",
  "entry_conditions": [],
  "invalidation_conditions": [],
  "primary_risks": [],
  "supporting_thesis_ids": ["thesis-001"]
}
```

Do not pass the entire Evidence Store into graph state. Pass selected IDs and compact summaries.

---

## 7. Acceptance Criteria

MVP is successful when the following can be demonstrated end to end:

1. A user submits a topic without specifying a ticker.
2. The system creates a research project and task plan.
3. At least two research tasks complete with source-grounded artifacts.
4. The system creates one thesis with:
   - claim
   - supporting evidence
   - counter-evidence or uncertainties
   - assumptions
   - catalysts
   - invalidation conditions
   - confidence
5. The user can inspect the thesis and its evidence references.
6. The system selects or accepts one asset candidate for committee review.
7. Trading Committee returns a structured proposal.
8. The user can approve or reject the proposal.
9. The decision and rationale are persisted.
10. The UI shows current project/task/decision status.

---

## 8. Suggested Implementation Order

1. Define domain schemas and persistence boundary.
2. Create minimal backend API for project, task, evidence, artifact, thesis, and decision records.
3. Build topic submission and project creation.
4. Implement deterministic task planner for 2-3 research facets before adding more autonomous planning.
5. Wire evidence ingestion using existing `source_tools` where applicable.
6. Generate research artifacts with explicit citation contract.
7. Generate thesis from artifacts.
8. Build minimal UI matching the prototype workflow.
9. Wrap Trading Committee behind one API call.
10. Add approve / reject decision handling.

---

## 9. Main Risks

- Research artifacts may look plausible without enough evidence grounding.
- Topic-to-asset selection can become speculative if not separated from thesis generation.
- TradingAgents integration can leak its internal state model into Studio domain objects.
- UI may drift into portfolio dashboard work before research workflow is proven.
- Agent orchestration can become too abstract before there are enough real task patterns.

---

## 10. Non-Goals For First Demo

The first demo should not try to prove investment performance.

It should prove:

- topic-driven research works,
- evidence is traceable,
- thesis is inspectable,
- committee decision is structured,
- user has final control.
