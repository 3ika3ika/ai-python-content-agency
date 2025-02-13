from agency_swarm import Agent

class ContentManager(Agent):
    def __init__(self):
        super().__init__(
            name="Content Manager",
            description="Manages content strategy and coordinates between analytics and trend research",
            instructions="./instructions.md",
            tools_folder="./tools",
            temperature=0.5  # Lower temperature for more consistent responses
        ) 
    
    def handle_request(self, user_input: str) -> str:
        """
        Handle user requests and coordinate with other agents
        """
        try:
            # Use the built-in chat method to process requests
            response = self.chat(user_input)
            return response
        except Exception as e:
            return f"Error processing request: {str(e)}"

    def process_message(self, message: str) -> str:
        """Process a message and return a response"""
        try:
            # Use the agent's built-in completion method
            return self.complete(message)
        except Exception as e:
            return f"Error processing message: {str(e)}" 