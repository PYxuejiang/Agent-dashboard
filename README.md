# AI Journal Dashboard

一个用于监控和展示 MCP Agent 工作日志的桌面悬浮组件。

## 功能特性

- 🖥️ 桌面悬浮窗口，置顶显示
- 📊 实时监控项目日志变化
- 📝 显示今日所有项目的工作摘要
- 🔍 点击查看详细信息
- 📂 快速打开日志文件和目录
- 🔄 自动刷新，无需手动操作

## 项目结构

```
ai_journal_dashboard/
├── Dai_journal/           # MCP Logger 模块
│   └── mcp_logger.py      # 日志记录核心逻辑
├── Dai_journalstore/      # 日志存储目录
│   └── [项目名]/
│       └── [日期]/
│           ├── *.md       # Markdown 格式日志
│           └── *.jsonl    # JSONL 格式结构化日志
├── dashboard/             # 桌面组件
│   ├── app.py            # 主程序入口
│   ├── parser.py         # 日志解析器
│   ├── watcher.py        # 文件监听器
│   └── ui/               # UI 组件
│       ├── main_widget.py    # 主窗口
│       └── detail_dialog.py  # 详情对话框
├── requirements.txt       # Python 依赖
└── config.json           # 配置文件
```

## 安装

```bash
pip install -r requirements.txt
```

## 使用

### 启动桌面组件

```bash
python dashboard/app.py
```

### MCP Logger 使用

MCP Logger 会自动记录 Agent 的工作日志到 `Dai_journalstore` 目录。

## 配置

编辑 `config.json` 修改配置：

```json
{
  "store_path": "./Dai_journalstore",
  "window_opacity": 0.95,
  "auto_refresh": true,
  "refresh_interval": 2
}
```

## 开发

- Python 3.8+
- PySide6
- watchdog

## License

MIT