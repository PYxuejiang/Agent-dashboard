"""详情对话框"""

import os
import subprocess
import sys
from typing import Dict, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QWidget, QFrame
)


class ChatCard(QFrame):
    def __init__(self, chat_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.chat_data = chat_data
        self._build_ui()

    def _build_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            ChatCard {
                background: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 6px;
                margin: 4px 0;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        c = self.chat_data
        name = QLabel(f"💬 {c['chat']}")
        name.setStyleSheet("color:#cdd6f4; font-weight:bold; font-size:12px;")
        layout.addWidget(name)

        count = QLabel(f"{c['event_count']} 个事件")
        count.setStyleSheet("color:#6c7086; font-size:11px;")
        layout.addWidget(count)

        # 聊天目的
        if c.get("purpose"):
            purpose = QLabel(f"🎯 {c['purpose']}")
            purpose.setStyleSheet("color:#f9e2af; font-size:10px;")
            purpose.setWordWrap(True)
            layout.addWidget(purpose)

        if c.get("last_summary"):
            s = QLabel(f"摘要: {c['last_summary']}")
            s.setStyleSheet("color:#a6e3a1; font-size:11px;")
            s.setWordWrap(True)
            layout.addWidget(s)

        if c.get("last_next_action"):
            n = QLabel(f"下一步: {c['last_next_action']}")
            n.setStyleSheet("color:#89dceb; font-size:11px;")
            n.setWordWrap(True)
            layout.addWidget(n)

        # 文件变更
        files = c.get("files_changed", [])
        if files:
            file_title = QLabel(f"📝 文件变更 ({len(files)})")
            file_title.setStyleSheet("color:#fab387; font-size:10px; font-weight:bold;")
            layout.addWidget(file_title)
            for f in files:
                purpose = f.get("purpose", "")
                if purpose:
                    f_line = QLabel(f"  • {purpose}")
                    f_line.setStyleSheet("color:#6c7086; font-size:10px;")
                    f_line.setWordWrap(True)
                    layout.addWidget(f_line)

        issue = QLabel(f"问题: {c.get('open_issues', 0)} open / {c.get('solved_issues', 0)} solved")
        color = "#f38ba8" if c.get('open_issues', 0) > 0 else "#6c7086"
        issue.setStyleSheet(f"color:{color}; font-size:11px;")
        layout.addWidget(issue)

        # 按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)

        md_btn = QPushButton("打开 MD")
        md_btn.setStyleSheet(self._btn_style())
        md_btn.clicked.connect(lambda: self._open_file(c["files"]["md"]))

        jsonl_btn = QPushButton("打开 JSONL")
        jsonl_btn.setStyleSheet(self._btn_style())
        jsonl_btn.clicked.connect(lambda: self._open_file(c["files"]["jsonl"]))

        dir_btn = QPushButton("打开目录")
        dir_btn.setStyleSheet(self._btn_style())
        dir_btn.clicked.connect(lambda: self._open_dir(c["files"]["dir"]))

        btn_row.addWidget(md_btn)
        btn_row.addWidget(jsonl_btn)
        btn_row.addWidget(dir_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _btn_style(self):
        return """
            QPushButton {
                background: #313244;
                color: #cdd6f4;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
            }
            QPushButton:hover { background: #45475a; }
        """

    def _open_file(self, path: str):
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])

    def _open_dir(self, path: str):
        if sys.platform == "win32":
            subprocess.run(["explorer", path])
        elif sys.platform == "darwin":
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])


class DetailDialog(QDialog):
    def __init__(self, project_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle(f"{self.project_data['project']} - 详情")
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.resize(500, 600)

        self.setStyleSheet("""
            QDialog { background: #181825; }
            QLabel { color: #cdd6f4; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 标题
        p = self.project_data
        title = QLabel(f"📁 {p['project']}")
        title.setStyleSheet("color:#cba6f7; font-size:16px; font-weight:bold;")
        layout.addWidget(title)

        info = QLabel(f"{p['date']} | {p['event_count']} 个事件 | {p['chat_count']} 个聊天")
        info.setStyleSheet("color:#6c7086; font-size:11px;")
        layout.addWidget(info)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")

        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background:transparent;")
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(6)

        for chat in p.get("chats", []):
            card = ChatCard(chat)
            scroll_layout.addWidget(card)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #313244;
                color: #cdd6f4;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover { background: #45475a; }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
