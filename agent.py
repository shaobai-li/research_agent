import os
from dotenv import load_dotenv
import openai
from dataclasses import dataclass, field
from typing import List
import json
from system_prompts import SYSTEM_PROMPT_REPORT_STRUCTURE, SYSTEM_PROMPT_FIRST_SEARCH, SYSTEM_PROMPT_FIRST_SUMMARY, SYSTEM_PROMPT_REFLECTION
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


#### 第一个 Agent


research_input = "请帮我调研一下web3.0的开发"

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT_REPORT_STRUCTURE},
        {"role": "user", "content": research_input}
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

report_structure = json.loads(clean_json_tags(response.choices[0].message.content))

print("根据输出的大纲更新状态...")
STATE = State()
print(type(report_structure))
for paragraph in report_structure:
    STATE.paragraphs.append(Paragraph(title=paragraph["title"], content=paragraph["content"]))

print("报告大纲：")
for i, paragraph in enumerate(STATE.paragraphs):
    print(f"第{i}个段落标题: {paragraph.title}") 
    print(f"第{i}个段落内容: {paragraph.content}")


print("把第一个段落给搜索计划Agent，作为输入:")
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

print("搜索计划Agent根据第一个段落输出的要做的搜索查询:")
search_interface = response.choices[0].message.content
search_input = json.loads(search_interface)

print(search_input["search_query"])


search_output = tavily_search(search_input["search_query"])

print("根据搜索结果更新状态...")
STATE = update_state_with_search_results(search_output, 0, STATE)

print("搜索到的结果：")
for search in STATE.paragraphs[0].research.search_history:
    print(search.url)
    print(search.content)




print("把搜索到的结果给写段落的Agent，作为输入:")
input_json_search_results = {
    "title": STATE.paragraphs[0].title,
    "content": STATE.paragraphs[0].content,
    "search_query": search_input["search_query"],
    "search_results": [ result["raw_content"] for result in search_output["results"] if result["raw_content"]]
}

print(json.dumps(input_json_search_results, ensure_ascii=False))


response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role":"system","content":SYSTEM_PROMPT_FIRST_SUMMARY},
        {"role":"user","content":json.dumps(input_json_first_search)}
        ],
    temperature=1
    )

print("Agent根据搜索结果输出的段落:")
paragraph_output = json.loads(response.choices[0].message.content)

print(paragraph_output["paragraph_latest_state"])


print("把当前段落的最新信息给反思Agent，作为输入:")

input_json_reflection = {
    "title": STATE.paragraphs[0].title,
    "content": STATE.paragraphs[0].content,
    "paragraph_latest_state": paragraph_output["paragraph_latest_state"]
}

response = client.chat.completions.create(
    model="deepseek-reasoner",
    messages=[
        {"role":"system","content":SYSTEM_PROMPT_REFLECTION},
        {"role":"user","content":json.dumps(input_json_reflection)}
        ],
    temperature=1
    )

reflection_output = json.loads(response.choices[0].message.content)

print("反思Agent根据当前段落输出的要做的搜索查询:")
print(reflection_output["search_query"])