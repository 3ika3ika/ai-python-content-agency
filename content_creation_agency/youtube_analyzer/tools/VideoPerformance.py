from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime
from typing import Dict, Any

# ANSI color codes
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

load_dotenv()

youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

class VideoPerformance(BaseTool):
    """
    Analyzes performance of specific videos using public metrics
    """
    video_id: str = Field(
        ..., 
        description="ID or URL of the video to analyze"
    )
    
    def _extract_video_id(self, video_input: str) -> str:
        """Extract video ID from various input formats"""
        # If it's already a video ID
        if len(video_input) == 11:
            return video_input
            
        # If it's a full URL
        import re
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu.be\/)([^&\n?#]+)',
            r'youtube.com/shorts/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_input)
            if match:
                return match.group(1)
                
        return video_input

    def _format_number(self, num_str: str) -> str:
        """Format large numbers for readability"""
        num = int(num_str)
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        return str(num)

    def _format_date(self, date_str: str) -> str:
        """Format date to readable format"""
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date.strftime("%B %d, %Y")

    def _format_duration(self, duration: str) -> str:
        """Convert YouTube duration format to readable format"""
        import re
        match = re.search(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
        if not match:
            return "00:00"
        
        hours = match.group(1)[:-1] if match.group(1) else 0
        minutes = match.group(2)[:-1] if match.group(2) else 0
        seconds = match.group(3)[:-1] if match.group(3) else 0
        
        if hours:
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        return f"{int(minutes):02d}:{int(seconds):02d}"

    def run(self):
        """
        Retrieves public performance metrics for a specific video
        """
        try:
            # Extract and validate video ID
            video_id = self._extract_video_id(self.video_id)
            
            # Get video details and statistics
            video_response = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                return f"{RED}❌ Error: Video not found or not accessible{ENDC}"
            
            video = video_response['items'][0]
            snippet = video['snippet']
            stats = video['statistics']
            
            # Format output
            output = [
                f"\n{BOLD}📊 VIDEO PERFORMANCE ANALYSIS{ENDC}",
                "=" * 50,
                f"\n{BLUE}📺 Title:{ENDC} {snippet['title']}",
                f"{BLUE}👤 Channel:{ENDC} {snippet['channelTitle']}",
                f"{BLUE}📅 Published:{ENDC} {self._format_date(snippet['publishedAt'])}",
                f"{BLUE}⏱ Duration:{ENDC} {self._format_duration(video['contentDetails']['duration'])}",
                "",
                f"{BOLD}📈 PERFORMANCE METRICS{ENDC}",
                f"👀 Views: {self._format_number(stats.get('viewCount', '0'))}",
                f"👍 Likes: {self._format_number(stats.get('likeCount', '0'))}",
                f"💬 Comments: {self._format_number(stats.get('commentCount', '0'))}",
                "",
                f"{BOLD}📝 DESCRIPTION{ENDC}",
                f"{snippet['description'][:200]}..."  # Truncate long descriptions
            ]
            
            # Add tags if available
            if 'tags' in snippet:
                output.extend([
                    "",
                    f"{BOLD}🏷 TAGS{ENDC}",
                    ", ".join(snippet['tags'][:10])  # Show first 10 tags
                ])
            
            return "\n".join(output)

        except Exception as e:
            return f"{RED}❌ Error analyzing video performance: {str(e)}{ENDC}"

if __name__ == "__main__":
    # Test with real YouTube videos
    test_videos = [
        "https://www.youtube.com/watch?v=aircAruvnKk",  # 3Blue1Brown neural networks video
        "dQw4w9WgXcQ",  # Another popular video
        "https://youtu.be/dQw4w9WgXcQ"  # Same video with different URL format
    ]
    
    for video in test_videos:
        print(f"\n{BOLD}🔍 Analyzing video: {video}{ENDC}")
        print("=" * 80)
        tool = VideoPerformance(video_id=video)
        result = tool.run()
        print(result)
        print("=" * 80) 