# 阅读入口与目录维护

首页是全书目录，正文按篇放在 `juan/`；GitHub 可以直接阅读 Markdown。当前为五章二十三则，另有自志与众娘考源附录。

- [全书目录](../README.md#目录)：封面、序与章节入口。
- [考源材料簿](../juan/kaoyuan.md)：11 个模型家族、23 条材料；8 张有逐项许可记录的本地图，其余只留出处。
- [志异离线页](zhiyi.html)：类别筛选与夜间配色。
- [考源离线页](ai-girls.html)：按家族、题名或署名筛选。
- [早期档案说明](../docs/ARCHIVE_README.md)：原研究档案仍独立保留。

GitHub 的 HTML 文件页显示源码；离线阅读请下载仓库，再用浏览器打开相应 HTML。考源图片使用相对路径，需连同 `data/ai-girls/media/` 一起保留。

## 修改哪一份

| 内容 | 编辑入口 | 生成结果 |
| --- | --- | --- |
| 志异篇目、顺序、正文、来源、考据状态 | `data/zhiyi.json` | `README.md`、`juan/z-*.md`、`juan/zizhi.md`、`prototype/zhiyi.html` |
| 志异网页布局 | `templates/zhiyi.html` | `prototype/zhiyi.html` |
| AI 娘形象材料与许可 | `data/ai-girls/collection.json` | `juan/kaoyuan.md`、`prototype/ai-girls.html` |
| 封面与印章 | `assets/` | 首页与分卷页引用 |
| 早期研究案例 | `data/cases/` 等 | `docs/cases/`、目录与 `site/index.html` |

不要直接修改生成后的首页或分卷。实质更正保留日期与修订说明；旧 ID 和分卷文件名保持稳定。

## 生成与核对

在仓库根目录执行：

```text
python scripts/build_ai_girls.py
node scripts/zhiyi_pages.mjs
python scripts/archive.py build
python scripts/build_ai_girls.py --check
node scripts/zhiyi_pages.mjs --check
python scripts/archive.py check
```

三套检查各自覆盖自己的生成结果；它们不证明正文所述历史与出处已经全部考实。本轮的目录整理沿用原正文的来源记录，没有把二次转述或评论提升成已核事实。

## 图片与考源边界

考源附录逐项保留来源、署名、许可声明与未核事项，图库投稿日期不能充当形象诞生日期。图片许可与形象起源分别核对。

`Z-006` 的网传配图作者、首发与许可尚未核实，不属于新收集的 8 张许可素材。维护者决定公开时保留此图，页面注明出处不明；权利人可按 `TAKEDOWN.md` 所述渠道要求署名或撤下。
