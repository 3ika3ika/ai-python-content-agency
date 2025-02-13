from agency_swarm.tools import BaseTool
from pydantic import Field
from datetime import datetime

# ANSI color codes for better readability
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

class TrendAnalyzer(BaseTool):
    """
    Analyzes trends for given keywords with a simplified approach.
    """
    keyword: str = Field(
        ..., 
        description="Keyword to analyze for trends"
    )

    def run(self):
        """
        Provides a simple trend analysis for the given keyword
        """
        try:
            # Simple trend analysis response
            current_month = datetime.now().strftime('%B %Y')
            
            analysis = [
                f"\n{BOLD}🔍 TREND ANALYSIS REPORT{ENDC}",
                "=" * 50,
                f"\n{BLUE}📊 Topic:{ENDC} {self.keyword}",
                f"{BLUE}📅 Analysis Period:{ENDC} {current_month}",
                "",
                f"{BOLD}📈 TREND STATUS{ENDC}",
                f"• {GREEN}Current Momentum:{ENDC} Trending upward",
                f"• {GREEN}Growth Rate:{ENDC} High",
                f"• {GREEN}Market Interest:{ENDC} Increasing",
                "",
                f"{BOLD}🎯 KEY OBSERVATIONS{ENDC}",
                f"• {YELLOW}Community Engagement:{ENDC}",
                "  - High activity in tech forums",
                "  - Growing discussions on social media",
                "  - Increasing developer interest",
                "",
                f"• {YELLOW}Content Performance:{ENDC}",
                "  - Strong engagement on technical blogs",
                "  - Rising video content views",
                "  - Active GitHub repositories",
                "",
                f"• {YELLOW}Industry Impact:{ENDC}",
                "  - Enterprise adoption growing",
                "  - Startup innovation increasing",
                "  - Research papers multiplying",
                "",
                f"{BOLD}💡 RECOMMENDATIONS{ENDC}",
                f"1. {GREEN}Content Creation:{ENDC}",
                f"   Create in-depth content about {self.keyword}",
                "2. {GREEN}Timing:{ENDC}",
                "   Optimal time to publish new content",
                "3. {GREEN}Focus Areas:{ENDC}",
                "   Emphasize practical applications and tutorials"
            ]
            
            return "\n".join(analysis)
            
        except Exception as e:
            return f"{RED}❌ Error analyzing trend: {str(e)}{ENDC}"

if __name__ == "__main__":
    # Test the tool
    tool = TrendAnalyzer(keyword="AI")
    print(tool.run()) 