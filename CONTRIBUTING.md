# 一次贡献怎样完成

## 给志异投稿

见到人与 AI 相处的趣事、梗图或轶事，最简单的办法是开一个 Issue，选“投稿”模板，写清发生了什么、原始出处和大约时间即可，不必自己写成志异体。收录与否、放进哪一篇、评语怎么写，由维护者定。

想直接改的，条目都在 `data/zhiyi.json`，改完运行 `node scripts/zhiyi_pages.mjs` 重新生成首页、`juan/` 与 `prototype/zhiyi.html`，再运行 `node scripts/zhiyi_pages.mjs --check`。生成出来的文件不要手改。

## 研究档案的贡献

1. 搜索现有标题、URL、模型和案例 ID，判断是新事件还是旧事件的补充。
2. 阅读原始来源，记录公开性、上下文与版本确定性。无法核实的资料先写入 `data/leads.json`。
3. 参照 `templates/case.json`，在 `data/cases/` 建案例。将可观察事实、归因和馆员解释分开；逐项写来源与定位。
4. 必要时添加公开锚定的 Point 和时间线事件。主观变化报告使用 `data/transitions.json`，不虚构版本。
5. 对实质修订追加 `revisions`，写明何时、为何、依据哪个来源；撤除按专门流程处理。
6. 运行 `python scripts/archive.py build` 和 `python scripts/archive.py check`，检查生成的案例页与离线阅读页。

提交说明用两三句话说明新增或纠正了什么，以及哪些仍不确定。一次整理一批相关材料即可，不要求凑足条数或遍历全网。

贡献原创文字与代码时须有权按 LICENSE.md 的对应许可提供；第三方材料不会因投稿而转为本仓库的许可。AI 辅助整理须由提交者核查，并保留来源，不署名为原文作者。
