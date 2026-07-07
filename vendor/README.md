# Vendor

Third-party source snapshots, forks, or submodules live here only when the project intentionally vendors them.

## Current Guidance

Do not deep fork TradingAgents by default.

If TradingAgents is added, prefer a clear boundary:

- submodule or pinned source under `vendor/`
- wrapper in `services/trading-committee/`
- compact schemas in `packages/schemas/`

