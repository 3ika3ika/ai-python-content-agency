from agency_swarm import Agent

class TrendAnalyzer(Agent):
    def __init__(self):
        super().__init__(
            name="Trend Analyzer",
            description="Analyzes trends and patterns in AI and tech content",
            instructions="./instructions.md",
            tools_folder="./tools",
            temperature=0.7
        ) 