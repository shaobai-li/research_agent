import os
from dotenv import load_dotenv
import openai
from dataclasses import dataclass, field
from typing import List
import json
# from openai import OpenAI

load_dotenv()

@dataclass
class Search:
    url: str = ""
    content: str = ""

@dataclass
class Research:
    search_history: List[Search] = field(default_factory=list)
    latest_summary: str = ""
    reflection_iteration: int = 0


@dataclass
class Paragraph:
    title: str = ""
    content: str = ""
    research: Research = field(default_factory=Research)

@dataclass
class State:
    report_title: str = ""
    paragraphs: List[Paragraph] = field(default_factory=list)

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

def clean_json_tags(json_str):
    return json_str.replace("```json", "").replace("```", "").strip()

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

client = openai.OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
    )

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT_REPORT_STRUCTURE},
        {"role": "user", "content": "请帮我调研一下web3.0的开发"}
    ]
)

# client = openai.OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY")
# )

# response = client.chat.completions.create(
#     # model="gpt-3.5-turbo",
#     model="gpt-4o-2024-08-06",
#     messages=[
#         {"role": "system", "content": SYSTEM_PROMPT_REPORT_STRUCTURE},
#         {"role": "user", "content": "请帮我调研一下web3.0的开发"}
#     ]
# )

# #print(response.choices[0].message.reasoning_content)
print(response.choices[0].message.content)

report_structure = json.loads(clean_json_tags(response.choices[0].message.content))

STATE = State()


print(type(report_structure))
for paragraph in report_structure:
    STATE.paragraphs.append(Paragraph(title=paragraph["title"], content=paragraph["content"]))
