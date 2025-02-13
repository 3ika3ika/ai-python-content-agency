from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import re
import json
from datetime import datetime
from typing import Dict, Any

load_dotenv()

youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

class CompetitorAnalysis(BaseTool):
    """
    Analyzes competitor channels and their public content
    """
    competitor_channel_id: str = Field(
        ..., 
        description="ID or URL of the competitor channel to analyze"
    )
    
    def _format_number(self, num_str):
        """Format large numbers for readability"""
        num = int(num_str)
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
        Analyzes a competitor's channel and their recent videos
        """
        try:
            channel_id = self._extract_channel_id(self.competitor_channel_id)
            if not channel_id:
                return "❌ Error: Invalid channel ID or URL provided"

            channel_response = youtube.channels().list(
                part="snippet,statistics,brandingSettings",
                id=channel_id
            ).execute()
            
            if not channel_response.get('items'):
                return f"❌ Error: No channel found with ID {channel_id}"

            videos_response = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                order="date",
                type="video",
                maxResults=10
            ).execute()
            
            if videos_response.get('items'):
                video_ids = [item['id']['videoId'] for item in videos_response['items']]
                videos_stats = youtube.videos().list(
                    part="statistics",
                    id=','.join(video_ids)
                ).execute()
            else:
                videos_stats = {'items': []}

            channel_info = channel_response['items'][0]
            
            data = {
                "Channel Analysis": {
                    "Title": channel_info['snippet']['title'],
                    "Subscribers": self._format_number(channel_info['statistics']['subscriberCount']),
                    "Total Videos": self._format_number(channel_info['statistics']['videoCount']),
                    "Total Views": self._format_number(channel_info['statistics']['viewCount']),
                    "Description": channel_info['snippet']['description'][:200] + "..."
                },
                "Recent Videos Analysis": []
            }

            for video in videos_response.get('items', []):
                video_stats = next(
                    (stats for stats in videos_stats['items'] 
                     if stats['id'] == video['id']['videoId']), 
                    {'statistics': {}}
                )
                
                video_info = {
                    "Title": video['snippet']['title'],
                    "Published": self._format_date(video['snippet']['publishedAt']),
                    "Views": self._format_number(video_stats.get('statistics', {}).get('viewCount', '0')),
                    "Likes": self._format_number(video_stats.get('statistics', {}).get('likeCount', '0')),
                    "Comments": self._format_number(video_stats.get('statistics', {}).get('commentCount', '0')),
                    "URL": f"https://youtube.com/watch?v={video['id']['videoId']}"
                }
                data["Recent Videos Analysis"].append(video_info)

            return self._format_output(data)

        except Exception as e:
            return f"❌ Error analyzing competitor: {str(e)}"

if __name__ == "__main__":
    test_channels = [
        "UCWN3xxRkmTPmbKwht9FuE5A",  # Siraj Raval
        "https://www.youtube.com/channel/UCbmCqH_WOUviDUsV83qloZQ"  # Your channel
    ]
    
    for channel in test_channels:
        print(f"\n🔍 Analyzing channel: {channel}")
        print("=" * 80)
        tool = CompetitorAnalysis(competitor_channel_id=channel)
        result = tool.run()
        print(result)
        print("=" * 80) 