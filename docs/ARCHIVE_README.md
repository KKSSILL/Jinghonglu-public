> 这是《惊鸿录》早期“人机相处档案”的说明，2026-10-12 从仓库首页挪到此处保存。现在的首页是志异版，见 [README](../README.md)。

# 《惊鸿录》· 人机相处档案

**记录人与人工智能相遇、合作、误解和告别的历史。**

> We preserve the record. The future can judge.
> 我们保存记录，留给未来判断。

这里保存可追溯的材料，也保留后来改变看法的空间。一次令人发笑的回应、一次协作摩擦、一场模型更新引起的争论，都可能值得留下。收录一则材料，不代表认可其中的判断。

## 从这里开始

- **新版阅读样稿**：[志异之体 · 二十三则](../prototype/zhiyi.html)，独立的单栏阅读与夜间配色试稿；当前范围见[样稿说明](../prototype/README.md)。下载到本地后用浏览器打开。
- **直接浏览**：双击 [site/index.html](../site/index.html)，离线可用，无须安装、登录或启动服务器。
- **阅读目录**：[案例总览](../docs/CATALOG.md) · [双时间线](../docs/TIMELINE.md)。
- **了解方法**：[档案结构](../docs/DATA_MODEL.md) · [伦理前言](../ETHICS.md)。
- **交给 Dot**：[馆员接手说明](../docs/DOT_HANDOFF.md)。此仓库没有启用后台采集或定时任务。

代码保存于 [KKSSILL/jinghonglu-public](https://github.com/KKSSILL/jinghonglu-public)。HTML 尚未部署为在线网站；GitHub 文件页显示源码，下载后才能直接阅读。

v0.1 是一批历史精选，覆盖 1966—2025 年，采集核对日期为 2026-10-10。它不是截至今日的完整模型史，也不是排行榜。首批以可读原始论文、厂商原文和少量公开用户自述起步；长期协作、告别、中文社区与非主流产品的材料仍很不足。

## 一份材料，多条阅读路径

**Point 负责身份，Timeline 负责来路，Case 负责证据，Collection / Lens 负责观察。**

- **模型节点**：有公开依据的模型版本、研究变体或产品配置阶段。节点说明区分这三者，不猜测未知权重或快照。
- **官方时间线**：发布、配置改变、公告与回滚。
- **观察时间线**：用户报告、研究发表、后续解释。发表日期不冒充互动发生日期。
- **案例**：原始来源、可观察事实、馆员解释和不能推出的结论分别保存。
- **视角 / 专题**：灵光、摩擦、关系、变迁、对待、事件。同一案例可以进入多个视角，不复制材料。

“最近感觉变了”可以登记为待核实的变化候选，不据此发明一个模型版本。节点、案例与来源都有稳定 ID；后续认识追加记录，隐私撤除则优先保护当事人。

这个项目借鉴材料与解释分离、观察不改写历史的研究方法，采用普通 Git 与 JSON。当前没有接入 Universe Core，也不把模型档案节点当作 Subject、人格、意识或道德地位的证明。

## 整理与构建

需要 Python 3.10+，不需要第三方库。

```powershell
python scripts/archive.py validate
python scripts/archive.py build
python scripts/archive.py check
```

编辑 `data/`；`docs/cases/`、两份目录与 `site/index.html` 是生成的阅读副本，不直接编辑。`check` 会检查生成物是否与数据一致。打开页面不会联网、采集、写档案或调用模型。

```text
data/                    权威记录：来源、节点、案例、时间线、专题
docs/cases/              可在 Git 中阅读的生成案例页
site/index.html          可直接打开的离线阅读页
prototype/zhiyi.html     独立的志异阅读样稿，尚未接入正式数据
web/                     阅读页模板、样式和交互
scripts/archive.py       校验与生成工具
templates/case.json       新案例样板
```

## 投稿、权利和纠错

[CONTRIBUTING.md](../CONTRIBUTING.md) · [SOURCE_POLICY.md](../SOURCE_POLICY.md) · [PRIVACY.md](../PRIVACY.md) · [TAKEDOWN.md](../TAKEDOWN.md) · [LICENSE.md](../LICENSE.md)

默认只留原链接、必要署名、原创简述和少量必要引文；不批量搬运聊天截图或第三方全文。本地初版尚未发布；公开前必须配置可用的私密撤除联系方式，见 `data/archive.json` 的 `publication`。
