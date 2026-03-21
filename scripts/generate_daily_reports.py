"""
PatientClaw 增强版医生日报生成器
覆盖：10天（系统第1-10天），含优先级/病情恶化/患者提问/用药效果/闭环建议
"""
import csv, os
from collections import defaultdict
from datetime import datetime, timedelta

# ===== 数据读取 =====
patients = {}
with open('data/patients.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        patients[row['patient_id']] = row

visits_all = []
with open('data/visits.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        visits_all.append(row)

rx_by_visit = {}
with open('data/prescriptions.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        vid = row['visit_id']
        if vid not in rx_by_visit:
            rx_by_visit[vid] = []
        rx_by_visit[vid].append(row)

followups_all = []
with open('data/followups.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        followups_all.append(row)

# ===== 系统时间轴：第1天=2026-03-18 … 第10天=2026-03-27 =====
SYSTEM_DAY_START = datetime(2026, 3, 18)

def system_day(date_str):
    """将日历日期转系统天数(1-based)，超出范围返回None"""
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d')
        return (d - SYSTEM_DAY_START).days + 1
    except:
        return None

# ===== 分配followup到各系统天 =====
# followup.scheduled_time 是随访发出的日期
# followup.reply_time 是患者回复的日期
# 两者都可能落在系统某一天

# 为每条followup计算对应的系统天
for f in followups_all:
    f['day_sent'] = system_day(f['scheduled_time'])
    if f['reply_time']:
        f['day_reply'] = system_day(f['reply_time'])
    else:
        f['day_reply'] = None

# ===== 按系统天分组 =====
# 语义：
#   sent     = 该天发出的随访（每条followup只出现在其发出日）
#   replied  = 该天收到的回复（每条followup只出现在其回复日）
#   urgent/attention/normal = 当天所有相关随访的优先级分类
days_data = defaultdict(lambda: {
    'sent': [],
    'replied': [],
    'urgent': [],
    'attention': [],
    'normal': [],
})

for f in followups_all:
    # 发出日
    if f['day_sent'] and 1 <= f['day_sent'] <= 10:
        d = f['day_sent']
        days_data[d]['sent'].append(f)
        if f['priority_level'] == 'urgent':
            days_data[d]['urgent'].append(f)
        elif f['priority_level'] == 'attention':
            days_data[d]['attention'].append(f)
        else:
            days_data[d]['normal'].append(f)
    # 回复日（仅当与发出日不同）
    if f['day_reply'] and 1 <= f['day_reply'] <= 10 and f['day_reply'] != f['day_sent'] and f['reply_received']:
        d = f['day_reply']
        days_data[d]['replied'].append(f)
        # 优先级不重复计入（沿用发出日的分类）

# ===== 统计每种药的效果（跨所有followup） =====
# 建立患者→最新随访映射
latest_fu = {}
for f in followups_all:
    pid = f['patient_id']
    day = int(f['followup_day'])
    if pid not in latest_fu or day > int(latest_fu[pid]['followup_day']):
        latest_fu[pid] = f

# 药物-效果映射
med_effects = defaultdict(lambda: {'users': [], 'improved': 0, 'stable': 0, 'worsened': 0, 'adherence_good': 0, 'adherence_partial': 0, 'adverse': 0})

# 简化识别每条followup涉及的药物
MED_KEYWORDS = {
    '沙库巴曲缬沙坦': ['沙库巴曲缬沙坦', '诺欣妥'],
    '利伐沙班': ['利伐沙班'],
    '阿司匹林': ['阿司匹林'],
    '氨氯地平': ['氨氯地平'],
    '缬沙坦': ['缬沙坦'],
    '比索洛尔': ['比索洛尔', '康忻', '博苏'],
    '螺内酯': ['螺内酯'],
    '达格列净': ['达格列净', '安达唐'],
    '呋塞米': ['呋塞米', '速尿'],
    '胺碘酮': ['胺碘酮'],
    '二甲双胍': ['二甲双胍'],
    '他汀类': ['阿托伐他汀', '瑞舒伐他汀', '匹伐他汀', '立普妥'],
    '地高辛': ['地高辛'],
    '贝那普利': ['贝那普利'],
    '培哚普利': ['培哚普利'],
    '托拉塞米': ['托拉塞米'],
    '卡维地洛': ['卡维地洛'],
    '地尔硫卓': ['地尔硫卓'],
}

def detect_meds(f):
    """从消息和诊断中识别涉及的药物"""
    text = f.get('message_sent', '') + ' ' + f.get('reply_received', '')
    found = set()
    for med_name, keywords in MED_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                found.add(med_name)
                break
    return found

# 计算各药效果
for pid, f in latest_fu.items():
    meds = detect_meds(f)
    for med in meds:
        me = med_effects[med]
        me['users'].append(pid)
        if f['condition_status'] == 'improved':
            me['improved'] += 1
        elif f['condition_status'] == 'worsened':
            me['worsened'] += 1
        else:
            me['stable'] += 1
        if f['medication_adherence'] == 'good':
            me['adherence_good'] += 1
        elif f['medication_adherence'] in ('partial', 'none'):
            me['adherence_partial'] += 1
        if f['adverse_reaction']:
            me['adverse'] += 1

# ===== 患者所有随访汇总（用于判断累计状态）=====
patient_all_fu = defaultdict(list)
for f in followups_all:
    patient_all_fu[f['patient_id']].append(f)
for pid in patient_all_fu:
    patient_all_fu[pid].sort(key=lambda x: int(x['followup_day']))

# ===== 收集所有患者提问 =====
all_questions = []
for f in followups_all:
    reply = f.get('reply_received', '')
    if '请问' in reply and '李主任' in reply:
        q_start = reply.find('请问')
        q_text = reply[q_start:].replace('请问李主任，', '').strip()
        q_text = q_text.rstrip('。').rstrip('？').rstrip(',')
        if q_text:
            all_questions.append({
                'pid': f['patient_id'],
                'day': f['followup_day'],
                'date': f['scheduled_time'],
                'reply_date': f['reply_time'],
                'question': q_text,
                'priority': f['priority_level'],
                'condition': f['condition_status'],
                'adherence': f['medication_adherence'],
            })

# ===== 辅助函数 =====
def p_icon(p):
    return {'urgent': '🔴', 'attention': '🟡', 'normal': '⚪'}.get(p, '⚪')

def c_icon(c):
    return {'improved': '📈', 'stable': '➡️', 'unchanged': '—', 'worsened': '📉', 'recovered': '★'}.get(c, '?')

def a_icon(a):
    return {'good': '✅', 'partial': '⚠️', 'none': '❌', 'unknown': '？'}.get(a, '?')

def d_icon(d):
    return {'same': '⚡', 'next': '⏳', 'later': '🐢', 'no_reply': '❌'}.get(d, '?')

def priority_of_question(q):
    """判断患者问题的重要性"""
    urgent_keywords = ['严重', '立即', '急诊', '危险', '快死了', '不行了', '很难受']
    attention_keywords = ['加量', '停药', '换药', '要不要', '需要加', '需要换', '好了吗']
    # 病情加重+提问 = 高优先级
    if q['condition'] == 'worsened':
        return 'high'
    if q['priority'] == 'attention':
        return 'medium'
    if any(kw in q['question'] for kw in urgent_keywords):
        return 'high'
    if any(kw in q['question'] for kw in attention_keywords):
        return 'medium'
    return 'low'

def day_date(day_num):
    return (SYSTEM_DAY_START + timedelta(days=day_num - 1)).strftime('%Y-%m-%d')

def question_tag(q):
    tag = priority_of_question(q)
    return {'high': '🔴需立即回复', 'medium': '🟡建议回复', 'low': '⚪无需回复'}[tag]

# ===== 生成单日日报 =====
def generate_daily_report(day_num):
    dd = days_data[day_num]

    # 收集该天及之前的累计数据（用于第八章表格）
    cumulative = {'urgent': [], 'attention': [], 'normal': [], 'questions': []}
    seen_fids = set()
    for d in range(1, day_num + 1):
        for f in days_data[d]['sent']:
            if f['followup_id'] in seen_fids:
                continue
            seen_fids.add(f['followup_id'])
            if f['priority_level'] == 'urgent':
                cumulative['urgent'].append(f)
            elif f['priority_level'] == 'attention':
                cumulative['attention'].append(f)
            else:
                cumulative['normal'].append(f)

    # 累计患者提问（去重：同一患者+同一问题内容只出现一次）
    cum_questions = []
    seen_qkeys = set()
    for d in range(1, day_num + 1):
        for f in days_data[d]['sent']:
            reply = f.get('reply_received', '')
            if '请问' in reply and '李主任' in reply:
                q_start = reply.find('请问')
                q_text = reply[q_start:].replace('请问李主任，', '').strip()
                q_text = q_text.rstrip('。').rstrip('？').rstrip(',')
                if q_text:
                    qkey = (f['patient_id'], q_text)
                    if qkey not in seen_qkeys:
                        seen_qkeys.add(qkey)
                        cum_questions.append({
                            'pid': f['patient_id'],
                            'day': f['followup_day'],
                            'date': f['scheduled_time'],
                            'question': q_text,
                            'priority': f['priority_level'],
                            'condition': f['condition_status'],
                            'adherence': f['medication_adherence'],
                        })

    # 该天活跃随访（当天发出的）
    active = dd['sent']

    # ===== 按患者去重（每患者当天只出现一次，取病情最重的分类） =====
    # 优先级：worsened > attention_flag > improved > stable/unchanged
    # 分类：📉恶化 > 🟡关注 > 📈好转
    def classify_for_day(f):
        if f['condition_status'] == 'worsened':
            return 0  # 病情恶化（最高）
        elif f['reply_received'] and any(kw in f['reply_received'] for kw in ['漏', '没吃', '没服', '停了', '不良反应', '不舒服']):
            return 1  # 需持续关注（有依从/不良反应问题）
        elif f['condition_status'] == 'improved':
            return 2  # 病情好转
        elif f['condition_status'] == 'stable':
            return 3  # 病情稳定
        else:
            return 4  # 其他

    # 按患者分组，每患者取病情最重的那条followup
    pid_best = {}  # pid -> best followup for the day
    for f in active:
        pid = f['patient_id']
        if pid not in pid_best:
            pid_best[pid] = f
        else:
            if classify_for_day(f) < classify_for_day(pid_best[pid]):
                pid_best[pid] = f

    # 分三大类（互斥，每患者只出现一次）
    wors_pids = set(pid for pid, f in pid_best.items() if f['condition_status'] == 'worsened')
    attn_pids = set(pid for pid, f in pid_best.items()
                    if pid not in wors_pids and
                    f['reply_received'] and
                    any(kw in f['reply_received'] for kw in ['漏', '没吃', '没服', '停了', '不良反应', '不舒服']))
    imp_pids  = set(pid for pid, f in pid_best.items()
                    if pid not in wors_pids and pid not in attn_pids and
                    f['condition_status'] == 'improved')

    wors_list = [pid_best[pid] for pid in wors_pids]
    attn_list = [pid_best[pid] for pid in attn_pids]
    imp_list  = [pid_best[pid] for pid in imp_pids]

    # 用药依从性（独立分类，列出所有非good的患者，不重复展示完整回复）
    bad_adh_list = [f for f in active
                     if f['medication_adherence'] in ('partial', 'none', 'unknown') and
                     f['patient_id'] not in wors_pids]  # 已在📉出现过的不重复列

    # 未回复
    pending_list = [f for f in active if f['reply_delay_type'] == 'no_reply']

    lines = []
    report_date = day_date(day_num)
    n_active = len(active)
    n_total = len(patients)

    # === 头部 ===
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"PatientClaw 日报")
    lines.append(f"李晓峰主任医师 · {report_date}（系统第{day_num}天）")
    lines.append(f"今日随访更新：{n_active}人 · 在管患者总计：{n_total}人")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")

    # === 第一章：紧急关注 ===
    n_urg = len(dd['urgent'])
    lines.append(f"🔴 需立即处理（{n_urg}人）")
    lines.append("──────────────────────")
    if n_urg == 0:
        lines.append("今日无紧急患者，继续观察。")
    else:
        for f in dd['urgent']:
            pid = f['patient_id']
            p = patients[pid]
            cond_short = p['primary_condition'].split('）')[0].split('（')[0]
            lines.append(f"**{p['name']}（{pid}）** | {cond_short}")
            lines.append(f"  问题：{f['adverse_reaction'] or f['ai_summary']}")
            lines.append(f"  患者自述：{f['reply_received'][:80] if f['reply_received'] else '【未回复】'}")
            lines.append(f"  建议：立即电话联系，确认病情，考虑提前复诊或急诊评估")
            lines.append("")
    lines.append("")

    # === 第二章：病情恶化（每患者只出现一次）===
    lines.append(f"📉 病情恶化（{len(wors_list)}人）")
    lines.append("──────────────────────")
    if not wors_list:
        lines.append("今日无病情恶化患者。")
    else:
        for f in wors_list:
            pid = f['patient_id']
            p = patients[pid]
            lines.append(f"**{p['name']}（{pid}）** ⚠️")
            lines.append(f"  第{f['followup_day']}天 · {f['adverse_reaction'] or '病情加重'}")
            lines.append(f"  患者自述：{f['reply_received'][:100] if f['reply_received'] else '【未回复】'}")
            lines.append("")
    lines.append("")

    # === 第三章：需持续关注（每患者只出现一次）===
    lines.append(f"🟡 需持续关注（{len(attn_list)}人）")
    lines.append("──────────────────────")
    if not attn_list:
        lines.append("今日无需持续关注患者。")
    else:
        for f in attn_list:
            pid = f['patient_id']
            p = patients[pid]
            note = f['adverse_reaction'] if f['adverse_reaction'] else \
                   ('依从性问题' if f['medication_adherence'] in ('partial','none') else '需持续观察')
            lines.append(f"**{p['name']}（{pid}）** | {note}")
            reply_short = f['reply_received'][:60] if f['reply_received'] else '【未回复】'
            lines.append(f"  患者回复：{reply_short}")
            lines.append("")
    lines.append("")

    # === 第四章：病情好转（每患者只出现一次）===
    lines.append(f"📈 今日病情好转（{len(imp_list)}人）")
    lines.append("──────────────────────")
    if not imp_list:
        lines.append("今日无病情明显好转患者。")
    else:
        for f in imp_list:
            pid = f['patient_id']
            p = patients[pid]
            adh = a_icon(f['medication_adherence'])
            lines.append(f"**{p['name']}（{pid}）** {adh}")
            # 简洁病情描述
            reply_short = f['reply_received'][:60] if f['reply_received'] else ''
            lines.append(f"  第{f['followup_day']}天 · {reply_short}")
            lines.append("")
    lines.append("")

    # === 第五章：用药依从性（只列患者名，不重复完整回复）===
    all_bad = [f for f in active if f['medication_adherence'] in ('partial','none','unknown')]
    bad_unique = {}  # pid -> best followup
    for f in all_bad:
        pid = f['patient_id']
        if pid not in bad_unique:
            bad_unique[pid] = f
        elif f['medication_adherence'] == 'none':
            bad_unique[pid] = f  # 停药优先

    n_bad = len(bad_unique)
    lines.append(f"🍬 今日用药依从性")
    lines.append("──────────────────────")
    n_good = sum(1 for f in active if f['medication_adherence'] == 'good')
    lines.append(f"✅ 按时服药：{n_good}人 | ⚠️ 漏服/停药：{n_bad}人")
    lines.append("")
    if n_bad > 0:
        for pid, f in bad_unique.items():
            p = patients[pid]
            adh_val = f['medication_adherence']
            adh_note = {'partial': '部分漏服', 'none': '自行停药', 'unknown': '未确认'}.get(adh_val, '')
            # 一句话概括问题，不重复完整患者回复
            if f['reply_received']:
                short_reply = f['reply_received'][:40].replace('\n', ' ')
                snippet = f"（{short_reply}…）" if len(f['reply_received']) > 40 else f"（{short_reply}）"
            else:
                snippet = ""
            lines.append(f"  {p['name']}（{pid}）：{adh_note}{snippet}")
        lines.append("")
    lines.append("")

    # === 第六章：患者提问（按患者分组，同一患者多条问题合并一条） ===
    patient_questions = defaultdict(list)
    for q in cum_questions:
        patient_questions[q['pid']].append(q)

    lines.append(f"💬 患者提问汇总（共{len(cum_questions)}条，来自{len(patient_questions)}人）")
    lines.append("──────────────────────")

    if not cum_questions:
        lines.append("目前暂无患者提问。")
    else:
        def q_priority(pid):
            qs = patient_questions[pid]
            for q in qs:
                if priority_of_question(q) == 'high': return 'high'
            for q in qs:
                if priority_of_question(q) == 'medium': return 'medium'
            return 'low'

        def fmt_qs(pid):
            qs = patient_questions[pid]
            return ' | '.join(q['question'] for q in qs)

        all_pids = list(patient_questions.keys())
        high = sorted([p for p in all_pids if q_priority(p) == 'high'], key=lambda p: patient_questions[p][0]['date'])
        med  = sorted([p for p in all_pids if q_priority(p) == 'medium'], key=lambda p: patient_questions[p][0]['date'])
        low  = sorted([p for p in all_pids if q_priority(p) == 'low'], key=lambda p: patient_questions[p][0]['date'])

        if high:
            lines.append(f"🔴 需立即回复（{len(high)}人）— 今日电话回复")
            for pid in high:
                p = patients.get(pid, {})
                qs = patient_questions[pid]
                lines.append(f"  {p.get('name', pid)}（{pid}）")
                lines.append(f"    {fmt_qs(pid)}")
                lines.append(f"    病情{qs[0]['condition']} | {qs[0]['date']}")
                lines.append("")
        else:
            lines.append("🔴 需立即回复（0人）")

        if med:
            lines.append(f"🟡 建议回复（{len(med)}人）— 方便时回复")
            for pid in med:
                p = patients.get(pid, {})
                lines.append(f"  {p.get('name', pid)}（{pid}）：{fmt_qs(pid)}")
            lines.append("")

        if low:
            lines.append(f"⚪ 常规问答（{len(low)}人）— 下次复诊一并解答")
            for pid in low:
                p = patients.get(pid, {})
                lines.append(f"  {p.get('name', pid)}（{pid}）：{fmt_qs(pid)}")
            lines.append("")
    lines.append("")

    # === 第七章：未回复患者 ===
    n_pending = len(pending_list)
    lines.append(f"📭 未回复患者（{n_pending}人）")
    lines.append("──────────────────────")
    if n_pending == 0:
        lines.append("今日所有随访患者均已回复。")
    else:
        for f in pending_list:
            pid = f['patient_id']
            p = patients[pid]
            day_f = f['followup_day']
            lines.append(f"**{p['name']}（{pid}）** | {p['primary_condition'].split('）')[0].split('（')[0][:15] if '）' in p['primary_condition'] else p['primary_condition'][:15]}")
            lines.append(f"  第{day_f}天随访未回复，建议电话跟进")
            lines.append("")
    lines.append("")

    # === 第八章：累计在管患者状态 ===
    lines.append(f"📋 累计在管患者状态（系统第{day_num}天）")
    lines.append("──────────────────────")

    # 按最新随访的priority分类
    all_active_pids = set()
    for d in range(1, day_num + 1):
        for f in days_data[d]['sent']:
            all_active_pids.add(f['patient_id'])

    # 累计各优先级
    total_urgent = 0
    total_attention = 0
    total_normal = 0
    total_unreplied = 0

    pid_latest = {}
    for pid in all_active_pids:
        recs = patient_all_fu[pid]
        if recs:
            latest = max(recs, key=lambda x: int(x['followup_day']))
            pid_latest[pid] = latest

    for pid, latest in pid_latest.items():
        prio = latest['priority_level']
        if prio == 'urgent': total_urgent += 1
        elif prio == 'attention': total_attention += 1
        else: total_normal += 1
        if latest['reply_delay_type'] == 'no_reply': total_unreplied += 1

    lines.append(f"🔴 高风险：{total_urgent}人 | 🟡 中风险：{total_attention}人 | ⚪ 低风险：{total_normal}人 | 📭 未回复：{total_unreplied}人")
    lines.append("")

    # 简表
    lines.append(f"| 患者 | 诊断 | 最新状态 | 依从 | 优先级 |")
    lines.append(f"|------|------|---------|------|--------|")
    for pid in sorted(pid_latest.keys()):
        latest = pid_latest[pid]
        p = patients[pid]
        pname = p['name']
        diag = p['primary_condition'].split('）')[0].split('（')[0][:10]
        cond = c_icon(latest['condition_status'])
        adh = {'good':'✅','partial':'⚠️','none':'❌','unknown':'？'}.get(latest['medication_adherence'],'?')
        prio_icon = {'urgent':'🔴','attention':'🟡','normal':'⚪'}.get(latest['priority_level'],'⚪')
        lines.append(f"| {pname} | {diag} | {cond} | {adh} | {prio_icon} |")
    lines.append("")

    # === 第九章：用药方案效果统计 ===
    lines.append("📊 用药方案效果统计（累计）")
    lines.append("──────────────────────")
    if med_effects:
        lines.append(f"| 药物 | 使用患者 | 改善率 | 稳定率 | 恶化率 | 依从率 | 不良反应 | 评估 |")
        lines.append(f"|------|---------|--------|--------|--------|--------|---------|------|")
        for med, me in sorted(med_effects.items(), key=lambda x: -len(x[1]['users'])):
            n_users = len(me['users'])
            if n_users == 0:
                continue
            imp_rate = round(100 * me['improved'] / n_users)
            stab_rate = round(100 * me['stable'] / n_users)
            wors_rate = round(100 * me['worsened'] / n_users)
            adh_rate = round(100 * me['adherence_good'] / n_users)
            adv_rate = round(100 * me['adverse'] / n_users)

            # 评估标签
            if imp_rate >= 70 and adv_rate < 10:
                eval_tag = '✅ 推荐'
            elif imp_rate >= 50 and adv_rate < 20:
                eval_tag = '🟡 可用'
            elif adv_rate >= 20:
                eval_tag = '⚠️ 关注不良反应'
            elif wors_rate >= 20:
                eval_tag = '❓ 需关注'
            else:
                eval_tag = '➡️ 观察中'
            lines.append(f"| {med} | {n_users}人 | {imp_rate}% | {stab_rate}% | {wors_rate}% | {adh_rate}% | {adv_rate}% | {eval_tag} |")
        lines.append("")
    else:
        lines.append("暂无足够的用药效果数据。")
        lines.append("")

    # === 第十章：今日洞察与闭环建议 ===
    lines.append("💡 今日洞察与闭环建议")
    lines.append("──────────────────────")

    insights = []

    # 1. 紧急情况
    high_qs = [q for q in cum_questions if priority_of_question(q) == 'high']
    if wors_list:
        for f in wors_list:
            pid = f['patient_id']
            p = patients[pid]
            diag = p['primary_condition'].split('）')[0].split('（')[0][:15]
            insights.append(f"⚠️ {p['name']}（{diag}）：病情加重，{f['adverse_reaction'] or '需评估调整方案'}。")
    if high_qs:
        insights.append(f"🔴 今日{len(high_qs)}条紧急提问需优先电话回复。")
    if total_unreplied > 0:
        insights.append(f"📭 {total_unreplied}名患者随访未回复，建议电话跟进确认安全。")

    # 2. 用药综合洞察（不按药逐条列，只综合分析）
    if med_effects:
        good_meds = []      # 推荐：改善率高+无不良反应
        watch_meds = []      # 关注：有用药问题
        for med, me in med_effects.items():
            n = len(me['users'])
            if n < 2:
                continue
            imp_rate = 100 * me['improved'] / n
            adv_rate = 100 * me['adverse'] / n
            adh_rate = 100 * me['adherence_good'] / n
            if adv_rate >= 20:
                watch_meds.append(f"{med}({me['adverse']}例不良反应/{n}人，{adv_rate:.0f}%)")
            elif adh_rate < 60:
                watch_meds.append(f"{med}(依从率{adh_rate:.0f}%，需加强用药教育)")
            elif imp_rate >= 70 and adv_rate < 10:
                good_meds.append(med)
        if good_meds:
            insights.append(f"✅ 本组核心用药（{','.join(good_meds)}）改善率均超70%且无不良反应，建议继续规范使用。")
        for w in watch_meds:
            insights.append(f"⚠️ {w}，建议评估是否调整剂量或换药。")

    # 3. 心衰GDMT方案汇总
    hf_meds = ['沙库巴曲缬沙坦', '螺内酯', '达格列净', '呋塞米', '卡维地洛']
    hf_users = {}
    for med in hf_meds:
        if med in med_effects:
            hf_users[med] = med_effects[med]
    if len(hf_users) >= 3:
        hf_names = list(hf_users.keys())
        insights.append(f"❤️ 心衰GDMT方案（{','.join(hf_names)}）本组应用效果良好，建议继续滴定至最大耐受剂量。")

    # 4. 依从性问题汇总（跨患者）
    bad_adh_pids = [pid for pid in bad_unique.keys()]
    if len(bad_adh_pids) >= 2:
        names = [patients[pid]['name'] for pid in bad_adh_pids[:3]]
        insights.append(f"🍬 本日{len(bad_adh_pids)}名患者存在漏服/停药问题（{'、'.join(names)}等），建议加强随访宣教。")

    if not insights:
        insights.append("今日整体状况稳定，继续按当前方案管理。")

    for ins in insights:
        lines.append(f"· {ins}")
    lines.append("")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return '\n'.join(lines)


# ===== 批量生成10天日报 =====
os.makedirs('data/reports', exist_ok=True)
for day in range(1, 11):
    report = generate_daily_report(day)
    filename = f"data/reports/daily_report_day{day:02d}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ 第{day}天日报 → {filename}")

print("\n全部10天日报生成完毕！")
