from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

def tavily_search(query, include_raw_content=True, max_results=2):

    tavily_client = TavilyClient(
        api_key=os.getenv("TAVILY_API_KEY")
    )

    return tavily_client.search(
        query=query,
        include_raw_content=include_raw_content,
        max_results=max_results
    )



if __name__ == "__main__":
    result = tavily_search("web3 development") 

    # for r in result["results"]:
    #     print(type(r["url"]))
    #     print(r["url"])

    #     print(type(r["content"]))
    #     print(len(r["content"]))
    #     print(r["content"])

    #     print(r["raw_content"])
