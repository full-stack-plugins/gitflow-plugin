# GitFlow 视觉资产

`logo.png` 用于插件与市场图标：1254 × 1254 PNG，透明背景。保留 Git 橙色菱形的视觉来源，内部以纵向主线、圆形提交节点和分支汇合环表达 workflow。浅色、深色界面共用同一透明图像。

## 来源与署名

- 原作者：Jason Long。
- 官方来源：[Git Logo Downloads](https://git-scm.com/community/logos)。
- 原图：[Orange logomark PNG](https://git-scm.com/images/logos/downloads/Git-Icon-1788C.png)，包内副本为 `reference/git-official.png`。
- 原图许可：[Creative Commons Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/)。本包的原图与衍生 `logo.png` 同样采用 CC BY 3.0，保留本署名及修改说明。仓库代码的 Apache-2.0 不覆盖这两个图像文件。
- 修改者：Full Stack Plugins；2026-10-07，以内置 image_gen 基于官方原图二次创作，改变节点数量、连线、颜色反差和内部分支结构。未使用 CLI fallback，未进行程序化图像重绘。
- Git 和 Git logo 是 Software Freedom Conservancy 的商标；参见 [Git 商标政策](https://git-scm.com/about/trademark)。本图用于独立 GitFlow 插件，不代表 Git 项目官方产品或背书。

## 生成提示

输入：官方橙色 Git logomark；设置：`transparent_background=true`。

```text
Use case: logo-brand. Asset type: square marketplace icon for the independent GitFlow workflow plugin. Create a polished derivative of the supplied official Git logomark. Preserve the recognizable Git orange rounded diamond silhouette and flat geometric design language, but redesign its inner branch structure to convey a controlled workflow: a strong mainline with circular commit nodes, one clean branch splitting off and smoothly merging back, and a subtle continuous return path suggesting release backport. This must be a coherent simple connected graph, not decorative disconnected shapes. Orange #F05032 diamond, crisp white internal paths and round nodes. The original open upper-left entry may be reinterpreted as an intentional mainline entry. One centered icon, square canvas with ample transparent padding, large simple forms legible at 32px. Actual transparent alpha background. No letters, no wordmark, no arrows outside the icon, no shadow, no gradients, no glow, no mockup, no border, no extra symbols. Feel orderly, directional, and fluid. Use the reference as brand ancestry while making this a distinct workflow plugin mark.
```
