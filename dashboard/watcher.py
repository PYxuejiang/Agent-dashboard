"""文件监听器 - 监听日志目录变化并触发回调"""

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class _LogChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith((".jsonl", ".md")):
            self.callback()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith((".jsonl", ".md")):
            self.callback()


class LogWatcher:
    def __init__(self, store_path: str, on_change):
        self.store_path = Path(store_path)
        self.on_change = on_change
        self.observer = None

    def start(self):
        if not self.store_path.exists():
            self.store_path.mkdir(parents=True, exist_ok=True)

        handler = _LogChangeHandler(self.on_change)
        self.observer = Observer()
        self.observer.schedule(handler, str(self.store_path), recursive=True)
        self.observer.start()

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2)
