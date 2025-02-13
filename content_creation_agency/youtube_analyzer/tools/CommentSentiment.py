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

# Initialize YouTube API
youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))

def get_all_comments(video_id: str, max_results: int = 100) -> list:
    """Get all available comments for a video"""
    try:
        comments = []
        next_page_token = None
        
        while len(comments) < max_results:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=min(100, max_results - len(comments)),
                pageToken=next_page_token,
                order="relevance"
            )
            
            response = request.execute()
            
            # Add comments from this page
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append(comment)
            
            # Check if there are more pages
            next_page_token = response.get('nextPageToken')
            if not next_page_token or len(response.get('items', [])) == 0:
                break
        
        return comments
        
    except Exception as e:
        print(f"Error getting comments: {str(e)}")
        return []

class CommentSentiment(BaseTool):
    """
    Analyzes sentiment in video comments for any YouTube video
    """
    video_id: str = Field(
        ..., 
        description="Video ID or URL to analyze comments from"
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

    def run(self):
        """
        Analyzes sentiment of video comments
        """
        try:
            # Extract video ID from input
            video_id = self._extract_video_id(self.video_id)
            
            # Get video details
            video_response = youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            ).execute()
            
            if not video_response.get('items'):
                return f"{RED}❌ Error: Video not found{ENDC}"
            
            video = video_response['items'][0]
            
            # Get comments
            comments = get_all_comments(video_id, max_results=100)
            
            if not comments:
                stats = video['statistics']
                comment_count = int(stats.get('commentCount', 0))
                if comment_count > 0:
                    return f"{YELLOW}⚠️ Video has {comment_count} comments but couldn't retrieve them. This might be due to API limitations.{ENDC}"
                else:
                    return f"{YELLOW}⚠️ No comments found for this video{ENDC}"

            # Analyze sentiment
            sentiments = []
            for comment in comments:
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
                "=" * 70,
                "",
                f"{BOLD}📺 VIDEO DETAILS{ENDC}",
                f"{'─' * 30}",
                f"{BLUE}Title:{ENDC} {video['snippet']['title']}",
                f"{BLUE}Channel:{ENDC} {video['snippet']['channelTitle']}",
                f"{BLUE}Published:{ENDC} {self._format_date(video['snippet']['publishedAt'])}",
                f"{BLUE}Views:{ENDC} {video['statistics'].get('viewCount', '0')}",
                "",
                f"{BOLD}📊 SENTIMENT SUMMARY{ENDC}",
                f"{'─' * 30}",
                f"Overall Sentiment: {self._format_sentiment(avg_sentiment)}",
                f"Total Comments Analyzed: {len(sentiments)}",
                "",
                f"{BOLD}💬 TOP COMMENTS BY SENTIMENT{ENDC}",
                f"{'─' * 30}"
            ]

            # Add top positive comments
            output.append(f"\n{GREEN}Most Positive Comments:{ENDC}")
            for comment in sorted(sentiments, key=lambda x: x['sentiment'], reverse=True)[:3]:
                output.extend([
                    f"  • {comment['text'][:100]}...",
                    f"    👤 {comment['author']} | 👍 {comment['likes']} likes | "
                    f"💭 {self._format_sentiment(comment['sentiment'])}"
                ])

            # Add top negative comments
            output.append(f"\n{RED}Most Critical Comments:{ENDC}")
            for comment in sorted(sentiments, key=lambda x: x['sentiment'])[:3]:
                output.extend([
                    f"  • {comment['text'][:100]}...",
                    f"    👤 {comment['author']} | 👍 {comment['likes']} likes | "
                    f"💭 {self._format_sentiment(comment['sentiment'])}"
                ])

            # Add sentiment distribution
            positive = sum(1 for s in sentiments if s['sentiment'] > 0.3)
            negative = sum(1 for s in sentiments if s['sentiment'] < -0.3)
            neutral = len(sentiments) - positive - negative
            
            output.extend([
                "",
                f"{BOLD}📈 SENTIMENT DISTRIBUTION{ENDC}",
                f"{'─' * 30}",
                f"{GREEN}Positive:{ENDC} {positive} ({positive/len(sentiments)*100:.1f}%)",
                f"{YELLOW}Neutral:{ENDC} {neutral} ({neutral/len(sentiments)*100:.1f}%)",
                f"{RED}Negative:{ENDC} {negative} ({negative/len(sentiments)*100:.1f}%)"
            ])

            return "\n".join(output)

        except Exception as e:
            if "commentsDisabled" in str(e):
                return f"{YELLOW}⚠️ Comments are disabled for this video{ENDC}"
            elif "invalidVideoId" in str(e):
                return f"{RED}❌ Invalid video ID{ENDC}"
            elif "quotaExceeded" in str(e):
                return f"{RED}❌ YouTube API quota exceeded. Please try again later.{ENDC}"
            else:
                return f"{RED}❌ Error analyzing comments: {str(e)}{ENDC}"

    def _format_date(self, date_str: str) -> str:
        """Format date to readable format"""
        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date.strftime("%B %d, %Y")

    def _format_sentiment(self, sentiment: float) -> str:
        """Format sentiment score with color and emoji"""
        if sentiment > 0.3:
            return f"{GREEN}Positive 😊 ({sentiment:.2f}){ENDC}"
        elif sentiment < -0.3:
            return f"{RED}Negative 😠 ({sentiment:.2f}){ENDC}"
        return f"{YELLOW}Neutral 😐 ({sentiment:.2f}){ENDC}"

if __name__ == "__main__":
    # Test with a specific video
    video_url = "https://www.youtube.com/watch?v=aircAruvnKk"  # Example video
    tool = CommentSentiment(video_id=video_url)
    print(tool.run()) 