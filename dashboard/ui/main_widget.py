"""主悬浮窗口 - 小图标 + 点击展开，支持拖拽缩放"""

from typing import List, Dict, Any

from PySide6.QtCore import Qt, QPoint, QSize, Signal
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QStackedWidget
)

_RESIZE_MARGIN = 8  # 右下角可拖拽缩放区域大小


class ProjectCard(QFrame):
    clicked = Signal(dict)

    def __init__(self, project_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self._build_ui()
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def _build_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            ProjectCard {
                background: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 6px;
                margin: 2px 0;
            }
            ProjectCard:hover { border-color: #89b4fa; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(3)

        p = self.project_data
        name_row = QHBoxLayout()
        name_lbl = QLabel(p["project"])
        name_lbl.setStyleSheet("color:#cdd6f4; font-weight:bold; font-size:13px;")
        count_lbl = QLabel(f"{p['event_count']} 条  {p['chat_count']} 个chat")
        count_lbl.setStyleSheet("color:#6c7086; font-size:11px;")
        name_row.addWidget(name_lbl)
        name_row.addStretch()
        name_row.addWidget(count_lbl)
        layout.addLayout(name_row)

        # 项目目的
        if p.get("purpose"):
            purpose = QLabel(f"🎯 {p['purpose'][:80]}...")
            purpose.setStyleSheet("color:#f9e2af; font-size:10px;")
            purpose.setWordWrap(True)
            layout.addWidget(purpose)

        if p.get("last_summary"):
            s = QLabel(p["last_summary"])
            s.setStyleSheet("color:#a6e3a1; font-size:11px;")
            s.setWordWrap(True)
            layout.addWidget(s)

        if p.get("last_next_action"):
            n = QLabel(f"→ {p['last_next_action']}")
            n.setStyleSheet("color:#89dceb; font-size:11px;")
            n.setWordWrap(True)
            layout.addWidget(n)

        # 文件变更
        files = p.get("files_changed", [])
        if files:
            file_lbl = QLabel(f"📝 {len(files)} 个文件变更")
            file_lbl.setStyleSheet("color:#fab387; font-size:10px;")
            layout.addWidget(file_lbl)
            for f in files[:2]:  # 只显示前2个
                purpose = f.get("purpose", "")
                if purpose:
                    f_line = QLabel(f"  • {purpose[:60]}")
                    f_line.setStyleSheet("color:#6c7086; font-size:10px;")
                    layout.addWidget(f_line)

        open_c = p.get("open_issues", 0)
        color = "#f38ba8" if open_c > 0 else "#6c7086"
        issue_lbl = QLabel(f"问题: {open_c} open / {p.get('solved_issues', 0)} solved")
        issue_lbl.setStyleSheet(f"color:{color}; font-size:11px;")
        layout.addWidget(issue_lbl)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.project_data)


class FloatIcon(QWidget):
    """常驻小图标，点击展开/收起主面板"""
    def __init__(self, panel: "MainWidget", parent=None):
        super().__init__(parent)
        self.panel = panel
        self._drag_pos = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(48, 48)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        lbl = QLabel("📓", self)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-size:28px; background:transparent;")
        lbl.setGeometry(0, 0, 48, 48)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            moved = (event.globalPosition().toPoint() - self.frameGeometry().topLeft()) != self._drag_pos
            self._drag_pos = None
            if not moved:
                if self.panel.isVisible():
                    self.panel.hide()
                else:
                    # 面板出现在图标旁边
                    geo = self.frameGeometry()
                    self.panel.move(geo.right() + 8, geo.top())
                    self.panel.show()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)


class MainWidget(QWidget):
    project_selected = Signal(dict)
    date_mode_changed = Signal(str)  # "today", "yesterday", "7day"

    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.config = config
        self._drag_pos = None
        self._resizing = False
        self._resize_start = None
        self._resize_size = None
        self.current_mode = "today"
        self.setStyleSheet("MainWidget { background: transparent; }")
        self._build_ui()
        self._apply_window_flags()
        self.setMouseTracking(True)

    def _apply_window_flags(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(self.config.get("window_opacity", 0.95))
        sz = self.config.get("window_size", {})
        self.resize(sz.get("width", 400), sz.get("height", 600))
        self.setMinimumSize(250, 200)

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setStyleSheet("QWidget { background: #181825; border-radius: 10px; }")
        outer.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        # 标题栏
        title_row = QHBoxLayout()
        title = QLabel("AI Journal")
        title.setStyleSheet("color:#cba6f7; font-size:14px; font-weight:bold;")
        self.status_lbl = QLabel("加载中...")
        self.status_lbl.setStyleSheet("color:#6c7086; font-size:11px;")
        close_btn = QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton { background:#f38ba8; color:#1e1e2e; border-radius:10px; font-weight:bold; border:none; }
            QPushButton:hover { background:#eba0ac; }
        """)
        close_btn.clicked.connect(self.hide)
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(self.status_lbl)
        title_row.addWidget(close_btn)
        layout.addLayout(title_row)

        # 日期导航栏
        nav_row = QHBoxLayout()
        nav_row.setSpacing(4)

        self.today_btn = QPushButton("Today")
        self.yesterday_btn = QPushButton("Yesterday")
        self.week_btn = QPushButton("7-Day")

        for btn in [self.today_btn, self.yesterday_btn, self.week_btn]:
            btn.setFixedHeight(28)
            btn.setStyleSheet(self._nav_btn_style(False))

        self.today_btn.setStyleSheet(self._nav_btn_style(True))

        self.today_btn.clicked.connect(lambda: self._switch_mode("today"))
        self.yesterday_btn.clicked.connect(lambda: self._switch_mode("yesterday"))
        self.week_btn.clicked.connect(lambda: self._switch_mode("7day"))

        nav_row.addWidget(self.today_btn)
        nav_row.addWidget(self.yesterday_btn)
        nav_row.addWidget(self.week_btn)
        nav_row.addStretch()
        layout.addLayout(nav_row)

        # StackedWidget 切换内容
        self.stacked = QStackedWidget()
        self.stacked.setStyleSheet("background:transparent;")

        # Today 页面
        self.today_scroll = self._create_scroll_area()
        self.stacked.addWidget(self.today_scroll)

        # Yesterday 页面
        self.yesterday_scroll = self._create_scroll_area()
        self.stacked.addWidget(self.yesterday_scroll)

        # 7-Day 页面（占位，后续由 app.py 注入 SummaryWidget）
        self.week_widget = QWidget()
        self.week_widget.setStyleSheet("background:transparent;")
        self.week_layout = QVBoxLayout(self.week_widget)
        self.week_layout.setContentsMargins(0, 0, 0, 0)
        self.stacked.addWidget(self.week_widget)

        layout.addWidget(self.stacked)

        # 右下角缩放提示
        grip = QLabel("⠿")
        grip.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        grip.setStyleSheet("color:#45475a; font-size:14px; background:transparent;")
        layout.addWidget(grip)

    def _create_scroll_area(self) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none; background:transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        cards_widget = QWidget()
        cards_widget.setStyleSheet("background:transparent;")
        cards_layout = QVBoxLayout(cards_widget)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.setSpacing(4)
        cards_layout.addStretch()

        scroll.setWidget(cards_widget)
        scroll.cards_layout = cards_layout  # 保存引用
        return scroll

    def _nav_btn_style(self, active: bool) -> str:
        if active:
            return """
                QPushButton {
                    background: #89b4fa;
                    color: #1e1e2e;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-size: 11px;
                    font-weight: bold;
                }
            """
        else:
            return """
                QPushButton {
                    background: #313244;
                    color: #cdd6f4;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-size: 11px;
                }
                QPushButton:hover { background: #45475a; }
            """

    def _switch_mode(self, mode: str):
        self.current_mode = mode

        # 更新按钮样式
        self.today_btn.setStyleSheet(self._nav_btn_style(mode == "today"))
        self.yesterday_btn.setStyleSheet(self._nav_btn_style(mode == "yesterday"))
        self.week_btn.setStyleSheet(self._nav_btn_style(mode == "7day"))

        # 切换页面
        if mode == "today":
            self.stacked.setCurrentIndex(0)
        elif mode == "yesterday":
            self.stacked.setCurrentIndex(1)
        elif mode == "7day":
            self.stacked.setCurrentIndex(2)

        # 发射信号
        self.date_mode_changed.emit(mode)

    def update_projects(self, projects: List[Dict[str, Any]], mode: str = "today"):
        """更新项目列表"""
        if mode == "today":
            scroll = self.today_scroll
        elif mode == "yesterday":
            scroll = self.yesterday_scroll
        else:
            return  # 7day 由 SummaryWidget 处理

        cards_layout = scroll.cards_layout

        # 清空旧卡片
        while cards_layout.count() > 1:
            item = cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not projects:
            empty = QLabel("暂无日志")
            empty.setStyleSheet("color:#6c7086; font-size:12px;")
            empty.setAlignment(Qt.AlignCenter)
            cards_layout.insertWidget(0, empty)
        else:
            for i, p in enumerate(projects):
                card = ProjectCard(p)
                card.clicked.connect(self.project_selected.emit)
                cards_layout.insertWidget(i, card)

        if mode == self.current_mode:
            self.status_lbl.setText(f"{len(projects)} 个项目")

    def _in_resize_zone(self, pos: QPoint) -> bool:
        return (pos.x() >= self.width() - _RESIZE_MARGIN * 2 and
                pos.y() >= self.height() - _RESIZE_MARGIN * 2)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._in_resize_zone(event.position().toPoint()):
                self._resizing = True
                self._resize_start = event.globalPosition().toPoint()
                self._resize_size = QSize(self.width(), self.height())
            else:
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        if self._resizing and event.buttons() == Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._resize_start
            self.resize(
                max(250, self._resize_size.width() + delta.x()),
                max(200, self._resize_size.height() + delta.y())
            )
        elif self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
        else:
            if self._in_resize_zone(pos):
                self.setCursor(QCursor(Qt.SizeFDiagCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._resizing = False
        self._resize_start = None
        self._resize_size = None
