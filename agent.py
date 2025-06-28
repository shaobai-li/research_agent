import os
from dotenv import load_dotenv
import openai
from dataclasses import dataclass, field
from typing import List
import json
from system_prompts import SYSTEM_PROMPT_REPORT_STRUCTURE, SYSTEM_PROMPT_FIRST_SEARCH
from search_tool import tavily_search
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


def clean_json_tags(json_str):
    return json_str.replace("```json", "").replace("```", "").strip()


def update_state_with_search_results(search_results, idx_paragraph, state):

    for search_result in search_results["results"]:
        search = Search(url=search_result["url"], content=search_result["content"])
        state.paragraphs[idx_paragraph].research.search_history.append(search)
    return state

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


print("给Agent的第一个段落的内容:")
input_json_first_search = {
    "title": STATE.paragraphs[0].title,
    "content": STATE.paragraphs[0].content
}
print(json.dumps(input_json_first_search, ensure_ascii=False))

response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role":"system","content":SYSTEM_PROMPT_FIRST_SEARCH},
        {"role":"user","content":json.dumps(input_json_first_search)}
        ],
    temperature=1
    )

print("Agent根据第一个段落输出的要做的搜索查询:")
search_interface = response.choices[0].message.content
search_input = json.loads(search_interface)

print(search_input["search_query"])


search_output = tavily_search(search_input["search_query"])

print("搜索到的网页内容:")

STATE = update_state_with_search_results(search_output, 0, STATE)

print("更新后的状态:")
for search in STATE.paragraphs[0].research.search_history:
    print(search.url)
    print(search.content)