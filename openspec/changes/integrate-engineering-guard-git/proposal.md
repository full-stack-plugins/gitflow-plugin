## Why

GitFlow 已有分支策略、组织基线及 CI 提交范围检查，但 Git 元数据允许不等于架构和代码质量通过。统一工程守卫需要绑定实际操作、最终候选和可信授权，防止旧证据合入及并行任务引入语义冲突。

## What Changes

- 新增跨插件 Git 证据投影、任务变更范围、base/head/merge candidate 身份与授权执行接口。
- 扩展最终候选验证与目标引用比较更新；保留分支/范围检查和质量判定的独立性。
- P3 使用 CodeGraph 提供的影响事实进行语义冲突预警，最终仍以候选编译/测试/契约验证为准。
- 保留 Python 标准库、argv Git、.gitflow 布局、预览零副作用、显式 apply 和未知不放行。
- 规划 GitHub/GitLab CI、受保护分支、最小权限身份及恢复测试；服务端配置不由本轮执行。

## Capabilities

### New Capabilities

- `engineering-git-integration`: 操作证据、候选合入、范围与并发控制集成。

### Modified Capabilities

无。已有 ci-governance、policy-rules、organization-policy 不变；受控模式显式启用，不将 GitFlow v2 规则静默迁移为另一份策略。

## Impact

未来涉及 scripts/gitflow/service.py、ci.py、policy.py、rules.py、layout.py、CLI/MCP 和 action.yml；共享决策通过固定协议调用 Rust 内核，本仓不引入第二个质量策略引擎。

本轮仅规划，不修改执行代码、.gitflow 项目状态、分支、远端或发布版本。
