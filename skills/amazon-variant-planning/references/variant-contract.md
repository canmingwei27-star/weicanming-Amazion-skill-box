# 字段与数据契约

## 输入示例列及含义

| 原始列 | 规范字段 | 解释 |
|---|---|---|
| 品牌 | brand | 本品品牌，不从SKU猜测 |
| 分类 | category_label | 用户分类，不视为Amazon精确类目节点 |
| 父体SKU | parent_sku | 家族分组标识，原样保留 |
| MSKU | msku | 子体标识，保留大小写及原始值 |
| 属性 | attribute_label_raw | 辅助展示/核对，不当作固定颜色轴 |
| 属性1、属性2… | attributes[].value_raw | 依次读取属性值 |
| 每个属性右侧的属性单位 | attributes[].unit_raw | 按物理列位置配对，可为“颜色”或“码”等 |
| 实际 | actual_spec_raw | 本品实际规格原文，不自行把10CM分配为长度或宽度 |
| 价格（美金） | price | 数值及USD币种；仅该MSKU，价格不是变体属性轴 |
| 包装-长/宽/高(inch) | package_dimensions | 包装外尺寸，原单位in，不是产品展开尺寸 |
| 包装-重量(lb) | package_weight | 包装重量，原单位lb，不是净重、单件重或计费重 |
| 商品重量/净重等明确字段 | product_weight | 独立保存重量类型及原单位，无数据则null |

未映射列完整保留。缺失为null，不填0或从相邻行、竞品、旧产品补值。SKU末尾1Y/5Y只是检查线索，不能覆盖属性列和“实际”。三者冲突时保留原值及受影响字段，等用户更正；明确更正后记录旧值、新值、来源和作用行。

“实际”中的总幅宽、流苏长、带宽、售卖长度与包装三边是不同概念。例如用户说明10cm由9cm流苏和1cm带宽构成，记录组成关系，不能改写为产品长10cm或包装宽10cm。读不到明确结构时只展示原文。

数字与单位分开存储，同时保留原字符串。保留用户原单位为主；需要换算时标记“换算值”及公式，不能把换算数称为实测。常数可用1yd=0.9144m、1in=2.54cm、1lb=453.59237g。无单位的重量不可默认lb。

## 标准化输入

JSON必须使用位置数组，避免重复表头丢失：

```json
{"source":"来源标识","sheet":"工作表或聊天表格","headers":["父体SKU","MSKU","属性1","属性单位","属性2","属性单位"],"rows":[{"row":2,"values":["P","P-Red-1Y","红色","颜色",1,"码"]}]}
```

CSV通过csv.reader读取表头与行数组。显式更正文件为JSON对象，例如 {"BJ-LS-F0221-Red-5Y":"BJ-LS-F0221-Red-1Y"}；只允许传入用户明确授权的更正，原数据不覆盖。没有明确更正不能擅自加此映射。

## 输出与身份

输出schema_version、source、headers（含列位置）、raw_rows、variants、families、issues、duplicate_groups、corrections、summary。每条variant含variant_id、parent_sku、msku、brand、category_label、attributes、actual_spec_raw、price、package_dimensions、package_weight、product_weight、sources、status、issues及extras。

variant_id稳定关联父体SKU+MSKU；同ID数据冲突保存conflict_records和各自来源，并标needs_review。MSKU缺失时给临时行ID，但不把它冒充真实MSKU。families保存实际组合；重复属性组合而MSKU不同为ambiguous_combination，保留各行，不静默合并。

脚本只识别当前契约和常见长度单位；其他字段走extras，需人工映射。颜色名称中英文不一致、不同父体复用MSKU、母品牌不一致、陌生单位等人工复查。完整variants.json是后续文案、UI及图片策划的数据源，而非根据HTML反向恢复事实。
