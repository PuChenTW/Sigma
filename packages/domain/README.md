# Domain Package

Product domain model for AI Investment Research Studio.

## Core Concepts

- `ResearchProject`
- `ResearchTask`
- `Evidence`
- `EvidenceCitation`
- `ResearchArtifact`
- `Thesis`
- `DecisionProposal`
- `InvestmentDecision`
- `Position`
- `ActivityEvent`

## Rules

- Research is separate from investment decisions.
- Raw evidence is separate from research artifacts.
- A report is not a thesis.
- A role is not a runtime agent instance.
- Deterministic computation is separate from LLM reasoning.
- TradingAgents state must not become the Studio domain model.

