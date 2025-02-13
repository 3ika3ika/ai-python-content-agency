from agency_swarm.tools import BaseTool
from pydantic import Field
import os

class ScriptEditor(BaseTool):
    """
    Edits existing scripts based on suggestions
    """
    filename: str = Field(..., description="Name of the script file to edit")
    edits: str = Field(..., description="Edits to apply to the script")
    
    def run(self):
        """
        Applies edits to an existing script file
        """
        try:
            if not os.path.exists(self.filename):
                return f"Error: File {self.filename} not found"
            
            # Read existing content
            with open(self.filename, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Create backup
            backup_file = f"{self.filename}.bak"
            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Write new content
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(f"{content}\n\n## Edits\n{self.edits}")
            
            return f"Script edited successfully. Backup saved as {backup_file}"
        except Exception as e:
            return f"Error editing script: {str(e)}"

if __name__ == "__main__":
    tool = ScriptEditor(
        filename="scripts/test_script.md",
        edits="Added this new section with important information."
    )
    print(tool.run()) 