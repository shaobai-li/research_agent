from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

def tavily_search(query, include_raw_content=True, max_results=5):

    tavily_client = TavilyClient(
        api_key=os.getenv("TAVILY_API_KEY")
    )

    return tavily_client.search(
        query=query,
        include_raw_content=include_raw_content,
        max_results=max_results
    )



if __name__ == "__main__":
    result = tavily_search("web3.0的开发")
    print(result)
    print(type(result))