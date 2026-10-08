## Why

现有插件能约束分支角色、来源和流转，但提交检查主要依靠单个正则，缺少逐规则严重级别、机器可消费修正值、业务仓库 PR 检查及组织基线接入。让 AI、本地 Hook 与 CI 依据同一契约形成检查、反馈、修正、复检闭环。

## What Changes

- 增加兼容 v1 的 workflow v2：逐规则 off/warn/error、稳定编号、结构化结果和确定性修正建议。
- 提供提交格式/长度、作者、Signed-off-by、AI 声明、Tag 规则；保留已有分支来源、方向和保护硬门禁。
- CLI/MCP/原生 commit-msg 共用引擎，增加规则解释与接线诊断；检查不会自动修复、提交、fetch 或安装 Hook。
- 新增只读提交范围与 PR 检查、squash 候选消息检查和可供业务仓库调用的 GitHub Action。使用 base 中受信策略，拒绝 PR 修改规则后自我放行。
- 引入固定 SHA-256 的组织规则快照与不可覆盖规则，缺失/篡改拒绝静默降级。导入仅显式 apply；项目规则保留来源追踪。
- 同步九技能、说明、测试与分发版本；本次功能不依赖 commit-check 或第三方运行时包。

## Capabilities

### New Capabilities
- `policy-rules`: 可配置规则与结构化反馈、多入口一致性及 v1 兼容。
- `ci-governance`: 提交范围、PR 合并方向与受信策略检查、Action 入口。
- `organization-policy`: 固定摘要组织快照、锁定规则、规则解释与接线诊断。

### Modified Capabilities

无现存 OpenSpec capability；既有 R01–R25 原文作为兼容性基线，保留。

## Impact

插件 scripts/gitflow、CLI/MCP/Hook、Action 与 tests；独立 git-skills 的使用契约及插件 vendor 快照；市场版本与发行验证。无全局安装，无实际业务仓库分支变更，无自动设置服务端保护。

不在本次范围：托管 GitHub App、识别未声明的 AI 生成代码、自动重写历史、密码学签名验证、通用文件内容质量检查。GitFlow 治理结果与 CodeGuard 质量证据保持分离。
