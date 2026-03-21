"""
PatientClaw 随访记录 — 多样化真实场景生成
覆盖：依从性(good/partial/none) × 病情(improved/stable/unchanged/worsened) × 回复时机(same/next/later/no_reply)
"""
import csv
from datetime import datetime, timedelta

with open('data/followups.csv', newline='', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
fieldnames = list(rows[0].keys())

# ===== 30名患者多样化场景 =====
SCENARIOS = {

    # ── P001 王建国 高血压3级 退休老人 依从性从好→自行减药 ──
    'P001': {
        3:  ('good','stable','','','same',
             '三种药都在吃，血压128/82，没有头晕，感觉还好。',
             '请问可以稍微多吃点盐吗？清淡饮食太难受了。'),
        7:  ('good','improved','','','same',
             '三种药一直在吃，血压124/78，没有头晕，感觉很好，比刚吃药时好多了。',
             '请问可以稍微放宽点盐吗？'),
        14: ('partial','unchanged','','','next',
             '这周缬沙坦漏了两天，血压134/92，比之前高了点，没有头晕，最近有点忙确实忘了。',
             '请问问题不大吧？要不要紧？'),
    },

    # ── P002 李美华 高血压+糖尿病 退休阿姨 饮食控制难 ──
    'P002': {
        3:  ('good','stable','','','same',
             '两种药都在吃，血压128/80，血糖6.2，没有不舒服。',
             '请问糖尿病饮食太严格了，可以稍微放宽一点吗？'),
        7:  ('partial','unchanged','血糖波动（空腹6.6mmol/L）','true','same',
             '两种药都在吃，但这周贝那普利忘了两天，血压130/88，血糖6.6偏高，这周没控制住吃了两次火锅。',
             '请问血糖6.6是不是很高？需要加药吗？'),
        14: ('good','improved','','','same',
             '两种药都在吃，上周漏药的情况已经改进了，血压124/78，血糖降到6.0了，饮食也注意了一些，感觉好多了。',
             '请问糖尿病饮食可以稍微放宽一点吗？'),
    },

    # ── P003 张伟 高血压+冠心病 退休工人 依从性好 ──
    'P003': {
        3:  ('good','stable','','','same',
             '三种药都在吃，血压130/82，没有胸闷，感觉还好。',
             '请问可以坐飞机吗？想回老家看看。'),
        7:  ('good','improved','','','same',
             '三种药都在吃，血压126/80，心率72，没有胸闷，走路也没问题，感觉比上周好多了。',
             '请问可以坐飞机吗？'),
        14: ('good','improved','','','same',
             '三种药一直在吃，血压126/80，心率68，没有胸闷，走路爬楼都没问题，感觉很好，比刚来看病时好多了。',
             '请问下次复诊是什么时候？'),
    },

    # ── P004 刘静 高血压+高脂血症 中年女性 他汀肌痛 ──
    'P004': {
        3:  ('good','stable','','','same',
             '两种药都在吃，血压128/80，没有肌肉痛，感觉挺好的。',
             '请问他汀要吃多久？'),
        7:  ('partial','unchanged','他汀类药物引起肌肉酸痛','true','same',
             '氨氯地平在吃，但瑞舒伐他汀这周三片我只吃了两片，腿有点酸，怀疑是副作用，周三停了一天没吃，血压126/84。',
             '请问这个肌肉酸痛怎么办？要不要停他汀？'),
        14: ('good','improved','','','same',
             '两种药都在吃，上周看了李主任换了匹伐他汀，肌肉酸痛已经消失了，血压124/78，感觉很好。',
             '请问匹伐他汀要吃多久？'),
    },

    # ── P005 陈强 心衰HFrEF NYHA I-II 依从性好 持续改善 ──
    'P005': {
        3:  ('good','stable','','','same',
             '四种药都在吃，今天体重62.8kg，血压126/80，没有气短，腿不肿。',
             '请问现在能做轻微运动吗？'),
        5:  ('good','improved','','','same',
             '四种药都在吃，体重62.5kg稳定，血压124/78，没有气短，感觉还好。',
             '请问利尿剂可以减量吗？'),
        7:  ('good','improved','','','same',
             '四种药都在吃，今天体重62.5kg，血压126/78，没有气短，走路轻松多了，感觉比上周好。',
             '请问可以坐飞机吗？'),
        14: ('good','improved','','','same',
             '四种药一直在吃，今天体重62.5kg，血压124/76，没有气短，现在能爬三层楼不喘了，感觉比刚来看病时好太多了。',
             '请问可以恢复工作了吗？'),
        21: ('good','improved','','','same',
             '四种药一直在吃，今天体重62.2kg稳定，血压122/76，没有气短，走路很轻松，状态非常好，感谢李主任！',
             '请问可以坐飞机了吗？上次问过没回复。'),
    },

    # ── P006 杨梅 高血压1级 老年女性 自行减药 ──
    'P006': {
        3:  ('good','stable','','','same',
             '缬沙坦每天吃，血压130/82，没有头晕，感觉还好。',
             '请问缬沙坦要吃多久？'),
        7:  ('partial','unchanged','','true','same',
             '缬沙坦感觉血压降得差不多了，上周一到周四正常吃，周五到周日自己减成了半片，这两天血压132/90，比之前高了一点，但没有头晕。',
             '需要恢复全量吗？'),
        14: ('good','improved','','','next',
             '缬沙坦每天都在吃，上周减量的问题李主任说了不能减，我改正了，血压126/80，没有头晕，感觉很好，比刚开始吃药时好多了。',
             '请问血压稳定了可以减药吗？上次问过没回复。'),
    },

    # ── P007 赵磊 高血压+高脂血症+糖尿病前期 中年男性 饮食管理难 ──
    'P007': {
        3:  ('good','stable','','','same',
             '三种药都在吃，血压132/82，血糖6.1，没有不舒服。',
             '请问需要忌口吗？'),
        7:  ('partial','unchanged','血糖波动（空腹6.5mmol/L）','true','same',
             '氨氯地平和阿托伐他汀在吃，二甲双胍这周有一顿忘了吃，血压130/86，血糖6.5偏高，这周吃了两三次火锅。',
             '请问血糖6.5需要加药吗？'),
        14: ('good','improved','','','same',
             '三种药一直在吃，血压128/82，血糖降到5.9了，上周饮食注意了一些，感觉好多了。',
             '请问还需要继续看内分泌科吗？'),
    },

    # ── P008 黄丽 高血压2级 中年女性 生活方式难改 ──
    'P008': {
        3:  ('good','stable','','','same',
             '氨氯地平每天吃，血压130/82，没有头晕，感觉挺好的。',
             '请问可以喝咖啡吗？'),
        7:  ('partial','unchanged','','true','same',
             '氨氯地平都在吃，但这周有两三天忘了测血压，今天测了138/90，比上周稍高，跟这周加班熬夜多有关系，饮食也没太控制。',
             '请问血压偏高怎么办？'),
        14: ('good','improved','','','same',
             '氨氯地平每天都在吃，血压126/80，没有头晕，最近作息规律了一些，感觉很好，比刚吃药时好多了。',
             '请问可以喝咖啡吗？上次问过没回复。'),
    },

    # ── P009 周斌 高血压+脑梗死后遗症 老年男性 恢复期 ──
    'P009': {
        3:  ('good','stable','','','same',
             '三种药都在吃，血压130/80，头晕好多了，走路也比以前稳。',
             '请问可以恢复驾驶吗？'),
        7:  ('good','improved','','','same',
             '三种药一直在吃，血压128/80，头晕完全没有了，走路比以前稳多了，感觉很好。',
             '请问可以恢复驾驶吗？'),
        14: ('good','improved','','','same',
             '三种药一直在吃，血压126/78，头晕完全消失了，走路比以前稳多了，感觉很好。',
             '请问可以恢复驾驶吗？上次问过没回复。'),
    },

    # ── P010 吴霞 高血压+焦虑 中年女性 焦虑影响依从 ──
    'P010': {
        3:  ('good','stable','','','same',
             '比索洛尔每天吃，血压130/84，心率76，焦虑感觉还好。',
             '请问比索洛尔要吃多久？'),
        7:  ('partial','unchanged','焦虑症状反复','true','same',
             '这周比索洛尔忘了两天，血压138/92，心率84，焦虑感又回来了，晚上睡不太好，头也有点痛。',
             '请问焦虑又犯了怎么办？'),
        14: ('good','improved','','','same',
             '比索洛尔每天都吃，上周忘了两天的问题改进了，血压126/80，心率72，焦虑好多了，睡眠也好转了，头痛基本没有了。',
             '请问焦虑症还需要继续看心理科吗？'),
    },

    # ── P011 徐涛 高血压+高脂血症（他汀不耐受）中年男性 记性差 ──
    'P011': {
        3:  ('good','stable','','','same',
             '两种药都在吃，血压128/80，没有不舒服。',
             '请问匹伐他汀要吃多久？'),
        7:  ('partial','unchanged','','true','same',
             '这周匹伐他汀忘了两天，血压132/88，稍微高了一点，没有肌肉痛。',
             '请问匹伐他汀要吃多久？可以停吗？'),
        14: ('good','improved','','','same',
             '两种药一直在吃，血压124/76，没有肌肉痛，感觉很好，比之前精神多了。',
             '请问LDL降到多少可以停匹伐他汀？'),
    },

    # ── P012 马超 房颤+脑梗史+CKD 老年男性 依从性差 病情加重 ──
    'P012': {
        3:  ('good','stable','乏力（可能与CKD相关）','true','same',
             '地尔硫卓和利伐沙班都在吃，没有出血，血压136/84，就是最近有点乏力，不知道是不是肾的问题。',
             '请问乏力是不是肾的问题？需要复查吗？'),
        5:  ('partial','unchanged','','true','same',
             '地尔硫卓这周有两天忘了吃，血压142/92，心悸又开始了，头有点晕，乏力的感觉没变化。',
             '请问心悸又有了，需要加药吗？'),
        7:  ('partial','worsened','心悸加重，血压升高','true','same',
             '这周利伐沙班漏了三天，地尔硫卓也漏了两天，昨天开始心悸明显了，血压148/96，有时候感觉心跳不规律，乏力也更明显了。',
             '请问这是不是严重了？需要立即来看吗？'),
        14: ('good','unchanged','','','same',
             '这周开始按时吃了，血压138/88，稍微好一点，心悸减轻了一些，但还是有点，乏力的感觉也轻了一些，没有出血。',
             '请问利伐沙班剂量需要调整吗？'),
        21: ('good','stable','','','same',
             '地尔硫卓和利伐沙班一直坚持吃，血压128/82，心率72，感觉比上周好多了，乏力的感觉也轻了很多，没有不舒服，状态稳定。',
             '请问还需要加别的药吗？'),
    },

    # ── P013 胡杰 高血压+睡眠呼吸暂停 中年男性 CPAP依从差 ──
    'P013': {
        3:  ('good','stable','','','same',
             '氨氯地平每天吃，血压140/88，CPAP也在用，头痛少多了。',
             '请问CPAP要戴多久？'),
        7:  ('partial','unchanged','','true','same',
             '氨氯地平每天吃，CPAP这周有两晚没用，血压142/90，晨起头痛又有了。',
             '请问CPAP不坚持用会影响效果吗？'),
        14: ('good','improved','','','same',
             '氨氯地平每天吃，血压136/86，CPAP坚持用了，现在已经习惯了，头痛基本消失了，睡眠质量好多了。',
             '请问CPAP要戴多久？上次问过没回复。'),
    },

    # ── P014 罗健 冠心病支架术后 依从性好 ──
    'P014': {
        3:  ('good','stable','','','same',
             '四种药都在吃，血压126/80，心率72，没有胸闷，感觉挺好的。',
             '请问可以喝酒吗？'),
        7:  ('good','improved','','','same',
             '四种药都在吃，血压124/78，心率70，没有胸闷，上周也没有胸痛，感觉很好。',
             '请问可以喝酒吗？'),
        14: ('good','improved','','','same',
             '四种药一直在吃，血压124/78，心率68，没有胸闷，走路也没问题，状态很好。请问可以喝酒吗？上次问过没回复。',
             ''),
    },

    # ── P015 韩旭 心衰HFpEF 退休工人 依从性好 ──
    'P015': {
        3:  ('good','stable','','','same',
             '三种药都在吃，今天体重68.2kg，血压128/80，没有气短，脚也不肿。',
             '请问可以出去旅游吗？'),
        7:  ('good','improved','','','same',
             '三种药都在吃，今天体重68.0kg，血压126/80，没有气短，脚不肿，感觉挺好的。',
             '请问可以出去旅游吗？'),
        14: ('good','improved','','','same',
             '三种药一直在吃，今天体重68.0kg稳定，血压124/78，没有气短，脚不肿，感觉很好。',
             '请问可以出去旅游吗？上次问过没回复。'),
    },

    # ── P016 彭宇 心功能不全 中年男性 依从性好 持续改善 ──
    'P016': {
        3:  ('good','stable','','','same',
             '四种药都在吃，今天体重71.8kg，血压130/84，没有气短，腿不肿。',
             '请问可以正常工作吗？'),
        7:  ('good','improved','','','same',
             '四种药都在吃，今天体重71.5kg，血压128/82，没有气短，腿也不肿，感觉比上周好多了。',
             '请问可以正常工作吗？'),
        14: ('good','improved','','','same',
             '四种药一直在吃，今天体重71.2kg稳定，血压126/80，没有气短，腿也不肿，感觉比刚来看病时好多了。',
             '请问可以正常工作吗？上次问过没回复。'),
    },

    # ── P017 方远 房颤+脑梗史 老年男性 依从性差 病情反复 ──
    'P017': {
        3:  ('good','stable','','','same',
             '利伐沙班和地高辛都在吃，没有出血，心跳感觉还可以，血压134/82。',
             '请问可以少量喝酒吗？'),
        5:  ('partial','unchanged','','true','same',
             '利伐沙班这周有两天忘了吃，血压138/88，感觉心律有点不齐了。',
             '请问心律不齐要紧吗？'),
        7:  ('partial','worsened','','true','same',
             '地高辛这周漏了两天，利伐沙班也有两天没吃，昨天开始心悸明显了，血压142/94，有时候感觉心跳不规律，头有点晕。',
             '请问这是不是严重了？需要立即来看吗？'),
        14: ('good','stable','','','same',
             '这周按时吃药了，血压130/82，心律感觉比上周好了，心悸轻了很多，没有出血。',
             '请问下次复诊是什么时候？'),
        21: ('good','improved','','','same',
             '利伐沙班和地高辛一直坚持吃，心跳感觉很规律，血压126/80，没有不舒服，状态稳定。',
             '请问可以少量喝酒吗？上次问过没回复。'),
    },

    # ── P018 邵杰 稳定型心绞痛 依从性好 ──
    'P018': {
        3:  ('good','stable','','','same',
             '五种药都在吃，没有胸痛，走路也没问题，感觉比之前好一些。',
             '请问可以快走运动吗？'),
        7:  ('good','improved','','','same',
             '五种药都在吃，这周没有胸痛，走路上楼都没问题，血压128/80，感觉比以前好多了。',
             '请问可以快走运动吗？'),
        14: ('good','improved','','','same',
             '五种药一直在吃，这两周没有胸痛，走路上楼都没问题，血压126/78，感觉比以前好多了。',
             '请问可以快走运动吗？上次问过没回复。'),
    },

    # ── P019 段勇 冠心病支架术后单抗维持 老年男性 阿司匹林胃刺激 ──
    'P019': {
        3:  ('good','stable','','','same',
             '阿司匹林每天吃，没有胸闷，血压130/80，感觉挺好的。',
             '请问可以喝点酒吗？'),
        7:  ('partial','unchanged','','true','same',
             '阿司匹林每天吃，但这周有两天忘了饭后吃，胃有点不舒服，有点反酸。',
             '请问胃不舒服怎么办？'),
        14: ('partial','unchanged','胃部不适（阿司匹林副作用）','true','same',
             '阿司匹林每天吃，胃还是有点不舒服，有时候反酸，血压128/80，没有胸闷。',
             '请问胃不舒服需要换药吗？'),
    },

    # ── P020 汤波 心梗后稳定EF50% 中年男性 依从性好 ──
    'P020': {
        3:  ('good','stable','','','same',
             '药都在吃，血压130/80，没有气短胸痛，感觉挺好的。',
             '请问需要多久复查一次心脏？'),
        7:  ('good','improved','','','same',
             '药都在吃，血压128/80，没有气短胸痛，走路有劲，感觉挺好的。',
             '请问需要多久复查一次心脏？'),
        14: ('good','improved','','','same',
             '药一直在吃，血压124/78，没有气短胸痛，走路有劲，感觉挺好的，状态稳定。',
             '请问可以快走运动吗？上次问过没回复。'),
    },

    # ── P021 张丽 心衰HFrEF EF40% 老年女性 依从性好 持续改善 ──
    'P021': {
        3:  ('good','stable','','','same',
             '四种药都在吃，今天体重58.5kg，血压128/82，没有气短，脚不肿。',
             '请问可以爬楼梯吗？'),
        7:  ('good','improved','','','same',
             '四种药都在吃，今天体重58.2kg，血压126/80，没有气短，腿不肿，感觉比上周还好，走路轻松多了。',
             '请问可以爬楼梯吗？'),
        14: ('good','improved','','','same',
             '四种药一直在吃，今天体重58.0kg稳定，血压124/78，没有气短，腿不肿，感觉比两周前好多了，走路轻松多了。',
             '请问可以快走运动吗？上次问过没回复。'),
    },

    # ── P022 徐慧 阵发性房颤 中年女性 胺碘酮漏服 心律不齐 ──
    'P022': {
        3:  ('good','stable','','','same',
             '三种药都在吃，没有心悸，血压132/82，感觉挺好的。',
             '请问胺碘酮要吃多久？'),
        7:  ('partial','unchanged','','true','same',
             '胺碘酮这周漏了两天，血压138/88，昨天开始感觉心悸又有了，有时候心跳不规律。',
             '请问心悸又有了要紧吗？'),
        14: ('good','stable','','','next',
             '三种药一直在吃，这两周没有心悸，血压126/78，心律感觉比之前规律了，上次没看到消息抱歉。',
             '请问胺碘酮要长期吃吗？可以考虑消融手术吗？'),
    },

    # ── P023 孙浩 持续性房颤 中年男性 比索洛尔漏服 ──
    'P023': {
        3:  ('good','stable','','','same',
             '四种药都在吃，心跳感觉平稳，没有心悸，血压126/80。',
             '请问可以喝咖啡吗？'),
        7:  ('partial','unchanged','','true','same',
             '比索洛尔这周漏了两天，心率偏快88bpm，有时候感觉心悸，没有出血，血压130/84。',
             '请问心率偏快要紧吗？'),
        14: ('good','improved','','','same',
             '四种药一直在吃，心跳平稳，心率76bpm，没有心悸，没有出血，血压122/76，感觉挺好的。',
             '请问可以喝咖啡吗？上次问过没回复。'),
    },

    # ── P024 胡娟 频发室早 中年女性 依从性好 持续改善 ──
    'P024': {
        3:  ('good','stable','','','same',
             '比索洛尔在吃，心悸感觉少多了，偶尔还有一点，但比之前好很多，没有头晕。',
             '请问室早能完全消失吗？'),
        7:  ('good','improved','','','next',
             '比索洛尔每天吃，心悸基本没有了，偶尔有一点点，血压122/76，没有头晕，感觉比刚开始好很多了。',
             '请问室早能完全消失吗？上次问过没回复。'),
        14: ('good','improved','','','same',
             '比索洛尔每天都在吃，室早基本消失了，偶尔有一点，血压120/76，没有头晕，感觉好多了。',
             '请问室早能完全消失吗？还要继续看心脏科吗？'),
    },

    # ── P025 郭英 房颤+心衰 老年女性 依从性差 病情加重 ──
    'P025': {
        3:  ('good','stable','','','same',
             '四种药都在吃，今天体重72.3kg，血压132/84，没有气短，腿不肿。',
             '请问可以喝咖啡吗？'),
        7:  ('partial','unchanged','','true','same',
             '这周托拉塞米漏了两天，今天体重73.2kg，比上周重了1kg，腿有点肿了，血压136/88。',
             '请问腿肿要紧吗？'),
        14: ('partial','worsened','下肢水肿加重，体重增加2kg','true','same',
             '这周又漏了三天托拉塞米，今天体重74.5kg，腿肿明显了，血压138/90，走路有点喘了，比之前差了。',
             '请问是不是严重了？需要立即来看吗？'),
    },

    # ── P026 韩梅 心衰HFrEF EF45% NYHA I级 依从性好 持续改善 ──
    'P026': {
        3:  ('good','stable','','','same',
             '四种药都在吃，今天体重58.2kg，血压126/80，没有气短，感觉比刚出院好多了。',
             '请问可以进行快走运动吗？'),
        5:  ('good','improved','','','same',
             '四种药都在吃，今天体重58.0kg，血压124/78，没有气短，比上周好。',
             '请问心率56bpm是不是偏慢了？'),
        7:  ('good','improved','','','same',
             '四种药都在吃，今天体重57.8kg，血压124/78，没有气短，腿不肿，感觉比上周好，走路也轻松了。',
             '请问心率偏慢需要减药吗？'),
        14: ('good','improved','','','same',
             '四种药一直在吃，今天体重57.5kg稳定，血压122/76，没有气短，现在能走路半小时不喘，感觉和正常人差不多了，非常感谢李主任！',
             '请问沙库巴曲缬沙坦需要加量吗？'),
        21: ('good','improved','','','same',
             '四种药一直在吃，今天体重57.2kg稳定，血压120/74，没有气短，状态非常好，感谢李主任！',
             '请问这种情况可以停药吗？上次问过没回复。'),
    },

    # ── P027 曹阳 HFpEF+房颤 中年男性 依从性好 ──
    'P027': {
        3:  ('good','stable','','','same',
             '四种药都在吃，今天体重74.2kg，血压130/82，没有气短，腿不肿。',
             '请问可以出去旅游吗？'),
        7:  ('partial','unchanged','','true','same',
             '这周达比加群漏了两天，心率有点不规律，血压134/88，体重74.5kg，腿有点肿。',
             '请问腿肿要紧吗？'),
        14: ('good','improved','','','same',
             '四种药一直在吃，今天体重74.0kg稳定，血压128/82，心率78bpm，没有气短，腿不肿，感觉比两周前好多了。',
             '请问可以快走运动吗？上次问过没回复。'),
    },

    # ── P028 许静 扩张型心肌病/ICD 中年女性 依从性好 ──
    'P028': {
        3:  ('good','stable','','','same',
             '四种药都在吃，今天体重62.0kg，血压124/78，没有气短，ICD没有放电，感觉挺好的。',
             '请问ICD需要定期检查吗？'),
        7:  ('good','improved','','','same',
             '四种药都在吃，今天体重61.8kg，血压124/78，没有气短，ICD没有放电，感觉挺好的。',
             '请问ICD需要定期检查吗？'),
        14: ('good','improved','','','same',
             '四种药一直在吃，今天体重61.5kg稳定，血压122/76，没有气短，ICD没有放电，感觉很好。请问ICD需要定期检查吗？上次问过没回复。',
             ''),
    },

    # ── P029 邓凯 缺血性心肌病重度心衰 NYHA III-IV 依从性好 逐步改善 ──
    'P029': {
        3:  ('good','stable','','','same',
             '四种药都在吃，今天体重78.5kg，血压124/80，气短比之前好一些，腿肿也轻了。',
             '请问还能恢复到正常生活吗？'),
        5:  ('good','improved','','','same',
             '四种药都在吃，今天体重78.3kg，血压122/78，气短比上周好一些，腿肿也轻了，可以走100米了。',
             '请问可以加大运动量吗？'),
        7:  ('good','improved','','','same',
             '四种药都在吃，今天体重78.0kg，血压122/78，气短比之前明显好转，腿肿也轻了很多，可以走200米了，比刚来时好多了。',
             '请问还能恢复到正常生活吗？'),
        14: ('good','improved','','','same',
             '四种药一直在吃，今天体重77.5kg，血压120/76，气短比之前又好转了，腿肿基本消失了，可以走300米了，比刚来时好多了。',
             '请问EF能恢复到多少？'),
        21: ('partial','unchanged','','true','same',
             '四种药一直在吃，今天体重77.8kg，稍微重了点，血压122/76，走路还是有点喘，腿没肿，状态还可以。请问沙库巴曲缬沙坦需要加量吗？',
             ''),
    },

    # ── P030 江华 家族性高胆固醇血症 依从性好 指标改善 ──
    'P030': {
        3:  ('good','stable','','','same',
             '三种药都在吃，今天测了LDL 2.1，血压124/80，没有不舒服。',
             '请问依折麦布要长期吃吗？'),
        7:  ('good','improved','','','same',
             '三种药都在吃，LDL降到了1.9，血压122/76，没有不舒服，感觉在慢慢好转。请问依折麦布要长期吃吗？',
             ''),
        14: ('good','improved','','','same',
             '三种药一直在吃，LDL降到了1.8，血压120/76，没有不舒服，感觉非常好，感谢医生！请问LDL降到多少可以减少用药？',
             ''),
    },
}

# ===== 应用场景到每条记录 =====
def build_reply(pid, day):
    if pid not in SCENARIOS or day not in SCENARIOS[pid]:
        return None
    s = SCENARIOS[pid][day]
    adherence, condition, adverse, needs_fu, delay, reply_body, question = s
    reply = reply_body
    if question:
        reply += f' 还有个问题想问：我请问李主任，{question}'
    else:
        reply = reply_body
    reply = reply.rstrip()
    return adherence, condition, adverse, needs_fu, delay, reply

# 构建priority和ai_summary
def get_priority(adherence, condition, adverse, needs_fu):
    if needs_fu == 'true' or adverse:
        return 'attention'
    if condition == 'worsened':
        return 'attention'
    if adherence == 'none':
        return 'attention'
    return 'normal'

def get_summary(pid, name, adherence, condition, adverse, delay, delay_type_map):
    names_map = {
        'same': '本轮回复。',
        'next': '次轮补回复。',
        'later': '较晚回复确认。',
        'no_reply': '未回复。',
    }
    timing_note = names_map.get(delay, '')

    adh_map = {'good': '规律服药', 'partial': '部分依从', 'none': '依从性差', 'unknown': '依从性未知'}
    cond_map = {'improved': '病情改善', 'stable': '病情稳定', 'unchanged': '病情无变化', 'worsened': '病情恶化', 'recovered': '已痊愈'}
    adh_str = adh_map.get(adherence, adherence)
    cond_str = cond_map.get(condition, condition)

    summary = f"{name}：{adh_str}，{cond_str}"
    if adverse:
        summary += f'，需关注：{adverse}'
    elif condition == 'worsened':
        summary += '，需密切观察'
    elif condition == 'unchanged':
        summary += '，需继续观察'
    else:
        summary += '，无明显不适'
    summary += f'。{timing_note}'
    return summary

# delay字段转reply_delay_type
delay_map = {'same': 'same', 'next': 'next', 'later': 'later', 'no_reply': 'no_reply'}

# 更新rows
updated = 0
for r in rows:
    pid = r['patient_id']
    day = int(r['followup_day'])
    result = build_reply(pid, day)
    if result:
        adherence, condition, adverse, needs_fu, delay, reply = result
        priority = get_priority(adherence, condition, adverse, needs_fu)
        summary = get_summary(pid, pid, adherence, condition, adverse, delay, delay_map)

        # reply_time: 本轮当天，下轮+1，较晚+2，不回复留空
        base = datetime.strptime(r['scheduled_time'], '%Y-%m-%d')
        if delay == 'same':
            reply_date = base.strftime('%Y-%m-%d')
        elif delay == 'next':
            reply_date = (base + timedelta(days=1)).strftime('%Y-%m-%d')
        elif delay == 'later':
            reply_date = (base + timedelta(days=2)).strftime('%Y-%m-%d')
        else:
            reply_date = ''

        r['reply_received'] = reply
        r['reply_time'] = reply_date
        r['reply_delay_type'] = delay
        r['medication_adherence'] = adherence
        r['condition_status'] = condition
        r['adverse_reaction'] = adverse
        r['needs_followup'] = needs_fu
        r['priority_level'] = priority
        r['ai_summary'] = summary
        updated += 1

# 写入
with open('data/followups.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ 更新完成，共更新 {updated} 条记录")

# 质量报告
from collections import Counter
adh = Counter(r['medication_adherence'] for r in rows)
cond = Counter(r['condition_status'] for r in rows)
delay = Counter(r['reply_delay_type'] for r in rows)
prio = Counter(r['priority_level'] for r in rows)
has_q = sum(1 for r in rows if '请问' in r.get('reply_received','') and '李主任' in r.get('reply_received',''))
no_reply = sum(1 for r in rows if not r.get('reply_received','').strip())

print(f"\n📊 依从性分布: good={adh['good']} partial={adh['partial']} none={adh['none']} unknown={adh['unknown']}")
print(f"📊 病情分布: improved={cond['improved']} stable={cond['stable']} unchanged={cond['unchanged']} worsened={cond['worsened']}")
print(f"📊 回复时机: same={delay['same']} next={delay['next']} later={delay['later']} no_reply={delay['no_reply']}")
print(f"📊 优先级: normal={prio['normal']} attention={prio['attention']} urgent={prio['urgent']}")
print(f"📊 含患者提问: {has_q}条 / {len(rows)}条")
print(f"📊 无回复记录: {no_reply}条")
