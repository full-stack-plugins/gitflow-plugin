# GitFlow 验证记录

下方首版数据为历史记录；当前 v0.1.3 的 R19–R21 证据见本文末尾。

## 0.1.0 本地验证

2026-10-07：本地首版实现完成。对应 [规格](superpowers/specs/2026-10-07-gitflow.md) R01–R18，未把宿主安装、CI 或发行计入完成范围。源目录未 Git 初始化，没有提交、推送、安装或修改其他项目 refs。

**完整回归：69/69 PASS**，耗时 44.892 秒；Python 3.14.3、Git 2.48.1、macOS。所有 Git 写测试使用隔离临时工作树与本地 bare 远端。未在 Linux 或 Python 3.11 实际执行；Windows 写操作不支持 POSIX 锁。

九技能 quick_validate 与自包含引用通过；Agent Plugins 1.0.0 官方 plugin/mcp Schema 通过；技能来源锁90文件通过。TRACE静态评分4.43–4.46，均值4.44/5；它是启发式结构评估，不是技能在真实Agent中的效果验收。

独立审查实际复现了同名tag误判、原生集成拒绝、非快进推送、换行与原生命令语义、坏来源导致MCP中断；还指出来源可信度、脚本漂移和锁内身份问题。各项已加入复现测试并修复；活跃release回灌与冲突继续的残余也有原生Hook回归。未声称审查能证明没有其他问题。

## 验收与证据

| 要求 | 当前证据 |
|---|---|
| R01 | sources.json、八模板及 Fork 协作参考；来源/日期/项目扩展标识。 |
| R02 | 九个 SKILL.md quick_validate；独立目录运行每份观察脚本、坏 .git 未验证与自包含引用校验。 |
| R03 | core/boundaries：父仓、unborn、detached、linked worktree、损坏 Git；完整 refs 处理同名 tag。 |
| R04 | core/onboarding：无 Git 明确 initialize-git、默认预览、既有规范不覆盖、长期缺失提示、保留人工 Markdown。 |
| R05 | core/storage_layout：shared/local 的 .gitflow/state/、worktree 共用状态锚点且日志隔离。 |
| R06 | core/boundaries：候选漂移、严格布尔/字段/关系、受限正则；锁内候选/激活身份复核。 |
| R07 | audit：长期角色覆盖、来源 OID/角色/修订/祖先结构，损坏和过期记录为未知；服务端保护单列未验证。 |
| R08 | operations：创建/命名/基线、切换 dirty 保护、worktree 占用、重命名、未合入删除、reconcile。 |
| R09 | core/protocols：保护分支日常提交、源目标角色；native 集成绑定 journal/OID/修订；质量 not_evaluated。 |
| R10 | operations/protocols：临时 bare 远端 push/fetch/pull、真实 merge/rebase、非快进强推拒绝、明确定义 ref。 |
| R11 | operations/boundaries/protocols：release 双目标、活跃 release hotfix 回灌、冲突剩余目标、同名 tag；维护传播模型独立。 |
| R12 | operations/boundaries/protocols：保留原引用迁移、dirty 携带、abort/continue、等价补丁幂等、观察式 resume 确认。 |
| R13 | protocols：真实 Hook stdin/out、Git -C/cd、换行/动态/alias/绝对 Git；原生 Hook 实际提交/推送。宿主未安装。 |
| R14 | protocols：PLUGIN_DATA 的 defer 决定持久化，后来 Git 状态变化重新发现。 |
| R15 | protocols：真实 stdio initialize/list/call；闭合参数与非法 bool 无副作用；统一查询结果与退出码。 |
| R16 | operations/boundaries：before/after 日志、运行中阻塞、坏 origins/journal 在 Git 写前拒绝、锁前 refs 改变拒绝。超时保留 unknown 不重放。 |
| R17 | package：90 文件锁摘要、上游对比、篡改拒绝、官方 Schema 与包路径校验。 |
| R18 | 完整69测试通过、9技能结构与引用通过、TRACE4.43–4.46、解包异 cwd CLI/MCP。独立审查发现问题已按复现用例红绿修复。 |

## 实际限制

- Hook协议通过真实subprocess验证，但没有安装到Claude/Codex/ZCode，没有真实宿主事件与UI验证。兼容清单只代表可审阅产物。
- 远端推送使用临时本地bare仓库；托管服务的权限、分支保护、PR策略、CI与生产发布未验证。
- 初始空仓不造提交或长期refs；classic的保护主线首次提交需确认bootstrap候选修订，完成后恢复保护。
- 浅历史、未知来源、远端对象不足、规则漂移返回未知或未验证；本地记录不提供对本机写权限用户的安全隔离。
- squash定义可表达，自动squash提交未实现，执行明确拒绝并要求独立方案；强推/镜像/删除、多ref推送不支持。
- resume不重放命令，仅对可证明的创建/集成/迁移/推送结果确认完成；无法证明的fetch/pull/rebase与损坏历史仍要求明确恢复方案。
- 同一GitFlow锁不约束外部Git；apply前重新绑定所有本地分支OID与规则修订，不能据此宣称不存在外部竞争。

[原始回归输出](evidence/validation-output.txt)；[源与输入指纹](evidence/source-validation.json)。runtime_sha256的范围是scripts/*.py、profiles/*.json和schemas/*.json；tests与技能锁分别摘要，不包含本报告以避免自引用。ZIP身份在独立交付清单中记录。

## v0.1.3 Git 项目触发增量（R19–R21）

本次在 macOS 上执行完整 81 项真实 Git/CLI/MCP/Hook/打包测试通过，新增项目触发测试 12 项。首次目标回归在 10 项用例中出现 27 个行为断言失败：普通目录/bare/缺失 cwd 仍输出、紧凑 -C 未正确解析等；实现后全部转绿；复核另发现 cd 后动态目标沿用旧 cwd 的问题，增加红灯用例并修复，最终共 12 项触发测试通过。原先版本测试写死 0.1.0，与已发布 0.1.2 不一致，已改为运行时和清单版本一致性验证。

- 普通目录：五事件输出 {}；项目和 PLUGIN_DATA 无新增文件，未知/动态命令不被插件执行。
- Git 工作树：空历史、子目录、detached worktree、子模块正确启用；子模块读取自己的 github-flow，未误用父仓 classic-gitflow。
- 命令目标：从普通目录经 git -C / 紧凑 -Cpath / 多次 -C / cd 访问仓库，保护主线提交被拒绝；反向访问无 Git 目录静默。
- 状态变化：先无 Git，初始化后启用；移走 Git 元数据后停用；不缓存活动状态。
- 环境与错误：GIT_DIR/GIT_WORK_TREE 不能将普通目录误判为仓库；损坏元数据返回未验证，未伪造 allow。
- 分发：ZIP 解包后在异 cwd 重放全部无 Git Hook，随后初始化临时项目再次调用 SessionStart；CLI/MCP/原生 Hook 既有回归保持通过。

本次源码、测试及输入指纹与完整输出见 [项目触发证据](evidence/project-activation.json) 和 [完整回归输出](evidence/project-activation-output.txt)。上方 0.1.0 的 69 项报告及 source-validation.json 保留为历史，不能用于证明新源码。新增 .github/workflows/validate.yml 在 Ubuntu/Python 3.11 与 macOS/Python 3.13 执行相同完整回归；实际远端结果绑定发布 commit，可从 Actions 查验。尚未进行真实宿主安装与事件接线验证。

## v0.1.4 跨平台闭环补丁

[v0.1.3 CI](https://github.com/full-stack-plugins/gitflow-plugin/actions/runs/37640761024) 在 macOS/Python 3.13 通过 81 项，Linux/Python 3.11 全量执行 81 项、失败 5 项原生 Hook 测试（commit-msg 参数 -- 未被旧 argparse 解析）。这是真实兼容性失败，不能算 Linux 验证通过。

修复：Hook/native 参数入口使用 parse_intermixed_args，既有真实原生提交/推送/集成测试负责验证；重新执行完整本地 81 项及双平台 CI。当前补丁证据为 [v0.1.4 指纹](evidence/project-activation-v0.1.4.json) 与 [v0.1.4 完整输出](evidence/project-activation-v0.1.4-output.txt)。v0.1.3 的本地指纹保留为历史；公开版本的源码绑定结果由 GitHub Actions 记录。

## v0.1.5：统一 .gitflow/（R23–R25）

当前源码本地完整回归 91/91 通过，新增 10 项真实 Git 存储测试。覆盖 local 状态忽略、linked worktree 共用规则与日志隔离、separate-git-dir、只读不迁移、旧数据及 linked 日志迁移、来源后续写入、冲突/符号链接保留、原生 Hook 重定位与自定义 Hook 保护。九技能 validate/quick_validate 与 TRACE 完成，快照 90 文件通过；源码与日志摘要见 `docs/evidence/storage-layout-v0.1.5.json`。

最初目标测试有 6 项行为红灯及 1 项测试 CLI 参数错误；参数修正后进入实现。第一次完整回归另暴露 2 项测试夹具目录未创建和 1 项消息断言不匹配，均修正后完整重跑。已有 Python 环境缺少 PyYAML，quick_validate 改用已安装的 Anaconda Python 3.13 执行，未安装依赖。远端 CI 以实际发布 commit 查询；CLI/MCP/Hook 回放不代表实际宿主安装验收。
