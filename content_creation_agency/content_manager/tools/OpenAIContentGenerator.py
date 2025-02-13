from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAIContentGenerator(BaseTool):
    """
    Generates content ideas using OpenAI's latest GPT-4 model via the chat completions API.
    """
    prompt: str = Field(
        ..., description="The prompt to generate content ideas from"
    )
    
    def run(self):
        """
        Generates content ideas using OpenAI's API
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",
                messages=[
                    {"role": "system", "content": "You are a creative content strategist specialized in AI content."},
                    {"role": "user", "content": self.prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating content: {str(e)}"

if __name__ == "__main__":
    tool = OpenAIContentGenerator(prompt="Generate 5 video ideas about AI trends")
    print(tool.run()) 