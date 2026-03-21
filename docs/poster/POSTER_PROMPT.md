## Prompt for Claude

---

请帮我制作 PatientClaw 项目的海报 HTML，保存为 `/Users/zth/Documents/Code/PatientClaw/docs/poster/index.html`。

## 尺寸要求（关键！必须严格遵守）

- **物理尺寸：0.8m × 2.0m**（宽 × 高，A1 竖版），150 DPI
- **像素：4725px × 11811px**
- **浏览器预览：945px × 2362px**（1/5 比例）
- `@page { size: 842mm 2388mm; margin: 0; }` 让浏览器打印时自动 1:1 输出

## 高度分配（必须恰好加总到 2362px）

| Section | 高度 | 说明 |
|---------|------|------|
| hero | **241px** | hero 加了 51px 补差 |
| social | 490px | |
| flow | 318px | |
| data | 208px | |
| cases | 258px | |
| rpt | 234px | |
| pat | 234px | |
| feat | 160px | |
| exp | 94px | |
| foot | 98px | |
| divider × 9 | 27px | 每个 3px |
| **合计** | **2362px** | **✓ 正好** |

## CSS 技术规范

- ❌ 禁止使用 CSS 变量 `--S`
- ❌ 禁止使用 `calc()`
- ✅ 所有 font-size / padding / margin / height 直接写固定 px 值
- 字体：body 14px，标题更大，PingFang SC / Microsoft YaHei / system-ui
- 风格：深色科技风，背景 `#080c14`，绿/蓝/紫/青/橙/红配色

## 各节内容（从顶部到底部顺序）

### ① HERO（241px，padding: 22px 80px）
- 顶部左侧蓝色标签：`北纬 · 龙虾大赛（第一届）· OpenClaw Hackathon · 生产力赛道`（padding: 5px 18px，圆角30px，border 1px）
- 顶部右侧橙色标签：`🏆 决赛入围`（padding: 4px 14px，圆角20px）
- 中间大标题：**PatientClaw**（渐变紫蓝，120px粗体，letter-spacing -5px）
- 副标题：`患者诊后病情全自动跟踪统计系统`（24px，灰色）
- 三个青色标签（gap:14px）：`🤖 OpenClaw 驱动 · 全自动随访` `📊 数据驱动 · 精准干预` `🏥 助力分级诊疗`
- 底部左侧：卡片（bg2，border 1px，圆角14px，padding 12px 20px）
  - 大字：李晓峰 主任医师 · 心血管内科
  - 小字：北京协和医院 · 专长：冠心病介入 / 高血压管理 / 心律失常 / 心力衰竭
  - 灰字：全系统唯一真实用户 · 每天只需查看飞书推送日报
- 底部右侧：github链接、邮箱、Powered by OpenClaw（紫色加粗）

### ② 社会意义（490px，padding: 32px 80px，背景渐变 bg2→bg）
- Section Label：`应用价值与社会效益`（11px 粗体，大写字母间距0.18em，灰色，mb:16px）
- 标题（26px 粗体）：心血管病管理缺口巨大，患者离院后处于**"信息孤岛"**（绿色）
- 描述（14px，灰色，mb:24px，2.5行）：中国心血管病（CVD）患者超3.3亿，年死亡超400万。70%患者离院后因缺乏随访而延误干预；医生日均接诊30-50人，无暇主动追踪每一位患者；高危患者病情加重时往往错过最佳干预窗口。PatientClaw将AI Agent自动化引入诊后管理，打通医患信息断点，让每一次就诊都有后续。
- **两栏并排**（grid:1fr 1fr，gap:22px，mb:24px）：
  - 左栏（bg:rgba红0.05，border:1.5px红，radius:14px，padding:20px 22px）：
    - 标题：`❌ 当前困境`（15px粗体，大写，红色）
    - 5条item（flex，gap:10px，mb:12px）：
      - ·（红色16px）+ 文字（13px灰色，lh:1.65）
  - 右栏（bg:rgba绿0.05，border:1.5px绿，radius:14px，padding:20px 22px）：
    - 标题：`✅ PatientClaw的核心价值`（15px粗体，大写，绿色）
    - 6条item
- **底部4个数据卡片**（grid:repeat4 1fr，gap:14px）：
  - 各卡：bg3，border 1px，radius:12px，padding:18px 14px，text-align:center
  - 数字：40px粗体，40px高
  - 说明：11px灰色，lh:1.5
  - 颜色：绿/蓝/紫/橙

### ③ 系统流程（318px，padding: 32px 80px，bg:bg2）
- Section Label
- Intro（13px灰色，mb:22px，lh:1.7）
- **两栏并排**（grid:1fr 1fr，gap:28px）：
  - 左：flow-col-title + 时间轴（tl容器，flex column，gap:7px）
    - 每行：tl-dot(12px圆点，5色)+tl-content(bg3,border,adius10px,padding9px13px)
    - tl-title: 13px粗体 | tl-desc: 11px灰色 | tl-badge: 10px灰色
    - tl-arrow: 文字"↓"居中
  - 右：flow-col-title + cron-box(bg:rgba青0.05,border青,adius14px,padding16px20px)
    - cron-hdr: 13px粗体青色，mb:12px
    - 5条cron-item：flex，gap:10px，mb:11px
      - cron-tag: 青底青字，padding:2px 9px，radius:14px，font-size:10px
      - cron-text: 12px灰色，lh:1.55

### ④ 数据总览（208px，padding: 28px 80px）
- Section Label
- **2×2网格**（gap:14px）：
  - 各panel：bg2，border 1px，radius:14px，padding:16px 18px
  - Panel标题：13px粗体，大写，灰色，mb:14px
  - Panel1 进度条：bar-row（flex，gap:10px，mb:10px）
    - bar-lbl: 12px灰色，width:100px
    - bar-track: flex:1，h:16px，bg3，adius:8px
    - bar-fill: h:100%，adius8px，渐变色
    - br-pct: 12px粗体，width:46px，text-align:right
  - Panel2 圆环图：donut-row（flex，gap:18px）
    - donut-wrap: relative，120×120px
    - SVG圆环（rotate:-90deg）
    - leg列表（flex col，gap:9px）
  - Panel3 回复率：rstat（flex，gap:14px，mb:12px）+ 3个进度条
  - Panel4 提问：大字+说明+3进度条+底部小字

### ⑤ 典型案例（258px，padding: 28px 80px，bg:bg2）
- Section Label
- **两栏**（gap:14px）：
  - 各cc：bg3，border1px，adius14px，padding:16px18px，border-left:5px
    - cc.ok: border-left绿色 | cc.alert: border-left红色
  - cc-top：flex，gap:8px，mb:10px
    - cc-badge: 11px，padding:2px9px，adius12px
    - cc-pid: 11px，灰色，ml:auto
  - msg-label: 10px灰色，mb:5px
  - msg-box: bg:rgba白0.025，adius8px，p:8px11px，11px灰色，lh:1.65，mb:7px，border-left:3px
  - reply-label: 10px灰色，mb:5px
  - reply-box: bg:rgba紫0.05，p:8px11px，11px浅紫色，lh:1.65，border-left:3px
  - tags-row: flex，gap:6px，flex-wrap:wrap，mt:9px
    - tag-s: 10px，p:2px8px，adius8px，bg4，灰字，border
    - tag-s.alert: 红色背景+红色字+红色border

### ⑥ 医生日报（234px，padding: 28px 80px）
- Section Label
- rpt-panel（bg2，border1px，adius14px，overflow:hidden，h:100%）
- rpt-hdr（bg3，border-bottom1px，p:10px18px，flex justify-between）
  - rpt-title: 14px粗体
  - rpt-meta: 11px灰色
- rpt-body（p:14px18px，grid:1fr1fr，gap:14px，h:calc(100%-52px)，align-content:start）
  - rpt-col-title: 11px粗体，大写，灰色，mb:8px
  - ri: 11px灰色，lh:1.6，mb:6px，pl:12px，position:relative
    - ::before: ·，absolute left:0
    - ri.r/o/g/b: color对应颜色
  - rpt-divider: grid-col:1/-1，h:1px，bg:border
  - rpt-insight-title: grid-col:1/-1，11px粗体，黄色，mb:6px
  - rpt-insight-item: 11px灰色，lh:1.6，mb:5px，pl:12px，position:relative
    - ::before: ·，黄色，absolute left:0

### ⑦ 患者病情报告（234px，padding: 28px 80px，bg:bg2）
- Section Label
- pat-panel（bg3，border1px，adius14px，p:16px20px，h:100%）
- pat-hdr（flex justify-between，mb:12px）
- pat-table（w:100%，collapse，11px）：
  - th: bg4，灰字，padding:5px8px，text-align:left，bb1px，font-size:10px，大写，nowrap
  - td: 灰字，padding:5px8px，bb1px，lh:1.6，v-align:top
  - tr:last-child td: bb:none
- ptag: inline-block，p:1px7px，adius8px，font-size:10px粗体
  - ok: 绿底绿字 | neu: bg4灰字
- pat-summary: mt:10px，11px灰色，lh:1.7，border-top1px，pt:10px
  - strong: 白色

### ⑧ 核心功能（160px，padding: 28px 80px）
- Section Label
- feat-grid（grid:repeat3 1fr，gap:10px，h:100%，align-content:start）
- feat-item（bg2，border1px，adius12px，p:12px14px，flex，gap:10px）
- feat-emoji: 20px，flex-shrink:0
- feat-title: 13px粗体，mb:3px
- feat-desc: 11px灰色，lh:1.55

### ⑨ 扩展方向（94px，padding: 22px 80px，bg:bg2）
- Section Label
- exp-tags（flex，gap:10px，flex-wrap:wrap）
- exp-tag: bg:rgba蓝0.10，border蓝，color蓝，p:6px18px，adius30px，font-size:14px

### ⑩ Footer（98px，padding: 22px 80px，bg:bg2）
- flex（justify-content:space-between，align-items:center）
- 左侧：foot-name 20px粗体 + foot-school 13px灰色
- 中间：PatientClaw（渐变紫蓝，36px粗体，letter-spacing -1px）
- 右侧：12px灰色，lh:2.2，text-align:right
  - a: 蓝色，无下划线

---

## 完成后请验证

```python
heights = {
    'hero': 241, 'social': 490, 'flow': 318, 'data': 208,
    'cases': 258, 'rpt': 234, 'pat': 234, 'feat': 160,
    'exp': 94, 'foot': 98, 'divider×9': 27
}
total = sum(heights.values())
print(f"总高: {total}px (必须=2362)")
```
