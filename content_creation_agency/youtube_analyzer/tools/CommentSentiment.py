from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from textblob import TextBlob
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

class CommentSentiment(BaseTool):
    """
    Analyzes sentiment in video comments
    """
    video_id: str = Field(
        ..., 
        description="ID or URL of the video to analyze comments from"
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

    def _format_date(self, date_str: str) -> str:
        """Format date to readable format"""
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date.strftime("%B %d, %Y")

    def _get_video_details(self, video_id: str) -> Dict:
        """Get video details for context"""
        try:
            response = youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            ).execute()
            
            if not response.get('items'):
                return None
                
            return response['items'][0]
        except Exception:
            return None

    def _format_sentiment(self, sentiment: float) -> str:
        """Format sentiment score with color and emoji"""
        if sentiment > 0.3:
            return f"{GREEN}Positive 😊 ({sentiment:.2f}){ENDC}"
        elif sentiment < -0.3:
            return f"{RED}Negative 😠 ({sentiment:.2f}){ENDC}"
        return f"{YELLOW}Neutral 😐 ({sentiment:.2f}){ENDC}"

    def run(self):
        """
        Retrieves and analyzes sentiment of public comments on a video
        """
        try:
            # Extract and validate video ID
            video_id = self._extract_video_id(self.video_id)
            
            # Get video details first
            video_details = self._get_video_details(video_id)
            if not video_details:
                return f"{RED}❌ Error: Video not found or not accessible{ENDC}"

            # Get comments
            comments_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100
            ).execute()
            
            if not comments_response.get('items'):
                return f"{YELLOW}⚠️ No comments found for this video{ENDC}"

            # Analyze sentiment
            sentiments = []
            for item in comments_response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                analysis = TextBlob(comment['textDisplay'])
                sentiments.append({
                    'text': comment['textDisplay'],
                    'author': comment['authorDisplayName'],
                    'date': comment['publishedAt'],
                    'likes': comment.get('likeCount', 0),
                    'sentiment': analysis.sentiment.polarity,
                    'subjectivity': analysis.sentiment.subjectivity
                })

            # Calculate average sentiment
            avg_sentiment = sum(s['sentiment'] for s in sentiments) / len(sentiments)
            
            # Format output
            output = [
                f"\n{BOLD}💭 COMMENT SENTIMENT ANALYSIS{ENDC}",
                "=" * 50,
                f"\n{BLUE}📺 Video:{ENDC} {video_details['snippet']['title']}",
                f"{BLUE}👤 Channel:{ENDC} {video_details['snippet']['channelTitle']}",
                f"{BLUE}📅 Published:{ENDC} {self._format_date(video_details['snippet']['publishedAt'])}",
                f"{BLUE}📊 Stats:{ENDC} {video_details['statistics'].get('viewCount', '0')} views, "
                f"{video_details['statistics'].get('likeCount', '0')} likes",
                "",
                f"{BOLD}📊 SENTIMENT SUMMARY{ENDC}",
                f"Overall Sentiment: {self._format_sentiment(avg_sentiment)}",
                f"Total Comments Analyzed: {len(sentiments)}",
                "",
                f"{BOLD}💬 TOP COMMENTS BY SENTIMENT{ENDC}"
            ]

            # Add top positive and negative comments
            sorted_comments = sorted(sentiments, key=lambda x: x['sentiment'], reverse=True)
            
            output.append(f"\n{GREEN}Most Positive Comments:{ENDC}")
            for comment in sorted_comments[:3]:
                output.extend([
                    f"  • {comment['text'][:100]}...",
                    f"    👤 {comment['author']} | 👍 {comment['likes']} likes | "
                    f"💭 {self._format_sentiment(comment['sentiment'])}"
                ])

            output.append(f"\n{RED}Most Negative Comments:{ENDC}")
            for comment in sorted_comments[-3:]:
                output.extend([
                    f"  • {comment['text'][:100]}...",
                    f"    👤 {comment['author']} | 👍 {comment['likes']} likes | "
                    f"💭 {self._format_sentiment(comment['sentiment'])}"
                ])

            return "\n".join(output)

        except Exception as e:
            return f"{RED}❌ Error analyzing comments: {str(e)}{ENDC}"

if __name__ == "__main__":
    # Test with a real YouTube video (using a popular AI-related video as example)
    test_videos = [
        "https://www.youtube.com/watch?v=aircAruvnKk",  # 3Blue1Brown neural networks video
        "dQw4w9WgXcQ"  # Direct video ID
    ]
    
    for video in test_videos:
        print(f"\n{BOLD}🔍 Analyzing video: {video}{ENDC}")
        print("=" * 80)
        tool = CommentSentiment(video_id=video)
        result = tool.run()
        print(result)
        print("=" * 80) 