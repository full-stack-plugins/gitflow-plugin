# 更新记录

## 0.1.4 — 2026-10-07

- 修复 Python 3.11 原生 Hook CLI 解析 `--` 及后续位置参数的兼容性；混合参数使用 parse_intermixed_args。
- v0.1.3 远端全量 CI 在 macOS/Python 3.13 通过，在 Linux/Python 3.11 发现 5 项原生 Hook 失败；此补丁保留真实失败记录并重新验证双平台。

## 0.1.3 — 2026-10-07

- 增加真实 Git 工作树检测；自动 Hook 在无 Git、bare 或缺失 cwd 时保持静默，不写入上下文记录。
- PreToolUse 按 git -C / cd 的实际目标判断，支持紧凑 -Cpath、worktree、子模块和仓库状态变化。
- 保留显式 discover/context/init；损坏 Git 元数据仍标为未验证。
- 增加项目触发与打包回归；修正旧版本断言，加入 Linux/macOS 全量 CI。

## 0.1.2 — 2026-10-07

- 使用用户确认的直线主干、平行分支与斜向汇合新版 logo。
- 对齐 CodeReview/Stitch 常见的 512 × 512 图标尺寸；透明 PNG 为 122,985 字节，优化前后缩放图像的 RGBA 像素完全一致。
- 同步插件及市场发布身份；Git 治理逻辑不变。

## 0.1.1 — 2026-10-07

- 新增基于 Git 官方标志二次创作的 workflow logo、原图与 CC BY 3.0 署名。
- 补齐版本固定的单仓市场清单、Kimi 技能/MCP 清单与三端展示字段，收录 Full Stack Plugins。
- CLI/MCP 版本同步为 0.1.1；Git 治理逻辑不变。宿主实际安装与服务端保护验收仍未完成。

## 0.1.0 — 2026-10-07

九技能锁快照、八个模板、标准库 CLI/MCP、Hook 与显式分支/同步/发布/恢复。仅本地交付，未宿主安装、公开发布或远端 CI 验收。
