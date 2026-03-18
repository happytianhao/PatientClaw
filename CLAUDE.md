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
- **本轮回复**（40%）：当轮随访触发时生成回复
- **下轮才回复**（30%）：下次随访触发时生成回复
- **再下轮才回复**（20%）：再等一轮后生成回复
- **不回复**（10%）：超过3次触发（30分钟）未回复，标记为 `no_reply`

回复内容也要模拟真实性：
- 有时患者说病情好了（但用药没严格遵守）
- 有时患者反映不良反应（但没有立即来复诊）
- 有时患者回复很简短（"挺好的"）
- 有时患者会问问题

---

## 三、数据结构

所有数据在 `data/` 目录下，CSV 格式。

### 3.1 doctors.csv
字段：`doctor_id, name, age, gender, title, department, hospital, specialty, education, feishu_account, papers, awards`

详细内容见 `docs/doctor-profile.md`

### 3.2 patients.csv
字段：`patient_id, name, age, gender, occupation, feishu_account, primary_condition, medical_history, allergies, emergency_contact, first_visit_date`

30名患者，P001-P030，全部心血管科相关。

### 3.3 visits.csv
字段：`visit_id, patient_id, doctor_id, visit_date, visit_num, chief_complaint, diagnosis, bp, hr, notes`

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
你是北京协和医院心血管内科李晓峰主任医师的智能随访助理。

当前任务：为以下患者生成第{day}天随访消息。

患者信息：
- 姓名：{name}，{age}岁，{gender}
- 就诊日期：{visit_date}
- 诊断：{diagnosis}
- 当前用药：{medications}
- 医嘱要点：{notes}
- 历次随访摘要：{previous_followups}

要求：
1. 语气温暖专业，像医生助理一样关心患者
2. 针对该患者的具体病情和用药提问（不能用通用问题）
3. 根据第{day}天调整问题重点：
   - 第3天：重点问是否已开始服药、有无初始不适
   - 第7天：重点问用药效果、症状变化（血压/心率/胸痛等）
   - 第14天：重点做总结性评估，问是否需要复诊
4. 字数控制在120-150字
5. 结尾引导患者简要回复（如"请告知您最近的血压数值和用药情况"）

禁止：不得出现任何与该患者诊断无关的通用问候语；不得出现诊断结论或用药建议（只问，不改方案）。
```

### 4.3 患者回复解析 Prompt

```
你是一个医疗数据结构化助手。请分析以下患者对随访消息的回复，提取关键信息。

患者背景：
- 诊断：{diagnosis}
- 当前用药：{medications}

患者回复原文：
"{reply_text}"

请输出以下 JSON 格式（不要输出其他内容）：
{
  "medication_adherence": "good/partial/none/unknown",
  "condition_status": "improved/stable/unchanged/worsened/recovered",
  "adverse_reaction": "描述不良反应，无则填null",
  "key_values": {"blood_pressure": "如有提及血压值", "heart_rate": "如有提及心率", "other": "其他关键指标"},
  "needs_immediate_attention": true/false,
  "attention_reason": "如果needs_immediate_attention=true，说明原因",
  "priority_level": "normal/attention/urgent",
  "summary": "50字以内的中文摘要"
}

判断标准：
- urgent：患者描述胸痛加重/呼吸困难/晕厥/严重不适，需立即通知医生
- attention：用药依从性差/症状无改善/出现不良反应
- normal：用药正常/症状改善/无明显不适
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

报告格式（严格按此结构）：

# PatientClaw 日报 | {date}（系统第{system_day}天）
李晓峰主任 · 今日随访更新：{n}人 · 在管患者总计：{total}人

## ⚠️ 需立即关注（{n}人）
[列出priority=urgent的患者，包含：姓名、诊断、问题描述、建议行动]

## 🔔 需持续关注（{n}人）
[列出priority=attention的患者：姓名、诊断、问题描述]

## ✅ 今日状态良好（{n}人）
[简表：姓名 | 诊断 | 最新状态]

## 📭 未回复患者（{n}人）
[姓名 | 诊断 | 已发随访消息 | 等待天数]

## 📊 用药方案效果（累计）
[药物名称 | 使用患者数 | 依从率 | 症状改善率 | 不良反应发生率]

## 💡 今日用药洞察与建议
[基于今日数据，对特定药物/病种给出观察性总结，辅助医生调整策略]

要求：重点突出，数据准确，建议可操作，格式清晰便于手机阅读。
```

---

## 五、项目文件结构

```
Doctor/
├── README.md                         # 项目介绍（入门用）
├── CLAUDE.md                         # 本文件：AI 开发指导总文档
├── .gitignore
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
- [x] prescriptions.csv（88条药方记录）
- [x] doctor-profile.md（医生详细简介）

### 文档
- [x] README.md（项目入门介绍）
- [x] CLAUDE.md（AI 开发指导）
- [x] docs/doctor-profile.md（医生简介）
- [x] docs/report/PatientClaw项目说明书.md
- [ ] docs/openclaw-setup-guide.md（OpenClaw 配置教程）

### 功能开发（等 OpenClaw 配置后进行）
- [ ] 了解 OpenClaw 本地安装配置和接口
- [ ] 配置飞书机器人（获取 Bot Token）
- [ ] 实现定时扫描调度
- [ ] 实现随访消息生成（接入上述 Prompt）
- [ ] 实现患者回复模拟（含延迟/不回复逻辑）
- [ ] 实现回复解析（结构化数据写入 followups.csv + chat_logs.csv）
- [ ] 实现患者病情追踪报告生成
- [ ] 实现医生每日综合报告生成+飞书推送
- [ ] 端到端测试（跑通完整流程）

### 提交材料
- [ ] 海报制作 → docs/poster/
- [ ] 演示视频录制（≤3分钟）→ 上传B站/YouTube
- [ ] 所有公开链接填入 README
- [x] 首次推送到 GitHub
- [ ] 在 claw.lab.bza.edu.cn 提交报名

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
