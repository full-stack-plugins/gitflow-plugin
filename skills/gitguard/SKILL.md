---
name: gitguard
description: 当用户需要约束智能体研发中的分支、Worktree、变更范围、最终合并候选或 Git 写操作安全时使用；先识别仓库现行 Git 流，再执行可核验检查，不把局部 Git PASS 当成工程质量通过。
---

# GitGuard

GitGuard 是 Partme Guard 的 Git 分支与合并安全入口。

## 使用顺序

1. 识别仓库现行 Git 模型、目标分支和保护规则。
2. 检查任务分支、Worktree、变更范围与允许路径。
3. 检查最终合并候选与最新目标版本。
4. 将结果交给 GuardEngine 或独立 CI；不自行签发技术审批。
5. 写入失败或结果不确定时先对账，不自动重放。

## 边界

- 不替代 ArchGuard、CodeGuard、TestGuard、SpecGuard 的专业检查。
- 不绕过受保护分支、必需检查或审计。
- 没有真实 Git 证据时报告 UNKNOWN，不报 PASS。
