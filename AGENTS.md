# GitFlow 开发规则

- 增量规格事实源：openspec/。既有 v0.1.5 契约保留在 docs/superpowers/specs/2026-10-07-gitflow.md 作为兼容性基线；新变更不得另建重复 Superpowers 规格。
- Python 3.11+ 标准库运行时；所有 Git 调用使用 argv，不调用 shell。
- 技能事实源为独立 git-skills 包；插件 skills/ 为锁定的自包含快照，通过 scripts/vendor_skills.py 同步。
- 遵守项目工作流与已有授权；查询不写项目，变更必须显式 apply。
- 未知、缺历史、远端未观察与损坏配置不能伪造通过。
- 测试使用临时仓库和本地 bare remote；不修改用户仓库分支。
- 不把 CLI/MCP/Hook 重放验证称为实际宿主安装验收。
