"""
MCP Logger - 用于记录 MCP Agent 工作日志的核心模块

功能：
- 按项目、日期、聊天主题组织日志
- 同时生成 Markdown 和 JSONL 格式
- 支持事件类型：prompt, close_step, issue, next_action
- 提供查询和检索能力
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class MCPLogger:
    """MCP 日志记录器"""

    def __init__(self, root_path: str = "./Dai_journalstore"):
        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)
        self.current_project = None
        self.current_chat = None

    def set_project(self, project_name: str):
        """设置当前项目"""
        self.current_project = project_name

    def set_chat(self, chat_name: str):
        """设置当前聊天主题"""
        self.current_chat = chat_name

    def _get_log_path(self, date: str = None) -> Path:
        """获取日志文件路径"""
        if not self.current_project or not self.current_chat:
            raise ValueError("必须先设置 project 和 chat")

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        project_dir = self.root / self.current_project / date
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """记录事件到 md 和 jsonl"""
        log_dir = self._get_log_path()

        # 准备事件数据
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "project": self.current_project,
            "chat": self.current_chat,
            **data
        }

        # 写入 JSONL
        jsonl_file = log_dir / f"{self.current_chat}.jsonl"
        with open(jsonl_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        # 写入 Markdown
        md_file = log_dir / f"{self.current_chat}.md"
        md_content = self._format_markdown(event)
        with open(md_file, "a", encoding="utf-8") as f:
            f.write(md_content + "\n\n")

    def _format_markdown(self, event: Dict) -> str:
        """格式化为 Markdown"""
        lines = [
            f"## {event['type'].upper()} - {event['timestamp']}",
            ""
        ]

        if event['type'] == 'prompt':
            lines.append(f"**任务**: {event.get('abstract_task', 'N/A')}")
            if 'details' in event:
                lines.append(f"\n{event['details']}")

        elif event['type'] == 'close_step':
            lines.append(f"**摘要**: {event.get('summary', 'N/A')}")
            if 'details' in event:
                lines.append(f"\n{event['details']}")

        elif event['type'] == 'issue':
            status = event.get('status', 'open')
            lines.append(f"**问题** [{status}]: {event.get('description', 'N/A')}")
            if 'solution' in event:
                lines.append(f"\n**解决方案**: {event['solution']}")

        elif event['type'] == 'next_action':
            lines.append(f"**下一步**: {event.get('action', 'N/A')}")

        return "\n".join(lines)

    def list_projects(self) -> List[str]:
        """列出所有项目"""
        if not self.root.exists():
            return []
        return [d.name for d in self.root.iterdir() if d.is_dir()]

    def get_project_dates(self, project: str) -> List[str]:
        """获取项目的所有日期"""
        project_dir = self.root / project
        if not project_dir.exists():
            return []
        return sorted([d.name for d in project_dir.iterdir() if d.is_dir()], reverse=True)

    def get_today_logs(self, project: str) -> Dict[str, Any]:
        """获取项目今日日志摘要"""
        today = datetime.now().strftime("%Y-%m-%d")
        date_dir = self.root / project / today

        if not date_dir.exists():
            return {
                "project": project,
                "date": today,
                "event_count": 0,
                "chats": []
            }

        chats = []
        total_events = 0

        for jsonl_file in date_dir.glob("*.jsonl"):
            chat_name = jsonl_file.stem
            events = self._read_jsonl(jsonl_file)
            total_events += len(events)

            # 提取关键信息
            last_summary = None
            last_next_action = None
            open_issues = 0
            solved_issues = 0

            for event in events:
                if event['type'] == 'close_step':
                    last_summary = event.get('summary')
                elif event['type'] == 'next_action':
                    last_next_action = event.get('action')
                elif event['type'] == 'issue':
                    if event.get('status') == 'open':
                        open_issues += 1
                    elif event.get('status') == 'solved':
                        solved_issues += 1

            chats.append({
                "chat": chat_name,
                "event_count": len(events),
                "last_summary": last_summary,
                "last_next_action": last_next_action,
                "open_issues": open_issues,
                "solved_issues": solved_issues,
                "files": {
                    "md": str(date_dir / f"{chat_name}.md"),
                    "jsonl": str(jsonl_file)
                }
            })

        return {
            "project": project,
            "date": today,
            "event_count": total_events,
            "chats": chats
        }

    def _read_jsonl(self, file_path: Path) -> List[Dict]:
        """读取 JSONL 文件"""
        events = []
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
        return events

    def search_logs(self, project: str, keyword: str, date: str = None) -> List[Dict]:
        """搜索日志"""
        results = []
        project_dir = self.root / project

        if not project_dir.exists():
            return results

        dates = [date] if date else self.get_project_dates(project)

        for d in dates:
            date_dir = project_dir / d
            if not date_dir.exists():
                continue

            for jsonl_file in date_dir.glob("*.jsonl"):
                events = self._read_jsonl(jsonl_file)
                for event in events:
                    event_str = json.dumps(event, ensure_ascii=False).lower()
                    if keyword.lower() in event_str:
                        results.append(event)

        return results


# 全局实例
logger = MCPLogger()


# 便捷函数
def set_project(project_name: str):
    logger.set_project(project_name)


def set_chat(chat_name: str):
    logger.set_chat(chat_name)


def log_prompt(abstract_task: str, details: str = ""):
    logger.log_event("prompt", {"abstract_task": abstract_task, "details": details})


def log_close_step(summary: str, details: str = ""):
    logger.log_event("close_step", {"summary": summary, "details": details})


def log_issue(description: str, status: str = "open", solution: str = ""):
    logger.log_event("issue", {"description": description, "status": status, "solution": solution})


def log_next_action(action: str):
    logger.log_event("next_action", {"action": action})