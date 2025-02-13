from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import re
import json
from datetime import datetime
from typing import Dict, Any

# ANSI color codes
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'

load_dotenv()

youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
default_channel = os.getenv('DEFAULT_CHANNEL_ID', 'UCbmCqH_WOUviDUsV83qloZQ')  # Fallback to your channel if not set

class CompetitorAnalysis(BaseTool):
    """
    Analyzes competitor YouTube channels
    """
    channel_id: str = Field(
        default=default_channel,
        description="Channel ID to analyze (defaults to channel from .env)"
    )
    
    def _format_number(self, num: int) -> str:
        """Format large numbers for readability"""
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        return str(num)

    def _format_date(self, date_str):
        """Format date to readable format"""
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date.strftime("%B %d, %Y")

    def _format_output(self, data: Dict[str, Any]) -> str:
        """Creates a nicely formatted string output"""
        output = []
        
        # Channel Analysis Section
        channel = data["Channel Analysis"]
        output.append("\n📊 CHANNEL ANALYSIS")
        output.append("=" * 50)
        output.append(f"📌 Channel: {channel['Title']}")
        output.append(f"👥 Subscribers: {channel['Subscribers']}")
        output.append(f"🎥 Total Videos: {channel['Total Videos']}")
        output.append(f"👀 Total Views: {channel['Total Views']}")
        output.append(f"\n📝 Description:\n{channel['Description']}")
        
        # Recent Videos Section
        output.append("\n\n🎬 RECENT VIDEOS ANALYSIS")
        output.append("=" * 50)
        
        for i, video in enumerate(data["Recent Videos Analysis"], 1):
            output.append(f"\n{i}. {video['Title']}")
            output.append(f"   📅 Published: {video['Published']}")
            output.append(f"   👀 Views: {video['Views']}")
            output.append(f"   👍 Likes: {video['Likes']}")
            output.append(f"   💬 Comments: {video['Comments']}")
            output.append(f"   🔗 URL: {video['URL']}")
        
        return "\n".join(output)

    def _extract_channel_id(self, channel_input):
        """Extract channel ID from various input formats"""
        if re.match(r'^UC[\w-]{22}$', channel_input):
            return channel_input
            
        channel_url_match = re.search(r'youtube\.com/channel/(UC[\w-]{22})', channel_input)
        if channel_url_match:
            return channel_url_match.group(1)
            
        try:
            response = youtube.search().list(
                part="snippet",
                q=channel_input,
                type="channel",
                maxResults=1
            ).execute()
            
            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
        except Exception:
            pass
            
        return None

    def run(self):
        """
        Analyzes a competitor's channel and recent videos
        """
        try:
            # Get channel details
            channel_response = youtube.channels().list(
                part="snippet,statistics,contentDetails",
                id=self.channel_id
            ).execute()
            
            if not channel_response.get('items'):
                return f"{RED}❌ Error: Channel not found{ENDC}"
                
            channel = channel_response['items'][0]
            stats = channel['statistics']
            
            # Format output
            output = [
                f"\n{BOLD}📊 CHANNEL ANALYSIS{ENDC}",
                "=" * 50,
                f"\n{BLUE}📺 Channel:{ENDC} {channel['snippet']['title']}",
                f"{BLUE}👥 Subscribers:{ENDC} {self._format_number(int(stats.get('subscriberCount', 0)))}",
                f"{BLUE}🎥 Total Videos:{ENDC} {self._format_number(int(stats.get('videoCount', 0)))}",
                f"{BLUE}👀 Total Views:{ENDC} {self._format_number(int(stats.get('viewCount', 0)))}",
                "",
                f"{BOLD}📝 Description:{ENDC}",
                f"{channel['snippet']['description'][:200]}..."  # Truncate long descriptions
            ]
            
            # Get recent videos
            playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
            videos_response = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=10
            ).execute()
            
            if videos_response.get('items'):
                output.extend([
                    "",
                    f"{BOLD}🎬 RECENT VIDEOS{ENDC}"
                ])
                
                for item in videos_response['items']:
                    video = item['snippet']
                    output.extend([
                        f"\n• {video['title']}",
                        f"  Published: {video['publishedAt'][:10]}"
                    ])
            
            return "\n".join(output)
            
        except Exception as e:
            return f"{RED}❌ Error analyzing channel: {str(e)}{ENDC}"

if __name__ == "__main__":
    # Test the tool
    tool = CompetitorAnalysis()  # Will use default channel from .env
    print(tool.run())
    
    # Test with a different channel
    tool = CompetitorAnalysis(channel_id="UCWN3xxRkmTPmbKwht9FuE5A")  # Siraj Raval's channel
    print(tool.run()) 