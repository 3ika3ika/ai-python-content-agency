from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class WebSearchTool(BaseTool):
    """
    Searches the web for AI trends using Tavily API
    """
    query: str = Field(..., description="Search query for AI trends")
    
    def run(self):
        """
        Performs a web search using Tavily API
        """
        try:
            response = tavily.search(
                query=self.query,
                search_depth="advanced",
                include_answer=True,
                include_domains=["techcrunch.com", "wired.com", "venturebeat.com", "ai.gov"]
            )
            return str(response)
        except Exception as e:
            return f"Error performing web search: {str(e)}"

if __name__ == "__main__":
    tool = WebSearchTool(query="latest developments in artificial intelligence")
    print(tool.run()) 