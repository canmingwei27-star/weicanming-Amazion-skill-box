# 运行与数据约定 v3

用于单一总入口、包内文案规则及变体/图片策划配套技能间的交接，不沿用旧版十点文案数据契约。

## 项目与状态

使用用户指定项目目录；未指定时，在当前工作区 `work/amazon-listing/<project-id>/` 保存 state.json、标准化资料、分析结果、draft.json 和检查记录。project-id 用安全的名称，不得包含路径穿越或绝对路径。用户可交付内容保存到当前工作区outputs下，以产品/版本区分；默认交付HTML，含目标语言原文及中文翻译，详见 [HTML与中文翻译规则](html-delivery.md)。内部JSON保留用于溯源和续接。

项目至少记录：schema_version、project_id、product_id、sku/variant、marketplace、category、language、brand、mode、requested_outputs、input_sources、confirmed_facts、pending_questions、stages、all_requested_complete。未知信息为 null，不从旧项目静默继承产品事实。

每阶段记录 status、input_versions、module_path、module_version（文件哈希可用时）、output_paths、output_kind（plan/draft/final/analysis）、assumptions、issues、updated_at。状态定义：

- pending：尚未执行，依赖尚未齐备。
- ready：可执行。
- done：该阶段在所记录输入版本及输出类型下完成；不代表整套项目完成。
- needs_input：缺事实、确认、文件或适用规则，记录具体问题。
- needs_skill：需要的模块未接入或文件不可用。
- stale：依赖发生变化，旧结果仅作参考，需复核。
- not_requested：当前交付范围未要求该项。

某阶段可同时保存已完成的部分文件与 needs_input 状态。输入不齐但可做部分分析时推进可执行部分，不能将其标为完整 done。

状态保存由执行当前工作流的助手完成，不假设存在后台调度器。只有确实写出并核对文件后才记录对应产物已保存。

## 输入交接

沿用资料接收结果的 project、sources、keywords、roots、competitors、brand_rules、forbidden_terms、product_data/facts、issues/readiness。所有事实、关键词和结论保留 ID 和来源。

竞品结论保留 competitor_ids、source_refs、evidence、observation、inference、fact_ids、adoption_status、reason 与目标字段；关键词规划保留原词/标签/指标、采用状态、目标字段及排除原因。

确认记录至少含 confirmation_id、用户确认内容、关联事实或问题、适用变体、确认来源/时间和状态。用户修订事实或否定确认时更新记录并使相关输出过期；不把“未回复”视为确认。

## draft.json 与计数工具适配

只保存实际生成的文本，不把说明、外部编号、分析或占位文字混入。尚未生成的分区省略，并在 state.json 明确缺失。

```json
{
  "title": {
    "main": "实际主标题",
    "subtitle": "实际副标题",
    "subtitle_field": "item_highlights",
    "platform_main_limit": null,
    "platform_subtitle_limit": null,
    "prefix": {"brand": "已确认品牌", "quantity": "已确认数量及单位", "total_length": "已确认总长度及单位", "color": "已确认颜色"},
    "core_keyword": "取自关键词库的精准短语",
    "roots": []
  },
  "bullet_outline": [
    {"point_id": 1, "topic_id": "specifications", "focus": "包装和规格", "buyer_question": "包含什么规格", "claim_ids": ["package_and_dimensions"], "fact_ids": ["本品事实ID"], "root_ids": ["实际词根ID"], "competitor_refs": [], "embedding_plan": [], "exclude_topics": ["其他点的主题"]}
  ],
  "bullets": [
    {"point_id": 1, "topic_id": "specifications", "claim_ids": ["package_and_dimensions"], "text": "整点实际展示文本", "body": "正文实际文本", "fact_ids": [], "root_ids": []}
  ],
  "description": {"text": "实际长描述", "fact_ids": [], "root_ids": []},
  "qas_delivery_mode": "review_candidates",
  "qas": [
    {"question": "实际问题", "answer": "实际拟写答案", "evidence_status": "unconfirmed", "review_note": "需人工核实的假设", "fact_ids": [], "source_refs": ["实际关键词或竞品来源ID"], "gap": "拟解决的购买疑问", "overlap": []}
  ]
}
```

副标题附subtitle_root_plan，按顺序保存raw、root_id、relevance、source、fact_ids或适配说明及排列理由；实际副标题按词根堆积，111–124字符含空格，单空格连接，禁止标点符号。不再要求subtitle_phrase_plan及中心名词/修饰关系；旧字段仅作历史记录。

QA默认qas_delivery_mode=review_candidates，固定10条完整Q/A，状态为confirmed/inferred/unconfirmed。所有条目有source_refs；confirmed有fact_ids，其他条目有非空review_note且交付时逐条显示标签。QA候选齐备即生成done，人工审核另记pending_user_review；不得将旧版事实不足当数量缺口。verified模式只接受confirmed且有依据的答案。候选假设不迁入其他发布字段。

示例数组只表示结构；完整成稿的 bullets 为5项，qas 为10项。标题字段映射由标题模块确定，未确认时 subtitle_field 为 null，不能默认所有站点支持 Item Highlights。

`platform_main_limit`、`platform_subtitle_limit` 只有在核实本项目适用要求后填入数值；null 会让计数工具报告对应平台限制未验证。`roots` 必须从实际词根表传入完整有效目录的非空原词，用于重复与库外词检查；不得从生成标题反向提取，不添加库外词使检查通过。prefix四字段只放用户已确认的品牌、数量、总长度、颜色，不夹带形态或性能；core_keyword必须紧随固定前缀，并保留原关键词ID、原等级与来源于evidence.json。所有主副标题词根附root_id、源工作表及行号；前缀附fact_id。计数工具新增检查固定顺序与库外词，缺目录/前缀/核心词时不能视为标题通过。主标题少于75时附capacity_reason，说明完整词根无法继续填充的原因。

bullet_outline必须在五点成稿之前保存，完整提纲为按point_id 1–5排列的五项；每点focus、buyer_question、topic_id、claim_ids、fact_ids、root_ids必填。topic_id按主题含义归一化，不用point_1等位置编号假装独立主题；珠径、尺寸选择、卷长、包装数量同属specifications。claim_ids标识主要主张，一个主要主张只归一个点；支持事实可交叉引用。每点competitor_refs保留原点序号与片段，embedding_plan记录原词/ID/属性/计划语境，场景词明确分配位置。没有竞品时列表可空并记录原因，不能造来源。生成的每条bullet须匹配对应point_id、topic_id、claim_ids；来源记录与正文分离。

没有内部小标题时 text=body；有小标题时 text 含小标题与分隔符并以完整 body 结尾。五点计数包含 text 全文，不含外部序号；结尾标点针对 body。

主标题/副标题、长描述的事实映射可置于独立 evidence.json，按字段路径对应，不重复污染纯文本。计数工具可以读取 draft.json 中它支持的 title、bullets、qas，其他字段不表示已被检查。只有长描述的单项任务不要调用不支持该分区的计数工具，应单独计算和核对。

生成 ST 后在 draft.json 中新增 `st` 对象：text（实际纯文本）、root_ids（按输出顺序且去重）、character_count、target_characters=240、max_characters=250、rule_source=user_instruction、listing_version、dedup_scope、dedup_complete、exclusions。另记录input_snapshot（本次实际使用字段及版本或哈希）、missing_fields（执行时未提供字段）及generation_status。规划结果另存 st_plan，不冒充 text 成稿。尚未完成时省略 st 正文并记录状态。

ST计数包含实际空格，目标约240字符，硬上限250字符。旧utf8_bytes、platform_bytes与platform_byte_rule仅属历史记录，不再用于本流程生成或验收，不在新交付中显示。初始候选保存绝对精准全量及其逐项处理结果。dedup_scope列明本次快照中实际存在并参与去重的字段；对该快照所有已有字段完成检查后dedup_complete可为true。尚未提供字段单列missing_fields，不把当前范围完成冒充未来或缺失字段已检查。直接输出实际ST后generation_status可记done，不因QA人工筛选待处理设为needs_input；整套项目缺失字段另行记录。全部等级（包括绝对精准）跨当前字段与ST内去重。

check_copy.py 仍只支持 title、bullets、qas；ST 由 ST 模块单独核对。单独生成 ST 时不得用其他字段计数成功冒充 ST 检查。

## 更新与失效

保留原文件及旧稿，不静默覆盖用户资料。依赖变化按实际引用传播：

| 变更 | 至少需复核的结果 |
| --- | --- |
| 本品事实、变体或用户确认 | 相关竞品适配、关键词分配、所有使用该事实的文案、QA 与终检 |
| 关键词/词根及其等级 | 关键词分配、使用相关词的标题/五点/长描述/QA、ST 规划、成稿及覆盖报告 |
| 竞品卖点 | 五点竞品分析、相关关键词规划和五点/长描述，随后 QA 新增信息与终检 |
| 竞品标题 | 标题竞品分析、相关关键词规划和标题，随后描述衔接、QA 与终检 |
| Brands、当前品牌或违规词库 | 使用资格、所有受影响文案与终检；原始竞品统计可保留 |
| 标题、副标题、五点或长描述实际文本 | 下游衔接、QA的gap；本次需更新ST时以新快照生成新版并终检，旧ST保留旧版本依据 |
| QA 实际文本 | 本次需要更新ST时用新QA生成新版并终检；人工筛选待处理不阻止当前ST交付 |
| 平台要求、语言或站点 | 适用规则、排序可比性及受影响文案/计数/终检 |
| 内部模块或用户格式要求 | 使用该规则的阶段及其下游结果 |

有证据证明不受影响的结果可保留，记录原因；不为方便将过期结果继续标记 done。终检造成的修改也遵循依赖传播，但仅标记实际变化影响的下游，避免无变化的循环重跑。

## 终检记录

按字段分别记录机械计数、事实、品牌、违规词、适用平台规则、覆盖、自然度与 QA 新增信息检查的 pass/fail/unverified/not_applicable、证据及问题。某一工具返回成功不等于全部检查通过。

项目范围来自用户当前明确请求及已接受的项目目标。整套项目原目标含 ST 时完成其生成与检查；用户仅要求其他字段时将 ST 记为 not_requested。最终状态明确区分“本次请求已完成”与“原完整 Listing 项目仍有缺口”。

旧项目的 skill_path/skill_version 可保留为历史字段；继续执行时记录当前包内 module_path/module_version，并复核受影响的阶段，不自动视为已完成。

## 变体与图片交接

有变体表时保存variants.json，包含列位置表头、raw_rows、唯一variants、families及真实combinations、issues、corrections、duplicate_groups和summary。参照[变体数据契约](../../amazon-variant-planning/references/variant-contract.md)。原始行与用户明确更正分开记录；同父体同MSKU仅完全一致时合并。未知商品重量为null，不继承包装重量。

逐变体稿保存drafts/<variant_id>.json，结构沿用draft.json；state中variant_outputs记录variant_id、MSKU、draft_path、evidence_path、input_versions及检查状态。共享稿须明确适用MSKU和事实依据；具体变体稿优先。内部路径使用安全variant_id，不直接把任意MSKU拼作路径。

新增stages.variants、stages.image_plan；不在本次请求范围时记not_requested。image-plan.json引用listing_version、variant_version及事实，逐图记录id1–9、类型、文案依据、构图、素材、目标语言上图文案、中文、适用MSKU、changing_elements、待核实项和检查结果，详见[图片契约](../../amazon-image-planning/references/planning-contract.md)。

outputs分别记录listing_html和image_plan_html两个路径，不能指向同一文件或同一文件锚点。缺失原始照片等素材不冒充制作完成；策划完成与图片制作完成分开记录。all_requested_complete只检查本次请求的阶段；模板本身交付不代表某个商品九图策划已完成。

变体事实、当前文案或确认状态改变时，只将实际引用它们的文案、计数、ST及图片条目标记stale并复核；本次需更新ST时依据新快照直接输出。仅图片排版或翻译改变不触发ST重写。
