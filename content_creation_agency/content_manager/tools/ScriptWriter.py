from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from datetime import datetime

class ScriptWriter(BaseTool):
    """
    Writes scripts in Markdown format and saves them locally
    """
    title: str = Field(..., description="Title of the script")
    content: str = Field(..., description="Content of the script in Markdown format")
    
    def run(self):
        """
        Writes the script to a markdown file in the scripts folder
        """
        try:
            # Create scripts directory if it doesn't exist
            os.makedirs("scripts", exist_ok=True)
            
            # Create filename from title and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scripts/{timestamp}_{self.title.lower().replace(' ', '_')}.md"
            
            # Write content to file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"# {self.title}\n\n{self.content}")
            
            return f"Script saved successfully to {filename}"
        except Exception as e:
            return f"Error saving script: {str(e)}"

if __name__ == "__main__":
    tool = ScriptWriter(
        title="Test Script",
        content="## Introduction\nThis is a test script.\n\n## Main Content\nHere's the main content."
    )
    print(tool.run()) 