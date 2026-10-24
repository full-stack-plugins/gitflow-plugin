## Purpose

为 Partme Guard 提供 engineering-git-integration 的可观察行为契约，统一已批准约束、当前候选和独立验证证据的关联，并明确未知、失败、兼容模式与越权情况下不得伪造工程通过的边界。

## ADDED Requirements

### Requirement: EG-GIT-001 Operation evidence

插件 SHALL 输出与 action、真实仓库、任务、base/head/target、策略摘要匹配的 Git 证据；Git allow 不升级质量，现有 quality_decision=not_evaluated 保持。

#### Scenario: EG-GIT-001 contract behavior
- **WHEN** Git 命名与方向通过但代码验证缺失
- **THEN** 仅满足 Git 义务，统一门禁仍不允许合入

### Requirement: EG-GIT-002 Change scope

插件 SHALL 根据批准任务范围核对实际新增、删除、重命名、模式与公共契约变更；策略来源使用受信基线，候选不能通过自改范围放行。

#### Scenario: EG-GIT-002 contract behavior
- **WHEN** Agent 移动文件越过允许模块或修改门禁配置
- **THEN** 记录越界与原始对象；不采用候选中的放宽规则

### Requirement: EG-GIT-003 Exact merge candidate

插件 MUST 在受控模式绑定最终候选、当前目标版本及策略；目标变化触发重验，合入执行使用支持预期引用版本的原子机制。

#### Scenario: EG-GIT-003 contract behavior
- **WHEN** 检查后另一个任务合入目标分支
- **THEN** 旧决定失效，不使用旧 PASS 合入新目标

### Requirement: EG-GIT-004 Independent CI

插件 SHALL 保留可信 base 策略的只读范围检查，并接入固定生产者的独立工程证据；GitHub/GitLab 服务端保护和身份均须实际核验。

#### Scenario: EG-GIT-004 contract behavior
- **WHEN** PR 修改自身检查脚本或组织规则
- **THEN** 受信引擎与基线仍生效；配置文件存在不证明 required check 已启用

### Requirement: EG-GIT-005 Safe execution and conflicts

插件 SHALL 保留 argv、预览零副作用、显式 apply、操作授权、.gitflow 位置及未知恢复；语义冲突仅预警，未知 Git 写结果须对账而非重放。

#### Scenario: EG-GIT-005 contract behavior
- **WHEN** 网络中断导致 push 结果未知或两个任务语义相冲突
- **THEN** 保留 operationId 与真实 refs，复核后恢复；不擅自 force/reset/删分支
