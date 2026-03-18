# GitHub Pages 项目网站 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 PatientClaw 构建一个深色产品风格的 GitHub Pages 单页网站，展示项目介绍、功能、架构、资源链接。

**Architecture:** 单文件静态 HTML，放在 `docs/index.html`，GitHub Pages 指向 `docs/` 目录。无框架依赖，纯 HTML/CSS/JS，内联样式。

**Tech Stack:** HTML5, CSS3（CSS Variables + Grid + Flexbox），无外部依赖（字体用 system-ui）

---

### Task 1: 创建 docs/index.html 骨架

**Files:**
- Create: `docs/index.html`

**Step 1: 创建 HTML 文件骨架**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>PatientClaw · 患者诊后病情全自动跟踪统计系统</title>
  <style>
    /* 全局变量 */
    :root {
      --bg: #0d1117;
      --bg2: #161b22;
      --bg3: #21262d;
      --accent: #7c3aed;
      --accent2: #3b82f6;
      --text: #e6edf3;
      --text2: #8b949e;
      --border: #30363d;
      --radius: 12px;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: system-ui, -apple-system, sans-serif; line-height: 1.6; }
    a { color: var(--accent2); text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <!-- 内容将在后续步骤填入 -->
</body>
</html>
```

**Step 2: 提交**

```bash
git add docs/index.html
git commit -m "feat: 初始化 GitHub Pages 骨架"
```

---

### Task 2: Hero 区块

**Files:**
- Modify: `docs/index.html`

**Step 1: 在 `<body>` 中添加 Hero 区块 HTML**

```html
<header id="hero">
  <div class="container">
    <div class="badge">北纬·龙虾大赛 · OpenClaw Hackathon</div>
    <h1>Patient<span class="accent">Claw</span></h1>
    <p class="tagline">患者诊后病情全自动跟踪统计系统</p>
    <p class="sub">医生不改变任何工作习惯，系统在后台静默运行——自动随访、理解回复、生成日报。</p>
    <div class="tags">
      <span>全自动随访</span>
      <span>AI 回复解析</span>
      <span>飞书日报推送</span>
      <span>30名患者模拟</span>
    </div>
    <div class="hero-actions">
      <a href="https://github.com/happytianhao/PatientClaw" class="btn-primary" target="_blank">查看代码</a>
      <a href="docs/report/PatientClaw项目说明书.md" class="btn-secondary" target="_blank">项目说明书</a>
    </div>
  </div>
</header>
```

**Step 2: 在 `<style>` 中添加 Hero 样式**

```css
.container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }
#hero { padding: 100px 0 80px; text-align: center; background: radial-gradient(ellipse at 50% 0%, rgba(124,58,237,0.15) 0%, transparent 70%); }
.badge { display: inline-block; background: rgba(124,58,237,0.2); border: 1px solid rgba(124,58,237,0.4); color: #a78bfa; padding: 4px 14px; border-radius: 20px; font-size: 13px; margin-bottom: 24px; }
h1 { font-size: clamp(48px, 8vw, 80px); font-weight: 800; letter-spacing: -2px; margin-bottom: 16px; }
.accent { background: linear-gradient(135deg, #7c3aed, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.tagline { font-size: clamp(18px, 3vw, 24px); color: var(--text2); margin-bottom: 16px; }
.sub { font-size: 16px; color: var(--text2); max-width: 600px; margin: 0 auto 32px; }
.tags { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-bottom: 40px; }
.tags span { background: var(--bg3); border: 1px solid var(--border); padding: 6px 16px; border-radius: 20px; font-size: 14px; }
.hero-actions { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
.btn-primary { background: linear-gradient(135deg, #7c3aed, #3b82f6); color: white; padding: 12px 28px; border-radius: 8px; font-weight: 600; font-size: 15px; }
.btn-primary:hover { opacity: 0.9; text-decoration: none; }
.btn-secondary { background: var(--bg3); border: 1px solid var(--border); color: var(--text); padding: 12px 28px; border-radius: 8px; font-weight: 600; font-size: 15px; }
.btn-secondary:hover { border-color: var(--accent); text-decoration: none; }
```

**Step 3: 提交**

```bash
git add docs/index.html
git commit -m "feat: 添加 Hero 区块"
```

---

### Task 3: 功能介绍区块（6张卡片）

**Files:**
- Modify: `docs/index.html`

**Step 1: 在 Hero 后添加功能区 HTML**

```html
<section id="features">
  <div class="container">
    <h2 class="section-title">核心功能</h2>
    <div class="cards">
      <div class="card">
        <div class="card-icon">📅</div>
        <h3>全自动随访</h3>
        <p>就诊后第 3 / 7 / 14 天自动触发，根据病情动态调整随访频率，无需人工干预。</p>
      </div>
      <div class="card">
        <div class="card-icon">💬</div>
        <h3>个性化问询</h3>
        <p>结合每位患者的诊断、用药、就诊天数生成专属消息，不是通用模板。</p>
      </div>
      <div class="card">
        <div class="card-icon">🤖</div>
        <h3>患者回复模拟</h3>
        <p>OpenClaw 自动模拟患者回复，含立即回复、延迟回复、不回复等真实场景。</p>
      </div>
      <div class="card">
        <div class="card-icon">🔍</div>
        <h3>回复智能解析</h3>
        <p>解析患者自然语言回复，提取用药依从性、症状变化、不良反应等结构化数据。</p>
      </div>
      <div class="card">
        <div class="card-icon">📋</div>
        <h3>病情追踪报告</h3>
        <p>为每位患者生成标准化病情追踪档案，记录完整随访时间线和趋势分析。</p>
      </div>
      <div class="card">
        <div class="card-icon">📊</div>
        <h3>医生每日日报</h3>
        <p>每天汇总所有患者情况，重点标注需关注患者和用药效果，推送至飞书。</p>
      </div>
    </div>
  </div>
</section>
```

**Step 2: 添加功能区样式**

```css
section { padding: 80px 0; }
.section-title { text-align: center; font-size: clamp(24px, 4vw, 36px); font-weight: 700; margin-bottom: 48px; }
#features { background: var(--bg2); }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
.card { background: var(--bg3); border: 1px solid var(--border); border-radius: var(--radius); padding: 28px; transition: border-color 0.2s, transform 0.2s; }
.card:hover { border-color: var(--accent); transform: translateY(-2px); }
.card-icon { font-size: 32px; margin-bottom: 16px; }
.card h3 { font-size: 18px; font-weight: 600; margin-bottom: 10px; }
.card p { color: var(--text2); font-size: 14px; line-height: 1.7; }
```

**Step 3: 提交**

```bash
git add docs/index.html
git commit -m "feat: 添加功能介绍区块"
```

---

### Task 4: 系统架构区块

**Files:**
- Modify: `docs/index.html`

**Step 1: 添加架构区 HTML（纯 CSS 流程图）**

```html
<section id="arch">
  <div class="container">
    <h2 class="section-title">系统架构</h2>
    <div class="flow">
      <div class="flow-item">
        <div class="flow-box">定时调度引擎<br><small>每10分钟 = 系统1天</small></div>
      </div>
      <div class="flow-arrow">↓</div>
      <div class="flow-row">
        <div class="flow-box small">扫描需随访患者</div>
        <div class="flow-box small">检查超时未回复</div>
        <div class="flow-box small">触发每日日报</div>
      </div>
      <div class="flow-arrow">↓</div>
      <div class="flow-row">
        <div class="flow-box small accent-box">生成个性化随访消息</div>
        <div class="flow-box small accent-box">模拟患者回复</div>
        <div class="flow-box small accent-box">解析回复→写入数据</div>
      </div>
      <div class="flow-arrow">↓</div>
      <div class="flow-item">
        <div class="flow-box highlight-box">飞书日报推送给医生 📱</div>
      </div>
    </div>
  </div>
</section>
```

**Step 2: 添加架构区样式**

```css
#arch { background: var(--bg); }
.flow { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.flow-item { width: 100%; max-width: 400px; }
.flow-row { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; width: 100%; }
.flow-box { background: var(--bg3); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; text-align: center; font-size: 15px; }
.flow-box.small { flex: 1; min-width: 160px; font-size: 13px; padding: 12px 16px; }
.flow-box.accent-box { border-color: rgba(124,58,237,0.5); background: rgba(124,58,237,0.1); }
.flow-box.highlight-box { border-color: var(--accent2); background: rgba(59,130,246,0.1); font-weight: 600; }
.flow-box small { display: block; color: var(--text2); font-size: 12px; margin-top: 4px; }
.flow-arrow { color: var(--text2); font-size: 20px; }
```

**Step 3: 提交**

```bash
git add docs/index.html
git commit -m "feat: 添加系统架构区块"
```

---

### Task 5: 资源链接区块 + 页脚

**Files:**
- Modify: `docs/index.html`

**Step 1: 添加资源区 HTML**

```html
<section id="resources">
  <div class="container">
    <h2 class="section-title">项目资源</h2>
    <div class="resource-grid">
      <a href="https://github.com/happytianhao/PatientClaw" class="resource-card" target="_blank">
        <div class="resource-icon">💻</div>
        <div>
          <div class="resource-title">代码仓库</div>
          <div class="resource-desc">GitHub · happytianhao/PatientClaw</div>
        </div>
      </a>
      <a href="docs/report/PatientClaw项目说明书.md" class="resource-card" target="_blank">
        <div class="resource-icon">📄</div>
        <div>
          <div class="resource-title">项目说明书</div>
          <div class="resource-desc">完整技术文档与设计说明</div>
        </div>
      </a>
      <div class="resource-card disabled">
        <div class="resource-icon">🖼️</div>
        <div>
          <div class="resource-title">项目海报</div>
          <div class="resource-desc">即将上线</div>
        </div>
      </div>
      <div class="resource-card disabled">
        <div class="resource-icon">🎬</div>
        <div>
          <div class="resource-title">演示视频</div>
          <div class="resource-desc">即将上线</div>
        </div>
      </div>
    </div>
  </div>
</section>

<footer>
  <div class="container">
    <p>PatientClaw · 北纬·龙虾大赛（第一届）· OpenClaw Hackathon</p>
    <p>主办方：中关村人工智能研究院 · 截止日期：2026年3月22日</p>
  </div>
</footer>
```

**Step 2: 添加资源区和页脚样式**

```css
#resources { background: var(--bg2); }
.resource-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }
.resource-card { display: flex; align-items: center; gap: 16px; background: var(--bg3); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px 24px; transition: border-color 0.2s; color: var(--text); }
.resource-card:hover:not(.disabled) { border-color: var(--accent2); text-decoration: none; }
.resource-card.disabled { opacity: 0.5; cursor: default; }
.resource-icon { font-size: 28px; flex-shrink: 0; }
.resource-title { font-weight: 600; font-size: 15px; margin-bottom: 4px; }
.resource-desc { color: var(--text2); font-size: 13px; }
footer { background: var(--bg); border-top: 1px solid var(--border); padding: 32px 0; text-align: center; color: var(--text2); font-size: 13px; line-height: 2; }
```

**Step 3: 提交**

```bash
git add docs/index.html
git commit -m "feat: 添加资源链接区块和页脚"
```

---

### Task 6: 配置 GitHub Pages

**Step 1: 确认 `docs/index.html` 已存在并推送**

```bash
git push origin main
```

**Step 2: 在 GitHub 仓库设置中启用 Pages**

1. 打开 https://github.com/happytianhao/PatientClaw/settings/pages
2. Source 选择 `Deploy from a branch`
3. Branch 选 `main`，目录选 `/docs`
4. 点击 Save

**Step 3: 等待部署完成（约1-2分钟），访问**

```
https://happytianhao.github.io/PatientClaw/
```

**Step 4: 将网站链接更新到 README.md 和 CLAUDE.md**

在 README.md 顶部添加：
```markdown
**项目网站**：https://happytianhao.github.io/PatientClaw/
```

**Step 5: 提交**

```bash
git add README.md CLAUDE.md
git commit -m "docs: 添加 GitHub Pages 网站链接"
git push origin main
```
