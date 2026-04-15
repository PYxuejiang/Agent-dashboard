"""示例：如何使用 MCP Logger"""

from Dai_journal.mcp_logger import set_project, set_chat, log_prompt, log_close_step, log_issue, log_next_action

# 设置项目和聊天主题
set_project("PTM_GNN_SEQ")
set_chat("fusion_stageB_w63")

# 记录任务开始
log_prompt("完成 fusion stageB w63 后台命令整理", "需要统一日志输出路径并验证配置")

# 记录完成步骤
log_close_step("已完成 fusion stageB w63 后台命令整理，并统一日志输出路径")

# 记录问题
log_issue("发现 window63 配置文件缺少 batch_size 参数", status="open")

# 记录下一步行动
log_next_action("继续比较 stageB w63 与 stageA 指标差异")

# 记录问题解决
log_issue("window63 配置文件缺少 batch_size 参数", status="solved", solution="已添加默认值 batch_size=32")

print("✓ 日志已记录到 Dai_journalstore/PTM_GNN_SEQ/")
