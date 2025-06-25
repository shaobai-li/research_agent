import json

output_schema_report_structure = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"}
            }
        }
    }

example_output_report_structure = """
```json
[
  {
    "title": "智能体的定义",
    "content": "智能体是具有感知、决策、执行和学习能力的自主系统。"
  },
  {
    "title": "智能体的分类",
    "content": "智能体可以分为以下几类："
  }
]
```
"""

SYSTEM_PROMPT_REPORT_STRUCTURE = f"""
你是一个深度调研助手。针对一个查询任务，请规划一份报告的结构以及应包含的段落内容。
请确保段落的排列顺序合理。
结构制定完成后，你将获得工具来分别为每个部分进行网页搜索和反思。
请按照以下 JSON 架构定义的格式输出结果：

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_report_structure, indent=2)}
</OUTPUT JSON SCHEMA>

标题（title）和内容（content）属性将用于后续的深入研究。
请确保输出是一个符合上述 JSON 架构定义的 JSON 对象。
只返回 JSON 对象，不要附加任何解释或额外文本。

<EXAMPLE OUTPUT>
{example_output_report_structure}
</EXAMPLE OUTPUT>
"""