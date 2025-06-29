from openai import OpenAI

class Agent:
    def __init__(self):
        self.llm = OpenAI(
        api_key="sk-25b2d906d58649868199153b93454684", 
        base_url="https://api.deepseek.com"
    )

    def get_system_prompt(self):
        return "You are an AI assistant that helps people find information."

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