# 实施验证 — 2026-10-08

规格事实源为本 change；实施前严格验证通过，按实际 OpenSpec CLI 推进，未虚构 Slash Command 调用。采用真实临时 Git 仓库的红灯/绿灯验证；运行时与测试输入指纹、原始红灯/全量输出见 docs/evidence/governance-v0.2.0.json 与对应 output.txt。

| 规格 | 实现 | 行为证据 |
|---|---|---|
| v1 兼容、闭合规则、warning 与修正 | policy/rules/service | 原有91项回归；test_policy_rules.py 全7项 |
| 同一引擎 CLI/MCP/原生 Hook | service/hooks/mcp | 同消息结果对照；实际 git commit；受管 merge 拒绝后经 recovery continue 成功 |
| 全范围、分离 HEAD、可信 base、squash | ci.py | test_ci_governance.py 全8项；缺对象/无祖先、恶意 head、错误合并方向、标签与候选 |
| Action 安全输入及返回码 | ci_check.py/action.yml | 恶意 shell/HTML 事件无执行并转义；真实成功与坏事件回放；YAML 解析 |
| 摘要、锁定、导入与诊断 | organization/diagnostics | test_organization_policy.py 全7项；未联网预览、不覆盖、漂移、来源、local 离线快照 |
| 不完整或恶意边界 | 各检查入口 | test_governance_boundaries.py 全11项；500条上限、浅历史、squash 作者及未知 signer、重复字段、symlink、MCP 注解 |

全量 **124/124 PASS**。包校验、官方 plugin/MCP Schema、90文件技能快照、9技能结构与 quick_validate、v2示例均通过。TRACE 为确定性基础分 4.43–4.46，不声称达到4.5全覆盖或真实任务效果验收。

自审修复两项：组织导入 MCP 网络副作用注解；共享定义缺失时仍校验引用的组织基线，防止同时删定义和基线绕过检查。未发现剩余阻断实现的问题。旧 v1 模板、项目 .gitflow 布局与显式 apply 边界保留。

未覆盖真实 ZCode/Codex 宿主安装、业务仓库 GitHub PR 实跑及管理员 required checks。仓库自身发布 CI 另按精确 SHA 查询；本地 event 回放不是业务 PR 实跑。发布过程和验收边界见 docs/release-v0.2.0.md。
