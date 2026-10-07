# 项目规则、授权与证据契约

## 规则事实源

先读项目 AGENTS.md/CLAUDE.md/CONTRIBUTING、发布文档与已有 Git 约定。规范不得由远端默认分支或名字推断。共享模式 `.gitflow/workflow.json` 是定义；生成的 workflow.md 只是说明。插件在 `git rev-parse --path-format=absolute --git-common-dir` 对应目录的 gitflow/activation.json 保存已确认快照。候选修订须预览并显式激活，编辑候选不会立即放宽门禁。local 模式只在 Git 元数据中保存规范，不随 clone 分发。

没有安装插件时依本文步骤读取、解释并人工逐条核验；不要声称插件门禁或已激活快照存在。仅有文档允许提出候选规则，不自动授权初始化、创建/切换分支、合并、提交、推送、清理或发布。用户已有明确授权持续有效；新的影响需明确范围。

## 独立可执行发现

本技能包含只读脚本 inspect_repository.py，无第三方依赖。在支持技能挂载的环境执行：

```bash
python3 /mnt/skills/user/git-audit/scripts/inspect_repository.py /absolute/project
```

其他安装方式应以当前技能实际目录定位脚本，不虚构上述挂载存在。也可直接查询：

```bash
git -C /absolute/project rev-parse --show-toplevel
git -C /absolute/project rev-parse --absolute-git-dir
git -C /absolute/project rev-parse --path-format=absolute --git-common-dir
git -C /absolute/project symbolic-ref --quiet --short HEAD
git -C /absolute/project status --porcelain=v1
git -C /absolute/project for-each-ref --format='%(refname:short)' refs/heads
```

路径是参数，不拼接 shell 字符串；实际命令必须使用用户项目绝对路径。脚本不 fetch、不建立索引、不写配置、不初始化、不提交。Git 命令不存在、权限失败、损坏元数据、bare 仓库或超时返回未验证，不能当空项目。

## 判定与失败

允许（allow）表示本动作分支规则通过；deny 表示明确违反；unverified 表示缺少身份、历史、授权范围或可信规则。未知不会自动降为成功。CodeGuard 质量验收是另一项独立检查。

真实仓库根可在当前目录之上；linked worktree 的 `.git` 为文件。不能在子目录重复 init。空历史无法预先创建多个有效分支；先确认初始提交，再补长期角色。临时 feature/release/hotfix 不要求总是存在。merge-base 不证明分支创建来源；没有 provenance 应报告未知。远端跟踪不等于实时远端，浅历史不能证明完整合入。服务端保护须独立核实。

任何写动作先输出具体计划：仓库、当前 branch/HEAD、来源/目标 refs、规则修订、保留修改方式、预计命令及验收。执行后重新读取 refs/HEAD/status；出现冲突留在实际中断现场，不虚称原分支已恢复，不自动 reset --hard、强推、stash drop。副作用超时可能已发生，先观察再恢复，不重复 cherry-pick 或发布。

## 插件可用时

从当前插件实际目录调用 `python3 <plugin-root>/scripts/gitflow.py <command> <project> --json`；默认预览，受管写操作显式 `--apply`。插件位置需由宿主或用户提供，本技能不依赖插件安装。

退出码：0 本动作允许/预览/完成；1 违规；2 用法错误；3 未验证；4 内部错误。不要将预览或退出码 0 扩大为整体 Git 规范、CI、部署或生产验收。
