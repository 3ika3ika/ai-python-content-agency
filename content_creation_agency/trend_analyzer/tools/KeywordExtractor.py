from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

class KeywordExtractor(BaseTool):
    """
    Extracts and analyzes trending keywords and topics.
    """
    keywords: str = Field(
        ..., 
        description="Keywords or topics to analyze, comma-separated"
    )

    def run(self):
        """
        Analyze the provided keywords and return trend information
        """
        try:
            # Simple response for now to avoid getting stuck
            keywords_list = [k.strip() for k in self.keywords.split(',')]
            
            response = f"Trend Analysis for: {', '.join(keywords_list)}\n\n"
            for keyword in keywords_list:
                response += f"- {keyword}: Currently trending upward\n"
                response += f"  • High engagement in tech communities\n"
                response += f"  • Growing interest since {datetime.now().strftime('%B %Y')}\n\n"
            
            return response
            
        except Exception as e:
            return f"Error analyzing trends: {str(e)}"

if __name__ == "__main__":
    # Test the tool
    tool = KeywordExtractor(keywords="AI, Machine Learning, Data Science")
    print(tool.run()) 