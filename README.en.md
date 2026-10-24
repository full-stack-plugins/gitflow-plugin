# GitGuard (分支规范防护)

> 分支、提交、同步、发布、Hook 与 CI 检查已实现。

**Version**: 0.4.0 · **License**: Apache-2.0 · **Skills**: 9

[简体中文](README.md)

## Positioning

GitGuard is an independent plugin in the Partme Guard family. Its command prefix is gitguard. It is installed, versioned and executed independently.

## CLI Commands

| Command | Type |
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

## Installation

~~~bash
codex plugin marketplace add partme-ai/full-stack-plugins
codex plugin add gitguard-plugin@full-stack-plugins
~~~

## Quick Start

~~~bash
gitguard version
gitguard doctor
gitguard status
~~~

## Current Status

分支、提交、同步、发布、Hook 与 CI 检查已实现。

No PASS without real execution evidence. Unimplemented capabilities report DESIGN_ONLY or UNVERIFIED.

## Architecture

See product-docs/GitGuard/ and docs/ for command lifecycle, read-only checks and evidence boundaries.

## Boundaries

- Not merged into a single Partme Guard command.
- Does not replace another Guard's domain decision.
- Does not auto-commit, auto-push or modify user code.

## Verification

~~~bash
python3 -m pytest -q
~~~

## License

Apache-2.0
