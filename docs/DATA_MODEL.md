# 小而清楚的数据结构

`data/` 是唯一编辑入口；其余目录页和网站由它生成。所有 ID 都由馆员分配，不能根据标题变化重新编号。当前 schema_version = 1，暂不引入数据库、Core、身份晋升或自动推理服务。

## 志异阅读版与考源材料（2026-10-12）

现有五章二十三则独立保存在 `data/zhiyi.json`，保留原 ID、来源、考据状态和章内顺序。`scripts/zhiyi_pages.mjs` 统一生成首页目录、`juan/` 分卷正文和 `prototype/zhiyi.html`；页面外观在 `templates/zhiyi.html`。它们没有自动晋升为下表的研究案例。

`data/ai-girls/collection.json` 保存图像及出处线索，`media/` 保留逐项有许可记录的素材；`scripts/build_ai_girls.py` 生成 `juan/kaoyuan.md` 与离线材料页。作品作者、投稿者、角色最初设计者和不同日期不可混同。材料已编目不表示起源已考实。

两套阅读生成器各有 `--check`，原 `archive.py check` 只覆盖早期研究档案。完整命令见 `prototype/README.md`。

| 文件 | 含义 | 不代表什么 |
| --- | --- | --- |
| archive.json | 名称、模型家族、观察视角、专题、发布配置 | 完整模型名录 |
| sources.json | 谁在哪里公开了材料；何时读到；能读多少 | 原网页的永久镜像或不可变原件 |
| points.json | 有公开锚定的版本、变体或产品阶段 | 主体出生、人格连续、权重必然更换 |
| cases/*.json | 一份案例，包含证据、解释、边界、修订 | 独立认证或群体代表性 |
| timeline.json | official / observed 两轨的带来源事件 | 因果关系、互动的精确发生时刻 |
| transitions.json | 尚无公开版本依据的变化候选 | 已确认的新 Point |
| leads.json | 未充分读取或还需核实的线索 | 已接收入主库的事实 |

## Point

`kind` 为 documented-system、model-release、research-variant、product-configuration。`anchor_date` 是所引用公开锚点的日期；`anchor_kind` 明确它是论文发表、发布还是配置公告。`model_version` 可以是 null；`certainty` 不因归档自动提升。

`related_points` 中的关系必须具名。例如研究变体可以标为 `research-variant-of`，公开时间顺序只能是 `public-sequence`。不能仅因名称、材料或行为相似而声称技术继承。

## Case 的三层

1. `evidence[]`：`claim` + `attribution` + `source_ids` + `locator`。明确“厂商称”“作者报告”“研究者发现”。
2. 编目：标题、模型与关联 Point、多个 lenses、材料类型、来源日期、实际发生日期、完整性。
3. `interpretation`：馆员署名的研究问题与留存理由；`limits[]` 明确不支持的推论。

`occurred_on` 为 null 很正常。`date` 用于目录，必须有 `date_basis` 解释依据。支持 YYYY、YYYY-MM、YYYY-MM-DD，不自动补零日；精度不同的日期只用于粗排序，不能推导同日或先后因果。

`point_ids: []` 表示目前没有可核实的具体阶段归属。不要把跨版本研究硬绑到某个发布时间。`model.certainty` 区分 official-family、research-reported、user-reported、unknown；`model.version` 允许 null。

## 修订、撤回与快照

每个案例有 `revisions[]`，包含记录时间、作者、变更内容、依据。实质修订需保留先前主张和新判断的差别；错误文本可以更正，但不能让历史看起来从未提出过。

Git 提交保存本仓库版本，**不能冻结外部网页**。当前只保存链接和简述，未取得转载许可时不追求全文不可变快照。未来有许可的材料可附哈希和许可证明，另行设计保存路径。

隐私和合法撤除优先于保留历史；不保证第三方副本可删除。馆员无权自行强推历史。

## 与创世纪研究思路的距离

这里只采用材料、解释、可替换阅读视图分离的方法。网站是派生的 Eye，阅读、筛选和切换专题均不会修改源记录。这里的 Point 是档案词汇，不是 Universe 的 Subject Outer Point；不借用那个项目的私有源码、数据或身份合同。
