# 午夜审计 (1928)

> *"灵感源自 H.P. 洛夫克拉夫特《敦威治恐怖事件》(1928)"*

[![Kiroween 2026 Hackathon](https://img.shields.io/badge/Kiroween_2026-Frankenstein_Track-8A1C14.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-454F48.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Excel VBA](https://img.shields.io/badge/Client-Excel_VBA_1990s-D3CEB9.svg)](#)

---

## 📖 简介："弗兰肯斯坦"概念

**午夜审计 (1928)** 是跨越四十年的异构技术缝合体：
- **客户端 (1990s)**：伪装成密斯卡托尼克大学附属档案馆逾期台账的 Microsoft Excel VBA 工作簿。
- **本地守护进程 (2026)**：现代 Python FastAPI 微服务，负责状态同步与事件缓冲。
- **智能大脑 (2026)**：通过模型上下文协议 (MCP) 集成的 Kiro IDE Agent，实时监控审计员击键并以此操控表格。

### 🩸 零门槛原则 (3–5 分钟流程)
无需任何克苏鲁神话背景知识。整个体验完全限定在深夜查账这一日常办公任务中。所有线索都内嵌于表格内的黄色"交接便签"中。

---

## 🕹️ 快速上手与游玩指南

### 第一步：克隆项目并搭建本地后端（离线游玩可选）
```bash
# 克隆仓库
git clone https://github.com/example/the-midnight-audit-1928.git
cd "The Midnight Audit (1928)"

# 创建 Python 虚拟环境
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # runtime + test tools (use requirements.txt for runtime only)

# 安装 uv（Kiro MCP 与验证钩子需要）
# macOS 使用 Homebrew:
brew install uv
# 其他平台: https://docs.astral.sh/uv/getting-started/installation
uv --version

# 启动本地守护进程桥接
python3 -m src.backend.server
# (或: python3 src/backend/server.py)
```
*(守护进程默认运行于 `http://127.0.0.1:8000`；可通过 `SERVER_PORT` 环境变量自定义端口)*

### 第二步：Kiro MCP 集成（可选）
本项目自带 `.kiro/settings/mcp.json`。Kiro 会使用 `uv` 启动 `midnight-audit-mcp` 服务器，因此在 Kiro 中打开项目前请先安装 `uv`。配置重载后，Agent 即可使用 `inspect_ledger`、`haunt_spreadsheet` 和 `judge_ritual` 等 MCP 工具。

`.kiro/hooks/verify-backend-and-ledger.json` 中的保存钩子同样依赖 `uv`。当后端 Python 文件或 `scripts/build_ledger.py` 被保存时，它会运行完整测试套件，仅在测试通过后重建模板。

手动验证相同命令：

```bash
uv run --with-requirements requirements-dev.txt python -m pytest -q && \
  uv run --with-requirements requirements.txt python scripts/build_ledger.py
```

### 第三步：生成或打开台账
```bash
# 生成初始"阴森档案"模板
python3 scripts/build_ledger.py
```

#### 将 VBA 模块导入 Excel（一次性配置）
由于 `openpyxl` 仅生成 `.xlsx` 的样式与排版，而 Excel 宏代码必须由 Excel 自身编译进专有的二进制容器 (`vbaProject.bin`)，因此只需在 Excel 中**一次性**导入 VBA 模块并另存为 `.xlsm`。之后每次打开该 `.xlsm` 文件即可直接游玩：

1. **打开模板文件**：使用 Microsoft Excel 打开 `Midnight_Audit_1928_Template.xlsx`。
2. **打开 VBA 编辑器**：
   - **Windows**：按下 **`Alt + F11`**
   - **macOS**：按下 **`Fn + Option + F11`**（或顶部菜单：*工具 > 宏 > Visual Basic 编辑器*）。
3. **导入 3 个标准模块（`.bas` 文件）**：
   - 在 VBA 编辑器菜单中选择 **文件 > 导入文件...**，从 `src/vba/` 导入以下 3 个 `.bas` 文件：
     - `src/vba/M_Bootstrap.bas`
     - `src/vba/M_DaemonBridge.bas`
     - `src/vba/M_HorrorFX.bas`（内含 30×30 实体面孔点阵的生成副本；修改 `puzzle_state.py` 中的 `ENTITY_FACE_MATRIX` 后，运行 `python scripts/sync_vba_radar.py` 并重新导入）
4. **粘贴 2 个文档事件类（`.cls` 文件 — 仅限复制粘贴）**：
   - ⚠️ *重要*：`Sheet1_Archive.cls` 和 `ThisWorkbook.cls` 是 Excel 文档类模块。**切勿**使用 *文件 > 导入文件*（导入会创建无法拦截工作表/工作簿事件的独立类模块）。
   - 在左侧 VBA 工程树中双击 **`Sheet1 (Audit_Ledger_1928)`**，用文本编辑器打开 `src/vba/Sheet1_Archive.cls`，复制**从第 10 行 `Option Explicit` 到末尾的所有代码**（跳过前 9 行 `VERSION 1.0 CLASS ... Attribute VB_...`），粘贴到 `Sheet1` 代码窗口。
   - 在左侧工程树双击 **`ThisWorkbook`**，用文本编辑器打开 `src/vba/ThisWorkbook.cls`，同样复制**从第 10 行 `Option Explicit` 到末尾的所有代码**，粘贴到 `ThisWorkbook` 代码窗口。
5. **另存为 `.xlsm`**：
   - 返回 Excel，选择 **文件 > 另存为...**，文件格式选择 **Excel 启用宏的工作簿 (`.xlsm`)**，保存为 `Midnight_Audit_1928_Template.xlsm`。

### 第四步：Excel 安全与宏设置
1. 关闭并重新打开 `Midnight_Audit_1928_Template.xlsm`。当 Excel 提示时，点击 **"启用内容"** 或 **"启用宏"**（`Workbook_Open` 会自动启动 1928 档案室界面）。
2. **紧急恢复 (`Ctrl + Shift + R`)**：如需随时恢复标准 Excel 工具栏、功能区、公式栏和网格线，按下 **`Ctrl + Shift + R`**（或手动运行 `EmergencyReset` 宏）。

### 第五步：解开四阶段审计循环
1. **第一阶段（账目差异）**：阅读黄色交接便签 (`K4:AN12`) 规则 1。查看第 7 行借阅者 `Wilbur Whateley`（逾期 140 天）。在 **`H7`** 单元格直接输入数字 `7.00`（或 `7`）（140 × $0.05）并按回车（无需手动输入 `$` 货币符号，单元格已预设货币格式，会自动显示为 `$7.00`）。观看第 13 行深渊苏醒。
2. **第二阶段（隐形入侵者）**：阅读规则 2。点击绿色 **`[ SPRAY REAGENT ]`** 按钮 (`K18:AN18`)。观看 30×30 邪教祭坛与闪烁的宇宙之眼 (`W34:X35`) 显形。
3. **第三阶段（打字机劫持）**：阅读规则 3。解码烧焦的 ROT-3 密码条 (`B21:H28`：`VHDO WKH GHHS YDXOW` -> `SEAL THE DEEP VAULT`)。先在 **`B18`** 单元格输入任意字符体验打字机劫持（自动篡改为 `YOUR SALARY CANNOT SAVE YOU`），然后输入真正的封印短语 **`SEAL THE DEEP VAULT`** 并按回车 —— `[ SEAL ARCHIVE ]` (`C18:D18`) 变为警告红。
4. **第四阶段（午夜结算）**：点击 **`[ SEAL ARCHIVE ]`** (`C18:D18`)。雷电闪烁，窗口震动，台账被永久盖上 `OCTOBER 31, 1928 - 00:01 AM` 封存印章。

---

## 🏛️ 系统架构

```text
┌────────────────────────────────────────────────────────┐
│             Excel 1990s 客户端 (.xlsm / VBA)           │
│  - 阴森档案界面 (隐藏菜单, Courier New 字体)          │
│  - 工作表事件钩子 (Change, SelectionChange)            │
│  - 感官特效 (单元格扩散, 眼睛眨眼, 屏幕震颤)          │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP POST / 事件队列 (JSON)
                           ▼
┌────────────────────────────────────────────────────────┐
│             本地 Python 守护进程 (2026)                │
│  - FastAPI 桥接 (localhost:8000)                       │
│  - 状态机与事件缓冲 (game_state.json)                  │
│  - 双模式 (守护进程激活 vs 离线降级)                   │
└──────────────────────────┬─────────────────────────────┘
                           │ JSON-RPC 2.0 (stdio / SSE)
                           ▼
┌────────────────────────────────────────────────────────┐
│             Kiro 智能 IDE (智能大脑)                   │
│  - 模型上下文协议 (MCP) 服务器                         │
│  - 工具: inspect_ledger, haunt_spreadsheet, judge...  │
│  - 动态操控与古老恐怖人格注入                         │
└────────────────────────────────────────────────────────┘
```

---

## 🛡️ Kiro 规范系统 (`/.kiro`) 与 Agent 准则

本项目严格遵循 Kiro Agent 引导与规范标准构建：
- [`.kiro/steering/agent_guidelines.md`](.kiro/steering/agent_guidelines.md)：核心 Agent 工作准则、整体 UI 设计标准、Karpathy 准则、TDD 协议与故事背景。
- [`.kiro/steering/architecture.md`](.kiro/steering/architecture.md)：跨平台 PtrSafe VBA 规则与 Windows 文件锁规避。
- [`.kiro/steering/aesthetic_autopsy.md`](.kiro/steering/aesthetic_autopsy.md)："阴森档案"配色方案、字体规则与第 13 行深渊。
- [`.kiro/steering/cosmic_entity_persona.md`](.kiro/steering/cosmic_entity_persona.md)：威尔伯·沃特雷的官僚恶魔人格。
- [`.kiro/specs/puzzle_engine_spec.md`](.kiro/specs/puzzle_engine_spec.md)：四阶段状态转换与离线降级规则。
- [`.kiro/specs/mcp_contract.md`](.kiro/specs/mcp_contract.md)：JSON-RPC MCP 工具模式与 HTTP 桥接契约。

---

## 🧪 测试

运行自动化后端与解谜验证测试：
```bash
pytest tests/ -v
```

---

## 📜 许可证
MIT 许可证。灵感源自 H.P. 洛夫克拉夫特《敦威治恐怖事件》(1928，公共领域)。
