# GitFlow 开发规则

- 增量规格事实源：openspec/。既有 v0.1.5 契约保留在 docs/superpowers/specs/2026-10-07-gitflow.md 作为兼容性基线；新变更不得另建重复 Superpowers 规格。
- Python 3.11+ 标准库运行时；所有 Git 调用使用 argv，不调用 shell。
- 技能事实源为独立 git-skills 包；插件 skills/ 为锁定的自包含快照，通过 scripts/vendor_skills.py 同步。
- 遵守项目工作流与已有授权；查询不写项目，变更必须显式 apply。
- 未知、缺历史、远端未观察与损坏配置不能伪造通过。
- 测试使用临时仓库和本地 bare remote；不修改用户仓库分支。
- 不把 CLI/MCP/Hook 重放验证称为实际宿主安装验收。

<!-- partme-agent-plugin-policy:v1 -->
## Partme Agent Plugin Architecture Rules v1

- 组织级架构规范（跨 `full-aigc-plugins` 与 `full-stack-plugins` 的唯一事实源）：[Partme Agent Plugin Architecture Rules v1](https://github.com/full-aigc-plugins/.github/blob/main/docs/standards/partme-agent-plugin-architecture-rules-v1.md)。
- **Harness 可选**：默认直接使用 Skills + CLI/MCP；只有确有必要时才使用最多一个可发现的 `skills/*-harness/SKILL.md`，其中的 `scripts/harness.py` 同样可选。
- 不重复开发宿主 Agent Runtime、原生 CLI/MCP 业务执行器、持久数据库或权威任务状态。正式功能必须具备可核验的 Agent → Skill/Command → Tool → Artifact 调用链。
- 保留本仓库现有 OpenSpec、技能来源锁、安全门禁、版本发布及 CI 要求；静态检查不能替代真实宿主验收。
- CI 复用组织级 [Partme Plugin Architecture 检查器](https://github.com/full-aigc-plugins/.github/blob/main/scripts/check_plugin_architecture.py)，不得复制独立实现。
<!-- /partme-agent-plugin-policy:v1 -->
