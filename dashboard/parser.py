"""日志解析器 - 聚合今日所有项目日志"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from collections import Counter


def get_today_overview(store_path: str) -> List[Dict[str, Any]]:
    """扫描 store 目录，返回今日所有项目的聚合摘要"""
    today = datetime.now().strftime("%Y-%m-%d")
    return _get_date_overview(store_path, today)


def get_yesterday_overview(store_path: str) -> List[Dict[str, Any]]:
    """获取昨天的日志"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    return _get_date_overview(store_path, yesterday)


def _read_jsonl(path: Path) -> List[Dict]:
    events = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
    except Exception:
        pass
    return events


def _get_date_overview(store_path: str, date_str: str) -> List[Dict[str, Any]]:
    """通用日期聚合函数"""
    root = Path(store_path)
    projects = []

    if not root.exists():
        return projects

    for project_dir in sorted(root.iterdir()):
        if not project_dir.is_dir():
            continue

        date_dir = project_dir / date_str
        if not date_dir.exists():
            continue

        chats = []
        total_events = 0
        last_summary = None
        last_next_action = None
        open_issues = 0
        solved_issues = 0
        project_purpose = None
        project_method = None
        all_files_changed = []

        for jsonl_file in sorted(date_dir.glob("*.jsonl")):
            events = _read_jsonl(jsonl_file)
            total_events += len(events)

            chat_summary = None
            chat_next_action = None
            chat_open = 0
            chat_solved = 0
            chat_files = []
            chat_purpose = None

            for ev in events:
                t = ev.get("type")
                payload = ev.get("payload", {})

                # 提取项目目的（从 prompt）
                if t == "prompt" and not project_purpose:
                    project_purpose = payload.get("abstract_task") or ev.get("abstract_task")
                    chat_purpose = project_purpose

                # 提取方法（从 issue 的 diagnosis）
                if t == "issue" and not project_method:
                    project_method = payload.get("diagnosis") or ev.get("diagnosis")

                # 提取文件变更（从 command）
                if t == "command":
                    cmd = payload.get("command") or ev.get("command", "")
                    purpose = payload.get("purpose") or ev.get("purpose", "")
                    if cmd or purpose:
                        chat_files.append({"command": cmd[:100], "purpose": purpose})
                        all_files_changed.append({"command": cmd[:100], "purpose": purpose})

                if t == "close_step":
                    chat_summary = payload.get("summary") or ev.get("summary")
                    last_summary = chat_summary
                elif t == "next_action":
                    chat_next_action = payload.get("action") or ev.get("action")
                    last_next_action = chat_next_action
                elif t == "issue":
                    status = payload.get("status") or ev.get("status")
                    if status == "open":
                        chat_open += 1
                        open_issues += 1
                    elif status == "solved":
                        chat_solved += 1
                        solved_issues += 1

            chats.append({
                "chat": jsonl_file.stem,
                "event_count": len(events),
                "last_summary": chat_summary,
                "last_next_action": chat_next_action,
                "open_issues": chat_open,
                "solved_issues": chat_solved,
                "purpose": chat_purpose,
                "files_changed": chat_files[-5:],  # 最近5个文件变更
                "files": {
                    "md": str(date_dir / f"{jsonl_file.stem}.md"),
                    "jsonl": str(jsonl_file),
                    "dir": str(date_dir),
                },
            })

        projects.append({
            "project": project_dir.name,
            "date": date_str,
            "event_count": total_events,
            "chat_count": len(chats),
            "last_summary": last_summary,
            "last_next_action": last_next_action,
            "open_issues": open_issues,
            "solved_issues": solved_issues,
            "purpose": project_purpose,
            "method": project_method,
            "files_changed": all_files_changed[-10:],  # 最近10个文件变更
            "chats": chats,
        })

    return projects


def get_7day_summary(store_path: str) -> Dict[str, Any]:
    """获取最近7天的汇总统计"""
    root = Path(store_path)
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    all_issues = []
    all_milestones = []
    all_tags = []
    all_summaries = []
    project_activity = Counter()
    date_activity = Counter()
    project_backgrounds = {}  # 项目背景

    if not root.exists():
        return _empty_7day_summary()

    for project_dir in sorted(root.iterdir()):
        if not project_dir.is_dir():
            continue

        proj_purpose = None
        proj_method = None

        for date_str in dates:
            date_dir = project_dir / date_str
            if not date_dir.exists():
                continue

            for jsonl_file in date_dir.glob("*.jsonl"):
                events = _read_jsonl(jsonl_file)
                if events:
                    project_activity[project_dir.name] += len(events)
                    date_activity[date_str] += len(events)

                for ev in events:
                    t = ev.get("type")
                    payload = ev.get("payload", {})
                    context = ev.get("context", {})

                    # 收集项目背景
                    if t == "prompt" and not proj_purpose:
                        proj_purpose = payload.get("abstract_task") or ev.get("abstract_task")
                    if t == "issue" and not proj_method:
                        proj_method = payload.get("diagnosis") or ev.get("diagnosis")

                    # 收集 milestone
                    milestone = context.get("milestone") or ev.get("milestone")
                    if milestone:
                        all_milestones.append(milestone)

                    # 收集 tags
                    tags = context.get("tags") or ev.get("tags") or []
                    all_tags.extend(tags)

                    # 收集 issue
                    if t == "issue":
                        desc = payload.get("description") or payload.get("problem") or ev.get("description", "")
                        status = payload.get("status") or ev.get("status", "open")
                        all_issues.append({"description": desc[:100], "status": status, "date": date_str})

                    # 收集 summary
                    if t == "close_step":
                        summary = payload.get("summary") or ev.get("summary")
                        if summary:
                            all_summaries.append(summary)

        # 保存项目背景
        if proj_purpose or proj_method:
            project_backgrounds[project_dir.name] = {
                "purpose": proj_purpose,
                "method": proj_method
            }

    return {
        "date_range": f"{dates[-1]} ~ {dates[0]}",
        "total_events": sum(project_activity.values()),
        "active_projects": len(project_activity),
        "project_activity": dict(project_activity.most_common(10)),
        "project_backgrounds": project_backgrounds,
        "date_activity": dict(sorted(date_activity.items())),
        "issues": {
            "total": len(all_issues),
            "open": len([i for i in all_issues if i["status"] == "open"]),
            "solved": len([i for i in all_issues if i["status"] == "solved"]),
            "list": all_issues[-20:]  # 最近20个
        },
        "milestones": dict(Counter(all_milestones).most_common(10)),
        "tags": dict(Counter(all_tags).most_common(15)),
        "recent_summaries": all_summaries[-10:]  # 最近10条
    }


def _empty_7day_summary() -> Dict[str, Any]:
    return {
        "date_range": "",
        "total_events": 0,
        "active_projects": 0,
        "project_activity": {},
        "project_backgrounds": {},
        "date_activity": {},
        "issues": {"total": 0, "open": 0, "solved": 0, "list": []},
        "milestones": {},
        "tags": {},
        "recent_summaries": []
    }
