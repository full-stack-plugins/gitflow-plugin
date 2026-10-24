> ⏸️ **已冻结（2026-10-09 用户决定）**：engineering-guard 系列整体冻结，暂停实施。保留任务与文档，不开始新任务、不新增计划、不并行推进实现；解冻需用户明确批准。

# 工程守卫实施任务

状态：全部待实施。本轮仅完成规划；下面的 fixture/测试模块为拟新增，不声称已经存在或执行。只在实现、目标 RED→GREEN、受影响回归及所需真实环境证据齐备后勾选。

依赖前缀：K=codeguard 内核，F=codegraph-plugin，H=codeguard-plugin，R=codereview-plugin，G=gitflow-plugin，W=flowguard-plugin。跨仓依赖通过任务 ID 引用，完成状态只在所属仓账本维护。所有实现先复核当前 HEAD 与用户修改；目标路径见 [design](design.md)。

## 1. P0 操作身份与候选

- [ ] 1.1 **EG-G01** 增加 GitFlow 报告统一投影，保留 quality_decision；测试 Git allow 不自动产生工程 allow。 依赖：EG-K01。规格：EG-GIT-001。
- [ ] 1.2 **EG-G02** 实现任务范围与实际 diff 比较，覆盖新增/删除/rename/mode/契约路径；候选自改范围反例拒绝。 依赖：EG-G01, EG-K03。规格：EG-GIT-002。
- [ ] 1.3 **EG-G03** 用临时仓和本地 bare remote 构造最终候选与目标 OID；目标变化必须失效，禁止改用户真实分支。 依赖：EG-G02, EG-K04。规格：EG-GIT-003。
- [ ] 1.4 **EG-G04** 实现受控 apply 的 grant/expected OID/操作授权核验与日志对账；重放、断连未知和外部 Git 竞态实测。 依赖：EG-G03, EG-K10。规格：EG-GIT-003, EG-GIT-005。

## 2. P0 独立 CI 与强制边界

- [ ] 2.1 **EG-G05** 在受信 base 规则下关联架构/代码/流程证据；PR 改脚本/策略不能自放行，保持 check 不执行 PR 代码。 依赖：EG-G04, EG-K08。规格：EG-GIT-002, EG-GIT-004。
- [ ] 2.2 **EG-G06** 完成 GitHub required check/合并队列实际接线与绕过验证，使用最小权限身份；没有管理员授权时不擅自改配置。 依赖：EG-G05。规格：EG-GIT-004。

## 3. P2 平台与兼容

- [ ] 3.1 **EG-G07** 完成 GitLab 合入候选/受保护分支等价适配与真实验收；标准库、argv、.gitflow、preview/apply、原 Hook/MCP 保持。 依赖：EG-G05。规格：EG-GIT-004, EG-GIT-005。

## 4. P3/P4 并行与演进

- [ ] 4.1 **EG-G08** 提供任务操作/变更集合给语义冲突分析，验证不同文件接口冲突、unknown 图谱和合法独立任务；不替代最终候选测试。 依赖：EG-G03, EG-F05。规格：EG-GIT-005。
- [ ] 4.2 **EG-G09** 建立基线传播、release/backport 与多 worktree 对账样例；merge/squash/rebase 独立声明已支持范围。 依赖：EG-G06, EG-G07, EG-K23。规格：EG-GIT-003, EG-GIT-005。
- [ ] 4.3 **EG-G10** 完成 N/N-1、不可变发布、validate_package/vendor/临时 Git 测试、真实服务端证据和回滚；不自动删除分支或撤销保护。 依赖：EG-G09。规格：EG-GIT-001, EG-GIT-004。
