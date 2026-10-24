# GitGuard（分支规范防护）

> 分支、提交、同步、发布、Hook 与 CI 检查已实现。

**版本**：0.4.0 · **许可证**：Apache-2.0 · **技能**：9 个

[English](README.en.md)

## 项目定位

GitGuard 是 Partme Guard 研发防护体系中的独立插件，命令前缀为 gitguard。它不依赖统一总命令，可独立安装、独立发版、独立执行。

## CLI 命令

| 命令 | 类型 |
| :--- | :--- |
| install | 独立入口 |
| uninstall | 独立入口 |
| upgrade | 独立入口 |
| version | 独立入口 |
| doctor | 独立入口 |
| status | 独立入口 |
| discover | 独立入口 |
| init | 独立入口 |
| check | 独立入口 |
| audit | 独立入口 |
| policy | 独立入口 |
| branch | 独立入口 |
| sync | 独立入口 |
| release | 独立入口 |
| hooks | 独立入口 |
| report | 独立入口 |
| completion | 独立入口 |

## 安装

~~~bash
codex plugin marketplace add partme-ai/full-stack-plugins
codex plugin add gitguard-plugin@full-stack-plugins
~~~

## 快速开始

~~~bash
gitguard version
gitguard doctor
gitguard status
~~~

## 当前状态

分支、提交、同步、发布、Hook 与 CI 检查已实现。

没有真实执行证据时，不报告 PASS；未实现能力报告 DESIGN_ONLY 或 UNVERIFIED。

## 架构

命令入口、生命周期、只读检查和证据边界见 product-docs/GitGuard/ 与 docs/。

## 边界

- 不合并为 Partme Guard 总命令。
- 不替代其他 Guard 的专业判断。
- 不自动提交、推送或修改用户代码。

## 验证

~~~bash
python3 -m pytest -q
~~~

## 许可证

Apache-2.0
