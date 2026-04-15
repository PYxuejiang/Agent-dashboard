# AI Journal Dashboard - 完整技术文档

## 项目概述

AI Journal Dashboard 是一个基于 PySide6 的桌面悬浮组件，用于实时监控和展示 MCP Agent 的工作日志。

### 核心功能
- 📓 桌面小图标，点击展开/收起主面板
- 📅 Today/Yesterday/7-Day 三种视图切换
- 🔄 自动监听日志文件变化并刷新
- 📊 项目背景、文件变更、问题统计可视化
- 🖱️ 支持拖拽移动、右下角缩放
- 🗂️ 快速打开 MD/JSONL 文件和目录

---

## 项目结构

```
D:/PyCharm_AI/
├── app.py                          # 主程序入口
├── config.json                     # 配置文件
├── requirements.txt                # Python 依赖
├── example_usage.py                # MCP Logger 使用示例
├── README.md                       # 项目说明
├── .gitignore                      # Git 忽略规则
├── 技术.txt                        # 技术改造说明
│
├── Dai_journal/                    # MCP 日志记录模块
│   ├── __init__.py
│   └── mcp_logger.py               # 日志记录核心
│
├── Dai_journalstore/               # 日志存储目录（被 .gitignore 排除）
│   └── [项目名]/
│       └── [日期]/
│           ├── *.md                # Markdown 格式日志
│           └── *.jsonl             # JSONL 格式结构化日志
│
└── dashboard/                      # 桌面组件
    ├── __init__.py
    ├── parser.py                   # 日志解析器
    ├── watcher.py                  # 文件监听器
    └── ui/                         # UI 组件
        ├── __init__.py
        ├── main_widget.py          # 主悬浮窗
        ├── detail_dialog.py        # 详情对话框
        └── summary_widget.py       # 7天汇总视图
```

---

## 核心模块详解

### 1. app.py - 主程序入口

**职责：**
- 初始化 Qt 应用
- 创建主窗口、小图标、系统托盘
- 连接信号槽，处理视图切换
- 启动文件监听和定时刷新

**关键代码：**

```python
def main():
    app = QApplication(sys.argv)
    
    # 主窗口 + 小图标
    widget = MainWidget(config)
    float_icon = FloatIcon(widget)
    
    # 7-Day 汇总组件
    summary_widget = SummaryWidget()
    widget.week_layout.addWidget(summary_widget)
    
    # 刷新函数
    def refresh_today():
        projects = get_today_overview(store_path)
        widget.update_projects(projects, "today")
    
    # 视图切换信号
    widget.date_mode_changed.connect(on_mode_changed)
    
    # 文件监听
    watcher = LogWatcher(store_path, on_file_change)
    watcher.start()
    
    # 定时刷新（默认 2 秒）
    timer = QTimer()
    timer.timeout.connect(on_file_change)
    timer.start(interval)
    
    # 系统托盘
    tray = QSystemTrayIcon(app)
    tray.setIcon(_create_tray_icon())
```

**托盘图标生成：**
```python
def _create_tray_icon() -> QIcon:
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor("#cba6f7"))  # 紫色圆点
    painter.drawEllipse(1, 1, 14, 14)
    return QIcon(pixmap)
```

---

### 2. dashboard/parser.py - 日志解析器

**职责：**
- 扫描 `store_path` 目录
- 解析 JSONL 格式日志
- 提取项目背景、文件变更、问题统计
- 聚合今日/昨日/7天数据

**核心函数：**

#### `get_today_overview(store_path) -> List[Dict]`
返回今日所有项目的聚合摘要。

#### `get_yesterday_overview(store_path) -> List[Dict]`
返回昨日所有项目的聚合摘要。

#### `get_7day_summary(store_path) -> Dict`
返回最近7天的汇总统计。

**数据提取逻辑：**

```python
for ev in events:
    t = ev.get("type")
    payload = ev.get("payload", {})
    
    # 提取项目目的（从 prompt）
    if t == "prompt":
        project_purpose = payload.get("abstract_task")
    
    # 提取方法（从 issue 的 diagnosis）
    if t == "issue":
        project_method = payload.get("diagnosis")
    
    # 提取文件变更（从 command）
    if t == "command":
        cmd = payload.get("command")
        purpose = payload.get("purpose")
        chat_files.append({"command": cmd, "purpose": purpose})
```

**返回数据结构：**

```python
{
    "project": "项目名",
    "date": "2026-04-15",
    "event_count": 42,
    "chat_count": 3,
    "last_summary": "最近完成的摘要",
    "last_next_action": "下一步行动",
    "open_issues": 2,
    "solved_issues": 5,
    "purpose": "项目目的（从 prompt 提取）",
    "method": "实现方法（从 issue.diagnosis 提取）",
    "files_changed": [
        {"command": "git diff", "purpose": "查看代码变更"}
    ],
    "chats": [...]
}
```

---

### 3. dashboard/watcher.py - 文件监听器

**职责：**
- 使用 `watchdog` 监听日志目录
- 检测 `.jsonl` 和 `.md` 文件的创建/修改
- 触发回调函数刷新 UI

**实现：**

```python
class LogWatcher:
    def __init__(self, store_path: str, on_change):
        self.store_path = Path(store_path)
        self.on_change = on_change
        self.observer = None
    
    def start(self):
        handler = _LogChangeHandler(self.on_change)
        self.observer = Observer()
        self.observer.schedule(handler, str(self.store_path), recursive=True)
        self.observer.start()
```

**事件处理：**

```python
class _LogChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith((".jsonl", ".md")):
            self.callback()
    
    def on_modified(self, event):
        if event.src_path.endswith((".jsonl", ".md")):
            self.callback()
```

---

### 4. dashboard/ui/main_widget.py - 主悬浮窗

**职责：**
- 显示项目卡片列表
- 提供 Today/Yesterday/7-Day 导航栏
- 支持拖拽移动和右下角缩放
- 发射信号通知视图切换

**关键组件：**

#### FloatIcon - 小悬浮图标

```python
class FloatIcon(QWidget):
    def __init__(self, panel: "MainWidget"):
        self.panel = panel
        self.setFixedSize(48, 48)
        # 显示 📓 图标
        lbl = QLabel("📓", self)
    
    def mouseReleaseEvent(self, event):
        if not moved:
            if self.panel.isVisible():
                self.panel.hide()
            else:
                self.panel.show()
```

#### MainWidget - 主面板

**窗口属性：**
```python
self.setWindowFlags(
    Qt.FramelessWindowHint |      # 无边框
    Qt.WindowStaysOnTopHint |     # 置顶
    Qt.Tool                       # 工具窗口
)
self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
```

**日期导航栏：**
```python
self.today_btn = QPushButton("Today")
self.yesterday_btn = QPushButton("Yesterday")
self.week_btn = QPushButton("7-Day")

self.today_btn.clicked.connect(lambda: self._switch_mode("today"))
```

**StackedWidget 切换内容：**
```python
self.stacked = QStackedWidget()
self.stacked.addWidget(self.today_scroll)      # 索引 0
self.stacked.addWidget(self.yesterday_scroll)  # 索引 1
self.stacked.addWidget(self.week_widget)       # 索引 2
```

**拖拽缩放实现：**
```python
def _in_resize_zone(self, pos: QPoint) -> bool:
    return (pos.x() >= self.width() - 16 and
            pos.y() >= self.height() - 16)

def mousePressEvent(self, event):
    if self._in_resize_zone(event.position().toPoint()):
        self._resizing = True
    else:
        self._drag_pos = ...  # 拖拽移动

def mouseMoveEvent(self, event):
    if self._resizing:
        self.resize(new_width, new_height)
    elif self._drag_pos:
        self.move(new_position)
```

#### ProjectCard - 项目卡片

**显示内容：**
- 项目名 + 事件数
- 🎯 项目目的（`purpose`）
- 最近摘要（`last_summary`）
- → 下一步行动（`last_next_action`）
- 📝 文件变更（`files_changed`）
- 问题统计（`open_issues` / `solved_issues`）

**点击事件：**
```python
def mousePressEvent(self, event):
    if event.button() == Qt.LeftButton:
        self.clicked.emit(self.project_data)
```

---

### 5. dashboard/ui/detail_dialog.py - 详情对话框

**职责：**
- 显示单个项目的所有聊天
- 每个聊天显示目的、摘要、文件变更
- 提供"打开 MD/JSONL/目录"按钮

**ChatCard 显示内容：**
```python
- 💬 聊天名称
- 事件数
- 🎯 聊天目的
- 摘要
- 下一步
- 📝 文件变更列表
- 问题统计
- [打开 MD] [打开 JSONL] [打开目录]
```

**打开文件：**
```python
def _open_file(self, path: str):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])
```

---

### 6. dashboard/ui/summary_widget.py - 7天汇总视图

**职责：**
- 显示最近7天的统计数据
- 项目背景（目的 + 方法）
- 问题统计、里程碑、标签云
- 项目活跃度、最近完成

**显示卡片：**

```python
def _create_card(self, title: str, lines: list) -> QFrame:
    card = QFrame()
    layout = QVBoxLayout(card)
    
    title_lbl = QLabel(title)
    layout.addWidget(title_lbl)
    
    for line in lines:
        lbl = QLabel(line)
        layout.addWidget(lbl)
    
    return card
```

**项目背景卡片：**
```python
backgrounds = data.get("project_backgrounds", {})
for proj, bg in backgrounds.items():
    purpose = bg.get("purpose")  # 从 prompt.abstract_task
    method = bg.get("method")    # 从 issue.diagnosis
    bg_lines.append(f"**{proj}**")
    bg_lines.append(f"  目的: {purpose}")
    bg_lines.append(f"  方法: {method}")
```

---

### 7. Dai_journal/mcp_logger.py - MCP 日志记录模块

**职责：**
- 按项目/日期/聊天主题组织日志
- 同时生成 Markdown 和 JSONL 格式
- 提供便捷函数记录事件

**使用示例：**

```python
from Dai_journal.mcp_logger import (
    set_project, set_chat,
    log_prompt, log_close_step, log_issue, log_next_action
)

# 设置上下文
set_project("PTM_GNN_SEQ")
set_chat("fusion_stageB_w63")

# 记录任务
log_prompt("完成 fusion stageB w63 后台命令整理")

# 记录完成
log_close_step("已完成命令整理，并统一日志输出路径")

# 记录问题
log_issue("发现配置文件缺少参数", status="open")

# 记录下一步
log_next_action("继续比较 stageB 与 stageA 指标差异")
```

**日志存储路径：**
```
Dai_journalstore/
└── PTM_GNN_SEQ/
    └── 2026-04-15/
        ├── fusion_stageB_w63.md
        └── fusion_stageB_w63.jsonl
```

---

## 配置文件 config.json

```json
{
  "store_path": "D:/ai_journal/store",
  "window_opacity": 0.95,
  "auto_refresh": true,
  "refresh_interval": 2,
  "window_position": {
    "x": null,
    "y": null
  },
  "window_size": {
    "width": 400,
    "height": 600
  }
}
```

**参数说明：**
- `store_path`: 日志存储目录（绝对路径）
- `window_opacity`: 窗口透明度（0.0-1.0）
- `auto_refresh`: 是否自动刷新
- `refresh_interval`: 刷新间隔（秒）
- `window_position`: 窗口初始位置（null 表示默认）
- `window_size`: 窗口初始大小

---

## 依赖 requirements.txt

```
PySide6>=6.6.0
watchdog>=3.0.0
markdown>=3.5.0
```

**安装：**
```bash
pip install -r requirements.txt
```

---

## 运行方式

### 1. 创建 Conda 环境

```bash
conda create -n ai_journal_dashboard python=3.10 -y
conda activate ai_journal_dashboard
```

### 2. 安装依赖

```bash
cd D:\PyCharm_AI
pip install -r requirements.txt
```

### 3. 配置日志路径

编辑 `config.json`，设置 `store_path` 为你的日志目录：

```json
{
  "store_path": "D:/ai_journal/store"
}
```

### 4. 启动程序

```bash
python app.py
```

---

## 交互说明

### 桌面小图标
- **拖拽**：按住左键移动图标位置
- **点击**：展开/收起主面板

### 主面板
- **拖拽**：按住标题栏移动窗口
- **缩放**：拖拽右下角调整大小
- **导航栏**：点击 Today/Yesterday/7-Day 切换视图
- **项目卡片**：点击查看详情

### 详情对话框
- **打开 MD**：用默认编辑器打开 Markdown 文件
- **打开 JSONL**：用默认编辑器打开 JSONL 文件
- **打开目录**：在资源管理器中打开日志目录

### 系统托盘
- **右键菜单**：显示/退出
- **左键点击**：显示主面板

---

## 数据流程

```
MCP Agent 工作
    ↓
mcp_logger.py 记录日志
    ↓
Dai_journalstore/[项目]/[日期]/[聊天].jsonl
    ↓
watchdog 监听文件变化
    ↓
parser.py 解析 JSONL
    ↓
提取：项目目的、方法、文件变更、问题统计
    ↓
main_widget.py 显示项目卡片
    ↓
用户点击查看详情
    ↓
detail_dialog.py 显示聊天详情
```

---

## 日志格式说明

### JSONL 事件类型

#### set_context - 设置上下文
```json
{
  "type": "set_context",
  "project": "PTM_GNN_SEQ",
  "chat": "fusion_stageB_w63",
  "milestone": "window63_ablation",
  "context": {
    "tags": ["baseline", "phospho"],
    "priority": "high"
  }
}
```

#### prompt - 任务开始
```json
{
  "type": "prompt",
  "payload": {
    "abstract_task": "完成 fusion stageB w63 后台命令整理",
    "category": "project_progress"
  }
}
```

#### command - 命令执行
```json
{
  "type": "command",
  "payload": {
    "command": "git diff",
    "purpose": "查看代码变更"
  }
}
```

#### issue - 问题记录
```json
{
  "type": "issue",
  "payload": {
    "problem": "配置文件缺少参数",
    "diagnosis": "需要添加 batch_size 参数",
    "status": "open"
  }
}
```

#### close_step - 步骤完成
```json
{
  "type": "close_step",
  "payload": {
    "summary": "已完成命令整理",
    "next_action": "继续比较指标差异"
  }
}
```

---

## 样式主题

使用 Catppuccin Mocha 配色：

```python
# 主色调
background = "#181825"      # 深色背景
surface = "#1e1e2e"         # 卡片背景
border = "#313244"          # 边框
text = "#cdd6f4"            # 主文本

# 强调色
purple = "#cba6f7"          # 标题
blue = "#89b4fa"            # 按钮激活
green = "#a6e3a1"           # 摘要
cyan = "#89dceb"            # 下一步
yellow = "#f9e2af"          # 项目目的
peach = "#fab387"           # 文件变更
red = "#f38ba8"             # 问题
gray = "#6c7086"            # 次要文本
```

---

## 常见问题

### Q: 显示"今日暂无日志"？
A: 检查 `config.json` 中的 `store_path` 是否正确，确保路径下有对应日期的日志文件。

### Q: 文件监听不生效？
A: 确保 `watchdog` 已正确安装，且日志目录有读取权限。

### Q: 托盘图标不显示？
A: Windows 系统可能需要在"任务栏设置"中启用托盘图标显示。

### Q: 窗口白边无法去除？
A: 已在代码中设置透明背景，如仍有白边，可能是系统渲染问题，尝试调整 `window_opacity`。

### Q: 如何修改刷新间隔？
A: 编辑 `config.json`，修改 `refresh_interval` 值（单位：秒）。

---

## 开发建议

### 添加新的事件类型
1. 在 `mcp_logger.py` 中添加便捷函数
2. 在 `parser.py` 中添加提取逻辑
3. 在 UI 组件中添加显示逻辑

### 自定义样式
修改各 UI 组件中的 `setStyleSheet()` 调用。

### 添加新的视图
1. 在 `parser.py` 中添加数据聚合函数
2. 创建新的 Widget 组件
3. 在 `main_widget.py` 中添加到 StackedWidget
4. 在导航栏添加按钮

---

## 性能优化

- 使用 `watchdog` 而非轮询，减少 CPU 占用
- JSONL 逐行解析，避免大文件内存溢出
- 卡片懒加载，只显示可见区域
- 定时器间隔可配置，平衡实时性与性能

---

## 安全注意事项

- 日志文件可能包含敏感信息，建议不要提交到公开仓库
- `.gitignore` 已排除 `Dai_journalstore/` 目录
- 如需分享，请先脱敏处理

---

## 许可证

MIT License

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## 更新日志

### v1.1.0 (2026-04-15)
- ✨ 新增 Today/Yesterday/7-Day 视图切换
- ✨ 提取并显示项目目的、方法、文件变更
- ✨ 7-Day 视图显示项目背景
- 🐛 修复白边问题
- 🐛 修复托盘图标告警

### v1.0.0 (2026-04-14)
- 🎉 初始版本发布
- ✨ 桌面小图标 + 主面板
- ✨ 实时监听日志变化
- ✨ 项目卡片显示
- ✨ 详情对话框
- ✨ 系统托盘集成
