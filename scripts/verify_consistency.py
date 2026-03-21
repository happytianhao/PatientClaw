import csv, os, re
from datetime import datetime, timedelta
from collections import defaultdict

with open('data/patients.csv', newline='', encoding='utf-8') as f:
    patients = {r['patient_id']: r for r in csv.DictReader(f)}
with open('data/followups.csv', newline='', encoding='utf-8') as f:
    followups = list(csv.DictReader(f))

SYSTEM_DAY_START = datetime(2026, 3, 18)

def system_day(date_str):
    try:
        return (datetime.strptime(date_str, '%Y-%m-%d') - SYSTEM_DAY_START).days + 1
    except:
        return None

for f in followups:
    f['day_sent'] = system_day(f['scheduled_time'])
    f['day_reply'] = system_day(f['reply_time']) if f['reply_time'] else None

dedup_days = defaultdict(set)
for f in followups:
    for d in [f['day_sent'], f['day_reply']]:
        if d and 1 <= d <= 10:
            dedup_days[d].add(f['followup_id'])

issues = []
all_ok = True

print('=' * 50)
print('[1] 日报随访计数')
for d in range(1, 11):
    dedup = len(dedup_days[d])
    with open(f'data/reports/daily_report_day{d:02d}.md') as fh:
        content = fh.read()
    m = re.search(r'今日随访更新：(\d+)人', content)
    n_report = int(m.group(1)) if m else None
    ok = (n_report == dedup)
    if not ok: all_ok = False
    mark = 'OK' if ok else f'EXPECTED={dedup}'
    print(f'  Day{d:02d}: actual={dedup}, reported={n_report} {mark}')

print()
print('[2] 30份患者报告随访天数')
for pid in sorted(patients.keys()):
    actual = set(int(f['followup_day']) for f in followups if f['patient_id'] == pid)
    path = f'data/reports/{pid}_report.md'
    if not os.path.exists(path):
        issues.append(f'MISSING: {pid}'); continue
    content = open(path, encoding='utf-8').read()
    in_report = set(int(x) for x in re.findall(r'第(\d+)天', content))
    if in_report != actual:
        all_ok = False
        issues.append(f'  {pid}: report={sorted(in_report)}, actual={sorted(actual)}')
if not issues:
    print('  ALL OK - all 30 reports match followups.csv')
else:
    print('  ISSUES: ' + str(issues[:5]))

print()
print('[3] 回复时机（第八章）')
for pid in sorted(patients.keys()):
    path = f'data/reports/{pid}_report.md'
    if not os.path.exists(path): continue
    content = open(path, encoding='utf-8').read()
    idx = content.find('## 八、回复规律分析')
    if idx < 0: continue
    ch8 = content[idx:idx+1000]
    for label, dtype in [
        ('本轮回复（当天）', 'same'),
        ('次轮回复（延迟1天）', 'next'),
        ('较晚回复（延迟2天）', 'later'),
        ('未回复', 'no_reply')
    ]:
        m = re.search(label + r'\s+\|\s+(\d+)', ch8)
        if m:
            n_rpt = int(m.group(1))
            n_act = sum(1 for f in followups if f['patient_id']==pid and f['reply_delay_type']==dtype)
            if n_rpt != n_act:
                all_ok = False
                issues.append(f'  {pid} {label}: report={n_rpt}, actual={n_act}')

print()
print('[4] patients.csv字段')
ec_empty = [pid for pid,r in patients.items() if not r.get('emergency_contact') or r['emergency_contact']=='无']
allg_bad = [pid for pid,r in patients.items() if r.get('allergies','无') != '无']
print(f'  emergency_contact empty: {len(ec_empty)} {"" if not ec_empty else "ERROR: "+str(ec_empty[:3])}')
print(f'  allergies wrong: {len(allg_bad)} {"" if not allg_bad else "ERROR"}')
if ec_empty or allg_bad: all_ok = False

print()
print('=' * 50)
if all_ok and not issues:
    print('ALL CHECKS PASSED - data is fully consistent')
else:
    print(f'ISSUES FOUND ({len(issues)}):')
    for i in issues[:20]:
        print('  ' + str(i))
