# 亚马逊运营技能库

给 AI 助手使用的亚马逊运营工具箱：分析评论、编写 Listing、整理变体、策划和生成图片，以及查询赛狐 ERP 数据。

采用 **英文目录名 + 中文功能名称**。日常使用时直接用中文描述需求即可。

## 1. 有哪些功能

| 中文名称 | 英文目录名 | 能做什么 |
| --- | --- | --- |
| 技能导航 | [amazon-skill-router](amazon-skill-router/) | 根据你的需求选择合适的技能 |
| 评论分析 | [amazon-review-analysis](skills/amazon-review-analysis/) | 分析买家评论，统计产品优缺点、出现频次和改进建议 |
| Listing 全流程 | [amazon-listing-workflow](skills/amazon-listing-workflow/) | 整理资料、分析竞品和关键词，生成标题、五点、长描述、QA、后台搜索词（ST），检查文案并衔接图片策划 |
| 变体规划 | [amazon-variant-planning](skills/amazon-variant-planning/) | 整理父体和 MSKU 的颜色、尺寸等属性，检查重复与冲突，将文案绑定到对应变体 |
| 九图策划 | [amazon-image-planning](skills/amazon-image-planning/) | 规划九张产品图的内容、构图、素材和中英上图文案，交付独立 HTML 方案 |
| 图片生成（可选） | [amazon-image-generation](skills/amazon-image-generation/) | 根据产品资料和图片方案，按需生成 Listing 图片或 A+ 图片 |
| 赛狐 ERP 调用 | [sellfox-mcp-query](skills/sellfox-mcp-query/) | 通过 Sellfox-MCP 查询销售、毛利润、订单、MSKU、广告、库存等数据，按需精简返回结果 |

完整 Listing 流程：

**产品资料 → 变体整理 → 竞品与关键词分析 → 文案生成与检查 → 九图策划 → 图片生成（按需）**

每项功能都可以单独调用。完整 Listing 默认包含九图文字方案；图片生成放在最后，明确要求时才执行，需要当前环境提供图像生成工具。

## 2. 目录结构

```text
weicanming-Amazion-skill-box/
├── README.md                     # 使用说明书
├── skills-manifest.json          # 技能清单：名称、路径、用途和触发词
├── amazon-skill-router/          # 技能导航入口
│   ├── SKILL.md
│   └── references/skill-catalog.md  # 根据技能清单自动生成的导航索引
├── skills/                      # 六个业务技能
│   ├── amazon-review-analysis/   # 评论分析
│   ├── amazon-listing-workflow/  # Listing 全流程
│   ├── amazon-variant-planning/  # 变体规划
│   ├── amazon-image-planning/    # 九图策划
│   ├── amazon-image-generation/  # 图片生成（可选）
│   └── sellfox-mcp-query/        # 赛狐 ERP 调用
├── scripts/                     # 技能同步、导航索引生成工具
└── tests/                       # 清单与同步工具的测试
```

每个技能以 `SKILL.md` 为使用规则入口，按需要配有：

- `references/`：详细规则和参考资料。
- `scripts/`：辅助处理和检查脚本。
- `assets/`：模板等素材。
- `agents/`：助手展示配置。

## 3. 怎么调用

安装后，在支持技能的 AI 助手中直接提出需求，并提供相关资料：

| 想做的事 | 可以这样说 | 建议提供 |
| --- | --- | --- |
| 分析评论 | “分析这些亚马逊评论，找出主要优缺点” | 评论表或文件，包含 ASIN、评论标题和正文 |
| 编写 Listing | “根据这些资料生成美国站 Listing” | 产品信息、目标站点、关键词、竞品资料和禁用词 |
| 整理变体 | “整理这份变体表，检查 MSKU 冲突” | 父体 SKU、MSKU、属性及规格表 |
| 策划图片 | “为这个产品做九图策划” | 产品事实、现有文案、产品图及变体资料 |
| 生成图片 | “按方案生成第 1 张产品图”或“生成普通 A+ 图片” | 产品参考图、图片方案及尺寸要求 |
| 查询利润 | “按发货口径统计本月美国和加拿大店铺的毛利润” | 已连接的 Sellfox-MCP，以及日期、店铺、币种和统计口径 |

也可以指定英文技能名，例如：“调用 `amazon-image-planning`”。资料不全时，助手会说明缺少什么。

**评论分析约定：** 按 ASIN 分别统计，分析结论和改进建议均以评论证据为依据；没有评分时不推断星级分布。也可以只要求生成一份可复用的评论分析提示词。

**内置敏感词库：** Listing 技能执行时默认读取随技能安装的 `敏感词-词库.xlsx`，合并你补充的禁用词，用于生成时避用和交付前检查，无需重复上传。

**交付方式：** Listing 文案默认以目标语言原文和中文翻译的 HTML 文件交付；九图策划另存为独立 HTML 文件。

**赛狐查询约定：** 本仓库已配置当前账号的美国和加拿大店铺；换账号使用时需修改技能中的店铺 ID。USD 与 CAD 分开统计；区分发货口径和结算口径；报表毛利润不等于净利润。查询依赖 Sellfox-MCP 的连接、权限和实际接口能力。

## 4. 安装与更新

将仓库下载或克隆到本地后，在仓库目录运行以下命令（需要 Python 3）：

```bash
python scripts/sync_skills.py --source auto
```

默认安装到用户目录下的 `~/.codex/skills/`，包含技能导航和清单中的六个业务技能。同名技能已存在时会跳过。

`--source auto` 每次运行都会检查 GitHub 指定分支（默认 `main`）的最新技能内容，并从远程版本同步；不会修改本地仓库或同步脚本自身。连接失败时会明确提示，再使用本地文件，不会声称已更新到最新版。

更新已安装的技能时运行（同名技能会先备份再替换）：

```bash
python scripts/sync_skills.py --source auto --force
```

`--force` 会先备份同名技能，再替换为仓库版本。备份保存在安装目录下的 `.skill-backups/`。

只使用本地文件可加 `--source local`；要求必须从 GitHub 获取可用 `--source remote`（连接失败则停止）。这些检查只在运行命令时发生，不会后台定时执行。

要更新本地仓库及同步脚本自身，请在仓库目录执行 `git pull`。

## 5. 如何维护技能库

1. 新技能放入 `skills/<英文技能名>/`，至少包含 `SKILL.md`。
2. 在 `skills-manifest.json` 登记或更新技能信息。
3. 生成导航索引并检查：

```bash
python scripts/render_skill_catalog.py --write
python scripts/render_skill_catalog.py --check
python -m unittest discover -s tests
```

英文目录名保持稳定，中文名称用于说明用途。导航索引由脚本生成，不要手动修改。
