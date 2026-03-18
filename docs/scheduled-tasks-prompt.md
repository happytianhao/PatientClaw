# PatientClaw 定时任务配置文档

> **本文档供 OpenClaw 读取，用于配置三个核心定时任务。请严格按照本文档的要求创建 Agent 并设置定时触发。**

---

## 时间约定

**系统内每过 10 分钟 = 现实中过了 1 天。**

所有时间计算均基于此约定：
- 患者就诊后 30 分钟 = 第3天随访
- 患者就诊后 70 分钟 = 第7天随访
- 患者就诊后 140 分钟 = 第14天随访
- 3 次触发（30分钟）内未回复 = 患者未回复，需标记并提醒

---

## 数据文件路径

所有数据文件位于项目 `data/` 目录下：

| 文件 | 说明 |
|------|------|
| `data/patients.csv` | 患者基础信息（patient_id, name, age, gender, occupation, feishu_account, primary_condition, medical_history, allergies） |
| `data/visits.csv` | 就诊记录（visit_id, patient_id, doctor_id, visit_date, visit_num, chief_complaint, diagnosis, bp, hr, notes） |
| `data/prescriptions.csv` | 药方记录（prescription_id, visit_id, medication, dosage, frequency, duration_days, instructions） |
| `data/followups.csv` | 随访记录（followup_id, patient_id, visit_id, followup_day, scheduled_time, sent_time, message_sent, reply_received, reply_time, reply_delay_type, medication_adherence, condition_status, adverse_reaction, needs_followup, priority_level, ai_summary） |
| `data/chat_logs.csv` | 聊天记录（log_id, patient_id, timestamp, sender, message_type, content） |
| `data/reports/{patient_id}_report.md` | 每位患者的病情追踪档案（系统自动生成和更新） |

---

## 任务一：患者病情询问 + 自动回复模拟

**Agent 名称**：`PatientClaw-随访询问器`
**触发频率**：每 10 分钟执行一次
**时区**：Asia/Shanghai

### 执行逻辑

每次触发时，按以下步骤执行：

**Step 0：扫描需要随访的患者（必须先做，提高效率）**

```
1. 读取 visits.csv，找每位患者最近就诊日期
2. 计算每位患者就诊后天数 = 今天 - 最近就诊日
3. 根据患者类型确定随访节点列表：
   - 加密（心衰/高血压3级）：[3, 7, 14, 21]
   - 标准：[3, 7, 14]
   - 高频（病情加重）：[3, 5, 7, 14]
   - 减频（痊愈）：[14]
4. 读取 followups.csv，找出每位患者已完成的节点
5. 待发节点 = 应完成节点 - 已完成节点
6. 只处理有待发节点的患者，其余跳过
```

输出格式示例：
```
今日需随访：14人，共20条消息
P001 就诊后第10天，待发：[3, 7]
P007 就诊后第6天，待发：[3]
...
```

读取 `data/patients.csv` 和 `data/visits.csv`，计算每位患者的就诊时间距现在过了多少小时，判断是否到达随访节点：

**标准患者**（病情控制良好，依从性好）：
- 第3/7/14天随访，对应就诊后 30/70/140 分钟

**加密患者**（慢性病：心衰、高血压3级）：
- 第3/7/14/21天随访，对应就诊后 30/70/140/210 分钟

**高频患者**（病情加重或未遵医嘱）：
- 第3/5/7/14天随访，对应就诊后 30/50/70/140 分钟，并立即提醒医生

**减频患者**（已痊愈或状态极佳）：
- 只做第14天随访，对应就诊后 140 分钟

每次触发时容差为 ±5 分钟。检查 `data/followups.csv`，跳过已发送过该随访节点消息的患者（避免重复发送）。

**Step 2：生成个性化随访消息**

对每位需要随访的患者，读取其完整信息后，使用以下 Prompt 生成随访消息：

```
你是北京协和医院心血管内科李晓峰主任医师的智能随访助理。

当前任务：为以下患者生成第{day}天随访消息。

【患者信息】
姓名：{name}，{age}岁，{gender}，{occupation}
就诊日期：{visit_date}
主诉：{chief_complaint}
诊断：{diagnosis}
血压/心率：{bp}/{hr}
医嘱要点：{notes}

【当前用药】
{medications_list}
（格式：药物名 {dosage}，{frequency}，共{duration_days}天，{instructions}）

【历次随访摘要】
{previous_followups_summary}
（如无历史随访，填"首次随访"）

【生成要求】
1. 语气温暖专业，像医生助理（不是医生本人）在关心患者
2. 针对该患者的具体病情提问：
   - 高血压患者：必问今日血压数值
   - 冠心病/心绞痛患者：必问胸痛/胸闷/活动耐量情况
   - 心力衰竭患者：必问气短/双踝水肿/每日体重变化
   - 心律失常患者：必问心悸/心跳不规律的感觉
   - 服用抗凝药（华法林等）患者：必问有无异常出血迹象
3. 根据第{day}天调整问题重点：
   - 第3天：主要问是否已开始规律服药，有无初期不适反应
   - 第5/7天：主要问症状是否改善，用药是否规律，有无副作用
   - 第14/21天：综合评估，问整体状态，是否需要复诊
4. 字数120-150字，结尾明确提示患者需要回复的内容
5. 不得出现与该患者诊断无关的问题
6. 不得给出用药建议或修改医嘱

只输出消息正文，不要有任何额外说明。
```

**Step 3：记录发送**

将随访消息写入以下文件：

写入 `data/followups.csv`（新增一行）：
- `followup_id`：自动生成（格式：F{patient_id}_{day}_{timestamp}）
- `patient_id`：患者ID
- `visit_id`：对应就诊ID
- `followup_day`：随访天数（3/5/7/10/14/21）
- `scheduled_time`：当前时间戳
- `sent_time`：当前时间戳
- `message_sent`：生成的随访消息内容
- 其余字段留空，等待回复后填写

写入 `data/chat_logs.csv`（新增一行）：
- `sender`：system
- `message_type`：followup_question
- `content`：随访消息内容

**Step 4：检查所有未回复患者，模拟本轮回复**

每次触发时，扫描 `data/followups.csv` 中所有 `reply_received` 为空的记录（即已发送随访消息但尚未收到回复的患者），对每位患者随机决定本轮是否回复：

- **本轮回复**（40%概率）：本次触发时生成患者回复
- **下轮才回复**（30%概率）：本轮跳过，下次触发时再判断
- **再下轮才回复**（20%概率）：跳过两轮后再判断
- **不回复**（10%概率）：若该记录已等待超过 3 次触发（3小时）仍未回复，标记为 `no_reply`

**注意**：患者回复只在每轮随访触发时被检查和生成，不使用独立的延迟定时器。

对于本轮决定回复的患者，使用以下 Prompt 生成患者回复内容：

```
你是一个医疗场景模拟助手，正在模拟患者收到随访消息后的真实回复。

【患者信息】
姓名：{name}，{age}岁，{gender}，{occupation}
诊断：{diagnosis}
当前用药：{medications_list}
随访天数：第{day}天
历次随访状态：{previous_status}

【收到的随访消息】
{followup_message}

【模拟规则】
根据以下概率随机选择患者当前状态：
- 60%：病情按预期改善，用药基本规律（偶尔漏服一次）
- 20%：用药依从性差（经常忘吃，或自行减量）
- 10%：出现轻微不良反应（如头晕、踝部水肿、胃部不适）
- 5%：症状加重，需要关注（如血压升高、胸痛加重、气短明显）
- 5%：病情明显好转或接近痊愈

【语言风格要求】
- 60岁以上老年患者：回复较详细，配合度高，用词朴实，可能会多说几句生活情况
- 40-60岁中年患者：回复较简洁，有时间紧迫感，直接说关键信息
- 40岁以下年轻患者：回复简短，偶尔用网络语，可能只回复几个字

【内容要求】
- 必须回应随访消息中具体问到的问题
- 如果有血压/心率等数值，给出具体数字（在合理范围内随机）
- 语言自然真实，不要像在填表格
- 如果状态是"症状加重"，描述要具体但不要过于夸张

只输出患者的回复文字，不要有任何额外说明。
```

**Step 5：解析回复并写入数据**

收到（模拟的）患者回复后，使用以下 Prompt 解析：

```
你是一个医疗数据结构化助手。请分析以下患者对随访消息的回复，提取关键信息。

【患者背景】
诊断：{diagnosis}
当前用药：{medications_list}
随访天数：第{day}天

【患者回复原文】
"{reply_text}"

请输出以下 JSON 格式（不要输出其他任何内容）：
{
  "medication_adherence": "good/partial/none/unknown",
  "condition_status": "improved/stable/unchanged/worsened/recovered",
  "adverse_reaction": "描述不良反应，无则填null",
  "key_values": {
    "blood_pressure": "如有提及血压值，如138/88mmHg，无则null",
    "heart_rate": "如有提及心率，无则null",
    "weight": "如有提及体重，无则null",
    "other": "其他关键指标"
  },
  "needs_immediate_attention": true或false,
  "attention_reason": "如果needs_immediate_attention=true，说明原因，否则null",
  "priority_level": "normal/attention/urgent",
  "reply_delay_type": "same_round/next_round/later_round/no_reply",
  "summary": "50字以内的中文摘要，客观描述患者状态"
}

判断标准：
- urgent：患者描述胸痛加重/呼吸困难/晕厥/严重不适，需立即通知医生
- attention：用药依从性差/症状无改善/出现不良反应/血压控制不佳
- normal：用药正常/症状改善/无明显不适
```

解析完成后：

更新 `data/followups.csv` 对应行：
- `reply_received`：患者回复原文
- `reply_time`：回复时间戳
- `reply_delay_type`：immediate/delayed/long_delayed/no_reply
- `medication_adherence`：解析结果
- `condition_status`：解析结果
- `adverse_reaction`：解析结果
- `needs_followup`：true/false
- `priority_level`：normal/attention/urgent
- `ai_summary`：50字摘要

写入 `data/chat_logs.csv`（新增一行）：
- `sender`：patient
- `message_type`：patient_reply
- `content`：患者回复原文

**如果 priority_level = urgent**，立即额外写入 `data/chat_logs.csv` 一条紧急提醒记录：
- `sender`：system
- `message_type`：doctor_alert
- `content`：`🚨 紧急提醒 | 患者{name}（{patient_id}）| 诊断：{diagnosis} | 问题：{attention_reason} | 建议立即联系患者`

**Step 6：每轮随访后立即更新患者病情总结**

每次随访消息发送并处理完回复后，立即为该患者更新病情追踪档案（不等待病情报告生成器的定时触发）。

读取该患者的完整数据（patients.csv + visits.csv + prescriptions.csv + followups.csv），使用任务二中的病情报告 Prompt 生成最新报告，覆盖写入 `data/reports/{patient_id}_report.md`。

同时在 `data/chat_logs.csv` 写入一条记录：
- `sender`：system
- `message_type`：system_note
- `content`：`已更新患者{name}（{patient_id}）病情追踪档案，第{day}天随访后更新，最新状态：{latest_status}`

**Step 7：检查超时未回复**

扫描 `data/followups.csv` 中所有 `reply_received` 为空且 `sent_time` 距现在超过 3 小时的记录，将其 `reply_delay_type` 更新为 `no_reply`，`priority_level` 更新为 `attention`，并写入一条 chat_log：
- `message_type`：system_note
- `content`：`患者{name}已超过3小时未回复第{day}天随访消息，已标记为未回复`

---

## 任务二：患者病情报告自动撰写与更新

**Agent 名称**：`PatientClaw-病情报告生成器`
**触发频率**：每 10 分钟执行一次
**时区**：Asia/Shanghai

### 执行逻辑

每次触发时，对所有在管患者执行以下操作：

**Step 1：读取患者完整数据**

对每位患者，读取：
- `data/patients.csv` 中该患者的基础信息
- `data/visits.csv` 中该患者的所有就诊记录
- `data/prescriptions.csv` 中该患者的所有药方
- `data/followups.csv` 中该患者的所有随访记录（按时间排序）

**Step 2：生成或更新病情追踪档案**

使用以下 Prompt 生成报告内容：

```
你是一个医疗文书助手。请根据以下数据，为患者生成标准化病情追踪档案。

【患者基础信息】
{patient_info}

【就诊记录】
{visit_records}

【用药方案】
{prescription_records}

【随访记录（按时间顺序）】
{followup_records}

【生成要求】
1. 格式严格按照下方模板
2. 语言专业、客观、准确，不做诊断，不修改用药建议
3. 病情趋势分析要基于随访数据客观描述，指出改善/恶化/稳定的具体依据
4. 用药依从性评估要给出百分比估算和具体说明
5. 后续建议要具体可操作（如"建议在第X天安排复诊"）
6. 如果随访数据不足（如只有1次随访），趋势分析部分注明"数据积累中"

输出格式：

# {name}（{patient_id}）病情追踪档案

**诊断**：{diagnosis}
**首次就诊**：{first_visit_date}
**报告生成时间**：{timestamp}
**报告类型**：{interim（中期）或 final（终期，仅Day14随访完成后）}

---

## 基本信息

| 项目 | 内容 |
|------|------|
| 姓名 | {name} |
| 年龄 | {age}岁 |
| 性别 | {gender} |
| 职业 | {occupation} |
| 主要诊断 | {diagnosis} |
| 既往病史 | {medical_history} |
| 药物过敏 | {allergies} |

## 就诊记录摘要

{visit_summary_table}
格式：| 就诊日期 | 主诉 | 诊断 | 血压/心率 | 医嘱要点 |

## 当前用药方案

{medications_table}
格式：| 药物名称 | 剂量 | 频次 | 疗程 | 特殊说明 |

## 随访时间线

{followup_timeline_table}
格式：| 随访天数 | 时间 | 用药依从 | 病情状态 | 不良反应 | 优先级 | 摘要 |

## 病情趋势分析

{trend_analysis}
（基于随访数据，客观描述症状变化趋势、血压/心率等关键指标变化、整体恢复情况）

## 用药依从性评估

{adherence_evaluation}
（估算依从率，说明依从性好/差的具体表现，分析可能原因）

## 后续随访建议

{followup_recommendations}
（根据当前状态，建议下次随访时间、需要重点关注的指标、是否需要复诊）

---
*本档案由 PatientClaw 自动生成，仅供医生参考，不构成诊断或治疗建议。*
```

**Step 3：写入文件**

将生成的报告写入 `data/reports/{patient_id}_report.md`：
- 如果文件不存在：直接创建并写入
- 如果文件已存在：**覆盖更新**（每次生成最新完整版本，不追加）

同时在 `data/chat_logs.csv` 写入一条记录：
- `sender`：system
- `message_type`：system_note
- `content`：`已更新患者{name}（{patient_id}）病情追踪档案，当前随访{n}次，最新状态：{latest_status}`

---

## 任务三：医生每日综合日报

**Agent 名称**：`PatientClaw-医生日报生成器`
**触发频率**：每 10 分钟执行一次
**时区**：Asia/Shanghai

### 执行逻辑

**Step 1：汇总数据**

读取：
- `data/followups.csv`：过去10分钟内新增或更新的随访记录
- `data/followups.csv`：所有患者的最新随访状态（每位患者取最新一条）
- `data/patients.csv`：患者基础信息
- `data/chat_logs.csv`：过去10分钟内的紧急提醒记录

统计：
- 今日随访更新人数（过去1小时内有新随访记录的患者数）
- urgent 患者列表
- attention 患者列表
- normal 患者列表
- no_reply 患者列表
- 各药物的依从率和症状改善率（从所有 followups 记录中统计）

**Step 2：生成日报**

使用以下 Prompt 生成日报内容：

```
你是一个医疗数据分析助手。请根据以下数据，为李晓峰主任医师生成今日患者综合日报。

【系统时间信息】
当前时间：{current_time}
系统运行天数：{system_day}（每1小时 = 1天）

【今日随访汇总】
今日随访更新患者数：{today_followup_count}
在管患者总数：{total_patients}

【需立即关注患者（priority=urgent）】
{urgent_list}
格式：patient_id | 姓名 | 诊断 | 问题描述 | 患者原话摘录

【需持续关注患者（priority=attention）】
{attention_list}
格式：patient_id | 姓名 | 诊断 | 问题描述

【今日状态良好患者（priority=normal）】
{normal_list}
格式：patient_id | 姓名 | 诊断 | 用药依从 | 最新状态

【超时未回复患者】
{no_reply_list}
格式：patient_id | 姓名 | 诊断 | 随访天数 | 已等待时长

【用药统计数据（累计）】
{drug_stats}
格式：药物名称 | 使用患者数 | 依从率 | 症状改善率 | 不良反应发生率

【生成要求】
1. 严格按照下方格式输出，不要增减章节
2. 重点突出，urgent 患者必须有具体建议行动
3. 用药洞察要基于数据，给出可操作的观察性建议（不是诊断，是数据规律）
4. 格式清晰，适合手机阅读
5. 数字要准确，不要编造数据

输出格式：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PatientClaw 日报
李晓峰主任医师 · {date}（系统第{system_day}天）
今日随访更新：{today_count}人 · 在管患者总计：{total}人
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 需立即关注（{n}人）
──────────────────────
{urgent_section}
每人格式：
• {name}（{diagnosis}）
  问题：{problem_description}
  患者原话："{quote}"
  建议：{action}

🔔 需持续关注（{n}人）
──────────────────────
{attention_section}
每人格式：• {name}（{diagnosis}）- {issue}

✅ 今日状态良好（{n}人）
──────────────────────
{good_section}
格式：{name} | {diagnosis} | 依从：{adherence} | {status}

📭 未回复患者（{n}人）
──────────────────────
{no_reply_section}
格式：{name} | {diagnosis} | 第{day}天随访 | 已等待{hours}小时

📊 用药方案效果（累计统计）
──────────────────────
{drug_efficacy_section}
格式：{drug_name} | {n}人使用 | 依从率{x}% | 改善率{x}% | 不良反应{x}%

💡 今日用药洞察与建议
──────────────────────
{insights_section}
（基于今日数据，指出值得关注的用药规律，辅助医生调整策略。每条建议一行，以"·"开头）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Step 3：记录日报**

将生成的日报写入 `data/chat_logs.csv`：
- `sender`：system
- `message_type`：doctor_report
- `content`：完整日报文本

同时将日报保存到本地文件 `data/reports/daily_report_{date}.md`，便于后续查阅。

**Step 4：通过飞书发送给医生**

调用飞书 Bot API，将日报发送给医生账号（feishu_account 见 `data/doctors.csv`）。

---

## 所有任务的通用要求

1. **每次执行必须有记录**：所有操作结果都要写入 `data/chat_logs.csv` 或对应数据文件，不允许静默执行。
2. **错误处理**：如果某个患者的数据读取失败，跳过该患者并在 chat_logs 写入错误记录，不影响其他患者的处理。
3. **幂等性**：每个随访节点只发送一次消息，执行前检查 followups.csv 避免重复。
4. **时间戳格式**：统一使用 ISO 8601 格式（`2026-03-18T14:30:00+08:00`）。
5. **文件编码**：所有 CSV 和 Markdown 文件使用 UTF-8 编码。
