"""主程序入口"""

import json
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor

from dashboard.parser import get_today_overview, get_yesterday_overview, get_7day_summary
from dashboard.watcher import LogWatcher
from dashboard.ui.main_widget import MainWidget, FloatIcon
from dashboard.ui.detail_dialog import DetailDialog
from dashboard.ui.summary_widget import SummaryWidget


def load_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _create_tray_icon() -> QIcon:
    pixmap = QPixmap(16, 16)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#cba6f7"))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(1, 1, 14, 14)
    painter.end()
    return QIcon(pixmap)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = load_config()
    store_path = config.get("store_path", "./Dai_journalstore")

    # 主窗口
    widget = MainWidget(config)
    float_icon = FloatIcon(widget)

    # 7-Day 汇总组件
    summary_widget = SummaryWidget()
    widget.week_layout.addWidget(summary_widget)

    # 刷新函数
    def refresh_today():
        projects = get_today_overview(store_path)
        widget.update_projects(projects, "today")

    def refresh_yesterday():
        projects = get_yesterday_overview(store_path)
        widget.update_projects(projects, "yesterday")

    def refresh_7day():
        data = get_7day_summary(store_path)
        summary_widget.update_summary(data)

    def on_mode_changed(mode: str):
        if mode == "today":
            refresh_today()
        elif mode == "yesterday":
            refresh_yesterday()
        elif mode == "7day":
            refresh_7day()

    widget.date_mode_changed.connect(on_mode_changed)
    widget.project_selected.connect(
        lambda data: DetailDialog(data, widget).exec()
    )

    # 文件监听（只刷新当前模式）
    def on_file_change():
        mode = widget.current_mode
        if mode == "today":
            refresh_today()
        elif mode == "yesterday":
            refresh_yesterday()
        elif mode == "7day":
            refresh_7day()

    watcher = LogWatcher(store_path, on_file_change)
    watcher.start()

    # 定时刷新
    interval = config.get("refresh_interval", 2) * 1000
    timer = QTimer()
    timer.timeout.connect(on_file_change)
    timer.start(interval)

    # 系统托盘
    tray = QSystemTrayIcon(app)
    tray.setIcon(_create_tray_icon())
    tray.setToolTip("AI Journal Dashboard")

    tray_menu = QMenu()
    show_action = QAction("显示")
    show_action.triggered.connect(widget.show)
    quit_action = QAction("退出")
    quit_action.triggered.connect(app.quit)
    tray_menu.addAction(show_action)
    tray_menu.addSeparator()
    tray_menu.addAction(quit_action)
    tray.setContextMenu(tray_menu)
    tray.activated.connect(lambda reason: widget.show() if reason == QSystemTrayIcon.Trigger else None)
    tray.show()

    # 初始加载
    refresh_today()
    refresh_yesterday()
    refresh_7day()
    float_icon.show()

    ret = app.exec()
    watcher.stop()
    sys.exit(ret)


if __name__ == "__main__":
    main()
