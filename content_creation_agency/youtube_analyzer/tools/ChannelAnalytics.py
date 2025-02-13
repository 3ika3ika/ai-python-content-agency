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

# Initialize YouTube API and get default channel
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
default_channel = os.getenv('DEFAULT_CHANNEL_ID')  # Get channel ID from .env

class ChannelAnalytics(BaseTool):
    """
    Analyzes YouTube channel statistics and public data
    """
    channel_input: str = Field(
        default=default_channel,
        description="Channel URL, ID, or name to analyze (defaults to channel from .env)"
    )
    metric_type: str = Field(
        default="videos",
        description="Type of analysis (statistics, videos, playlists)"
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
        try:
            # If it's already the default channel ID, return it
            if channel_input == default_channel:
                return channel_input
                
            # If it's a channel ID
            if channel_input.startswith('UC'):
                return channel_input
                
            # If it's a URL
            if 'youtube.com' in channel_input:
                if '/channel/' in channel_input:
                    return channel_input.split('/channel/')[1].split('/')[0]
                elif '/@' in channel_input:
                    # Get channel by handle
                    response = youtube.search().list(
                        part="snippet",
                        q=channel_input,
                        type="channel",
                        maxResults=1,
                        relevanceLanguage="en"
                    ).execute()
                    if response.get('items'):
                        return response['items'][0]['snippet']['channelId']
            
            # Search for channel
            response = youtube.search().list(
                part="snippet",
                q=channel_input,
                type="channel",
                maxResults=1,
                relevanceLanguage="en"
            ).execute()
            
            if response.get('items'):
                return response['items'][0]['snippet']['channelId']
                
            return None
            
        except Exception as e:
            print(f"Error extracting channel ID: {str(e)}")
            return None

    def run(self):
        """
        Retrieves channel analytics based on specified metric type
        """
        try:
            # Extract channel ID from input
            channel_id = self._extract_channel_id(self.channel_input)
            if not channel_id:
                return f"{RED}❌ Error: Channel not found{ENDC}"
            
            # Get channel details
            channel_response = youtube.channels().list(
                part="snippet,statistics,contentDetails,brandingSettings",
                id=channel_id
            ).execute()
            
            if not channel_response.get('items'):
                return f"{RED}❌ Error: Channel data not accessible{ENDC}"
                
            channel = channel_response['items'][0]
            stats = channel['statistics']
            snippet = channel['snippet']
            
            # Format basic info with enhanced sections
            output = [
                f"\n{BOLD}🎥 YOUTUBE CHANNEL ANALYSIS REPORT{ENDC}",
                "=" * 70,
                "",
                f"{BOLD}📌 CHANNEL OVERVIEW{ENDC}",
                f"{'─' * 30}",
                f"{BLUE}Channel Name:{ENDC}     {snippet['title']}",
                f"{BLUE}Created:{ENDC}          {self._format_date(snippet['publishedAt'])}",
                f"{BLUE}Country:{ENDC}          {snippet.get('country', 'Not specified')}",
                f"{BLUE}Language:{ENDC}         {snippet.get('defaultLanguage', 'Not specified')}",
                "",
                f"{BOLD}📊 PERFORMANCE METRICS{ENDC}",
                f"{'─' * 30}",
                f"{GREEN}Subscribers:{ENDC}     {self._format_number(int(stats.get('subscriberCount', 0)))}",
                f"{GREEN}Total Videos:{ENDC}    {self._format_number(int(stats.get('videoCount', 0)))}",
                f"{GREEN}Total Views:{ENDC}     {self._format_number(int(stats.get('viewCount', 0)))}",
                f"{GREEN}Avg Views/Video:{ENDC} {self._format_number(int(int(stats.get('viewCount', 0)) / int(stats.get('videoCount', 1))))}",
                "",
                f"{BOLD}📝 CHANNEL DESCRIPTION{ENDC}",
                f"{'─' * 30}",
                f"{snippet.get('description', 'No description available')[:300]}...",
                "",
                f"{BOLD}🎯 CHANNEL TOPICS{ENDC}",
                f"{'─' * 30}"
            ]
            
            # Add topic categories if available
            if 'topicDetails' in channel:
                topics = channel['topicDetails'].get('topicCategories', [])
                for topic in topics:
                    topic_name = topic.split('/')[-1].replace('_', ' ')
                    output.append(f"• {topic_name}")
            else:
                output.append("No topic categories available")
            
            # Get recent videos if requested
            if self.metric_type == "videos":
                playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
                videos_response = youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=5
                ).execute()
                
                if videos_response.get('items'):
                    output.extend([
                        "",
                        f"{BOLD}🎬 RECENT VIDEOS{ENDC}",
                        f"{'─' * 30}"
                    ])
                    
                    for i, item in enumerate(videos_response['items'], 1):
                        video = item['snippet']
                        video_id = item['contentDetails']['videoId']
                        
                        # Get video statistics
                        video_stats = youtube.videos().list(
                            part="statistics",
                            id=video_id
                        ).execute()
                        
                        if video_stats.get('items'):
                            stats = video_stats['items'][0]['statistics']
                            views = self._format_number(int(stats.get('viewCount', 0)))
                            likes = self._format_number(int(stats.get('likeCount', 0)))
                            comments = self._format_number(int(stats.get('commentCount', 0)))
                            
                            output.extend([
                                f"\n{YELLOW}{i}. {video['title']}{ENDC}",
                                f"   📅 Published: {self._format_date(video['publishedAt'])}",
                                f"   👀 Views: {views}",
                                f"   👍 Likes: {likes}",
                                f"   💬 Comments: {comments}",
                                f"   📝 Description: {video['description'][:100]}...",
                                f"   🔗 Watch: https://youtube.com/watch?v={video_id}"
                            ])
                        else:
                            output.extend([
                                f"\n{YELLOW}{i}. {video['title']}{ENDC}",
                                f"   📅 Published: {self._format_date(video['publishedAt'])}",
                                f"   ⚠️ Statistics not available",
                                f"   📝 Description: {video['description'][:100]}...",
                                f"   🔗 Watch: https://youtube.com/watch?v={video_id}"
                            ])
            
            # Add custom playlists if available
            playlists_response = youtube.playlists().list(
                part="snippet,contentDetails",
                channelId=channel_id,
                maxResults=3
            ).execute()
            
            if playlists_response.get('items'):
                output.extend([
                    "",
                    f"{BOLD}📑 FEATURED PLAYLISTS{ENDC}",
                    f"{'─' * 30}"
                ])
                
                for playlist in playlists_response['items']:
                    output.extend([
                        f"• {playlist['snippet']['title']}",
                        f"  Videos: {playlist['contentDetails']['itemCount']}"
                    ])
            
            # Add social links if available
            if 'brandingSettings' in channel:
                social_links = channel['brandingSettings'].get('channel', {}).get('customUrls', [])
                if social_links:
                    output.extend([
                        "",
                        f"{BOLD}🔗 SOCIAL LINKS{ENDC}",
                        f"{'─' * 30}"
                    ])
                    for link in social_links:
                        output.append(f"• {link}")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"{RED}❌ Error analyzing channel: {str(e)}{ENDC}"

if __name__ == "__main__":
    # Test with default channel from .env
    print(f"\n{BOLD}🔍 Testing channel analytics{ENDC}")
    print("=" * 50)
    
    tool = ChannelAnalytics()
    print(tool.run()) 