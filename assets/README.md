# GitFlow 视觉资产

`logo.png` 用于插件与市场图标：512 × 512 PNG（122,985 字节，约 120.1 KiB），透明背景。保留 Git 橙色菱形的视觉来源，内部以直线主干、平行分支、圆形提交节点和斜向汇合表达 workflow。浅色、深色界面共用同一透明图像。

## 来源与署名

- 原作者：Jason Long。
- 官方来源：[Git Logo Downloads](https://git-scm.com/community/logos)。
- 原图：[Orange logomark PNG](https://git-scm.com/images/logos/downloads/Git-Icon-1788C.png)，包内副本为 `reference/git-official.png`。
- 原图许可：[Creative Commons Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/)。本包的原图与衍生 `logo.png` 同样采用 CC BY 3.0，保留本署名及修改说明。仓库代码的 Apache-2.0 不覆盖这两个图像文件。
- 修改者：Full Stack Plugins；2026-10-07，以内置 image_gen 基于官方原图二次创作，改变节点数量、连线、颜色反差和内部分支结构。未使用生成 CLI fallback。新版图像按用户要求通过 macOS sips 等比导出为 512 × 512，并以 ImageMagick 去除元数据及无损优化 PNG；优化前后 RGBA 像素完全一致。
- Git 和 Git logo 是 Software Freedom Conservancy 的商标；参见 [Git 商标政策](https://git-scm.com/about/trademark)。本图用于独立 GitFlow 插件，不代表 Git 项目官方产品或背书。

## 新版生成与导出

设计经用户确认采用：图一作为视觉基础，Git 提交图截图作为直线分支与汇合布局参考；使用内置 image_gen，`transparent_background=true`。生成母版为 1254 × 1254；本包分发 512 × 512 图标，保持原图纵横比与透明背景。CodeReview/Stitch 当前同样采用 512 × 512；市场其他插件尺寸并非完全统一。

```text
Use case: logo-brand. Asset type: GitFlow plugin marketplace icon, a refined edit of Image 1. Input images: Image 1 is the existing orange-diamond logo to improve; Image 2 is a Git history graph reference for the branch geometry only, not its colors, text, or background. Primary request: retain Image 1's recognizable Git orange diamond and white circular commit nodes, but replace the curved branch entirely with an angular Git commit graph that clearly forks, runs in a parallel branch lane, and merges back into the mainline. Refer to Gitflow/Gitflow+ workflow concepts: feature or hotfix diverges from a base, advances independently, then reintegrates into the mainline. Geometry: a dominant vertical mainline slightly left of center with three white circular nodes; a secondary straight vertical lane on the right with two smaller white circular nodes; connect the upper mainline node to the upper secondary lane with a straight 45-degree diagonal, and connect the lower secondary lane back to the lower mainline node with another straight 45-degree diagonal. The secondary lane must have enough vertical length to clearly look like an independent branch, rather than a triangle or a letter. All connecting strokes must be perfectly straight horizontal, vertical, or 45-degree diagonal segments with crisp angular joins. Absolutely no curved connector, no arc, no bezier, no swoosh, no rounded bends. Keep only the commit nodes circular and the outer diamond corners gently rounded. Preserve the upper-left diagonal mainline entry motif of Image 1 where it fits cleanly. Style: professionally precise flat vector-like mark, uniform solid Git orange #F05032 and pure white, crisp edges, balanced consistent stroke width and negative space, optically centered. Improve cleanliness: remove grain, gradients and stray edge pixels. One single isolated square icon with comfortable transparent margin, readable at 32px. Actual transparent alpha background, not black or checkerboard. No lettering, UI screenshot, labels, arrows, shadows, 3D effects, gradients, extra decorative elements or border. Preserve the overall visual identity of Image 1; change the internal graph to express straight-line branching and return merging as in Image 2.
```
