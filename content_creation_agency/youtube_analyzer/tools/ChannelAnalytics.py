from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from datetime import datetime
from typing import Dict, Any
import re

# ANSI color codes for terminal output
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

load_dotenv()

CHANNEL_ID = "UCX6OQ3DkcsbYNE6H8uQQuVA"  # MrBeast's channel ID
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

class ChannelAnalytics(BaseTool):
    """
    Analyzes YouTube channel statistics and public data
    """
    channel_input: str = Field(
        ..., 
        description="Channel URL, ID, or name to analyze"
    )
    metric_type: str = Field(
        ..., 
        description="Type of metrics to analyze (statistics, videos, playlists)"
    )
    
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
        match = re.search(r'PT(\d+H)?(\d+M)?(\d+S)?', duration)
        if not match:
            return "00:00"
        
        hours = match.group(1)[:-1] if match.group(1) else 0
        minutes = match.group(2)[:-1] if match.group(2) else 0
        seconds = match.group(3)[:-1] if match.group(3) else 0
        
        if hours:
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        return f"{int(minutes):02d}:{int(seconds):02d}"

    def _format_channel_statistics(self, data: Dict) -> str:
        """Format channel statistics output"""
        channel = data['items'][0]
        stats = channel['statistics']
        
        output = [
            f"\n{BOLD}📊 CHANNEL STATISTICS{ENDC}",
            "=" * 50,
            f"{BLUE}📌 Channel Name:{ENDC} {channel['snippet']['title']}",
            f"{BLUE}📝 Description:{ENDC} {channel['snippet']['description'][:200]}...",
            f"{BLUE}📅 Created:{ENDC} {self._format_date(channel['snippet']['publishedAt'])}",
            "",
            f"{YELLOW}📈 Performance Metrics:{ENDC}",
            f"   👥 Subscribers: {self._format_number(stats['subscriberCount'])}",
            f"   👀 Total Views: {self._format_number(stats['viewCount'])}",
            f"   🎥 Video Count: {self._format_number(stats['videoCount'])}",
            "",
            f"{GREEN}🔗 Channel URL:{ENDC} https://youtube.com/channel/{channel['id']}"
        ]
        return "\n".join(output)

    def _format_videos_list(self, data: Dict) -> str:
        """Format videos list output"""
        output = [
            f"\n{BOLD}🎬 RECENT VIDEOS{ENDC}",
            "=" * 50
        ]
        
        for i, item in enumerate(data['items'], 1):
            video = item['snippet']
            output.extend([
                f"\n{BOLD}{i}. {video['title']}{ENDC}",
                f"   📅 Published: {self._format_date(video['publishedAt'])}",
                f"   📝 Description: {video['description'][:100]}...",
                f"   🔗 URL: https://youtube.com/watch?v={item['id']['videoId']}"
            ])
        
        return "\n".join(output)

    def _format_playlists(self, data: Dict) -> str:
        """Format playlists output"""
        output = [
            f"\n{BOLD}📑 PLAYLISTS{ENDC}",
            "=" * 50
        ]
        
        for i, item in enumerate(data['items'], 1):
            playlist = item['snippet']
            details = item['contentDetails']
            output.extend([
                f"\n{BOLD}{i}. {playlist['title']}{ENDC}",
                f"   📝 Description: {playlist['description'][:100]}...",
                f"   🎥 Videos Count: {details['itemCount']}",
                f"   🔗 URL: https://youtube.com/playlist?list={item['id']}"
            ])
        
        return "\n".join(output)

    def _extract_channel_id(self, channel_input: str) -> str:
        """Extract channel ID from various input formats"""
        # If it's already a channel ID
        if channel_input.startswith('UC') and len(channel_input) == 24:
            return channel_input
            
        # If it's a channel URL
        import re
        patterns = [
            r'youtube\.com/channel/(UC[\w-]{22})',
            r'youtube\.com/c/([^/\n?]+)',
            r'youtube\.com/@([^/\n?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, channel_input)
            if match:
                if pattern.startswith('youtube.com/channel/'):
                    return match.group(1)
                else:
                    # Search for channel by custom URL or handle
                    try:
                        response = youtube.search().list(
                            part="snippet",
                            q=match.group(1),
                            type="channel",
                            maxResults=1
                        ).execute()
                        
                        if response.get('items'):
                            return response['items'][0]['snippet']['channelId']
                    except Exception:
                        pass
        
        # If it's a channel name/handle, search for it
        try:
            response = youtube.search().list(
                part="snippet",
                q=channel_input,
                type="channel",
                maxResults=1
            ).execute()
            
            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
        except Exception as e:
            raise ValueError(f"Could not find channel: {str(e)}")
            
        raise ValueError(f"Could not find channel: {channel_input}")

    def run(self):
        """
        Retrieves channel analytics based on specified metric type
        """
        try:
            # Extract channel ID from input
            channel_id = self._extract_channel_id(self.channel_input)
            
            if self.metric_type == "statistics":
                response = youtube.channels().list(
                    part="snippet,statistics",
                    id=channel_id
                ).execute()
                return self._format_channel_statistics(response)
            
            elif self.metric_type == "videos":
                videos = youtube.search().list(
                    part="snippet",
                    channelId=channel_id,
                    order="date",
                    type="video",
                    maxResults=10
                ).execute()
                return self._format_videos_list(videos)
            
            elif self.metric_type == "playlists":
                playlists = youtube.playlists().list(
                    part="snippet,contentDetails",
                    channelId=channel_id,
                    maxResults=10
                ).execute()
                return self._format_playlists(playlists)
            
            return f"{RED}❌ Invalid metric type specified. Use 'statistics', 'videos', or 'playlists'.{ENDC}"
            
        except Exception as e:
            return f"{RED}❌ Error analyzing channel: {str(e)}{ENDC}"

if __name__ == "__main__":
    print(f"\n{BOLD}🔍 YOUTUBE CHANNEL ANALYSIS{ENDC}")
    print("=" * 50)
    
    # Test all metric types
    metric_types = ["statistics", "videos", "playlists"]
    for metric in metric_types:
        tool = ChannelAnalytics(channel_input="UCX6OQ3DkcsbYNE6H8uQQuVA", metric_type=metric)
        print(tool.run())
        print("\n" + "=" * 50) 