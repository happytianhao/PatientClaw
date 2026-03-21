# PatientClaw 项目开发指导文档

> **本文档供 AI 助手（如 Claude）阅读，用于理解项目全貌并指导后续所有开发工作。**
> 每次开始新任务前，请先读完本文档再动手。

---

## 一、项目概述

**项目名称**：PatientClaw：患者诊后病情全自动跟踪统计系统
**副标题**：助力医生提升医术
**比赛**：北纬·龙虾大赛（第一届）· OpenClaw Hackathon
**主办方**：中关村人工智能研究院
**GitHub 仓库**：https://github.com/happytianhao/PatientClaw.git
**比赛截止**：2026年3月22日
**当前状态**：🏆 生产力赛道 · 决赛入围

---

## 二、系统核心设计

### 2.1 模拟医生

参见 `docs/doctor-profile.md`，心血管内科主任医师，北京协和医院，专长冠心病介入、高血压管理、心律失常、心力衰竭。

### 2.2 患者规模

- **30名患者**（patients.csv），全部为心血管科病患
- 病种覆盖：高血压（P001-P013）、冠心病/心绞痛（P014-P021）、心律失常（P022-P025）、心力衰竭（P026-P030）
- 就诊次数：慢性病患者3-6次，稳定患者2-3次，急症/筛查患者1次

### 2.3 时间压缩模型

**核心约定：系统内每过 10 分钟 = 现实中过了 1 天**

- 患者就诊后第3天（30分钟后）进行首次随访
- 患者就诊后第7天（70分钟后）进行中期随访
- 患者就诊后第14天（140分钟后）进行末期随访
- 每1天（10分钟后）生成一次医生日报，推送至飞书

### 2.4 随访频率动态调整规则

| 患者状态 | 随访频率 | 系统触发时间（分钟） |
|---------|---------|------------------|
| 病情控制良好，依从性好 | 标准：第3/7/14天 | 30/70/140 分钟后 |
| 慢性病（心衰、高血压3级） | 加密：第3/7/14/21天 | 30/70/140/210 分钟后 |
| 病情加重或未遵医嘱 | 高频：第3/5/7/14天 + 立即提醒医生 | 30/50/70/140 分钟后 |
| 已痊愈或状态极佳 | 减频：只做第14天 | 140 分钟后 |

### 2.5 随访消息设计原则

- **个性化**：必须结合患者具体诊断、用药、就诊天数生成，不能用通用模板
- **专业且温暖**：语气关心但不夸张，问题具体（"血压今天测了多少"而非"你好吗"）
- **简洁**：150字以内，明确告诉患者需要回复什么
- **渐进**：第3天问基础服药情况，第7天问效果，第14天做总结性评估

### 2.6 角色分工与交互模型

**系统只有一个真实飞书账号（医生账号），所有其他角色均由 OpenClaw 模拟。**

| 角色 | 由谁扮演 | 说明 |
|------|---------|------|
| 医生（李晓峰） | 真实用户 | 只需被动接收日报，无需主动操作 |
| 患者（P001-P030） | OpenClaw 模拟 | 自动生成回复，模拟真实延迟和内容 |
| 医生查询患者 | OpenClaw 模拟 | 系统自动模拟医生可能提出的问题并给出智能回答 |

**工作流说明**：
- OpenClaw 定时向自己（模拟患者）发送随访消息，并自动生成患者回复
- OpenClaw 解析模拟回复，写入 followups.csv 和 chat_logs.csv
- 每 10 分钟（= 1天）生成日报，通过飞书推送给真实医生账号
- 医生只需在飞书查看日报，无需任何操作

### 2.7 患者回复模拟规则

由于系统只有一个真实飞书账号（医生），患者回复完全由 OpenClaw 模拟生成，且**只在每轮随访触发时检查和生成**：
- **本轮回复**（67%）：当轮随访触发当天生成回复
- **下轮才回复**（20%）：次轮触发时才生成回复（延迟1天）
- **再下轮才回复**（10%）：较晚回复（延迟2-3天）
- **不回复**（3%）：超过3次触发仍未回复，标记为 `no_reply`

回复内容也要模拟真实性：
- 有时患者说病情好了（但用药没严格遵守）
- 有时患者反映不良反应（但没有立即来复诊）
- 有时患者回复很简短（"挺好的"）
- 有时患者会问问题

---

## 三、数据结构

所有数据在 `data/` 目录下，CSV 格式。

### 3.1 doctors.csv
字段：`doctor_id, name, age, gender, title, department, hospital, specialty, education, feishu_account, clinical_experience_years, outpatient_visits, pci_surgeries, pacemaker_cases, radiofrequency_cases, papers, awards, annual_patient_satisfaction, gratitude_letters, philosophy`

详细内容见 `docs/doctor-profile.md`

### 3.2 patients.csv
字段：`patient_id, name, age, gender, occupation, feishu_account, primary_condition, medical_history, allergies, emergency_contact, first_visit_date`

30名患者，P001-P030，全部心血管科相关。

### 3.3 visits.csv
字段：`visit_id, patient_id, doctor_id, visit_date, visit_time, clinic_location, visit_num, chief_complaint, diagnosis, bp, hr, examinations, exam_results, notes`

| 字段 | 说明 |
|------|------|
| visit_time | 就诊时段（上午/下午） |
| clinic_location | 诊室地点（如：东院区门诊楼3层312诊室） |
| examinations | 本次做的检查项目（如：心电图、Holter、超声心动、NT-proBNP） |
| exam_results | 检查结果（如：EF 35%、LDL 1.8mmol/L、ST段压低） |

慢性病患者有多条就诊记录（visit_num 递增）。

### 3.4 prescriptions.csv
字段：`prescription_id, visit_id, medication, dosage, frequency, duration_days, instructions`

与 visits.csv 通过 visit_id 关联。

### 3.5 followups.csv（系统运行时生成）
字段：
```
followup_id, patient_id, visit_id, followup_day, scheduled_time, sent_time,
message_sent, reply_received, reply_time, reply_delay_type,
medication_adherence, condition_status, adverse_reaction,
needs_followup, priority_level, ai_summary
```

字段说明：
- `reply_delay_type`：same_round / next_round / later_round / no_reply
- `medication_adherence`：good / partial / none / unknown
- `condition_status`：improved / stable / unchanged / worsened / recovered
- `priority_level`：normal / attention / urgent（urgent 触发立即通知医生）

### 3.6 chat_logs.csv（系统运行时生成，实时追加）
字段：
```
log_id, patient_id, timestamp, sender, message_type, content
```

字段说明：
- `sender`：system（系统发出）/ patient（患者回复）
- `message_type`：followup_question / patient_reply / system_note / doctor_alert

---

## 四、OpenClaw 工作流设计

### 4.1 工作流总览

```
┌─────────────────────────────────────────────────────┐
│              定时调度引擎（每10分钟扫描一次）            │
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────▼──────────────┐
          │  扫描任务：               │
          │  1. 检查需要随访的患者     │
          │  2. 检查超时未回复的患者   │
          │  3. 检查是否触发日报       │
          └────────────┬──────────────┘
                       │
          ┌────────────▼──────────────┐
          │  任务执行：               │
          │  A. 生成个性化随访消息     │
          │  B. 通过飞书发送给患者     │
          │  C. 监听并处理患者回复     │
          │  D. 解析回复→写入数据      │
          │  E. 生成患者病情报告       │
          │  F. 生成医生综合报告       │
          └───────────────────────────┘
```

### 4.1.1 定时任务设计

系统共有三类定时任务，所有执行结果均写入本地文件留存：

| 任务 | 触发频率 | 系统内含义 | 输出记录 |
|------|---------|-----------|---------|
| 医生日报推送 | 每 10 分钟 | 每天生成一次日报 | `chat_logs.csv`（message_type=doctor_report） |
| 患者病情询问 | 每 10 分钟 | 每天检查并执行一次随访 | `followups.csv` + `chat_logs.csv` |
| 患者病情总结 | 每 10 分钟 | 每天为每位患者更新病情追踪档案 | `data/reports/{patient_id}_report.md` |

**患者病情总结文件说明**：
- 路径：`data/reports/{patient_id}_report.md`，每位患者一个文件
- 内容：每次更新时追加最新随访摘要，保留完整历史记录
- 触发：每10分钟自动更新一次，Day 14 随访后生成完整版终期报告

### 4.2 随访消息生成 Prompt（核心）

```
你是北京协和医院心血管内科李晓峰主任医师的智能随访助理小龙虾。

当前任务：为以下患者生成第{day}天随访消息。

患者信息：
- 姓名：{name}，{age}岁，{gender}
- 就诊日期：{visit_date}
- 诊断：{diagnosis}
- 当前用药：{medications}
- 医嘱要点：{notes}
- 历次随访摘要：{previous_followups}

一、随访关怀问题清单（小龙虾每次必须覆盖的十大问题域）
1. 【用药情况】药有没有按时吃？有没有漏服或自行停药？
2. 【不良反应】吃药后有没有不舒服？比如头晕、咳嗽、脚肿、皮疹等？
3. 【自测指标】最近血压/心率在家测了吗？数值是多少？
4. 【核心症状】最困扰您的主要症状（胸闷/头晕/气短/水肿）有没有改善？
5. 【发作频率】最近不舒服发作的次数有没有减少或加重？
6. 【生活方式】饮食控制得怎么样？有没有坚持运动？烟酒情况如何？
7. 【睡眠质量】最近睡眠怎么样？夜间有没有憋醒或呼吸困难？
8. 【心理状态】最近情绪和心态怎么样？焦虑吗？
9. 【复诊提醒】下次复诊时间您记得吗？
10. 【想对医生说的】您有什么不舒服想告诉医生，或者想问医生的问题吗？

二、病种定制随访要点（必须结合患者诊断选配）

【高血压患者】必问：
- 近几日血压测了多少？（目标<130/80）
- 有没有按时服药？（强调不可自行停药）
- 有无头晕、头痛？（血压过高或过低信号）
- 盐有没有控制？（<6g/日）

【冠心病/心绞痛患者】必问：
- 有无胸闷、胸痛发作？（频率/持续时间/诱因）
- 活动耐力如何？（走路/上楼有无不适）
- 有无皮肤瘀青或牙龈出血？（抗血小板药物副作用）
- 硝酸酯类药物有没有8小时空白期？

【心力衰竭（HFrEF/HFpEF）患者】必问：
- 今日体重是多少？（每日监测，体重2天内增>2kg要警惕）
- 有无气短加重或夜间端坐呼吸？
- 有无双下肢水肿？（脚肿/腿肿）
- 限水限盐有没有做到？（水<2000ml/日）

【心房颤动患者】必问：
- 心悸感觉如何？（发作频率/持续时间）
- 有无异常出血迹象？（皮肤瘀青/牙龈出血/血尿）
- 抗凝药有没有按时吃？（绝对不可停药）
- 心室率/心律是否规律？

【糖尿病合并患者】必问：
- 空腹血糖测了吗？数值是多少？（目标<7mmol/L）
- 有无低血糖反应？（头晕/出冷汗/饥饿感）
- 有无下肢麻木或视物模糊？（糖尿病并发症信号）

【脑梗死后遗症患者】必问：
- 有无头晕加重、步态不稳？
- 有无新的肢体无力或麻木？
- 血压有没有坚持监测？（目标<130/80）

【睡眠呼吸暂停患者】必问：
- CPAP呼吸机有没有坚持使用？
- 晨起头痛有没有改善？
- 夜间打鼾和呼吸暂停情况如何？

三、随访节点侧重点

【第3天随访（出院/新用药初期）】
重点：药吃得习惯吗？有没有不舒服？有没有开始监测指标？
语气：关心+提醒，告知初期可能的小反应，鼓励坚持

【第7天随访（用药一周评估）】
重点：药效如何？症状有没有改善？指标控制得怎么样？
语气：鼓励+评估，确认依从性，关注副作用

【第14天随访（两周总结评估）】
重点：整体感觉怎么样？需要来复诊吗？
语气：温暖+总结，引导复诊，提醒检查指标复查

【慢性病定期随访】
重点：综合指标+症状+生活方式+依从性
语气：稳定关怀，建立长期信任关系

四、紧急情况识别规则
出现以下关键词或描述，必须立即标记为 urgent 并建议患者就诊：
- 胸痛持续>20分钟不缓解
- 突发呼吸困难、不能平卧
- 意识丧失/晕厥/眼前发黑
- 血压极高（>180/120）或极低（<90/60）
- 严重出血（消化道/脑出血疑似）
- 下肢突然肿胀疼痛（深静脉血栓？）
- 严重心律失常感（心跳极快/极慢/不规律伴头晕）

小龙虾发现紧急情况时的回复语气：关切+坚定，告知患者立即联系医生或就近急诊。

五、消息生成要求
1. 语气温暖专业，像医生助理一样关心患者，体现李晓峰主任团队的医者仁心
2. 针对该患者的具体病种、用药组合提问（必须用病种定制问题，不得用通用问题）
3. 根据第{day}天调整问题重点（见第三节）
4. 字数控制在120-150字
5. 结尾引导患者简要回复，明确告知需要回复哪些内容
6. 严禁出现诊断结论或用药方案调整建议（只问，不判断）

禁止：
- 不得出现与患者诊断无关的通用问候语（如"最近天气变化，注意身体哦"）
- 不得做出诊断结论或修改用药建议
- 不得向患者透露医疗费用或药品价格信息
```

### 4.3 患者回复解析 Prompt

```
你是一个医疗数据结构化助手。请分析以下患者对随访消息的回复，提取关键信息。

患者背景：
- 诊断：{diagnosis}
- 当前用药：{medications}
- 随访天数：第{day}天

患者回复原文：
"{reply_text}"

请输出以下 JSON 格式（不要输出其他内容）：
{
  "medication_adherence": "good/partial/none/unknown",
  "condition_status": "improved/stable/unchanged/worsened/recovered",
  "adverse_reaction": "描述不良反应，无则填null",
  "key_values": {
    "blood_pressure": "如有提及血压值，如135/85",
    "heart_rate": "如有提及心率，如72bpm",
    "weight": "如有提及体重，如68.2kg（心衰患者必填）",
    "blood_glucose": "如有提及血糖值",
    "other": "其他关键指标，如体重变化、水肿程度等"
  },
  "symptom_assessment": {
    "chest_pain": "有无胸痛（有心绞痛/冠心病患者必填）",
    "dyspnea": "有无气短/呼吸困难",
    "edema": "有无下肢水肿",
    "palpitation": "有无心悸",
    "dizziness": "有无头晕",
    "bleeding": "有无出血迹象（抗凝/抗血小板患者必填）"
  },
  "lifestyle_factors": {
    "diet": "饮食控制情况",
    "exercise": "运动情况",
    "smoking_alcohol": "烟酒情况"
  },
  "needs_immediate_attention": true/false,
  "attention_reason": "如果needs_immediate_attention=true，说明原因",
  "urgent_keywords_detected": ["如有检测到紧急关键词，列出"],
  "priority_level": "normal/attention/urgent",
  "followup_frequency_suggestion": "建议下一轮随访频率：standard/enhanced/high_frequency/reduced",
  "summary": "50字以内的中文摘要"
}

判断标准：
- urgent（紧急）：患者描述以下任意情况 → 立即通知医生
  * 胸痛持续>20分钟不缓解
  * 突发呼吸困难、不能平卧（夜间端坐呼吸）
  * 意识丧失/晕厥/眼前发黑
  * 血压极高（>180/120）或极低（<90/60）
  * 严重出血（消化道出血/脑出血疑似）
  * 下肢突然肿胀疼痛
  * 严重心律失常感伴头晕
- attention（需关注）：用药依从性 partial/none / 症状 unchanged/worsened / 出现不良反应
- normal（正常）：用药 good / 症状 improved/recovered / 无明显不适

随访频率建议：
- standard（标准）：控制良好，无特殊情况 → 第3/7/14天
- enhanced（加密）：症状改善慢/依从性 partial → 第3/5/7/14天
- high_frequency（高频）：心衰急性期/病情加重 → 立即提醒医生
- reduced（减频）：状态极佳，依从性好 → 只做第14天
```

### 4.4 患者病情追踪报告 Prompt

```
你是一个医疗文书助手。请根据以下数据，为患者{name}生成一份标准化病情追踪报告。

患者基础信息：{patient_info}
就诊记录：{visit_info}
用药方案：{prescriptions}
随访记录（按时间顺序）：{followups}

报告要求：
- 格式：结构化Markdown，包含以下章节
  1. 患者基本信息
  2. 诊断与就诊记录
  3. 用药方案
  4. 随访时间线（每次随访一行）
  5. 病情趋势分析（客观描述变化）
  6. 用药依从性评估
  7. 后续随访建议
- 语言：专业、客观、准确
- 长度：500-800字
- 不得做出诊断或修改用药建议
```

### 4.5 医生每日综合报告 Prompt

触发频率：每 10 分钟（= 系统内1天）生成一次，通过飞书推送给医生。

```
你是一个医疗数据分析助手。请根据以下患者数据，为李晓峰主任医师生成今日患者综合日报。

数据范围：过去10分钟（= 系统内1天）内所有随访更新，以及所有患者当前状态
患者随访汇总：{all_followup_summaries}
用药统计数据：{medication_stats}
所有患者当前状态：{all_patient_status}
回复时机数据：{reply_delay_stats}

报告格式（严格按此10章结构）：

# PatientClaw 日报 | {date}（系统第{system_day}天）
李晓峰主任 · 今日随访更新：{n}人 · 在管患者总计：{total}人

## 🔴 需立即处理（{n}人）
[priority=urgent 的患者：姓名、诊断、紧急问题、患者自述、医生建议行动]

## 📉 病情恶化（{n}人）
[当日病情加重的患者：姓名、诊断、病情描述]

## 🟡 需持续关注（{n}人）
[priority=attention 的患者：姓名、诊断、问题类型（依从/不良反应/需观察）]

## 📈 今日病情好转（{n}人）
[当日症状改善的患者：姓名、诊断、改善情况]

## 🍬 今日用药依从性
[按时服药：N人 | 漏服/停药：M人，列出漏服患者]

## 💬 患者提问汇总
[分类展示：🔴需立即回复（M条）/ 🟡建议回复（N条）/ ⚪常规问答（L条）]

## 📭 未回复患者（{n}人）
[未回复患者姓名、诊断、第几天随访，建议电话跟进]

## 📋 累计在管患者状态（系统第X天）
[全体患者状态总表：姓名 | 诊断 | 最新状态 | 依从性 | 优先级]

## 📊 用药方案效果统计（累计）
[药物 | 使用患者 | 改善率 | 稳定率 | 恶化率 | 依从率 | 不良反应 | 评估标签]

## 💡 今日洞察与闭环建议
[病情加重分析 + 用药效果洞察 + 紧急提问提醒 + 失联患者跟进 + 闭环指导医生调整策略]

要求：重点突出，数据准确，建议可操作，格式清晰便于手机阅读。
优先级：紧急问题必须排在最前面。
```

---

## 五、项目文件结构

```
Doctor/
├── README.md                         # 项目介绍（入门用）
├── CLAUDE.md                         # 本文件：AI 开发指导总文档
├── .gitignore
│
├── scripts/                          # 生成脚本（运行时自动生成数据，非提交物）
│   ├── generate_followups.py          # 生成随访记录
│   ├── generate_reports.py            # 生成30份患者病情报告
│   ├── generate_daily_reports.py      # 生成10份医生日报
│   ├── generate_diverse_scenarios.py  # 多样化病情场景模拟
│   └── verify_consistency.py          # 一致性验证
│
├── data/                             # 数据层（CSV）
│   ├── doctors.csv                   # 医生档案
│   ├── patients.csv                  # 30名患者
│   ├── visits.csv                    # 就诊记录（~91条，含多次就诊）
│   ├── prescriptions.csv             # 药方记录
│   ├── followups.csv                 # 随访记录（系统生成）
│   └── chat_logs.csv                 # 聊天记录（系统实时写入）
│
├── docs/
│   ├── doctor-profile.md             # 医生简介文档
│   ├── report/
│   │   └── PatientClaw项目说明书.md  # 比赛提交说明书
│   ├── openclaw-setup-guide.md       # OpenClaw 配置教程（小白版）
│   ├── poster/                       # 海报
│   ├── slides/                       # 演示视频稿 PPT
│   └── video/                        # 视频说明
│
└── materials/                        # 参考材料（不提交）
```

---

## 六、待完成清单

### 数据 ✅
- [x] doctors.csv（1名心内科主任医师）
- [x] patients.csv（30名患者）
- [x] visits.csv（~91条记录，含多次就诊）
- [x] prescriptions.csv（95条药方记录）
- [x] doctor-profile.md（医生详细简介）

### 文档 ✅（决赛版已更新）
- [x] README.md（项目入门介绍，突出应用价值与社会效益）
- [x] CLAUDE.md（AI 开发指导）
- [x] docs/doctor-profile.md（医生简介）
- [x] docs/report/PatientClaw项目说明书.md（强化社会价值章节）
- [ ] docs/openclaw-setup-guide.md（OpenClaw 配置教程）

### 提交材料（决赛版）
- [x] ✅ 海报制作 → docs/poster/index.html（HTML版，需导出PNG @ 150DPI 0.8m×2m）
- [x] ✅ 演示视频稿 PPT → docs/slides/index.html（16:10比例，含社会价值内容）
- [x] ✅ 演示视频 → https://youtu.be/3f7pIgkAC7s（3分钟，16:9）
- [x] ✅ README 所有公开链接已填入
- [x] ✅ 代码已推送 GitHub
- [ ] 在 claw.lab.bza.edu.cn 提交报名（3月21日前）
- [ ] 导出海报 PNG 并上传提交平台

---

## 七、开发约定

- 所有代码提交到 `main` 分支
- 提交格式：`feat/fix/docs/data: 描述`
- 视频文件不提交 git，用外链
- 完成每个模块后更新本文档的待完成清单
- 如遇技术方案选择，先列选项+权衡，再实施

---

## 八、AI 助手工作指引

1. **优先读完本文档**再开始任何任务
2. 不要在未确认 OpenClaw API 的情况下写具体调用代码，先探索其文档/配置
3. 数据字段不要擅自修改（其他模块依赖这些字段）
4. Prompt 语气要体现心血管科专业性（精准的医学术语 + 温暖的患者沟通）
5. 完成任何模块后更新第六节的待完成清单
6. 不确定的技术方案，先列出选项和权衡，由用户决策
7. **跨文档一致性原则**：每当用户提出任何修改建议或功能变更，必须同步更新**所有相关文档**，包括但不限于 `README.md`、`CLAUDE.md`、`docs/openclaw-setup-guide.md`、`docs/report/PatientClaw项目说明书.md`。不可只改一处，其他文档保持旧内容。
8. **更新本文档**：用户提出的工作规则、架构决策或设计变更，也要写入本节，确保下次 AI 助手能继续遵守。

---

## 九、决赛提交要求

> 比赛：北纬·龙虾大赛（第一届）· OpenClaw Hackathon · 生产力赛道
> 评审标准：**应用价值与社会效益**
> 决赛提交截止：**2026年3月21日（周六）**

### 9.1 提交材料清单

| 材料 | 要求 | 状态 | 文件位置 |
|------|------|------|---------|
| 易拉宝图片 | 150DPI，0.8m × 2m（4725 × 11811 px） | HTML已就绪，需导出PNG | `docs/poster/index.html` |
| 路演 PPT | 16:10 比例 | ✅ 已完成 | `docs/slides/index.html` |
| 演示视频 | 16:9 比例，≤3分钟 | ✅ YouTube外链 | https://youtu.be/3f7pIgkAC7s |
| 项目说明书 | 突出社会价值与应用效益 | ✅ 已更新 | `docs/report/PatientClaw项目说明书.md` |

### 9.2 提交时间节点

- **3月21日 中午12:00前**：易拉宝 + 项目材料提交
- **3月21日 下午17:00前**：PPT + 视频提交
- ⚠️ 逾期提交将被取消比赛资格

### 9.3 评审重点（应用价值与社会效益）

路演和文档应重点呈现：
1. **真实社会问题**：70%患者诊后失联的现状和数据
2. **可量化影响**：30人零失联、92%依从率、自动预警4例异常
3. **可扩展性**：科室扩展、地域扩展、渠道扩展路径
4. **对医疗系统的价值**：降低医疗成本、提升基层医疗质量、改善医患关系
