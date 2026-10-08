# GitFlow 0.2.0 发行验收

实现规格：add-policy-rules-and-ci-governance。本地验收与输入指纹见 [治理证据](evidence/governance-v0.2.0.json)，操作指南见 [治理指南](governance.md)。

本地完成：124/124 测试；九技能校验与90文件快照；清单Schema；OpenSpec严格校验。git-skills源提交 f3ef639aba4c499e4a69ff47e24dd816bd431600。v1定义与 .gitflow/state 布局兼容。

发行身份通过 v0.2.0 标签及同名 GitHub Release 确定；ZIP 和 delivery JSON 为固定附件。归档只表示实现规格闭环，发行完成须另外核对：插件与技能远端提交、标签指向、附件摘要、市场 GitFlow 条目与精确提交 CI。避免把旧报告用于新源码。

CI 检查地址：[插件 Actions](https://github.com/full-stack-plugins/gitflow-plugin/actions/workflows/validate.yml)、[市场 Actions](https://github.com/partme-ai/full-stack-plugins/actions/workflows/validate-marketplace.yml)。最终状态以对应 release commit / marketplace commit 的运行结果为准，不以配置文件存在代替运行。

市场只发布GitFlow条目，保留本地CodeGuard未提交修改。未安装或更新实际宿主插件；市场刷新与宿主更新提示尚需用户安装状态配合。真实业务 PR、MCP宿主、服务端保护、AI代码来源检测和密码学签名验证不在本次验收内。
