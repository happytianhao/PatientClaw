"""
生成 PatientClaw 随访记录
用法: python3 generate_followups.py
"""
import csv
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

# 构建每个患者数据
patient_data = {}
for v in visits_all:
    pid = v['patient_id']
    if pid not in patient_data:
        patient_data[pid] = {'visits': []}
    patient_data[pid]['visits'].append(v)

for pid, data in patient_data.items():
    data['visits'] = sorted(data['visits'], key=lambda x: (int(x['visit_num']), x['visit_date']))
    data['current_meds'] = []
    for v in reversed(data['visits']):
        vid = v['visit_id']
        if vid in rx_by_visit and rx_by_visit[vid]:
            data['current_meds'] = rx_by_visit[vid]
            break

# ===== 个性化随访频率 =====
FREQ = {
    'P005': [3, 5, 7, 14, 21],
    'P026': [3, 5, 7, 14, 21],
    'P029': [3, 5, 7, 14, 21],
    'P012': [3, 5, 7, 14, 21],
    'P017': [3, 5, 7, 14, 21],
    'P015': [3, 7, 14],
    'P016': [3, 7, 14],
    'P021': [3, 7, 14],
    'P025': [3, 7, 14],
    'P027': [3, 7, 14],
    'P028': [3, 7, 14],
    'P003': [3, 7, 14],
    'P014': [3, 7, 14],
    'P018': [3, 7, 14],
    'P019': [3, 7, 14],
    'P020': [3, 7, 14],
    'P001': [3, 7, 14],
    'P002': [3, 7, 14],
    'P004': [3, 7, 14],
    'P006': [3, 7, 14],
    'P007': [3, 7, 14],
    'P008': [3, 7, 14],
    'P009': [3, 7, 14],
    'P010': [3, 7, 14],
    'P011': [3, 7, 14],
    'P013': [3, 7, 14],
    'P022': [3, 7, 14],
    'P023': [3, 7, 14],
    'P024': [3, 7, 14],
    'P030': [3, 7, 14],
}

# ===== 辅助函数 =====
def get_meds_str(meds):
    return '、'.join([m['medication'] for m in meds])

def get_last_visit(pid):
    visits = patient_data[pid]['visits']
    return visits[-1]

def get_diagnosis(pid):
    return get_last_visit(pid)['diagnosis']

def get_notes(pid):
    return get_last_visit(pid)['notes']

def get_bp_hr(pid):
    v = get_last_visit(pid)
    return v['bp'], v['hr']

# ===== 随访消息模板函数 =====
def gen_msg(pid, day, meds_str, diag, notes_str, name, age, gender, prev_summary=''):
    """生成小龙虾随访消息"""
    # 高血压相关关键词
    hp_keywords = ['高血压', '血压', '高脂血症', '高胆固醇']
    cad_keywords = ['冠心病', '心绞痛', '支架', '心梗', '心肌梗死', '心梗后']
    hf_keywords = ['心力衰竭', '心衰', 'HFpEF', 'HFrEF', '心功能']
    af_keywords = ['心房颤动', '房颤', 'AF']
    dm_keywords = ['糖尿病', '血糖']
    stroke_keywords = ['脑梗死', '脑卒中', '偏瘫']
    sleep_keywords = ['睡眠呼吸', 'CPAP', '鼾声']
    vp_keywords = ['室性早搏', '室早']
    dcm_keywords = ['扩张型心肌病', 'ICD']
    fh_keywords = ['家族性高胆固醇', 'FH', '他汀']

    is_hp = any(k in diag for k in hp_keywords)
    is_cad = any(k in diag for k in cad_keywords)
    is_hf = any(k in diag for k in hf_keywords)
    is_af = any(k in diag for k in af_keywords)
    is_dm = any(k in diag for k in dm_keywords)
    is_stroke = any(k in diag for k in stroke_keywords)
    is_sleep = any(k in diag for k in sleep_keywords)
    is_vp = any(k in diag for k in vp_keywords)
    is_dcm = any(k in diag for k in dcm_keywords)
    is_fh = any(k in diag for k in fh_keywords)

    # 通用部分
    time_tip = {3: '3', 5: '5', 7: '7', 14: '两周', 21: '3周'}

    parts = [f"{name}您好！我是李晓峰主任诊室的随访助理小龙虾。"]

    if day == 3:
        parts.append(f"您就诊已满3天。")
        if meds_str:
            parts.append(f"请问{meds_str}是否已开始规律服用？")
        parts.append("有无头晕、乏力或其他不适？")
        if is_hf:
            parts.append("今日体重是多少？")
        if is_hp:
            parts.append("血压开始测了吗？")
        if is_cad:
            parts.append("有无胸闷胸痛？")
    elif day == 5:
        parts.append(f"您就诊已满5天，上次随访您状态不错。")
        if meds_str:
            parts.append(f"请问{meds_str}继续按时服用了吗？")
        if is_hf:
            parts.append("体重有没有变化？")
            parts.append("有没有气短或腿肿？")
        if is_hp:
            parts.append("血压这几天稳定吗？")
        if is_af:
            parts.append("心跳感觉规律吗？有没有心悸？")
        if is_cad:
            parts.append("有无胸痛发作？")
    elif day == 7:
        parts.append(f"您就诊已满一周。")
        if meds_str:
            parts.append(f"请问{meds_str}是否坚持每日服用？")
        if is_hf:
            parts.append("今日体重是多少？")
            parts.append("有无气短或双踝水肿？")
        elif is_hp:
            parts.append("血压近两日测了多少？")
        elif is_cad:
            parts.append("有无胸闷或胸痛发作？")
            parts.append("活动耐力如何？")
        elif is_af:
            parts.append("心悸感觉如何？")
            parts.append("有没有出血迹象（瘀青/牙龈出血）？")
        if is_dm:
            parts.append("血糖有没有监测？")
        if is_stroke:
            parts.append("头晕和步态怎么样？")
    elif day == 14:
        parts.append(f"您就诊已满两周，整体情况如何？")
        if meds_str:
            parts.append(f"请问{meds_str}是否坚持服用？")
        if is_hf:
            parts.append("体重稳定吗？")
            parts.append("活动耐力有没有改善？")
        elif is_hp:
            parts.append("血压这段时间控制得怎么样？")
        elif is_cad:
            parts.append("症状有没有改善？")
        if is_af:
            parts.append("心律控制得如何？")
        parts.append("您有什么想问医生或想告诉我们的吗？下次复诊时间您记得吗？")
    elif day == 21:
        parts.append(f"您就诊已满三周，这次随访情况如何？")
        if meds_str:
            parts.append(f"请问{meds_str}是否坚持服用？")
        if is_hf:
            parts.append("体重监测情况如何？")
            parts.append("心衰症状有没有进一步改善？")
        parts.append("您有什么不舒服想告诉医生，或者想问李主任什么问题吗？")

    parts.append("请简要回复，感谢配合，祝您健康！")
    return ''.join(parts)


def gen_reply(pid, day, meds_str, diag, bp, hr, name, gender, prev_summary=''):
    """生成患者回复（含提问）"""
    is_hf = any(k in diag for k in ['心力衰竭', '心衰', 'HFpEF', 'HFrEF', '心功能'])
    is_hp = any(k in diag for k in ['高血压'])
    is_cad = any(k in diag for k in ['冠心病', '心绞痛', '支架', '心梗'])
    is_af = any(k in diag for k in ['心房颤动', '房颤'])
    is_dm = any(k in diag for k in ['糖尿病', '血糖'])
    is_stroke = any(k in diag for k in ['脑梗死', '脑卒中'])
    is_sleep = any(k in diag for k in ['睡眠呼吸', 'CPAP'])
    is_vp = any(k in diag for k in ['室性早搏', '室早'])
    is_dcm = any(k in diag for k in ['扩张型心肌病', 'ICD'])

    pronoun = '他' if gender == '男' else '她'

    # 随时间变化的病情状态
    if day == 3:
        replies_3 = {
            'P005': ('三种药都在吃，今天体重62.8kg，血压126/80，没有气短，腿不肿。', 'same'),
            'P026': ('四种药都在吃，体重58.2kg，血压126/80，没有气短，感觉比刚出院好多了。', 'same'),
            'P029': ('四种药都在吃，今天体重78.5kg，血压124/80，气短比之前好一些，腿肿也轻了。', 'same'),
            'P012': ('地尔硫卓和利伐沙班都在吃，没有出血，血压136/84，就是最近有点乏力。', 'same'),
            'P017': ('利伐沙班和地高辛都在吃，没有出血，心跳感觉还可以，血压134/82。', 'same'),
            'P015': ('三种药都在吃，今天体重68.2kg，血压128/80，没有气短，脚也不肿。', 'same'),
            'P016': ('四种药都在吃，今天体重71.8kg，血压130/84，没有气短，腿不肿。', 'same'),
            'P021': ('四种药都在吃，今天体重58.5kg，血压128/82，没有气短，脚不肿。', 'same'),
            'P025': ('四种药都在吃，今天体重72.3kg，血压132/84，没有气短，腿不肿。', 'same'),
            'P027': ('四种药都在吃，今天体重74.2kg，血压130/82，没有气短，腿不肿。', 'same'),
            'P028': ('四种药都在吃，今天体重62.0kg，血压124/78，没有气短，ICD没有放电。', 'same'),
            'P003': ('三种药都在吃，血压130/82，没有胸闷，感觉还好。', 'same'),
            'P014': ('四种药都在吃，血压126/80，心率72，没有胸闷，感觉挺好的。', 'same'),
            'P018': ('五种药都在吃，没有胸痛，走路也没问题，感觉比之前好一些。', 'same'),
            'P019': ('阿司匹林每天吃，没有胸闷，血压130/80，感觉挺好的。', 'same'),
            'P020': ('药都在吃，血压130/80，没有气短胸痛，感觉挺好的。', 'same'),
            'P001': ('三种药都在吃，血压128/82，没有头晕，感觉还好。', 'same'),
            'P002': ('两种药都在吃，血压128/80，没有不舒服，状态不错。', 'same'),
            'P004': ('两种药都在吃，血压128/80，没有肌肉痛，感觉挺好的。', 'same'),
            'P006': ('缬沙坦每天吃，血压130/82，没有头晕，感觉还好。', 'same'),
            'P007': ('三种药都在吃，血压132/82，血糖6.1，没有不舒服。', 'same'),
            'P008': ('氨氯地平每天吃，血压130/82，没有头晕，感觉挺好的。', 'same'),
            'P009': ('三种药都在吃，血压130/80，头晕好多了，走路也比以前稳。', 'same'),
            'P010': ('比索洛尔每天吃，血压130/84，心率76，焦虑好多了。', 'same'),
            'P011': ('两种药都在吃，血压128/80，没有肌肉痛，感觉挺好的。', 'same'),
            'P013': ('氨氯地平每天吃，血压138/86，CPAP也在用，头痛少多了。', 'same'),
            'P022': ('三种药都在吃，没有心悸，血压132/82，感觉挺好的。', 'same'),
            'P023': ('四种药都在吃，心跳感觉平稳，没有出血，血压126/80。', 'same'),
            'P024': ('比索洛尔在吃，心悸感觉少多了，没有头晕，感觉还好。', 'same'),
            'P030': ('三种药都在吃，今天测了LDL 2.0，血压124/80，没有不舒服。', 'same'),
        }
        if pid in replies_3:
            reply_text, timing = replies_3[pid]
        else:
            reply_text, timing = (f'{meds_str}都在吃，状态还可以。', 'same')

        # 患者提问
        questions = {
            'P005': '请问陈医生，我现在能开始做一点轻微运动了吗？',
            'P026': '李主任，请问我现在可以进行快走运动了吗？',
            'P029': '邓医生，请问这种情况还能恢复到什么程度？',
            'P012': '马医生，这个乏力是不是肾的问题？需要复查吗？',
            'P017': '方医生，我想问一下，现在可以喝点酒吗？',
            'P015': '韩医生，请问我可以出去旅游吗？',
            'P016': '彭医生，我以后还能正常工作吗？',
            'P021': '张医生，请问我这种情况可以爬楼梯吗？',
            'P025': '郭医生，我的心率偏快正常吗？',
            'P027': '曹医生，我现在可以喝点酒了吗？',
            'P028': '许医生，我想问ICD需要定期检查吗？',
            'P003': '张医生，我以后还能坐飞机吗？',
            'P014': '罗医生，请问我以后还能开车吗？',
            'P018': '邵医生，我现在可以喝酒吗？',
            'P019': '段医生，我现在可以喝点酒吗？',
            'P020': '汤医生，请问我需要多久复查一次心脏？',
            'P001': '王医生，请问我可以吃咸一点吗？',
            'P002': '李医生，糖尿病饮食太严格了，可以稍微放宽一点吗？',
            'P004': '刘医生，请问他汀要吃多久？',
            'P006': '杨医生，缬沙坦要吃多久？',
            'P007': '赵医生，请问我需要忌口吗？',
            'P008': '黄医生，请问我可以喝咖啡吗？',
            'P009': '周医生，请问我以后还能开车吗？',
            'P010': '吴医生，焦虑症还需要继续看心理科吗？',
            'P011': '徐医生，匹伐他汀要吃多久？',
            'P013': '胡医生，CPAP呼吸机要戴多久？',
            'P022': '徐医生，请问胺碘酮吃多久可以停？',
            'P023': '孙医生，请问我能喝咖啡吗？',
            'P024': '胡医生，室早能完全消失吗？',
            'P030': '江医生，依折麦布要长期吃吗？PCSK9抑制剂要打多久？',
        }
        q = questions.get(pid, f'请问{name}医生，这些药要长期吃吗？')
        reply_text = reply_text + f' 还有个问题想问：我{q}'

    elif day == 5:
        replies_5 = {
            'P005': ('三种药都在吃，体重62.5kg稳定，血压124/78，没有气短，感觉还好。', 'same'),
            'P026': ('四种药都在吃，今天体重58.0kg，血压124/78，没有气短，比上周好。', 'same'),
            'P029': ('四种药都在吃，今天体重78.8kg，血压122/80，气短减轻了一些，腿肿也轻了。', 'same'),
            'P012': ('地尔硫卓和利伐沙班都在吃，血压132/84，乏力的感觉轻了一些，没有出血。', 'same'),
            'P017': ('利伐沙班和地高辛都在吃，心跳感觉规律了，血压130/82，没有出血。', 'same'),
        }
        if pid in replies_5:
            reply_text, timing = replies_5[pid]
        else:
            reply_text, timing = (f'药都在吃，状态稳定。', 'same')

        questions = {
            'P005': '请问陈医生，体重稳定的话利尿剂可以减量吗？',
            'P026': '请问李主任，我的心率70左右是不是偏慢了？',
            'P029': '邓医生，请问这种情况还能恢复到什么程度？',
            'P012': '马医生，请问这个利伐沙班剂量需要调整吗？',
            'P017': '方医生，我的心率72bpm是不是偏慢了？',
        }
        q = questions.get(pid, f'请问{name}医生，最近状态还好，有什么需要注意的吗？')
        reply_text = reply_text + f' 还有个问题想问：我{q}'

    elif day == 7:
        replies_7 = {
            'P005': ('四种药都在吃，今天体重62.5kg，血压126/78，没有气短，走路轻松多了，感觉比上周好。', 'same'),
            'P026': ('四种药都在吃，今天体重57.8kg，血压124/78，没有气短，腿不肿，感觉比上周好，走路也轻松了。', 'same'),
            'P029': ('四种药都在吃，今天体重78.5kg，血压122/80，气短比上周好一些，腿肿也轻了，就是走路还是有点费劲。', 'same'),
            'P012': ('地尔硫卓和利伐沙班都在吃，心跳感觉好多了，血压130/82，没有出血，乏力减轻了一些。', 'same'),
            'P017': ('利伐沙班和地高辛都在吃，心跳感觉平稳了，血压130/82，没有出血，感觉比上周好多了。', 'same'),
            'P015': ('三种药都在吃，今天体重68.0kg，血压126/80，没有气短，脚不肿，感觉挺好的。', 'same'),
            'P016': ('四种药都在吃，今天体重71.5kg，血压128/82，没有气短，腿也不肿，感觉比上周好多了。', 'same'),
            'P021': ('四种药都在吃，今天体重58.2kg，血压126/80，没有气短，腿不肿，感觉比上周还好，走路轻松多了。', 'same'),
            'P025': ('四种药都在吃，今天体重72.0kg，血压130/82，心率80，没有气短，腿不肿，感觉比上周好一些。', 'same'),
            'P027': ('四种药都在吃，今天体重74.0kg，血压130/82，没有气短，腿不肿，感觉还好。', 'same'),
            'P028': ('四种药都在吃，今天体重61.8kg，血压124/78，没有气短，ICD没有放电，感觉挺好的。', 'same'),
            'P003': ('三种药都在吃，血压126/80，心率72，没有胸闷，走路也没问题，感觉比上周好多了。', 'same'),
            'P014': ('四种药都在吃，血压126/80，心率70，没有胸闷，感觉挺好的，上周也没有胸痛。', 'same'),
            'P018': ('五种药都在吃，这周没有胸痛，走路上楼都没问题，血压128/80，感觉比以前好多了。', 'same'),
            'P019': ('阿司匹林每天吃，没有胸闷，血压128/80，感觉挺好的。', 'same'),
            'P020': ('药都在吃，血压128/80，没有气短胸痛，走路有劲，感觉挺好的。', 'same'),
            'P001': ('三种药一直在吃，血压128/80，没有头晕，感觉很好，比刚吃药时好多了。', 'same'),
            'P002': ('两种药都在吃，血压126/80，血糖6.0，没有不舒服，感觉挺好的。', 'same'),
            'P004': ('两种药都在吃，血压126/78，没有肌肉痛，血脂应该降了一些，感觉挺好的。', 'same'),
            'P006': ('缬沙坦每天都吃，血压128/82，没有头晕，感觉很好，比刚开始吃药时好多了。', 'same'),
            'P007': ('三种药一直在吃，血压132/82，血糖6.0，没有肌肉痛，胃也没有不舒服，感觉挺好的。', 'same'),
            'P008': ('氨氯地平每天都吃，血压128/80，没有头晕，感觉很好，比刚开始吃药时好多了。', 'same'),
            'P009': ('三种药一直在吃，血压128/80，头晕完全没有了，走路比以前稳多了，感觉很好。', 'same'),
            'P010': ('比索洛尔每天都吃，血压126/80，心率72，焦虑好多了，睡眠也好转了，头痛完全没有了。', 'same'),
            'P011': ('两种药都在吃，血压128/78，没有肌肉痛，感觉挺好的，比之前精神多了。', 'same'),
            'P013': ('氨氯地平每天吃，血压136/86，CPAP也在用，现在已经习惯了，头痛基本没有了。', 'same'),
            'P022': ('三种药都在吃，这周没有心悸，血压130/82，感觉挺好的。上次没看到消息抱歉了。', 'next'),
            'P023': ('四种药都在吃，心跳平稳，没有心悸，也没有出血，血压126/80，心率76，感觉挺好的。', 'same'),
            'P024': ('比索洛尔每天吃，心悸基本消失了，偶尔有一点点，但比刚开始好很多，没有头晕。', 'same'),
            'P030': ('三种药都在吃，LDL降到了2.1，血压122/78，没有不舒服，感觉在慢慢好转。', 'same'),
        }
        if pid in replies_7:
            reply_text, timing = replies_7[pid]
        else:
            reply_text, timing = (f'{meds_str}都在吃，状态稳定，感觉还好。', 'same')

        questions = {
            'P005': '请问陈医生，我现在可以坐飞机吗？',
            'P026': '请问李主任，我的心率56bpm是不是偏慢了？需要减药吗？',
            'P029': '邓医生，我现在走路还是有点喘，还能恢复到什么程度？',
            'P012': '马医生，我的肌酐有点高，这个利伐沙班需要换药吗？',
            'P017': '方医生，我现在心率70bpm感觉正好，还需要调整吗？',
            'P015': '韩医生，我什么时候可以恢复工作？',
            'P016': '彭医生，我现在可以开车吗？',
            'P021': '张医生，我的心率偏快正常吗？',
            'P025': '郭医生，请问我可以喝咖啡吗？',
            'P027': '曹医生，我现在可以出去旅游吗？',
            'P028': '许医生，ICD需要定期检查吗？',
            'P003': '张医生，我以后还能坐飞机吗？',
            'P014': '罗医生，请问我什么时候可以减药？',
            'P018': '邵医生，我现在可以喝酒吗？',
            'P019': '段医生，我现在可以喝点酒吗？',
            'P020': '汤医生，请问我需要多久复查一次心脏？',
            'P001': '王医生，请问可以稍微多吃点盐吗？',
            'P002': '李医生，糖尿病饮食可以稍微放宽一点吗？',
            'P004': '刘医生，请问瑞舒伐他汀要吃多久？',
            'P006': '杨医生，血压稳定了可以减药吗？',
            'P007': '赵医生，请问我可以吃柚子吗？',
            'P008': '黄医生，请问我可以喝咖啡吗？',
            'P009': '周医生，请问我以后还能开车吗？',
            'P010': '吴医生，焦虑症还需要继续看心理科吗？',
            'P011': '徐医生，匹伐他汀要长期吃吗？',
            'P013': '胡医生，CPAP呼吸机要戴多久？',
            'P022': '徐医生，胺碘酮要长期吃吗？可以考虑消融手术吗？',
            'P023': '孙医生，达比加群需要和餐一起吃吗？',
            'P024': '胡医生，室早能完全消失吗？',
            'P030': '江医生，依洛尤单抗要打多久？可以停吗？',
        }
        q = questions.get(pid, f'请问{name}医生，这些药要长期吃吗？下次复诊是什么时候？')
        reply_text = reply_text + f' 还有个问题想问：我{q}'

    elif day == 14:
        replies_14 = {
            'P005': ('四种药一直在吃，今天体重62.5kg，血压126/78，没有气短，现在能爬三层楼不喘了，感觉比刚来看病时好太多了。', 'same'),
            'P026': ('四种药一直在吃，今天体重57.5kg，血压122/76，没有气短，腿不肿，现在能走路半小时不喘，感觉和正常人差不多了，非常感谢李主任！', 'same'),
            'P029': ('四种药一直在吃，今天体重78.0kg，血压122/78，气短比之前明显好转，腿肿也轻了很多，可以走200米了，虽然还是有点费劲但比刚来时好多了。', 'same'),
            'P012': ('地尔硫卓和利伐沙班一直坚持吃，血压128/82，心悸基本没有，乏力的感觉也减轻了，没有出血，就是偶尔有点困倦。', 'same'),
            'P017': ('利伐沙班和地高辛一直坚持吃，心跳感觉平稳了，血压128/82，没有出血，感觉比两周前好多了。', 'same'),
            'P015': ('三种药一直在吃，今天体重68.0kg稳定，血压124/78，没有气短，脚不肿，感觉很好。', 'same'),
            'P016': ('四种药一直在吃，今天体重71.2kg稳定，血压126/80，没有气短，腿也不肿，感觉比刚来看病时好多了。', 'same'),
            'P021': ('四种药一直在吃，今天体重58.0kg稳定，血压124/78，没有气短，腿不肿，感觉比两周前好多了，走路轻松多了。', 'same'),
            'P025': ('四种药一直在吃，今天体重72.0kg稳定，血压128/82，心率76，没有气短，腿不肿，感觉比两周前好了一些。', 'same'),
            'P027': ('四种药一直在吃，今天体重74.0kg稳定，血压128/82，心率78，没有气短，腿不肿，感觉比两周前好多了。', 'same'),
            'P028': ('四种药一直在吃，今天体重61.5kg稳定，血压122/76，没有气短，ICD没有放电，感觉很好。', 'same'),
            'P003': ('三种药一直在吃，血压126/80，心率68，没有胸闷，走路爬楼都没问题，感觉很好，比刚来看病时好多了。', 'same'),
            'P014': ('四种药一直在吃，血压124/78，心率68，没有胸闷，走路也没问题，状态很好。', 'same'),
            'P018': ('五种药一直在吃，这两周没有胸痛，走路上楼都没问题，血压126/78，感觉比以前好多了。', 'same'),
            'P019': ('阿司匹林每天吃，没有胸闷，血压126/78，感觉挺好的，状态稳定。', 'same'),
            'P020': ('药一直在吃，血压124/78，没有气短胸痛，走路有劲，感觉挺好的，状态稳定。', 'same'),
            'P001': ('三种药一直在吃，血压128/80稳定，没有头晕，感觉很好，比刚吃药时好多了。', 'same'),
            'P002': ('两种药一直在吃，血压124/78，血糖6.0正常，没有不舒服，感觉很好。', 'same'),
            'P004': ('两种药一直在吃，血压124/76，没有肌肉痛，感觉很好，血脂也控制得不错。', 'same'),
            'P006': ('缬沙坦每天都在吃，血压126/80，没有头晕，感觉很好，比刚开始吃药时好多了。', 'same'),
            'P007': ('三种药一直在吃，血压130/80，血糖6.0，没有肌肉痛，感觉挺好的。', 'same'),
            'P008': ('氨氯地平每天都在吃，血压126/78，没有头晕，感觉很好，比刚吃药时好多了。', 'same'),
            'P009': ('三种药一直在吃，血压126/78，头晕完全消失了，走路比以前稳多了，感觉很好。', 'same'),
            'P010': ('比索洛尔每天都在吃，血压124/76，心率68，焦虑好多了，睡眠也好转了，头痛完全没有了，感觉比以前好太多了。', 'same'),
            'P011': ('两种药一直在吃，血压124/76，没有肌肉痛，感觉很好，比之前精神多了。', 'same'),
            'P013': ('氨氯地平每天吃，血压134/84，CPAP坚持用，头痛完全消失了，睡眠质量好多了，感觉比两周前好多了。', 'same'),
            'P022': ('三种药一直在吃，这两周没有心悸，血压126/78，心律感觉比之前规律，感觉好多了。上次消息没看到抱歉！', 'same'),
            'P023': ('四种药一直在吃，心跳平稳，没有心悸，没有出血，血压122/76，心率74，感觉挺好的。', 'same'),
            'P024': ('比索洛尔每天都在吃，室早基本消失了，偶尔有一点，血压122/76，没有头晕，感觉好多了。', 'same'),
            'P030': ('三种药一直在吃，LDL降到了1.9，血压120/76，没有不舒服，感觉非常好，感谢医生！', 'same'),
        }
        if pid in replies_14:
            reply_text, timing = replies_14[pid]
        else:
            reply_text, timing = (f'{meds_str}都在吃，状态稳定，感觉还好。', 'same')

        questions = {
            'P005': '请问陈医生，我现在可以恢复工作了吗？',
            'P026': '请问李主任，这种改善还能持续吗？需要加量吗？',
            'P029': '邓医生，我现在还能恢复到正常生活吗？',
            'P012': '马医生，请问我还需要加别的药吗？',
            'P017': '方医生，下次复诊是什么时候？',
            'P015': '韩医生，下次复诊是什么时候？',
            'P016': '彭医生，请问我什么时候可以恢复工作？',
            'P021': '张医生，请问我可以快走运动吗？',
            'P025': '郭医生，下次复诊是什么时候？',
            'P027': '曹医生，请问我可以快走运动吗？',
            'P028': '许医生，EF恢复到多少算正常？',
            'P003': '张医生，下次复诊是什么时候？',
            'P014': '罗医生，请问我可以喝酒吗？',
            'P018': '邵医生，请问我可以快走运动吗？',
            'P019': '段医生，下次复诊是什么时候？',
            'P020': '汤医生，请问我可以快走运动吗？',
            'P001': '王医生，请问可以稍微多吃点盐吗？',
            'P002': '李医生，请问我还需要继续看内分泌科吗？',
            'P004': '刘医生，请问我可以停药吗？',
            'P006': '杨医生，血压稳定了可以减药吗？',
            'P007': '赵医生，请问我还需要继续看内分泌科吗？',
            'P008': '黄医生，请问我可以喝咖啡吗？',
            'P009': '周医生，请问我以后还能开车吗？',
            'P010': '吴医生，焦虑症还需要继续看心理科吗？',
            'P011': '徐医生，LDL降到多少可以停药？',
            'P013': '胡医生，CPAP要戴多久？',
            'P022': '徐医生，胺碘酮要长期吃吗？可以考虑消融手术吗？',
            'P023': '孙医生，请问我可以喝咖啡吗？',
            'P024': '胡医生，室早能完全消失吗？',
            'P030': '江医生，请问我LDL降到多少可以减少用药？',
        }
        q = questions.get(pid, f'请问{name}医生，下次复诊是什么时候？这些药需要长期吃吗？')
        reply_text = reply_text + f' 还有个问题想问：我{q}'

    elif day == 21:
        replies_21 = {
            'P005': ('四种药一直在吃，今天体重62.2kg稳定，血压122/76，没有气短，走路很轻松，状态非常好，感谢李主任！', 'same'),
            'P026': ('四种药一直在吃，今天体重57.2kg稳定，血压120/74，没有气短，状态非常好，感谢李主任！', 'same'),
            'P029': ('四种药一直在吃，今天体重77.5kg，血压120/76，气短比上周又好转了一些，腿肿基本消失了，可以走300米了，比刚来时好多了。', 'same'),
            'P012': ('地尔硫卓和利伐沙班一直坚持吃，血压126/80，心率72，感觉很好，没有不舒服，状态稳定。', 'same'),
            'P017': ('利伐沙班和地高辛一直坚持吃，心跳感觉很规律，血压126/80，没有不舒服，状态稳定。', 'same'),
        }
        if pid in replies_21:
            reply_text, timing = replies_21[pid]
        else:
            reply_text, timing = (f'药都在吃，状态稳定，感觉还好。', 'same')

        questions = {
            'P005': '请问陈医生，我现在可以坐飞机吗？',
            'P026': '请问李主任，EF持续改善，请问沙库巴曲缬沙坦需要加量吗？',
            'P029': '邓医生，我现在走路能走300米了，还能更好吗？',
            'P012': '马医生，请问地尔硫卓需要调整剂量吗？',
            'P017': '方医生，请问我可以少量喝酒吗？',
        }
        q = questions.get(pid, f'请问{name}医生，这些药要长期吃吗？')
        reply_text = reply_text + f' 还有个问题想问：我{q}'

    else:
        reply_text = f'{meds_str}都在吃，状态还可以。'
        timing = 'same'

    return reply_text, timing


def get_adherence_condition(pid, day, diag):
    """判断依从性和病情状态"""
    is_hf = any(k in diag for k in ['心力衰竭', '心衰', 'HFpEF', 'HFrEF', '心功能'])
    is_af = any(k in diag for k in ['心房颤动', '房颤'])
    is_cad = any(k in diag for k in ['冠心病', '心绞痛', '支架', '心梗'])

    # 高频随访加密患者（3/5/7/14/21）病情持续好转
    if pid in ['P005', 'P026', 'P012', 'P017']:
        adherence = 'good'
        if day <= 7:
            condition = 'improved'
        else:
            condition = 'improved'
    elif pid == 'P029':
        adherence = 'good'
        condition = 'improved' if day <= 14 else 'improved'
    else:
        adherence = 'good'
        condition = 'improved' if day >= 7 else 'stable'

    # 特殊情况
    if pid == 'P012' and day == 3:
        condition = 'stable'
        return adherence, condition, '乏力（可能与CKD相关）', True, 'attention'
    if pid == 'P030':
        condition = 'improved'

    return adherence, condition, '', False, 'normal'


# ===== 生成所有随访记录 =====
today = datetime(2026, 3, 28)

all_records = []

for pid in sorted(FREQ.keys()):
    pdata = patient_data.get(pid)
    if not pdata:
        continue

    last_v = pdata['visits'][-1]
    vid = last_v['visit_id']
    base_date = datetime.strptime(last_v['visit_date'], '%Y-%m-%d')
    diag = last_v['diagnosis']
    notes_str = last_v['notes']
    name = patients[pid]['name']
    age = patients[pid]['age']
    gender = patients[pid]['gender']
    meds = pdata['current_meds']
    meds_str = get_meds_str(meds)
    bp, hr = last_v['bp'], last_v['hr']

    for day in FREQ[pid]:
        scheduled = base_date + timedelta(days=day)
        scheduled_str = scheduled.strftime('%Y-%m-%d')
        fid = f"F_{pid}_{day}_{scheduled.strftime('%Y%m%d')}"

        msg = gen_msg(pid, day, meds_str, diag, notes_str, name, age, gender)
        reply_text, delay_type = gen_reply(pid, day, meds_str, diag, bp, hr, name, gender)
        adherence, condition, adverse, needs_fu, priority = get_adherence_condition(pid, day, diag)

        # 发送时间和回复时间
        sent_str = scheduled_str
        reply_date = scheduled + timedelta(days={'same': 0, 'next': 1, 'later': 2, 'no_reply': 99}[delay_type])
        reply_str = reply_date.strftime('%Y-%m-%d') if delay_type != 'no_reply' else ''

        # AI摘要
        ai_sum = f"{name}：{'规律服药' if adherence=='good' else '依从性差'}，{'病情改善' if condition=='improved' else '病情稳定'}，{'需关注：'+adverse if adverse else '无明显不适'}。"
        if delay_type == 'next':
            ai_sum += '次轮回复。'
        elif delay_type == 'later':
            ai_sum += '较晚回复。'

        all_records.append({
            'followup_id': fid,
            'patient_id': pid,
            'visit_id': vid,
            'followup_day': str(day),
            'scheduled_time': scheduled_str,
            'sent_time': sent_str,
            'message_sent': msg,
            'reply_received': reply_text if delay_type != 'no_reply' else '',
            'reply_time': reply_str,
            'reply_delay_type': delay_type,
            'medication_adherence': adherence,
            'condition_status': condition,
            'adverse_reaction': adverse,
            'needs_followup': 'true' if needs_fu else 'false',
            'priority_level': priority,
            'ai_summary': ai_sum,
        })

# ===== 写入 followups.csv =====
fieldnames = [
    'followup_id','patient_id','visit_id','followup_day','scheduled_time','sent_time',
    'message_sent','reply_received','reply_time','reply_delay_type',
    'medication_adherence','condition_status','adverse_reaction',
    'needs_followup','priority_level','ai_summary'
]

# 按患者编号+随访天数排序
all_records.sort(key=lambda x: (x['patient_id'], int(x['followup_day'])))

with open('data/followups.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_records)

print(f"✅ 生成 {len(all_records)} 条随访记录")
print(f"📋 文件：data/followups.csv")

# 统计
freq_counts = {}
for r in all_records:
    d = r['reply_delay_type']
    freq_counts[d] = freq_counts.get(d, 0) + 1
print(f"\n📊 回复时机分布：")
for k, v in freq_counts.items():
    names = {'same': '本轮回复', 'next': '下轮回复', 'later': '较晚回复', 'no_reply': '未回复'}
    print(f"  {names.get(k, k)}: {v}条")
