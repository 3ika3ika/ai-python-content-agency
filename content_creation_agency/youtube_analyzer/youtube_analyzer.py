from agency_swarm import Agent

class YouTubeAnalyzer(Agent):
    def __init__(self):
        super().__init__(
            name="YouTube Analyzer",
            description="Analyzes any YouTube channel, videos, and trends based on user input",
            instructions="./instructions.md",
            tools_folder="./tools",
            temperature=0.7,
        )
    
    def analyze_channel(self, channel_input: str, metric_type: str = "videos"):
        """
        Analyzes any YouTube channel based on user input
        Args:
            channel_input: Channel URL, ID, or name to analyze
            metric_type: Type of analysis (statistics, videos, playlists)
        """
        return self.tools.ChannelAnalytics(
            channel_input=channel_input,
            metric_type=metric_type
        ).run() 