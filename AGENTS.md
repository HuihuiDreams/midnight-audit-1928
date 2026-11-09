# AGENTS.md — Universal Agent Working Guidelines & Repository Protocols

> **Repository**: *The Midnight Audit (1928)*  
> **Target Audience**: All AI Agents (Claude, Gemini, GPT, Kiro, Codex, etc.) and Human Contributors  
> **Core Specifications**: [`.kiro/steering/aesthetic_autopsy.md`](.kiro/steering/aesthetic_autopsy.md), [`.kiro/specs/puzzle_engine_spec.md`](.kiro/specs/puzzle_engine_spec.md), [`.kiro/steering/architecture.md`](.kiro/steering/architecture.md)

---

## 1. 核心叙事与 UI 整体设计准则 (Core Narrative & Holistic UI Design)

在项目前期开发复盘中，曾暴露出严重的偏离倾向：**零散修补、东拼西凑、版面失控以及叙事跑偏**（例如因局部修补导致右下角多出突兀的 `Rows 51..80` 突出块，或偏离大学图书馆语境误入警局尸检报告）。所有操作此仓库的 Agent 必须将以下两条原则视为不可逾越的铁律：

### 1.1 绝不能偏离最初的故事设定 (Strict Grounding in the Original Lore)

* **故事源头与世界观**：
  * 本项目严格脱胎于 H.P. 洛夫克拉夫特经典克苏鲁短篇《敦威治恐怖事件》（*The Dunwich Horror*, 1928）与万圣夜设定。
* **玩家核心身份与情境**：
  * **时间**：**1928 年 10 月 31 日深夜（万圣节前夕 / All Hallows' Eve）**。
  * **地点**：密斯卡托尼克大学附属档案馆（Miskatonic University Annex Archive）。
  * **身份**：夜班审计员，接替昨晚离奇失踪的前任审计员 Ward 核查逾期图书借阅台账。
* **恐怖感来源（叙事母题）**：
  * **“死板规整、讲究借贷平衡的日常办公表格（Excel Ledger），被地板下潜伏的不可名状实体悄然侵蚀”**。
  * 实体并非外界打砸的怪兽，而是将复式记账法视为封印几何学、对账平账视为瓦解封印的实体（Wilbur Whateley / 敦威治无名双生子）。
* **物证自洽原则（Diegetic Artifacts）**：
  * 表格中的一切文本与模块必须是**1928 年大学档案馆办公场景内自然存在的真实公文**：
    1. 图书借阅逾期台账（`A6:I17`）；
    2. 前任 Ward 留下的黄色交接便签（`K4:U16`）；
    3. 特藏部夜班规程与显影剂卡（`W4:AN16`）；
    4. 烧焦的 ROT-3 封印密码条（`B20:H26`）；
    5. 馆长阿米蒂奇博士的特藏部封存指令（`B28:H49`）；
    6. 地下室建筑平面图与显影雷达（`K20:AN49`）。
* **禁止的叙事漂移（反模式）**：
  * ❌ **严禁引入与大学档案室无关的外部语境**：例如前期曾错误引入“阿卡姆警署法医解剖尸检报告”，破坏了前任去向的悬疑并破坏了学院场景；
  * ❌ **严禁随意堆砌无叙事意义的节日剪贴画或游戏展柜**：任何万圣节元素（如煤油烛台、南瓜灯、颅骨）必须作为祭坛或档案场景的有机组成部分，不可突兀乱贴。

---

### 1.2 界面整体设计原则（彻底杜绝东拼西凑）(Holistic UI Design)

* **严守 `A1:AN50` 全局画布边界**：
  * 界面由四象限严格拼合，左右两翼必须在 **第 50 行（`B50:H50` 与 `K50:AN50`）严丝合缝齐平收底**。
  * ❌ **绝不允许产生任何参差不齐的“突出块”**（如曾被废弃的底部 `Rows 51..80` 或右侧 `Columns AO..BC` 延伸）。
* **吸收异常行高**：
  * 第 13 行深渊（Row 13 Abyss）高度为 `220 pt`，具有视觉冲击力。右侧区域（`W4:AN16`）必须通过规整的公文卡片与边框设计**自然吸收**这一超大行高，禁止因行高拉伸导致内容畸变。
* **规整的正方形 1:1 微像素画布**：
  * 右下角 `K20:AN49`（30 列 × 30 行）是全表唯一的微像素主画布（行高 12pt，列宽 2.2，物理比例 1:1）。
  * 无论是建筑蓝图还是克苏鲁邪神颅骨神龛，所有 16-Bit 像素艺术都必须**完整收拢在此 30×30 画布内**，不准在外部零碎散落。
* **严格遵守 10 色 Morbid Archive 调色盘**：
  * 仅使用定义在 [`.kiro/steering/aesthetic_autopsy.md`](.kiro/steering/aesthetic_autopsy.md) 和 `src/backend/puzzle_state.py` 中的 10 种墨水/纸张色（骨白 `#D3CEB9`、腐纸 `#C5BFA8`、打字机碳黑 `#181614`、干血痂 `#2E0F0D`、磷光绿 `#3B533E`、便签黄 `#E5D982`、警告红 `#8A1C14`、冷灰 `#8A8D8F`、深渊黑 `#000000`、万圣橘 `#D9681A`）。
  * 可读文本一律使用 `Courier New`，严禁使用纯白 `#FFFFFF` 或现代荧光色作为普通界面底色。

---

## 2. Karpathy 编码准则 (Karpathy Guidelines)

在编写、重构或调试代码时，必须遵守以下四项核心准则：

### 2.1 Think Before Coding (思考先于编码)
* **不假设，不隐藏疑惑，亮明取舍**：
  * 动笔前明确列出假设。如果存在多种解读，主动呈现选项，绝不静默猜测。
  * 如果存在更简洁的实现路径，直接说明并据理力争。遇到不明确之处，立即指出并澄清。

### 2.2 Simplicity First (简洁第一)
* **解决问题的最少代码，不做任何投机性设计**：
  * 绝不添加未被要求的冗余功能。
  * 绝不为单次使用的代码构建过度抽象或通用层。
  * 绝不编写脱离实际场景的“防御性配置”或“未来扩展接口”。
  * 50 行能写完的逻辑绝不写 200 行。随时自问：“资深工程师会觉得这过度设计了吗？”

### 2.3 Surgical Changes (外科手术式变更)
* **只碰必须碰的代码，清理自己制造的代码废弃物**：
  * 编辑现有代码时，不要顺手“优化”相邻无关代码、注释或排版。
  * 不要重构没坏的代码。
  * 即使自己习惯不同，也必须严格遵循已有代码风格。
  * 每次修改产生的废弃 import、无用变量必须彻底清除；但绝不擅自删除原本就存在的遗留死代码。
  * **黄金检验标准**：改动的每一行代码，都必须能直接追溯到用户的当前需求。

### 2.4 Goal-Driven Execution (目标驱动执行)
* **明确成功标准，验证闭环**：
  * “添加功能/修改逻辑” → “先写/改测试，验证失败，再改代码，验证全绿”。
  * 拆解多步任务并提供可验证计划：
    ```
    1. [步骤] → 验证方式: [具体检查点]
    2. [步骤] → 验证方式: [具体检查点]
    ```

---

## 3. 测试驱动开发 (Test-Driven Development, TDD)

* **修改功能必须同步修改测试**：
  * 任何对 `src/backend/`、`scripts/build_ledger.py`、宏坐标或业务逻辑的功能修改，**必须同时新增或修改 `tests/` 中的单元与集成测试**。
  * 如果修改了单元格坐标、调色盘映射、状态机流转或 API Contract，对应的测试用例（如 `test_build_ledger.py`, `test_puzzle_state.py`, `test_server.py`, `test_mcp_server.py`）必须同步更新，保证测试能真正反映最新业务现实。
* **严禁测试红灯交付**：
  * 在任何任务结束前，必须在虚拟环境中执行全量测试：
    ```bash
    .venv/bin/pytest
    ```
  * 必须保证 **100% 测试通过**，严禁带着失败测试结束回复。

---

## 4. 文档与更新日志维护 (Documentation & CHANGELOG Protocol)

* **变更必记 CHANGELOG**：
  * 只要代码库发生功能变动、UI 调整、修复、重构或重要规范变更，**必须同步在 [`CHANGELOG.md`](CHANGELOG.md) 的 `[Unreleased]` 区块下记录**。
  * 严格遵循 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 与语义化版本规范分类（`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`）。
* **同步关联规范文档**：
  * 界面布局与视觉变动 → 同步 [`.kiro/steering/aesthetic_autopsy.md`](.kiro/steering/aesthetic_autopsy.md)；
  * 解谜逻辑与状态变动 → 同步 [`.kiro/specs/puzzle_engine_spec.md`](.kiro/specs/puzzle_engine_spec.md)；
  * 系统架构与跨平台 VBA 变动 → 同步 [`.kiro/steering/architecture.md`](.kiro/steering/architecture.md) 与 `README.md`。

---

## 5. 技术架构与系统铁律 (Architecture & Hard Constraints)

```text
┌────────────────────────────────────────────────────────┐
│             Excel 1990s Client (.xlsm / VBA)           │
│  - Morbid Archive UI (Stripped menus, Courier New)    │
│  - Worksheet Event Hooks (Change, SelectionChange)     │
│  - Sensory FX (Cell spreading, eye blink, screen tremor)│
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP POST / Event Queue (JSON)
                           ▼
┌────────────────────────────────────────────────────────┐
│             Local Python Daemon (2026)                  │
│  - FastAPI Bridge (localhost:8000)                     │
│  - State Machine & Event Buffering (game_state.json)   │
│  - Dual-mode (Daemon Active vs Offline Fallback)       │
└──────────────────────────┬─────────────────────────────┘
                           │ JSON-RPC 2.0 (stdio / SSE)
                           ▼
┌────────────────────────────────────────────────────────┐
│             Agent Mastermind (AI Agent IDE / CLI)      │
│  - Model Context Protocol (MCP) Server                 │
│  - Tools: inspect_ledger, haunt_spreadsheet, judge... │
│  - Dynamic Haunting & Eldritch Personality Injection   │
└────────────────────────────────────────────────────────┘
```

1. **Windows 独占文件锁铁律 (Windows File Lock Avoidance)**：
   * ⚠️ **严禁在 Excel 打开状态下使用 `openpyxl` 读写 `.xlsm` 文件**。
   * `openpyxl` 仅限离线构建脚本（`scripts/build_ledger.py`）。运行时的一切单元格读写与视觉反馈必须通过 VBA 本地执行或 HTTP Bridge (`/api/event`, `/api/haunt`) 交互。
2. **跨平台 PtrSafe 与 macOS 降级支持**：
   * 所有 Win32 API 声明必须封装在 `#If VBA7 ... #ElseIf Mac ... #End If` 条件编译块中。
   * macOS 上无 `kernel32`/`user32`，必须自动降级为 AppleScript 蜂鸣与视觉抖动。
3. **紧急复位快捷键 (`Ctrl+Shift+R`)**：
   * 恢复 Excel 菜单栏、公式栏与网格线，防止意外锁死用户界面。

---

## 6. Agent 协作与委派规范 (Agent Delegation Pattern)

* **通用多代理/子任务委派**：
  * 当面对大批量的矩阵坐标生成、重复性图表构建或机械性代码落地时，可委派更快速轻量的子代理（如轻量模型）执行；
  * **主代理（Lead Agent）必须亲自把关验收**：对子代理提交的代码进行严格审查、执行 `pytest` 全量测试套件，并对生成的表格资产进行视觉与规格核验。
