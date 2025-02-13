from agency_swarm import set_openai_key
from content_manager.content_manager import ContentManager
from youtube_analyzer.youtube_analyzer import YouTubeAnalyzer
from trend_analyzer.trend_analyzer import TrendAnalyzer
from agency_swarm import Agency
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
set_openai_key(os.getenv('OPENAI_API_KEY'))

# Initialize agents
content_manager = ContentManager()
youtube_analyzer = YouTubeAnalyzer()
trend_analyzer = TrendAnalyzer()

# Create agency with communication flows
agency = Agency(
    [
        content_manager,  # Content Manager is the entry point
        [content_manager, youtube_analyzer],
        [content_manager, trend_analyzer],
    ],
    shared_instructions="agency_manifesto.md"
)

if __name__ == "__main__":
    # Run the agency in demo mode
    agency.run_demo() 