"""7天汇总视图"""

from typing import Dict, Any
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame


class SummaryWidget(QWidget):
    """7天汇总统计面板"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background:transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)

        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)

    def update_summary(self, data: Dict[str, Any]):
        # 清空旧内容
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not data or data.get("total_events", 0) == 0:
            empty = QLabel("最近7天暂无数据")
            empty.setStyleSheet("color:#6c7086; font-size:12px;")
            empty.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(empty)
            return

        # 标题
        title = QLabel(f"📊 7天汇总 ({data['date_range']})")
        title.setStyleSheet("color:#cba6f7; font-size:14px; font-weight:bold;")
        self.content_layout.addWidget(title)

        # 总览卡片
        overview = self._create_card("总览", [
            f"总事件数: {data['total_events']}",
            f"活跃项目: {data['active_projects']}",
        ])
        self.content_layout.addWidget(overview)

        # 项目背景
        backgrounds = data.get("project_backgrounds", {})
        if backgrounds:
            bg_lines = []
            for proj, bg in list(backgrounds.items())[:3]:  # 只显示前3个
                purpose = bg.get("purpose", "")
                method = bg.get("method", "")
                if purpose:
                    bg_lines.append(f"**{proj}**")
                    bg_lines.append(f"  目的: {purpose[:80]}...")
                    if method:
                        bg_lines.append(f"  方法: {method[:80]}...")
            if bg_lines:
                bg_card = self._create_card("项目背景", bg_lines)
                self.content_layout.addWidget(bg_card)

        # 问题统计
        issues = data.get("issues", {})
        issue_card = self._create_card("问题统计", [
            f"总计: {issues.get('total', 0)}",
            f"🔴 Open: {issues.get('open', 0)}",
            f"🟢 Solved: {issues.get('solved', 0)}",
        ])
        self.content_layout.addWidget(issue_card)

        # 里程碑
        milestones = data.get("milestones", {})
        if milestones:
            ms_lines = [f"• {k}: {v}次" for k, v in list(milestones.items())[:5]]
            ms_card = self._create_card("里程碑 Top5", ms_lines)
            self.content_layout.addWidget(ms_card)

        # 标签
        tags = data.get("tags", {})
        if tags:
            tag_lines = [f"#{k} ({v})" for k, v in list(tags.items())[:8]]
            tag_card = self._create_card("标签", tag_lines)
            self.content_layout.addWidget(tag_card)

        # 项目活跃度
        proj_act = data.get("project_activity", {})
        if proj_act:
            proj_lines = [f"• {k}: {v}条" for k, v in list(proj_act.items())[:5]]
            proj_card = self._create_card("项目活跃度 Top5", proj_lines)
            self.content_layout.addWidget(proj_card)

        # 最近完成
        summaries = data.get("recent_summaries", [])
        if summaries:
            sum_lines = [f"✓ {s[:80]}" for s in summaries[-5:]]
            sum_card = self._create_card("最近完成", sum_lines)
            self.content_layout.addWidget(sum_card)

        self.content_layout.addStretch()

    def _create_card(self, title: str, lines: list) -> QFrame:
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("""
            QFrame {
                background: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 6px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color:#89dceb; font-weight:bold; font-size:12px;")
        layout.addWidget(title_lbl)

        for line in lines:
            lbl = QLabel(line)
            lbl.setStyleSheet("color:#cdd6f4; font-size:11px;")
            lbl.setWordWrap(True)
            layout.addWidget(lbl)

        return card
