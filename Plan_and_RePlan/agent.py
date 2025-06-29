from openai import OpenAI

class Agent:
    def __init__(self):
        self.llm = OpenAI(
        api_key="sk-25b2d906d58649868199153b93454684", 
        base_url="https://api.deepseek.com"
    )

    def get_system_prompt(self):
        return """你是一个专业的任务规划专家。你的目标是将用户给定的复杂请求分解成一系列清晰、有序且可独立执行的子步骤。

**规则：**
1.  每一步都应该是一个具体的、可操作的任务描述，避免模糊不清的指令。
2.  确保所有步骤的逻辑顺序是正确的，并且一步接一步能够最终达成用户请求的目标。
3.  不要跳过任何必要的中间步骤。
4.  不要包含多余的、与最终目标无关的步骤。
5.  你的输出应该是一个编号的步骤列表，每一步以“步骤N:”开头。

**示例输出格式：**
步骤1: [第一个任务的详细描述]
步骤2: [第二个任务的详细描述]
...
步骤N: [最后一个任务的详细描述，其结果应直接满足用户请求]"""

    def execute(self, task):

        print("# The agent is running ...")
        llm_response = self.llm.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": task}
            ],
            stream=False
        )

        return llm_response.choices[0].message.content


if __name__ == "__main__":
    agent = Agent()
    ai_output_content = agent.execute("请帮我调研一下web3技术")
    print("# The output from the agent:")
    print(ai_output_content)