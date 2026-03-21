"""
生成 PatientClaw 患者随访报告
用法: python3 generate_reports.py
"""
import csv, os
from datetime import datetime, timedelta

# ===== 数据读取 =====
patients = {}
with open('data/patients.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        patients[row['patient_id']] = row

rx_by_visit = {}
with open('data/prescriptions.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        vid = row['visit_id']
        if vid not in rx_by_visit:
            rx_by_visit[vid] = []
        rx_by_visit[vid].append(row)

visits_all = []
with open('data/visits.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        visits_all.append(row)

followups_all = []
with open('data/followups.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        followups_all.append(row)

# 构建患者数据
patient_data = {}
for v in visits_all:
    pid = v['patient_id']
    if pid not in patient_data:
        patient_data[pid] = {'visits': [], 'followups': [], 'rx': []}
    patient_data[pid]['visits'].append(v)
for pid, data in patient_data.items():
    data['visits'].sort(key=lambda x: int(x['visit_num']))

# 填入随访记录（注意用的是 followups_all）
for f in followups_all:
    pid = f['patient_id']
    if pid in patient_data:
        patient_data[pid]['followups'].append(f)
for pid in patient_data:
    patient_data[pid]['followups'].sort(key=lambda x: int(x['followup_day']))

for pid, data in patient_data.items():
    for v in data['visits']:
        vid = v['visit_id']
        if vid in rx_by_visit:
            data['rx'].extend(rx_by_visit[vid])

# ===== 辅助函数 =====
def adherence_label(a):
    return {'good':'✓ 规律服药','partial':'⚠ 部分漏服','none':'✗ 自行停药','unknown':'？ 未确认'}[a]

def condition_label(c):
    return {'improved':'↑ 改善','stable':'→ 稳定','unchanged':'— 无变化','worsened':'↓ 恶化','recovered':'★ 痊愈'}[c]

def delay_label(d):
    return {'same':'✓ 本轮回复','next':'○ 次轮回复','later':'△ 较晚回复','no_reply':'✗ 未回复'}[d]

def priority_icon(p):
    return {'normal':'⚪','attention':'🟡','urgent':'🔴'}[p]

def get_latest_rx(pid):
    data = patient_data.get(pid, {})
    if not data['visits']:
        return []
    # 向前追溯最近有处方的visit
    for v in reversed(data['visits']):
        vid = v['visit_id']
        if vid in rx_by_visit:
            return rx_by_visit[vid]
    return []

def adherence_overall(followups):
    """综合判断整体依从性"""
    ads = [f['medication_adherence'] for f in followups]
    if 'none' in ads: return 'none'
    if 'unknown' in ads: return 'unknown'
    if ads.count('partial') >= len(ads) * 0.5: return 'partial'
    if 'partial' in ads: return 'partial'
    return 'good'

def condition_trend(followups):
    """判断病情趋势"""
    conds = [f['condition_status'] for f in followups if f.get('condition_status')]
    if not conds: return '暂无数据'
    if 'worsened' in conds: return '恶化'
    if conds[-1] == 'improved' and conds.count('improved') >= len(conds) * 0.6: return '持续改善'
    if conds[-1] == 'improved': return '逐步改善'
    if conds[-1] == 'stable': return '基本稳定'
    if conds[-1] == 'unchanged': return '无明显变化'
    return conds[-1]

def generate_report(pid):
    p = patients[pid]
    data = patient_data[pid]
    followups = data['followups']
    visits = data['visits']
    rx_list = get_latest_rx(pid)

    name = p['name']
    age = p['age']
    gender = p['gender']
    occupation = p['occupation']
    primary_condition = p['primary_condition']
    medical_history = p['medical_history']
    allergies = p['allergies']
    emergency_contact = p['emergency_contact']
    first_visit_date = p['first_visit_date']

    last_visit = visits[-1] if visits else {}
    last_diag = last_visit.get('diagnosis', '暂无')
    last_bp = last_visit.get('bp', '?')
    last_hr = last_visit.get('hr', '?')

    # 整体评估
    overall_adh = adherence_overall(followups)
    trend = condition_trend(followups)
    no_reply_count = sum(1 for f in followups if f['reply_delay_type'] == 'no_reply')
    partial_count = sum(1 for f in followups if f['medication_adherence'] == 'partial')
    worsening_count = sum(1 for f in followups if f['condition_status'] == 'worsened')
    attention_count = sum(1 for f in followups if f['priority_level'] in ('attention','urgent'))

    # 患者提问收集
    patient_questions = []
    for f in followups:
        reply = f.get('reply_received', '')
        if '请问' in reply and '李主任' in reply:
            q_start = reply.find('请问')
            q_text = reply[q_start:].replace('请问李主任，','').strip()
            q_text = q_text.rstrip('。').rstrip(',').rstrip('？').rstrip('?')
            if q_text:
                patient_questions.append({
                    'day': f['followup_day'],
                    'question': q_text,
                    'reply_time': f['reply_time'],
                    'reply_delay': f['reply_delay_type']
                })

    # ===== 构建 Markdown 报告 =====
    lines = []
    lines.append(f"# 患者随访报告 | {name}（{pid}）")
    lines.append(f"")
    lines.append(f"> **生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    lines.append(f"> **报告医生**：李晓峰 主任医师（心血管内科）  ")
    lines.append(f"> **随访系统**：PatientClaw 患者诊后病情全自动跟踪统计系统  ")
    lines.append(f"")

    # ===== 第一章：患者基本信息 =====
    lines.append(f"## 一、患者基本信息")
    lines.append(f"")
    lines.append(f"| 项目 | 内容 |")
    lines.append(f"|------|------|")
    lines.append(f"| 患者编号 | {pid} |")
    lines.append(f"| 姓名 | {name} |")
    lines.append(f"| 年龄 | {age}岁 |")
    lines.append(f"| 性别 | {'男' if gender == '男' else '女'} |")
    lines.append(f"| 职业 | {occupation} |")
    lines.append(f"| 首次就诊日期 | {visits[0]['visit_date'] if visits else '无'} |")
    lines.append(f"| 就诊次数 | {len(visits)}次 |")
    lines.append(f"| 主诊断 | {primary_condition} |")
    lines.append(f"| 既往病史 | {medical_history} |")
    lines.append(f"| 过敏史 | {p['allergies'] if p['allergies'] else '无'} |")
    lines.append(f"| 紧急联系人 | {p['emergency_contact']} |")
    lines.append(f"")

    # ===== 第二章：诊断与就诊记录 =====
    lines.append(f"## 二、诊断与就诊记录")
    lines.append(f"")
    lines.append(f"| 就诊次数 | 日期 | 主诉 | 诊断 | 血压 | 心率 | 备注 |")
    lines.append(f"|----------|------|------|------|------|------|------|")
    for v in visits:
        chief = v['chief_complaint']
        diag = v['diagnosis']
        bp = v['bp']
        hr = v['hr']
        notes = v['notes']
        lines.append(f"| 第{v['visit_num']}次 | {v['visit_date']} | {chief} | {diag} | {bp} | {hr} | {notes} |")
    lines.append(f"")

    # ===== 第三章：用药方案 =====
    lines.append(f"## 三、当前用药方案")
    lines.append(f"")
    if rx_list:
        lines.append(f"| 药物 | 剂量 | 用法 | 持续时间 | 医嘱 |")
        lines.append(f"|------|------|------|----------|------|")
        for r in rx_list:
            lines.append(f"| {r['medication']} | {r['dosage']} | {r['frequency']} | {r['duration_days']} | {r['instructions']} |")
    else:
        lines.append(f"*暂无处方记录*")
    lines.append(f"")
    lines.append(f"> **注**：随访记录基于最新一次就诊的用药方案。如就诊期间有方案调整，以最近一次为准。")
    lines.append(f"")

    # ===== 第四章：随访时间线 =====
    fu_days = [f['followup_day'] for f in followups]
    fu_freq_note = f"第{'/'.join(fu_days)}天（共{len(followups)}次）"
    lines.append(f"## 四、随访时间线")
    lines.append(f"")
    lines.append(f"> **随访频率**：{fu_freq_note}（{priority_icon('normal') if attention_count == 0 else priority_icon('attention')} {'需重点关注' if attention_count > 0 else '整体状况良好'}）")
    lines.append(f"")
    lines.append(f"| 随访节点 | 随访日期 | 医生提问摘要 | 患者回复摘要 | 依从性 | 病情状态 | 不良反应 | 回复时机 | 优先 |")
    lines.append(f"|----------|----------|------------|------------|--------|----------|---------|---------|------|")

    for f in followups:
        msg = f['message_sent']
        # 提取消息核心问题（前50字）
        msg_short = msg[:60].replace('\n','').replace('\r','')

        reply = f['reply_received']
        if reply:
            reply_short = reply[:50].replace('\n','').replace('\r','')
        else:
            reply_short = '【患者未回复】'

        adh = adherence_label(f['medication_adherence'])
        cond = condition_label(f['condition_status'])
        adverse = f['adverse_reaction'] if f['adverse_reaction'] else '—'
        delay = delay_label(f['reply_delay_type'])
        prio = f['priority_level']

        lines.append(f"| 第{f['followup_day']}天 | {f['scheduled_time']} | {msg_short}… | {reply_short}… | {adh} | {cond} | {adverse} | {delay} | {prio} |")

    lines.append(f"")

    # ===== 第五章：用药依从性评估 =====
    lines.append(f"## 五、用药依从性评估")
    lines.append(f"")
    adh_icon = {'good':'✅','partial':'⚠️','none':'❌','unknown':'❓'}
    adh_desc = {
        'good': f'{adh_icon["good"]} **整体依从性：良好**',
        'partial': f'{adh_icon["partial"]} **整体依从性：部分依从**',
        'none': f'{adh_icon["none"]} **整体依从性：依从性差（自行停药）**',
        'unknown': f'{adh_icon["unknown"]} **整体依从性：未能确认（未回复）**',
    }
    lines.append(adh_desc.get(overall_adh, overall_adh))
    lines.append(f"")
    lines.append(f"| 随访节点 | 依从性 | 具体情况 |")
    lines.append(f"|----------|--------|----------|")
    for f in followups:
        adh_val = f['medication_adherence']
        adh_str = adherence_label(adh_val)
        if adh_val == 'good':
            detail = '按时服药，遵医嘱'
        elif adh_val == 'partial':
            reply = f['reply_received']
            # 提取漏服信息
            if '漏' in reply or '忘' in reply:
                detail = reply[:60].replace('\n','')
            else:
                detail = '存在依从性问题'
        elif adh_val == 'none':
            detail = '自行停药'
        elif adh_val == 'unknown':
            detail = '未回复随访消息'
        else:
            detail = ''
        lines.append(f"| 第{f['followup_day']}天 | {adh_str} | {detail} |")
    lines.append(f"")

    # ===== 第六章：病情趋势分析 =====
    lines.append(f"## 六、病情趋势分析")
    lines.append(f"")
    lines.append(f"### 6.1 病情总趋势")
    lines.append(f"")
    trend_icons = {'持续改善':'📈','逐步改善':'📈','基本稳定':'➡️','无明显变化':'➡️','恶化':'📉'}
    lines.append(f"**总体趋势**：{trend_icons.get(trend, '•')} {trend}")
    lines.append(f"")

    lines.append(f"### 6.2 各随访节点病情对比")
    lines.append(f"")
    lines.append(f"| 随访节点 | 病情状态 | 指标/症状记录 |")
    lines.append(f"|----------|----------|--------------|")
    for f in followups:
        reply = f['reply_received'] if f['reply_received'] else '【未回复】'
        cond = condition_label(f['condition_status'])
        lines.append(f"| 第{f['followup_day']}天 | {cond} | {reply[:80]} |")
    lines.append(f"")

    # 病情变化总结
    worsened_items = [(f['followup_day'], f['reply_received']) for f in followups if f['condition_status'] == 'worsened']
    improved_items = [(f['followup_day'], f['reply_received']) for f in followups if f['condition_status'] == 'improved']

    if worsening_count > 0:
        lines.append(f"### 6.3 病情加重记录")
        lines.append(f"")
        for day, reply in worsened_items:
            lines.append(f"**第{day}天**：{reply}")
            lines.append(f"")
        lines.append(f"> ⚠️ 上述节点出现病情加重，需重点关注并及时处理。")
        lines.append(f"")
    else:
        lines.append(f"### 6.3 病情加重记录")
        lines.append(f"")
        lines.append(f"> ✅ 随访期间未出现病情加重情况。")
        lines.append(f"")

    # ===== 第七章：患者提问记录 =====
    lines.append(f"## 七、患者提问记录")
    lines.append(f"")
    if patient_questions:
        lines.append(f"> 患者共提出 {len(patient_questions)} 个问题，以下为详细记录：")
        lines.append(f"")
        lines.append(f"| 随访节点 | 提问内容 | 回复时机 |")
        lines.append(f"|----------|----------|----------|")
        for q in patient_questions:
            delay_emoji = {'same':'✓','next':'○','later':'△','no_reply':'✗'}.get(q['reply_delay'],'•')
            lines.append(f"| 第{q['day']}天 | {q['question']} | {delay_emoji} {q['reply_time']} |")
        lines.append(f"")
    else:
        lines.append(f"> 随访期间患者未主动提问。")
        lines.append(f"")

    # ===== 第八章：回复规律分析 =====
    lines.append(f"## 八、回复规律分析")
    lines.append(f"")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| 应答随访次数 | {len(followups)}次 |")
    lines.append(f"| 本轮回复（当天） | {sum(1 for f in followups if f['reply_delay_type']=='same')}次 |")
    lines.append(f"| 次轮回复（延迟1天） | {sum(1 for f in followups if f['reply_delay_type']=='next')}次 |")
    lines.append(f"| 较晚回复（延迟2天） | {sum(1 for f in followups if f['reply_delay_type']=='later')}次 |")
    lines.append(f"| 未回复 | {no_reply_count}次 |")
    lines.append(f"")

    if no_reply_count > 0:
        lines.append(f"> ⚠️ 共有 **{no_reply_count}次** 随访患者未回复，建议通过电话等渠道主动跟进。")
        lines.append(f"")
    else:
        lines.append(f"> ✅ 患者在所有随访节点均及时回复，沟通顺畅。")
        lines.append(f"")

    # ===== 第九章：随访综合评估与建议 =====
    lines.append(f"## 九、随访综合评估与建议")
    lines.append(f"")

    # 综合评估
    lines.append(f"### 综合评估")
    lines.append(f"")

    risk_factors = []
    if overall_adh in ('partial', 'none', 'unknown'):
        risk_factors.append('用药依从性问题')
    if worsening_count > 0:
        risk_factors.append('随访期间病情有加重记录')
    if no_reply_count > 0:
        risk_factors.append('存在失联/未回复情况')
    if attention_count > 0:
        risk_factors.append(f'共{attention_count}次随访标记为"需关注"')

    if risk_factors:
        lines.append(f"**风险因素**：{'、'.join(risk_factors)}")
    else:
        lines.append(f"**风险因素**：无明显风险因素")
    lines.append(f"")

    # 分级
    if worsening_count >= 2 or overall_adh == 'none' or no_reply_count >= 2:
        level = '🔴 高风险'
        level_desc = '建议立即与患者取得联系，详细评估病情，必要时安排提前复诊。'
    elif worsening_count == 1 or overall_adh == 'partial' or no_reply_count == 1 or attention_count >= 3:
        level = '🟡 中风险'
        level_desc = '需持续密切观察，加强随访频率，关注患者依从性。'
    elif partial_count > 0 or attention_count > 0:
        level = '🟢 低风险'
        level_desc = '整体状况良好，但存在个别依从性问题，建议持续关注。'
    else:
        level = '✅ 良好'
        level_desc = '患者依从性好，病情稳定/改善，继续按计划随访。'

    lines.append(f"**随访等级**：{level}")
    lines.append(f"")
    lines.append(f"**评估说明**：{level_desc}")
    lines.append(f"")

    # 建议
    lines.append(f"### 随访建议")
    lines.append(f"")

    suggestions = []
    if worsening_count > 0:
        suggestions.append('密切监测病情变化，必要时提前安排复诊')
    if overall_adh == 'partial':
        suggestions.append('加强用药依从性教育，简化用药方案，减少漏服可能')
    if overall_adh == 'none':
        suggestions.append('立即联系患者，了解停药原因，强调规范治疗重要性')
    if no_reply_count > 0:
        suggestions.append('尝试电话等渠道主动联系，确认患者安全')
    if worsening_count == 0 and overall_adh == 'good':
        suggestions.append('继续按当前方案管理，保持现状')
    if trend in ('持续改善','逐步改善'):
        suggestions.append('维持当前治疗方案，关注长期预后')

    for i, s in enumerate(suggestions, 1):
        lines.append(f"{i}. {s}")
    lines.append(f"")

    # ===== 报告结尾 =====
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"*本报告由 PatientClaw 患者诊后病情全自动跟踪统计系统自动生成*")
    lines.append(f"*Doctor: 李晓峰 主任医师 | 北京协和医院 心血管内科*")
    lines.append(f"*Report ID: {pid}_report | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    return '\n'.join(lines)


# ===== 批量生成 =====
os.makedirs('data/reports', exist_ok=True)
generated = 0
for pid in sorted(patients.keys()):
    report = generate_report(pid)
    filepath = f'data/reports/{pid}_report.md'
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)
    generated += 1

print(f"✅ 生成 {generated} 份患者随访报告 → data/reports/")

# 验证
for pid in ['P005','P012','P029','P019']:
    size = os.path.getsize(f'data/reports/{pid}_report.md')
    lines = open(f'data/reports/{pid}_report.md', encoding='utf-8').read().count('\n')
    print(f"  {pid}: {size} bytes, {lines} 行")
